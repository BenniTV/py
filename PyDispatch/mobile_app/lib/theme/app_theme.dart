/// PyDispatch Mobile – App-Theme.
/// Modernes dunkles Farbschema mit Premium-Look.
import 'package:flutter/material.dart';

class AppColors {
  // Primärfarben
  static const primary = Color(0xFF4A90FF);
  static const primaryDark = Color(0xFF2D6DD9);
  static const primaryLight = Color(0xFF6AAFFF);

  // Status-Farben
  static const success = Color(0xFF34D399);
  static const successDark = Color(0xFF059669);
  static const danger = Color(0xFFEF4444);
  static const dangerDark = Color(0xFFDC2626);
  static const warning = Color(0xFFFBBF24);
  static const warningDark = Color(0xFFD97706);

  // Alarm
  static const alarmRed = Color(0xFFFF1744);
  static const alarmRedDark = Color(0xFFD50000);

  // Hintergründe – tiefes Dunkelblau statt Grau
  static const bgDark = Color(0xFF0F1123);
  static const bgCard = Color(0xFF1A1D35);
  static const bgCardLight = Color(0xFF232847);
  static const bgInput = Color(0xFF252A4A);
  static const bgSurface = Color(0xFF161930);

  // Text
  static const text = Color(0xFFE8ECF4);
  static const textSecondary = Color(0xFF8B92B0);
  static const textMuted = Color(0xFF5C6385);

  // Rahmen
  static const border = Color(0xFF2A2F52);
  static const borderLight = Color(0xFF353B66);

  // Status-Farben für Home-Screen
  static const statusSchool = Color(0xFF34D399);
  static const statusAway = Color(0xFFEF4444);
  static const statusExam = Color(0xFFFBBF24);
}

ThemeData appTheme() {
  return ThemeData(
    brightness: Brightness.dark,
    scaffoldBackgroundColor: AppColors.bgDark,
    primaryColor: AppColors.primary,
    fontFamily: 'SF Pro Display',
    colorScheme: const ColorScheme.dark(
      primary: AppColors.primary,
      secondary: AppColors.success,
      surface: AppColors.bgCard,
      error: AppColors.danger,
    ),
    appBarTheme: const AppBarTheme(
      backgroundColor: Colors.transparent,
      elevation: 0,
      centerTitle: true,
      titleTextStyle: TextStyle(
        fontSize: 18,
        fontWeight: FontWeight.w600,
        color: AppColors.text,
      ),
    ),
    cardTheme: CardThemeData(
      color: AppColors.bgCard,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: const BorderRadius.all(Radius.circular(16)),
        side: BorderSide(color: AppColors.border.withValues(alpha: 0.5)),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: AppColors.bgInput,
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      border: OutlineInputBorder(
        borderRadius: const BorderRadius.all(Radius.circular(12)),
        borderSide: BorderSide(color: AppColors.border.withValues(alpha: 0.5)),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: const BorderRadius.all(Radius.circular(12)),
        borderSide: BorderSide(color: AppColors.border.withValues(alpha: 0.5)),
      ),
      focusedBorder: const OutlineInputBorder(
        borderRadius: BorderRadius.all(Radius.circular(12)),
        borderSide: BorderSide(color: AppColors.primary, width: 2),
      ),
      labelStyle: const TextStyle(color: AppColors.textSecondary, fontSize: 14),
      hintStyle: const TextStyle(color: AppColors.textMuted, fontSize: 14),
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: AppColors.primary,
        foregroundColor: Colors.white,
        minimumSize: const Size(double.infinity, 52),
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(14),
        ),
        textStyle: const TextStyle(
          fontSize: 16,
          fontWeight: FontWeight.w600,
          letterSpacing: 0.3,
        ),
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: AppColors.primary,
        minimumSize: const Size(double.infinity, 52),
        side: const BorderSide(color: AppColors.primary, width: 1.5),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(14),
        ),
        textStyle: const TextStyle(
          fontSize: 16,
          fontWeight: FontWeight.w600,
        ),
      ),
    ),
    textTheme: const TextTheme(
      headlineLarge: TextStyle(
          fontSize: 28, fontWeight: FontWeight.w800, color: AppColors.text,
          letterSpacing: -0.5, decoration: TextDecoration.none),
      headlineMedium: TextStyle(
          fontSize: 24, fontWeight: FontWeight.w700, color: AppColors.text,
          letterSpacing: -0.3, decoration: TextDecoration.none),
      titleLarge: TextStyle(
          fontSize: 20, fontWeight: FontWeight.w600, color: AppColors.text,
          decoration: TextDecoration.none),
      titleMedium: TextStyle(
          fontSize: 16, fontWeight: FontWeight.w600, color: AppColors.text,
          decoration: TextDecoration.none),
      bodyLarge: TextStyle(fontSize: 16, color: AppColors.text,
          decoration: TextDecoration.none),
      bodyMedium: TextStyle(fontSize: 14, color: AppColors.text,
          decoration: TextDecoration.none),
      bodySmall: TextStyle(fontSize: 12, color: AppColors.textSecondary,
          decoration: TextDecoration.none),
    ),
  );
}
