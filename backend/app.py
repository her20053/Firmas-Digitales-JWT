import jwt
from datetime import datetime, timedelta, timezone
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
import bcrypt

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

# Uso de la clase UserManager
uri = "mongodb+srv://mongodbuser:mongodbpassword@firmasdigitalesjwt.bci9p39.mongodb.net/?retryWrites=true&w=majority&appName=FirmasDigitalesJWT"
user_manager = UserManager(uri)

# # Ejemplo de creación de usuario
creado_exitosamente, mensaje = user_manager.crear_usuario("usuario_prueba_3", "contraseña_prueba_3")
print(mensaje)

# Ejemplo de autenticación de usuario
autenticado, mensaje = user_manager.autenticar_usuario("usuario_prueba_3", "contraseña_prueba_3")
print(mensaje)

# Ejemplo de generación y verificación de token JWT
if autenticado:
    token = user_manager.generar_token_jwt("usuario_prueba")
    print("Token JWT generado:", token)
    verificado, user_id = user_manager.verificar_token_jwt(token)
    if verificado:
        print("Token JWT verificado. ID de usuario:", user_id)
    else:
        print("Error al verificar el token JWT.")
