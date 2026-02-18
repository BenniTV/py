class AlarmEvent {
  const AlarmEvent({
    required this.id,
    required this.keyword,
    required this.location,
    required this.createdAt,
  });

  final String id;
  final String keyword;
  final String location;
  final DateTime createdAt;
}
