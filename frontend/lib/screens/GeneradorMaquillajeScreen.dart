import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class GeneradorMaquillajeScreen extends StatefulWidget {
  final String promptFinal;

  GeneradorMaquillajeScreen({required this.promptFinal});

  @override
  _GeneradorMaquillajeScreenState createState() =>
      _GeneradorMaquillajeScreenState();
}

class _GeneradorMaquillajeScreenState extends State<GeneradorMaquillajeScreen> {
  String? generatedImageUrl;

  // Función para obtener la imagen del usuario
  Future<Uint8List?> _getUserImage() async {
    try {
      final response = await http.get(
        Uri.parse('http://192.168.1.88:5000/get_photo'),
      );

      if (response.statusCode == 200) {
        return response.bodyBytes; // Devuelve la imagen en bytes
      } else {
        throw Exception('Failed to load image');
      }
    } catch (e) {
      print("Error al obtener la imagen: $e");
      return null;
    }
  }

  // Función para enviar la imagen y el prompt para generar el maquillaje
  Future<void> _generateMakeup() async {
    try {
      final userImage = await _getUserImage();
      if (userImage == null) {
        print("No se pudo obtener la imagen del usuario.");
        return;
      }

      // Se prepara la imagen y el prompt final para enviarlos al servidor
      final uri = Uri.parse('http://192.168.1.88:8000/generate');
      var request =
          http.MultipartRequest('POST', uri)
            ..fields['prompt'] = widget.promptFinal
            ..files.add(
              http.MultipartFile.fromBytes(
                'file',
                userImage,
                filename: 'img.jpg',
              ),
            );

      var response = await request.send();

      if (response.statusCode == 200) {
        // Obtener la respuesta del servidor (en este caso, la imagen generada)
        var responseBody = await http.Response.fromStream(response);
        var imageData = responseBody.bodyBytes;

        setState(() {
          generatedImageUrl = base64Encode(
            imageData,
          ); // Codificamos la imagen en base64 para mostrarla
        });
      } else {
        print("Error al generar el maquillaje: ${response.statusCode}");
      }
    } catch (e) {
      print("Error en la generación del maquillaje: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("Generador de Maquillaje")),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            ElevatedButton(
              onPressed: _generateMakeup,
              child: Text("Generar Maquillaje"),
              style: ButtonStyle(
                backgroundColor: MaterialStateProperty.all(Colors.purple),
              ),
            ),
            if (generatedImageUrl != null)
              Image.memory(
                base64Decode(
                  generatedImageUrl!,
                ), // Decodificar y mostrar la imagen
              ),
          ],
        ),
      ),
    );
  }
}
