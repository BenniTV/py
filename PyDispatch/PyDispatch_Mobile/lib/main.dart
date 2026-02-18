import 'package:flutter/material.dart';

import 'app.dart';
import 'repositories/mysql_mobile_repository.dart';
import 'services/config_service.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();

  runApp(
    PyDispatchMobileApp(
      repository: MysqlMobileRepository(),
      configService: ConfigService(),
    ),
  );
}
