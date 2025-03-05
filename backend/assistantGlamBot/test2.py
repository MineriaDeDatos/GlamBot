from diffusers import StableDiffusionXLControlNetPipeline, ControlNetModel
from diffusers.utils import load_image
import torch
import cv2
import numpy as np
from PIL import Image

# 📌 Cargar modelo base de Stable Diffusion XL
pipe = StableDiffusionXLControlNetPipeline.from_pretrained(
    "diffusers/stable-diffusion-xl-1.0-controlnet-canny",
    torch_dtype=torch.float16
).to("cuda")

# 📌 Cargar el modelo de ControlNet (Canny Edge)
controlnet = ControlNetModel.from_pretrained(
    "diffusers/controlnet-canny-sdxl-1.0",
    torch_dtype=torch.float16
).to("cuda")

pipe.controlnet = controlnet

# 📌 Cargar la imagen base
image_path = "imagen_base.jpg"
image = Image.open(image_path).convert("RGB")

# 📌 Aplicar filtro de detección de bordes (Canny Edge)
image_np = np.array(image)
image_gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
edges = cv2.Canny(image_gray, threshold1=100, threshold2=200)
edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)  # Convertir a 3 canales
edge_image = Image.fromarray(edges)

# 📌 Definir prompt para aplicar maquillaje
prompt = "A beautiful woman with red lipstick, soft eyeshadow, and glowing skin, realistic makeup"
negative_prompt = "low quality, blurry, unnatural"

# 📌 Generar imagen editada
edited_image = pipe(
    prompt=prompt,
    image=image,
    control_image=edge_image,
    negative_prompt=negative_prompt,
    num_inference_steps=30,
    guidance_scale=7.5,
    controlnet_conditioning_scale=1.0
).images[0]

# 📌 Guardar resultado
edited_image.save("imagen_maquillada.png")

# 📌 Opcional: Guardar la imagen con contornos detectados
edge_image.save("contornos_detectados.png")
