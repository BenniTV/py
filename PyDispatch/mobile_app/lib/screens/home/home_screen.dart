/// PyDispatch Mobile – Home-Screen.
/// Zeigt Schichtstatus, Status-Buttons und Gruppenmitglieder.
import 'package:flutter/material.dart';
import '../../models/user.dart';
import '../../services/device_service.dart';
import '../../services/status_service.dart';
import '../../theme/app_theme.dart';

/// Status-Varianten.
class StatusConfig {
  final String key;
  final String label;
  final String subtitle;
  final IconData icon;
  final Color color;
  final Color bgColor;

  const StatusConfig(
      this.key, this.label, this.subtitle, this.icon, this.color, this.bgColor);
}

final _statuses = [
  StatusConfig(
    'in_der_schule',
    'In der Schule',
    'Voller Alarm bei Einsatz',
    Icons.school_rounded,
    AppColors.statusSchool,
    AppColors.statusSchool.withValues(alpha: 0.12),
  ),
  StatusConfig(
    'nicht_in_der_schule',
    'Nicht in der Schule',
    'Keine Alarmierung',
    Icons.home_rounded,
    AppColors.statusAway,
    AppColors.statusAway.withValues(alpha: 0.12),
  ),
  StatusConfig(
    'klassenarbeit',
    'Klassenarbeit',
    'Nur stiller Alarm',
    Icons.edit_note_rounded,
    AppColors.statusExam,
    AppColors.statusExam.withValues(alpha: 0.12),
  ),
];

class HomeScreen extends StatefulWidget {
  final int benutzerId;
  const HomeScreen({super.key, required this.benutzerId});

  @override
  State<HomeScreen> createState() => HomeScreenState();
}

class HomeScreenState extends State<HomeScreen> {
  String _currentStatus = 'nicht_in_der_schule';
  String _userName = '—';
  String _userInitials = '?';
  String _einrichtung = 'PyDispatch';
  String _groupName = '—';
  bool _inActiveGroup = false;
  List<AppUser> _members = [];
  bool _loading = false;

  @override
  void initState() {
    super.initState();
    refreshData();
  }

  Future<void> refreshData() async {
    try {
      final user = await DeviceService.getUserInfo(widget.benutzerId);
      if (user != null) {
        final v = user['vorname']?.toString() ?? '';
        final n = user['nachname']?.toString() ?? '';
        _userName = '$v $n'.trim();
        if (_userName.isEmpty) {
          _userName = user['benutzername']?.toString() ?? '—';
        }
        _userInitials = _getInitials(v, n);
        _currentStatus = user['status']?.toString() ?? 'nicht_in_der_schule';
      }

      _einrichtung = await DeviceService.getEinrichtungName();

      final group = await StatusService.getActiveGroup();
      if (group != null) {
        _groupName = group['name']?.toString() ?? '—';
        _inActiveGroup =
            await StatusService.isUserInActiveGroup(widget.benutzerId);
      } else {
        _groupName = 'Keine aktiv';
        _inActiveGroup = false;
      }

      _members = await StatusService.getGroupMembers();
      if (mounted) setState(() {});
    } catch (_) {}
  }

  String _getInitials(String vorname, String nachname) {
    final v = vorname.isNotEmpty ? vorname[0].toUpperCase() : '';
    final n = nachname.isNotEmpty ? nachname[0].toUpperCase() : '';
    if (v.isEmpty && n.isEmpty) return '?';
    return '$v$n';
  }

  Future<void> _setStatus(String status) async {
    setState(() => _loading = true);
    final (ok, _) = await StatusService.setStatus(widget.benutzerId, status);
    if (ok) _currentStatus = status;
    setState(() => _loading = false);
  }

  StatusConfig get _currentConfig =>
      _statuses.firstWhere((s) => s.key == _currentStatus,
          orElse: () => _statuses[1]);

  @override
  Widget build(BuildContext context) {
    return RefreshIndicator(
      color: AppColors.primary,
      backgroundColor: AppColors.bgCard,
      onRefresh: refreshData,
      child: ListView(
        padding: EdgeInsets.zero,
        children: [
          _buildHeader(),
          const SizedBox(height: 20),
          _buildInfoCards(),
          const SizedBox(height: 24),
          _buildStatusSection(),
          const SizedBox(height: 24),
          _buildMembersSection(),
          const SizedBox(height: 32),
        ],
      ),
    );
  }

