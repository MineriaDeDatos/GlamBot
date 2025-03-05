import os
import torch
import yaml
from ultralytics import YOLO
from pathlib import Path
import re
import shutil

# Limitar CUDA a la primera GPU disponible
# os.environ["CUDA_VISIBLE_DEVICES"] = "0"

try:
    # Definir la ruta base del dataset
    base_path = Path("/root/Desktop/NewModels/lip_model_segmentacion/Lip_Makeup_Segmentation-8")
    yaml_path = base_path / "data.yaml"

    # Cargar el modelo YOLO de segmentación
    model = YOLO("yolov8n-seg.pt")

    # Configuración del dispositivo (GPU si está disponible, de lo contrario CPU)
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model.to(device)
    print(f" Usando dispositivo: {device}")

    # Liberar memoria antes de entrenar
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()

    # Definir la carpeta de checkpoints
    checkpoint_dir = base_path / "checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    # Determinar el número del próximo experimento
    dataset_name = base_path.name.lower().replace("-", "").replace("_", "")
    existing_experiments = [d.name for d in checkpoint_dir.iterdir() if d.is_dir() and d.name.startswith(dataset_name)]
    experiment_numbers = [int(re.search(fr"{dataset_name}(\d+)$", exp).group(1)) for exp in existing_experiments if re.search(fr"{dataset_name}(\d+)$", exp)]
    experiment_number = max(experiment_numbers, default=0) + 1
    experiment_name = f"{dataset_name}{experiment_number}"

    # Entrenar el modelo con configuraciones optimizadas para segmentación
    results = model.train(
        data=str(yaml_path),
        epochs=50,
        imgsz=640,
        project=str(checkpoint_dir),
        name=experiment_name,
        single_cls=True,
        rect=False,  # Deshabilitado para evitar conflictos con shuffle
        workers=8,  # Reducir uso de CPU/RAM
        optimizer='Adam',
        lr0=0.001,
        weight_decay=0.0005,
        warmup_epochs=3.0,
        warmup_momentum=0.8,
        warmup_bias_lr=0.1,
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        perspective=0.001,
        flipud=0.5,
        fliplr=0.5,
        device=[0, 1, 2, 3]
    )

    # Guardar el modelo entrenado
    model_path = base_path / f"{dataset_name}_segmentation_model.pt"
    best_model_checkpoint = checkpoint_dir / experiment_name / "weights" / "best.pt"

    if best_model_checkpoint.exists():
        shutil.move(str(best_model_checkpoint), str(model_path))
        print(f" Modelo de segmentación guardado en: {model_path}")
    else:
        print(f"  No se encontró 'best.pt' en {best_model_checkpoint}. Verifica el entrenamiento.")

except Exception as e:
    print(f"L Ocurrió un error: {e}")
