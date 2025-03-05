import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../theme.dart';
import 'camera_assistant_screen.dart'; // Asegúrate de que la ruta sea correcta

class AssistantCameraScreen extends StatefulWidget {
  @override
  _AssistantCameraScreenState createState() => _AssistantCameraScreenState();
}

class _AssistantCameraScreenState extends State<AssistantCameraScreen> {
  final ImagePicker _picker = ImagePicker();
  XFile? _image;

  // Función para abrir la cámara y capturar una imagen.
  Future<void> _openCamera() async {
    try {
      final XFile? image = await _picker.pickImage(source: ImageSource.camera);
      if (image != null) {
        setState(() {
          _image = image;
        });
        // Lógica para continuar después de tomar la foto.
      }
    } catch (e) {
      print("Error al abrir la cámara: $e");
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
              'assets/images/background.jpg', // Asegúrate de que la imagen exista
              fit: BoxFit.cover,
            ),
          ),
          SafeArea(
            child: Center(
              child: Container(
                padding: EdgeInsets.all(30),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.85),
                  borderRadius: BorderRadius.circular(20),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.1),
                      blurRadius: 20,
                      offset: Offset(0, 10),
                    ),
                  ],
                ),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    // Título actualizado
                    Text(
                      "¡Listo, vamos a empezar! Soy tu asistente virtual 💁‍♀️",
                      style: TextStyle(
                        fontSize: 28,
                        fontWeight: FontWeight.bold,
                        color: AppTheme.primaryColor,
                        letterSpacing: 1.2, // Espaciado entre letras
                      ),
                      textAlign: TextAlign.center,
                    ),
                    SizedBox(height: 20),
                    // Descripción
                    Text(
                      "Por favor, asegúrate de tener la cámara y el micrófono habilitados.",
                      style: TextStyle(fontSize: 18, color: Colors.black87),
                      textAlign: TextAlign.center,
                    ),
                    SizedBox(height: 20),
                    Text(
                      "Para un mejor rendimiento, evita usar accesorios como lentes o auriculares.",
                      style: TextStyle(fontSize: 16, color: Colors.black54),
                      textAlign: TextAlign.center,
                    ),
                    SizedBox(height: 40),
                    // Mensaje indicando que es necesario continuar para acceder a la cámara y micro
                    Text(
                      "Al continuar, activaremos la cámara y el micrófono para que puedas interactuar con el asistente.",
                      style: TextStyle(fontSize: 16, color: Colors.black87),
                      textAlign: TextAlign.center,
                    ),
                    SizedBox(height: 40),
                    // Botón para continuar
                    ElevatedButton(
                      onPressed: () {
                        // Navega a la siguiente pantalla (donde se muestra la cámara en tiempo real)
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => WebRTCVideoScreen(),
                          ),
                        );
                      },
                      child: Text("Continuar"),
                      style: ElevatedButton.styleFrom(
                        padding: EdgeInsets.symmetric(
                          horizontal: 40,
                          vertical: 18,
                        ),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(15),
                        ),
                        backgroundColor: AppTheme.primaryColor,
                        foregroundColor: Colors.white,
                        elevation: 5, // Sombra sutil para profundidad
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
