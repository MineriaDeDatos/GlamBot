import 'dart:io';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
import 'AssistantScreen.dart';
import 'camera_assistant_screen.dart';

class PreviewScreen extends StatelessWidget {
  final XFile? imageFile;

  PreviewScreen({Key? key, required this.imageFile}) : super(key: key);

  // Función para enviar la imagen al servidor y validar la respuesta
  Future<bool> sendImageToServer(XFile imageFile) async {
    final request = http.MultipartRequest(
      'POST',
      Uri.parse('http://192.168.1.88:5000/receive_photo'),
    );

    request.files.add(
      await http.MultipartFile.fromPath('photo', imageFile.path),
    );

    try {
      final response = await request.send();
      if (response.statusCode == 200) {
        print('Imagen enviada correctamente');
        return true; // Permitir la navegación
      } else {
        print('Error al enviar la imagen: ${response.statusCode}');
        return false; // Bloquear la navegación
      }
    } catch (e) {
      print('Error al enviar la imagen: $e');
      return false;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("Vista Previa")),
      body: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          if (imageFile != null) Image.file(File(imageFile!.path), height: 300),
          SizedBox(height: 20),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              ElevatedButton(
                onPressed: () async {
                  bool success = await sendImageToServer(imageFile!);
                  if (success) {
                    // Solo navegar si la imagen fue aceptada
                    Navigator.pushReplacement(
                      context,
                      MaterialPageRoute(
                        builder: (context) => AssistantScreen(),
                      ),
                    );
                  } else {
                    // Mostrar alerta si la imagen es rechazada
                    showDialog(
                      context: context,
                      builder: (BuildContext context) {
                        return AlertDialog(
                          title: Text("Error"),
                          content: Text(
                            "No se detectó un rostro en la imagen. Intenta nuevamente.",
                          ),
                          actions: [
                            TextButton(
                              child: Text("Aceptar"),
                              onPressed: () {
                                Navigator.of(context).pop();
                              },
                            ),
                          ],
                        );
                      },
                    );
                  }
                },
                child: Text("Aceptar"),
              ),
              SizedBox(width: 20),
              ElevatedButton(
                onPressed: () {
                  Navigator.pushReplacement(
                    context,
                    MaterialPageRoute(
                      builder: (context) => WebRTCVideoScreen(),
                    ),
                  );
                },
                child: Text("Rechazar"),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
