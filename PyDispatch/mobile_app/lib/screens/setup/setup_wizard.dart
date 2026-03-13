/// PyDispatch Mobile – Setup-Wizard.
/// Zwei-Schritt-Setup: MySQL-Verbindung → Geräte-ID → Fertig.
import 'package:flutter/material.dart';
import '../../config/settings.dart';
import '../../database/connection.dart';
import '../../services/device_service.dart';
import '../../theme/app_theme.dart';

class SetupWizard extends StatefulWidget {
  final VoidCallback onComplete;
  const SetupWizard({super.key, required this.onComplete});

  @override
  State<SetupWizard> createState() => _SetupWizardState();
}

class _SetupWizardState extends State<SetupWizard> {
  int _step = 1;
  String _statusMsg = '';
  Color _statusColor = AppColors.textSecondary;
  bool _loading = false;

  // Step 1: MySQL
  final _hostCtrl = TextEditingController(text: 'localhost');
  final _portCtrl = TextEditingController(text: '3306');
  final _userCtrl = TextEditingController();
  final _passCtrl = TextEditingController();
  final _dbCtrl = TextEditingController(text: 'pydispatch');

  // Step 2: Geräte-ID
  final _geraeteCtrl = TextEditingController();

  @override
  void dispose() {
    _hostCtrl.dispose();
    _portCtrl.dispose();
    _userCtrl.dispose();
    _passCtrl.dispose();
    _dbCtrl.dispose();
    _geraeteCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bgDark,
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: _step == 1 ? _buildStep1() : _buildStep2(),
          ),
        ),
      ),
    );
  }

  Widget _buildStep1() {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        // Logo / Icon
        Container(
          width: 80,
          height: 80,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [AppColors.primary, AppColors.primaryDark],
            ),
            boxShadow: [
              BoxShadow(
                color: AppColors.primary.withValues(alpha: 0.3),
                blurRadius: 24,
                offset: const Offset(0, 8),
              ),
            ],
          ),
          child: const Center(
            child: Text('🚒', style: TextStyle(fontSize: 36)),
          ),
        ),
        const SizedBox(height: 20),
        Text('PyDispatch',
            style: Theme.of(context)
                .textTheme
                .headlineMedium
                ?.copyWith(fontWeight: FontWeight.w800)),
        const SizedBox(height: 6),
        // Stepper
        _buildStepIndicator(),
        const SizedBox(height: 8),
        const Text('Datenbankverbindung einrichten',
            style: TextStyle(
                color: AppColors.textSecondary,
                fontSize: 14,
                fontWeight: FontWeight.w500)),
        const SizedBox(height: 28),
        // Formular-Karte
        Container(
          decoration: BoxDecoration(
            color: AppColors.bgCard,
            borderRadius: BorderRadius.circular(20),
            border:
                Border.all(color: AppColors.border.withValues(alpha: 0.5)),
          ),
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildField('Host', _hostCtrl, Icons.dns_rounded),
              _buildField('Port', _portCtrl, Icons.tag_rounded,
                  keyboardType: TextInputType.number),
              _buildField('Benutzer', _userCtrl, Icons.person_rounded),
              _buildField('Passwort', _passCtrl, Icons.lock_rounded,
                  obscure: true),
              _buildField('Datenbank', _dbCtrl, Icons.storage_rounded),
            ],
          ),
        ),
        const SizedBox(height: 20),
        if (_statusMsg.isNotEmpty)
          Padding(
            padding: const EdgeInsets.only(bottom: 16),
            child: Container(
              padding:
                  const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              decoration: BoxDecoration(
                color: _statusColor.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                    color: _statusColor.withValues(alpha: 0.3)),
              ),
              child: Text(_statusMsg,
                  style: TextStyle(
                      color: _statusColor, fontWeight: FontWeight.w500)),
            ),
          ),
        Row(
          children: [
            Expanded(
              child: OutlinedButton(
                onPressed: _loading ? null : _testConnection,
                child: const Text('Testen'),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: ElevatedButton(
                onPressed: _loading ? null : _step1Next,
                child: _loading
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                            strokeWidth: 2, color: Colors.white))
                    : const Text('Weiter →'),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildStep2() {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 80,
          height: 80,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [AppColors.success, AppColors.successDark],
            ),
            boxShadow: [
              BoxShadow(
                color: AppColors.success.withValues(alpha: 0.3),
                blurRadius: 24,
                offset: const Offset(0, 8),
              ),
            ],
          ),
          child: const Center(
            child: Text('📱', style: TextStyle(fontSize: 36)),
          ),
        ),
        const SizedBox(height: 20),
        Text('Geräte-ID',
            style: Theme.of(context)
                .textTheme
                .headlineMedium
                ?.copyWith(fontWeight: FontWeight.w800)),
        const SizedBox(height: 6),
        _buildStepIndicator(),
        const SizedBox(height: 8),
        const Text('Gerät mit Benutzer verknüpfen',
            style: TextStyle(
                color: AppColors.textSecondary,
                fontSize: 14,
                fontWeight: FontWeight.w500)),
        const SizedBox(height: 28),
        Container(
          decoration: BoxDecoration(
            color: AppColors.bgCard,
            borderRadius: BorderRadius.circular(20),
            border:
                Border.all(color: AppColors.border.withValues(alpha: 0.5)),
          ),
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Hinweis
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: AppColors.primary.withValues(alpha: 0.08),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                      color: AppColors.primary.withValues(alpha: 0.2)),
                ),
                child: Row(
                  children: [
                    Icon(Icons.info_outline_rounded,
                        color: AppColors.primary.withValues(alpha: 0.7),
                        size: 20),
                    const SizedBox(width: 10),
                    const Expanded(
                      child: Text(
                        'Die ID wurde in der Admin-Software generiert und dem Gerät zugewiesen.',
                        style: TextStyle(
                            fontSize: 13, color: AppColors.textSecondary),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),
              const Text('Geräte-ID',
                  style: TextStyle(
                      fontSize: 13,
                      color: AppColors.textSecondary,
                      fontWeight: FontWeight.w500)),
              const SizedBox(height: 8),
              TextField(
                controller: _geraeteCtrl,
                style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 1),
                decoration: const InputDecoration(
                  hintText: 'MG-XXXXXXXX',
                  prefixIcon: Icon(Icons.smartphone_rounded,
                      color: AppColors.textSecondary),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 20),
        if (_statusMsg.isNotEmpty)
          Padding(
            padding: const EdgeInsets.only(bottom: 16),
            child: Container(
              padding:
                  const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              decoration: BoxDecoration(
                color: _statusColor.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                    color: _statusColor.withValues(alpha: 0.3)),
              ),
              child: Text(_statusMsg,
                  style: TextStyle(
                      color: _statusColor, fontWeight: FontWeight.w500)),
            ),
          ),
        Row(
          children: [
            Expanded(
              child: OutlinedButton(
                onPressed: _loading
                    ? null
                    : () => setState(() {
                          _step = 1;
                          _statusMsg = '';
                        }),
                child: const Text('← Zurück'),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: ElevatedButton(
                onPressed: _loading ? null : _step2Finish,
                style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.success),
                child: _loading
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                            strokeWidth: 2, color: Colors.white))
                    : const Text('Fertig ✓'),
              ),
            ),
          ],
        ),
      ],
    );
  }

  // ── Step-Indicator ──
  Widget _buildStepIndicator() {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          _stepDot(1),
          Container(
            width: 32,
            height: 2,
            color: _step >= 2 ? AppColors.primary : AppColors.border,
          ),
          _stepDot(2),
        ],
      ),
    );
  }

  Widget _stepDot(int step) {
    final active = _step >= step;
    return Container(
      width: 28,
      height: 28,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: active ? AppColors.primary : AppColors.bgCard,
        border: Border.all(
          color: active ? AppColors.primary : AppColors.border,
          width: 2,
        ),
      ),
      child: Center(
        child: Text(
          '$step',
          style: TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w700,
            color: active ? Colors.white : AppColors.textSecondary,
          ),
        ),
      ),
    );
  }

  Widget _buildField(String label, TextEditingController ctrl, IconData icon,
      {bool obscure = false, TextInputType? keyboardType}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 14),
      child: TextField(
        controller: ctrl,
        obscureText: obscure,
        keyboardType: keyboardType,
        decoration: InputDecoration(
          labelText: label,
          prefixIcon: Icon(icon, color: AppColors.textSecondary, size: 20),
        ),
      ),
    );
  }

  Future<void> _testConnection() async {
    setState(() {
      _loading = true;
      _statusMsg = '';
    });
    final (ok, msg) = await db.testConnection(
      host: _hostCtrl.text.trim(),
      port: int.tryParse(_portCtrl.text.trim()) ?? 3306,
      user: _userCtrl.text.trim(),
      password: _passCtrl.text,
      database: _dbCtrl.text.trim(),
    );
    setState(() {
      _loading = false;
      _statusMsg = ok ? '✅ Verbindung erfolgreich!' : '❌ $msg';
      _statusColor = ok ? AppColors.success : AppColors.danger;
    });
  }

  Future<void> _step1Next() async {
    final host = _hostCtrl.text.trim();
    final port = int.tryParse(_portCtrl.text.trim()) ?? 3306;
    final user = _userCtrl.text.trim();
    final pass = _passCtrl.text;
    final database = _dbCtrl.text.trim();

    if (host.isEmpty || user.isEmpty || database.isEmpty) {
      setState(() {
        _statusMsg = 'Bitte alle Pflichtfelder ausfüllen.';
        _statusColor = AppColors.danger;
      });
      return;
    }

    setState(() => _loading = true);
    final connected = await db.connect(
      host: host,
      port: port,
      user: user,
      password: pass,
      database: database,
    );

    if (!connected) {
      setState(() {
        _loading = false;
        _statusMsg = '❌ Verbindung fehlgeschlagen.';
        _statusColor = AppColors.danger;
      });
      return;
    }

    await AppConfig.saveMysqlConfig(
      host: host,
      port: port,
      user: user,
      password: pass,
      database: database,
    );

    setState(() {
      _loading = false;
      _statusMsg = '';
      _step = 2;
    });
  }

  Future<void> _step2Finish() async {
    final gid = _geraeteCtrl.text.trim();
    if (gid.isEmpty) {
      setState(() {
        _statusMsg = 'Bitte die Geräte-ID eingeben.';
        _statusColor = AppColors.danger;
      });
      return;
    }

    setState(() => _loading = true);
    final (ok, msg, data) = await DeviceService.validateGeraeteId(gid);

    if (!ok) {
      setState(() {
        _loading = false;
        _statusMsg = '❌ $msg';
        _statusColor = AppColors.danger;
      });
      return;
    }

    await AppConfig.saveGeraeteId(gid);
    await AppConfig.setSetupDone(true);
    await DeviceService.updateLetzterKontakt(gid);

    final name =
        '${data?['vorname'] ?? ''} ${data?['nachname'] ?? ''}'.trim();
    setState(() {
      _loading = false;
      _statusMsg = '✅ Zugeordnet: $name';
      _statusColor = AppColors.success;
    });

    await Future.delayed(const Duration(milliseconds: 800));
    widget.onComplete();
  }
}
