import argparse
import asyncio
import json
import logging
import requests
import cv2
import time
import numpy as np
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from aiortc.contrib.media import MediaBlackhole
from ultralytics import YOLO

logger = logging.getLogger("pc")
pcs = set()

# Cargar los modelos YOLOv8 (.pt)
model_deteccion_rosto = YOLO("./Modelos/fashion_model.pt")
model_clasificacion_rosto = YOLO("./Modelos/facesclassification_model.pt")
model_ojos = YOLO("./Modelos/eyesclassification_model.pt")
model_tono_piel = YOLO("./Modelos/skinClas_model.pt")
#nuevos modelos
model_cejas_clasificacion = YOLO("./Modelos/cejasclasificacion_model.pt")
model_labios_clasificacion = YOLO("./Modelos/labiosclasificacion_model.pt")

# Variable global para almacenar las características detectadas
global_features = {}


class VideoTransformTrack(VideoStreamTrack):
    """
    Un track de video que transforma cada fotograma aplicándole YOLO.
    """

    def __init__(self, track):
        super().__init__()  # Inicializa la clase padre
        self.track = track
        self.features = {}  # Diccionario para almacenar las características detectadas

    async def recv(self):
        frame = await self.track.recv()
        img = frame.to_ndarray(format="bgr24")  # Convertir el fotograma a imagen BGR

        # Procesar la imagen con YOLO (detección de rostro)
        results_deteccion_rosto = model_deteccion_rosto(img)
        rostros = results_deteccion_rosto[0].boxes
        annotated_img = img.copy()

        # Procesar cada rostro detectado
        for rostro in rostros:
            x1, y1, x2, y2 = map(int, rostro.xyxy[0])  # Coordenadas del rostro
            cv2.rectangle(annotated_img, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Dibujar cuadro

            # Cortar la región del rostro
            rostro_cortado = img[y1:y2, x1:x2]

            # Clasificación de tipo de rostro
            results_clasificacion_rosto = model_clasificacion_rosto(rostro_cortado)
            tipo_rostro = results_clasificacion_rosto[0].names[results_clasificacion_rosto[0].probs.top1]

            # Clasificación de tono de piel
            results_tono_piel = model_tono_piel(rostro_cortado)
            tono_piel = results_tono_piel[0].names[results_tono_piel[0].probs.top1]

            # Clasificación de ojos
            results_ojos = model_ojos(rostro_cortado)
            tipo_ojos = results_ojos[0].names[results_ojos[0].probs.top1]
            
            # Clasificación de cejas
            results_cejas = model_cejas_clasificacion(rostro_cortado)
            tipo_cejas = results_cejas[0].names[results_cejas[0].probs.top1]

            # Clasificación de labios
            results_labios = model_labios_clasificacion(rostro_cortado)
            tipo_labios = results_labios[0].names[results_labios[0].probs.top1]
            


            # Dibujar etiquetas en la imagen
            cv2.putText(annotated_img, f"Rostro: {tipo_rostro}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            cv2.putText(annotated_img, f"Tono: {tono_piel}", (x1, y2 + 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            cv2.putText(annotated_img, f"Ojos: {tipo_ojos}", (x1, y2 + 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)

            cv2.putText(annotated_img, f"Cejas: {tipo_cejas}", (x1, y2 + 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 165, 0), 2)
            cv2.putText(annotated_img, f"Labios: {tipo_labios}", (x1, y2 + 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 20, 147), 2)
            
            # Guardar en el JSON
            self.features["rostro"] = tipo_rostro
            self.features["tono_piel"] = tono_piel
            self.features["ojos"] = tipo_ojos

            self.features["cejas"] = tipo_cejas
            self.features["labios"] = tipo_labios

        # Actualizar las características globales
        global global_features
        global_features = self.features.copy()  # Actualiza las características globales

        # Crear un nuevo frame con la imagen anotada
        new_frame = frame.from_ndarray(annotated_img, format="bgr24")
        new_frame.pts = frame.pts
        new_frame.time_base = frame.time_base

        # Imprimir el JSON generado
        print(f"Características detectadas: {json.dumps(self.features)}")

        return new_frame


# Función para enviar las características al servidor
def send_json_to_client2(features):
    """
    Función para enviar el JSON al client2 cuando la conexión ICE se cierra.
    """
    if features:
        print(f"Datos a enviar a client2: {json.dumps(features)}")  # Imprime los datos que se enviarán
        try:
            # Convertir las características a JSON antes de enviarlas
            response = requests.post('http://192.168.1.88:5000/receive_features', json=features)
            print(f"Respuesta del servidor client2: {response.status_code}")  # Ver el código de estado
            if response.status_code == 200:
                print("✅ JSON enviado correctamente a client2")
            else:
                print(f"⚠️ Error al enviar JSON: {response.text}")
        except Exception as e:
            print(f"❌ Error al conectar con client2: {str(e)}")


async def offer(request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("iceconnectionstatechange")
    async def on_iceconnectionstatechange():
        print("ICE connection state is %s" % pc.iceConnectionState)

        if pc.iceConnectionState == "closed":
            print("🔴 ICE closed detected, attempting to send JSON.")

            # Usar la variable global para las características
            if global_features:
                print(f"Características detectadas: {json.dumps(global_features)}")  # Aquí se imprime el JSON
            else:
                print("⚠️ No se detectaron características.")

            await asyncio.sleep(1)  # Retraso para asegurar que todo esté cerrado

            # Enviar el JSON si existen características
            if global_features:  # Asegurarse de que las características existen
                send_json_to_client2(global_features)
            else:
                print("⚠️ No features found to send.")

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
