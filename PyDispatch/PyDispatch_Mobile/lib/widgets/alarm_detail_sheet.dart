import 'package:flutter/material.dart';

import '../models/alarm_event.dart';

class AlarmDetailSheet extends StatelessWidget {
  const AlarmDetailSheet({
    super.key,
    required this.alarm,
    required this.onDismiss,
  });

  final AlarmEvent alarm;
  final VoidCallback onDismiss;

  @override
  Widget build(BuildContext context) {
    return Dismissible(
      key: ValueKey('alarm_${alarm.id}'),
      direction: DismissDirection.up,
      onDismissed: (_) => onDismiss(),
      child: Container(
        margin: const EdgeInsets.all(16),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.red.shade700,
          borderRadius: BorderRadius.circular(16),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'ALARM',
              style: TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text('Stichwort: ${alarm.keyword}', style: const TextStyle(color: Colors.white, fontSize: 16)),
            const SizedBox(height: 4),
            Text('Ort: ${alarm.location}', style: const TextStyle(color: Colors.white, fontSize: 16)),
            const SizedBox(height: 10),
            const Text(
              'Zum Schließen nach oben wischen',
              style: TextStyle(color: Colors.white70, fontSize: 13),
            ),
          ],
        ),
      ),
    );
  }
}
