/// PyDispatch Mobile – Geräte-Service.
/// Validiert die Geräte-ID und holt Benutzer-Informationen.
import '../database/connection.dart';

class DeviceService {
  /// Prüft, ob die Geräte-ID in der DB existiert und aktiv ist.
  /// Gibt (success, message, deviceData) zurück.
  static Future<(bool, String, Map<String, dynamic>?)> validateGeraeteId(
      String geraeteId) async {
    try {
      final rows = await db.execute(
        'SELECT mg.id, mg.geraete_id, mg.name AS geraet_name, mg.ist_aktiv, '
        'mg.benutzer_id, b.benutzername, b.vorname, b.nachname, b.rolle, '
        'b.ist_aktiv AS benutzer_aktiv, b.status '
        'FROM mobile_geraete mg '
        'LEFT JOIN benutzer b ON mg.benutzer_id = b.id '
        'WHERE mg.geraete_id = :id',
        {'id': geraeteId},
      );
      if (rows.isEmpty) {
        return (false, 'Geräte-ID nicht gefunden.', null);
      }
      final device = rows.first;
      final istAktiv = _toBool(device['ist_aktiv']);
      if (!istAktiv) {
        return (false, 'Dieses Gerät ist deaktiviert.', null);
      }
      if (device['benutzer_id'] == null) {
        return (false, 'Kein Benutzer zugeordnet.', null);
      }
      final benutzerAktiv = _toBool(device['benutzer_aktiv']);
      if (!benutzerAktiv) {
        return (false, 'Der zugeordnete Benutzer ist deaktiviert.', null);
      }
      return (true, 'Gerät verifiziert.', device);
    } catch (e) {
      return (false, 'Fehler: $e', null);
    }
  }

  /// Aktualisiert den letzten Kontakt-Zeitstempel.
  static Future<void> updateLetzterKontakt(String geraeteId) async {
    try {
      await db.executeModify(
        'UPDATE mobile_geraete SET letzter_kontakt = NOW() '
        'WHERE geraete_id = :id',
        {'id': geraeteId},
      );
    } catch (_) {}
  }

  /// Holt aktuelle Benutzer-Informationen.
  static Future<Map<String, dynamic>?> getUserInfo(int benutzerId) async {
    try {
      final rows = await db.execute(
        'SELECT id, benutzername, vorname, nachname, status, ist_aktiv '
        'FROM benutzer WHERE id = :id',
        {'id': benutzerId.toString()},
      );
      return rows.isNotEmpty ? rows.first : null;
    } catch (_) {
      return null;
    }
  }

  /// Gibt den Einrichtungsnamen zurück.
  static Future<String> getEinrichtungName() async {
    try {
      final rows = await db.execute('SELECT name FROM einrichtung LIMIT 1');
      return rows.isNotEmpty
          ? rows.first['name']?.toString() ?? 'PyDispatch'
          : 'PyDispatch';
    } catch (_) {
      return 'PyDispatch';
    }
  }

  static bool _toBool(dynamic value) {
    if (value is bool) return value;
    if (value is int) return value == 1;
    if (value is String) return value == '1' || value.toLowerCase() == 'true';
    return true;
  }
}
