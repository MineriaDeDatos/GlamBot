import requests
import pyttsx3
import base64
from flask import Flask, request, jsonify

# Configuración del servidor y el modelo
SERVER_URL = "http://192.168.1.88:1234/v1/chat/completions"
USER_DATA_URL = "http://192.168.1.88:5000/get_combined_data"
NOMBRE_MODELO = "Meta-Llama-3.1-8B-Instruct"

# Inicialización de la voz
engine = pyttsx3.init()
engine.setProperty("rate", 160)
engine.setProperty("volume", 0.9)
VOZ_OBJETIVO = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_ES-MX_SABINA_11.0"

# Configuración de la voz
for voz in engine.getProperty("voices"):
    if voz.id == VOZ_OBJETIVO:
        engine.setProperty("voice", voz.id)
        break

# Inicialización de Flask
app = Flask(__name__)

# 🔹 Función para obtener los datos del usuario
def get_user_features():
    try:
        response = requests.get(USER_DATA_URL)
        return response.json() if response.status_code == 200 else {}
    except Exception as e:
        print(f"⚠️ Error obteniendo datos del usuario: {e}")
        return {}

# 🔹 Función para limpiar el texto (eliminar caracteres innecesarios)
def clean_text(text):
    return text.replace("#", "").replace("*", "").replace("**", "").strip() if text else ""

# 🔹 Generación de respuesta con modelo local optimizado para maquillaje
def generate_makeup_prompt(user_input, features, skin_type, name):
    try:
        user_input = clean_text(user_input)

        # Asegurar valores predeterminados si no existen
        rostro = features.get("rostro", "desconocido")
        ojos = features.get("ojos", "desconocido")
        piel = features.get("tono_piel", "desconocido")
        skin_type = skin_type or piel  # Si `skin_type` está vacío, usa `tono_piel`

        # Construcción del prompt SOLO para maquillaje
        prompt = {
            "role": "system",
            "content": (
                f"Eres GlamBot, un experto en maquillaje. Solo genera respuestas relacionadas con maquillaje. Siempre me llamaras {name}. "
                f"Mis características son: rostro {rostro}, ojos {ojos}, y piel {skin_type}. "
                "Basado en mi solicitud, sugiere un maquillaje ideal sin agregar información adicional."
            )
        }

        # Datos de entrada para el modelo
        payload = {
            "model": NOMBRE_MODELO,
            "messages": [prompt, {"role": "user", "content": user_input}],
            "temperature": 0.3,
            "max_tokens": 250
        }

        # Realizar la petición al modelo
        response = requests.post(SERVER_URL, json=payload)
        if response.status_code == 200:
            response_data = response.json()
            return response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
        else:
            return "⚠️ No se pudo obtener una respuesta del modelo."
    except Exception as e:
        return f"⚠️ Error generando el prompt: {e}"

# 🔹 Función para convertir texto a voz en base64
def generate_audio_response(text):
    try:
        engine.save_to_file(text, "response.mp3")
        engine.runAndWait()

        # Convertir audio a base64
        with open("response.mp3", "rb") as audio_file:
            return base64.b64encode(audio_file.read()).decode("utf-8")
    except Exception as e:
        print(f"⚠️ Error generando audio: {e}")
        return ""

# 🔹 Ruta para interacción con GlamBot
@app.route("/interact", methods=["POST"])
def interact():
    user_features = get_user_features()
    features = user_features.get("features", {})
    skin_type = user_features.get("skin_type", features.get("tono_piel", "desconocido"))
    name = user_features.get("name", "Usuario")

    data = request.json
    user_input = clean_text(data.get("message", ""))

    # Generar la respuesta optimizada para maquillaje
    response_text = clean_text(generate_makeup_prompt(user_input, features, skin_type, name))

    # Generar audio en base64
    audio_base64 = generate_audio_response(response_text)

    return jsonify({
        "text_response": response_text,
        "audio_response": audio_base64
    })

# 🔹 Ejecutar el servidor Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
