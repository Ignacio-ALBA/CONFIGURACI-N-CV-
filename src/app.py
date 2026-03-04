from flask import Flask, render_template, request, redirect, url_for, flash, session

#from flask_mysqldb import MySQL
from extensions import db
from sqlalchemy.sql import text
from sqlalchemy.exc import OperationalError

from config import config
#proteccion para el login, tokken csrf_token
from flask_wtf.csrf import CSRFProtect 
#login manager
from flask_login import LoginManager, login_user, logout_user, login_required,current_user
 

#Control de inactividad en sesion parte 1
from flask_session import Session
from datetime import datetime, timedelta, timezone

#Models
from models.ModelUser import ModelUser

#Entities:
from models.entities.User import User

#Routes
from routes.scaizen import app_scaizen
from utilities.imports import *

#Eventos
import pytz
import logging #para registrar errores y eventos.
import bcrypt

from models.scaizen_cv import EventosComercializador,EventosDistribuidor


# Tiempo de inactividad en segundos
SESSION_TIMEOUT = 600

app = Flask(__name__)
csrf = CSRFProtect(app)

app.config['SESSION_TIMEOUT'] = SESSION_TIMEOUT  # 1 minuto en segundos
# Hacer disponible en todas las plantillas
@app.context_processor
def inject_session_timeout():
    return dict(SESSION_TIMEOUT=app.config['SESSION_TIMEOUT'])

# Genera una clave secreta segura si no existe
import secrets
if not os.environ.get('FLASK_SECRET_KEY'):
    secret_key = secrets.token_hex(32)  # Genera una clave de 32 bytes (64 caracteres hex)
    os.environ['FLASK_SECRET_KEY'] = secret_key

app.secret_key = os.environ['FLASK_SECRET_KEY']

app.config.from_object(config['development'])
app.register_blueprint(app_scaizen)

# Inicializa SQLAlchemy
db.init_app(app)





csrf = CSRFProtect()
#db = MySQL(app)

login_manager_app = LoginManager(app)

@login_manager_app.user_loader #aqui se construye el current_user ,Flask lee el ID guardado en sesión 
def load_user(id):#Asi con un usuario loggeado ya podemos redireccionar al seleccionar el logo
    #logging.debug("login_manager_app")
    #logging.debug(id)
    user = cv.Usuario_Cv.select_by_id(id)
    rol = cv.Roles.select_by_IdRol(user.IdRol_fk)
    UsuarioActual = cv.UsuarioActual(user,rol)
    return UsuarioActual



@app.route('/')
def index():#Al acceder me redirije a la ruta login
    return redirect(url_for('login'))

