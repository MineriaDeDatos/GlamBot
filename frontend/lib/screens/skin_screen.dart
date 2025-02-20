import 'package:flutter/material.dart';

class SkinScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final skinTypes = ['Grasa', 'Mixta', 'Seca', 'Normal'];
    return Scaffold(
      appBar: AppBar(title: Text('¿Cuál es tu tipo de piel?')),
      body: ListView.builder(
        padding: EdgeInsets.all(20),
        itemCount: skinTypes.length,
        itemBuilder: (context, index) {
          final type = skinTypes[index];
          return Card(
            margin: EdgeInsets.symmetric(vertical: 10),
            child: ListTile(
              title: Text(type, style: TextStyle(fontSize: 18)),
              onTap: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('Seleccionaste $type')),
                );
              },
            ),
          );
        },
      ),
    );
  }
}
