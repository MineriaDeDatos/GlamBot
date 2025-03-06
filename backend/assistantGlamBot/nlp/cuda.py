import torch
import pyttsx3


print("Torch version:", torch.__version__)
print("CUDA version:", torch.version.cuda)
print("CUDA disponible:", torch.cuda.is_available())
print("Dispositivo actual:", torch.cuda.current_device() if torch.cuda.is_available() else "CPU")
print("CUDA available:", torch.cuda.is_available())
print("GPU:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU only")



# Inicializar el motor de síntesis de voz
engine = pyttsx3.init()

# Obtener las voces disponibles
voices = engine.getProperty("voices")

# Imprimir las voces disponibles
for i, voice in enumerate(voices):
    print(f"Voz {i + 1}: {voice.name} - ID: {voice.id}")
