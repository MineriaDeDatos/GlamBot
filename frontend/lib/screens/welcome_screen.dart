import 'dart:convert'; // Para usar jsonEncode
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http; // Importa el paquete http
import '../theme.dart';
import 'skin_screen.dart'; // Importamos la pantalla de selección de piel

class WelcomeScreen extends StatelessWidget {
  final String userName;

  const WelcomeScreen({Key? key, required this.userName}) : super(key: key);

  // Función para enviar el nombre al servidor
  Future<void> sendNameToServer(String name) async {
    final response = await http.post(
      Uri.parse(
        'http://192.168.1.88:5000/receive_name',
      ), // Reemplaza con la IP de tu servidor
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'name': name}),
    );

    if (response.statusCode == 200) {
      print('Nombre enviado correctamente');
    } else {
      print('Error al enviar el nombre');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          // Fondo de pantalla
          Positioned.fill(
            child: Image.asset(
              'assets/images/background.jpg',
              fit: BoxFit.cover,
            ),
          ),
          SafeArea(
            child: Center(
              child: Container(
                padding: EdgeInsets.all(30),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.9),
                  borderRadius: BorderRadius.circular(20),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.1),
                      blurRadius: 15,
                      offset: Offset(0, 5),
                    ),
                  ],
                ),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    // Título con estilo mejorado
                    Text(
                      "¡Hola $userName, estamos listos para comenzar! 💖",
                      style: TextStyle(
                        fontSize: 30,
                        fontWeight: FontWeight.bold,
                        color: AppTheme.primaryColor,
                        letterSpacing: 1.2,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    SizedBox(height: 20),
                    // Subtítulo
                    Text(
                      "Es hora de personalizar tu experiencia de maquillaje 🌟",
                      style: TextStyle(
                        fontSize: 20,
                        color: Colors.black87,
                        fontWeight: FontWeight.w400,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    SizedBox(height: 20),
                    // Nombre del usuario
                    Text(
                      "$userName",
                      style: TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: AppTheme.primaryColor,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    SizedBox(height: 30),
                    // Botón "Continuar"
                    ElevatedButton(
                      onPressed: () async {
                        // Enviar el nombre al servidor
                        await sendNameToServer(userName);

                        // Navega a la pantalla de selección de tipo de piel
                        Navigator.push(
                          context,
                          MaterialPageRoute(builder: (context) => SkinScreen()),
                        );
                      },
                      child: Text("Continuar"),
                      style: ElevatedButton.styleFrom(
                        padding: EdgeInsets.symmetric(
                          horizontal: 40,
                          vertical: 15,
                        ),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(20),
                        ),
                        backgroundColor: AppTheme.primaryColor,
                        foregroundColor: Colors.white,
                        elevation: 5, // Sombra
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