  // ── Header mit Gradient ──
  Widget _buildHeader() {
    final cfg = _currentConfig;
    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            AppColors.bgCard,
            AppColors.bgSurface,
          ],
        ),
        borderRadius: const BorderRadius.only(
          bottomLeft: Radius.circular(28),
          bottomRight: Radius.circular(28),
        ),
      ),
      child: SafeArea(
        bottom: false,
        child: Padding(
          padding: const EdgeInsets.fromLTRB(24, 16, 24, 24),
          child: Column(
            children: [
              // Einrichtung
              Text(
                _einrichtung,
                style: const TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w500,
                  color: AppColors.textSecondary,
                  letterSpacing: 1,
                ),
              ),
              const SizedBox(height: 16),
              // Avatar + Name
              Row(
                children: [
                  // Avatar
                  Container(
                    width: 56,
                    height: 56,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      gradient: LinearGradient(
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                        colors: [
                          AppColors.primary,
                          AppColors.primaryDark,
                        ],
                      ),
                      boxShadow: [
                        BoxShadow(
                          color: AppColors.primary.withValues(alpha: 0.3),
                          blurRadius: 12,
                          offset: const Offset(0, 4),
                        ),
                      ],
                    ),
                    child: Center(
                      child: Text(
                        _userInitials,
                        style: const TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.w700,
                          color: Colors.white,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 16),
                  // Name + Status
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          _userName,
                          style: const TextStyle(
                            fontSize: 22,
                            fontWeight: FontWeight.w700,
                            color: AppColors.text,
                          ),
                        ),
                        const SizedBox(height: 6),
                        // Status-Chip
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 12, vertical: 5),
                          decoration: BoxDecoration(
                            color: cfg.color.withValues(alpha: 0.15),
                            borderRadius: BorderRadius.circular(20),
                            border: Border.all(
                              color: cfg.color.withValues(alpha: 0.3),
                            ),
                          ),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Container(
                                width: 8,
                                height: 8,
                                decoration: BoxDecoration(
                                  color: cfg.color,
                                  shape: BoxShape.circle,
                                ),
                              ),
                              const SizedBox(width: 8),
                              Text(
                                cfg.label,
                                style: TextStyle(
                                  fontSize: 13,
                                  fontWeight: FontWeight.w600,
                                  color: cfg.color,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  // ── Info-Karten ──
  Widget _buildInfoCards() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: Row(
        children: [
          Expanded(
            child: _GlassCard(
              icon: Icons.groups_rounded,
              iconColor: AppColors.primary,
              title: 'Aktive Gruppe',
              value: _groupName,
              valueColor: AppColors.primary,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: _GlassCard(
              icon: _inActiveGroup
                  ? Icons.check_circle_rounded
                  : Icons.remove_circle_outline_rounded,
              iconColor:
                  _inActiveGroup ? AppColors.success : AppColors.textSecondary,
              title: 'Dein Dienst',
              value: _inActiveGroup ? 'Eingeteilt ✓' : 'Nicht dran',
              valueColor:
                  _inActiveGroup ? AppColors.success : AppColors.textSecondary,
            ),
          ),
        ],
      ),
    );
  }

  // ── Status-Buttons ──
  Widget _buildStatusSection() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Padding(
            padding: EdgeInsets.only(left: 4, bottom: 14),
            child: Text(
              'Status ändern',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w700,
                color: AppColors.text,
              ),
            ),
          ),
          ..._statuses.map((s) => Padding(
                padding: const EdgeInsets.only(bottom: 10),
                child: _StatusButton(
                  config: s,
                  isActive: s.key == _currentStatus,
                  onTap: _loading ? null : () => _setStatus(s.key),
                ),
              )),
        ],
      ),
    );
  }

  // ── Mitglieder ──
  Widget _buildMembersSection() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.only(left: 4, bottom: 14),
            child: Row(
              children: [
                const Text(
                  'Schicht-Kollegen',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.w700,
                    color: AppColors.text,
                  ),
                ),
                const SizedBox(width: 8),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(
                    color: AppColors.primary.withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Text(
                    '${_members.length}',
                    style: const TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w700,
                      color: AppColors.primary,
                    ),
                  ),
                ),
              ],
            ),
          ),
          Container(
            decoration: BoxDecoration(
              color: AppColors.bgCard,
              borderRadius: BorderRadius.circular(16),
              border:
                  Border.all(color: AppColors.border.withValues(alpha: 0.5)),
            ),
            child: _members.isEmpty
                ? Padding(
                    padding: const EdgeInsets.all(24),
                    child: Center(
                      child: Column(
                        children: [
                          Icon(Icons.group_off_rounded,
                              size: 36, color: AppColors.textMuted),
                          const SizedBox(height: 8),
                          const Text('Keine aktive Gruppe',
                              style: TextStyle(
                                  color: AppColors.textSecondary,
                                  fontSize: 14)),
                        ],
                      ),
                    ),
                  )
                : Column(
                    children: [
                      for (var i = 0; i < _members.length; i++) ...[
                        _MemberTile(
                          member: _members[i],
                          isSelf: _members[i].id == widget.benutzerId,
                        ),
                        if (i < _members.length - 1)
                          Divider(
                            height: 1,
                            indent: 60,
                            color: AppColors.border.withValues(alpha: 0.3),
                          ),
                      ],
                    ],
                  ),
          ),
        ],
      ),
    );
  }
}

