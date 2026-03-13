/// PyDispatch Mobile – Alarm-Screen.
/// Vollbild-Alarm mit SOS-Taschenlampen-Blitz, Vibration und lautem Alarmton.
///
/// Modi:
/// - "full":   Ton + Blitz + Vibration (Status: in_der_schule)
/// - "silent": Nur Blitz (Status: klassenarbeit) – auto-dismiss 10 Min
import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:torch_light/torch_light.dart';
import 'package:vibration/vibration.dart';
import '../../models/einsatz.dart';
import '../../theme/app_theme.dart';

/// SOS-Muster: kurz=150ms, lang=400ms, Pause=100ms, Buchstaben-Pause=300ms
const _sosPattern = [
  150, 100, 150, 100, 150, 300, // S
  400, 100, 400, 100, 400, 300, // O
  150, 100, 150, 100, 150, 600, // S + Wort-Pause
];

class AlarmScreen extends StatefulWidget {
  final Einsatz einsatz;
  final String mode; // "full" oder "silent"
  final VoidCallback onDismiss;

  const AlarmScreen({
    super.key,
    required this.einsatz,
    this.mode = 'full',
    required this.onDismiss,
  });

  @override
  State<AlarmScreen> createState() => _AlarmScreenState();
}

class _AlarmScreenState extends State<AlarmScreen>
    with TickerProviderStateMixin {
  bool _flashOn = false;
  int _sosIndex = 0;
  Timer? _sosTimer;
  Timer? _stopTimer;
  Timer? _autoDismissTimer;
  bool _hasTorch = false;
  bool _hasVibrator = false;

  // Animationen
  late AnimationController _pulseController;
  late AnimationController _bgController;
  late Animation<Color?> _bgAnimation;

  bool _dismissed = false;

  @override
  void initState() {
    super.initState();

    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 600),
    )..repeat(reverse: true);

    _bgController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
    )..repeat(reverse: true);

    _bgAnimation = ColorTween(
      begin: const Color(0xFF1A0000),
      end: const Color(0xFF3D0000),
    ).animate(CurvedAnimation(
      parent: _bgController,
      curve: Curves.easeInOut,
    ));

    _initHardware();
    // Effekte leicht verzögert starten → gibt dem UI-Thread Zeit zum Rendern
    // und reduziert Skipped Frames.
    Future.delayed(const Duration(milliseconds: 100), _startAlarm);
  }

  Future<void> _initHardware() async {
    try {
      _hasTorch = await TorchLight.isTorchAvailable();
    } catch (_) {
      _hasTorch = false;
    }
    try {
      final result = await Vibration.hasVibrator();
      _hasVibrator = result == true;
    } catch (_) {
      _hasVibrator = false;
    }
  }

  void _startAlarm() {
    if (!mounted) return;
    // SOS-Blitz IMMER starten (beide Modi)
    _nextSosStep();

    if (widget.mode == 'full') {
      // Vibration starten
      _vibratePattern();

      // Audio wird NICHT hier gestartet! Wird von _AppShellState._triggerAlarm()
      // in main.dart gesteuert (entkoppelt vom Widget-Lifecycle).

      // Effekte nach 30 Sekunden stoppen
      _stopTimer = Timer(const Duration(seconds: 30), _stopEffects);
    } else {
      // Silent: Nur SOS-Blitz, kein Ton
      _stopTimer = Timer(const Duration(seconds: 30), _stopEffects);
      _autoDismissTimer =
          Timer(const Duration(minutes: 10), widget.onDismiss);
    }
  }

  void _nextSosStep() {
    if (!mounted) return;
    final index = _sosIndex % _sosPattern.length;
    final duration = _sosPattern[index];
    final isOn = index % 2 == 0;
    setState(() => _flashOn = isOn);
    if (isOn) {
      _torchOn();
    } else {
      _torchOff();
    }
    _sosIndex++;
    _sosTimer = Timer(Duration(milliseconds: duration), _nextSosStep);
  }

  Future<void> _torchOn() async {
    if (!_hasTorch) return;
    try {
      await TorchLight.enableTorch();
    } catch (_) {}
  }

  Future<void> _torchOff() async {
    if (!_hasTorch) return;
    try {
      await TorchLight.disableTorch();
    } catch (_) {}
  }

  Future<void> _vibratePattern() async {
    if (!_hasVibrator) return;
    try {
      // Starkes SOS-Vibrationsmuster, repeat=0 → wiederholt von Index 0
      await Vibration.vibrate(
        pattern: [
          0, 200, 100, 200, 100, 200, 300,  // S: kurz kurz kurz
          500, 100, 500, 100, 500, 300,      // O: lang lang lang
          200, 100, 200, 100, 200, 800,      // S: kurz kurz kurz + Pause
        ],
        intensities: [
          0, 255, 0, 255, 0, 255, 0,
          255, 0, 255, 0, 255, 0,
          255, 0, 255, 0, 255, 0,
        ],
        repeat: 0,
      );
    } catch (_) {}
  }

  void _stopEffects() {
    _sosTimer?.cancel();
    _sosTimer = null;
    _torchOff();
    // Audio-Stop wird NICHT hier gemacht – wird von main.dart onDismiss gesteuert.
    if (_hasVibrator) Vibration.cancel();
    if (mounted) setState(() => _flashOn = false);
  }

  void _dismiss() {
    if (_dismissed) return;
    _dismissed = true;
    _stopEffects();
    widget.onDismiss();
  }

  @override
  void dispose() {
    _sosTimer?.cancel();
    _stopTimer?.cancel();
    _autoDismissTimer?.cancel();
    _torchOff();
    // Audio-Stop wird NICHT hier gemacht – wird von main.dart onDismiss gesteuert.
    _pulseController.dispose();
    _bgController.dispose();
    if (_hasVibrator) Vibration.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _bgAnimation,
      builder: (context, child) => Scaffold(
        backgroundColor: _flashOn
            ? const Color(0xFF500000)
            : (_bgAnimation.value ?? const Color(0xFF1A0000)),
        body: SafeArea(
          child: Column(
            children: [
              // Dünne blinkende Leiste oben
              AnimatedContainer(
                duration: const Duration(milliseconds: 100),
                height: 4,
                color: _flashOn ? AppColors.alarmRed : Colors.transparent,
              ),
              Expanded(
                child: widget.mode == 'full'
                    ? _buildFullAlarm()
                    : _buildSilentAlarm(),
              ),
              _buildDismissArea(),
            ],
          ),
        ),
      ),
    );
  }

  // ── Voll-Alarm ──
  Widget _buildFullAlarm() {
    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
      child: Column(
        children: [
          const SizedBox(height: 20),
          // Pulsierendes Alarm-Icon
          AnimatedBuilder(
            animation: _pulseController,
            builder: (_, __) {
              final scale = 1.0 + _pulseController.value * 0.15;
              final glow = _pulseController.value * 0.6;
              return Transform.scale(
                scale: scale,
                child: Container(
                  width: 120,
                  height: 120,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: AppColors.alarmRed.withValues(alpha: 0.2),
                    boxShadow: [
                      BoxShadow(
                        color: AppColors.alarmRed.withValues(alpha: glow),
                        blurRadius: 60,
                        spreadRadius: 20,
                      ),
                    ],
                  ),
                  child: const Center(
                    child: Text('🚨', style: TextStyle(fontSize: 56)),
                  ),
                ),
              );
            },
          ),
          const SizedBox(height: 24),
          // ALARM-Text mit Gradient
          ShaderMask(
            shaderCallback: (bounds) => const LinearGradient(
              colors: [AppColors.alarmRed, Color(0xFFFF6B6B)],
            ).createShader(bounds),
            child: const Text(
              'ALARM',
              style: TextStyle(
                fontSize: 44,
                fontWeight: FontWeight.w900,
                color: Colors.white,
                letterSpacing: 12,
              ),
            ),
          ),
          const SizedBox(height: 32),
          _buildEinsatzCard(),
        ],
      ),
    );
  }

  // ── Einsatz-Info-Karte ──
  Widget _buildEinsatzCard() {
    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(20),
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFF2A1A1A), Color(0xFF1E1215)],
        ),
        border: Border.all(
          color: AppColors.alarmRed.withValues(alpha: 0.3),
          width: 1.5,
        ),
      ),
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Stichwort Badge + Label
          Row(
            children: [
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: AppColors.alarmRed.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(6),
                  border: Border.all(
                    color: AppColors.alarmRed.withValues(alpha: 0.4),
                  ),
                ),
                child: Text(
                  widget.einsatz.kuerzel,
                  style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                    color: AppColors.alarmRed,
                  ),
                ),
              ),
              const SizedBox(width: 8),
              const Text(
                'STICHWORT',
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w600,
                  color: AppColors.textSecondary,
                  letterSpacing: 1.5,
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Text(
            widget.einsatz.stichwortName,
            style: const TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 20),
          Container(height: 1, color: Colors.white.withValues(alpha: 0.08)),
          const SizedBox(height: 20),
          // Standort
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(Icons.location_on,
                  color: AppColors.alarmRed.withValues(alpha: 0.7), size: 20),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('STANDORT',
                        style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w600,
                          color: AppColors.textSecondary,
                          letterSpacing: 1.5,
                        )),
                    const SizedBox(height: 4),
                    Text(
                      widget.einsatz.standortDisplay,
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.w600,
                        color: Colors.white,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          // Notiz
          if (widget.einsatz.notiz != null &&
              widget.einsatz.notiz!.isNotEmpty) ...[
            const SizedBox(height: 20),
            Container(height: 1, color: Colors.white.withValues(alpha: 0.08)),
            const SizedBox(height: 20),
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(Icons.notes,
                    color: AppColors.warning.withValues(alpha: 0.7), size: 20),
                const SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('NOTIZ',
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.w600,
                            color: AppColors.textSecondary,
                            letterSpacing: 1.5,
                          )),
                      const SizedBox(height: 4),
                      Text(widget.einsatz.notiz!,
                          style: const TextStyle(
                              fontSize: 15, color: AppColors.text)),
                    ],
                  ),
                ),
              ],
            ),
          ],
          if (widget.einsatz.kategorie != null) ...[
            const SizedBox(height: 20),
            Container(
              padding:
                  const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: AppColors.warning.withValues(alpha: 0.15),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(
                    color: AppColors.warning.withValues(alpha: 0.3)),
              ),
              child: Text(
                widget.einsatz.kategorie!,
                style: const TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                  color: AppColors.warning,
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  // ── Stiller Alarm ──
  Widget _buildSilentAlarm() {
    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 24),
      child: Column(
        children: [
          const SizedBox(height: 20),
          AnimatedBuilder(
            animation: _pulseController,
            builder: (_, __) {
              final opacity = 0.4 + _pulseController.value * 0.6;
              return Opacity(
                opacity: opacity,
                child: Container(
                  width: 100,
                  height: 100,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: AppColors.warning.withValues(alpha: 0.15),
                  ),
                  child: const Center(
                    child: Text('⚡', style: TextStyle(fontSize: 48)),
                  ),
                ),
              );
            },
          ),
          const SizedBox(height: 20),
          const Text(
            'Einsatz eingegangen',
            style: TextStyle(
              fontSize: 22,
              fontWeight: FontWeight.bold,
              color: AppColors.warning,
            ),
          ),
          const SizedBox(height: 8),
          Container(
            padding:
                const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            decoration: BoxDecoration(
              color: AppColors.bgCard,
              borderRadius: BorderRadius.circular(20),
            ),
            child: const Text(
              'Klassenarbeitsmodus · Nur Lichtsignal',
              style:
                  TextStyle(fontSize: 13, color: AppColors.textSecondary),
            ),
          ),
          const SizedBox(height: 32),
          _buildEinsatzCard(),
        ],
      ),
    );
  }

  // ── Dismiss-Bereich ──
  Widget _buildDismissArea() {
    if (widget.mode == 'silent') {
      return Padding(
        padding: const EdgeInsets.fromLTRB(24, 8, 24, 24),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 10),
          decoration: BoxDecoration(
            color: AppColors.bgCard.withValues(alpha: 0.5),
            borderRadius: BorderRadius.circular(12),
          ),
          child: const Center(
            child: Text('Verschwindet automatisch nach 10 Minuten',
                style:
                    TextStyle(fontSize: 13, color: AppColors.textSecondary)),
          ),
        ),
      );
    }

    return Padding(
      padding: const EdgeInsets.fromLTRB(24, 0, 24, 32),
      child: Column(
        children: [
          const Text('Zum Schließen schieben',
              style: TextStyle(fontSize: 13, color: AppColors.textSecondary)),
          const SizedBox(height: 12),
          _SlideToAction(onDismiss: _dismiss),
        ],
      ),
    );
  }
}

