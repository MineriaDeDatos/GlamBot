import 'package:flutter/material.dart';
import 'name_screen.dart'; // Importamos la nueva pantalla

class HomeScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          // Fondo de pantalla
          Positioned.fill(
            child: Image.asset(
              'assets/images/logo.jpg', // Asegúrate de que el archivo esté en la carpeta correcta
              fit: BoxFit.cover,
            ),
          ),

          // Botón para ir a la pantalla del nombre
          Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                ElevatedButton(
                  onPressed: () {
                    // Transición a la pantalla NameScreen
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (context) => NameScreen()),
                    );
                  },
                  child: Text("Comenzar"),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.black, // Color de fondo del botón
                    padding: EdgeInsets.symmetric(horizontal: 30, vertical: 15),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(10),
                    ),
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
