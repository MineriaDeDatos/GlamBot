import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'name_screen.dart'; // Importamos la nueva pantalla

class HomeScreen extends StatefulWidget {
  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final ImagePicker _picker = ImagePicker();
  XFile? _image;
  stt.SpeechToText _speech = stt.SpeechToText();
  bool _isListening = false;
  String _text = "Presiona el botón para hablar...";

  // 📷 Función para abrir la cámara
  Future<void> _openCamera() async {
    try {
      final XFile? image = await _picker.pickImage(source: ImageSource.camera);
      if (image != null) {
        setState(() {
          _image = image;
        });
      }
    } catch (e) {
      print("Error al abrir la cámara: $e");
    }
  }

  // 🎤 Función para iniciar el asistente de voz
  void _listenAssistant() async {
    if (!_isListening) {
      bool available = await _speech.initialize(
        onStatus: (status) => print('Estado: $status'),
        onError: (error) => print('Error: $error'),
      );

      if (available) {
        setState(() => _isListening = true);
        _speech.listen(
          onResult: (result) {
            setState(() {
              _text = result.recognizedWords;
            });
          },
        );
      }
    } else {
      setState(() => _isListening = false);
      _speech.stop();
    }
  }

  // 📌 Función para ir a la pantalla del nombre
  void _goToNameScreen() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => NameScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          // 📌 Fondo de pantalla
          Positioned.fill(
            child: Image.asset(
              'assets/images/logo.jpg', // Asegúrate de que el archivo esté en la carpeta correcta
              fit: BoxFit.cover,
            ),
          ),

          // 📷 Botón para abrir la cámara
          Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                ElevatedButton.icon(
                  onPressed: _openCamera,
                  icon: const Icon(Icons.camera_alt),
                  label: const Text('Abrir Cámara'),
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 30,
                      vertical: 15,
                    ),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(10),
                    ),
                  ),
                ),
                SizedBox(height: 20), // Espaciado
                ElevatedButton(
                  onPressed: _goToNameScreen,
                  child: Text("Comenzar"),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.pink,
                    padding: EdgeInsets.symmetric(horizontal: 30, vertical: 15),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(10),
                    ),
                  ),
                ),
              ],
            ),
          ),

          // 🎤 Botón para el asistente virtual (esquina inferior derecha)
          Positioned(
            bottom: 20,
            right: 20,
            child: FloatingActionButton(
              onPressed: _listenAssistant,
              backgroundColor: Colors.pink, // Color llamativo
              child: Icon(_isListening ? Icons.mic_off : Icons.mic),
            ),
          ),

          // 📋 Texto que muestra lo que reconoce el asistente
          Positioned(
            bottom: 80,
            left: 20,
            right: 20,
            child: Container(
              padding: EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.8),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Text(
                _text,
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
