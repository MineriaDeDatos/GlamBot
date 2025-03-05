import requests
import pyttsx3
import speech_recognition as sr
import json

# Dirección del servidor local (asegúrate de que LM Studio esté corriendo con el modelo)
SERVER_URL = "http://192.168.1.88:1234/v1/chat/completions"

# Definir variables para el usuario y el modelo
NOMBRE_USUARIO = "Karen"  # Nombre del usuario
NOMBRE_MODELO = "Meta-Llama-3.1-8B-Instruct"  # Nombre del modelo en LM Studio

# JSON con datos de morfología facial (ejemplo)
MORFOLOGIA_USUARIO = {
    "tipo_rostro": "redondo",
    "ojos": "grandes",
    "color_piel": "clara"
}

# Inicialización de la voz
engine = pyttsx3.init()

# Configuración de voz personalizada
VOZ_OBJETIVO = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_ES-MX_SABINA_11.0"

# Buscar la voz exacta
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
engine.setProperty("rate", 160)  # Velocidad de habla
engine.setProperty("volume", 0.9)  # Volumen


# Función para limpiar el texto (eliminar caracteres innecesarios como # y *)
def clean_text(text):
    return text.replace("#", "").replace("*", "").replace("**", "").strip()


# Función para convertir el texto en voz
def speak(text):
    text = clean_text(text)  # Limpiar el texto antes de hablar
    engine.say(text)
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


# Función para generar respuesta con el modelo local (LM Studio)
def generate_response_with_local_model(user_input, morfologia):
    try:
        # Convertir la morfología a una descripción en texto
        descripcion_morfologia = (
            f"Tengo un rostro {morfologia['tipo_rostro']}, ojos {morfologia['ojos']} y piel {morfologia['color_piel']}."
        )

        # Datos de entrada para el modelo
        payload = {
            "model": NOMBRE_MODELO,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        f"Eres un experto en maquillaje y belleza personal. "
                        f"Siempre me llamas '{NOMBRE_USUARIO}'. "
                        "Tu objetivo es asesorarme sobre maquillaje, cuidado de la piel, peinados y estilos de belleza. "
                        "Si la pregunta no es sobre estos temas, debes redirigir la conversación a maquillaje o belleza. "
                        f"Mi información de belleza es la siguiente: {descripcion_morfologia}"
                    )
                },
                {"role": "user", "content": user_input}
            ],
            "temperature": 0.7,  # Nivel de creatividad del modelo
            "max_tokens": 300  # Límite de tokens generados
        }

        # Realizar la petición POST al servidor
        response = requests.post(SERVER_URL, json=payload)

        # Si la respuesta es exitosa, procesarla
        if response.status_code == 200:
            response_data = response.json()
            answer = response_data.get('choices', [{}])[0].get('message', {}).get('content', '')

            # Si la respuesta no es sobre maquillaje, redirigir al tema correcto
            if "no relacionado" in answer.lower() or "pregunta fuera de tema" in answer.lower():
                return f"{NOMBRE_USUARIO}, recuerda que solo hablo sobre maquillaje y belleza. ¿Quieres consejos de maquillaje?"

            return answer
        else:
            print(f"⚠️ Error al obtener la respuesta del modelo: {response.status_code}")
            return "Ocurrió un error al procesar tu solicitud."

    except Exception as e:
        print(f"⚠️ Error al realizar la solicitud: {e}")
        return "Ocurrió un error procesando tu solicitud."


# Función para preguntar preferencias al usuario
def preguntar_preferencias():
    speak(f"{NOMBRE_USUARIO}, ¿qué tipo de maquillaje prefieres hoy?")
    print(f"🤖 [GlamBot]: {NOMBRE_USUARIO}, ¿qué tipo de maquillaje prefieres hoy?")
    preferencia = listen()

    if not preferencia:
        return "natural"  # Valor por defecto si no responde

    return preferencia


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

        # Preguntar preferencias
        preferencia_maquillaje = preguntar_preferencias()

        # Generar respuesta con el modelo incluyendo las preferencias
        input_con_preferencia = f"{user_input}. Me gustaría un maquillaje {preferencia_maquillaje}."
        response = generate_response_with_local_model(input_con_preferencia, MORFOLOGIA_USUARIO)

        print(f"🤖 [GlamBot]: {response}")
        speak(response)


# Ejecutar el asistente
if __name__ == "__main__":
    interact_with_assistant()
