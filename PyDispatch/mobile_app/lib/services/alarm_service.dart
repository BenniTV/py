/// PyDispatch Mobile – Alarm-Service.
/// Erkennt neue Einsätze und liefert Alarm-Informationen.
import '../database/connection.dart';
import '../models/einsatz.dart';

class AlarmService {
  /// Gibt alle aktiven Einsätze zurück.
  static Future<List<Einsatz>> getActiveEinsaetze() async {
    try {
      final rows = await db.execute(
        'SELECT e.id, e.stichwort_id, e.standort_text, e.standort_id, '
        'e.alarmiert_am, e.status, e.notiz, '
        'sw.kuerzel, sw.bezeichnung AS stichwort_name, sw.kategorie, '
        's.name AS standort_name '
        'FROM einsaetze e '
        'JOIN stichwoerter sw ON e.stichwort_id = sw.id '
        'LEFT JOIN standorte s ON e.standort_id = s.id '
        'WHERE e.status = :status '
        'ORDER BY e.alarmiert_am DESC',
        {'status': 'aktiv'},
      );
      return rows.map((r) => Einsatz.fromMap(r)).toList();
    } catch (_) {
      return [];
    }
  }

  /// Gibt den neuesten aktiven Einsatz zurück.
  static Future<Einsatz?> getLatestEinsatz() async {
    try {
      final rows = await db.execute(
        'SELECT e.id, e.stichwort_id, e.standort_text, e.standort_id, '
        'e.alarmiert_am, e.status, e.notiz, '
        'sw.kuerzel, sw.bezeichnung AS stichwort_name, sw.kategorie, '
        's.name AS standort_name '
        'FROM einsaetze e '
        'JOIN stichwoerter sw ON e.stichwort_id = sw.id '
        'LEFT JOIN standorte s ON e.standort_id = s.id '
        'WHERE e.status = :status '
        'ORDER BY e.alarmiert_am DESC LIMIT 1',
        {'status': 'aktiv'},
      );
      return rows.isNotEmpty ? Einsatz.fromMap(rows.first) : null;
    } catch (_) {
      return null;
    }
  }

  /// Zählt die aktiven Einsätze.
  static Future<int> countActive() async {
    try {
      final rows = await db.execute(
        'SELECT COUNT(*) AS anzahl FROM einsaetze WHERE status = :s',
        {'s': 'aktiv'},
      );
      if (rows.isNotEmpty) {
        final val = rows.first['anzahl'];
        if (val is int) return val;
        if (val is String) return int.tryParse(val) ?? 0;
      }
      return 0;
    } catch (_) {
      return 0;
    }
  }
}
