import 'package:shared_preferences/shared_preferences.dart';

import '../models/app_config.dart';
import '../models/duty_status.dart';

class ConfigService {
  static const _hostKey = 'host';
  static const _portKey = 'port';
  static const _userKey = 'user';
  static const _passwordKey = 'password';
  static const _databaseKey = 'database';
  static const _deviceIdKey = 'deviceId';
  static const _statusKey = 'status';

  Future<AppConfig?> load() async {
    final prefs = await SharedPreferences.getInstance();
    final host = prefs.getString(_hostKey);
    final deviceId = prefs.getString(_deviceIdKey);
    if (host == null || host.isEmpty || deviceId == null || deviceId.isEmpty) {
      return null;
    }

    return AppConfig(
      host: host,
      port: prefs.getString(_portKey) ?? '3306',
      user: prefs.getString(_userKey) ?? '',
      password: prefs.getString(_passwordKey) ?? '',
      database: prefs.getString(_databaseKey) ?? '',
      deviceId: deviceId,
      status: DutyStatusX.fromDbValue(prefs.getString(_statusKey) ?? 'not_in_school'),
    );
  }

  Future<void> save(AppConfig config) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_hostKey, config.host);
    await prefs.setString(_portKey, config.port);
    await prefs.setString(_userKey, config.user);
    await prefs.setString(_passwordKey, config.password);
    await prefs.setString(_databaseKey, config.database);
    await prefs.setString(_deviceIdKey, config.deviceId);
    await prefs.setString(_statusKey, config.status.dbValue);
  }

  Future<void> saveStatus(DutyStatus status) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_statusKey, status.dbValue);
  }

  Future<void> clear() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_hostKey);
    await prefs.remove(_portKey);
    await prefs.remove(_userKey);
    await prefs.remove(_passwordKey);
    await prefs.remove(_databaseKey);
    await prefs.remove(_deviceIdKey);
    await prefs.remove(_statusKey);
  }
}
