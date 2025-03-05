import os
import torch
import yaml
from ultralytics import YOLO
from pathlib import Path
import re
import shutil

# Limitar CUDA a la primera GPU disponible
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

try:
    # Definir la ruta base del dataset
    base_path = Path("/root/Desktop/NewModels/FaceDetection/FaceDetection-5")
    yaml_path = base_path / "data.yaml"

    # Verificar si el archivo YAML existe
    if not yaml_path.exists():
        raise FileNotFoundError(f"El archivo {yaml_path} no existe.")

    # Leer el archivo YAML
    with open(yaml_path, "r") as f:
        data_yaml = yaml.safe_load(f)

    # =9 Asegurar que hay 2 clases (Rostro y Background)
    data_yaml["nc"] = 2
    data_yaml["names"] = ["Rostro", "Background"]

    # =9 Actualizar la clave "data" si es necesario
    if data_yaml.get("data") != str(base_path):
        data_yaml["data"] = str(base_path)
        with open(yaml_path, "w") as f:
            yaml.safe_dump(data_yaml, f)
        print(f"=Ä Archivo YAML actualizado: {yaml_path}")

    # =9 Crear etiquetas vacías para imágenes sin anotaciones
    labels_path = base_path / "train/labels"
    images_path = base_path / "train/images"
    labels_path.mkdir(parents=True, exist_ok=True)

    for image in os.listdir(images_path):
        label_file = labels_path / (image.replace(".jpg", ".txt"))
        if not label_file.exists():
            open(label_file, "w").close()  # Crear archivo vacío
    print(" Se crearon etiquetas vacías para imágenes de fondo.")

    # Cargar el modelo YOLO
    model = YOLO("yolov8n.pt")

    # Configuración del dispositivo (GPU si está disponible, de lo contrario CPU)
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model.to(device)
    print(f"¡ Usando dispositivo: {device}")

    # Limpiar caché de GPU para evitar problemas de memoria
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    # Definir la carpeta de checkpoints
    checkpoint_dir = base_path / "checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    # Determinar el número del próximo experimento
    dataset_name = base_path.name.lower().replace("-", "").replace("_", "")
    existing_experiments = [d.name for d in checkpoint_dir.iterdir() if d.is_dir() and d.name.startswith(dataset_name)]
    experiment_numbers = [int(re.search(fr"{dataset_name}(\d+)$", exp).group(1)) for exp in existing_experiments if re.search(fr"{dataset_name}(\d+)$", exp)]
    experiment_number = max(experiment_numbers, default=0) + 1
    experiment_name = f"{dataset_name}{experiment_number}"

    # Entrenar el modelo
    results = model.train(
        data=str(yaml_path),
        epochs=50,  # Más épocas para mejor aprendizaje
        imgsz=640,  # Tamaño de imagen
        #batch=16,  # Tamaño de batch
        project=str(checkpoint_dir),
        name=experiment_name,
        single_cls=False,  # No forzar a una sola clase
        rect=True,  # Mantener relaciones de aspecto
        cache=True,  # Cargar datos en memoria para mayor velocidad
        workers=8,  # Número de hilos
        optimizer='Adam',  # Usar Adam en lugar de SGD
        lr0=0.001,  # Learning rate inicial
        weight_decay=0.0005,  # Regularización L2
        warmup_epochs=3.0,  # Warmup
        warmup_momentum=0.8,  # Momentum en warmup
        warmup_bias_lr=0.1,  # Learning rate de bias en warmup
        hsv_h=0.015,  # Aumento de tono
        hsv_s=0.7,  # Aumento de saturación
        hsv_v=0.4,  # Aumento de brillo
        perspective=0.001,  # Corrección de perspectiva
        flipud=0.5,  # Flip vertical
        fliplr=0.5  # Flip horizontal
    )

    # Guardar el modelo entrenado
    model_path = base_path / f"{dataset_name}_model.pt"
    best_model_checkpoint = checkpoint_dir / experiment_name / "weights" / "best.pt"

    if best_model_checkpoint.exists():
        shutil.move(str(best_model_checkpoint), str(model_path))
        print(f" Modelo guardado en: {model_path}")
    else:
        print(f"  No se encontró 'best.pt' en {best_model_checkpoint}. Verifica el entrenamiento.")

except Exception as e:
    print(f"L Ocurrió un error: {e}")
