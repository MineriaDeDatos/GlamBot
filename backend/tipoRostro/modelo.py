import os
import torch
from ultralytics import YOLO
from pathlib import Path
import re  # Para manejar expresiones regulares

# Limitar CUDA a la instancia 0 para evitar problemas con MIG (si aplica)
os.environ["CUDA_VISIBLE_DEVICES"] = "0,1,2,3"

try:
    # Nueva ruta del dataset
    dataset_folder = Path("/root/Downloads/tipoRostro/FacesClassification-20")

    # Verificar que el directorio del dataset exista
    if not dataset_folder.exists():
        raise FileNotFoundError(f"La carpeta del dataset no existe: {dataset_folder}")

    # Cargar el modelo YOLO de clasificación
    model = YOLO("yolov8n-cls.pt")

    # Configurar el dispositivo: usar GPU si está disponible
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # Definir la carpeta de checkpoints y asegurarse de que exista
    checkpoint_dir = dataset_folder / "facesclassification_checkpoints"
    checkpoint_dir.mkdir(exist_ok=True)

    # Obtener el número del último experimento
    existing_experiments = [
        d.name for d in checkpoint_dir.iterdir()
        if d.is_dir() and d.name.startswith("facesclassification_cls")
    ]

    # Extraer los números de los experimentos existentes
    experiment_numbers = [
        int(re.search(r"facesclassification_cls(\d+)$", exp).group(1))
        for exp in existing_experiments if re.search(r"facesclassification_cls(\d+)$", exp)
    ]

    # Determinar el número del siguiente experimento
    experiment_number = max(experiment_numbers, default=0) + 1
    experiment_name = f"facesclassification_cls{experiment_number}"

    # Entrenar el modelo de clasificación con parámetros optimizados
    results = model.train(
        task='classify',
        data=str(dataset_folder),
        epochs=100,
        imgsz=640,
        #batch=64,
        optimizer='SGD',
        lr0=0.01,
        lrf=0.1,
        momentum=0.9,
        weight_decay=0.0005,
        mixup=0.2,
        dropout=0.1,
        label_smoothing=0.1,
        cos_lr=True,
        save=True,
        project=str(checkpoint_dir),  #Guardar en la carpeta correcta
        name=experiment_name,  #Organiza los experimentos correctamente
        device=[0, 1, 2, 3]
    )

    # Verificar si el entrenamiento generó el mejor modelo
    model_path = dataset_folder / "facesclassification_model.pt"
    best_model_checkpoint = checkpoint_dir / experiment_name / "weights" / "best.pt"

    if best_model_checkpoint.exists():
        best_model_checkpoint.rename(model_path)
        print(f" Modelo guardado en: {model_path}")
    else:
        print(f" El archivo 'best.pt' no se encontró en {best_model_checkpoint}. Verifica el entrenamiento.")

except Exception as e:
    print(f"L Ocurrió un error: {e}")