@app.route('/login', methods=['GET','POST'])  # Ajusta la regla de ruta aquí
def login():
    if request.method == 'POST':        
            print(request.form['username'])
            print(request.form['password'])
            username = request.form['username']
            password = request.form['password']
            Componente = "Login Error"

            #user = User(0, request.form['username'],None,None ,request.form['password'],None,None,None)
            #logged_user=ModelUser.login(db, user)
            try:
                user = cv.Usuario_Cv.select_by_name(username)
                if user:
                    if bcrypt.checkpw(password.encode('utf-8'), user.Password.encode('utf-8')):
                        rol = cv.Roles.select_by_IdRol(user.IdRol_fk)
                        UsuarioActual = cv.UsuarioActual(user,rol)
                        
                        login_user(UsuarioActual)

                        descripcion_evento = f"Inicio de sesión exitoso para el usuario {user.Nombre}."
                        identificacion_componente_alarma = "Sistema de autenticación de usuarios"

                        estado = EventosDistribuidor.add(datetime.now(), user.Nombre, 5, descripcion_evento, identificacion_componente_alarma,request.remote_addr)
                        estado_2 = EventosComercializador.add(datetime.now(), user.Nombre, 5, descripcion_evento, identificacion_componente_alarma)

                        if estado is None or estado_2 is None:
                            logging.error("Error al registrar evento de inicio de sesión exitoso.")
 


                        password = None
                        username = None
                        """data_to_send = {
                                'id':user.Id
                                }
                        return redirect(url_for('app_scaizen.scaizen',**data_to_send))
                        """
                        return redirect(url_for('app_scaizen.scaizen'))

                    else:
                        flash("Contraseña invalida...")

                        descripcion_evento = f"{Componente}:Usuario desconocido."
                        identificacion_componente_alarma= "Sistema de autenticación de usuarios"

                        estado = EventosDistribuidor.add(datetime.now(),'Sistema',20,descripcion_evento,identificacion_componente_alarma,request.remote_addr)
                        if estado is None:
                            descripcion_evento_distribuidor_error_registro = f"Eventos:Error al registrar evento en {Componente}"
                            estado_registro_error = EventosDistribuidor.add(datetime.now(), None, 3,descripcion_evento_distribuidor_error_registro,identificacion_componente_alarma,request.remote_addr)
                            if estado_registro_error is None:
                                logging.error("Error al registrar evento de tipo 3 en eventos_comercializador")
                            else:
                                logging.info("Éxito al registrar evento del tipo 3")
                        else:
                            logging.info("Éxito al registrar evento tipo 20")



                        estado = EventosComercializador.add(datetime.now(),'Sistema', 20, descripcion_evento, identificacion_componente_alarma)
                        if estado is None:
                            estado_registro_error = EventosComercializador.add(datetime.now(),'Sistema', 3, descripcion_evento, identificacion_componente_alarma)
                            if estado_registro_error is None:
                                logging.error("Error al registrar evento de tipo 3 en eventos_comercializador")
                            else:
                                logging.info("Éxito al registrar evento del tipo 3")
                        else:
                            logging.info("Éxito al registrar evento tipo 20")

                        return render_template('auth/login.html') 
                else:
                    flash("Usuario no encontrado...")
                    
                    #formato_fecha_hora_minuto = formato_fecha_hora_minuto[:-2] + ':' + formato_fecha_hora_minuto[-2:]
                    descripcion_evento = f"{Componente}:Usuario desconocido."
                    identificacion_componente_alarma = "Sistema de autenticación de usuarios"

                    estado = EventosDistribuidor.add(datetime.now(), "Sistema", 20, descripcion_evento, identificacion_componente_alarma,request.remote_addr)                    
                    if estado is None:
                            descripcion_evento_distribuidor_error_registro = f"Eventos:Error al registrar evento en {Componente}"
                            estado_registro_error = EventosDistribuidor.add(datetime.now(), None, 3,descripcion_evento_distribuidor_error_registro,identificacion_componente_alarma,request.remote_addr)
                            if estado_registro_error is None:
                                logging.error("Error al registrar evento de tipo 3 en eventos_comercializador")
                            else:
                                logging.info("Éxito al registrar evento del tipo 3")
                    else:
                            logging.info("Éxito al registrar evento tipo 20")


                    #estado = EventosComercializador.add(datetime.now(),'Sistema',20,descripcion_evento,identificacion_componente_alarma,request.remote_addr)
                    estado = EventosComercializador.add(datetime.now(), 'Sistema', 20, descripcion_evento, identificacion_componente_alarma)

                    if estado is None:
                            #estado_registro_error = EventosComercializador.add(datetime.now(),'Sistema', 3, descripcion_evento, identificacion_componente_alarma,request.remote_addr)
                            estado_registro_error = EventosComercializador.add(datetime.now(), 'Sistema', 3, descripcion_evento, identificacion_componente_alarma)
                            if estado_registro_error is None:
                                logging.error("Error al registrar evento de tipo 3 en eventos_comercializador")
                            else:
                                logging.info("Éxito al registrar evento del tipo 3")
                    else:
                            logging.info("Éxito al registrar evento tipo 20")
                    return render_template('auth/login.html')






            except OperationalError:
                flash("No hay conexión a base de datos.", "warning")
                db.session.remove()  # Cierra la sesión actual
                return render_template('auth/login.html')  # Redirige a la página de login
    else:   
            return render_template('auth/login.html')

