/// PyDispatch Mobile – MySQL-Datenbankverbindung.
/// Singleton-Pattern für die Verbindung zur gemeinsamen Datenbank.
import 'package:mysql_client/mysql_client.dart';

class DatabaseConnection {
  static DatabaseConnection? _instance;
  MySQLConnection? _connection;

  DatabaseConnection._();

  static DatabaseConnection get instance {
    _instance ??= DatabaseConnection._();
    return _instance!;
  }

  bool get isConnected => _connection != null;

  /// Verbindung herstellen.
  Future<bool> connect({
    required String host,
    required int port,
    required String user,
    required String password,
    required String database,
  }) async {
    try {
      await disconnect();
      _connection = await MySQLConnection.createConnection(
        host: host,
        port: port,
        userName: user,
        password: password,
        databaseName: database,
        secure: false,
      );
      await _connection!.connect();
      return true;
    } catch (e) {
      _connection = null;
      return false;
    }
  }

  /// Verbindung testen (kurzfristig verbinden und trennen).
  Future<(bool, String)> testConnection({
    required String host,
    required int port,
    required String user,
    required String password,
    required String database,
  }) async {
    try {
      final conn = await MySQLConnection.createConnection(
        host: host,
        port: port,
        userName: user,
        password: password,
        databaseName: database,
        secure: false,
      );
      await conn.connect();
      await conn.close();
      return (true, 'Verbindung erfolgreich.');
    } catch (e) {
      return (false, 'Verbindungsfehler: $e');
    }
  }

  /// SELECT-Abfrage ausführen.
  Future<List<Map<String, dynamic>>> execute(
    String query, [
    Map<String, dynamic>? params,
  ]) async {
    try {
      if (_connection == null) return [];
      final result = await _connection!.execute(query, params ?? {});
      final rows = <Map<String, dynamic>>[];
      for (final row in result.rows) {
        rows.add(row.typedAssoc());
      }
      return rows;
    } catch (e) {
      return [];
    }
  }

  /// INSERT/UPDATE/DELETE ausführen.
  Future<bool> executeModify(
    String query, [
    Map<String, dynamic>? params,
  ]) async {
    try {
      if (_connection == null) return false;
      await _connection!.execute(query, params ?? {});
      return true;
    } catch (e) {
      return false;
    }
  }

  /// INSERT ausführen und die neue ID zurückgeben.
  Future<int?> executeInsert(
    String query, [
    Map<String, dynamic>? params,
  ]) async {
    try {
      if (_connection == null) return null;
      final result = await _connection!.execute(query, params ?? {});
      return result.lastInsertID.toInt();
    } catch (e) {
      return null;
    }
  }

  /// Verbindung trennen.
  Future<void> disconnect() async {
    try {
      await _connection?.close();
    } catch (_) {}
    _connection = null;
  }
}

/// Globaler Zugriff.
final db = DatabaseConnection.instance;
