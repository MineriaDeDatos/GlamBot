from ultralytics import YOLO

# Cargar YOLO con pesos preentrenados
modelo = YOLO("yolov8n.pt")

# Entrenar en dataset personalizado
modelo.train(data="../../datasets/faces/data.yaml", epochs=50, imgsz=640)

# Guardar el modelo entrenado
modelo.export(format="torchscript", path="yolo_face.pt")

print("✅ Entrenamiento de YOLO completado. Modelo guardado en 'yolo_face.pt'")