// ── Slide-to-Action Widget ──
class _SlideToAction extends StatefulWidget {
  final VoidCallback onDismiss;
  const _SlideToAction({required this.onDismiss});

  @override
  State<_SlideToAction> createState() => _SlideToActionState();
}

class _SlideToActionState extends State<_SlideToAction> {
  double _dragX = 0;
  double _maxDrag = 0;
  bool _triggered = false;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(builder: (context, constraints) {
      _maxDrag = constraints.maxWidth - 72;
      final progress = (_dragX / _maxDrag).clamp(0.0, 1.0);

      return Container(
        height: 64,
        decoration: BoxDecoration(
          color: const Color(0xFF1A1A2E),
          borderRadius: BorderRadius.circular(32),
          border: Border.all(
            color:
                AppColors.alarmRed.withValues(alpha: 0.2 + progress * 0.4),
            width: 1.5,
          ),
        ),
        child: Stack(
          children: [
            // Fortschritts-Füllung
            ClipRRect(
              borderRadius: BorderRadius.circular(32),
              child: Align(
                alignment: Alignment.centerLeft,
                child: Container(
                  width: 72 + _dragX,
                  height: 64,
                  decoration: BoxDecoration(
                    gradient: LinearGradient(colors: [
                      AppColors.alarmRed.withValues(alpha: 0.3),
                      AppColors.alarmRed.withValues(alpha: 0.05),
                    ]),
                  ),
                ),
              ),
            ),
            // Label
            Center(
              child: Opacity(
                opacity: 1.0 - progress,
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const SizedBox(width: 48),
                    const Text('Einsatz bestätigen',
                        style: TextStyle(
                          color: AppColors.textSecondary,
                          fontSize: 15,
                          fontWeight: FontWeight.w500,
                        )),
                    const SizedBox(width: 8),
                    Icon(Icons.arrow_forward_ios,
                        color:
                            AppColors.textSecondary.withValues(alpha: 0.5),
                        size: 14),
                  ],
                ),
              ),
            ),
            // Drag-Thumb
            Positioned(
              left: 4 + _dragX,
              top: 4,
              child: GestureDetector(
                onHorizontalDragUpdate: (d) {
                  if (_triggered) return;
                  setState(() {
                    _dragX =
                        (_dragX + d.delta.dx).clamp(0.0, _maxDrag);
                  });
                },
                onHorizontalDragEnd: (_) {
                  if (_triggered) return;
                  if (_dragX / _maxDrag > 0.85) {
                    setState(() {
                      _triggered = true;
                      _dragX = _maxDrag;
                    });
                    HapticFeedback.heavyImpact();
                    widget.onDismiss();
                  } else {
                    setState(() => _dragX = 0);
                  }
                },
                child: Container(
                  width: 56,
                  height: 56,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: const LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: [AppColors.alarmRed, AppColors.alarmRedDark],
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: AppColors.alarmRed.withValues(alpha: 0.4),
                        blurRadius: 12,
                        spreadRadius: 2,
                      ),
                    ],
                  ),
                  child: const Icon(Icons.chevron_right,
                      color: Colors.white, size: 28),
                ),
              ),
            ),
          ],
        ),
      );
    });
  }
}
