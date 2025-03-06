import requests
import pyttsx3
import base64
from flask import Flask, request, jsonify

# Configuración del servidor y el modelo
SERVER_URL = "http://192.168.1.88:1234/v1/chat/completions"
USER_DATA_URL = "http://192.168.1.88:5000/get_combined_data"  # URL para obtener los datos combinados
NOMBRE_MODELO = "Meta-Llama-3.1-8B-Instruct"  # Nombre del modelo en LM Studio

# Inicialización de la voz
engine = pyttsx3.init()
engine.setProperty("rate", 160)  # Velocidad de habla
engine.setProperty("volume", 0.9)  # Volumen
VOZ_OBJETIVO = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_ES-MX_SABINA_11.0"

# Configuración de la voz
voz_encontrada = None
for voz in engine.getProperty('voices'):
    if voz.id == VOZ_OBJETIVO:
        voz_encontrada = voz
        break
if voz_encontrada:
    engine.setProperty('voice', voz_encontrada.id)

# Flask para manejar interacciones
app = Flask(__name__)


# Función para obtener los datos del usuario desde el servidor
def get_user_features():
    try:
        response = requests.get(USER_DATA_URL)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"⚠️ Error al obtener los datos del usuario: {response.status_code}")
            return None
    except Exception as e:
        print(f"⚠️ Error al hacer la solicitud GET: {e}")
        return None


# Función para limpiar el texto (eliminar caracteres innecesarios)
def clean_text(text):
    return text.replace("#", "").replace("*", "").replace("**", "").strip()


# Función para generar la respuesta con el modelo local (LM Studio)
def generate_response_with_local_model(user_input, features, skin_type, name, conversation_history):
    try:
        # Limpiar el texto del usuario antes de procesarlo
        user_input = clean_text(user_input)

        # Convertir las características del usuario a una descripción
        descripcion_features = (
            f"Tengo un rostro {features['rostro']}, ojos {features['ojos']} y piel {features['tono_piel']}. "
            f"Mi tipo de piel es {skin_type}."
        )

        conversation_history.append({"role": "user", "content": user_input})

        # Datos de entrada para el modelo, incluyendo el historial de conversación
        payload = {
            "model": NOMBRE_MODELO,
            "messages": [{"role": "system",
                          "content": f"Eres un experto en maquillaje y belleza personal. Siempre me llamas '{name}'. Mi información de belleza es la siguiente: {descripcion_features}"},
                         *conversation_history],
            "temperature": 0.7,
            "max_tokens": 300
        }

        # Realizar la petición POST al servidor
        response = requests.post(SERVER_URL, json=payload)
        if response.status_code == 200:
            response_data = response.json()
            return response_data.get('choices', [{}])[0].get('message', {}).get('content', '')
        else:
            return "Error al procesar la solicitud"
    except Exception as e:
        return f"Error: {e}"


# Función para convertir texto en voz y devolverlo como base64
def generate_audio_response(text):
    engine.save_to_file(text, "response.mp3")
    engine.runAndWait()

    # Convertir audio a base64
    with open("response.mp3", "rb") as audio_file:
        audio_base64 = base64.b64encode(audio_file.read()).decode('utf-8')

    return audio_base64


# Ruta para recibir mensajes del cliente y generar la respuesta
@app.route("/interact", methods=["POST"])
def interact():
    # Obtener los datos del usuario
    user_features = get_user_features()
    if user_features is None:
        return jsonify({"error": "No se pudieron obtener los datos del usuario"}), 500

    data = request.json
    user_input = data.get('message')
    features = user_features.get("features", {})
    skin_type = user_features.get("skin_type", "desconocido")
    name = user_features.get("name", "Usuario")
    conversation_history = data.get('conversation_history', [])

    # Limpiar el texto del usuario antes de procesarlo
    user_input = clean_text(user_input)

    # Obtener la respuesta del modelo
    response_text = generate_response_with_local_model(user_input, features, skin_type, name, conversation_history)

    # Generar audio para la respuesta
    audio_base64 = generate_audio_response(response_text)

    return jsonify({
        "text_response": response_text,
        "audio_response": audio_base64
    })


# Ejecutar el servidor Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
