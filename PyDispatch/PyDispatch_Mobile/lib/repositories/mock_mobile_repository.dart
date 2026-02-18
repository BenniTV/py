import 'dart:async';

import '../models/alarm_event.dart';
import '../models/app_config.dart';
import '../models/device_binding_result.dart';
import '../models/duty_snapshot.dart';
import '../models/duty_status.dart';
import 'mobile_repository.dart';

class MockMobileRepository implements MobileRepository {
  final StreamController<AlarmEvent> _controller = StreamController<AlarmEvent>.broadcast();

  @override
  Future<DeviceBindingResult> validateAndBindDevice(AppConfig config) async {
    await Future<void>.delayed(const Duration(milliseconds: 300));
    if (config.deviceId.trim().isEmpty) {
      return const DeviceBindingResult(success: false, message: 'Geräte-ID fehlt');
    }
    return const DeviceBindingResult(success: true, message: 'Gerät erfolgreich gebunden');
  }

  @override
  Future<DutySnapshot> fetchDutySnapshot(AppConfig config) async {
    await Future<void>.delayed(const Duration(milliseconds: 250));
    return const DutySnapshot(
      activeGroupName: 'Gruppe A',
      userName: 'Max Mustermann',
      teammates: ['Anna', 'Lukas', 'Mia'],
      isOnDutyThisWeek: true,
    );
  }

  @override
  Future<void> updateDutyStatus(AppConfig config, DutyStatus status) async {
    await Future<void>.delayed(const Duration(milliseconds: 150));
  }

  @override
  Future<void> syncAlarmCursor(AppConfig config) async {
    await Future<void>.delayed(const Duration(milliseconds: 50));
  }

  @override
  Stream<AlarmEvent> subscribeToAlarms(AppConfig config) => _controller.stream;
}
