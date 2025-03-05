import queue
import sounddevice as sd
import numpy as np
import whisper
import requests
import json
import subprocess

# Configuración
LM_STUDIO_URL = "http://192.168.1.88:1234/v1/chat/completions"
MODEL_NAME = "Meta-Llama-3.1-8B-Instruct"
DEVICE = None  # Usa None para el micrófono por defecto
SAMPLE_RATE = 16000  # Frecuencia de muestreo recomendada

# Cargar Whisper en modo "tiny" o "small" para baja latencia
whisper_model = whisper.load_model("small")

# Cola para audio en tiempo real
audio_queue = queue.Queue()

def audio_callback(indata, frames, time, status):
    """Captura audio en tiempo real y lo almacena en la cola."""
    if status:
        print(status)
    audio_queue.put(indata.copy())

def transcribe_audio():
    """Toma el audio de la cola y lo transcribe en tiempo real."""
    print("Esperando entrada de voz...")
    while True:
        audio_chunk = audio_queue.get()
        if audio_chunk is None:
            break
        audio_chunk = np.squeeze(audio_chunk)  # Reducir dimensiones
        result = whisper_model.transcribe(audio_chunk, fp16=False)
        text = result["text"].strip()
        if text:
            print(f"Usuario: {text}")
            process_response(text)

def query_llama(prompt):
    """Envía el texto a LLaMA y obtiene la respuesta."""
    headers = {"Content-Type": "application/json"}
    data = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    }
    response = requests.post(LM_STUDIO_URL, headers=headers, data=json.dumps(data))
    return response.json()["choices"][0]["message"]["content"]

def text_to_speech(text):
    """Convierte el texto en voz usando Piper TTS."""
    command = f'echo "{text}" | piper --model es_ES --output-raw | aplay'
    subprocess.run(command, shell=True)

def process_response(text):
    """Procesa la respuesta en tiempo real."""
    response = query_llama(text)
    print(f"IA: {response}")
    text_to_speech(response)

# Iniciar captura de audio
print("Iniciando asistente de voz...")
with sd.InputStream(callback=audio_callback, channels=1, samplerate=SAMPLE_RATE, device=DEVICE):
    transcribe_audio()