// ── Glass-Card Widget ──
class _GlassCard extends StatelessWidget {
  final IconData icon;
  final Color iconColor;
  final String title;
  final String value;
  final Color? valueColor;

  const _GlassCard({
    required this.icon,
    required this.iconColor,
    required this.title,
    required this.value,
    this.valueColor,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.bgCard,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.border.withValues(alpha: 0.5)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 22, color: iconColor),
          const SizedBox(height: 10),
          Text(title,
              style: const TextStyle(
                  fontSize: 12,
                  color: AppColors.textSecondary,
                  fontWeight: FontWeight.w500)),
          const SizedBox(height: 4),
          Text(value,
              style: TextStyle(
                fontSize: 15,
                fontWeight: FontWeight.w700,
                color: valueColor ?? AppColors.text,
              )),
        ],
      ),
    );
  }
}

// ── Status-Button ──
class _StatusButton extends StatelessWidget {
  final StatusConfig config;
  final bool isActive;
  final VoidCallback? onTap;

  const _StatusButton({
    required this.config,
    required this.isActive,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return AnimatedContainer(
      duration: const Duration(milliseconds: 200),
      curve: Curves.easeOut,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(16),
        color: isActive ? config.bgColor : AppColors.bgCard,
        border: Border.all(
          color: isActive
              ? config.color.withValues(alpha: 0.5)
              : AppColors.border.withValues(alpha: 0.5),
          width: isActive ? 2 : 1,
        ),
        boxShadow: isActive
            ? [
                BoxShadow(
                  color: config.color.withValues(alpha: 0.15),
                  blurRadius: 16,
                  offset: const Offset(0, 4),
                ),
              ]
            : null,
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(16),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
            child: Row(
              children: [
                // Icon-Container
                Container(
                  width: 44,
                  height: 44,
                  decoration: BoxDecoration(
                    color: isActive
                        ? config.color.withValues(alpha: 0.2)
                        : AppColors.bgCardLight,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(
                    config.icon,
                    size: 22,
                    color: isActive ? config.color : AppColors.textSecondary,
                  ),
                ),
                const SizedBox(width: 16),
                // Label + Subtitle
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        config.label,
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                          color: isActive ? config.color : AppColors.text,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        config.subtitle,
                        style: const TextStyle(
                          fontSize: 12,
                          color: AppColors.textSecondary,
                        ),
                      ),
                    ],
                  ),
                ),
                // Check-Icon
                if (isActive)
                  Container(
                    width: 28,
                    height: 28,
                    decoration: BoxDecoration(
                      color: config.color,
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(Icons.check,
                        color: Colors.white, size: 16),
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

// ── Mitglieder-Zeile ──
class _MemberTile extends StatelessWidget {
  final AppUser member;
  final bool isSelf;

  const _MemberTile({required this.member, required this.isSelf});

  Color get _statusColor {
    switch (member.status) {
      case 'in_der_schule':
        return AppColors.statusSchool;
      case 'klassenarbeit':
        return AppColors.statusExam;
      default:
        return AppColors.statusAway;
    }
  }

  String get _statusLabel {
    switch (member.status) {
      case 'in_der_schule':
        return 'In der Schule';
      case 'klassenarbeit':
        return 'Klassenarbeit';
      default:
        return 'Nicht da';
    }
  }

  String get _initials {
    final v = member.fullName.split(' ');
    if (v.length >= 2) {
      return '${v[0][0]}${v[1][0]}'.toUpperCase();
    }
    return member.fullName.isNotEmpty
        ? member.fullName[0].toUpperCase()
        : '?';
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Row(
        children: [
          // Mini-Avatar
          Container(
            width: 36,
            height: 36,
            decoration: BoxDecoration(
              color: _statusColor.withValues(alpha: 0.15),
              shape: BoxShape.circle,
              border: Border.all(
                  color: _statusColor.withValues(alpha: 0.3), width: 1.5),
            ),
            child: Center(
              child: Text(
                _initials,
                style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w700,
                  color: _statusColor,
                ),
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  isSelf ? '${member.fullName} (Du)' : member.fullName,
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: isSelf ? FontWeight.w700 : FontWeight.w500,
                    color: AppColors.text,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  _statusLabel,
                  style: TextStyle(
                    fontSize: 12,
                    color: _statusColor.withValues(alpha: 0.8),
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),
          // Status-Dot
          Container(
            width: 10,
            height: 10,
            decoration: BoxDecoration(
              color: _statusColor,
              shape: BoxShape.circle,
              boxShadow: [
                BoxShadow(
                  color: _statusColor.withValues(alpha: 0.4),
                  blurRadius: 6,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
