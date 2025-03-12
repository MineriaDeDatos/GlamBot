import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'package:audioplayers/audioplayers.dart';
import 'package:http/http.dart' as http;
import 'GeneradorMaquillajeScreen.dart'; // Actualiza con la ruta correcta

class AssistantScreen extends StatefulWidget {
  @override
  _AssistantScreenState createState() => _AssistantScreenState();
}

class _AssistantScreenState extends State<AssistantScreen> {
  final WebSocketChannel channel = WebSocketChannel.connect(
    Uri.parse('ws://192.168.1.88:5001/socket.io/?EIO=4&transport=websocket'),
  );

  List<String> messages = [
    "Asistente: ¡Hola! ¿En qué puedo ayudarte?, puedes decir 'salir' o 'terminar' para finalizar la conversación.",
  ];
  String promptFinal = "";
  stt.SpeechToText _speechToText = stt.SpeechToText();
  bool _isListening = false;
  AudioPlayer _audioPlayer = AudioPlayer();
  bool _interactionEnded = false;

  @override
  void dispose() {
    // Detener la escucha de voz y la reproducción de audio cuando se cambie de pantalla
    _speechToText.stop();
    _audioPlayer.stop();
    channel.sink.close();
    _audioPlayer.dispose();
    super.dispose();
  }

  Future<Map<String, dynamic>> _sendMessageToBackend(String message) async {
    final response = await http.post(
      Uri.parse('http://192.168.1.88:5001/interact'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'message': message, 'conversation_history': []}),
    );

    if (response.statusCode == 200) {
      Map<String, dynamic> responseBody = jsonDecode(response.body);
      promptFinal = responseBody['text_response'];
      return responseBody;
    } else {
      throw Exception('Failed to load response');
    }
  }

  void listenAndSendMessage() async {
    if (!_isListening) {
      bool available = await _speechToText.initialize();
      if (available) {
        setState(() => _isListening = true);

        _speechToText.listen(
          onResult: (result) async {
            if (result.hasConfidenceRating && result.confidence > 0.5) {
              String userInput = result.recognizedWords;
              if (userInput.isNotEmpty) {
                setState(() => messages.add("Tú: $userInput"));

                final response = await _sendMessageToBackend(userInput);
                setState(
                  () => messages.add("Asistente: ${response['text_response']}"),
                );

                _playAudio(response['audio_response']);

                if (userInput.toLowerCase().contains("salir") ||
                    userInput.toLowerCase().contains("terminar") ||
                    userInput.toLowerCase().contains("adiós")) {
                  setState(() => _interactionEnded = true);
                }
              }
            }
          },
        );
      }
    } else {
      _speechToText.stop();
      setState(() => _isListening = false);
    }
  }

  void _playAudio(String audioData) async {
    try {
      Uint8List bytes = base64Decode(audioData);
      await _audioPlayer.play(BytesSource(bytes));
    } catch (e) {
      print("Error al reproducir el audio: $e");
    }
  }

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
      appBar: AppBar(
        title: Text("GlamBot 💋💄"),
        backgroundColor: Colors.purple, // Fondo morado para el AppBar
        automaticallyImplyLeading: false, // Elimina el ícono de regreso
      ),
      body: Stack(
        children: [
          Positioned.fill(
            child: Image.asset(
              'assets/images/background.jpg', // Asegúrate de tener esta imagen en assets
              fit:
                  BoxFit
                      .cover, // Ajusta la imagen para que cubra todo el área disponible
            ),
          ),
          Column(
            children: [
              Expanded(
                child: ListView.builder(
                  padding: EdgeInsets.all(16.0),
                  itemCount: messages.length,
                  itemBuilder: (context, index) {
                    return Card(
                      elevation: 2,
                      margin: EdgeInsets.symmetric(vertical: 5),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Padding(
                        padding: EdgeInsets.all(12.0),
                        child: Text(
                          messages[index],
                          style: TextStyle(fontSize: 16),
                        ),
                      ),
                    );
                  },
                ),
              ),
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  children: [
                    IconButton(
                      icon: Icon(
                        _isListening ? Icons.stop_circle : Icons.mic,
                        size: 40,
                      ),
                      color: _isListening ? Colors.red : Colors.blue,
                      onPressed: listenAndSendMessage,
                    ),
                    SizedBox(height: 10),
                    AnimatedSwitcher(
                      duration: Duration(milliseconds: 300),
                      child:
                          _interactionEnded
                              ? Container(
                                width: double.infinity,
                                height: 50,
                                child: ElevatedButton(
                                  onPressed: navigateToMakeupGenerator,
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor:
                                        Colors.purple, // Fondo morado
                                    shape: RoundedRectangleBorder(
                                      borderRadius: BorderRadius.circular(25),
                                    ),
                                  ),
                                  child: Text(
                                    "Generar Maquillaje",
                                    style: TextStyle(fontSize: 18),
                                  ),
                                ),
                              )
                              : SizedBox.shrink(),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
