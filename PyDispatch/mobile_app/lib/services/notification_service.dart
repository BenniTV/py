/// PyDispatch Mobile – Notification-Service.
/// Lokale Benachrichtigungen für Alarm-Meldungen.
/// Zeigt Vollbild-Notifications mit Ton und Vibration bei neuen Einsätzen.
import 'dart:typed_data';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';

class NotificationService {
  static final FlutterLocalNotificationsPlugin _plugin =
      FlutterLocalNotificationsPlugin();
  static const _alarmSoundName = 'alarm';

  /// Callback wenn eine Alarm-Notification angetippt wird.
  /// Payload = Einsatz-ID als String.
  static Function(String? payload)? onNotificationTap;

  /// Notification-Channel-IDs.
  static const alarmChannelId = 'pydispatch_alarm_v2';
  static const _alarmChannelName = 'Alarm';
  static const _alarmChannelDesc = 'Alarmierungen bei neuen Einsätzen';

  /// Basis-ID für Alarm-Notifications (+ Einsatz-ID).
  static const alarmNotificationBaseId = 9000;

  /// Initialisiert das Notification-Plugin und erstellt die Channels.
  static Future<void> init() async {
    const androidSettings =
        AndroidInitializationSettings('@mipmap/ic_launcher');
    const settings = InitializationSettings(android: androidSettings);

    await _plugin.initialize(
      settings,
      onDidReceiveNotificationResponse: (response) {
        onNotificationTap?.call(response.payload);
      },
    );

    // Alarm-Notification-Channel erstellen (maximale Priorität)
    final androidPlugin = _plugin.resolvePlatformSpecificImplementation<
        AndroidFlutterLocalNotificationsPlugin>();
    await androidPlugin?.createNotificationChannel(
      const AndroidNotificationChannel(
        alarmChannelId,
        _alarmChannelName,
        description: _alarmChannelDesc,
        importance: Importance.max,
        playSound: true,
        sound: RawResourceAndroidNotificationSound(_alarmSoundName),
        audioAttributesUsage: AudioAttributesUsage.alarm,
        enableVibration: true,
        enableLights: true,
      ),
    );
  }

  /// Prüft ob die App durch eine Alarm-Notification gestartet wurde.
  /// Gibt die Payload (Einsatz-ID) zurück, falls ja.
  static Future<String?> getLaunchPayload() async {
    final details = await _plugin.getNotificationAppLaunchDetails();
    if (details?.didNotificationLaunchApp ?? false) {
      return details?.notificationResponse?.payload;
    }
    return null;
  }

  /// Zeigt eine Alarm-Notification mit maximaler Priorität.
  /// fullScreenIntent weckt das Display und zeigt die Notification im Vollbild.
  static Future<void> showAlarmNotification({
    required int id,
    required String title,
    required String body,
    String? payload,
  }) async {
    final androidDetails = AndroidNotificationDetails(
      alarmChannelId,
      _alarmChannelName,
      channelDescription: _alarmChannelDesc,
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
      vibrationPattern: Int64List.fromList(
        [0, 500, 200, 500, 200, 500, 200, 500],
      ),
      ongoing: true,
      autoCancel: false,
    );

    await _plugin.show(
      id,
      title,
      body,
      NotificationDetails(android: androidDetails),
      payload: payload,
    );
  }

  /// Entfernt eine bestimmte Notification.
  static Future<void> cancel(int id) async {
    await _plugin.cancel(id);
  }

  /// Entfernt alle Notifications.
  static Future<void> cancelAll() async {
    await _plugin.cancelAll();
  }

  /// Fordert die Notification-Berechtigung an (Android 13+).
  static Future<bool> requestPermission() async {
    final androidPlugin = _plugin.resolvePlatformSpecificImplementation<
        AndroidFlutterLocalNotificationsPlugin>();
    final granted = await androidPlugin?.requestNotificationsPermission();
    return granted ?? false;
  }
}
