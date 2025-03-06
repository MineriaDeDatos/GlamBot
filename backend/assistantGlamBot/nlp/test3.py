from diffusers import StableDiffusionXLImg2ImgPipeline
import torch
from PIL import Image

# Cargar el pipeline de img2img
pipe = StableDiffusionXLImg2ImgPipeline.from_single_file(
    "https://huggingface.co/martyn/sdxl-turbo-mario-merge-top-rated/blob/main/topRatedTurboxlLCM_v10.safetensors"
)
pipe.to("cuda")

# Cargar la imagen base (asegúrate de que exista)
init_image = Image.open("../pablito.jpg").convert("RGB").resize((1024, 1024))

# Generar imagen basada en la imagen base y el nuevo prompt
prompt = "Maquillaje para boda con tonos dorados"
negative_prompt = "nsfw"
strength = 0.5  # Define cuánto se debe cambiar la imagen (0.0 = igual, 1.0 = muy diferente)
guidance_scale = 7.5
num_inference_steps = 50

image = pipe(
    prompt=prompt,
    negative_prompt=negative_prompt,
    image=init_image,
    strength=strength,
    guidance_scale=guidance_scale,
    num_inference_steps=num_inference_steps
).images[0]

# Guardar la imagen resultante
image.save("result_imgpablito.png")
