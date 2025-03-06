import 'dart:io';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
import 'AssistantScreen.dart';
import 'camera_assistant_screen.dart';

class PreviewScreen extends StatelessWidget {
  final XFile? imageFile;

  PreviewScreen({Key? key, required this.imageFile}) : super(key: key);

  // Función para enviar la imagen al servidor
  Future<void> sendImageToServer(XFile imageFile) async {
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
      } else {
        print('Error al enviar la imagen: ${response.statusCode}');
      }
    } catch (e) {
      print('Error al enviar la imagen: $e');
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
                  await sendImageToServer(imageFile!);
                  Navigator.pushReplacement(
                    context,
                    MaterialPageRoute(builder: (context) => AssistantScreen()),
                  );
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
