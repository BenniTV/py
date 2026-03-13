/// PyDispatch Mobile – Einstiegspunkt.
/// Verwaltet Setup-Flow, Alarm-Polling und Navigation.
/// Nutzt einen Foreground-Service für Alarm-Erkennung im Hintergrund.
import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_background_service/flutter_background_service.dart';
import 'config/settings.dart';
import 'database/connection.dart';
import 'models/einsatz.dart';
import 'services/alarm_service.dart';
import 'services/background_service.dart';
import 'services/device_service.dart';
import 'services/notification_service.dart';
import 'services/status_service.dart';
import 'screens/setup/setup_wizard.dart';
import 'screens/home/home_screen.dart';
import 'screens/alarm/alarm_screen.dart';
import 'theme/app_theme.dart';
import 'utils/alarm_tone.dart';

/// Ausstehende Alarm-ID (wenn App über Notification gestartet wurde).
int? _pendingAlarmId;

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Benachrichtigungen initialisieren & Berechtigung anfordern
  await NotificationService.init();
  await NotificationService.requestPermission();
  debugPrint('MAIN: Notifications initialisiert');

  // Prüfen ob App durch Alarm-Notification gestartet wurde
  final launchPayload = await NotificationService.getLaunchPayload();
  if (launchPayload != null) {
    _pendingAlarmId = int.tryParse(launchPayload);
    debugPrint('MAIN: App durch Notification gestartet, Alarm-ID: $_pendingAlarmId');
  }

  // Fallback-WAV im Hintergrund vorbereiten (compute-Isolate, blockiert UI nicht)
  // ignore: unawaited_futures
  AlarmTone.preCache();

  // Hintergrund-Service starten
  await initBackgroundService();
  debugPrint('MAIN: Hintergrund-Service konfiguriert');

  SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
    statusBarColor: Colors.transparent,
    statusBarIconBrightness: Brightness.light,
    systemNavigationBarColor: AppColors.bgDark,
    systemNavigationBarIconBrightness: Brightness.light,
  ));
  runApp(const PyDispatchMobileApp());
}

class PyDispatchMobileApp extends StatelessWidget {
  const PyDispatchMobileApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'PyDispatch Mobile',
      theme: appTheme(),
      debugShowCheckedModeBanner: false,
      builder: (context, child) {
        return DefaultTextStyle(
          style: const TextStyle(
            decoration: TextDecoration.none,
            color: AppColors.text,
          ),
          child: child!,
        );
      },
      home: const AppShell(),
    );
  }
}

/// Shell: Verwaltet den App-Zustand (Setup → Home → Alarm).
class AppShell extends StatefulWidget {
  const AppShell({super.key});

  @override
  State<AppShell> createState() => _AppShellState();
}

class _AppShellState extends State<AppShell> with WidgetsBindingObserver {
  _AppState _state = _AppState.loading;
  int? _benutzerId;
  String? _geraeteId;

  Timer? _pollTimer;
  Timer? _refreshTimer;
  final Set<int> _seenEinsatzIds = {};
  bool _alarmVisible = false;

