/// PyDispatch Mobile – Alarmton.
/// Spielt eine benutzerdefinierte MP3-Datei aus assets/sounds/alarm.mp3 ab.
/// Falls die Datei fehlt, wird ein Sirenen-WAV programmatisch erzeugt.
/// Nutzt den Android ALARM-Stream für maximale Lautstärke.
///
/// Design:
/// - Singleton-AudioPlayer: Die Instanz wird einmal erstellt und NICHT
///   zwischen Alarmen disposed. `stop()` stoppt nur die Wiedergabe.
/// - Die WAV-Generierung läuft in einem separaten Isolate (`compute()`),
///   damit der Main-Thread nicht blockiert wird (→ keine Skipped Frames).
/// - Ein Mutex (`_busy`) verhindert Race Conditions bei parallelen
///   play()/stop()-Aufrufen.
/// - Lautstärke wird über einen nativen MethodChannel direkt am
///   Android STREAM_ALARM gesetzt (nicht über VolumeController, der
///   nur STREAM_MUSIC steuert).
/// - Audio-Lifecycle ist vom AlarmScreen entkoppelt: play()/stop() werden
///   von _AppShellState in main.dart gesteuert.
import 'dart:async';
import 'dart:io';
import 'dart:math';
import 'dart:typed_data';
import 'package:audioplayers/audioplayers.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';

/// Top-Level-Funktion für `compute()` – erzeugt die WAV-Bytes
/// in einem eigenen Isolate, damit der UI-Thread frei bleibt.
Uint8List _generateAlarmWavBytes(void _) {
  const sampleRate = 44100;
  const durationSec = 4;
  const numSamples = sampleRate * durationSec;
  const freqLow = 390.0;
  const freqHigh = 1200.0;
  const sweepUpEnd = 1.5;
  const pauseEnd = 1.7;
  const sweepDownEnd = 3.2;

  final samples = Int16List(numSamples);
  double phase = 0.0;

  for (var i = 0; i < numSamples; i++) {
    final t = i / sampleRate;
    double freq;
    double amp;

    if (t < sweepUpEnd) {
      final progress = t / sweepUpEnd;
      freq = freqLow + (freqHigh - freqLow) * progress;
      amp = 0.95 * _smoothEnv(t, 0.0, sweepUpEnd);
    } else if (t < pauseEnd) {
      freq = freqHigh;
      final p = (t - sweepUpEnd) / (pauseEnd - sweepUpEnd);
      amp = 0.95 * (1.0 - p);
    } else if (t < sweepDownEnd) {
      final progress = (t - pauseEnd) / (sweepDownEnd - pauseEnd);
      freq = freqHigh - (freqHigh - freqLow) * progress;
      amp = 0.95 * _smoothEnv(t - pauseEnd, 0.0, sweepDownEnd - pauseEnd);
    } else {
      freq = freqLow;
      final p = (t - sweepDownEnd) / (durationSec - sweepDownEnd);
      amp = 0.95 * (1.0 - p);
    }

    phase += 2 * pi * freq / sampleRate;
    if (phase > 2 * pi) phase -= 2 * pi;

    final mainTone = sin(phase);
    final harmonic = 0.15 * sin(3 * phase);
    final sample = (amp * 32767 * (mainTone + harmonic) / 1.15)
        .round()
        .clamp(-32767, 32767);
    samples[i] = sample;
  }

  return _encodeWavStatic(samples, sampleRate);
}

double _smoothEnv(double tInSegment, double segStart, double segLen) {
  final pos = tInSegment - segStart;
  const fade = 0.015;
  if (pos < fade) return pos / fade;
  if (pos > segLen - fade) return (segLen - pos) / fade;
  return 1.0;
}

Uint8List _encodeWavStatic(Int16List samples, int sampleRate) {
  final dataSize = samples.length * 2;
  final fileSize = 36 + dataSize;
  final buf = ByteData(44 + dataSize);

  void writeStr(int offset, String str) {
    for (var i = 0; i < str.length; i++) {
      buf.setUint8(offset + i, str.codeUnitAt(i));
    }
  }

  writeStr(0, 'RIFF');
  buf.setUint32(4, fileSize, Endian.little);
  writeStr(8, 'WAVE');
  writeStr(12, 'fmt ');
  buf.setUint32(16, 16, Endian.little);
  buf.setUint16(20, 1, Endian.little);
  buf.setUint16(22, 1, Endian.little);
  buf.setUint32(24, sampleRate, Endian.little);
  buf.setUint32(28, sampleRate * 2, Endian.little);
  buf.setUint16(32, 2, Endian.little);
  buf.setUint16(34, 16, Endian.little);
  writeStr(36, 'data');
  buf.setUint32(40, dataSize, Endian.little);

  for (var i = 0; i < samples.length; i++) {
    buf.setInt16(44 + i * 2, samples[i], Endian.little);
  }

  return buf.buffer.asUint8List();
}

