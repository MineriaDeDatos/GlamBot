import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_webrtc/flutter_webrtc.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
import 'package:path_provider/path_provider.dart';
import 'PreviewScreen.dart'; // Importamos la pantalla de vista previa

class WebRTCVideoScreen extends StatefulWidget {
  @override
  _WebRTCVideoScreenState createState() => _WebRTCVideoScreenState();
}

class _WebRTCVideoScreenState extends State<WebRTCVideoScreen> {
  RTCPeerConnection? _peerConnection;
  MediaStream? _localStream;
  RTCVideoRenderer _remoteRenderer = RTCVideoRenderer();
  RTCVideoRenderer _localRenderer = RTCVideoRenderer();
  XFile? _imageFile; // Foto tomada

  @override
  void initState() {
    super.initState();
    initRenderers();
    startCall();
  }

  @override
  void dispose() {
    _closeConnection(); // Cerrar conexión al salir de la pantalla
    super.dispose();
  }

  Future<void> initRenderers() async {
    await _remoteRenderer.initialize();
    await _localRenderer.initialize();
  }

  Future<void> startCall() async {
    _localStream = await navigator.mediaDevices.getUserMedia({
      'audio': false,
      'video': {
        'facingMode': 'user',
        'width': {'ideal': 1920},
        'height': {'ideal': 1080},
        'frameRate': {'ideal': 30},
      },
    });

    _localRenderer.srcObject = _localStream;

    Map<String, dynamic> configuration = {
      "iceServers": [
        {"urls": "stun:stun.l.google.com:19302"},
      ],
    };

    _peerConnection = await createPeerConnection(configuration);

    _localStream?.getTracks().forEach((track) {
      _peerConnection?.addTrack(track, _localStream!);
    });

    _peerConnection?.onTrack = (RTCTrackEvent event) {
      if (event.track.kind == "video") {
        setState(() {
          _remoteRenderer.srcObject = event.streams[0];
        });
      }
    };

    RTCSessionDescription offer = await _peerConnection!.createOffer();
    await _peerConnection!.setLocalDescription(offer);

    var response = await http.post(
      Uri.parse("http://192.168.1.88:8080/offer"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"sdp": offer.sdp, "type": offer.type}),
    );

    var responseJson = jsonDecode(response.body);
    RTCSessionDescription answer = RTCSessionDescription(
      responseJson["sdp"],
      responseJson["type"],
    );
    await _peerConnection!.setRemoteDescription(answer);
  }

  Future<void> _takePhoto() async {
    final picker = ImagePicker();
    final image = await picker.pickImage(source: ImageSource.camera);
    if (image != null) {
      setState(() {
        _imageFile = image;
      });

      final directory = await getTemporaryDirectory();
      final imagePath = '${directory.path}/photo.jpg';
      await File(
        image.path,
      ).copy(imagePath); // Guardar en el directorio temporal

      // Cerrar conexión antes de navegar a la vista previa
      _closeConnection();

      // Navegar a la vista previa
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (context) => PreviewScreen(imageFile: _imageFile),
        ),
      );
    }
  }

  void _closeConnection() {
    _peerConnection?.close();
    _peerConnection = null;
    _localStream?.dispose();
    _localStream = null;
    _remoteRenderer.srcObject = null;
    _localRenderer.srcObject = null;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("WebRTC con YOLO")),
      body: Column(
        children: [
          Expanded(
            child: Container(
              width: double.infinity,
              height: double.infinity,
              child: RTCVideoView(
                _remoteRenderer,
                objectFit: RTCVideoViewObjectFit.RTCVideoViewObjectFitCover,
              ),
            ),
          ),
          ElevatedButton(onPressed: _takePhoto, child: Text("Tomar Foto")),
        ],
      ),
    );
  }
}
