import 'dart:math' as math;
import 'dart:typed_data';

import 'package:audioplayers/audioplayers.dart';
import 'package:flutter/foundation.dart';
import 'package:torch_light/torch_light.dart';
import 'package:vibration/vibration.dart';

import '../models/duty_status.dart';

class AlarmFeedbackService {
  final AudioPlayer _audioPlayer = AudioPlayer();

  Future<void> playForStatus(DutyStatus status) async {
    if (status == DutyStatus.notInSchool) {
      return;
    }

    if (status == DutyStatus.classwork) {
      await _blinkFlashlightForClasswork();
      return;
    }

    await Future.wait<void>([
      _playLoudAlarm(),
      _vibrate(),
      _blinkFlashlightForNormalAlarm(),
    ]);
  }

  Future<void> _playLoudAlarm() async {
    try {
      await _audioPlayer.setVolume(1.0);
      await _audioPlayer.setReleaseMode(ReleaseMode.loop);
      await _audioPlayer.play(BytesSource(_buildSirenWav()));
      await Future<void>.delayed(const Duration(seconds: 10));
      await _audioPlayer.stop();
    } catch (e) {
      debugPrint('Alarm sound failed: $e');
      try {
        await _audioPlayer.stop();
      } catch (_) {}
    }
  }

  Uint8List _buildSirenWav() {
    const sampleRate = 44100;
    const seconds = 2;
    const channels = 1;
    const bitsPerSample = 16;
    const amplitude = 0.5;

    final totalSamples = sampleRate * seconds;
    final byteRate = sampleRate * channels * (bitsPerSample ~/ 8);
    final blockAlign = channels * (bitsPerSample ~/ 8);
    final dataSize = totalSamples * blockAlign;
    final fileSize = 36 + dataSize;

    final bytes = BytesBuilder();

    void addString(String value) => bytes.add(value.codeUnits);

    void addInt32(int value) {
      bytes.add([
        value & 0xff,
        (value >> 8) & 0xff,
        (value >> 16) & 0xff,
        (value >> 24) & 0xff,
      ]);
    }

    void addInt16(int value) {
      bytes.add([
        value & 0xff,
        (value >> 8) & 0xff,
      ]);
    }

    addString('RIFF');
    addInt32(fileSize);
    addString('WAVE');
    addString('fmt ');
    addInt32(16);
    addInt16(1);
    addInt16(channels);
    addInt32(sampleRate);
    addInt32(byteRate);
    addInt16(blockAlign);
    addInt16(bitsPerSample);
    addString('data');
    addInt32(dataSize);

    for (var i = 0; i < totalSamples; i++) {
      final t = i / sampleRate;
      final sweep = (math.sin(2 * math.pi * 0.5 * t) + 1) / 2;
      final frequency = 700 + (900 * sweep);
      final sample = (math.sin(2 * math.pi * frequency * t) * amplitude * 32767).toInt();
      addInt16(sample);
    }

    return bytes.toBytes();
  }

  Future<void> _vibrate() async {
    try {
      final hasVibrator = await Vibration.hasVibrator();
      if (hasVibrator) {
        await Vibration.vibrate(duration: 10000);
      }
    } catch (e) {
      debugPrint('Vibration failed: $e');
    }
  }

  Future<void> _blinkFlashlightForNormalAlarm() async {
    try {
      for (var i = 0; i < 10; i++) {
        await TorchLight.enableTorch();
        await Future<void>.delayed(const Duration(milliseconds: 350));
        await TorchLight.disableTorch();
        await Future<void>.delayed(const Duration(milliseconds: 150));
      }
    } catch (e) {
      debugPrint('Torch failed: $e');
      try {
        await TorchLight.disableTorch();
      } catch (_) {}
    }
  }

  Future<void> _blinkFlashlightForClasswork() async {
    try {
      await TorchLight.enableTorch();
      await Future<void>.delayed(const Duration(seconds: 1));
      await TorchLight.disableTorch();
    } catch (e) {
      debugPrint('Classwork torch failed: $e');
      try {
        await TorchLight.disableTorch();
      } catch (_) {}
    }
  }
}
