import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import speech_recognition as sr
import pyttsx3

# Deshabilitar advertencias de symlinks en Windows
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# Nombre del modelo
MODEL_NAME = "meta-llama/Llama-2-7b-chat-hf"

# Configuración de quantización para eficiencia en memoria
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True
)

# Cargar tokenizador y modelo
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    device_map="auto",
    quantization_config=quantization_config
)

print("Modelo cargado en el dispositivo:", next(model.parameters()).device)

# Configurar nombre del usuario
NOMBRE_USUARIO = "Karen"  # Cambia esto según prefieras

# Inicializar síntesis de voz
engine = pyttsx3.init()
voices = engine.getProperty("voices")
if len(voices) > 2:
    engine.setProperty("voice", voices[2].id)
    print("Voz seleccionada:", voices[2].id)
else:
    print("No se encontró una tercera voz, usando la voz por defecto.")

engine.setProperty("rate", 165)  # Ajuste de velocidad más natural

# Inicializar reconocimiento de voz
recognizer = sr.Recognizer()
with sr.Microphone() as source:
    print("Ajustando para ruido ambiental...")
    recognizer.adjust_for_ambient_noise(source, duration=1)
    print("Listo, dime qué necesitas.")


def speak(text):
    """Convierte texto a voz con pausas naturales."""
    sentences = text.split(". ")
    for sentence in sentences:
        engine.say(sentence)
        engine.runAndWait()


def listen():
    """Escucha al usuario y convierte la voz en texto con mayor capacidad."""
    with sr.Microphone() as source:
        print("Te escucho... (Habla con calma y claridad)")
        try:
            audio = recognizer.listen(source, timeout=15, phrase_time_limit=25)  # Aumenta la duración del usuario
            text = recognizer.recognize_google(audio, language="es-ES")
            print(f"{NOMBRE_USUARIO} dijo:", text)
            return text
        except sr.UnknownValueError:
            print("Perdón, no entendí bien. ¿Puedes repetirlo?")
            speak("Perdón, no entendí bien. ¿Puedes repetirlo?")
        except sr.RequestError as e:
            print(f"Hubo un problema con el reconocimiento: {e}")
            speak("Parece que hubo un problema, intenta otra vez.")
        except sr.WaitTimeoutError:
            print("No escuché nada, dime otra vez.")
            speak("No escuché nada, dime otra vez.")
        return ""


def interact_with_assistant():
    conversation_history = (
        f"<<SYS>> Eres un experto en maquillaje y belleza. Habla de forma natural y cercana, sin sonar robótico. "
        f"Siempre llámame '{NOMBRE_USUARIO}'. Si te hacen preguntas fuera del tema, redirígelas a maquillaje. "
        f"Siempre responde en español, sin cambiar de idioma.<<SYS>>\n"
    )

    while True:
        user_input = listen()

        if user_input.strip().lower() == "salir":
            goodbye_msg = f"Me encantó hablar contigo, {NOMBRE_USUARIO}. Nos vemos pronto."
            print(goodbye_msg)
            speak(goodbye_msg)
            break

        # Si el usuario no ha dicho nada, seguimos esperando
        if not user_input.strip():
            continue

        # Agregar entrada del usuario al historial
        conversation_history += f"{NOMBRE_USUARIO}: {user_input}\n"

        # Si la respuesta está relacionada con maquillaje, seguimos
        if "maquillaje" not in user_input.lower() and "belleza" not in user_input.lower():
            no_related_msg = "Lo siento, solo puedo hablar sobre maquillaje y belleza. ¿Te gustaría hablar sobre eso?"
            print(no_related_msg)
            speak(no_related_msg)
            continue

        # Tokenizar el historial completo y mantener el contexto
        inputs = tokenizer(
            conversation_history + "Asistente:",
            return_tensors="pt",
            truncation=True,
            max_length=3072  # Aumenta la capacidad del historial
        )

        model_device = next(model.parameters()).device
        inputs = {k: v.to(model_device) for k, v in inputs.items()}

        # Generar respuesta con mayor cantidad de tokens
        outputs = model.generate(
            **inputs,
            max_new_tokens=350,  # Aumenta el límite de generación para respuestas más largas
            do_sample=True,
            temperature=0.7,
            pad_token_id=tokenizer.eos_token_id
        )

        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        assistant_response = response[len(conversation_history):].strip()

        # Limpiar posibles etiquetas como "Asistente:"
        assistant_response = assistant_response.replace("Asistente:", "").strip()

        # Verificar si la respuesta ya fue dada antes
        if assistant_response == conversation_history.split("\n")[-2]:
            print("Respuesta repetida detectada. No generando nueva respuesta.")
            continue

        # Hacer la respuesta más natural
        if assistant_response.endswith("."):
            assistant_response = assistant_response[:-1]

        print(f"Asistente ({NOMBRE_USUARIO}):", assistant_response, "\n")
        speak(assistant_response)

        # Mantener historial sin perder contexto
        conversation_history += assistant_response + "\n"

        # Evitar que el historial crezca demasiado
        if len(conversation_history) > 8000:
            conversation_history = conversation_history[-6000:]  # Mantiene más contexto


if __name__ == "__main__":
    interact_with_assistant()
