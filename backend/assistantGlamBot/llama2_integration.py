import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import pyttsx3
import speech_recognition as sr

# Nombre del modelo en Hugging Face
MODEL_NAME = "meta-llama/Meta-Llama-3.1-8B-Instruct"

# Definir variables para el usuario
NOMBRE_USUARIO = "Karen"  # Nombre del usuario

# JSON con datos de morfología facial del usuario
MORFOLOGIA_USUARIO = {
    "tipo_rostro": "redondo",
    "ojos": "grandes",
    "color_piel": "clara"
}

# Historial de la conversación
historial_conversacion = [
    {
        "role": "system",
        "content": (
            f"Eres GlamBot, un asistente experto en maquillaje y belleza. "
            f"Siempre te diriges a {NOMBRE_USUARIO} de forma amigable. "
            "Tu objetivo es asesorarla en maquillaje, cuidado de la piel y belleza en general. "
            "Si la conversación se aleja del tema, intenta redirigirla con tacto."
        )
    }
]

# Inicializar el modelo y el tokenizer
device = "cuda" if torch.cuda.is_available() else "cpu"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, torch_dtype=torch.float16).to(device)

# Inicialización de la voz
engine = pyttsx3.init()

# Configuración de la voz en español (Sabina de Microsoft)
VOZ_OBJETIVO = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_ES-MX_SABINA_11.0"
voz_encontrada = None
for voz in engine.getProperty('voices'):
    if voz.id == VOZ_OBJETIVO:
        voz_encontrada = voz
        break

if voz_encontrada:
    engine.setProperty('voice', voz_encontrada.id)
    print(f"✅ Voz seleccionada: {voz_encontrada.name}")
else:
    print("⚠️ Voz preferida no encontrada. Usando voz por defecto.")
    print(f"Voces disponibles: {[voz.name for voz in engine.getProperty('voices')]}")

# Configuración de la velocidad de habla y volumen
engine.setProperty("rate", 160)
engine.setProperty("volume", 0.9)

# Función para convertir el texto en voz
def speak(text):
    clean_text = text.replace("#", "").replace("*", "").strip()  # Limpiar texto
    engine.say(clean_text)
    engine.runAndWait()

# Función para capturar la entrada de voz del usuario
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            recognizer.adjust_for_ambient_noise(source, duration=0.8)
            print("\n🎤 [Escuchando...]")
            audio = recognizer.listen(source, timeout=12, phrase_time_limit=18)
            text = recognizer.recognize_google(audio, language="es-ES")
            print(f"👤 [Usuario]: {text}")
            return text
        except sr.WaitTimeoutError:
            print("⏳ [Sistema]: Tiempo de espera agotado")
            return None
        except Exception as e:
            print(f"❌ [Error]: {str(e)}")
            return None

# Función para generar respuesta con el modelo de Hugging Face
def generate_response_with_huggingface(historial):
    try:
        # Limitar el tamaño del historial a las últimas 5 interacciones
        MAX_HISTORY_LENGTH = 5
        if len(historial) > MAX_HISTORY_LENGTH:
            historial = historial[-MAX_HISTORY_LENGTH:]

        # Construir el prompt a partir del historial
        prompt = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in historial])

        # Limitar la longitud de la entrada a 1024 tokens
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024).to(device)

        # Generar respuesta con parámetros optimizados
        outputs = model.generate(**inputs, max_new_tokens=100, temperature=0.6, top_k=50)  # top_k para acelerar la generación

        # Decodificar respuesta
        response = tokenizer.decode(outputs[:, inputs.input_ids.shape[-1]:][0], skip_special_tokens=True)
        return response.strip()

    except Exception as e:
        print(f"⚠️ Error generando respuesta: {e}")
        return "Ocurrió un error procesando tu solicitud."

# Función principal para interactuar con el asistente
def interact_with_assistant():
    print(f"🤖 [GlamBot]: Hola {NOMBRE_USUARIO}, soy GlamBot. ¿En qué puedo ayudarte hoy?")
    speak(f"Hola {NOMBRE_USUARIO}, soy GlamBot. ¿En qué puedo ayudarte hoy?")

    while True:
        user_input = listen()

        if not user_input:
            continue

        # Verificar si el usuario quiere salir
        if any(word in user_input.lower() for word in ["salir", "terminar", "adiós"]):
            farewell = f"¡Gracias por conversar, {NOMBRE_USUARIO}! Hasta la próxima."
            print(f"🤖 [GlamBot]: {farewell}")
            speak(farewell)
            break

        # Agregar la entrada del usuario al historial de conversación
        historial_conversacion.append({"role": "user", "content": user_input})

        # Generar respuesta con el modelo
        response = generate_response_with_huggingface(historial_conversacion)

        # Agregar la respuesta del asistente al historial
        historial_conversacion.append({"role": "assistant", "content": response})

        # Mostrar y decir la respuesta
        print(f"🤖 [GlamBot]: {response}")
        speak(response)

# Ejecutar el asistente
if __name__ == "__main__":
    interact_with_assistant()
