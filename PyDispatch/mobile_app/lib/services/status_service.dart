/// PyDispatch Mobile – Status-Service.
/// Verwaltet den Benutzer-Status und liest Gruppen-Informationen.
import '../database/connection.dart';
import '../models/user.dart';

class StatusService {
  /// Setzt den Benutzer-Status.
  static Future<(bool, String)> setStatus(int benutzerId, String status) async {
    const valid = ['in_der_schule', 'nicht_in_der_schule', 'klassenarbeit'];
    if (!valid.contains(status)) {
      return (false, 'Ungültiger Status: $status');
    }
    try {
      final ok = await db.executeModify(
        'UPDATE benutzer SET status = :status WHERE id = :id',
        {'status': status, 'id': benutzerId.toString()},
      );
      return ok
          ? (true, 'Status aktualisiert.')
          : (false, 'Fehler beim Aktualisieren.');
    } catch (e) {
      return (false, 'Fehler: $e');
    }
  }

  /// Gibt den aktuellen Status des Benutzers zurück.
  static Future<String> getStatus(int benutzerId) async {
    try {
      final rows = await db.execute(
        'SELECT status FROM benutzer WHERE id = :id',
        {'id': benutzerId.toString()},
      );
      return rows.isNotEmpty
          ? rows.first['status']?.toString() ?? 'nicht_in_der_schule'
          : 'nicht_in_der_schule';
    } catch (_) {
      return 'nicht_in_der_schule';
    }
  }

  /// Gibt die aktuell aktive Gruppe zurück.
  static Future<Map<String, dynamic>?> getActiveGroup() async {
    try {
      final rows = await db.execute(
        'SELECT ag.gruppen_id, bg.name, ag.gesetzt_am '
        'FROM aktive_gruppe ag '
        'JOIN benutzergruppen bg ON ag.gruppen_id = bg.id '
        'WHERE ag.id = 1',
      );
      return rows.isNotEmpty ? rows.first : null;
    } catch (_) {
      return null;
    }
  }

  /// Prüft, ob der Benutzer in der aktiven Gruppe ist.
  static Future<bool> isUserInActiveGroup(int benutzerId) async {
    try {
      final group = await getActiveGroup();
      if (group == null) return false;
      final rows = await db.execute(
        'SELECT 1 FROM benutzer_gruppen '
        'WHERE benutzer_id = :uid AND gruppen_id = :gid',
        {
          'uid': benutzerId.toString(),
          'gid': group['gruppen_id'].toString(),
        },
      );
      return rows.isNotEmpty;
    } catch (_) {
      return false;
    }
  }

  /// Gibt alle Mitglieder der aktiven Gruppe zurück.
  static Future<List<AppUser>> getGroupMembers() async {
    try {
      final group = await getActiveGroup();
      if (group == null) return [];
      final rows = await db.execute(
        'SELECT b.id, b.vorname, b.nachname, b.benutzername, b.status, b.ist_aktiv '
        'FROM benutzer b '
        'JOIN benutzer_gruppen bg ON b.id = bg.benutzer_id '
        'WHERE bg.gruppen_id = :gid AND b.ist_aktiv = TRUE '
        'ORDER BY b.nachname, b.vorname',
        {'gid': group['gruppen_id'].toString()},
      );
      return rows.map((r) => AppUser.fromMap(r)).toList();
    } catch (_) {
      return [];
    }
  }
}
