import 'dart:async';
import 'dart:convert';

import 'package:mysql_client/mysql_client.dart';

import '../models/alarm_event.dart';
import '../models/app_config.dart';
import '../models/device_binding_result.dart';
import '../models/duty_snapshot.dart';
import '../models/duty_status.dart';
import 'mobile_repository.dart';

class MysqlMobileRepository implements MobileRepository {
  int? _lastSeenAlarmId;
  static const Duration _dbTimeout = Duration(seconds: 6);

  Future<T> _withTimeout<T>(Future<T> future, {String context = 'DB operation'}) {
    return future.timeout(
      _dbTimeout,
      onTimeout: () => throw Exception('$context timeout after ${_dbTimeout.inSeconds}s'),
    );
  }

  Future<MySQLConnection> _connect(AppConfig config) async {
    final conn = await _withTimeout(
      MySQLConnection.createConnection(
        host: config.host,
        port: int.tryParse(config.port) ?? 3306,
        userName: config.user,
        password: config.password,
        databaseName: config.database,
        secure: false,
      ),
      context: 'DB connection create',
    );
    await _withTimeout(conn.connect(), context: 'DB connect');
    return conn;
  }

  int _dbStatusFromDuty(DutyStatus status) {
    switch (status) {
      case DutyStatus.inSchool:
        return 1;
      case DutyStatus.notInSchool:
        return 0;
      case DutyStatus.classwork:
        return 1;
    }
  }

  Future<_DeviceContext?> _loadDeviceContext(MySQLConnection conn, String deviceId) async {
    final result = await _withTimeout(
      conn.execute(
      '''
      SELECT d.id AS device_pk, d.device_id, d.user_id, u.username, u.group_id, g.name AS group_name
      FROM devices d
      LEFT JOIN users u ON u.id = d.user_id
      LEFT JOIN user_groups g ON g.id = u.group_id
      WHERE d.device_id = :deviceId AND d.is_active = TRUE
      LIMIT 1
      ''',
      {'deviceId': deviceId},
    ), context: 'Load device context');

    final row = result.rows.isEmpty ? null : result.rows.first.assoc();
    if (row == null) {
      return null;
    }

    final userId = int.tryParse(row['user_id'] ?? '');
    if (userId == null) {
      return null;
    }

    return _DeviceContext(
      userId: userId,
      userName: row['username'] ?? 'Unbekannt',
      groupId: int.tryParse(row['group_id'] ?? ''),
      groupName: row['group_name'] ?? 'Keine Gruppe',
    );
  }

  Future<int?> _resolveActiveGroupId(MySQLConnection conn) async {
    final activeSetting = await _withTimeout(
      conn.execute(
        "SELECT setting_value FROM settings WHERE setting_key = 'active_group_id' LIMIT 1",
      ),
      context: 'Load active group setting',
    );

    final settingRow = activeSetting.rows.isEmpty ? null : activeSetting.rows.first.assoc();
    final activeGroupId = int.tryParse(settingRow?['setting_value'] ?? '');
    if (activeGroupId != null) {
      return activeGroupId;
    }

    final fallback = await _withTimeout(
      conn.execute(
      '''
      SELECT id
      FROM user_groups
      ORDER BY priority DESC, name ASC
      LIMIT 1
      ''',
    ), context: 'Load fallback active group');
    final fallbackRow = fallback.rows.isEmpty ? null : fallback.rows.first.assoc();
    return int.tryParse(fallbackRow?['id'] ?? '');
  }

  Future<String> _resolveActiveGroupName(MySQLConnection conn, int? activeGroupId) async {
    if (activeGroupId == null) {
      return 'Keine Gruppe';
    }

    final result = await _withTimeout(
      conn.execute(
        'SELECT name FROM user_groups WHERE id = :id LIMIT 1',
        {'id': activeGroupId},
      ),
      context: 'Load active group name',
    );

    final row = result.rows.isEmpty ? null : result.rows.first.assoc();
    return row?['name'] ?? 'Keine Gruppe';
  }

  Future<List<String>> _loadTeammates(MySQLConnection conn, int? activeGroupId) async {
    if (activeGroupId == null) {
      return <String>[];
    }

    final result = await _withTimeout(
      conn.execute(
      '''
      SELECT username
      FROM users
      WHERE is_active = TRUE AND group_id = :groupId
      ORDER BY username ASC
      ''',
      {'groupId': activeGroupId},
    ), context: 'Load teammates');

    return result.rows.map((row) => row.assoc()['username'] ?? '').where((name) => name.isNotEmpty).toList();
  }

