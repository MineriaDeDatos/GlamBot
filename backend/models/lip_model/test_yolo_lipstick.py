from ultralytics import YOLO
import cv2

# Cargar modelo entrenado
model = YOLO("runs/train/exp/weights/best.pt")  # Ajusta la ruta si es necesario

# Capturar video en tiempo real
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Realizar detección
    results = model(frame)

    # Mostrar resultados
    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = box.conf[0]
            label = "Labios maquillados" if conf > 0.5 else "No maquillados"
            color = (0, 255, 0) if conf > 0.5 else (0, 0, 255)

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"{label} ({conf:.2f})", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    cv2.imshow("Detección de Labios Maquillados", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
