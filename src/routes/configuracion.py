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
        #Mapeo del select        
        map_actividad =request.form.get('map_actividad')
        map_producto =request.form.get('map_producto')
        map_terminal =request.form.get('map_terminal')
        map_medidores =request.form.get('map_medidores')

 
        if map_actividad == "distribuidor" or map_actividad == "comercializador": 

                datos =scaizen_cv_funtions.Cv_configuration.Select_cv(map_actividad)
                print(datos)

                return jsonify({'map_actividad': datos})
        elif map_producto:
                datos =scaizen_cv_funtions.Producto_configuration.map_producto()
                return jsonify({'map_producto': datos})
        elif map_terminal:
             pass
        elif map_medidores:
            pass


        #Recuperacion de datos
        id = request.form.get('id')
        actividad =request.form.get('actividad')
        producto =request.form.get('producto')
        terminal =request.form.get('terminal')
        medidores =request.form.get('medidores')

        if producto:
            logging.info("Entre a la actividad")

            datos=scaizen_cv_funtions.Producto_configuration.Select_producto(id)
            logging.info('datos recuperados'+str(datos))
            return jsonify({'producto': datos})




        #Add,Delete,Update
        payload = request.get_json(silent=True)
        if not payload:
                return jsonify({"error": "JSON inválido"}), 400
        
        formulario = payload.get("formulario")
        data = payload.get("data") 
        id = int(payload.get('id', 0))
        proceso = payload.get("proceso")
        #print("Payload recibido:", payload)
        #print("Proceso:", proceso)
        #print("ID dato"+str(id))

        if formulario == "CV":
            cv_config = scaizen_cv_funtions.Cv_configuration()
            print("todo bien")
            try:
                if proceso =="add":
                    add_data_result = cv_config.Add_cv(data)            
                    #logging.info(f"CV recibido: {data}")
                    #logging.info(f"Resultado de add: {add_data_result}")
                    #logging.info(f"ID CV creado: {add_data_result.Id_CV}")
                    if add_data_result != 0:
                        return jsonify({"estatus": True,"id":add_data_result.Id_CV})
                
                elif proceso =="delete":
                    delete_data_result = cv_config.Delete_cv(id)            
                    if delete_data_result:
                        return jsonify({"estatus": True})
                
                elif proceso =="update":
                    print("ingrese a update")

                    update_data_result = cv_config.Update_cv(id,data)
                    logging.info(f"Resultado de add: {update_data_result}")
                    if update_data_result:
                         return jsonify({"estatus":True})

            except Exception as e:
                logging.error(f"Error procesando CV: {e}")
                return jsonify({"estatus": False, "mensaje": "Error interno"}), 500

            # 👉 Aquí va:
            # - validación
            # - guardado en DB
            # - generación XML

        
        return jsonify({"error": "Formulario no reconocido"}), 400
    else:
        session = cv.SessionLocal()
        usuarios = session.query(cv.Usuario_Cv.Nombre).all()
        usuarios = [u[0] for u in usuarios]
        logging.debug(usuarios)
        
        return render_template('scaizen/configuracion.html',endpoint='consultar_compras')