class AlarmTone {
  // ── Native MethodChannel für STREAM_ALARM Lautstärke ──
  static const _channel = MethodChannel('com.pydispatch/audio');

  // ── Singleton-Player ──
  static AudioPlayer? _player;
  static StreamSubscription? _stateSub;
  static StreamSubscription? _logSub;

  /// Gespeicherte vorherige Stream-Lautstärken (ALARM + MUSIC).
  static int? _previousAlarmVolume;
  static int? _previousMusicVolume;

  /// True solange eine play()- oder stop()-Operation läuft.
  static Completer<void>? _busy;

  /// Pfad zur vorgenerierten Fallback-WAV.
  static String? _cachedWavPath;

  /// True wenn gerade Audio spielt (entkoppelt vom Widget-Lifecycle).
  static bool get isPlaying =>
      _player != null && _player!.state == PlayerState.playing;

  static const _assetPath = 'sounds/alarm.mp3';
  static const _bundleAssetPath = 'assets/sounds/alarm.mp3';

  // ── Vorbereitungen ──

  /// Bereitet den Fallback-Alarmton im Hintergrund vor.
  static Future<void> preCache() async {
    if (_cachedWavPath != null) return;
    try {
      final bytes = await compute(_generateAlarmWavBytes, null);
      final file = File('${Directory.systemTemp.path}/pydispatch_alarm.wav');
      await file.writeAsBytes(bytes);
      _cachedWavPath = file.path;
      debugPrint('ALARM_TONE: Fallback-WAV vorberechnet (${bytes.length} bytes)');
    } catch (e) {
      debugPrint('ALARM_TONE: preCache fehlgeschlagen: $e');
    }
  }

  // ── Lautstärke (nativer ALARM-Stream) ──

  /// Setzt die Android ALARM- und MUSIC-Stream-Lautstärke auf Maximum.
  /// Speichert die vorherigen Werte zum Wiederherstellen.
  static Future<void> _setAlarmVolumeMax() async {
    try {
      final result = await _channel.invokeMethod<Map>('setAlarmVolumeMax');
      if (result != null) {
        _previousAlarmVolume = result['prevAlarm'] as int?;
        _previousMusicVolume = result['prevMusic'] as int?;
      }
      debugPrint('ALARM_TONE: ALARM+MUSIC-Stream auf Maximum gesetzt '
          '(vorher: alarm=$_previousAlarmVolume, music=$_previousMusicVolume)');
    } catch (e) {
      debugPrint('ALARM_TONE: Volume setzen fehlgeschlagen: $e');
    }
  }

  /// Stellt die vorherigen ALARM- und MUSIC-Stream-Lautstärken wieder her.
  static Future<void> _restoreAlarmVolume() async {
    if (_previousAlarmVolume == null && _previousMusicVolume == null) return;
    try {
      await _channel.invokeMethod('restoreAlarmVolume', {
        'alarmVolume': _previousAlarmVolume ?? 0,
        'musicVolume': _previousMusicVolume,
      });
      debugPrint('ALARM_TONE: Volumes wiederhergestellt: '
          'alarm=$_previousAlarmVolume, music=$_previousMusicVolume');
    } catch (e) {
      debugPrint('ALARM_TONE: Volume Restore fehlgeschlagen: $e');
    }
    _previousAlarmVolume = null;
    _previousMusicVolume = null;
  }

  // ── Player-Initialisierung ──

  /// Setzt den AudioContext für den Alarm-Stream.
  /// Wird vor JEDEM Play-Versuch aufgerufen, damit ein evtl.
  /// zurückgesetzter Kontext erneut gesetzt wird.
  static Future<void> _applyAudioContext(AudioPlayer player) async {
    try {
      await player.setAudioContext(AudioContext(
        android: AudioContextAndroid(
          isSpeakerphoneOn: false,
          audioMode: AndroidAudioMode.normal,
          stayAwake: true,
          audioFocus: AndroidAudioFocus.gainTransientExclusive,
          usageType: AndroidUsageType.alarm,
          contentType: AndroidContentType.sonification,
        ),
        iOS: AudioContextIOS(
          category: AVAudioSessionCategory.playback,
          options: {AVAudioSessionOptions.duckOthers},
        ),
      ));
      debugPrint('ALARM_TONE: AudioContext gesetzt (ALARM-Stream)');
    } catch (e) {
      debugPrint('ALARM_TONE: setAudioContext fehlgeschlagen: $e');
    }
  }

