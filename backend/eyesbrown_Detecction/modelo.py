import os
import torch
import yaml
from ultralytics import YOLO
from pathlib import Path
import re
import shutil

# Limitar CUDA a la primera GPU disponible
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

def load_model(model_path, device):
    """Carga el modelo YOLO y lo asigna al dispositivo especificado."""
    try:
        model = YOLO(model_path)
        model.to(device)
        return model
    except Exception as e:
        print(f"Error al cargar el modelo: {e}")
        return None

def get_device():
    """Devuelve el dispositivo disponible (GPU o CPU)."""
    return torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

def clear_gpu_memory():
    """Libera memoria en la GPU si está disponible."""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()

def determine_experiment_name(checkpoint_dir, dataset_name):
    """Determina el nombre para el nuevo experimento."""
    try:
        existing_experiments = [d.name for d in checkpoint_dir.iterdir() if d.is_dir() and d.name.startswith(dataset_name)]
        experiment_numbers = [
            int(re.search(fr"{dataset_name}(\d+)$", exp).group(1)) for exp in existing_experiments if re.search(fr"{dataset_name}(\d+)$", exp)
        ]
        experiment_number = max(experiment_numbers, default=0) + 1
        return f"{dataset_name}{experiment_number}"
    except Exception as e:
        print(f"Error al determinar el nombre del experimento: {e}")
        return None

def train_model(model, yaml_path, checkpoint_dir, experiment_name):
    """Entrena el modelo con los parámetros especificados."""
    try:
        return model.train(
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
            fliplr=0.5
        )
    except Exception as e:
        print(f"Error al entrenar el modelo: {e}")
        return None

def save_trained_model(checkpoint_dir, experiment_name, dataset_name, base_path):
    """Guarda el modelo entrenado si se encuentra el mejor checkpoint."""
    try:
        model_path = base_path / f"{dataset_name}_model.pt"
        best_model_checkpoint = checkpoint_dir / experiment_name / "weights" / "best.pt"

        if best_model_checkpoint.exists():
            shutil.move(str(best_model_checkpoint), str(model_path))
            print(f"Modelo guardado en: {model_path}")
        else:
            print(f"No se encontró 'best.pt' en {best_model_checkpoint}. Verifica el entrenamiento.")
    except Exception as e:
        print(f"Error al guardar el modelo: {e}")

def main():
    try:
        # Definir la ruta base del dataset
        base_path = Path("/root/Downloads/eyesbrown_model/eyesbrown_model-10")
        yaml_path = base_path / "data.yaml"

        # Configuración del dispositivo
        device = get_device()
        print(f"Usando dispositivo: {device}")

        # Cargar el modelo YOLO
        model = load_model("yolov8n.pt", device)
        if not model:
            raise Exception("No se pudo cargar el modelo.")

        # Liberar memoria antes de entrenar
        clear_gpu_memory()

        # Definir la carpeta de checkpoints
        checkpoint_dir = base_path / "checkpoints"
        checkpoint_dir.mkdir(parents=True, exist_ok=True)

        # Determinar el nombre del experimento
        dataset_name = base_path.name.lower().replace("-", "").replace("_", "")
        experiment_name = determine_experiment_name(checkpoint_dir, dataset_name)
        if not experiment_name:
            raise Exception("No se pudo determinar el nombre del experimento.")

        # Entrenar el modelo
        results = train_model(model, yaml_path, checkpoint_dir, experiment_name)
        if not results:
            raise Exception("Error al entrenar el modelo.")

        # Guardar el modelo entrenado
        save_trained_model(checkpoint_dir, experiment_name, dataset_name, base_path)

    except Exception as e:
        print(f"Ocurrió un error: {e}")

if __name__ == "__main__":
    main()
