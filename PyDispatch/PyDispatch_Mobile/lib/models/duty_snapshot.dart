class DutySnapshot {
  const DutySnapshot({
    required this.activeGroupName,
    required this.userName,
    required this.teammates,
    required this.isOnDutyThisWeek,
  });

  final String activeGroupName;
  final String userName;
  final List<String> teammates;
  final bool isOnDutyThisWeek;
}
