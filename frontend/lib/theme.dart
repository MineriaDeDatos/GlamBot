import 'package:flutter/material.dart';

class AppTheme {
  static Color primaryColor = Color(0xFFE91E63); // Fucsia
  static Color secondaryColor = Color(0xFFF8BBD0); // Rosa suave
  static Color backgroundColor = Color(0xFFFCE4EC); // Fondo rosa claro
  static Color textColor = Color(0xFF212121); // Negro suave

  static ThemeData getTheme() {
    return ThemeData(
      primaryColor: primaryColor,
      scaffoldBackgroundColor: backgroundColor,
      textTheme: TextTheme(
        bodyLarge: TextStyle(color: textColor, fontSize: 18),
        titleLarge: TextStyle(color: textColor, fontSize: 24, fontWeight: FontWeight.bold),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primaryColor,
          foregroundColor: Colors.white,
          padding: EdgeInsets.symmetric(horizontal: 20, vertical: 12),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        ),
      ),
    );
  }
}
