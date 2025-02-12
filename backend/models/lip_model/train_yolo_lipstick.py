from ultralytics import YOLO

# Cargar modelo preentrenado de YOLOv8
model = YOLO("yolov8n.pt")

# Entrenar el modelo
model.train(
    data="backend/models/lip_model/config.yaml",
    epochs=50,
    batch=16,
    imgsz=640
)

print("✅ Entrenamiento completado. Modelo guardado en 'runs/train/'.")
