import 'duty_status.dart';

class AppConfig {
  const AppConfig({
    required this.host,
    required this.port,
    required this.user,
    required this.password,
    required this.database,
    required this.deviceId,
    required this.status,
  });

  final String host;
  final String port;
  final String user;
  final String password;
  final String database;
  final String deviceId;
  final DutyStatus status;

  AppConfig copyWith({
    String? host,
    String? port,
    String? user,
    String? password,
    String? database,
    String? deviceId,
    DutyStatus? status,
  }) {
    return AppConfig(
      host: host ?? this.host,
      port: port ?? this.port,
      user: user ?? this.user,
      password: password ?? this.password,
      database: database ?? this.database,
      deviceId: deviceId ?? this.deviceId,
      status: status ?? this.status,
    );
  }

  Map<String, String> toMap() {
    return {
      'host': host,
      'port': port,
      'user': user,
      'password': password,
      'database': database,
      'deviceId': deviceId,
      'status': status.dbValue,
    };
  }

  static AppConfig fromMap(Map<String, String> map) {
    return AppConfig(
      host: map['host'] ?? '',
      port: map['port'] ?? '3306',
      user: map['user'] ?? '',
      password: map['password'] ?? '',
      database: map['database'] ?? '',
      deviceId: map['deviceId'] ?? '',
      status: DutyStatusX.fromDbValue(map['status'] ?? 'not_in_school'),
    );
  }
}
