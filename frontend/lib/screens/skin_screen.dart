import 'package:flutter/material.dart';
import 'assistant_camera_screen.dart'; // Importamos la pantalla de la cámara

class SkinScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final skinTypes = [
      {
        'name': 'Grasa ✨',
        'image': 'https://i.pinimg.com/736x/25/d1/2c/25d12c2fc80bcbf063dd883f6aed3cbb.jpg',
        'description': 'Piel con exceso de brillo y tendencia a acné. 🧴✨',
      },
      {
        'name': 'Mixta 🌿',
        'image': 'https://i.pinimg.com/736x/1c/0a/38/1c0a38947e7d43789453ab82bd0ac0e3.jpg',
        'description': 'Zona T grasa (frente, nariz, barbilla) y mejillas normales o secas. Balance esencial. 🌿💆‍♀️',
      },
      {
        'name': 'Seca 💧',
        'image': 'https://i.pinimg.com/736x/d9/45/cc/d945cc67016b7786a79c8900d1bb346c.jpg',
        'description': 'Piel que se siente tirante y puede descamarse. Necesita mucha hidratación. 💦🧴',
      },
      {
        'name': 'Normal 🌸',
        'image': 'https://i.pinimg.com/736x/a2/e6/eb/a2e6eb5fefdc8ad93c7d5a0f462d0e9f.jpg',
        'description': 'Equilibrada, sin exceso de grasa ni resequedad. Suave y saludable. ✨💖',
      },
    ];

    return Scaffold(
      body: Stack(
        children: [
          // Fondo de pantalla
          Positioned.fill(
            child: Image.asset(
              'assets/images/background.jpg', // Asegúrate de tener esta imagen en assets
              fit: BoxFit.cover,
            ),
          ),
          SafeArea(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                SizedBox(height: 30),
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  child: Column(
                    children: [
                      // Fondo rosa palo para el texto
                      Container(
                        padding: EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: Color.fromARGB(255, 252, 231, 231), // Rosa palo
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: Column(
                          children: [
                            Text(
                              "✨ ¡Queremos saber más sobre ti! ✨",
                              style: TextStyle(
                                fontSize: 26,
                                fontWeight: FontWeight.bold,
                                color: const Color.fromARGB(255, 230, 6, 110),
                                shadows: [
                                  Shadow(
                                    color: Colors.black45,
                                    blurRadius: 5,
                                    offset: Offset(2, 2),
                                  )
                                ],
                              ),
                              textAlign: TextAlign.center,
                            ),
                            SizedBox(height: 10),
                            Text(
                              "Para ayudarte con tu maquillaje 💄, dinos cuál es tu tipo de piel. 💖",
                              style: TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.w400,
                                color: const Color.fromARGB(255, 0, 0, 0),
                                shadows: [
                                  Shadow(
                                    color: Colors.black45,
                                    blurRadius: 3,
                                    offset: Offset(1, 1),
                                  )
                                ],
                              ),
                              textAlign: TextAlign.center,
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                SizedBox(height: 20),
                Expanded(
                  child: ListView.builder(
                    padding: EdgeInsets.symmetric(horizontal: 20),
                    itemCount: skinTypes.length,
                    itemBuilder: (context, index) {
                      final skin = skinTypes[index];

                      return GestureDetector(
                        onTap: () {
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              content: Text('💖 Seleccionaste ${skin['name']}'),
                              behavior: SnackBarBehavior.floating,
                              backgroundColor: Colors.pinkAccent,
                            ),
                          );
                          // Navegar a la cámara después de la selección
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) => AssistantCameraScreen(),
                            ),
                          );
                        },
                        child: Card(
                          color: Colors.white.withOpacity(0.9),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(15),
                          ),
                          elevation: 5,
                          margin: EdgeInsets.symmetric(vertical: 10),
                          child: Padding(
                            padding: EdgeInsets.all(10),
                            child: Row(
                              children: [
                                // Imagen a la izquierda
                                ClipRRect(
                                  borderRadius: BorderRadius.circular(10),
                                  child: Image.network(
                                    skin['image']!,
                                    width: 120, // Tamaño fijo de imagen
                                    height: 120,
                                    fit: BoxFit.cover,
                                    loadingBuilder: (context, child, loadingProgress) {
                                      if (loadingProgress == null) return child;
                                      return Center(child: CircularProgressIndicator());
                                    },
                                    errorBuilder: (context, error, stackTrace) {
                                      return Icon(Icons.error, size: 50, color: Colors.red);
                                    },
                                  ),
                                ),
                                SizedBox(width: 15), // Espacio entre imagen y texto
                                // Texto a la derecha
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        skin['name']!,
                                        style: TextStyle(
                                          fontSize: 18,
                                          fontWeight: FontWeight.bold,
                                          color: Colors.black87,
                                        ),
                                      ),
                                      SizedBox(height: 5),
                                      Text(
                                        skin['description']!,
                                        style: TextStyle(
                                          fontSize: 14,
                                          fontWeight: FontWeight.w400,
                                          color: Colors.black54,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      );
                    },
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