  final _homeKey = GlobalKey<HomeScreenState>();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);

    // Notification-Tap Handler: wird aufgerufen wenn User eine
    // Alarm-Notification antippt während die App läuft
    NotificationService.onNotificationTap = _onNotificationTap;

    // Hintergrund-Service: Auf 'alarmDetected' Events hören.
    // Der Background-Service sendet dieses Event wenn er einen neuen Alarm
    // erkennt während die App minimiert ist → App zeigt vollen Alarm-Screen.
    FlutterBackgroundService().on('alarmDetected').listen((event) {
      if (event == null) return;
      final einsatzId = event['einsatz_id'];
      if (einsatzId is int && einsatzId > 0) {
        debugPrint('MAIN: alarmDetected Event erhalten, Einsatz-ID: $einsatzId');
        // Notification entfernen da wir den vollen Alarm-Screen zeigen
        NotificationService.cancel(
          NotificationService.alarmNotificationBaseId + einsatzId,
        );
        _loadAndTriggerAlarm(einsatzId);
      }
    });

    _checkState();
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _pollTimer?.cancel();
    _refreshTimer?.cancel();
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    final bgService = FlutterBackgroundService();
    if (state == AppLifecycleState.resumed) {
      // App im Vordergrund: Hintergrund-Service pausiert, App pollt selbst
      bgService.invoke('setAsForeground');
      NotificationService.cancelAll();
      _startPolling();
    } else if (state == AppLifecycleState.paused) {
      // App im Hintergrund: Seen-IDs synchronisieren, Service übernimmt
      bgService.invoke('seenIds', {'ids': _seenEinsatzIds.toList()});
      bgService.invoke('setAsBackground');
      _pollTimer?.cancel();
      _refreshTimer?.cancel();
    }
  }

  Future<void> _checkState() async {
    setState(() => _state = _AppState.loading);

    final setupDone = await AppConfig.isSetupDone();
    if (!setupDone) {
      setState(() => _state = _AppState.setup);
      return;
    }

    final cfg = await AppConfig.getMysqlConfig();
    final connected = await db.connect(
      host: cfg['host'],
      port: cfg['port'],
      user: cfg['user'],
      password: cfg['password'],
      database: cfg['database'],
    );

    if (!connected) {
      setState(() => _state = _AppState.connectionError);
      return;
    }

    final gid = await AppConfig.getGeraeteId();
    if (gid.isEmpty) {
      setState(() => _state = _AppState.setup);
      return;
    }

    final (ok, _, data) = await DeviceService.validateGeraeteId(gid);
    if (!ok || data == null) {
      setState(() => _state = _AppState.setup);
      return;
    }

    _benutzerId = _toInt(data['benutzer_id']);
    _geraeteId = gid;
    await DeviceService.updateLetzterKontakt(gid);

    final existing = await AlarmService.getActiveEinsaetze();
    final pendingId = _pendingAlarmId;
    _pendingAlarmId = null;
    for (final e in existing) {
      // Wenn App durch Notification gestartet: diese ID NICHT als "gesehen"
      // markieren, damit der Alarm-Screen beim nächsten Poll ausgelöst wird
      if (e.id != pendingId) {
        _seenEinsatzIds.add(e.id);
      }
    }

    // Hintergrund-Service: Vordergrund-Modus aktivieren
    FlutterBackgroundService().invoke('setAsForeground');
    NotificationService.cancelAll();

    setState(() => _state = _AppState.home);
    _startPolling();
  }

  void _startPolling() {
    _pollTimer?.cancel();
    _refreshTimer?.cancel();

    _pollTimer = Timer.periodic(
      const Duration(seconds: 2),
      (_) => _pollForAlarms(),
    );

    _refreshTimer = Timer.periodic(
      const Duration(seconds: 10),
      (_) => _refreshHome(),
    );
  }

  Future<void> _pollForAlarms() async {
    if (_alarmVisible || _benutzerId == null) return;

    try {
      final status = await StatusService.getStatus(_benutzerId!);
      if (status == 'nicht_in_der_schule') return;

      final active = await AlarmService.getActiveEinsaetze();
      for (final einsatz in active) {
        if (!_seenEinsatzIds.contains(einsatz.id)) {
          _seenEinsatzIds.add(einsatz.id);
          _triggerAlarm(einsatz, status);
          return;
        }
      }

      if (_geraeteId != null) {
        await DeviceService.updateLetzterKontakt(_geraeteId!);
      }
    } catch (_) {}
  }

  void _refreshHome() {
    if (_alarmVisible) return;
    _homeKey.currentState?.refreshData();
  }

  /// Wird aufgerufen wenn eine Alarm-Notification angetippt wird
  /// während die App im Vordergrund oder Hintergrund läuft.
  void _onNotificationTap(String? payload) {
    if (payload == null || _benutzerId == null || _alarmVisible) return;
    final einsatzId = int.tryParse(payload);
    if (einsatzId == null) return;

    // Notification entfernen
    NotificationService.cancel(
      NotificationService.alarmNotificationBaseId + einsatzId,
    );

    // Einsatz laden und Alarm-Screen anzeigen
    _loadAndTriggerAlarm(einsatzId);
  }

  /// Lädt einen Einsatz anhand der ID und zeigt den Alarm-Screen.
  Future<void> _loadAndTriggerAlarm(int einsatzId) async {
    if (_benutzerId == null) {
      debugPrint('MAIN: _loadAndTriggerAlarm abgebrochen – _benutzerId ist null (App noch nicht initialisiert)');
      return; // Nicht in seenIds aufnehmen → wird beim nächsten Poll gefunden
    }
    if (_alarmVisible) {
      debugPrint('MAIN: _loadAndTriggerAlarm abgebrochen – Alarm ist bereits sichtbar');
      return;
    }
    try {
      final einsaetze = await AlarmService.getActiveEinsaetze();
      final einsatz = einsaetze.where((e) => e.id == einsatzId).firstOrNull;
      if (einsatz == null) {
        debugPrint('MAIN: Einsatz $einsatzId nicht in aktiven Einsätzen gefunden');
        return;
      }

      final status = await StatusService.getStatus(_benutzerId!);
      // Erst NACH erfolgreichem Laden als "gesehen" markieren
      _seenEinsatzIds.add(einsatzId);
      _triggerAlarm(einsatz, status);
    } catch (e) {
      debugPrint('MAIN: _loadAndTriggerAlarm Fehler: $e');
    }
  }

  void _triggerAlarm(Einsatz einsatz, String userStatus) {
    if (_alarmVisible) return;

    final mode = userStatus == 'in_der_schule' ? 'full' : 'silent';
    debugPrint('MAIN: _triggerAlarm mode=$mode, status=$userStatus, '
        'einsatz=${einsatz.id}');
    setState(() => _alarmVisible = true);

    // ── Audio HIER starten (nicht im AlarmScreen!) ──
    // So bleibt der Ton auch bei einem Screen-Crash aktiv.
    if (mode == 'full') {
      AlarmTone.play().catchError((e) {
        debugPrint('MAIN: AlarmTone.play() Fehler: $e');
      });
    }

    Navigator.of(context).push(
      PageRouteBuilder(
        opaque: true,
        pageBuilder: (_, __, ___) => AlarmScreen(
          einsatz: einsatz,
          mode: mode,
          onDismiss: () {
            // ── Audio HIER stoppen (nicht im AlarmScreen!) ──
            if (mode == 'full') {
              AlarmTone.stop().catchError((e) {
                debugPrint('MAIN: AlarmTone.stop() Fehler: $e');
              });
            }
            Navigator.of(context).pop();
            setState(() => _alarmVisible = false);
            _homeKey.currentState?.refreshData();
          },
        ),
        transitionsBuilder: (_, anim, __, child) =>
            FadeTransition(opacity: anim, child: child),
        transitionDuration: const Duration(milliseconds: 200),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    switch (_state) {
      case _AppState.loading:
        return Scaffold(
          backgroundColor: AppColors.bgDark,
          body: Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: 72,
                  height: 72,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: LinearGradient(
                      colors: [AppColors.primary, AppColors.primaryDark],
                    ),
                  ),
                  child: const Center(
                    child: Text('🚒', style: TextStyle(fontSize: 32)),
                  ),
                ),
                const SizedBox(height: 24),
                const SizedBox(
                  width: 32,
                  height: 32,
                  child: CircularProgressIndicator(
                    strokeWidth: 3,
                    color: AppColors.primary,
                  ),
                ),
                const SizedBox(height: 16),
                const Text('Verbinde...',
                    style: TextStyle(
                        color: AppColors.textSecondary,
                        fontSize: 14,
                        fontWeight: FontWeight.w500)),
              ],
            ),
          ),
        );

      case _AppState.setup:
        return SetupWizard(onComplete: _checkState);

      case _AppState.connectionError:
        return Scaffold(
          backgroundColor: AppColors.bgDark,
          body: Center(
            child: Padding(
              padding: const EdgeInsets.all(32),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    width: 80,
                    height: 80,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: AppColors.danger.withValues(alpha: 0.12),
                    ),
                    child: const Center(
                      child: Icon(Icons.wifi_off_rounded,
                          size: 36, color: AppColors.danger),
                    ),
                  ),
                  const SizedBox(height: 24),
                  Text('Keine Verbindung',
                      style: Theme.of(context)
                          .textTheme
                          .titleLarge
                          ?.copyWith(fontWeight: FontWeight.w700)),
                  const SizedBox(height: 8),
                  const Text(
                    'Verbindung zur Datenbank\nfehlgeschlagen.',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                        color: AppColors.textSecondary, fontSize: 14),
                  ),
                  const SizedBox(height: 32),
                  ElevatedButton.icon(
                    onPressed: _checkState,
                    icon: const Icon(Icons.refresh_rounded),
                    label: const Text('Erneut versuchen'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppColors.primary,
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextButton(
                    onPressed: () async {
                      await AppConfig.clearAll();
                      _checkState();
                    },
                    child: const Text('Neu einrichten',
                        style: TextStyle(color: AppColors.textSecondary)),
                  ),
                ],
              ),
            ),
          ),
        );

      case _AppState.home:
        return HomeScreen(
          key: _homeKey,
          benutzerId: _benutzerId!,
        );
    }
  }

  static int _toInt(dynamic value) {
    if (value is int) return value;
    if (value is String) return int.tryParse(value) ?? 0;
    return 0;
  }
}

enum _AppState { loading, setup, connectionError, home }
