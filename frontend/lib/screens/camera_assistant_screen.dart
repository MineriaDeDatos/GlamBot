import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import '../theme.dart';

class CameraAssistantScreen extends StatefulWidget {
  @override
  _CameraAssistantScreenState createState() => _CameraAssistantScreenState();
}

class _CameraAssistantScreenState extends State<CameraAssistantScreen> {
  CameraController? _cameraController;
  List<CameraDescription>? _cameras;
  bool _isCameraInitialized = false;
  stt.SpeechToText _speech = stt.SpeechToText();
  bool _isListening = false;
  String _assistantText = "Presiona el micrófono para hablar";

  @override
  void initState() {
    super.initState();
    initializeCamera();
  }

  Future<void> initializeCamera() async {
    try {
      // Obtén la lista de cámaras disponibles
      _cameras = await availableCameras();
      if (_cameras != null && _cameras!.isNotEmpty) {
        // Inicializa la primera cámara (por ejemplo, la trasera)
        _cameraController = CameraController(
          _cameras![0],
          ResolutionPreset.high,
        );
        await _cameraController!.initialize();
        setState(() {
          _isCameraInitialized = true;
        });
      }
    } catch (e) {
      print("Error al inicializar la cámara: $e");
    }
  }

  Future<void> _toggleListening() async {
    if (!_isListening) {
      bool available = await _speech.initialize(
        onStatus: (status) => print("Estado: $status"),
        onError: (error) => print("Error: $error"),
      );
      if (available) {
        setState(() {
          _isListening = true;
          _assistantText = "Escuchando...";
        });
        _speech.listen(
          onResult: (result) {
            setState(() {
              _assistantText = result.recognizedWords;
            });
          },
        );
      }
    } else {
      setState(() {
        _isListening = false;
      });
      _speech.stop();
    }
  }

  @override
  void dispose() {
    _cameraController?.dispose();
    _speech.stop();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _isCameraInitialized
          ? Stack(
              children: [
                // Vista de la cámara en tiempo real
                CameraPreview(_cameraController!),
                // Caja superior con el texto del asistente
                Positioned(
                  top: 40,
                  left: 20,
                  right: 20,
                  child: Container(
                    padding: EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: Colors.black54,
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Text(
                      _assistantText,
                      style: TextStyle(color: Colors.white, fontSize: 18),
                      textAlign: TextAlign.center,
                    ),
                  ),
                ),
                // Botón flotante para activar/desactivar el micrófono
                Positioned(
                  bottom: 20,
                  right: 20,
                  child: FloatingActionButton(
                    onPressed: _toggleListening,
                    backgroundColor: AppTheme.primaryColor,
                    child: Icon(_isListening ? Icons.mic_off : Icons.mic),
                  ),
                ),
              ],
            )
          : Center(child: CircularProgressIndicator()),
    );
  }
}
