import 'dart:async';

import 'package:flutter/material.dart';

import '../models/alarm_event.dart';
import '../models/app_config.dart';
import '../models/duty_snapshot.dart';
import '../models/duty_status.dart';
import '../repositories/mobile_repository.dart';
import '../services/alarm_feedback_service.dart';
import '../widgets/alarm_detail_sheet.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({
    super.key,
    required this.initialConfig,
    required this.repository,
    required this.onConfigChanged,
    required this.onReconfigure,
  });

  final AppConfig initialConfig;
  final MobileRepository repository;
  final ValueChanged<AppConfig> onConfigChanged;
  final Future<void> Function() onReconfigure;

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  late AppConfig _config;
  DutySnapshot? _snapshot;
  AlarmEvent? _activeAlarm;
  StreamSubscription<AlarmEvent>? _alarmSubscription;
  final _feedbackService = AlarmFeedbackService();
  bool _loading = true;
  String? _loadError;

  String _friendlyError(String rawError) {
    final lower = rawError.toLowerCase();
    if (lower.contains('failed host lookup') || lower.contains('no address associated with hostname') || lower.contains('errno = 7')) {
      return 'Host konnte nicht aufgelöst werden.\nPrüfe Host/IP in der Einrichtung (z. B. 135.125.201.14 statt Name).';
    }
    if (lower.contains('connection refused')) {
      return 'Verbindung abgelehnt. Läuft der MySQL-Server und ist der Port korrekt?';
    }
    if (lower.contains('access denied')) {
      return 'DB-Zugangsdaten sind ungültig (Benutzer/Passwort).';
    }
    return rawError;
  }

  @override
  void initState() {
    super.initState();
    _config = widget.initialConfig;
    _loadData();
    widget.repository.syncAlarmCursor(_config);
    _subscribeToAlarms();
  }

  @override
  void dispose() {
    _alarmSubscription?.cancel();
    super.dispose();
  }

  Future<void> _loadData() async {
    try {
      final snapshot = await widget.repository.fetchDutySnapshot(_config);
      if (!mounted) {
        return;
      }
      setState(() {
        _snapshot = snapshot;
        _loading = false;
        _loadError = null;
      });
    } catch (e) {
      if (!mounted) {
        return;
      }
      setState(() {
        _loading = false;
        _loadError = e.toString();
      });
    }
  }

  void _subscribeToAlarms() {
    _alarmSubscription = widget.repository.subscribeToAlarms(_config).listen((alarm) async {
      if (!mounted) {
        return;
      }

      if (_config.status == DutyStatus.notInSchool) {
        return;
      }

      if (_config.status != DutyStatus.classwork) {
        setState(() {
          _activeAlarm = alarm;
        });
      }

      unawaited(_feedbackService.playForStatus(_config.status));
    });
  }

  Future<void> _updateStatus(DutyStatus status) async {
    try {
      await widget.repository.updateDutyStatus(_config, status);
      await widget.repository.syncAlarmCursor(_config);
    } catch (e) {
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Status konnte nicht gespeichert werden: $e')),
      );
      return;
    }

    final next = _config.copyWith(status: status);

    if (!mounted) {
      return;
    }

    setState(() {
      _config = next;
    });
    widget.onConfigChanged(next);
    _loadData();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('PyDispatch Mobile')),
      body: Stack(
        children: [
          if (_loading)
            const Center(child: CircularProgressIndicator())
          else if (_loadError != null)
            Center(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.error_outline, size: 42, color: Colors.red),
                    const SizedBox(height: 10),
                    Text('Daten konnten nicht geladen werden:\n${_friendlyError(_loadError!)}', textAlign: TextAlign.center),
                    const SizedBox(height: 12),
                    FilledButton(onPressed: _loadData, child: const Text('Erneut versuchen')),
                    const SizedBox(height: 8),
                    OutlinedButton(
                      onPressed: () => widget.onReconfigure(),
                      child: const Text('Verbindung neu einrichten'),
                    ),
                  ],
                ),
              ),
            )
          else
            RefreshIndicator(
              onRefresh: _loadData,
              child: ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  _buildDutyCard(),
                  const SizedBox(height: 12),
                  _buildCurrentModeCard(),
                  const SizedBox(height: 12),
                  _buildStatusButtons(),
                  const SizedBox(height: 12),
                  _buildTeammatesCard(),
                ],
              ),
            ),
          if (_activeAlarm != null)
            Positioned(
              left: 0,
              right: 0,
              bottom: 0,
              child: AlarmDetailSheet(
                alarm: _activeAlarm!,
                onDismiss: () {
                  setState(() {
                    _activeAlarm = null;
                  });
                },
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildDutyCard() {
    final snapshot = _snapshot;
    if (snapshot == null) {
      return const SizedBox.shrink();
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Schichtstatus', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Text('Aktive Gruppe: ${snapshot.activeGroupName}'),
            Text('Diese Woche dran: ${snapshot.isOnDutyThisWeek ? 'Ja' : 'Nein'}'),
            Text('Nutzer: ${snapshot.userName}'),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusButtons() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Status', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            _statusButton(DutyStatus.inSchool, Colors.green),
            const SizedBox(height: 8),
            _statusButton(DutyStatus.notInSchool, Colors.grey.shade700),
            const SizedBox(height: 8),
            _statusButton(DutyStatus.classwork, Colors.orange.shade700),
          ],
        ),
      ),
    );
  }

  Widget _buildCurrentModeCard() {
    Color color;
    String subtitle;

    switch (_config.status) {
      case DutyStatus.inSchool:
        color = Colors.green.shade700;
        subtitle = 'Du erhältst volle Alarmierung (Ton/Vibration/Licht).';
        break;
      case DutyStatus.notInSchool:
        color = Colors.grey.shade700;
        subtitle = 'Du wirst nicht alarmiert.';
        break;
      case DutyStatus.classwork:
        color = Colors.orange.shade700;
        subtitle = 'Nur Lichtsignal bei Alarm (Klassenarbeitsmodus).';
        break;
    }

    return Card(
      color: color,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Aktueller Modus',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white),
            ),
            const SizedBox(height: 6),
            Text(
              _config.status.label,
              style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.white),
            ),
            const SizedBox(height: 4),
            Text(subtitle, style: const TextStyle(color: Colors.white)),
          ],
        ),
      ),
    );
  }

  Widget _statusButton(DutyStatus status, Color color) {
    final isSelected = _config.status == status;
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton(
        onPressed: () => _updateStatus(status),
        style: ElevatedButton.styleFrom(
          backgroundColor: color,
          foregroundColor: Colors.white,
          elevation: isSelected ? 1 : 0,
          padding: const EdgeInsets.symmetric(vertical: 14),
        ),
        child: Text(status.label),
      ),
    );
  }

  Widget _buildTeammatesCard() {
    final teammates = _snapshot?.teammates ?? const <String>[];
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Team', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            if (teammates.isEmpty)
              const Text('Keine Teamdaten verfügbar')
            else
              ...teammates.map((name) => Text('• $name')),
          ],
        ),
      ),
    );
  }
}
