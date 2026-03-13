/// PyDispatch Mobile – Einsatz-Model.
class Einsatz {
  final int id;
  final int stichwortId;
  final String? standortText;
  final int? standortId;
  final DateTime alarmiert;
  final String status;
  final String? notiz;
  final String kuerzel;
  final String stichwortName;
  final String? kategorie;
  final String? standortName;

  Einsatz({
    required this.id,
    required this.stichwortId,
    this.standortText,
    this.standortId,
    required this.alarmiert,
    required this.status,
    this.notiz,
    required this.kuerzel,
    required this.stichwortName,
    this.kategorie,
    this.standortName,
  });

  factory Einsatz.fromMap(Map<String, dynamic> map) {
    return Einsatz(
      id: _toInt(map['id']),
      stichwortId: _toInt(map['stichwort_id']),
      standortText: map['standort_text']?.toString(),
      standortId: map['standort_id'] != null ? _toInt(map['standort_id']) : null,
      alarmiert: _toDateTime(map['alarmiert_am']),
      status: map['status']?.toString() ?? 'aktiv',
      notiz: map['notiz']?.toString(),
      kuerzel: map['kuerzel']?.toString() ?? '?',
      stichwortName: map['stichwort_name']?.toString() ?? 'Einsatz',
      kategorie: map['kategorie']?.toString(),
      standortName: map['standort_name']?.toString(),
    );
  }

  String get standortDisplay => standortName ?? standortText ?? '—';

  static int _toInt(dynamic value) {
    if (value is int) return value;
    if (value is String) return int.tryParse(value) ?? 0;
    return 0;
  }

  static DateTime _toDateTime(dynamic value) {
    if (value is DateTime) return value;
    if (value is String) return DateTime.tryParse(value) ?? DateTime.now();
    return DateTime.now();
  }
}
