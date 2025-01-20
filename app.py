from flask import Flask, jsonify, request # type: ignore
from flask_jwt_extended import JWTManager, create_access_token # type: ignore
from supabase import create_client, Client # type: ignore
import os
from dotenv import load_dotenv # type: ignore

# Cargar variables de entorno
load_dotenv()

# Configuración inicial de Flask
app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "mi_clave_secreta")
jwt = JWTManager(app)

# Configuración de Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Ruta básica de prueba
@app.route('/')
def home():
    return jsonify({"message": "¡Bienvenido a la API Flask!"})

# Usuarios simulados para autenticación
users_table = "users"  # Nombre de la tabla en Supabase

@app.route('/register', methods=['POST'])
def register():
    """Registrar un nuevo usuario"""
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "El nombre de usuario y contraseña son obligatorios"}), 400

    # Verificar si el usuario ya existe
    response = supabase.table(users_table).select("*").eq("username", username).execute()
    if response.data:
        return jsonify({"error": "El usuario ya existe"}), 409

    # Crear el usuario
    new_user = {"username": username, "password": password}  # En producción, hashear la contraseña
    supabase.table(users_table).insert(new_user).execute()
    return jsonify({"message": "Usuario registrado exitosamente"}), 201

@app.route('/login', methods=['POST'])
def login():
    """Autenticación de usuario"""
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "El nombre de usuario y contraseña son obligatorios"}), 400

    # Verificar credenciales
    response = supabase.table(users_table).select("*").eq("username", username).eq("password", password).execute()
    print(response)
    if not response.data:
        return jsonify({"error": "Credenciales inválidas"}), 401

    # Crear token JWT
    access_token = create_access_token(identity=username)
    return jsonify({"access_token": access_token}), 200

if __name__ == '__main__':
    app.run(debug=True, port=10000, host='0.0.0.0')