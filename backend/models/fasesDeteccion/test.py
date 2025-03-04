import cv2
import numpy as np
from ultralytics import YOLO

# Cargar los modelos YOLOv8 (.pt) para cada tarea
model_deteccion_rosto = YOLO(
    "C:/Users/ASUS/Desktop/MineriaPF/GlamBot/backend/models/fasesDeteccion/Modelos/fashion_model.pt")
model_clasificacion_rosto = YOLO(
    "C:/Users/ASUS/Desktop/MineriaPF/GlamBot/backend/models/fasesDeteccion/Modelos/facesclassification_model.pt")
model_labios = YOLO(
    "C:/Users/ASUS/Desktop/MineriaPF/GlamBot/backend/models/fasesDeteccion/Modelos/lipmakeupdetection21_model.pt")
model_ojos = YOLO(
    "C:/Users/ASUS/Desktop/MineriaPF/GlamBot/backend/models/fasesDeteccion/Modelos/eyesclassification_model.pt")
model_tono_piel = YOLO(
    "C:/Users/ASUS/Desktop/MineriaPF/GlamBot/backend/models/fasesDeteccion/Modelos/skinClas_model.pt")

# Función para generar el prompt para StyleGAN
def generar_prompt(labels):
    """
    Combina las etiquetas de los rasgos faciales con el formato adecuado para StyleGAN.
    """
    prompt = f"Maquillaje: labios, piel {labels.get('piel', 'sin cambios')}, "
    prompt += f"ojos {labels.get('ojos', 'sin cambios')}, "
    prompt += f"rostro {labels.get('rostro', 'sin cambios')}"
    return prompt

# Captura de la cámara de la laptop
cap = cv2.VideoCapture(0)  # 0 es el índice de la cámara integrada

while True:
    ret, frame = cap.read()
    if not ret:
        break

    img = frame  # Convertir el fotograma a una imagen numpy array

    # Detección de rostros
    results_deteccion_rosto = model_deteccion_rosto(img)
    rostras = results_deteccion_rosto[0].boxes  # Obtener las cajas de detección

    annotated_img = img.copy()  # Imagen anotada
    labels = {}  # Aquí almacenaremos las etiquetas para el prompt

    for rostro in rostras:
        x1, y1, x2, y2 = map(int, rostro.xyxy[0])  # Coordenadas del rostro
        cv2.rectangle(annotated_img, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Dibujar caja

        # Extraer la región del rostro
        rostro_cortado = img[y1:y2, x1:x2]

        # Clasificación del tipo de rostro
        results_clasificacion_rosto = model_clasificacion_rosto(rostro_cortado)
        tipo_rostro = results_clasificacion_rosto[0].names[results_clasificacion_rosto[0].probs.top1]
        probabilidad_rostro = float(results_clasificacion_rosto[0].probs.top1conf)

        # Clasificación del tono de piel
        results_tono_piel = model_tono_piel(rostro_cortado)
        tono_piel = results_tono_piel[0].names[results_tono_piel[0].probs.top1]
        probabilidad_tono_piel = float(results_tono_piel[0].probs.top1conf)

        # Clasificación de los ojos
        results_ojos = model_ojos(rostro_cortado)
        tipo_ojos = results_ojos[0].names[results_ojos[0].probs.top1]
        probabilidad_ojos = float(results_ojos[0].probs.top1conf)

        # Guardar las etiquetas generadas
        labels['rostro'] = tipo_rostro
        labels['probabilidad_rostro'] = probabilidad_rostro
        labels['piel'] = tono_piel
        labels['probabilidad_piel'] = probabilidad_tono_piel
        labels['ojos'] = tipo_ojos
        labels['probabilidad_ojos'] = probabilidad_ojos

        # Mostrar los resultados en la imagen
        cv2.putText(annotated_img, f"{tipo_rostro} ({probabilidad_rostro * 100:.2f}%)",
                    (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
        cv2.putText(annotated_img, f"Tono: {tono_piel} ({probabilidad_tono_piel * 100:.2f}%)",
                    (x1, y2 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)

    # Procesar labios (si detecta algo relacionado con labios)
    results_labios = model_labios(img)
    annotated_img_labios = results_labios[0].plot()

    # Procesar sombras (si detecta algo relacionado con sombras)
    results_sombra = model_labios(img)  # Aquí podrías tener otro modelo para detectar sombras.
    annotated_img_sombra = results_sombra[0].plot()

    # Combinar todas las anotaciones
    combined_img = cv2.addWeighted(annotated_img, 0.33, annotated_img_labios, 0.33, 0)

    # Generar el prompt para StyleGAN con las etiquetas
    prompt = generar_prompt(labels)
    print("Generando prompt:", prompt)  # Esto es solo para ver el resultado

    # Mostrar imagen con resultados
    cv2.imshow('Video', combined_img)

    # Presiona 'q' para salir
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar recursos
cap.release()
cv2.destroyAllWindows()
