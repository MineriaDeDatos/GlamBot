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
              'assets/images/background.jpg',
              fit: BoxFit.cover,
            ),
          ),
          SafeArea(
            child: Center(
              child: Container(
                padding: EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.85),
                  borderRadius: BorderRadius.circular(15),
                ),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    // Mensaje del asistente
                    Text(
                      "¡Hola! Soy tu asistente virtual 💁‍♀️",
                      style: TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: AppTheme.primaryColor,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    SizedBox(height: 20),
                    Text(
                      "Por favor, prueba la cámara para continuar con la experiencia.",
                      style: TextStyle(
                        fontSize: 18,
                        color: Colors.black87,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    SizedBox(height: 30),
                    // Botón para abrir la cámara
                    ElevatedButton.icon(
                      onPressed: _openCamera,
                      icon: const Icon(Icons.camera_alt),
                      label: const Text('Abrir Cámara'),
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(horizontal: 30, vertical: 15),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(10),
                        ),
                        backgroundColor: AppTheme.primaryColor,
                        foregroundColor: Colors.white,
                      ),
                    ),
                    SizedBox(height: 30),
                    // Instrucciones o mensaje adicional
                    Text(
                      "Haz clic en el botón para tomar una foto y seguir.",
                      style: TextStyle(
                        fontSize: 16,
                        color: Colors.black87,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    SizedBox(height: 30),
                    // Botón para continuar a la siguiente pantalla (donde se muestra la cámara en tiempo real y el asistente interactúa)
                    ElevatedButton(
                      onPressed: () {
                        // Navega a la siguiente pantalla
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => CameraAssistantScreen(),
                          ),
                        );
                      },
                      child: Text("Continuar"),
                      style: ElevatedButton.styleFrom(
                        padding: EdgeInsets.symmetric(horizontal: 40, vertical: 15),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(10),
                        ),
                        backgroundColor: AppTheme.primaryColor,
                        foregroundColor: Colors.white,
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
