import '../models/alarm_event.dart';
import '../models/app_config.dart';
import '../models/device_binding_result.dart';
import '../models/duty_snapshot.dart';
import '../models/duty_status.dart';

abstract class MobileRepository {
  Future<DeviceBindingResult> validateAndBindDevice(AppConfig config);

  Future<DutySnapshot> fetchDutySnapshot(AppConfig config);

  Future<void> updateDutyStatus(AppConfig config, DutyStatus status);

  Future<void> syncAlarmCursor(AppConfig config);

  Stream<AlarmEvent> subscribeToAlarms(AppConfig config);
}
