from utilities.imports import *
from werkzeug.utils import secure_filename

app_configuracion = Blueprint('app_configuracion', __name__, url_prefix='/Configuración')

config = GlobalConfig()

def registrar_evento(Componente, Descripcion, tipo_evento):
    # Validación de parámetros
    if not all([Componente, Descripcion, tipo_evento]):
        logging.error("Faltan parámetros necesarios para registrar el evento: "
                      f"Componente={Componente}, Descripcion={Descripcion}, "
                      f"  tipo_evento={tipo_evento}.")
        return

    zona_horaria_mexico = pytz.timezone('America/Mexico_City')
    hora_utc = datetime.now(pytz.utc)
    hora_mexico = hora_utc.astimezone(zona_horaria_mexico)
    formato_fecha_hora_minuto = hora_mexico.strftime('%Y-%m-%dT%H:%M:%S%z')
    formato_fecha_hora_minuto = formato_fecha_hora_minuto[:-2] + ':' + formato_fecha_hora_minuto[-2:]

    descripcion_evento = f"{Descripcion}."
    identificacion_componente_alarma = Componente
    username = current_user.Nombre_completo  # Acceder al username

    try:
        estado = EventosDistribuidor.add(formato_fecha_hora_minuto, username, tipo_evento, descripcion_evento, identificacion_componente_alarma)
        alarmas = EventosAlarmasDistribuidor.add(estado,None,formato_fecha_hora_minuto  )
        
    except Exception as e:
        logging.error(f"Excepción al registrar evento: {str(e)} en {Componente} por {username}.")
        descripcion_evento_distribuidor_error_registro = f"Eventos: Error al registrar evento en {Componente}"
        EventosDistribuidor.add(formato_fecha_hora_minuto, username, 3, descripcion_evento_distribuidor_error_registro, identificacion_componente_alarma)    
        logging.error(f"Error al registrar evento de tipo {tipo_evento} en {Componente} por {username}.")

@app_configuracion.route('/Configuracion',methods=['POST','GET'])
@login_required
def configuracion():
    with VerificarPermisosUsuario("ClienteAlta", current_user.RolPerms) as contexto:
        if contexto is False:  # No tiene permisos
            return redirect("/scaizen/")
    if request.method == 'POST':
        
        actividad =request.form.get('actividad')
 
        print(actividad)
        if actividad:
                print("Entre a la actividad")

                datos =scaizen_cv_funtions.Cv_configuration.Select_cv(actividad)
                print(datos)

                return jsonify({'actividad': datos})
        

                
        payload = request.get_json(silent=True)
        if not payload:
                return jsonify({"error": "JSON inválido"}), 400

        formulario = payload.get("formulario")
        data = payload.get("data")
        if formulario == "CV":



            scaizen_cv_funtions.Cv_configuration.Add_cv(data)
            print("CV recibido correctamente")
            print(data)

            # 👉 Aquí va:
            # - validación
            # - guardado en DB
            # - generación XML

            return jsonify({"ok": True})
        
        return jsonify({"error": "Formulario no reconocido"}), 400
    else:
        session = cv.SessionLocal()
        usuarios = session.query(cv.Usuario_Cv.Nombre).all()
        usuarios = [u[0] for u in usuarios]
        logging.debug(usuarios)
        
        return render_template('scaizen/configuracion.html',endpoint='consultar_compras')

