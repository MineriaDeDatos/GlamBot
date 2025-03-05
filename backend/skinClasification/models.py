import os
import torch
import yaml
from ultralytics import YOLO
from pathlib import Path
import re  # Para manejar expresiones regulares

# Limitar CUDA a la instancia 0 para evitar problemas con MIG (si aplica)
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

try:
    # Directorio principal del dataset
    dataset_folder = Path("/root/Desktop/NewModels/skinClasification/-skin_tone_classification-15")

    # Ruta del archivo YAML del dataset (si existiera)
    yaml_path = dataset_folder / "data.yaml"

    if yaml_path.exists():
        # Cargar el contenido del YAML
        with open(yaml_path, "r") as f:
            data_yaml = yaml.safe_load(f)

        # Imprimir el valor actual de "data" para depuración
        print("Valor actual de 'data' en YAML:", data_yaml.get("data"))

        # Verificar y actualizar la clave "data" para que apunte al directorio raíz del dataset
        if data_yaml.get("data") != str(dataset_folder):
            print("Actualizando 'data' en YAML a:", str(dataset_folder))
            data_yaml["data"] = str(dataset_folder)
            with open(yaml_path, "w") as f:
                yaml.safe_dump(data_yaml, f)

    # Cargar el modelo YOLO de clasificación
    model = YOLO("yolov8n-cls.pt")

    # Configurar el dispositivo: usar GPU si está disponible
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # Definir la carpeta de checkpoints y asegurarse de que exista
    checkpoint_dir = dataset_folder / "checkpoints"
    checkpoint_dir.mkdir(exist_ok=True)

    # Obtener el número del último experimento
    existing_experiments = [
        d.name for d in checkpoint_dir.iterdir()
        if d.is_dir() and d.name.startswith("skinClas_cls")
    ]

    # Extraer los números de los experimentos existentes
    experiment_numbers = [
        int(re.search(r"skinClas_cls(\d+)$", exp).group(1))
        for exp in existing_experiments if re.search(r"skinClas_cls(\d+)$", exp)
    ]

    # Determinar el número del siguiente experimento
    experiment_number = max(experiment_numbers, default=0) + 1
    experiment_name = f"skinClas_cls{experiment_number}"

    # Entrenar el modelo de clasificación con mejores hiperparámetros
    results = model.train(
        task='classify',
        data=str(dataset_folder),  # Carpeta raíz con train/, valid/ y test/
        epochs=50,  # Más épocas para mejor precisión
        imgsz=640,  # Tamaño de imagen más grande
        batch=32,  # Optimización de batch según memoria GPU
        project=str(checkpoint_dir),
        name=experiment_name,
        single_cls=False,  # No forzar a una sola clase
        rect=True,  # Mantener relaciones de aspecto
        cache=True,  # Acelerar el entrenamiento
        workers=8,  # Usar múltiples núcleos de CPU
        optimizer='Adam',  # Usar Adam para mejor convergencia
        lr0=0.001,  # Tasa de aprendizaje inicial
        augment=True  # Aumentación de datos para mejorar generalización
    )

    # Verificar si el entrenamiento generó el mejor modelo
    model_path = dataset_folder / "skinClas_model.pt"
    best_model_checkpoint = checkpoint_dir / experiment_name / "weights" / "best.pt"

    if best_model_checkpoint.exists():
        best_model_checkpoint.rename(model_path)
        print(f"Modelo guardado en: {model_path}")
    else:
        print(f"El archivo 'best.pt' no se encontró en {best_model_checkpoint}. Verifica el entrenamiento.")

except Exception as e:
    print(f"Ocurrió un error: {e}")
