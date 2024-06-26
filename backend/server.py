from flask import Flask, request, jsonify
import jwt
from datetime import datetime, timedelta, timezone
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
import bcrypt

# Importamos CORS para permitir peticiones desde cualquier origen

from flask_cors import CORS

app = Flask(__name__)

# Permitimos peticiones desde cualquier origen

CORS(app)

class UserManager:
    def __init__(self, uri):
        self.client = MongoClient(uri, server_api=ServerApi('1'))
        self.db = self.client['Users']
        self.users_collection = self.db['usuarios']

    def crear_usuario(self, nombre_usuario, contraseña):
        # Verificar si el usuario ya existe
        if self.users_collection.find_one({"nombre_usuario": nombre_usuario}):
            return False, "El nombre de usuario ya está en uso."
        
        # Hashear la contraseña
        contraseña_hash = bcrypt.hashpw(contraseña.encode('utf-8'), bcrypt.gensalt())

        # Crear el nuevo usuario en la base de datos
        nuevo_usuario = {
            "nombre_usuario": nombre_usuario,
            "contraseña_hash": contraseña_hash
        }
        self.users_collection.insert_one(nuevo_usuario)
        return True, "Usuario creado exitosamente."

    def autenticar_usuario(self, nombre_usuario, contraseña):
        usuario = self.users_collection.find_one({"nombre_usuario": nombre_usuario})
        if usuario:
            # Verificar la contraseña hasheada
            if bcrypt.checkpw(contraseña.encode('utf-8'), usuario["contraseña_hash"]):
                return True, "Autenticación exitosa."
            else:
                return False, "Contraseña incorrecta."
        else:
            return False, "Usuario no encontrado."

    def generar_token_jwt(self, nombre_usuario):
        # Obtener el ID del usuario de la base de datos
        usuario = self.users_collection.find_one({"nombre_usuario": nombre_usuario})
        if usuario:
            user_id = str(usuario["_id"])

            # Configurar la información a incluir en el token
            payload = {
                "user_id": user_id,
                "exp": datetime.now(timezone.utc) + timedelta(days=1)
            }

            # Generar el token JWT firmado
            token = jwt.encode(payload, 'tu_clave_secreta', algorithm='HS256')

            return token
        else:
            return None

    def verificar_token_jwt(self, token):
        try:
            # Verificar y decodificar el token
            payload = jwt.decode(token, 'tu_clave_secreta', algorithms=['HS256'])
            user_id = payload["user_id"]
            # Aquí puedes realizar acciones adicionales, como cargar la información del usuario desde la base de datos si es necesario
            return True, user_id
        except jwt.ExpiredSignatureError:
            return False, "Token expirado."
        except jwt.InvalidTokenError:
            return False, "Token inválido."

@app.route('/registro', methods=['POST'])
def registro():
    datos = request.get_json()
    nombre_usuario = datos.get('nombre_usuario')
    contraseña = datos.get('contraseña')

    print(f"El nombre de usuario es: {nombre_usuario} con la contraseña: {contraseña}")

    creado_exitosamente, mensaje = user_manager.crear_usuario(nombre_usuario, contraseña)
    return jsonify({"creado_exitosamente": creado_exitosamente, "mensaje": mensaje})

@app.route('/autenticacion', methods=['POST'])
def autenticacion():
    datos = request.get_json()
    nombre_usuario = datos.get('nombre_usuario')
    contraseña = datos.get('contraseña')
    autenticado, mensaje = user_manager.autenticar_usuario(nombre_usuario, contraseña)
    if autenticado:
        token = user_manager.generar_token_jwt(nombre_usuario)
        return jsonify({"autenticado": autenticado, "mensaje": mensaje, "token": token})
    else:
        return jsonify({"autenticado": autenticado, "mensaje": mensaje})

@app.route('/verificacion', methods=['POST'])
def verificacion():
    datos = request.get_json()
    token = datos.get('token')
    verificado, user_id = user_manager.verificar_token_jwt(token)
    return jsonify({"verificado": verificado, "user_id": user_id})

if __name__ == '__main__':
    uri = "mongodb+srv://mongodbuser:mongodbpassword@firmasdigitalesjwt.bci9p39.mongodb.net/?retryWrites=true&w=majority&appName=FirmasDigitalesJWT"
    user_manager = UserManager(uri)
    app.run(debug=True)
