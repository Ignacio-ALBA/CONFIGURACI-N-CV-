from .entities.User import User
from sqlalchemy.sql import text
from models import scaizen_cv as cv

class ModelUser():
    @classmethod 
    def login(self, db, user): #referencia al propio objeto, conexion a la db, para hacer la autenticacion
        query_main = text('SELECT Id, Nombre, Nombre_completo, Telefono, Password,Tipo_usuario,Cambio_contraseña,Estatus_usuario  FROM usuarios_cv WHERE Nombre = :nombre')
        params = {'nombre': user.nombre_user}  # Clave 'nombre' coincide con el parámetro en la consulta

        try:
            with cv.SessionLocal() as connection:
                cursor = connection.execute(query_main, params)
                row = cursor.fetchone()
                if row != None:
                    user = User(row[0], row[1], row[2], row[3], User.check_password(row[4], user.password_user),row[5],row[6],row[7])
                    return user
                else:
                    return None
        except Exception as ex:
            raise Exception(ex)    

    @classmethod 
    def get_by_id(self, db, id): #referencia al propio objeto, conexion a la db, para hacer la autenticacion
        query_main = text('SELECT Id, Nombre, Nombre_completo, Telefono, Password,Tipo_usuario,Cambio_contraseña,Estatus_usuario  FROM usuarios_cv WHERE id = :id')
        params = {'id': id}  # Clave 'nombre' coincide con el parámetro en la consulta

        
        try:
            with cv.SessionLocal() as connection:
                cursor = connection.execute(query_main,params)
                row = cursor.fetchone()
                if row != None:
                    return User(row[0], row[1],row[2],row[3], row[4], row[5], row[6], row[7])

                    #checar return User(row[0], row[1],row[2],None, row[3], row[4], row[5], row[6])
                else:
                    return None

        except Exception as ex:
            raise Exception(ex)    
        finally:
            cursor.close()#Cierro la conexión--