/// PyDispatch Mobile – Benutzer-Model.
class AppUser {
  final int id;
  final String benutzername;
  final String? vorname;
  final String? nachname;
  final String rolle;
  final bool istAktiv;
  final String status;

  AppUser({
    required this.id,
    required this.benutzername,
    this.vorname,
    this.nachname,
    this.rolle = 'benutzer',
    this.istAktiv = true,
    this.status = 'nicht_in_der_schule',
  });

  factory AppUser.fromMap(Map<String, dynamic> map) {
    return AppUser(
      id: _toInt(map['id']),
      benutzername: map['benutzername']?.toString() ?? '',
      vorname: map['vorname']?.toString(),
      nachname: map['nachname']?.toString(),
      rolle: map['rolle']?.toString() ?? 'benutzer',
      istAktiv: _toBool(map['ist_aktiv']),
      status: map['status']?.toString() ?? 'nicht_in_der_schule',
    );
  }

  String get fullName {
    final parts = [vorname, nachname].where((p) => p != null && p.isNotEmpty);
    return parts.isNotEmpty ? parts.join(' ') : benutzername;
  }

  static int _toInt(dynamic value) {
    if (value is int) return value;
    if (value is String) return int.tryParse(value) ?? 0;
    return 0;
  }

  static bool _toBool(dynamic value) {
    if (value is bool) return value;
    if (value is int) return value == 1;
    if (value is String) return value == '1' || value.toLowerCase() == 'true';
    return true;
  }
}
