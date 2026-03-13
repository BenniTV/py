/// PyDispatch Mobile – Hintergrund-Service.
/// Foreground-Service der auch bei minimierter oder geschlossener App
/// die Datenbank nach neuen Alarmen abfragt und Benachrichtigungen anzeigt.
///
/// Architektur:
/// - Läuft als Android Foreground Service (persistente Hintergrund-Notification)
/// - Pollt die MySQL-Datenbank alle 5 Sekunden
/// - Zeigt Alarm-Notifications mit maximaler Priorität bei neuen Einsätzen
/// - Kommuniziert mit der Vordergrund-App über Events
///
/// WICHTIG: Der Background-Isolate hat KEINEN Zugriff auf UI-Plugins
/// (AudioPlayer, VolumeController etc.). Audio wird ausschließlich
/// über die Notification (eigener Sound-Kanal) oder durch Delegation
/// an den Main-Isolate (Event 'alarmDetected') abgespielt.
import 'dart:async';
import 'dart:ui';
import 'package:flutter/foundation.dart';
import 'package:flutter_background_service/flutter_background_service.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:mysql_client/mysql_client.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Notification-IDs und Channel-IDs.
const _bgNotificationChannelId = 'pydispatch_bg';
const _bgNotificationId = 888;
const _alarmNotificationBaseId = 9000;
const _alarmChannelId = 'pydispatch_alarm_v2';
const _alarmSoundName = 'alarm';

/// Initialisiert und konfiguriert den Hintergrund-Service.
Future<void> initBackgroundService() async {
  final service = FlutterBackgroundService();

  // Hintergrund-Notification-Channel erstellen (leise, für den Service selbst)
  final notifPlugin = FlutterLocalNotificationsPlugin();
  final androidPlugin = notifPlugin.resolvePlatformSpecificImplementation<
      AndroidFlutterLocalNotificationsPlugin>();
  await androidPlugin?.createNotificationChannel(
    const AndroidNotificationChannel(
      _bgNotificationChannelId,
      'PyDispatch Hintergrund',
      description: 'Hintergrund-Service für Alarm-Erkennung',
      importance: Importance.low,
    ),
  );

  await service.configure(
    androidConfiguration: AndroidConfiguration(
      onStart: onStart,
      autoStart: true,
      isForegroundMode: true,
      notificationChannelId: _bgNotificationChannelId,
      initialNotificationTitle: 'PyDispatch',
      initialNotificationContent: 'Alarm-Überwachung aktiv',
      foregroundServiceNotificationId: _bgNotificationId,
      foregroundServiceTypes: [AndroidForegroundType.dataSync],
    ),
    iosConfiguration: IosConfiguration(
      autoStart: false,
    ),
  );
}

/// Entry-Point für den Hintergrund-Isolate.
/// MUSS eine Top-Level-Funktion mit @pragma('vm:entry-point') sein,
/// damit der Dart-Compiler sie nicht entfernt.
///
/// WICHTIG: In diesem Isolate dürfen KEINE UI-Plugins verwendet werden
/// (kein AudioPlayer, kein VolumeController, kein TorchLight etc.).
/// Audio wird über den Notification-Sound-Channel abgespielt.
/// Wenn die App noch im Speicher ist, wird 'alarmDetected' an den
/// Main-Isolate gesendet, der dort den vollen Alarm-Screen zeigt.
@pragma('vm:entry-point')
void onStart(ServiceInstance service) async {
  // Fehler im Background-Isolate niemals unbehandelt lassen –
  // ein Crash hier tötet den gesamten Foreground Service.
  try {
    await _onStartImpl(service);
  } catch (e, stack) {
    debugPrint('BG-SERVICE: FATALER FEHLER in onStart: $e');
    debugPrint('BG-SERVICE: $stack');
  }
}