  static Future<AudioPlayer> _ensurePlayer() async {
    if (_player != null) return _player!;

    debugPrint('ALARM_TONE: Erstelle neuen AudioPlayer (Singleton)');
    final player = AudioPlayer();

    _stateSub = player.onPlayerStateChanged.listen((state) {
      debugPrint('ALARM_TONE: Player-Status: $state');
    });
    _logSub = player.onLog.listen((msg) {
      debugPrint('ALARM_TONE: Player-Log: $msg');
    });

    await _applyAudioContext(player);

    _player = player;
    return player;
  }

  /// Zerstört den Singleton-Player komplett.
  static Future<void> dispose() async {
    await stop();
    try {
      await _stateSub?.cancel();
      await _logSub?.cancel();
      await _player?.dispose();
    } catch (_) {}
    _player = null;
    _stateSub = null;
    _logSub = null;
    debugPrint('ALARM_TONE: Player komplett disposed');
  }

  // ── Wiedergabe ──

  /// Startet den Alarmton (Loop).
  /// Setzt den ALARM-Stream auf Maximum via nativen MethodChannel.
  static Future<void> play() async {
    // Auf laufende Operation warten
    if (_busy != null) {
      debugPrint('ALARM_TONE: play() wartet auf laufende Operation...');
      await _busy!.future;
    }
    _busy = Completer<void>();

    try {
      debugPrint('ALARM_TONE: ===== play() gestartet =====');

      if (_player != null && _player!.state == PlayerState.playing) {
        debugPrint('ALARM_TONE: Spielt bereits – kein Neustart');
        return;
      }

      // ── ALARM-Stream Lautstärke auf Maximum (nativer Kanal) ──
      await _setAlarmVolumeMax();

      // ── Singleton-Player initialisieren ──
      final player = await _ensurePlayer();

      // Vorherige Wiedergabe stoppen (OHNE dispose!)
      try {
        await player.stop();
      } catch (_) {}

      // AudioContext vor dem Abspielen (erneut) anwenden –
      // wurde er vom System oder einem anderen Plugin zurückgesetzt,
      // greift er jetzt wieder.
      await _applyAudioContext(player);

      await player.setReleaseMode(ReleaseMode.loop);
      await player.setVolume(1.0);

      // ── Versuch 1: MP3 als Flutter-Asset ──
      if (await _tryPlayAsset(player)) return;

      // Player stoppen+resetten bevor nächster Versuch startet –
      // verhindert Konflikte wenn der vorherige Source noch lädt.
      try { await player.stop(); } catch (_) {}
      await _applyAudioContext(player);
      await player.setReleaseMode(ReleaseMode.loop);
      await player.setVolume(1.0);

      // ── Versuch 2: Asset-Bytes direkt laden ──
      if (await _tryPlayBytes(player)) return;

      try { await player.stop(); } catch (_) {}
      await _applyAudioContext(player);
      await player.setReleaseMode(ReleaseMode.loop);
      await player.setVolume(1.0);

      // ── Versuch 3: Fallback-Sirene als WAV ──
      if (await _tryPlayWav(player)) return;

      // ── Letzter Ausweg: Player komplett neu erstellen ──
      await _recreatePlayerAndRetry();
    } catch (e) {
      debugPrint('ALARM_TONE: play() schwerer Fehler: $e');
    } finally {
      _busy!.complete();
      _busy = null;
    }
  }

  /// Prüft ob der Player nach einem play()-Aufruf tatsächlich spielt.
  /// Wartet bis zu [timeout] ms und pollt alle 200 ms.
  static Future<bool> _waitForPlaying(AudioPlayer player,
      {int timeout = 1500}) async {
    final end = DateTime.now().add(Duration(milliseconds: timeout));
    while (DateTime.now().isBefore(end)) {
      if (player.state == PlayerState.playing) return true;
      await Future.delayed(const Duration(milliseconds: 200));
    }
    return player.state == PlayerState.playing;
  }

