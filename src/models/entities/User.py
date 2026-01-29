from werkzeug.security import check_password_hash #, generate_password_hash

#Saber si se encuentra activo
from flask_login import UserMixin

 
class User(UserMixin):#Para el manejo de usaurios y autenticacion

    def __init__(self, Id, Nombre, Nombre_completo, Telefono, Password, Tipo_usuario, Cambio_contraseña, Estatus_usuario  ) -> None:
        self.id = Id
        self.nombre_user = Nombre
        self.Nombre_completo = Nombre_completo
        self.password_user = Password
        self.telefono_user = Telefono
        self.tipo_usuario_user = Tipo_usuario
        self.cambio_contraseña_user = Cambio_contraseña
        self.estatus_usuario_user = Estatus_usuario

    @classmethod  #No se instancia la clase    
    def check_password(self, hashed_password, password_user):#contraseña guardada en la db, texto plano
        return check_password_hash(hashed_password, password_user)

#import hashlib

#cadena = 'albadti'
#contaenar = '123456'
#cadena2 = contaenar + cadena
#hash_python = hashlib.sha256(cadena.encode()).hexdigest()
#print(hash_python)  
#print(generate_password_hash('albadti'))
