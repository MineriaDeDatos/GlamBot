import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'package:audioplayers/audioplayers.dart';
import 'package:http/http.dart' as http;
import 'GeneradorMaquillajeScreen.dart'; // Update with the correct path

class AssistantScreen extends StatefulWidget {
  @override
  _AssistantScreenState createState() => _AssistantScreenState();
}

class _AssistantScreenState extends State<AssistantScreen> {
  final WebSocketChannel channel = WebSocketChannel.connect(
    Uri.parse('ws://192.168.1.88:5001/socket.io/?EIO=4&transport=websocket'),
  );

  List<String> messages = [];
  String promptFinal = ""; // Variable para almacenar el prompt final
  stt.SpeechToText _speechToText = stt.SpeechToText();
  bool _isListening = false;
  AudioPlayer _audioPlayer = AudioPlayer();
  bool _interactionEnded = false;

  @override
  void dispose() {
    channel.sink.close();
    _audioPlayer.dispose();
    super.dispose();
  }

  // Función para enviar mensaje al backend y almacenar el prompt
  Future<Map<String, dynamic>> _sendMessageToBackend(String message) async {
    final response = await http.post(
      Uri.parse('http://192.168.1.88:5001/interact'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'message': message, 'conversation_history': []}),
    );

    if (response.statusCode == 200) {
      Map<String, dynamic> responseBody = jsonDecode(response.body);

      // Almacenar el prompt generado
      promptFinal = responseBody['text_response'];

      // Regresar la respuesta con el audio y texto
      return responseBody;
    } else {
      throw Exception('Failed to load response');
    }
  }

  // Función para escuchar y enviar el mensaje
  void listenAndSendMessage() async {
    if (!_isListening) {
      bool available = await _speechToText.initialize();
      if (available) {
        setState(() {
          _isListening = true;
        });

        _speechToText.listen(
          onResult: (result) async {
            if (result.hasConfidenceRating && result.confidence > 0.5) {
              String userInput = result.recognizedWords;
              if (userInput.isNotEmpty) {
                setState(() {
                  messages.add("Tú: $userInput");
                });

                // Enviar el mensaje al backend para obtener respuesta
                final response = await _sendMessageToBackend(userInput);

                // Mostrar el texto recibido
                setState(() {
                  messages.add("Asistente: ${response['text_response']}");
                });

                // Reproducir el audio
                _playAudio(response['audio_response']);

                // Verificar si el usuario ha dicho "salir", "terminar", o "adiós"
                if (userInput.toLowerCase().contains("salir") ||
                    userInput.toLowerCase().contains("terminar") ||
                    userInput.toLowerCase().contains("adiós")) {
                  setState(() {
                    _interactionEnded = true;
                  });
                }
              }
            }
          },
        );
      }
    } else {
      _speechToText.stop();
      setState(() {
        _isListening = false;
      });
    }
  }

  // Función para reproducir audio
  void _playAudio(String audioData) async {
    try {
      Uint8List bytes = base64Decode(audioData); // Convertir base64 a bytes
      await _audioPlayer.play(BytesSource(bytes)); // Reproducir el audio
    } catch (e) {
      print("Error al reproducir el audio: $e");
    }
  }

  // Función para navegar a la nueva pantalla "Generador de Maquillaje"
  void navigateToMakeupGenerator() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder:
            (context) => GeneradorMaquillajeScreen(promptFinal: promptFinal),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("Asistente de Voz")),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              itemCount: messages.length,
              itemBuilder: (context, index) {
                return ListTile(title: Text(messages[index]));
              },
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Row(
              children: [
                IconButton(
                  icon: Icon(_isListening ? Icons.stop : Icons.mic),
                  onPressed: listenAndSendMessage,
                ),
                if (_interactionEnded)
                  ElevatedButton(
                    onPressed: navigateToMakeupGenerator,
                    child: Text("Generar Maquillaje"),
                    style: ButtonStyle(
                      backgroundColor: MaterialStateProperty.all(Colors.purple),
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
