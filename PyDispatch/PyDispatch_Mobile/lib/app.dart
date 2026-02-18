import 'package:flutter/material.dart';

import 'models/app_config.dart';
import 'models/device_binding_result.dart';
import 'repositories/mobile_repository.dart';
import 'screens/home_screen.dart';
import 'screens/setup_screen.dart';
import 'services/config_service.dart';

class PyDispatchMobileApp extends StatefulWidget {
  const PyDispatchMobileApp({
    super.key,
    required this.repository,
    required this.configService,
  });

  final MobileRepository repository;
  final ConfigService configService;

  @override
  State<PyDispatchMobileApp> createState() => _PyDispatchMobileAppState();
}

class _PyDispatchMobileAppState extends State<PyDispatchMobileApp> {
  AppConfig? _config;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _bootstrap();
  }

  Future<void> _bootstrap() async {
    final config = await widget.configService.load();
    if (!mounted) {
      return;
    }

    setState(() {
      _config = config;
      _loading = false;
    });
  }

  Future<DeviceBindingResult> _handleSetupSubmit(AppConfig config) async {
    final result = await widget.repository.validateAndBindDevice(config);
    if (!result.success) {
      return result;
    }

    await widget.configService.save(config);
    if (mounted) {
      setState(() {
        _config = config;
      });
    }

    return result;
  }

  Future<void> _handleConfigUpdate(AppConfig config) async {
    await widget.configService.save(config);
    if (mounted) {
      setState(() {
        _config = config;
      });
    }
  }

  Future<void> _resetToSetup() async {
    await widget.configService.clear();
    if (mounted) {
      setState(() {
        _config = null;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'PyDispatch Mobile',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.red),
        useMaterial3: true,
      ),
      home: _loading
          ? const Scaffold(body: Center(child: CircularProgressIndicator()))
          : _config == null
              ? SetupScreen(onSubmit: _handleSetupSubmit)
              : HomeScreen(
                  initialConfig: _config!,
                  repository: widget.repository,
                  onConfigChanged: (cfg) => _handleConfigUpdate(cfg),
                  onReconfigure: _resetToSetup,
                ),
    );
  }
}