  Future<int?> _latestAlarmId(MySQLConnection conn) async {
    final result = await _withTimeout(
      conn.execute('SELECT id FROM alarms ORDER BY id DESC LIMIT 1'),
      context: 'Load latest alarm id',
    );
    final row = result.rows.isEmpty ? null : result.rows.first.assoc();
    return int.tryParse(row?['id'] ?? '');
  }

  @override
  Future<DeviceBindingResult> validateAndBindDevice(AppConfig config) async {
    try {
      final conn = await _connect(config);
      try {
        final context = await _loadDeviceContext(conn, config.deviceId);
        if (context == null) {
          return const DeviceBindingResult(
            success: false,
            message: 'Geräte-ID nicht gefunden oder keinem aktiven Benutzer zugewiesen',
          );
        }
        return DeviceBindingResult(success: true, message: 'Gerät gebunden: ${context.userName}');
      } finally {
        await conn.close();
      }
    } catch (e) {
      return DeviceBindingResult(success: false, message: 'Verbindung fehlgeschlagen: $e');
    }
  }

  @override
  Future<DutySnapshot> fetchDutySnapshot(AppConfig config) async {
    final conn = await _connect(config);
    try {
      final context = await _loadDeviceContext(conn, config.deviceId);
      if (context == null) {
        return const DutySnapshot(
          activeGroupName: 'Unbekannt',
          userName: 'Unbekannt',
          teammates: <String>[],
          isOnDutyThisWeek: false,
        );
      }

      final activeGroupId = await _resolveActiveGroupId(conn);
      final activeGroupName = await _resolveActiveGroupName(conn, activeGroupId);
      final teammates = await _loadTeammates(conn, activeGroupId);
      final isOnDuty = context.groupId != null && activeGroupId != null && context.groupId == activeGroupId;

      return DutySnapshot(
        activeGroupName: activeGroupName,
        userName: context.userName,
        teammates: teammates,
        isOnDutyThisWeek: isOnDuty,
      );
    } finally {
      await conn.close();
    }
  }

  @override
  Future<void> updateDutyStatus(AppConfig config, DutyStatus status) async {
    final conn = await _connect(config);
    try {
      final context = await _loadDeviceContext(conn, config.deviceId);
      if (context == null) {
        return;
      }

      await _withTimeout(
        conn.execute(
          'UPDATE users SET status = :status WHERE id = :id',
          {
            'status': _dbStatusFromDuty(status),
            'id': context.userId,
          },
        ),
        context: 'Update duty status',
      );
    } finally {
      await conn.close();
    }
  }

  @override
  Future<void> syncAlarmCursor(AppConfig config) async {
    final conn = await _connect(config);
    try {
      _lastSeenAlarmId = await _latestAlarmId(conn) ?? _lastSeenAlarmId;
    } finally {
      await conn.close();
    }
  }

  @override
  Stream<AlarmEvent> subscribeToAlarms(AppConfig config) async* {
    while (true) {
      try {
        final conn = await _connect(config);
        try {
          final context = await _loadDeviceContext(conn, config.deviceId);
          if (context == null) {
            await Future<void>.delayed(const Duration(seconds: 3));
            continue;
          }

          _lastSeenAlarmId ??= await _latestAlarmId(conn);

          final result = await _withTimeout(
            conn.execute(
            '''
            SELECT id, keyword_name, location_text, alerted_user_ids, created_at
            FROM alarms
            WHERE id > :lastId
            ORDER BY id ASC
            LIMIT 20
            ''',
            {
              'lastId': _lastSeenAlarmId ?? 0,
            },
          ), context: 'Poll alarms');

          for (final row in result.rows) {
            final data = row.assoc();
            final alarmId = int.tryParse(data['id'] ?? '');
            if (alarmId == null) {
              continue;
            }
            _lastSeenAlarmId = alarmId;

            final idsRaw = data['alerted_user_ids'] ?? '[]';
            List<dynamic> ids;
            try {
              ids = jsonDecode(idsRaw) as List<dynamic>;
            } catch (_) {
              ids = <dynamic>[];
            }

            final isRecipient = ids.any((id) => id.toString() == context.userId.toString());
            if (!isRecipient) {
              continue;
            }

            final createdAt = DateTime.tryParse(data['created_at'] ?? '') ?? DateTime.now();

            yield AlarmEvent(
              id: alarmId.toString(),
              keyword: data['keyword_name'] ?? 'Alarm',
              location: data['location_text'] ?? '',
              createdAt: createdAt,
            );
          }
        } finally {
          await conn.close();
        }
      } catch (_) {}

      await Future<void>.delayed(const Duration(seconds: 2));
    }
  }
}

class _DeviceContext {
  const _DeviceContext({
    required this.userId,
    required this.userName,
    required this.groupId,
    required this.groupName,
  });

  final int userId;
  final String userName;
  final int? groupId;
  final String groupName;
}
