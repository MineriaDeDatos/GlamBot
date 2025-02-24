import 'package:flutter/material.dart';
import 'screens/home_screen.dart'; // Importamos la pantalla principal

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false, // Oculta el banner de depuración
      title: 'Beauty App',
      theme: ThemeData(primarySwatch: Colors.pink),
      home: SplashScreen(), // Pantalla de carga inicial
    );
  }
}

class SplashScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    // Simulamos una carga de 2 segundos antes de ir a HomeScreen
    Future.delayed(Duration(seconds: 2), () {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (context) => HomeScreen()),
      );
    });

    return Scaffold(
      body: Center(
        child: CircularProgressIndicator(), // Indicador de carga
      ),
    );
  }
}
