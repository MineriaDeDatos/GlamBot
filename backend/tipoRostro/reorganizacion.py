import os
import shutil
import random
from pathlib import Path

# Definir la ruta base del dataset
dataset_folder = Path("/root/Downloads/tipoRostro/FacesClassification-21")

# Rutas de carpetas principales
all_folder = dataset_folder / "all"
train_folder = dataset_folder / "train"
valid_folder = dataset_folder / "valid"
test_folder = dataset_folder / "test"

# Crear las carpetas si no existen
for folder in [all_folder, train_folder, valid_folder, test_folder]:
    folder.mkdir(parents=True, exist_ok=True)

# Obtener todas las clases dentro de las carpetas train, valid y test
clases = [d.name for d in (train_folder).iterdir() if d.is_dir()]

# Paso 1: Mover todas las imágenes a la carpeta "all/"
for clase in clases:
    try:
        clase_train_path = train_folder / clase
        clase_all_path = all_folder / clase

        # Crear la carpeta "all/clase" si no existe
        clase_all_path.mkdir(parents=True, exist_ok=True)

        # Mover imágenes de "train/clase" a "all/clase"
        for img in clase_train_path.glob("*.*"):
            shutil.move(str(img), str(clase_all_path / img.name))

    except Exception as e:
        print(f"Error al mover imágenes de la clase '{clase}': {e}")

# Paso 2: Reorganizar en train (70%), valid (15%), test (15%)
for clase in clases:
    try:
        clase_all_path = all_folder / clase
        clase_train_path = train_folder / clase
        clase_valid_path = valid_folder / clase
        clase_test_path = test_folder / clase

        # Crear las carpetas de destino si no existen
        for folder in [clase_train_path, clase_valid_path, clase_test_path]:
            folder.mkdir(parents=True, exist_ok=True)

        # Obtener todas las imágenes de la clase
        imagenes = list(clase_all_path.glob("*.*"))  # Tomar todos los archivos en la carpeta

        # Mezclar aleatoriamente las imágenes
        random.shuffle(imagenes)

        # Calcular la distribución de imágenes (70% train, 15% valid, 15% test)
        total = len(imagenes)
        num_train = int(total * 0.7)   # 70% para entrenamiento
        num_valid = int(total * 0.15)  # 15% para validación
        num_test = total - num_train - num_valid  # 15% restante para test

        # Mover imágenes a train, valid y test
        for img in imagenes[:num_train]:
            shutil.move(str(img), str(clase_train_path / img.name))
        for img in imagenes[num_train:num_train + num_valid]:
            shutil.move(str(img), str(clase_valid_path / img.name))
        for img in imagenes[num_train + num_valid:]:
            shutil.move(str(img), str(clase_test_path / img.name))

        # Eliminar la carpeta de "all/clase" después de usarla
        shutil.rmtree(clase_all_path)

        # Mostrar resultados
        print(f"Clase '{clase}': Train={num_train}, Valid={num_valid}, Test={num_test}, Total={total}")

    except Exception as e:
        print(f"Error al reorganizar las imágenes de la clase '{clase}': {e}")

# Paso 3: Eliminar la carpeta "all/" después de usarla
try:
    shutil.rmtree(all_folder)
    print("Reorganización completada con éxito. Se eliminó la carpeta 'all/'.")
except Exception as e:
    print(f"Error al eliminar la carpeta 'all/': {e}")
