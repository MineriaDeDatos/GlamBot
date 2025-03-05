import base64
import cv2
import numpy as np
import uuid
import json
from fastapi import FastAPI, WebSocket
from ultralytics import YOLO

app = FastAPI()

# Carga el modelo YOLOv8n entrenado (se asume que fue entrenado con YOLOv8n y guardado en 'best.pt')
model = YOLO("C:/Users/ASUS/Desktop/Backend/Modelos/fashion_model.pt")


@app.websocket("/ws/detect")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        # Recibe el frame en formato base64 desde la app Flutter
        data = await websocket.receive_text()
        try:
            # Decodifica la imagen base64 a un array de numpy
            img_data = base64.b64decode(data)
            nparr = np.frombuffer(img_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        except Exception as e:
            await websocket.send_text(json.dumps({"error": "Error al procesar la imagen", "detalle": str(e)}))
            continue

        # Realiza la detección con el modelo YOLOv8
        results = model(frame)[0]  # Procesa la imagen y obtiene el primer resultado
        # Extrae las coordenadas, confianza y clase de cada detección
        boxes = results.boxes.xyxy.cpu().numpy()  # Bounding boxes en formato [x1, y1, x2, y2]
        confs = results.boxes.conf.cpu().numpy()  # Confianza de cada detección
        classes = results.boxes.cls.cpu().numpy()  # IDs de clase

        detections = []
        for i in range(len(boxes)):
            x1, y1, x2, y2 = boxes[i]
            confidence = float(confs[i])
            class_id = int(classes[i])
            # Calcula el centro, ancho y alto del bounding box
            x_center = (x1 + x2) / 2
            y_center = (y1 + y2) / 2
            width = x2 - x1
            height = y2 - y1
            detections.append({
                "x": x_center,
                "y": y_center,
                "width": width,
                "height": height,
                "confidence": confidence,
                "class": "rostro",  # Se asume que el modelo detecta únicamente rostros
                "class_id": class_id,
                "detection_id": str(uuid.uuid4())
            })
            # Dibuja el bounding box en el frame para la visualización
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

        # Codifica el frame anotado nuevamente a base64
        _, buffer = cv2.imencode('.jpg', frame)
        annotated_img = base64.b64encode(buffer).decode('utf-8')

        # Envía la respuesta en formato JSON con las detecciones y la imagen anotada
        response = {"detections": detections, "frame": annotated_img}
        await websocket.send_text(json.dumps(response))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
