import os
import torch
import yaml
from ultralytics import YOLO
from pathlib import Path
import re  # Para manejar expresiones regulares

# Limitar CUDA a la instancia 0 para evitar problemas con MIG (si aplica)
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

try:
    # Nueva ruta del dataset para el modelo de clasificación de ojos
    dataset_folder = Path("/root/Desktop/NewModels/EyeClassification/Ojos_almendrados-3")

    # Cargar el modelo YOLO de clasificación
    model = YOLO("yolov8n-cls.pt")

    # Configurar el dispositivo: usar GPU si está disponible
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # Definir la carpeta de checkpoints y asegurarse de que exista
    checkpoint_dir = dataset_folder / "eyesclassification_checkpoints"
    checkpoint_dir.mkdir(exist_ok=True)

    # Obtener el número del último experimento
    existing_experiments = [
        d.name for d in checkpoint_dir.iterdir()
        if d.is_dir() and d.name.startswith("eyesclassification_cls")
    ]

    # Extraer los números de los experimentos existentes
    experiment_numbers = [
        int(re.search(r"eyesclassification_cls(\d+)$", exp).group(1))
        for exp in existing_experiments if re.search(r"eyesclassification_cls(\d+)$", exp)
    ]

    # Determinar el número del siguiente experimento
    experiment_number = max(experiment_numbers, default=0) + 1
    experiment_name = f"eyesclassification_cls{experiment_number}"
    # Entrenar el modelo de clasificación
    results = model.train(
        task='classify',  # Especifica la tarea de clasificación
        data=str(dataset_folder),  # Carpeta raíz con train/, valid/ y test/
        epochs=200,
        imgsz=640,
        #batch=64,
        project=str(checkpoint_dir),
        name=experiment_name,
        single_cls=False,  # No forzar a una sola clase
        rect=True,  # Mantener relaciones de aspecto
        cache=False,
        workers=8
    )

    # Verificar si el entrenamiento generó el mejor modelo
    model_path = dataset_folder / "eyesclassification_model.pt"
    best_model_checkpoint = checkpoint_dir / experiment_name / "weights" / "best.pt"

    if best_model_checkpoint.exists():
        best_model_checkpoint.rename(model_path)
        print(f"Modelo guardado en: {model_path}")
    else:
        print(f"El archivo 'best.pt' no se encontró en {best_model_checkpoint}. Verifica el entrenamiento.")

except Exception as e:
    print(f"Ocurrió un error: {e}")
