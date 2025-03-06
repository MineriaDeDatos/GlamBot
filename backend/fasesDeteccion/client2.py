from flask import Flask, request, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Carpeta para almacenar las fotos
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

# Estructura para almacenar los datos temporalmente
user_data = {}

# Verificar si el archivo tiene una extensión permitida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# Ruta para recibir el nombre del usuario
@app.route('/receive_name', methods=['POST'])
def receive_name():
    try:
        data = request.json
        user_name = data.get('name', '')
        if user_name:
            user_data['name'] = user_name
            return jsonify({"message": "Name received successfully!"}), 200
        else:
            return jsonify({"message": "Name is missing!"}), 400
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500


# Ruta para recibir el tipo de piel
@app.route('/receive_skin_type', methods=['POST'])
def receive_skin_type():
    try:
        data = request.json
        skin_type = data.get('skin_type', '')
        if skin_type:
            user_data['skin_type'] = skin_type
            return jsonify({"message": "Skin type received successfully!"}), 200
        else:
            return jsonify({"message": "Skin type is missing!"}), 400
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500


# Ruta para recibir la foto del usuario
@app.route('/receive_photo', methods=['POST'])
def receive_photo():
    try:
        if 'photo' not in request.files:
            return jsonify({"message": "No photo part!"}), 400

        photo = request.files['photo']

        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo.save(filepath)
            user_data['photo'] = filepath  # Guardar la ruta del archivo de la foto
            return jsonify({"message": "Photo received successfully!"}), 200
        else:
            return jsonify({"message": "Invalid photo format!"}), 400

    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500


# Ruta para recibir las características del rostro, ojos y tono de piel
@app.route('/receive_features', methods=['POST'])
def receive_features():
    try:
        data = request.json
        if not data:
            return jsonify({"message": "No data received!"}), 400

        print(f"Datos recibidos en client2: {data}")  # Log de los datos recibidos

        # Almacenar las características en el diccionario user_data
        user_data['features'] = data
        return jsonify({"message": "Features received successfully!"}), 200
    except Exception as e:
        print(f"Error al recibir los datos: {str(e)}")  # Log de errores
        return jsonify({"message": f"Error: {str(e)}"}), 500


# Ruta para obtener todos los datos recibidos
@app.route('/get_user_data', methods=['GET'])
def get_user_data():
    try:
        return jsonify(user_data), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500


# Nueva ruta para obtener los datos combinados (nombre, tipo de piel, features)
@app.route('/get_combined_data', methods=['GET'])
def get_combined_data():
    try:
        combined_data = {
            "name": user_data.get('name', 'No name provided'),
            "skin_type": user_data.get('skin_type', 'No skin type provided'),
            "features": user_data.get('features', 'No features provided')
        }
        return jsonify(combined_data), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500


# Nueva ruta para obtener la foto recibida
@app.route('/get_photo', methods=['GET'])
def get_photo():
    try:
        # Verificar si se ha guardado una foto
        if 'photo' in user_data:
            photo_path = user_data['photo']
            # Extraer el nombre de archivo de la ruta de la foto
            filename = os.path.basename(photo_path)
            # Enviar la foto almacenada en el servidor
            return send_from_directory(app.config['UPLOAD_FOLDER'], filename), 200
        else:
            return jsonify({"message": "No photo found!"}), 404
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500


if __name__ == '__main__':
    # Verificar si la carpeta 'uploads' existe, si no, crearla
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    # Correr la aplicación Flask
    app.run(host='0.0.0.0', port=5000)
