import 'package:flutter/material.dart';
import 'skin_screen.dart';

class MakeupScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final makeupOptions = ['Natural', 'Glamuroso', 'Fiesta', 'Casual'];
    return Scaffold(
      appBar: AppBar(title: Text('Elige tu maquillaje 💕')),
      body: ListView.builder(
        padding: EdgeInsets.all(20),
        itemCount: makeupOptions.length,
        itemBuilder: (context, index) {
          final option = makeupOptions[index];
          return Card(
            margin: EdgeInsets.symmetric(vertical: 10),
            child: ListTile(
              title: Text(option, style: TextStyle(fontSize: 18)),
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => SkinScreen()),
                );
              },
            ),
          );
        },
      ),
    );
  }
}