Future<void> _onStartImpl(ServiceInstance service) async {
  DartPluginRegistrant.ensureInitialized();

  // ── Notification-Plugin im Hintergrund-Isolate initialisieren ──
  final notifPlugin = FlutterLocalNotificationsPlugin();
  const androidSettings =
      AndroidInitializationSettings('@mipmap/ic_launcher');
  await notifPlugin.initialize(
    const InitializationSettings(android: androidSettings),
  );

  // Alarm-Notification-Channel erstellen
  final androidPlugin = notifPlugin.resolvePlatformSpecificImplementation<
      AndroidFlutterLocalNotificationsPlugin>();
  await androidPlugin?.createNotificationChannel(
    const AndroidNotificationChannel(
      _alarmChannelId,
      'Alarm',
      description: 'Alarmierungen bei neuen Einsätzen',
      importance: Importance.max,
      playSound: true,
      sound: RawResourceAndroidNotificationSound(_alarmSoundName),
      audioAttributesUsage: AudioAttributesUsage.alarm,
      enableVibration: true,
      enableLights: true,
    ),
  );

  // ── Status-Tracking ──
  final Set<int> seenIds = {};
  MySQLConnection? dbConn;
  bool appInForeground = true; // Standardmäßig ja (App startet im Vordergrund)
  bool isPolling = false; // Verhindert gleichzeitige Poll-Durchläufe

  // ── Nachrichten vom Vordergrund empfangen ──
  if (service is AndroidServiceInstance) {
    service.on('setAsForeground').listen((_) {
      appInForeground = true;
      try {
        service.setAsForegroundService();
      } catch (e) {
        debugPrint('BG-SERVICE: setAsForegroundService fehlgeschlagen: $e');
      }
      debugPrint('BG-SERVICE: App im Vordergrund, Service bleibt Foreground');
    });

    service.on('setAsBackground').listen((_) {
      appInForeground = false;
      debugPrint('BG-SERVICE: App im Hintergrund, Polling übernommen');
    });
  }

  service.on('seenIds').listen((event) {
    if (event != null && event['ids'] is List) {
      for (final id in event['ids'] as List) {
        if (id is int) {
          seenIds.add(id);
        } else if (id is String) {
          final parsed = int.tryParse(id);
          if (parsed != null) seenIds.add(parsed);
        }
      }
    }
  });

  service.on('stopService').listen((_) {
    service.stopSelf();
  });

  // ── Polling-Timer: alle 5 Sekunden nach neuen Alarmen suchen ──
  debugPrint('BG-SERVICE: Polling-Timer gestartet');
  Timer.periodic(const Duration(seconds: 5), (timer) async {
    // Im Vordergrund übernimmt die App selbst das Polling
    if (appInForeground) return;
    // Sperre: kein paralleles Polling
    if (isPolling) return;
    isPolling = true;
    debugPrint('BG-SERVICE: Polling... (Hintergrund-Modus)');

    try {
      // Config aus SharedPreferences lesen
      final prefs = await SharedPreferences.getInstance();
      final setupDone = prefs.getBool('setup_done') ?? false;
      if (!setupDone) return;

      final host = prefs.getString('mysql_host') ?? 'localhost';
      final port = prefs.getInt('mysql_port') ?? 3306;
      final user = prefs.getString('mysql_user') ?? '';
      final password = prefs.getString('mysql_password') ?? '';
      final database = prefs.getString('mysql_database') ?? 'pydispatch';
      final geraeteId = prefs.getString('geraete_id') ?? '';
      if (user.isEmpty || geraeteId.isEmpty) return;

      // DB-Verbindung herstellen oder wiederverwenden
      if (dbConn == null) {
        dbConn = await MySQLConnection.createConnection(
          host: host,
          port: port,
          userName: user,
          password: password,
          databaseName: database,
          secure: false,
        );
        await dbConn!.connect();
      }

      // Benutzer-Status prüfen (nur alarmieren wenn in der Schule)
      final deviceRows = await dbConn!.execute(
        'SELECT mg.benutzer_id, b.status '
        'FROM mobile_geraete mg '
        'JOIN benutzer b ON mg.benutzer_id = b.id '
        'WHERE mg.geraete_id = :id AND mg.ist_aktiv = 1 AND b.ist_aktiv = 1',
        {'id': geraeteId},
      );

      if (deviceRows.rows.isEmpty) return;
      final deviceData = deviceRows.rows.first.typedAssoc();
      final userStatus =
          deviceData['status']?.toString() ?? 'nicht_in_der_schule';
      if (userStatus == 'nicht_in_der_schule') return;

      // Letzter Kontakt aktualisieren
      await dbConn!.execute(
        'UPDATE mobile_geraete SET letzter_kontakt = NOW() '
        'WHERE geraete_id = :id',
        {'id': geraeteId},
      );

      // Aktive Einsätze prüfen
      final einsatzRows = await dbConn!.execute(
        'SELECT e.id, sw.kuerzel, sw.bezeichnung AS stichwort_name, '
        's.name AS standort_name, e.standort_text '
        'FROM einsaetze e '
        'JOIN stichwoerter sw ON e.stichwort_id = sw.id '
        'LEFT JOIN standorte s ON e.standort_id = s.id '
        'WHERE e.status = :status '
        'ORDER BY e.alarmiert_am DESC',
        {'status': 'aktiv'},
      );

      for (final row in einsatzRows.rows) {
        final data = row.typedAssoc();
        final id = int.tryParse(data['id']?.toString() ?? '') ?? 0;
        if (id == 0 || seenIds.contains(id)) continue;

        seenIds.add(id);
        final kuerzel = data['kuerzel']?.toString() ?? '?';
        final stichwort = data['stichwort_name']?.toString() ?? 'Einsatz';
        final standort = data['standort_name']?.toString() ??
            data['standort_text']?.toString() ??
            '—';

        debugPrint('BG-SERVICE: NEUER ALARM! ID=$id, $kuerzel - $stichwort');

        // ── 1. Event an die Vordergrund-App senden ──
        // Wenn die App noch im Speicher ist (minimiert), empfängt sie
        // dieses Event und zeigt den vollen Alarm-Screen.
        service.invoke('alarmDetected', {
          'einsatz_id': id,
          'kuerzel': kuerzel,
          'stichwort': stichwort,
          'standort': standort,
          'user_status': userStatus,
        });

        // ── 2. Vollbild-Notification als Fallback ──
        // Öffnet die App mit dem Alarm-Screen wenn getippt
        // oder zeigt sich automatisch auf dem Sperrbildschirm.
        await notifPlugin.show(
          _alarmNotificationBaseId + id,
          '🚨 ALARM: $kuerzel',
          '$stichwort • 📍 $standort',
          const NotificationDetails(
            android: AndroidNotificationDetails(
              _alarmChannelId,
              'Alarm',
              channelDescription: 'Alarmierungen bei neuen Einsätzen',
              importance: Importance.max,
              priority: Priority.high,
              fullScreenIntent: true,
              category: AndroidNotificationCategory.alarm,
              visibility: NotificationVisibility.public,
              ticker: 'ALARM',
              playSound: true,
              sound: RawResourceAndroidNotificationSound(_alarmSoundName),
              audioAttributesUsage: AudioAttributesUsage.alarm,
              enableVibration: true,
              ongoing: true,
              autoCancel: false,
            ),
          ),
          payload: id.toString(),
        );

        // Nur einen Alarm auf einmal
        break;
      }
    } catch (e) {
      debugPrint('BG-SERVICE: Polling-Fehler: $e');
      // DB-Verbindung bei Fehler zurücksetzen
      try {
        await dbConn?.close();
      } catch (_) {}
      dbConn = null;
    } finally {
      isPolling = false;
    }
  });
}
