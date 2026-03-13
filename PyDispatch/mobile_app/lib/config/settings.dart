/// PyDispatch Mobile – Lokale Konfiguration.
/// Speichert MySQL-Verbindungsdaten und Geräte-ID mit SharedPreferences.
import 'package:shared_preferences/shared_preferences.dart';

class AppConfig {
  static const _keyHost = 'mysql_host';
  static const _keyPort = 'mysql_port';
  static const _keyUser = 'mysql_user';
  static const _keyPassword = 'mysql_password';
  static const _keyDatabase = 'mysql_database';
  static const _keyGeraeteId = 'geraete_id';
  static const _keySetupDone = 'setup_done';

  // ── Setup-Status ──

  static Future<bool> isSetupDone() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getBool(_keySetupDone) ?? false;
  }

  static Future<void> setSetupDone(bool done) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_keySetupDone, done);
  }

  // ── MySQL-Konfiguration ──

  static Future<Map<String, dynamic>> getMysqlConfig() async {
    final prefs = await SharedPreferences.getInstance();
    return {
      'host': prefs.getString(_keyHost) ?? 'localhost',
      'port': prefs.getInt(_keyPort) ?? 3306,
      'user': prefs.getString(_keyUser) ?? '',
      'password': prefs.getString(_keyPassword) ?? '',
      'database': prefs.getString(_keyDatabase) ?? 'pydispatch',
    };
  }

  static Future<void> saveMysqlConfig({
    required String host,
    required int port,
    required String user,
    required String password,
    required String database,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keyHost, host);
    await prefs.setInt(_keyPort, port);
    await prefs.setString(_keyUser, user);
    await prefs.setString(_keyPassword, password);
    await prefs.setString(_keyDatabase, database);
  }

  // ── Geräte-ID ──

  static Future<String> getGeraeteId() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_keyGeraeteId) ?? '';
  }

  static Future<void> saveGeraeteId(String id) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keyGeraeteId, id);
  }

  // ── Alles zurücksetzen ──

  static Future<void> clearAll() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
  }
}