  static Future<bool> _tryPlayAsset(AudioPlayer player) async {
    try {
      await player.play(
        AssetSource(_assetPath),
        volume: 1.0,
        mode: PlayerMode.mediaPlayer,
      );
      debugPrint('ALARM_TONE: AssetSource gestartet ($_assetPath)');
      if (await _waitForPlaying(player)) {
        debugPrint('ALARM_TONE: AssetSource OK – Player spielt');
        return true;
      }
      debugPrint('ALARM_TONE: AssetSource hat nicht gestartet '
          '(Status: ${player.state})');
    } catch (e) {
      debugPrint('ALARM_TONE: AssetSource fehlgeschlagen: $e');
    }
    return false;
  }

  static Future<bool> _tryPlayBytes(AudioPlayer player) async {
    try {
      final asset = await rootBundle.load(_bundleAssetPath);
      final bytes = asset.buffer.asUint8List();
      await player.setSourceBytes(bytes, mimeType: 'audio/mpeg');
      await player.resume();
      debugPrint('ALARM_TONE: MP3 über setSourceBytes gestartet '
          '(${bytes.length} bytes)');
      if (await _waitForPlaying(player)) return true;
      debugPrint('ALARM_TONE: setSourceBytes hat nicht gestartet');
    } catch (e) {
      debugPrint('ALARM_TONE: setSourceBytes fehlgeschlagen: $e');
    }
    return false;
  }

  static Future<bool> _tryPlayWav(AudioPlayer player) async {
    debugPrint('ALARM_TONE: MP3 nicht abspielbar – nutze Fallback-Sirene');
    try {
      if (_cachedWavPath == null) {
        debugPrint('ALARM_TONE: WAV noch nicht gecacht – erzeuge jetzt...');
        final bytes = await compute(_generateAlarmWavBytes, null);
        final file = File(
          '${Directory.systemTemp.path}/pydispatch_alarm.wav',
        );
        await file.writeAsBytes(bytes);
        _cachedWavPath = file.path;
      }
      await player.play(
        DeviceFileSource(_cachedWavPath!),
        volume: 1.0,
        mode: PlayerMode.mediaPlayer,
      );
      debugPrint('ALARM_TONE: Fallback-WAV gestartet');
      if (await _waitForPlaying(player)) return true;
      debugPrint('ALARM_TONE: Fallback-WAV hat nicht gestartet');
    } catch (e) {
      debugPrint('ALARM_TONE: Auch Fallback fehlgeschlagen: $e');
    }
    return false;
  }

  static Future<void> _recreatePlayerAndRetry() async {
    debugPrint('ALARM_TONE: Erstelle Player komplett neu...');
    try {
      await _stateSub?.cancel();
      await _logSub?.cancel();
      await _player?.dispose();
    } catch (_) {}
    _player = null;
    _stateSub = null;
    _logSub = null;

    try {
      final player = await _ensurePlayer();
      await _applyAudioContext(player);
      await player.setReleaseMode(ReleaseMode.loop);
      await player.setVolume(1.0);

      // Versuch 1: Asset
      await player.play(
        AssetSource(_assetPath),
        volume: 1.0,
        mode: PlayerMode.mediaPlayer,
      );
      if (await _waitForPlaying(player)) {
        debugPrint('ALARM_TONE: Retry (Asset) nach Neustart erfolgreich');
        return;
      }

      // Versuch 2: Fallback-WAV
      try { await player.stop(); } catch (_) {}
      if (_cachedWavPath != null) {
        await player.play(
          DeviceFileSource(_cachedWavPath!),
          volume: 1.0,
          mode: PlayerMode.mediaPlayer,
        );
        if (await _waitForPlaying(player)) {
          debugPrint('ALARM_TONE: Retry (WAV) nach Neustart erfolgreich');
          return;
        }
      }

      debugPrint('ALARM_TONE: Retry nach Neustart fehlgeschlagen');
    } catch (e) {
      debugPrint('ALARM_TONE: Retry nach Neustart Fehler: $e');
    }
  }

  // ── Stoppen ──

  /// Stoppt den Alarmton und stellt das ALARM-Stream-Volume wieder her.
  static Future<void> stop() async {
    if (_busy != null) {
      debugPrint('ALARM_TONE: stop() wartet auf laufende Operation...');
      await _busy!.future;
    }
    _busy = Completer<void>();

    try {
      debugPrint('ALARM_TONE: stop() aufgerufen');
      try {
        if (_player != null && _player!.state == PlayerState.playing) {
          await _player!.stop();
          debugPrint('ALARM_TONE: Player gestoppt');
        }
      } catch (e) {
        debugPrint('ALARM_TONE: stop() Player-Fehler: $e');
      }

      await _restoreAlarmVolume();
    } finally {
      _busy!.complete();
      _busy = null;
    }
  }
}
