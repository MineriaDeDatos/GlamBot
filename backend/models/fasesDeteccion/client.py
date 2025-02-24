import argparse
import asyncio
import json
import logging

import cv2
import numpy as np
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from aiortc.contrib.media import MediaBlackhole
from ultralytics import YOLO

logger = logging.getLogger("pc")
pcs = set()

# Cargar el modelo YOLOv8 (.pt); ajusta la ruta según corresponda
model = YOLO("C:/Users/ASUS/Desktop/MineriaPF/Backend/Modelos/fashion_model.pt")

class VideoTransformTrack(VideoStreamTrack):
    """
    Un track de video que transforma cada fotograma aplicándole YOLO.
    """
    def __init__(self, track):
        super().__init__()  # inicializa la clase padre
        self.track = track

    async def recv(self):
        frame = await self.track.recv()
        # Convertir el fotograma a una imagen BGR (numpy array)
        img = frame.to_ndarray(format="bgr24")
        # Procesar la imagen con YOLOv8
        results = model(img)
        annotated_img = results[0].plot()  # La imagen anotada en formato BGR
        # Crear un nuevo frame a partir de la imagen procesada
        new_frame = frame.from_ndarray(annotated_img, format="bgr24")
        new_frame.pts = frame.pts
        new_frame.time_base = frame.time_base
        return new_frame

async def offer(request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("iceconnectionstatechange")
    async def on_iceconnectionstatechange():
        print("ICE connection state is %s" % pc.iceConnectionState)
        if pc.iceConnectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    # Configurar la conexión remota
    await pc.setRemoteDescription(offer)

    # Reemplazar la pista de video entrante por una que aplique la transformación YOLO
    for t in pc.getTransceivers():
        if t.kind == "video" and t.receiver.track:
            local_video = VideoTransformTrack(t.receiver.track)
            pc.addTrack(local_video)

    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.Response(
        content_type="application/json",
        text=json.dumps({
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type,
        }),
    )

async def on_shutdown(app):
    # Cierra todas las conexiones
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0", help="Host para escuchar")
    parser.add_argument("--port", type=int, default=8080, help="Puerto para escuchar")
    args = parser.parse_args()

    app = web.Application()
    app.router.add_post("/offer", offer)
    app.on_shutdown.append(on_shutdown)
    web.run_app(app, host=args.host, port=args.port)
