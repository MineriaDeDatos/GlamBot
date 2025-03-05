import shutil
import random
import yaml
from pathlib import Path

# Ruta base del dataset
dataset_folder = Path("/root/Downloads/lip_model/Lip_Makeup_Detection2-1")

# Carpeta temporal "all" donde se almacenarán todas las imágenes y etiquetas antes de separar
all_images_folder = dataset_folder / "all" / "images"
all_labels_folder = dataset_folder / "all" / "labels"
all_unlabeled_images_folder = dataset_folder / "all" / "unlabeled_images"  # Carpeta para imágenes sin etiqueta

# Carpetas de destino para train, valid y test
train_images_folder = dataset_folder / "train" / "images"
train_labels_folder = dataset_folder / "train" / "labels"
valid_images_folder = dataset_folder / "valid" / "images"
valid_labels_folder = dataset_folder / "valid" / "labels"
test_images_folder = dataset_folder / "test" / "images"
test_labels_folder = dataset_folder / "test" / "labels"

# Crear todas las carpetas necesarias
for folder in [all_images_folder, all_labels_folder, all_unlabeled_images_folder,
               train_images_folder, train_labels_folder,
               valid_images_folder, valid_labels_folder,
               test_images_folder, test_labels_folder]:
    folder.mkdir(parents=True, exist_ok=True)

# Identificar todas las carpetas que contienen imágenes y etiquetas dentro de dataset_folder
image_folders = list(dataset_folder.glob("*/images"))  # Buscar todas las carpetas de imágenes
label_folders = [Path(str(folder).replace("/images", "/labels")) for folder in image_folders]  # Asumir estructura paralela de etiquetas

# Mover todas las imágenes y etiquetas a "all/" y las imágenes no etiquetadas a su carpeta respectiva
for img_folder, lbl_folder in zip(image_folders, label_folders):
    for img in img_folder.glob("*.jpg"):  # Buscar imágenes
        label = lbl_folder / (img.stem + ".txt")  # Buscar etiqueta correspondiente
        if label.exists():
            with open(label, 'r') as f:
                label_content = f.read().strip()
            if label_content:  # Si el archivo de etiqueta no está vacío
                shutil.move(str(img), str(all_images_folder / img.name))
                shutil.move(str(label), str(all_labels_folder / label.name))
            else:  # Si el archivo de etiqueta está vacío
                shutil.move(str(img), str(all_unlabeled_images_folder / img.name))
        else:
            shutil.move(str(img), str(all_unlabeled_images_folder / img.name))  # Si no hay archivo de etiqueta

# Obtener lista de imágenes con etiqueta y sin etiqueta en "all/"
labeled_images = list(all_images_folder.glob("*.jpg"))
unlabeled_images = list(all_unlabeled_images_folder.glob("*.jpg"))

# Mezclar aleatoriamente
random.shuffle(labeled_images)
random.shuffle(unlabeled_images)

# Calcular distribución (70% train, 15% valid, 15% test)
total_labeled = len(labeled_images)
total_unlabeled = len(unlabeled_images)

num_labeled_train = int(total_labeled * 0.7)
num_labeled_valid = int(total_labeled * 0.15)
num_labeled_test = total_labeled - num_labeled_train - num_labeled_valid  # Asegurar 100%

num_unlabeled_train = int(total_unlabeled * 0.7)
num_unlabeled_valid = int(total_unlabeled * 0.15)
num_unlabeled_test = total_unlabeled - num_unlabeled_train - num_unlabeled_valid  # Asegurar 100%

# Mover imágenes con etiqueta a train, valid y test
for img in labeled_images[:num_labeled_train]:  # Train (70% para imágenes etiquetadas)
    label = all_labels_folder / (img.stem + ".txt")
    shutil.move(str(img), str(train_images_folder / img.name))
    shutil.move(str(label), str(train_labels_folder / label.name))

for img in labeled_images[num_labeled_train:num_labeled_train + num_labeled_valid]:  # Valid (15% para imágenes etiquetadas)
    label = all_labels_folder / (img.stem + ".txt")
    shutil.move(str(img), str(valid_images_folder / img.name))
    shutil.move(str(label), str(valid_labels_folder / label.name))

for img in labeled_images[num_labeled_train + num_labeled_valid:]:  # Test (15% para imágenes etiquetadas)
    label = all_labels_folder / (img.stem + ".txt")
    shutil.move(str(img), str(test_images_folder / img.name))
    shutil.move(str(label), str(test_labels_folder / label.name))

# Mover imágenes sin etiqueta a train, valid y test
for img in unlabeled_images[:num_unlabeled_train]:  # Train (70% para imágenes sin etiquetar)
    shutil.move(str(img), str(train_images_folder / img.name))

for img in unlabeled_images[num_unlabeled_train:num_unlabeled_train + num_unlabeled_valid]:  # Valid (15% para imágenes sin etiquetar)
    shutil.move(str(img), str(valid_images_folder / img.name))

for img in unlabeled_images[num_unlabeled_train + num_unlabeled_valid:]:  # Test (15% para imágenes sin etiquetar)
    shutil.move(str(img), str(test_images_folder / img.name))

# Eliminar la carpeta "all/"
shutil.rmtree(dataset_folder / "all")

# Actualizar el archivo data.yaml
data_yaml = {
    "names": ["lips"],
    "nc": 1,
    "roboflow": {
        "license": "Private",
        "project": "lip_makeup_detection2",
        "url": "https://app.roboflow.com/ca-ioqio/lip_makeup_detection2/1",
        "version": 1,
        "workspace": "ca-ioqio"
    },
    "train": "../train/images",
    "val": "../valid/images",
    "test": "../test/images"
}

yaml_path = dataset_folder / "data.yaml"
with open(yaml_path, "w") as f:
    yaml.dump(data_yaml, f, default_flow_style=False)

# Imprimir resumen
print(f"Dataset reorganizado: Labeled Train={num_labeled_train}, Valid={num_labeled_valid}, Test={num_labeled_test}")
print(f"Dataset reorganizado: Unlabeled Train={num_unlabeled_train}, Valid={num_unlabeled_valid}, Test={num_unlabeled_test}")
print(f"Archivo data.yaml actualizado en {yaml_path}")
