import os
import pandas as pd
import shutil

# Rutas del dataset CelebA
celeba_path = "backend/models/lip_model/celebA/"
images_path = os.path.join(celeba_path, "img_align_celeba")
labels_path = os.path.join(celeba_path, "list_attr_celeba.txt")

# Rutas de salida para imágenes filtradas
output_dir = "backend/models/lip_model/dataset/"
lipstick_dir = os.path.join(output_dir, "labios_maquillados")
no_lipstick_dir = os.path.join(output_dir, "labios_no_maquillados")

# Crear carpetas de salida si no existen
os.makedirs(lipstick_dir, exist_ok=True)
os.makedirs(no_lipstick_dir, exist_ok=True)

# Cargar etiquetas
df = pd.read_csv(labels_path, sep="\s+", header=1)

# Filtrar imágenes y moverlas
for _, row in df.iterrows():
    img_name = row["image_id"]
    label = row["Wearing_Lipstick"]  # 1 = labios maquillados, -1 = sin maquillaje

    src_path = os.path.join(images_path, img_name)
    dst_path = os.path.join(lipstick_dir if label == 1 else no_lipstick_dir, img_name)

    if os.path.exists(src_path):
        shutil.move(src_path, dst_path)

print("✅ Filtrado completado. Imágenes clasificadas en:")
print(f"  📂 {lipstick_dir} → Labios maquillados")
print(f"  📂 {no_lipstick_dir} → Sin maquillaje")
