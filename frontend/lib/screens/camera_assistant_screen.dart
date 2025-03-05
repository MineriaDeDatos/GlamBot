import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_webrtc/flutter_webrtc.dart';
import 'package:http/http.dart' as http;

class WebRTCVideoScreen extends StatefulWidget {
  @override
  _WebRTCVideoScreenState createState() => _WebRTCVideoScreenState();
}

class _WebRTCVideoScreenState extends State<WebRTCVideoScreen> {
  RTCPeerConnection? _peerConnection;
  MediaStream? _localStream;
  RTCVideoRenderer _remoteRenderer = RTCVideoRenderer();
  RTCVideoRenderer _localRenderer = RTCVideoRenderer();
  String _faceType = ''; // Tipo de rostro
  double _confidence = 0.0; // Probabilidad de clasificación

  @override
  void initState() {
    super.initState();
    initRenderers();
    startCall();
  }

  @override
  void dispose() {
    _remoteRenderer.dispose();
    _localRenderer.dispose();
    _peerConnection?.close();
    super.dispose();
  }

  Future<void> initRenderers() async {
    await _remoteRenderer.initialize();
    await _localRenderer.initialize();
  }

  Future<void> startCall() async {
    // Obtener la cámara y crear el stream local con resolución máxima
    _localStream = await navigator.mediaDevices.getUserMedia({
      'audio': false,
      'video': {
        'facingMode': 'user', // Cámara frontal
        'width': {'ideal': 1920}, // Resolución máxima deseada
        'height': {'ideal': 1080}, // Resolución máxima deseada
        'frameRate': {'ideal': 30}, // Asegurar 30 fps
      },
    });

    _localRenderer.srcObject = _localStream;

    // Configuración avanzada de la conexión peer con requisitos de resolución
    Map<String, dynamic> configuration = {
      "iceServers": [
        {"urls": "stun:stun.l.google.com:19302"},
      ],
    };

    _peerConnection = await createPeerConnection(configuration);

    // Establecer preferencias de resolución para el stream remoto
    var constraints = {
      "mandatory": {
        "OfferToReceiveVideo": true,
        "maxWidth": 1920, // Establecer resolución máxima
        "maxHeight": 1080,
        "maxFrameRate": 30,
      },
      "optional": [],
    };

    // Agregar el stream local a la conexión
    _localStream?.getTracks().forEach((track) {
      _peerConnection?.addTrack(track, _localStream!);
    });

    // Escuchar la pista remota
    _peerConnection?.onTrack = (RTCTrackEvent event) {
      if (event.track.kind == "video") {
        setState(() {
          _remoteRenderer.srcObject = event.streams[0];
        });
      }
    };

    // Crear oferta
    RTCSessionDescription offer = await _peerConnection!.createOffer();
    await _peerConnection!.setLocalDescription(offer);

    // Enviar la oferta al servidor (ajusta la IP y puerto)
    var response = await http.post(
      Uri.parse("http://192.168.100.183:8080/offer"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"sdp": offer.sdp, "type": offer.type}),
    );

    var responseJson = jsonDecode(response.body);
    RTCSessionDescription answer = RTCSessionDescription(
      responseJson["sdp"],
      responseJson["type"],
    );
    await _peerConnection!.setRemoteDescription(answer);

    // Actualizar tipo de rostro y confianza
    updateFaceClassification(responseJson);
  }

  // Función para actualizar el tipo de rostro y la confianza
  void updateFaceClassification(Map<String, dynamic> responseJson) {
    if (responseJson.containsKey("predictions")) {
      var predictions = responseJson["predictions"];
      if (predictions.isNotEmpty) {
        setState(() {
          _faceType = predictions[0]["class"];
          _confidence = predictions[0]["confidence"];
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("WebRTC con YOLO")),
      body: Column(
        children: [
          // Barra de información con tipo de rostro y confianza
          Container(
            color: Colors.black.withOpacity(0.6),
            padding: EdgeInsets.all(10),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  "Tipo de rostro: $_faceType",
                  style: TextStyle(color: Colors.white, fontSize: 18),
                ),
                Text(
                  "Confianza: ${(_confidence * 100).toStringAsFixed(2)}%",
                  style: TextStyle(color: Colors.white, fontSize: 18),
                ),
              ],
            ),
          ),
          // Vista remota
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
        ],
      ),
    );
  }
}
