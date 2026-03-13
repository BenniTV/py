import 'package:flutter_test/flutter_test.dart';
import 'package:pydispatch_mobile/main.dart';

void main() {
  testWidgets('App startet', (WidgetTester tester) async {
    await tester.pumpWidget(const PyDispatchMobileApp());
    // App sollte einen Loading-Indikator zeigen
    expect(find.byType(PyDispatchMobileApp), findsOneWidget);
  });
}
