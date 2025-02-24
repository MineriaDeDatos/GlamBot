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
    // Obtener la cámara y crear el stream local
    _localStream = await navigator.mediaDevices.getUserMedia({
      'audio': false,
      'video': {'facingMode': 'user'},
    });

    _localRenderer.srcObject = _localStream;

    // Configurar la conexión peer
    Map<String, dynamic> configuration = {
      "iceServers": [
        {"urls": "stun:stun.l.google.com:19302"},
      ],
    };

    _peerConnection = await createPeerConnection(configuration);

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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("WebRTC con YOLO")),
      body: Column(
        children: [
          Expanded(child: RTCVideoView(_remoteRenderer)),
          Container(
            height: 150,
            child: RTCVideoView(_localRenderer, mirror: true),
          ),
        ],
      ),
    );
  }
}
