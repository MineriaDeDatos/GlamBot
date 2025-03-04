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

# Cargar los modelos YOLOv8 (.pt); ajusta la ruta según corresponda
model_deteccion_rosto = YOLO(
    "C:/Users/ASUS/Desktop/MineriaPF/GlamBot/backend/models/fasesDeteccion/Modelos/fashion_model.pt")
model_clasificacion_rosto = YOLO(
    "C:/Users/ASUS/Desktop/MineriaPF/GlamBot/backend/models/fasesDeteccion/Modelos/facesclassification_model.pt")
model_labios = YOLO(
    "C:/Users/ASUS/Desktop/MineriaPF/GlamBot/backend/models/fasesDeteccion/Modelos/lipmakeupdetection21_model.pt")
model_ojos = YOLO(
    "C:/Users/ASUS/Desktop/MineriaPF/GlamBot/backend/models/fasesDeteccion/Modelos/eyesclassification_model.pt")


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

        # Procesar la imagen con YOLOv8 (detección de rostro)
        results_deteccion_rosto = model_deteccion_rosto(img)
        rostras = results_deteccion_rosto[0].boxes  # Obtener las cajas de detección
        annotated_img = img.copy()  # Copia para anotación

        # Clasificación y anotación del tipo de rostro
        for rostro in rostras:
            x1, y1, x2, y2 = map(int, rostro.xyxy[0])  # Coordenadas del rectángulo del rostro
            cv2.rectangle(annotated_img, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Cortar la región del rostro para la clasificación
            rostro_cortado = img[y1:y2, x1:x2]

            # Clasificar el tipo de rostro con el modelo de clasificación
            results_clasificacion_rosto = model_clasificacion_rosto(rostro_cortado)
            probs = results_clasificacion_rosto[0].probs[0]  # Probabilidades como tensor
            probabilidad_maxima = float(results_clasificacion_rosto[0].probs.top1conf)  # Probabilidad más alta
            tipo_rostro = results_clasificacion_rosto[0].names[
                results_clasificacion_rosto[0].probs.top1]  # Tipo de rostro clasificado

            # Escribir el tipo de rostro y la probabilidad en la imagen
            cv2.putText(annotated_img, f"{tipo_rostro} ({probabilidad_maxima * 100:.2f}%)",
                        (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

        # Procesar labios (opcional)
        results_labios = model_labios(img)
        annotated_img_labios = results_labios[0].plot()  # La imagen anotada con los resultados de labios

        # Procesar ojos (opcional)
        results_ojos = model_ojos(img)
        annotated_img_ojos = results_ojos[0].plot()  # La imagen anotada con los resultados de ojos

        # Combinar los resultados de rostro, labios y ojos
        combined_img = cv2.addWeighted(annotated_img, 0.33, annotated_img_labios, 0.33, 0)
        combined_img = cv2.addWeighted(combined_img, 1, annotated_img_ojos, 0.33, 0)

        # Crear un nuevo frame a partir de la imagen procesada
        new_frame = frame.from_ndarray(combined_img, format="bgr24")
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
