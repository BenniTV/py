import 'package:flutter/material.dart';

import '../models/app_config.dart';
import '../models/duty_status.dart';
import '../models/device_binding_result.dart';

class SetupScreen extends StatefulWidget {
  const SetupScreen({
    super.key,
    required this.onSubmit,
  });

  final Future<DeviceBindingResult> Function(AppConfig config) onSubmit;

  @override
  State<SetupScreen> createState() => _SetupScreenState();
}

class _SetupScreenState extends State<SetupScreen> {
  final _formKey = GlobalKey<FormState>();
  final _hostController = TextEditingController();
  final _portController = TextEditingController(text: '3306');
  final _userController = TextEditingController();
  final _passwordController = TextEditingController();
  final _databaseController = TextEditingController();
  final _deviceIdController = TextEditingController();

  bool _isSaving = false;
  String? _error;

  String _normalizeHost(String value) {
    var host = value.trim();
    host = host.replaceAll('mysql://', '');
    host = host.replaceAll('http://', '');
    host = host.replaceAll('https://', '');
    if (host.contains('/')) {
      host = host.split('/').first;
    }
    if (host.contains(':')) {
      host = host.split(':').first;
    }
    return host.trim();
  }

  @override
  void dispose() {
    _hostController.dispose();
    _portController.dispose();
    _userController.dispose();
    _passwordController.dispose();
    _databaseController.dispose();
    _deviceIdController.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() {
      _isSaving = true;
      _error = null;
    });

    final normalizedHost = _normalizeHost(_hostController.text);
    if (normalizedHost.isEmpty) {
      setState(() {
        _isSaving = false;
        _error = 'Host ungültig. Bitte IP oder Hostnamen ohne http:// eingeben.';
      });
      return;
    }

    final config = AppConfig(
      host: normalizedHost,
      port: _portController.text.trim(),
      user: _userController.text.trim(),
      password: _passwordController.text,
      database: _databaseController.text.trim(),
      deviceId: _deviceIdController.text.trim(),
      status: DutyStatus.notInSchool,
    );

    final result = await widget.onSubmit(config);

    if (!mounted) {
      return;
    }

    setState(() {
      _isSaving = false;
      _error = result.success ? null : result.message;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('PyDispatch Mobile Setup')),
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 560),
          child: Card(
            margin: const EdgeInsets.all(16),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Form(
                key: _formKey,
                child: ListView(
                  shrinkWrap: true,
                  children: [
                    const Text('App-Einrichtung', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 8),
                    const Text('DB-Verbindung + Geräte-ID eingeben, danach läuft die App automatisch.'),
                    const SizedBox(height: 16),
                    _buildTextField(_hostController, 'Host'),
                    _buildTextField(_portController, 'Port'),
                    _buildTextField(_userController, 'DB Benutzer'),
                    _buildTextField(_passwordController, 'DB Passwort', obscureText: true, required: false),
                    _buildTextField(_databaseController, 'Datenbankname'),
                    _buildTextField(_deviceIdController, 'Geräte-ID'),
                    if (_error != null) ...[
                      const SizedBox(height: 8),
                      Text(_error!, style: const TextStyle(color: Colors.red)),
                    ],
                    const SizedBox(height: 16),
                    FilledButton(
                      onPressed: _isSaving ? null : _save,
                      child: Padding(
                        padding: const EdgeInsets.symmetric(vertical: 12),
                        child: Text(_isSaving ? 'Prüfe...' : 'Einrichtung abschließen'),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildTextField(
    TextEditingController controller,
    String label, {
    bool obscureText = false,
    bool required = true,
  }) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: TextFormField(
        controller: controller,
        obscureText: obscureText,
        validator: required
            ? (value) {
                if (value == null || value.trim().isEmpty) {
                  return '$label ist erforderlich';
                }
                return null;
              }
            : null,
        decoration: InputDecoration(labelText: label, border: const OutlineInputBorder()),
      ),
    );
  }
}