#cerrar sesion
@app.route('/logout' )
def logout():
     user = None
     logging.debug(current_user)
     if hasattr(current_user, 'Username'):
         user = current_user.Username
     
     descripcion_evento = f"Cierre de sesión para el usuario {user}."
     identificacion_componente_alarma = "Sistema de autenticación de usuarios"

     estado = EventosDistribuidor.add(datetime.now(), user, 5, descripcion_evento, identificacion_componente_alarma,request.remote_addr)
     if estado is None:
         logging.error("Error al registrar evento de cierre de sesión.")
     else:
         logging.info("Éxito al registrar evento de cierre de sesión.")

     logout_user()
     return redirect(url_for('login'))
 


#Para evitar regresar al menu al cerrar sesion
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response



@app.route('/permisos')
@login_required
def permisos(): #esta es una vista protegida solo para usuarios logeados
    return render_template('scaizen.html', title='Tablas', content=render_template('tables.html'),SESSION_TIMEOUT=SESSION_TIMEOUT)

@app.route('/protected')
@login_required
def protected(): #esta es una vista protegida solo para usuarios logeados
    return "<h1>Solo usuarios logeados</h1>"

def status_401(error):
    return redirect(url_for('login'))
def status_404(error):
    return render_template('error/error_404.html')



# Configuración de tiempo de inactividad (10 minutos)
# INACTIVITY_TIMEOUT = 600  # segundos

# @app.before_request
# def check_inactivity():
#     if current_user.is_authenticated:
#         now = datetime.now(timezone.utc)
#         last_activity = session.get('last_activity')
#         if last_activity:
#             last_activity_dt = datetime.strptime(last_activity, "%Y-%m-%d %H:%M:%S")
#             elapsed = (now.replace(tzinfo=None) - last_activity_dt).total_seconds()
#             if elapsed > INACTIVITY_TIMEOUT:
#                 logout_user()
#                 flash("Sesión cerrada por inactividad.", "warning")
#                 return redirect(url_for('login'))
#         # Actualiza la última actividad
#         session['last_activity'] = now.strftime("%Y-%m-%d %H:%M:%S")




@app.before_request
def update_last_activity():
    if current_user.is_authenticated:
        session['last_activity'] = datetime.now().isoformat()
        # Forzar la escritura de la sesión
        session.modified = True

@app.route('/check_session')
def check_session():
    if current_user.is_authenticated:
        last_activity = session.get('last_activity')
        if last_activity:
            last_activity = datetime.fromisoformat(last_activity)
            elapsed = (datetime.now() - last_activity).total_seconds()
            if elapsed > SESSION_TIMEOUT:
                logout_user()
                session.clear()
                return jsonify({'status': 'expired', 'redirect': url_for('login')})
        return jsonify({'status': 'active', 'remaining': SESSION_TIMEOUT - elapsed})
    return jsonify({'status': 'inactive'})

@app.route('/logout_by_timeout')
def logout_by_timeout():
    logout_user()
    session.clear()
    flash("Su sesión ha expirado por inactividad", "warning")
    return redirect(url_for('login'))

"""
@app.route('/scaizen')#Revisa si hay un usuario autenticado en sesión.
@login_required
def scaizen():
    #current_user es el usuario que está guardado en sesión principalmente en  login_user().
    user_id = current_user.id #Flask lee el ID guardado en sesión
    return render_template("scaizen.html")
"""





if __name__ == '__main__':

    # csrf.init_app(app)
    # app.config['SESSION_TYPE'] = 'filesystem'
    # app.config['SESSION_PERMANENT'] = False
    # app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)  # 10 minutos de inactividad
    # Session(app)

    csrf.init_app(app)
    # Configuración de sesión
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)

    Session(app)


    app.register_error_handler(401,status_401)
    app.register_error_handler(404,status_404)
    #cv.DescargasDistribuidor.load_data()
    #cv.CargaDistribuidor.load_data()
    app.run(host="0.0.0.0", port=5000, debug=True)
