import torch
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from PIL import Image
from io import BytesIO
import requests
from diffusers import StableDiffusionXLImg2ImgPipeline
import os

# Inicializar FastAPI
app = FastAPI()

# Cargar el modelo de SDXL-Img2Img
pipe = StableDiffusionXLImg2ImgPipeline.from_single_file(
    "https://huggingface.co/martyn/sdxl-turbo-mario-merge-top-rated/blob/main/topRatedTurboxlLCM_v10.safetensors"
)
pipe.to("cuda", torch.float32)

# Carpeta para guardar imágenes generadas
OUTPUT_FOLDER = "generated_images"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.post("/generate")
async def generate_image(
    file: UploadFile = File(...),  # Se requiere una imagen obligatoriamente
    prompt: str = Form(...),
    negative_prompt: str = Form("nsfw"),
    strength: float = Form(0.15),
    guidance_scale: float = Form(7.5),
    num_inference_steps: int = Form(50),
):
    try:
        # Cargar la imagen base
        init_image = Image.open(BytesIO(await file.read())).convert("RGB").resize((1024, 1024))

        # Generar imagen con IA
        with torch.cuda.amp.autocast(enabled=False):  # Evita errores de tipos de datos
            image = pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                image=init_image,
                strength=strength,
                guidance_scale=guidance_scale,
                num_inference_steps=num_inference_steps
            ).images[0]

        # Guardar la imagen generada
        output_path = os.path.join(OUTPUT_FOLDER, "generated_image.png")
        image.save(output_path)

        # Enviar la imagen generada como archivo
        return FileResponse(output_path, media_type="image/png", filename="generated_image.png")

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
