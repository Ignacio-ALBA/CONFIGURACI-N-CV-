# .venv\Scripts\activate   
# python .\src\app.py  
from utilities.imports import *
from routes.comercializador import app_comercializador
from routes.distribuidor import app_distribuidor
from routes.catalago import app_catalogo
from routes.configuracion import app_configuracion

mngj_son_src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..","data_json/reportes_volumetricos_data.json"))

config = GlobalConfig()

app_scaizen = Blueprint('app_scaizen', __name__, url_prefix='/scaizen')

#No repetir
#login_manager_app = LoginManager()
#login_manager_app.login_view = 'app_scaizen.login'
app_scaizen.register_blueprint(app_comercializador)
app_scaizen.register_blueprint(app_distribuidor)
app_scaizen.register_blueprint(app_catalogo)
app_scaizen.register_blueprint(app_configuracion)

elementos_por_pagina = 10
elementos = list(range(1, 101))

@app_scaizen.context_processor
def context_variables():
    return {
        'productos_color': config.PRODUCTOS_COLOR_BY_NAME,
        'productos_names': config.PRODUCTOS_NAMES
    }

@app_scaizen.route('/',methods=['GET','POST'])
##@fresh_login_required login reciente ,se usa para cambiar contraseña,eliminar cuenta y operaciones bancarias y cambiar email
@login_required
def scaizen():

    if request.method == 'POST':
        user_id = request.form.get('user_id')
        new_password = request.form.get('new_password')
        if user_id and new_password:
            user = cv.Usuario_Cv.select_by_id(user_id)
            user_change = cv.Usuario_Cv.update(user_id,password = new_password, cambio_contraseña=0, ultimo_cambio_pwd=True)
            if user_change:
                return {'response':True}
        else: return {'response':False}

    change_pwd_box = False
    logging.debug(current_user.Cambio_contraseña)
    if current_user.is_authenticated and current_user.Cambio_contraseña == 1 or \
        (current_user.ultimo_cambio_pwd + timedelta(days=30)).date() <= datetime.now().date():
        change_pwd_box = True
    #if current_user.is_authenticated and "delete_user" in current_user.RolPerms:

    """
    if request.method == 'POST':
        #print(request.form['new_password'])
        print("aquitadeologin")
        usuario = request.form['user']
        cv.Usuario_Cv.select_by_name(usuario)
    """
    return render_template('scaizen/inicio.html', img = True, change_pwd_box= change_pwd_box)

#Planificacion
@app_scaizen.route('/planificacion')
@login_required
def planificacion():

    return render_template('scaizen/permisos.html')

#subplanificacion
@app_scaizen.route('/compras/descarga', methods=['GET','POST'])
@login_required
def planificacion_descarga():
    config = GlobalConfig()
    page_num = request.form.get('page', 1, type=int)

    if request.method == 'POST':
    
        fecha_inicio = request.form.get('selected_start')
        fecha_fin = request.form.get('selected_end')
        
        descargas = Tabla_descargas(fecha_inicio,fecha_fin, None, None,  None, None, None, None, None,None)
        
        start_index = (page_num - 1) * elementos_por_pagina + 1
        end_index = start_index + elementos_por_pagina

        Mostrar_descargas, total = ModelTablas.descargas(db, descargas, page_num,elementos_por_pagina)

        total_pages = total // elementos_por_pagina + (total % elementos_por_pagina > 0)

        # Calcular el índice del último registro
        end_index = min(start_index + elementos_por_pagina, total)
        if end_index > total:
            end_index = total

        # Crear objeto paginable
        pagination = Pagination(page=page_num, total=total, per_page=elementos_por_pagina,
                                display_msg=f"Mostrando registros {start_index} - {end_index} de un total de <strong>({total})</strong>")
        if Mostrar_descargas != None:
                data = [{'id_orden_fk_descargas': descarga.id_orden_fk_descargas, 'date_created_descargas': descarga.date_created_descargas,
                        'fecha_recepcion_descargas': descarga.fecha_recepcion_descargas, 'ucl_operador_descargas': descarga.ucl_operador_descargas,
                        'cantidad_programada_descargas': descarga.cantidad_programada_descargas, 'producto_descargas': descarga.producto_descargas,
                        'tipo_descargas': descarga.tipo_descargas, 'estado_descargas': descarga.estado_descargas} for descarga in Mostrar_descargas]

                return jsonify({'descargas': data, 'pagination': str(pagination), 'total_pages':str(total_pages), 'mostrando':start_index,'cantidad':total ,'total_paginas':total_pages,'paginactual':page_num })

        else:
            flash("Datos no encontrados")
            return render_template('scaizen/descarga.html', descargas=None, pagination= None, total_pages=None, mostrando=None, productos_color = config.PRODUCTOS_COLOR_BY_NAME, PRODUCTOS_NAMES = config.PRODUCTOS_NAMES)
    else:
        return render_template('scaizen/descarga.html',descargas=None, pagination= None, total_pages=None,mostrando=None, productos_color = config.PRODUCTOS_COLOR_BY_NAME, PRODUCTOS_NAMES = config.PRODUCTOS_NAMES)



@app_scaizen.route('/ventas/carga', methods=['GET','POST']) 
@login_required
def planificacion_carga():
    config = GlobalConfig()
    page_num = request.form.get('page', 1, type=int)
    # Acceder a los datos del formulario utilizando request.form
    
    if  request.method == 'POST':
        fecha_inicio = request.form.get('selected_start')
        fecha_fin = request.form.get('selected_end')
        
        carga = Tabla_carga(fecha_inicio,fecha_fin, None, None,  None, None, None, None, None,None)
       

        start_index = (page_num - 1) * elementos_por_pagina + 1
        end_index = start_index + elementos_por_pagina

        Mostrar_carga, total =ModelTablas.cargas(db, carga,page_num,elementos_por_pagina)
        
        total_pages = total // elementos_por_pagina + (total % elementos_por_pagina > 0)
        print("==========================Pagina inicio", page_num, "Valores a omitir",start_index,"Total de elementos", total, "Total de paginas", total_pages, "Elementos por pagina",elementos_por_pagina)

        # Calcular el índice del último registro
        end_index = min(start_index + elementos_por_pagina, total)
        if end_index > total:
            end_index = total

        # Crear objeto paginable
        pagination = Pagination(page=page_num, total=total, per_page=elementos_por_pagina,
                                display_msg=f"Mostrando registros {start_index} - {end_index} de un total de <strong>({total})</strong>")
        print(Mostrar_carga)
        if Mostrar_carga !=None:
                data = [{'id_orden_fk_carga': carga.id_orden_fk_carga, 'date_created_carga': carga.date_created_carga,
                        'fecha_entrega_carga': carga.fecha_entrega_carga, 'ucl_operador_carga': carga.ucl_operador_carga,
                        'cantidad_programada_carga': carga.cantidad_programada_carga, 'producto_carga': carga.producto_carga,
                        'tipo_carga': carga.tipo_carga, 'estado_carga': carga.estado_carga} for carga in Mostrar_carga]

                return jsonify({'cargas': data, 'pagination': str(pagination), 'total_pages':str(total_pages), 'mostrando':start_index,'cantidad':total ,'total_paginas':total_pages,'paginactual':page_num })
        else:
            print("Datos no encontrados")
            return render_template('scaizen/carga.html',cargas=None, pagination= None, total_pages=None, mostrando=None,productos_color = config.PRODUCTOS_COLOR_BY_NAME, PRODUCTOS_NAMES = config.PRODUCTOS_NAMES)

    else:   
                return render_template('scaizen/carga.html',cargas= None, pagination= None, total_pages=None,mostrando=None,productos_color = config.PRODUCTOS_COLOR_BY_NAME, PRODUCTOS_NAMES = config.PRODUCTOS_NAMES)


#Reportes
@app_scaizen.route('/tanques/<int:id>', methods=['GET', 'POST'])
@login_required
def tanques(id):
    page_num = request.form.get('page', 1, type=int)

    if id == 1:
        titulo = "Reporte Histórico de Tanques"
    elif id == 2:
        titulo = "Reporte Diario por Tanques"
    elif id == 3: 
        titulo = "Reporte Mensual por Tanques"

    tipo_reporte =  id
    if  request.method == 'POST':
            
            start_index = (page_num - 1) * elementos_por_pagina + 1
            end_index = start_index + elementos_por_pagina

            Mostar_tanques, total =ModelTablas.tanques(db,page_num,elementos_por_pagina)
            print(Mostar_tanques)

            total_pages = total // elementos_por_pagina + (total % elementos_por_pagina > 0)
    
            # Calcular el índice del último registro
            end_index = min(start_index + elementos_por_pagina, total)
            if end_index > total:
                end_index = total
            # Crear objeto paginable
            pagination = Pagination(page=page_num, total=total, per_page=elementos_por_pagina,
                                    display_msg=f"Mostrando registros {start_index} - {end_index} de un total de <strong>({total})</strong>")
          
            if Mostar_tanques != None:
                data = [{'id_tanque': tanque.id_tanque, 'producto_tanque': tanque.producto_tanque, 
                         'tipo_venta_tanque': tanque.tipo_venta_tanque,'codigo_tanque':tanque.codigo_tanque} for tanque in Mostar_tanques]
                
                return jsonify({'value': tipo_reporte,'titulo': titulo,'tanques': data, 'pagination': str(pagination), 'total_pages':str(total_pages), 'mostrando':start_index,'cantidad':total ,'total_paginas':total_pages,'paginactual':page_num })
            else:
                    flash("Datos no encontrados")
                    return render_template('scaizen/tanques.html',value = tipo_reporte, titulo= titulo,tanques=None, pagination= None, total_pages=None, mostrando=None)
    else:
        return render_template('scaizen/tanques.html',value = tipo_reporte, titulo=titulo ,tanques=None, pagination= None, total_pages=None, mostrando=None)



## ELiminar ##
@app_scaizen.route('/mensual_tanques', methods=['GET', 'POST'])
@login_required
def mensual_tanques():
    #Ini - Cambio jul-25
    Componente = 'distribuidor/mensual_tanques'#checar o cambiar
    Descripcion = None
    Tipo_Evento = None
    #Fin - Cambio jul-25
    if request.method == 'POST':
        id_tanque = request.form.get('id_tanque')
        selectedId = request.form.get('selectedId')
        startDate = request.form.get('startDate')
        endDate = request.form.get('endDate')

        if id_tanque == "id_tanques":
            tanques_existentes = ModelTablas.numero_tanques(db)
            if tanques_existentes is not None:
                data = [{'id_tanque': cantidad_tanques.id_tanque, 'codigo_tanque': cantidad_tanques.codigo} for cantidad_tanques in tanques_existentes]
                return jsonify({'datos_tanque': data})
            else:
                return render_template('scaizen/orden_mes.html', tanques=None, informetanques=None)

        if selectedId and startDate and endDate:
            try:
                # Convertir las fechas del formato 'YYYY-MM-DD' a objetos datetime
                fecha_inicio = datetime.strptime(startDate, '%Y-%m-%d')
                fecha_fin = datetime.strptime(endDate, '%Y-%m-%d')
                # Generar lista de fechas entre fecha_inicio y fecha_fin
                fechas = []
                fecha_actual = fecha_inicio
                while fecha_actual <= fecha_fin:
                    fechas.append(fecha_actual.strftime('%Y-%m-%d'))
                    fecha_actual += timedelta(days=1)

                # Procesar cada fecha
                for fecha in fechas:
                    # Convertir la fecha a objetos datetime para el rango de tiempo
                    startDate1 = datetime.strptime(fecha, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
                    endDate1 = datetime.strptime(fecha, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
                    mensual_tanques = Tabla_batch_mensual_tanques(selectedId, startDate1, endDate1,  None, None, None, None, None, None, None, None, None, None, None, None, None, None)

                    total_mensual_tanques = ModelTablas.comercializadora_mensual_tanques(db, mensual_tanques)

                    if total_mensual_tanques:
                        data = [
                                {
                                    'fecha_start_batch': mensual.fecha_start_batch,
                                    'fecha_end_batch': mensual.fecha_end_batch,
                                    'numero_bol': mensual.numero_bol,
                                    'inicio_volumen_natural': mensual.inicio_volumen_natural,
                                    'inicio_volumen_neto': mensual.inicio_volumen_neto,
                                    'inicio_temperatura': mensual.inicio_temperatura,
                                    'recepcion_total_volumen_registros_descargas': mensual.recepcion_total_voluemn_registros_descargas,
                                    'recepcion_total_volumen_natural_descargas': mensual.recepcion_total_volumen_natural_descargas,
                                    'recepcion_total_volumen_neto_descargas': mensual.recepcion_total_volumen_neto_descargas,
                                    'recepcion_total_temperatura_descargas': mensual.recepcion_total_temperatura_descargas,
                                    'entrega_total_volumen_registros_cargas': mensual.entrega_total_volumen_registros_cargas,
                                    'entrega_total_volumen_natural_cargas': mensual.entrega_total_volumen_natural_cargas,
                                    'entrega_total_volumen_neto_cargas': mensual.entrega_total_volumen_neto_cargas,
                                    'entrega_total_temperatura_cargas': mensual.entrega_total_temperatura_cargas
                                } for mensual in total_mensual_tanques
                            ]
                        #Ini - Cambio jul-25
                        Descripcion = f'Obtención y recuperación de registros mensual de tanques periodo {fecha_inicio}-{fecha_fin}  '
                        Tipo_Evento = 3
                        EventosComercializador.add(
                            datetime.now(), current_user.Username, Tipo_Evento, Descripcion, Componente
                        )
                        #Fin - Cambio jul-25                
                        return jsonify({'diario': data, 'tanques': None, 'informetanques': None})                    
            except ValueError:
                return jsonify({'error': 'Formato de fecha inválido'}), 400
        
        # Si no se cumplen las condiciones, mostrar la plantilla de formulario vacío
        return render_template('scaizen/orden_mes.html', tanques=None, informetanques=None)
    
    # Si la solicitud no es POST, renderizar la plantilla
    return render_template('scaizen/orden_mes.html', tanques=None, informetanques=None)

@app_scaizen.route('/informe_de_tanque', methods=['GET','POST'])
@login_required
def informe_de_tanque():

    #Ini - Cambio jul-25
    Componente = 'distribuidor/consultar_ventas'#checar o cambiar
    Descripcion = None
    Tipo_Evento = None
    #Fin - Cambio jul-25

    if  request.method == 'POST':
        fecha  = request.form.get('selected_start')
        # Convertir la cadena de fecha a objeto datetime
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%dT%H:%M:%S.%fZ')
        # Añadir la hora "00:00:00"
        fecha_inicio_1 = fecha_obj.replace(hour=00, minute=00, second=00)
        fecha_obj_2 = datetime.strptime(fecha, '%Y-%m-%dT%H:%M:%S.%fZ')

        fecha_inicio_2 = fecha_obj_2.replace(hour=00, minute=2, second=00)

        print(fecha_inicio_1 ,fecha_inicio_2 )
        id_tanque = request.form.get('id_tanque')
        print(id_tanque )
        infotanque_inicio = Tabla_informetanque_dia_inicio(fecha_inicio_1,fecha_inicio_2,id_tanque, None, None, None, None)

        Medicion_dia_inicio = ModelTablas.informe_de_tanques_inicio(db, infotanque_inicio)
        
        print(Medicion_dia_inicio)
        
        fecha_obj_3 = datetime.strptime(fecha, '%Y-%m-%dT%H:%M:%S.%fZ')
        fecha_batch_1 = fecha_obj_3.replace(hour=00, minute=00, second=00)
        fecha_obj_4 = datetime.strptime(fecha, '%Y-%m-%dT%H:%M:%S.%fZ')
        fecha_batch_2 = fecha_obj_4.replace(hour=23, minute=59, second=59)
        print(fecha_batch_1,fecha_batch_2)
        #Por checar
        info_batch =batch_ucl_carga_descarga(fecha_batch_1,fecha_batch_2,id_tanque,None,None,None,None,None,None,None)

        inicio,batch,fin =  ModelTablas.informe_de_tanques_batch(db, info_batch )
        print(inicio)
        print(batch)
        print(fin)

        fecha_obj_5 = datetime.strptime(fecha, '%Y-%m-%dT%H:%M:%S.%fZ')
        fecha_fin_1 = fecha_obj_5.replace(hour=23, minute=58, second=59)
        fecha_obj_6 = datetime.strptime(fecha, '%Y-%m-%dT%H:%M:%S.%fZ')
        fecha_fin_2 = fecha_obj_6.replace(hour=23, minute=59, second=59)

        print(fecha_fin_1, fecha_fin_2)
        infotanque_fin = Tabla_informetanque_dia_fin(fecha_fin_1,fecha_fin_2 ,id_tanque, None, None, None,None  )
        Medicion_dia_fin  =  ModelTablas.informe_de_tanques_fin(db, infotanque_fin)
        print(Medicion_dia_fin)
        
        if Medicion_dia_inicio != None:
             
            data = [{'nivel_actual_fecha_actualizacion_informe': medicio_dia.nivel_actual_fecha_actualizacion_informe,
                     'volumen_natural_informe':medicio_dia.volumen_natural_informe,'volumen_neto_informe':medicio_dia.volumen_neto_informe,
                     'temperatura_informe':medicio_dia.temperatura_informe
                       } for medicio_dia in Medicion_dia_inicio]

            if inicio !=None:
                    data_2 = [{'nivel_actual_fecha_actualizacion_inicio': Medicion_inicio.nivel_actual_fecha_actualizacion_inicio,
                     'volumen_natural_inicio':Medicion_inicio.volumen_natural_inicio,'volumen_neto_inicio':Medicion_inicio.volumen_neto_inicio,
                     'temperatura_inicio':Medicion_inicio.temperatura_inicio                 
                       } for Medicion_inicio in inicio]
            if batch !=None:
                     data_3 = [{'id_batch': batch_1.id_batch,'volumen_natural_batch':batch_1.volumen_natural_batch,
                                'volumen_neto_batch':batch_1.volumen_neto_batch,'temperatura_batch':batch_1.temperatura_batch,
                                'tipo_batch':batch_1.tipo_batch,'totalizador_apertura_fecha_batch':batch_1.totalizador_apertura_fecha_batch,
                         
                       } for batch_1 in batch]        
            if fin !=None:
                    data_4 = [{'nivel_actual_fecha_actualizacion_fin': Medicion_fin.nivel_actual_fecha_actualizacion_fin,
                     'volumen_natural_fin':Medicion_fin.volumen_natural_fin,'volumen_neto_fin':Medicion_fin.volumen_neto_fin,
                     'temperatura_fin':Medicion_fin.temperatura_fin                 
                       } for Medicion_fin in fin]
            if Medicion_dia_fin !=None:
                    data_5 = [{'nivel_actual_fecha_actualizacion_informe': medicio_diafin.nivel_actual_fecha_actualizacion_informe,
                                        'volumen_natural_informe':medicio_diafin.volumen_natural_informe,'volumen_neto_informe':medicio_diafin.volumen_neto_informe,
                                        'temperatura_informe':medicio_diafin.temperatura_informe
                                        } for medicio_diafin in Medicion_dia_fin]

            #Ini - Cambio jul-25
            #Descripcion = f'Obtención y recuperación de registros mensual de tanques periodo {fecha_inicio_1}-{fecha_fin_1}  '
            #Tipo_Evento = 3
            #EventosDistribuidor.add(
            #    datetime.now(), current_user.Username, Tipo_Evento, Descripcion, Componente
            #)
            #Fin - Cambio jul-25                

            return jsonify({'medicion_dia': data,'inicio':data_2,'batch':data_3,'fin':data_4,'medicion_dia_fin':data_5})
        else:
            print("Datos no encontrados, intente de nuevo")
            return jsonify({'medicion_dia': None,'inicio':None,'batch':None,'fin':None,'medicion_dia_fin':None})
    else:   
            return render_template('scaizen/informe_tanques.html',informetanques=None)

def crear_tabla(pdf, x, y, diario, lectura_anterior_batch, lectura_posterior_batch, data_tanque_inico_fin, acumulado_post_entrega_descarga_nat, acumulado_post_entrega_descarga_neto, acumulado_post_entrega_carga_nat, acumulado_post_entrega_carga_neto):
    pdf.set_font("Arial", size=7)

    # Definir constantes y variables para la tabla
    subcell_width = 15
    cell_height = 5
    subheader_height = 4
    border_thickness = 0.5  # Grosor del borde (en mm)

    # Encabezados y sub-encabezados
    headers = [
        "Volumen Inicial del Tanque",
        "Volumen Recepción / Descargas (Recibido)",
        "Volumen Entrega / Cargas (Salidas)"
    ]
    subheaders = [
        ["Hora", "Vol.\n Nat", "Vol.\n Neto", "Temp", "UM", ""],
        ["#", "Vol.\n Nat", "Vol.\n Neto", "Temp", "UM", "Presión"],
        ["#", "Vol.\n Nat", "Vol.\n Neto", "Temp", "UM", "Presión"]
    ]

    header_colors = [(255, 222, 227), (133, 255, 133), (155, 155, 252)]
    subheader_colors = [(255, 200, 200), (200, 255, 200), (200, 200, 255)]

    # Calcular el ancho total de la tabla
    num_subheaders = len(subheaders[0])
    colspan_width = num_subheaders * subcell_width
    table_width = len(headers) * colspan_width

    # Posición x para centrar la tabla
    if x is None:
        page_width = pdf.w - pdf.r_margin - pdf.l_margin
        x = (page_width - table_width) / 2 + pdf.l_margin

    # Ajustar la posición x
    x -= 10

    # Establecer posición inicial
    pdf.set_xy(x, y if y is not None else pdf.get_y())

    # Dibujar encabezado principal
    for i, header in enumerate(headers):
        pdf.set_fill_color(*header_colors[i])
        pdf.set_font("Arial", style='B', size=7)
        pdf.cell(colspan_width, cell_height, header, 1, 0, 'C', 1)
    pdf.ln(cell_height)

    # Dibujar sub-encabezados
    pdf.set_xy(x, pdf.get_y())
    for color, subheader_row in zip(subheader_colors, subheaders):
        pdf.set_fill_color(*color)
        pdf.set_font("Arial", style='B', size=7)
        for item in subheader_row:
            pdf.cell(subcell_width, subheader_height, item, 1, 0, 'C', 1)
    pdf.ln(subheader_height)

    # Guardar posición actual
    start_y = pdf.get_y()

    # Primera fila
    if data_tanque_inico_fin:
        dato = data_tanque_inico_fin[0]
        fecha = dato.get('fecha', ['No disponible'])[0]  # Obtener el primer elemento de la lista
        fecha = str(fecha)  # Asegurarse de que sea una cadena

        # Separar la fecha de la hora
        try:
            _, hora = fecha.split(' ')
        except ValueError:
            hora = 'No disponible'

        fila = [
            hora,
            dato.get('vol_nat', 'No disponible'),
            dato.get('vol_neto', 'No disponible'),
            dato.get('temp', 'No disponible'),
            'UM04',
            '', '', '', '', '', '', '', '', '', '', '', '', ''
        ]
        pdf.set_xy(x, start_y)
        pdf.set_font("Arial", size=7)
        for dato in fila:
            pdf.cell(subcell_width, cell_height, str(dato), 1, 0, 'C')
        pdf.ln(cell_height)

        # Fila vacía
        fila_vacia = [''] * 18
        pdf.set_xy(x, pdf.get_y())
        pdf.set_font("Arial", size=7)
        for _ in fila_vacia:
            pdf.cell(subcell_width, cell_height, '', 1, 0, 'C')
        pdf.ln(cell_height)

        # Datos diarios
        if diario:
            for dato in diario:
                tipo = dato.get('tipo', 'No disponible')
                if tipo == "descarga":
                    fecha = dato.get('fecha_inicio', 'No disponible')
                    fecha = str(fecha)
                    try:
                         _, hora_intermedia_descarga = fecha.split(' ')
                    except ValueError:
                        hora_intermedia_descarga = 'No disponible'
                    fila = [
                        hora_intermedia_descarga,
                        '', '', '', '', '',      
                        dato.get('numero_bol', 'No disponible'),
                        dato.get('volumen_natural', 'No disponible'),
                        dato.get('volumen_neto', 'No disponible'),
                        dato.get('temperatura', 'No disponible'),
                        'UM04', '', '', '', '', '', '', ''
                    ]
                elif tipo == "carga":
                    fecha = dato.get('fecha_inicio', 'No disponible')
                    fecha = str(fecha)
                    try:
                         _, hora_intermedia_carga = fecha.split(' ')
                    except ValueError:
                        hora_intermedia_carga = 'No disponible'
                    fila = [
                        hora_intermedia_carga,
                        '', '', '', '', '',      
                        '', '', '', '', '', '', 
                        dato.get('numero_bol', 'No disponible'),
                        dato.get('volumen_natural', 'No disponible'),
                        dato.get('volumen_neto', 'No disponible'),
                        dato.get('temperatura', 'No disponible'),
                        'UM04', ''
                    ]

                pdf.set_xy(x, pdf.get_y())
                pdf.set_font("Arial", size=7)
                for dato in fila:
                    pdf.cell(subcell_width, cell_height, str(dato), 1, 0, 'C')
                pdf.ln(cell_height)

        # Fila vacía final
        fila_vacia = [''] * 18
        pdf.set_xy(x, pdf.get_y())
        pdf.set_font("Arial", size=7)
        for _ in fila_vacia:
            pdf.cell(subcell_width, cell_height, '', 1, 0, 'C')
        pdf.ln(cell_height)

        # Última fila
        if len(data_tanque_inico_fin) > 1:
            dato = data_tanque_inico_fin[-1]
            fecha = dato.get('fecha', 'No disponible')
            fecha = str(fecha)
            try:
                _, hora_fin = fecha.split(' ')
            except ValueError:
                hora_fin = 'No disponible'
            fila = [
                hora_fin,
                dato.get('vol_nat', 'No disponible'),
                dato.get('vol_neto', 'No disponible'),
                dato.get('temp', 'No disponible'),
                'UM04', '', '', '', '', '', '', '', '', '', '', '', '', ''
            ]
            pdf.set_xy(x, pdf.get_y())
            pdf.set_font("Arial", size=7)
            for dato in fila:
                pdf.cell(subcell_width, cell_height, str(dato), 1, 0, 'C')
            pdf.ln(cell_height)
    else:
        # Si no hay datos
        fila_vacia = ['No hay datos'] * 18
        pdf.set_xy(x, start_y)
        pdf.set_font("Arial", size=7)
        for dato in fila_vacia:
            pdf.cell(subcell_width, cell_height, str(dato), 1, 0, 'C')
        pdf.ln(cell_height)

    # Ajustar la posición para la nueva tabla
    pdf.ln(cell_height)
    y_nueva_tabla = pdf.get_y()
    x += 190  # Asegúrate de que esta posición se ajuste a tu diseño
    pdf.set_xy(x, y_nueva_tabla)

    # Definir los encabezados para la nueva tabla
    nuevos_headers = [
        " ",
        "Vol. Nat",
        "Vol. Net",
        "UM",
        "°C"
    ]
    nuevo_header_colors = [(200, 200, 200)] * 5

    num_nuevos_headers = len(nuevos_headers)
    colspan_width_nueva = subcell_width
    table_width_nueva = num_nuevos_headers * colspan_width_nueva

    # Dibujar encabezados de la nueva tabla
    #check_space_and_add_page(pdf, cell_height)
    pdf.set_font("Arial", style='B', size=8)
    for i, header in enumerate(nuevos_headers):
        pdf.set_fill_color(*nuevo_header_colors[i])
        pdf.cell(colspan_width_nueva, cell_height, str(header), 1, 0, 'C', 1)
    pdf.ln(cell_height)

    # Dibujar datos de la nueva tabla
    first_date = data_tanque_inico_fin[0]
    last_date = data_tanque_inico_fin[-1]
    datos_filas = [
        ["Vol Inicial", first_date.get('vol_nat', 'No disponible'), first_date.get('vol_neto', 'No disponible'), "UM04", ""],
        ["Recepción", acumulado_post_entrega_descarga_nat, acumulado_post_entrega_descarga_neto, "UM04", ""],
        ["Entrega", acumulado_post_entrega_carga_nat, acumulado_post_entrega_carga_neto, "UM04", ""],
        ["Vol. Existencias", "---", "---", "UM04", "---"],
        ["Vol. Final", last_date.get('vol_nat', 'No disponible'), last_date.get('vol_neto', 'No disponible'), "UM04", ""],
        ["Diferencia", "---", "---", "UM04", "---"]
    ]

    for fila in datos_filas:
        #check_space_and_add_page(pdf, cell_height)
        pdf.set_xy(x, pdf.get_y())
        for dato in fila:
            pdf.cell(colspan_width_nueva, cell_height, str(dato), 1, 0, 'C', 1)
        pdf.ln(cell_height)

def add_header(pdf, width, height,report_date):
        
    # Crear una instancia (aunque en este caso es una clase con solo atributos de clase)
    didipsa_instance = DIDIPSA()

    # Acceder a los atributos
    #print(didipsa_instance.RfcContribuyente)

    # Ajusta el grosor de la línea y el color del trazo
    pdf.set_line_width(1)
    pdf.set_draw_color(0, 0, 0)  # Color negro

    pdf.line(20, 20, width - 20, 20)
    
    # Agrega una imagen al encabezado
  
    # Añadir imagen al encabezado
    image_path = 'src/static/img/didipsa_HD.png'  # Ruta a la imagen
    pdf.image(image_path, x=20, y=5, w=50, h=10)

      # Establecer fuente y tamaño de texto
    pdf.set_font("Arial", style='B', size=7)

    # Coordenadas y texto
    header_text = "Versión del sistema "+str(didipsa_instance.Version)
    pdf.text(250, 10, header_text),#X y  Y

     #Izquierda
    pdf.text(20,  25, "RFC Contribuyente: "+str(didipsa_instance.RfcContribuyente))
    pdf.text(20,  30, "RFC Representante Legal: "+str(didipsa_instance.RfcRepresentanteLegal))
 
    pdf.text(20,  35, "Clave Instalación: "+ str(didipsa_instance.ClaveInstalacion))
    pdf.text(20,  40, "Número de contrato o asignación: "+ str(didipsa_instance.NumContratoOAsignacion))
    
    pdf.text(80,  35, "Carácter: "+ str(didipsa_instance.Caracter))
    pdf.text(120,  35, "Modalidad: "+ str(didipsa_instance.ModalidadPermiso))
    pdf.text(160, 35, "Número de Permiso: "+ str(didipsa_instance.NumPermiso))

    pdf.text(20,  50, "Descripción Instalación: "+ str(didipsa_instance.Descripcion_instalacion))
    pdf.text(20,  55, "Dirección: "+ str(didipsa_instance.Direccion_instalacion))
    pdf.text(190,  55, "Longitud: "+str(didipsa_instance.Geolocalizacion['GeolocalizacionLongitud']))
    pdf.text(240, 55, "Latitud: "+str(didipsa_instance.Geolocalizacion['GeolocalizacionLatitud']))

    pdf.text(20,60,"Fecha de reporte: "+str(report_date))
    pdf.text(60, 60, "Número de Pozos: "+ str(didipsa_instance.NumeroPozos))
    pdf.text(90, 60, "Número de Tanques: "+ str(didipsa_instance.NumeroTanques))
    pdf.text(120, 60, "Número Ducto Entrada/Salida: "+ str(didipsa_instance.NumeroDuctosTransporteDistribucion))
    pdf.text(180,  60, "Número Dispensarios: "+ str(didipsa_instance.NumeroDispensarios))
    now = datetime.now()
    current_datetime = now.strftime("%Y-%m-%d %H:%M")

    pdf.text(230,  60, "Fecha y Hora del Corte: "+str(current_datetime))

    pdf.text(210,  25, "RFC Proveedor del Sistema Informático: "+ str(didipsa_instance.RfcProveedor))
    pdf.text(210,  30, "RFC Proveedor de Equipos: "+ str(didipsa_instance.RfcProveedores[0]))
    
    pdf.set_font("Arial", size=7)
    pdf.text(120,  65, "")
    pdf.text(140, 75, " ")

    pdf.text(115,  90, " ")
    pdf.text(170,  100, " ")

    pdf.text(285, 90, "")
    pdf.text(390,  90, " ")
    pdf.text(555,  90, " ")

#Reportes
@app_scaizen.route('/reportes')
@login_required
def reporte():
    return render_template('user/permisos.html')


#Subreportes
@app_scaizen.route('/reportes/eventos', methods=['GET','POST'])
@login_required
def reporte_eventos():
    page_num = request.form.get('page', 1, type=int)
    
    if request.method == 'POST':
    
        fecha_inicio = request.form.get('selected_start')
        
        # Convertir la cadena de fecha a objeto datetime
        fecha_obj = datetime.strptime(fecha_inicio, '%Y-%m-%dT%H:%M:%S.%fZ')
        # Añadir la hora "00:00:00"
        inicio = fecha_obj.replace(hour=00, minute=00, second=00)

        # Convertir la cadena de fecha a objeto datetime
        fecha_obj_2 = datetime.strptime(fecha_inicio, '%Y-%m-%dT%H:%M:%S.%fZ')
        # Añadir la hora "00:00:00"
        fin = fecha_obj_2.replace(hour=23, minute=59, second=59)


        print(inicio)
        eventos = Tabla_eventos(inicio, fin,None, None, None, None, None,None )

        start_index = (page_num - 1) * elementos_por_pagina + 1
        end_index = start_index + elementos_por_pagina

        Mostrar_eventos, total = ModelTablas.eventos(db, eventos,page_num,elementos_por_pagina)

        total_pages = total // elementos_por_pagina + (total % elementos_por_pagina > 0)

        # Calcular el índice del último registro
        end_index = min(start_index + elementos_por_pagina, total)
        if end_index > total:
            end_index = total

        # Crear objeto paginable
        pagination = Pagination(page=page_num, total=total, per_page=elementos_por_pagina,
                                display_msg=f"Mostrando registros {start_index} - {end_index} de un total de <strong>({total})</strong>")
        print(total)
        print(Mostrar_eventos)
        if Mostrar_eventos != None:
             
            data = [{'id_eventos': eventos.id_eventos, 'fecha_eventos': eventos.fecha_eventos,
                        'nombre_eventos': eventos.nombre_eventos, 'mensaje_eventos': eventos.mensaje_eventos,
                        'proceso_eventos': eventos.proceso_eventos, 'tipo_eventos': eventos.tipo_eventos } for eventos in Mostrar_eventos]

            return jsonify({'eventos': data, 'pagination': str(pagination), 'total_pages':str(total_pages), 'mostrando':start_index,'cantidad':total ,'total_paginas':total_pages,'paginactual':page_num })
        else:
             flash("Datos no encontrados, intente de nuevo")
             return render_template('scaizen/eventos.html',eventos=None, pagination= None, total_pages=None, mostrando=None)
    else:   
         return render_template('scaizen/eventos.html',eventos=None, pagination= None, total_pages=None, mostrando=None)

 

@app_scaizen.route('/reportes/orden_del_dia',methods=['GET','POST'])
@login_required
def reporte_ordendia():
    page_num = request.form.get('page', 1, type=int)

    if request.method == 'POST':
        
        fecha_inicio = request.form.get('selected_start')
        fecha_fin = request.form.get('selected_start')
        print(fecha_fin)
        diarios = Tabla_operaciones_diarias(fecha_inicio,fecha_fin, None,None, None, None, None,None, None,None, None,  None,None,  None)

        print(diarios.fecha_fin_busqueda+"fechas")
        start_index = (page_num - 1) * elementos_por_pagina + 1
        end_index = start_index + elementos_por_pagina


        print("hola")
        Mostrar_operaciones, total = ModelTablas.operaciones_diarias_cargas(db, diarios,page_num,elementos_por_pagina)
 
        total_pages = total // elementos_por_pagina + (total % elementos_por_pagina > 0)

        # Calcular el índice del último registro
        end_index = min(start_index + elementos_por_pagina, total)
        if end_index > total:
            end_index = total

        # Crear objeto paginable
        pagination = Pagination(page=page_num, total=total, per_page=elementos_por_pagina,
                                display_msg=f"Mostrando registros {start_index} - {end_index} de un total de <strong>({total})</strong>")
        print(total)
        print(Mostrar_operaciones)
        if Mostrar_operaciones != None:
             data = [{'id_orden_fk_diario': operacion.id_orden_fk_diario, 'date_created_dia_diario': operacion.date_created_dia_diario,
                        'date_updated_diario': operacion.date_updated_diario, 'nombre_comercial_diario': operacion.nombre_comercial_diario,
                        'ucl_operador_diario': operacion.ucl_operador_diario, 'cantidad_programada_diario': operacion.cantidad_programada_diario,
                        'volumen_natural_diario': operacion.volumen_natural_diario, 'volumen_neto_diario': operacion.volumen_neto_diario, 
                        'temperatura_promedio_diario':operacion.temperatura_promedio_diario,'producto_diario':operacion.producto_diario, 'tipo_diario':operacion.tipo_diario,
                         'estado_diario':operacion.estado_diario } for operacion in Mostrar_operaciones]

             return jsonify({'operaciones': data, 'pagination': str(pagination), 'total_pages':str(total_pages), 'mostrando':start_index,'cantidad':total ,'total_paginas':total_pages,'paginactual':page_num })
         
        else:
             flash("Datos no encontrados, intente de nuevo")
             return render_template('scaizen/eventos.html',operaciones=None, pagination= None, total_pages=None, mostrando=None)

    else:  
        return render_template('scaizen/orden_dia.html',operaciones=None, pagination= None, total_pages=None, mostrando=None)



@app_scaizen.route('/reportes/orden_del_mes',methods=['GET','POST'])
@login_required
def reporte_ordenmes():
    page_num = request.form.get('page', 1, type=int)

    if request.method == 'POST':
        
        fecha_inicio = request.form.get('selected_start')
        fecha_fin = request.form.get('selected_end')
        #print(fecha_fin)
        diarios = Tabla_operaciones_mensuales(fecha_inicio,fecha_fin, None,None, None, None, None,None, None,None, None,  None,None,  None)

        #print(diarios.fecha_fin_busqueda+"fechas")
        start_index = (page_num - 1) * elementos_por_pagina + 1
        end_index = start_index + elementos_por_pagina


        Mostrar_operaciones, total = ModelTablas.operaciones_mensuales_cargas(db, diarios,page_num,elementos_por_pagina)
 
        total_pages = total // elementos_por_pagina + (total % elementos_por_pagina > 0)

        # Calcular el índice del último registro
        end_index = min(start_index + elementos_por_pagina, total)
        if end_index > total:
            end_index = total

        # Crear objeto paginable
        pagination = Pagination(page=page_num, total=total, per_page=elementos_por_pagina,
                                display_msg=f"Mostrando registros {start_index} - {end_index} de un total de <strong>({total})</strong>")
        if Mostrar_operaciones != None:
             data = [{'id_orden_fk_diario': operacion.id_orden_fk_diario, 'date_created_dia_diario': operacion.date_created_dia_diario,
                        'date_updated_diario': operacion.date_updated_diario, 'nombre_comercial_diario': operacion.nombre_comercial_diario,
                        'ucl_operador_diario': operacion.ucl_operador_diario, 'cantidad_programada_diario': operacion.cantidad_programada_diario,
                        'volumen_natural_diario': operacion.volumen_natural_diario, 'volumen_neto_diario': operacion.volumen_neto_diario, 
                        'temperatura_promedio_diario':operacion.temperatura_promedio_diario,'producto_diario':operacion.producto_diario, 'tipo_diario':operacion.tipo_diario,
                         'estado_diario':operacion.estado_diario } for operacion in Mostrar_operaciones]

             return jsonify({'operaciones': data, 'pagination': str(pagination), 'total_pages':str(total_pages), 'mostrando':start_index,'cantidad':total ,'total_paginas':total_pages,'paginactual':page_num })
         
        else:
             flash("Datos no encontrados, intente de nuevo")
             return render_template('scaizen/eventos.html',operaciones=None, pagination= None, total_pages=None, mostrando=None)

    else:  
        return render_template('scaizen/orden_mes.html',operaciones=None, pagination= None, total_pages=None, mostrando=None)

#Usuarios
@app_scaizen.route('/usuarios')
@login_required
def usuarios():
    return render_template('user/permisos.html')

#subusuarios
@app_scaizen.route('/usuarios/perfiles',methods=['GET','POST'])
@login_required
def usuarios_perfiles():
    page_num = request.form.get('page', 1, type=int)
    if  request.method == 'POST':
        elementos_por_pagina = 10
        start_index = (page_num - 1) * elementos_por_pagina + 1
        end_index = start_index + elementos_por_pagina
  
        perfiles, total = ModelTablas.rol_perfiles(db)
        print(perfiles)

        total_pages = total // elementos_por_pagina + (total % elementos_por_pagina > 0)
 
        # Calcular el índice del último registro
        end_index = min(start_index + elementos_por_pagina, total)
        if end_index > total:
            end_index = total
        # Crear objeto paginable
        pagination = Pagination(page=page_num, total=total, per_page=elementos_por_pagina,
                                display_msg=f"Mostrando registros {start_index} - {end_index} de un total de <strong>({total})</strong>")
        if perfiles !=None:
                data = [{'id_roll': perfil.id_roll, 'nombre_roll': perfil.nombre_roll, 
                        'status_roll': perfil.status_roll} for perfil in perfiles]
                
                return jsonify({'perfiles': data, 'pagination': str(pagination), 'total_pages':str(total_pages), 'mostrando':start_index,'cantidad':total ,'total_paginas':total_pages,'paginactual':page_num })
        else:
            print("Datos no encontrados")
            return render_template('scaizen/perfiles.html',perfil=None, pagination= None, total_pages=None, mostrando=None)
    else:
        return render_template('scaizen/perfiles.html',perfil=None, pagination= None, total_pages=None, mostrando=None)


@app_scaizen.route('/usuarios/perfiles/registrar',methods=['GET','POST'])
@login_required
def registrar_perfil():
    if  request.method == 'POST':
        fecha_actual  = request.form.get('horaActual')
        fecha_update  = request.form.get('horaActual')
        id_user_creator = request.form.get('id_user_creator')

        descripcion  = request.form.get('descripcion')
        nombre  = request.form.get('nombre')
        insertar = Alta_Roles(fecha_actual,fecha_update,id_user_creator ,None,None ,descripcion,nombre,None)
        Alta_perfil=ModelTablas.rol_alta(db,insertar)
        print(fecha_actual,fecha_update,id_user_creator,descripcion,nombre)

        if Alta_perfil !=None:
            flash("Exito al registro")
            return render_template('scaizen/registrar_perfil.html')
        else:
            flash("Error al registro")
            return render_template('scaizen/registrar_perfil.html')     
    else:
        return render_template('scaizen/registrar_perfil.html')
 

@app_scaizen.route('/usuarios/crear_usuarios',methods=['GET','POST'])
@login_required
def usuarios_crear():
   
    return render_template('scaizen/crear_perfil.html')
 
#Seccion de Distribuidor
@app_scaizen.route('/distribuidor/venta/Alta', methods=['POST', 'GET'])
@login_required
def distribuidor_venta_alta():
    if request.method == 'POST':
        id_cliente = request.form.get('id_cliente')

        if id_cliente == "id_cliente":
            # Obtener datos de clientes existentes
            clientes_existentes = ModelTablas.numero_clientes(db)
            estaciones_existentes = ModelTablas.numero_estaciones(db)
            proveedores_existentes = ModelTablas.numero_proveedores(db)
            if clientes_existentes is not None and estaciones_existentes is not None and proveedores_existentes is not None:
                data = [{'id_cliente': clientes.id_cliente, 'codigo_cliente': clientes.codigo_cliente} for clientes in clientes_existentes]
                data_2 = [{'id_tanque': estaciones.id_estacion, 'codigo_estacion': estaciones.codigo_estacion} for estaciones in estaciones_existentes]
                data_3 = [{'id_proveedor': proveedores.id_proveedor, 'codigo_proveedor': proveedores.codigo_proveedor} for proveedores in proveedores_existentes]

                return jsonify({'datos_cliente': data  ,'datos_estaciones': data_2,'datos_proveedores':data_3})
            # Si no hay datos de clientes ni estaciones, renderizar el template
            return render_template('scaizen/comercializador_venta_orden_alta.html')

        # Si hay datos en el formulario, procesar la venta
        proveedor = request.form.get('proveedor')
        transport = request.form.get('transport')
        cliente = request.form.get('cliente')
        producto = request.form.get('producto')
        cantidad_programada = request.form.get('cantidad_programada')
        autotanque = request.form.get('autotanque')
        datepicker_start1 = request.form.get('datepicker_start1')
        Costo = request.form.get('Costo')
        estatus = "Cerrado"
        informacion = request.form.get('informacion')
        if proveedor and producto and cantidad_programada and autotanque and datepicker_start1:
            print("Todo bien")
            if transport == None:
                distribuidor_venta = Tabla_distribuidor_venta(proveedor,None, cliente, producto, cantidad_programada, autotanque, datepicker_start1, Costo, estatus, informacion)
            elif cliente == None:
                distribuidor_venta = Tabla_distribuidor_venta(proveedor,transport, None, producto, cantidad_programada, autotanque, datepicker_start1, Costo, estatus, informacion)
            distribuidor_venta_consulta = ModelTablas.create_distribuidor_venta(db, distribuidor_venta)
            if distribuidor_venta_consulta:
                return jsonify({'estatus': True, 'status': 'success'}), 201
            else:
                return jsonify({'estatus': False, 'status': 'error'}), 500
    else:
    # Si la solicitud no es POST, también se debe manejar el caso GET (podrías querer devolver algo en este caso)
        return render_template('scaizen/comercializador_venta_orden_alta.html')


@app_scaizen.route('/distribuidor/venta/Consultar', methods=['POST', 'GET'])
@login_required
def distribuidor_venta_consultar():
    page_num = request.form.get('page', 1, type=int)
    # Acceder a los datos del formulario utilizando request.form
    
    if  request.method == 'POST':
        cancelar = request.form.get('cancelar')
        mostrar = request.form.get('mostrar')
        id = request.form.get('id')
        if mostrar == 'mostrar':
                fecha_inicio = request.form.get('selected_start')
                fecha_fin = request.form.get('selected_end')
                
                consultar_ventas = Tabla_distribuidor_venta_consultar(fecha_inicio,fecha_fin,None, None, None, None, None, None, None, None, None, None, None)

                elementos_por_pagina = 10
                start_index = (page_num - 1) * elementos_por_pagina + 1
                end_index = start_index + elementos_por_pagina


                Mostrar_consultar_ventas, total =ModelTablas.consultar_distribuidor_ventas(db,consultar_ventas,page_num,elementos_por_pagina)
                print(total)
                total_pages = total // elementos_por_pagina + (total % elementos_por_pagina > 0)
                # Calcular el índice del último registro
                end_index = min(start_index + elementos_por_pagina, total)
                if end_index > total:
                    end_index = total

                # Crear objeto paginable
                pagination = Pagination(page=page_num, total=total, per_page=elementos_por_pagina,
                                        display_msg=f"Mostrando registros {start_index} - {end_index} de un total de <strong>({total})</strong>")

                if Mostrar_consultar_ventas !=None:
                        data = [{'id':consultas.id ,'fecha':consultas.fecha,'id_proveedor':consultas.id_proveedor ,'id_estacion': consultas.id_estacion,'id_cliente':consultas.id_cliente,
                                'tipo_producto':consultas.tipo_producto,'cantidad':consultas.cantidad,'autotanque':consultas.autotanque,
                                'costo':consultas.costo,'estatus':consultas.estatus,'informacion':consultas.informacion} for consultas in Mostrar_consultar_ventas]

                        #Ini - Cambio jul-25
                        # Registrar el evento de consultar venta
                        descripcion_evento = f"Consultar venta de las fechas: {fecha_inicio} al {fecha_fin}."
                        identificacion_componente_alarma = "Consultar venta"
                        EventosDistribuidor.add(
                            datetime.now(), current_user.Username, 99, descripcion_evento, identificacion_componente_alarma
                        )
                        #Fin - Cambio jul-25

                        return jsonify({'consultas_distribuidor': data, 'pagination': str(pagination), 'total_pages':str(total_pages), 'mostrando':start_index,'cantidad':total ,'total_paginas':total_pages,'paginactual':page_num })
                else:                   
                    return render_template('scaizen/distribuidor_venta_orden_consultar.html',cargas=None, pagination= None, total_pages=None, mostrando=None)
        elif cancelar == 'cancelar':
            try:
                cancelar_1 = Cancelar_Venta(id)
                venta_cancelar = ModelTablas.venta_cancelada(db, cancelar_1)
                
                if venta_cancelar:
                    return jsonify({'estatus': True, 'status': 'success'}), 200
                else:
                    return jsonify({'estatus': False, 'status': 'error'}), 500
            except Exception as e:
                return jsonify({'estatus': False, 'status': 'error', 'message': str(e)}), 500

    return render_template('scaizen/distribuidor_venta_orden_consultar.html')


@app_scaizen.route('Comercializador/Reportes/diario_tanques', methods=['GET', 'POST'])
@login_required
def comercializadora_diario_tanques():
    id_tanque = request.form.get('id_tanque')
    selectedId = request.form.get('selectedId')
    startDate = request.form.get('startDate')

    if request.method == 'POST':
        print(startDate)

        if id_tanque == "id_tanques":
            tanques_existentes = ModelTablas.numero_tanques(db)
            if tanques_existentes is not None:
                data = [{'id_tanque': cantidad_tanques.id_tanque, 'codigo_tanque': cantidad_tanques.codigo} for cantidad_tanques in tanques_existentes]
                return jsonify({'datos_tanque': data})
            else:
                return render_template('scaizen/informe_tanques.html', tanques=None, informetanques=None)
        if selectedId is not None and startDate is not None:
            try:
                # Intenta analizar la fecha en el formato esperado
                fecha_obj = datetime.strptime(startDate, '%Y-%m-%dT%H:%M:%S%z')
                # Añadir la hora "00:00:00" al inicio
                startDate1 = fecha_obj.replace(hour=0, minute=0, second=0)
                # Establecer el final del día
                endDate1 = fecha_obj.replace(hour=23, minute=59, second=0)
                
                busqueda_tanque = Tabla_batch_diario_tanques(selectedId, startDate1, endDate1, None, None, None, None, None, None, None, None)
                diario_tanque, total_tanques = ModelTablas.comercializadora_diario_tanques(db, busqueda_tanque)
                
                if diario_tanque is not None:
                    data = [{'numero_bol': diario.numero_bol, 'fecha_inicio': diario.fecha_inicio,
                            'fecha_termino': diario.fecha_termino, 'volumen_natural': diario.volumen_natural,
                            'volumen_neto': diario.volumen_neto, 'temperatura': diario.temperatura,
                            'densidad': diario.densidad, 'tipo': diario.tipo} for diario in diario_tanque]
                    data_total = [{'total_volumen_natural_carga': total.total_volumen_natural_carga, 'total_volumen_neto_carga': total.total_volumen_neto_carga,
                                   'total_volumen_natural_descarga':total.total_volumen_natural_descarga,
                                   'total_volumen_neto_descarga':total.total_volumen_neto_descarga, 'temperaturas_promedio_carga_1':total.temperaturas_promedio_carga_1,
                                   'temperaturas_promedio_descarga_1':total.temperaturas_promedio_descarga_1} for total in total_tanques]
                    
                    return jsonify({'diario': data, 'total_tanques': data_total, 'tanques': None, 'informetanques': None})
                else:
                    return render_template('scaizen/informe_tanques.html', tanques=None, informetanques=None)
            except ValueError:
                return jsonify({'error': 'Formato de fecha inválido'}), 400
    else:
        return render_template('scaizen/informe_tanques.html', tanques=None, informetanques=None)

#Seccion catalogo
@app_scaizen.route('/Catalogo/cliente/Alta', methods=['POST', 'GET'])
@login_required
def catalogo_cliente_alta():
    with VerificarPermisosUsuario("ClienteAlta", current_user.RolPerms) as contexto:
        if contexto is False:  # No tiene permisos
            return redirect("/scaizen/")
        
    if request.method == 'POST':
            with VerificarPermisosUsuario("ClienteAlta", current_user.RolPerms) as contexto:
                if contexto is False:  # No tiene permisos
                    return jsonify({'error':'El usuario actual no tiene los permisos para ejecutar esta accion.','action':'redirect'})
            codigo = request.form.get('codigo')
            nombre_comercial = request.form.get('nombre_comercial')
            razon = request.form.get('razon')
            rfc = request.form.get('rfc')
            regimen = request.form.get('regimen')
            direccion = request.form.get('direccion')
            cod_pos = request.form.get('cod_pos')
            telefono = request.form.get('telefono')
            email = request.form.get('email')
            informacion = request.form.get('informacion')
 
            # Crear una instancia de Tabla_User con los datos recibidos
            crear_cliente = Tabla_Cliente(codigo, nombre_comercial, razon, rfc, regimen, direccion, cod_pos, telefono, email, informacion)
            # Llamar al método create_user y obtener el resultado
            Alta_cliente = ModelTablas.create_client(db, crear_cliente)
            if Alta_cliente:
                #Ini - Cambio jul-25
                # Registrar el evento de alta cliente
                descripcion_evento = f"Alta de cliente: {nombre_comercial}."
                identificacion_componente_alarma = "Alta cliente"
                EventosComercializador.add(
                    datetime.now(), current_user.Username, 88, descripcion_evento, identificacion_componente_alarma
                )
                #Fin - Cambio jul-25
                # Retorna un mensaje JSON si la inserción fue exitosa
                return jsonify({'estatus': True, 'status': 'success'}), 201
            else:
                # Retorna un mensaje JSON si la inserción falló
                return jsonify({'estatus': False, 'status': 'error'}), 500
        
    else:
          return render_template('scaizen/catalogo_cliente_alta.html')
    

@app_scaizen.route('/Catalogo/cliente/Consultar', methods=['POST', 'GET'])
@login_required
def catalogo_cliente_consultar():
    with VerificarPermisosUsuario("ClienteConsultar", current_user.RolPerms) as contexto:
        if contexto is False:  # No tiene permisos
            return redirect("/scaizen/")
        
    page_num = request.form.get('page', 1, type=int)

    if request.method == 'POST':
        with VerificarPermisosUsuario("ClienteConsultar", current_user.RolPerms) as contexto:
                if contexto is False:  # No tiene permisos
                    return jsonify({'error':'El usuario actual no tiene los permisos para ejecutar esta accion.','action':'redirect'})
        id_cliente = request.form.get('id_cliente')
        id = request.form.get('id')

        eliminar = request.form.get('eliminar')

        if id_cliente and not eliminar:
            elementos_por_pagina = 10
            start_index = (page_num - 1) * elementos_por_pagina + 1
            end_index = start_index + elementos_por_pagina
            # Obtener datos de clientes existentes
            #clientes_existentes, total = ModelTablas.consulta_clientes(db,page_num,elementos_por_pagina)
            #clientes_existentes, total = cv.ClienteCV.select_for_pagination(page_num,elementos_por_pagina)
            clientes_existentes, total = cv.ClienteCV.select_given_between_date_for_pagination(page_num,elementos_por_pagina)

            print("aqui")
            print(total)
            total_pages = total // elementos_por_pagina + (total % elementos_por_pagina > 0)

            # Calcular el índice del último registro
            end_index = min(start_index + elementos_por_pagina, total)
            if end_index > total:
                end_index = total

            # Crear objeto paginable
            pagination = Pagination(page=page_num, total=total, per_page=elementos_por_pagina,
                                    display_msg=f"Mostrando registros {start_index} - {end_index} de un total de <strong>({total})</strong>")
            if clientes_existentes:
                data = clientes_existentes
                user_perms = []
                if config.CHECK_USER_PERM("ClienteEditar",current_user.RolPerms): user_perms.append("ClienteEditar")
                if config.CHECK_USER_PERM("ClienteEliminar",current_user.RolPerms): user_perms.append("ClienteEliminar")

                #Ini - Cambio jul-25
                # Registrar el evento de Consultar cliente
                descripcion_evento = f"Consultar clientes."
                identificacion_componente_alarma = "Consultar cliente"
                EventosComercializador.add(
                    datetime.now(), current_user.Username, 99, descripcion_evento, identificacion_componente_alarma
                )
                #Fin - Cambio jul-25

                return jsonify({'datos_cliente_consulta': data, 'pagination': str(pagination), 'total_pages':str(total_pages), 'mostrando':start_index,
                                'cantidad':total ,'total_paginas':total_pages,'paginactual':page_num, 'user_perms':user_perms })
        elif id and eliminar == "eliminar":
            with VerificarPermisosUsuario("ClienteEliminar", current_user.RolPerms) as contexto:
                if contexto is False:  # No tiene permisos
                    return redirect("/scaizen/")
            try:
                delete = Eliminar_Cliente(id)
                clientes_eliminar = ModelTablas.eliminar_clientes(db, delete)
                
                if clientes_eliminar:
                    #Ini - Cambio jul-25
                    # Registrar el evento de eliminar cliente
                    descripcion_evento = f"Eliminar cliente: {id}."
                    identificacion_componente_alarma = "Eliminar cliente"
                    EventosComercializador.add(
                        datetime.now(), current_user.Username, 66, descripcion_evento, identificacion_componente_alarma
                    )
                    #Fin - Cambio jul-25
                    return jsonify({'estatus': True, 'status': 'success'}), 200
                else:
                    return jsonify({'estatus': False, 'status': 'error'}), 500
            except Exception as e:
                return jsonify({'estatus': False, 'status': 'error', 'message': str(e)}), 500

    # Si es una solicitud GET o no se cumple la condición POST
    # Renderiza el template sin datos específicos de clientes
    return render_template('scaizen/catalogo_cliente_consultar.html')


@app_scaizen.route('/Catalogo/cliente/Consultar/Editar', methods=['POST', 'GET'])
@login_required
def catalogo_cliente_editar():
    with VerificarPermisosUsuario("ClienteEditar", current_user.RolPerms) as contexto:
        if contexto is False:  # No tiene permisos
            return redirect("/scaizen/")
    if request.method == 'POST':
        with VerificarPermisosUsuario("ClienteEditar", current_user.RolPerms) as contexto:
                if contexto is False:  # No tiene permisos
                    return jsonify({'error':'El usuario actual no tiene los permisos para ejecutar esta accion.','action':'redirect'})
        # Extrae datos del formulario
        csrf_token = request.form.get('csrf_token')  # Si usas CSRF protection, valida el token aquí
        id_t = request.form.get('actualizar')

        if id_t:
            # Consultar cliente específico
            especifico = Tabla_Cliente_actualizar(id_t, None, None, None, None, None, None, None, None, None, None, None)
            clientes_especifico = ModelTablas.consulta_clientes_especifico(db, especifico)

            if clientes_especifico:
                data = [{'id_cliente': cliente.id,
                         'codigo': cliente.codigo,
                         'nombre_comercial': cliente.nombre_comercial,
                         'razon': cliente.razon,
                         'rfc': cliente.rfc,
                         'regimen': cliente.regimen,
                         'direccion': cliente.direccion,
                         'cod_pos': cliente.cod_pos,
                         'telefono': cliente.telefono,
                         'email': cliente.email,
                         'informacion': cliente.informacion
                         } for cliente in clientes_especifico]
                return jsonify({'datos_cliente_especifico': data})
            else:
                return jsonify({'estatus': False, 'status': 'no_data'}), 404

        codigo = request.form.get('codigo')
        nombre_comercial = request.form.get('nombre_comercial')
        razon = request.form.get('razon')
        rfc = request.form.get('rfc')
        regimen = request.form.get('regimen')
        direccion = request.form.get('direccion')
        cod_pos = request.form.get('cod_pos')
        telefono = request.form.get('telefono')
        email = request.form.get('email')
        informacion = request.form.get('informacion')
        editar = request.form.get('editar')
        actualizar_id = request.form.get('actualizar_id')
        if editar:
            actualizar_cliente = Tabla_Cliente_actualizar_update(actualizar_id,codigo, nombre_comercial, razon, rfc, regimen, direccion, cod_pos, telefono, email, informacion)
            exito_editar = ModelTablas.update_client(db, actualizar_cliente)

            if exito_editar:
                #Ini - Cambio jul-25
                # Registrar el evento de editar cliente
                descripcion_evento = f"Editar cliente: {nombre_comercial}."
                identificacion_componente_alarma = "Editar cliente"
                EventosComercializador.add(
                    datetime.now(), current_user.Username, 77, descripcion_evento, identificacion_componente_alarma
                )
                #Fin - Cambio jul-25
                return jsonify({'estatus': True, 'status': 'success'}), 200
            else:
                return jsonify({'estatus': False, 'status': 'error'}), 500

    return render_template('scaizen/catalogo_cliente_editar.html')

@app_scaizen.route('/Catalogo/Proveedor/Alta', methods=['POST', 'GET'])
@login_required
def catalogo_proveedor_alta():
    with VerificarPermisosUsuario("ProveedorAlta", current_user.RolPerms) as contexto:
        if contexto is False:  # No tiene permisos
            return redirect("/scaizen/")
    if request.method == 'POST':
        with VerificarPermisosUsuario("ProveedorAlta", current_user.RolPerms) as contexto:
                if contexto is False:  # No tiene permisos
                    return jsonify({'error':'El usuario actual no tiene los permisos para ejecutar esta accion.','action':'redirect'})
        codigo = request.form.get('codigo')
        nombre_comercial = request.form.get('nombre_comercial')
        razon = request.form.get('razon')
        rfc = request.form.get('rfc')
        direccion = request.form.get('direccion')
        telefono = request.form.get('telefono')
        email = request.form.get('email')
        informacion = request.form.get('informacion')

        crear_proveedor = Tabla_Proveedores(codigo,nombre_comercial,razon,rfc,direccion,telefono,email,informacion)
        Alta_proveedor = ModelTablas.create_proveedor(db, crear_proveedor)
        # Llamar al método create_user y obtener el resultado
        if Alta_proveedor:
            #Ini - Cambio jul-25
            # Registrar el evento de alta proveedor
            descripcion_evento = f"Alta de proveedor: {nombre_comercial}."
            identificacion_componente_alarma = "Alta proveedor"
            EventosComercializador.add(
                datetime.now(), current_user.Username, 88, descripcion_evento, identificacion_componente_alarma
            )
            #Fin - Cambio jul-25
            # Retorna un mensaje JSON si la inserción fue exitosa
            return jsonify({'estatus': True, 'status': 'success'}), 201
        else:
            # Retorna un mensaje JSON si la inserción falló
            return jsonify({'estatus': False, 'status': 'error'}), 500
    else:
        return render_template('scaizen/catalogo_proveedor_alta.html')

@app_scaizen.route('/Catalogo/Proveedor/Consulta', methods=['POST', 'GET'])
@login_required
def catalogo_proveedor_consultar():
    with VerificarPermisosUsuario("ProveedorConsultar", current_user.RolPerms) as contexto:
        if contexto is False:  # No tiene permisos
            return redirect("/scaizen/")
        
    page_num = request.form.get('page', 1, type=int)

    if request.method == 'POST':
        with VerificarPermisosUsuario("ProveedorConsultar", current_user.RolPerms) as contexto:
            if contexto is False:  # No tiene permisos
                return jsonify({'error':'El usuario actual no tiene los permisos para ejecutar esta accion.','action':'redirect'})
        id_proveedor = request.form.get('id_cliente')


        eliminar = request.form.get('eliminar')
        id = request.form.get('id')


        if id_proveedor == "id_cliente":
            elementos_por_pagina = 10
            start_index = (page_num - 1) * elementos_por_pagina + 1
            end_index = start_index + elementos_por_pagina


            # Obtener datos de clientes existentes
            #proveedor_existentes,total = ModelTablas.consulta_proveedores(db,page_num,elementos_por_pagina)
            proveedor_existentes,total =  cv.ProveedorCV.select_given_between_date_for_pagination(page_num,elementos_por_pagina)
            total_pages = total // elementos_por_pagina + (total % elementos_por_pagina > 0)

            # Calcular el índice del último registro
            end_index = min(start_index + elementos_por_pagina, total)
            if end_index > total:
                end_index = total

            # Crear objeto paginable
            pagination = Pagination(page=page_num, total=total, per_page=elementos_por_pagina,
                                    display_msg=f"Mostrando registros {start_index} - {end_index} de un total de <strong>({total})</strong>")

            if proveedor_existentes is not None:
                """
                data = [{'Id_proveedor': proveedor.id,
                         'codigo': proveedor.codigo,
                         'nombre_comercial': proveedor.nombre_comercial,
                         'razon': proveedor.razon,
                         'rfc': proveedor.rfc,
                         'direccion': proveedor.direccion,
                         'telefono': proveedor.telefono,
                         'email': proveedor.email,
                         'informacion': proveedor.informacion
                         } for proveedor in proveedor_existentes]
                """
                data = proveedor_existentes
                user_perms = []
                if config.CHECK_USER_PERM("ProveedorEditar",current_user.RolPerms): user_perms.append("ProveedorEditar")
                if config.CHECK_USER_PERM("ProveedorEliminar",current_user.RolPerms): user_perms.append("ProveedorEliminar")
                
                #Ini - Cambio jul-25
                # Registrar el evento de Consultar proveedores
                descripcion_evento = f"Consultar lista de Proveedores."
                identificacion_componente_alarma = "Consultar proveedores"
                EventosComercializador.add(
                    datetime.now(), current_user.Username, 99, descripcion_evento, identificacion_componente_alarma
                )
                #Fin - Cambio jul-25
                
                return jsonify({'datos_proveedor_consulta': data, 'pagination': str(pagination), 'total_pages':str(total_pages), 'mostrando':start_index,
                                'cantidad':total ,'total_paginas':total_pages,'paginactual':page_num, 'user_perms':user_perms })

        elif id and eliminar == "eliminar":
            with VerificarPermisosUsuario("ProveedorEliminar", current_user.RolPerms) as contexto:
                if contexto is False:  # No tiene permisos
                    return redirect("/scaizen/")
            try:
                delete = EliminarProveedor(id)
                proveedor_eliminar = ModelTablas.eliminar_proveedor(db, delete)
                
                if proveedor_eliminar:
                    #Ini - Cambio jul-25
                    # Registrar el evento de eliminar proveedor
                    descripcion_evento = f"Eliminar proveedor: {id}."
                    identificacion_componente_alarma = "Eliminar proveedor"
                    EventosComercializador.add(
                        datetime.now(), current_user.Username, 66, descripcion_evento, identificacion_componente_alarma
                    )
                    #Fin - Cambio jul-25
                    return jsonify({'estatus': True, 'status': 'success'}), 200
                else:
                    return jsonify({'estatus': False, 'status': 'error'}), 500
            except Exception as e:
                return jsonify({'estatus': False, 'status': 'error', 'message': str(e)}), 500


    return render_template('scaizen/catalogo_proveedor_consulta.html')

@app_scaizen.route('/Catalogo/Proveedor/Consulta/Editar', methods=['POST', 'GET'])
@login_required
def catalogo_proveedor_editar():
    with VerificarPermisosUsuario("ProveedorEditar", current_user.RolPerms) as contexto:
        if contexto is False:  # No tiene permisos
            return redirect("/scaizen/")
    if request.method == 'POST':
        with VerificarPermisosUsuario("ProveedorEditar", current_user.RolPerms) as contexto:
            if contexto is False:  # No tiene permisos
                return jsonify({'error':'El usuario actual no tiene los permisos para ejecutar esta accion.','action':'redirect'})
        # Extrae datos del formulario
        csrf_token = request.form.get('csrf_token')  # Si usas CSRF protection, valida el token aquí
        id_t = request.form.get('actualizar')

        if id_t:
            # Consultar cliente específico
            especifico = Tabla_Proveedor_actualizar(id_t,None,None,None,None,None,None,None,None,None)
            proveedor_especifico = ModelTablas.consulta_proveedores_especifico(db, especifico)

            if proveedor_especifico:
                data = [{'id_proveedor': proveedor.id,
                        'codigo': proveedor.codigo,
                        'nombre_comercial': proveedor.nombre_comercial,
                        'razon_social': proveedor.razon_social,
                        'rfc': proveedor.rfc,
                        'direccion': proveedor.direccion,
                        'telefono': proveedor.telefono,
                        'email': proveedor.email,
                        'informacion': proveedor.informacion,

                         } for proveedor  in proveedor_especifico]
                return jsonify({'datos_proveedor_especifico': data})
            else:
                return jsonify({'estatus': False, 'status': 'no_data'}), 404

        
        codigo = request.form.get('codigo')
        comercial = request.form.get('nombre_comercial')
        razon = request.form.get('razon')
        rfc = request.form.get('rfc')
        Direccion = request.form.get('direccion')
        Telefono = request.form.get('telefono')
        Email = request.form.get('email')
        informacion = request.form.get('informacion')
        editar = request.form.get('editar')
        actualizar_id = request.form.get('actualizar_id')

        if editar:
            actualizar_estacion = Tabla_Proveedor_actualizar_update(actualizar_id,codigo, comercial,razon, rfc,Direccion, Telefono, Email, informacion)
            
            exito_editar = ModelTablas.update_proveedor(db, actualizar_estacion)

            if exito_editar:
                #Ini - Cambio jul-25
                # Registrar el evento de editar proveedor
                descripcion_evento = f"Editar proveedor: {comercial}."
                identificacion_componente_alarma = "Editar proveedor"
                EventosComercializador.add(
                    datetime.now(), current_user.Username, 77, descripcion_evento, identificacion_componente_alarma
                )
                #Fin - Cambio jul-25
                return jsonify({'estatus': True, 'status': 'success'}), 200
            else:
                return jsonify({'estatus': False, 'status': 'error'}), 500

    return render_template('scaizen/catalogo_proveedor_editar.html')

@app_scaizen.route('/Catalogo/Estación_de_servició/Alta', methods=['POST', 'GET'])
@login_required
def catalogo_estacion_alta():
    with VerificarPermisosUsuario("EstacióndeservicioAlta", current_user.RolPerms) as contexto:
        if contexto is False:  # No tiene permisos
            return redirect("/scaizen/")
    if request.method == 'POST':
        with VerificarPermisosUsuario("EstacióndeservicioAlta", current_user.RolPerms) as contexto:
            if contexto is False:  # No tiene permisos
                return jsonify({'error':'El usuario actual no tiene los permisos para ejecutar esta accion.','action':'redirect'})
        try:
            id_tanque = request.form.get('id_tanque')
            codigo = request.form.get('codigo')
            permiso = request.form.get('Permiso')
            estacion = request.form.get('estacion')
            comercial = request.form.get('comercial')
            RFC = request.form.get('RFC')
            regimen = request.form.get('regimen')
            gerente = request.form.get('gerente')
            direccion = request.form.get('direccion')
            cod_pos = request.form.get('cod_pos')
            telefono = request.form.get('telefono')
            email = request.form.get('email')
            informacion = request.form.get('informacion')

            if id_tanque == "id_tanques":
                clientes_existentes = ModelTablas.numero_clientes(db)
                if clientes_existentes is not None:
                    data = [{'id_cliente': clientes.id_cliente, 'codigo_cliente': clientes.codigo_cliente} for clientes in clientes_existentes]
                    return jsonify({'datos_cliente': data})
                else:
                    return render_template('scaizen/catalogo_estacion_alta.html')

            if codigo and permiso:
                Alta_estacion = cv.EstacionesCV.add(codigo, permiso, estacion, comercial, RFC, regimen, gerente, direccion, cod_pos, telefono, email, informacion)
                logging.info(f"Alta de estación: {Alta_estacion}")
                if Alta_estacion:
                    #Ini - Cambio jul-25
                    # Registrar el evento de alta estación
                    descripcion_evento = f"Alta de Estación de servicio: {comercial}."
                    identificacion_componente_alarma = "Alta Estación"
                    EventosComercializador.add(
                        datetime.now(), current_user.Username, 88, descripcion_evento, identificacion_componente_alarma
                    )
                    #Fin - Cambio jul-25
                    # Retorna un mensaje JSON si la inserción fue exitosa
                    return jsonify({'estatus': True, 'status': 'success'}), 201
                else:
                    # Retorna un mensaje JSON si la inserción falló
                    return jsonify({'estatus': False, 'status': 'error'}), 500
        except Exception as e:
            logging.error(f"Error en catalogo_estacion_alta: {e}")
            return jsonify({'error': 'Ocurrió un error inesperado', 'details': str(e)}), 500
    else:
        return render_template('scaizen/catalogo_estacion_alta.html')

@app_scaizen.route('/Catalogo/Estación_de_servició/Consultar', methods=['POST', 'GET'])
@login_required
def catalogo_estacion_consultar():
    with VerificarPermisosUsuario("EstacióndeservicioConsultar", current_user.RolPerms) as contexto:
        if contexto is False:  # No tiene permisos
            return redirect("/scaizen/")

    if request.method == 'POST':
        with VerificarPermisosUsuario("EstacióndeservicioConsultar", current_user.RolPerms) as contexto:
            if contexto is False:  # No tiene permisos
                return jsonify({'error':'El usuario actual no tiene los permisos para ejecutar esta accion.','action':'redirect'})

        id_estaciones = request.form.get('id_estaciones')
        elementos_por_pagina=10
        page_num = request.form.get('page', 1, type=int)

        eliminar = request.form.get('eliminar')
        id = request.form.get('id')

        if id_estaciones and not eliminar:
            try:       
                

                start_index = (page_num - 1) * elementos_por_pagina + 1
                end_index = start_index + elementos_por_pagina

                # Obtener datos de clientes existentes
                estaciones_existentes,total = cv.EstacionesCV.select_given_between_date_for_pagination(page_num,elementos_por_pagina)

                total_pages = total // elementos_por_pagina + (total % elementos_por_pagina > 0)

                # Calcular el índice del último registro
                end_index = min(start_index + elementos_por_pagina, total)
                if end_index > total:
                    end_index = total

                # Crear objeto paginable
                pagination = Pagination(page=page_num, total=total, per_page=elementos_por_pagina,
                                        display_msg=f"Mostrando registros {start_index} - {end_index} de un total de <strong>({total})</strong>")
                
                if estaciones_existentes:

                    data = estaciones_existentes
                    user_perms = []
                    if config.CHECK_USER_PERM("EstacióndeservicioEditar",current_user.RolPerms): user_perms.append("EstacióndeservicioEditar")
                    if config.CHECK_USER_PERM("EstacióndeservicioEliminar",current_user.RolPerms): user_perms.append("EstacióndeservicioEliminar")
                    
                    #Ini - Cambio jul-25
                    # Registrar el evento de Consultar Estación servicio
                    descripcion_evento = f"Consultar lista de Estaciones servicio."
                    identificacion_componente_alarma = "Consultar estaciones servicio"
                    EventosComercializador.add(
                        datetime.now(), current_user.Username, 99, descripcion_evento, identificacion_componente_alarma
                    )
                    #Fin - Cambio jul-25

                    return jsonify({'datos_estacion_consulta': data, 'pagination': str(pagination), 'total_pages':str(total_pages), 'mostrando':start_index,
                                    'cantidad':total ,'total_paginas':total_pages,'paginactual':page_num,'user_perms': user_perms })
                else:
                    return jsonify({'estatus': False, 'status': 'No clients found'}), 404
            except ValueError as e:
                return jsonify({'error': f'Ocurrió un error: {str(e)}'})

        elif id and eliminar == "eliminar":
            with VerificarPermisosUsuario("EstacióndeservicioEliminar", current_user.RolPerms) as contexto:
                if contexto is False:  # No tiene permisos
                    return redirect("/scaizen/")
            try:
                delete = EliminarEstacion(id)
                clientes_eliminar = ModelTablas.eliminar_estacion(db, delete)
                
                if clientes_eliminar:
                    #Ini - Cambio jul-25
                    # Registrar el evento de eliminar estación de servicio
                    descripcion_evento = f"Eliminar estación de servicio: {id}."
                    identificacion_componente_alarma = "Eliminar estación"
                    EventosComercializador.add(
                        datetime.now(), current_user.Username, 66, descripcion_evento, identificacion_componente_alarma
                    )
                    #Fin - Cambio jul-25
                    return jsonify({'estatus': True, 'status': 'success'}), 200
                else:
                    return jsonify({'estatus': False, 'status': 'error'}), 500
            except Exception as e:
                return jsonify({'estatus': False, 'status': 'error', 'message': str(e)}), 500
    else:
        return render_template('scaizen/catalogo_estacion_consulta.html')

@app_scaizen.route('/Catalogo/Estación_de_servició/Consultar/Editar', methods=['POST', 'GET'])
@login_required
def catalogo_estacion_editar():
    with VerificarPermisosUsuario("EstacióndeservicioEditar", current_user.RolPerms) as contexto:
        if contexto is False:  # No tiene permisos
            return redirect("/scaizen/")
    if request.method == 'POST':
        with VerificarPermisosUsuario("EstacióndeservicioEditar", current_user.RolPerms) as contexto:
            if contexto is False:  # No tiene permisos
                return jsonify({'error':'El usuario actual no tiene los permisos para ejecutar esta accion.','action':'redirect'})
        # Extrae datos del formulario
        csrf_token = request.form.get('csrf_token')  # Si usas CSRF protection, valida el token aquí
        id_t = request.form.get('actualizar')
        logging.debug('logging.debug(id_t)')
        logging.debug(id_t)

        if id_t:
            # Consultar cliente específico
            especifico = Tabla_Estacion_actualizar(id_t, None, None, None, None, None, None, None, None, None, None, None, None, None)
            estacion_especifico = ModelTablas.consulta_estaciones_especifico(db, especifico)

            if estacion_especifico:
                data = [{'id_estacion': estacion.id,
                         'codigo': estacion.codigo,
                         'permiso_cre': estacion.permiso_cre,
                         'numero_estacion': estacion.numero_estacion,
                         'nombre_comercial':estacion.nombre_comercial,
                         'rfc': estacion.rfc,
                         'regimen': estacion.regimen,
                         'gerente':estacion.gerente,
                         'direccion': estacion.direccion,
                         'cod_pos': estacion.cod_pos,
                         'telefono': estacion.telefono,
                         'email': estacion.email,
                         'informacion': estacion.informacion
                         } for estacion in estacion_especifico]
                return jsonify({'datos_estacion_especifico': data})
            else:
                return jsonify({'estatus': False, 'status': 'no_data'}), 404

        
        codigo = request.form.get('codigo')
        Permiso = request.form.get('Permiso')
        estacion = request.form.get('estacion')
        comercial = request.form.get('comercial')
        RFC = request.form.get('RFC')
        regimen = request.form.get('regimen')
        gerente = request.form.get('gerente')
        Direccion = request.form.get('direccion')
        cod_pos = request.form.get('cod_pos')
        Telefono = request.form.get('telefono')
        Email = request.form.get('email')
        informacion = request.form.get('informacion')
        editar = request.form.get('editar')
        actualizar_id = request.form.get('actualizar_id')

        if editar:
            actualizar_estacion = Tabla_Estacion_actualizar_update(actualizar_id,codigo, Permiso, estacion, comercial, RFC, regimen, gerente, Direccion, cod_pos, Telefono, Email, informacion)
            
            exito_editar = ModelTablas.update_station(db, actualizar_estacion)

            if exito_editar:
                #Ini - Cambio jul-25
                # Registrar el evento de editar estación
                descripcion_evento = f"Editar estación de servicio: {comercial}."
                identificacion_componente_alarma = "Editar estación"
                EventosComercializador.add(
                    datetime.now(), current_user.Username, 77, descripcion_evento, identificacion_componente_alarma
                )
                #Fin - Cambio jul-25
                return jsonify({'estatus': True, 'status': 'success'}), 200
            else:
                return jsonify({'estatus': False, 'status': 'error'}), 500

    return render_template('scaizen/catalogo_estacion_editar.html')

@app_scaizen.route('/usuarios/perfiles/registrar')
@login_required
def registrar_usuario():
    return render_template('scaizen/perfiles.html')

@app_scaizen.route('/usuarios/permisos')
@login_required
def usuarios_permisos():
    return render_template('scaizen/privilegios.html')

@app_scaizen.route('/Catalogo/Usuarios/Alta', methods=['POST', 'GET'])
def catalogo_usuarios_alta():
    with VerificarPermisosUsuario("UsuariosAlta", current_user.RolPerms) as contexto:
        if contexto is False:  # No tiene permisos
            return redirect("/scaizen/")
    if request.method == 'POST':
        with VerificarPermisosUsuario("UsuariosAlta", current_user.RolPerms) as contexto:
            if contexto is False:  # No tiene permisos
                return jsonify({'error':'El usuario actual no tiene los permisos para ejecutar esta accion.','action':'redirect'})
        user_name = request.form.get('user_name')
        user_full = request.form.get('user_full')
        password = request.form.get('password')
        rol = request.form.get('role')
        if user_name and user_full and password and rol:
            estatus = "activo"
            id_rol = config.desencriptar_desde_hex(clave_hex_hash, rol)
            new_user =  cv.Usuario_Cv.add(user_name,user_full,None,password,id_rol,estatus)
            if new_user:
                #Ini - Cambio jul-25
                # Registrar el evento de alta usuario
                descripcion_evento = f"Alta de usuario: {user_full}."
                identificacion_componente_alarma = "Alta usuario"
                EventosComercializador.add(
                    datetime.now(), current_user.Username, 88, descripcion_evento, identificacion_componente_alarma
                )
                #Fin - Cambio jul-25
                # Retorna un mensaje JSON si la inserción fue exitosa
                return jsonify({'estatus': True, 'status': 'success'}), 201
            else:
                # Retorna un mensaje JSON si la inserción falló
                return jsonify({'estatus': False, 'status': 'error'}), 500
        return jsonify({'estatus': False, 'status': 'error'}), 500
    else:
        roles = cv.Roles.select_all()
        for rol in roles:
            rol.IdRol = config.encriptar_a_hex(clave_hex_hash, rol.IdRol)

        roles = cv.query_to_json(roles)
        # Renderiza el formulario HTML para crear un usuario
        return render_template('scaizen/catalogo_usuarios_crear.html',roles=roles)

@app_scaizen.route('/Catalogo/Usuarios/Consultar', methods=['POST', 'GET'])
def catalogo_usuarios_consultar():
    with VerificarPermisosUsuario("UsuariosConsultar", current_user.RolPerms) as contexto:
        if contexto is False:  # No tiene permisos
            return redirect("/scaizen/")
    page_num = request.form.get('page', 1, type=int)

    if request.method == 'POST':
        with VerificarPermisosUsuario("UsuariosConsultar", current_user.RolPerms) as contexto:
            if contexto is False:  # No tiene permisos
                return jsonify({'error':'El usuario actual no tiene los permisos para ejecutar esta accion.','action':'redirect'})
        id_usuarios = request.form.get('id_usuarios')
        id = request.form.get('id')

        eliminar = request.form.get('eliminar')

        if id_usuarios and not eliminar:
            elementos_por_pagina=10
            start_index = (page_num - 1) * elementos_por_pagina + 1
            end_index = start_index + elementos_por_pagina

            # Obtener datos de clientes existentes
            #usuario_existentes,total = ModelTablas.consulta_usuarios(db,page_num,elementos_por_pagina)
            usuario_existentes,total = cv.Usuario_Cv.select_for_pagination(page_num,elementos_por_pagina)

            total_pages = total // elementos_por_pagina + (total % elementos_por_pagina > 0)

            # Calcular el índice del último registro
            end_index = min(start_index + elementos_por_pagina, total)
            if end_index > total:
                end_index = total

            # Crear objeto paginable
            pagination = Pagination(page=page_num, total=total, per_page=elementos_por_pagina,
                                    display_msg=f"Mostrando registros {start_index} - {end_index} de un total de <strong>({total})</strong>")
            if usuario_existentes:
                data = cv.query_to_json(usuario_existentes)
                logging.debug(data)
                user_perms = []
                if config.CHECK_USER_PERM("UsuariosEditar",current_user.RolPerms): user_perms.append("UsuariosEditar")
                if config.CHECK_USER_PERM("UsuariosEliminar",current_user.RolPerms): user_perms.append("UsuariosEliminar")
                
                #Ini - Cambio jul-25
                # Registrar el evento de Consultar usuarios
                descripcion_evento = f"Consultar lista de usuarios."
                identificacion_componente_alarma = "Consultar usuarios"
                EventosComercializador.add(
                    datetime.now(), current_user.Username, 99, descripcion_evento, identificacion_componente_alarma
                )
                #Fin - Cambio jul-25

                return jsonify({'datos_usuario_consulta': data, 'pagination': str(pagination), 'total_pages':str(total_pages), 'mostrando':start_index,
                                'cantidad':total ,'total_paginas':total_pages,'paginactual':page_num, 'user_perms':user_perms})
            else:
                return jsonify({'estatus': False, 'status': 'No clients found'}), 404

        elif id and eliminar == "eliminar":
            with VerificarPermisosUsuario("UsuariosEliminar", current_user.RolPerms) as contexto:
                if contexto is False:  # No tiene permisos
                    return redirect("/scaizen/")
            try:
                #delete = Eliminar_Usuario(id)
                logging.debug(id)
                user_id = config.desencriptar_desde_hex(clave_hex_hash,id)
                usuaio_eliminar = cv.Usuario_Cv.delete(user_id)
                
                if usuaio_eliminar:
                    #Ini - Cambio jul-25
                    # Registrar el evento de eliminar usuario
                    descripcion_evento = f"Eliminar usuario: {id}."
                    identificacion_componente_alarma = "Eliminar usuario"
                    EventosComercializador.add(
                        datetime.now(), current_user.Username, 66, descripcion_evento, identificacion_componente_alarma
                    )
                    #Fin - Cambio jul-25
                    return jsonify({'estatus': True, 'status': 'success'}), 200
                else:
                    return jsonify({'estatus': False, 'status': 'error'}), 500
            except Exception as e:
                return jsonify({'estatus': False, 'status': 'error', 'message': str(e)}), 500   
    return render_template('scaizen/catalogo_usuarios_consultar.html')

@app_scaizen.route('/Catalogo/Usuarios/Consultar/Editar', methods=['POST', 'GET'])
@login_required
def catalogo_usuario_editar():
    with VerificarPermisosUsuario("UsuariosEditar", current_user.RolPerms) as contexto:
        if contexto is False:  # No tiene permisos
            return redirect("/scaizen/")
    roles = cv.Roles.select_all()
    for rol in roles:
        rol.IdRol = config.encriptar_a_hex(clave_hex_hash, rol.IdRol)
    roles = cv.query_to_json(roles)

    if request.method == 'POST':
        with VerificarPermisosUsuario("UsuariosEditar", current_user.RolPerms) as contexto:
            if contexto is False:  # No tiene permisos
                return jsonify({'error':'El usuario actual no tiene los permisos para ejecutar esta accion.','action':'redirect'})
        # Extrae datos del formulario
        csrf_token = request.form.get('csrf_token')  # Si usas CSRF protection, valida el token aquí
        id_t = request.form.get('actualizar')
        if id_t:
            id_user = config.desencriptar_desde_hex(clave_hex_hash, id_t)
            usuario_especifico = cv.Usuario_Cv.select_by_id(id_user)

            if usuario_especifico:
                rol = cv.Roles.select_by_IdRol(usuario_especifico.IdRol_fk)
                usuario_especifico.Password = None
                usuario_especifico.Id = config.encriptar_a_hex(clave_hex_hash,usuario_especifico.Id)
                usuario_especifico.IdRol_fk = config.encriptar_a_hex(clave_hex_hash,usuario_especifico.IdRol_fk)
                data = {}
                usuario_especifico = cv.query_to_json([usuario_especifico])[0]
                data['usuario'] = usuario_especifico
                data['rol'] = rol.NombreRol if rol else "Desconocido"
                return jsonify({'datos_usuario_especifico': data})
            else:
                return jsonify({'estatus': False, 'status': 'no_data'}), 404

        user_name = request.form.get('user_name')
        user_full = request.form.get('user_full')
        password = request.form.get('password')
        role = request.form.get('role')
        editar = request.form.get('editar')
        actualizar_id = request.form.get('actualizar_id') 
        
        if editar and  actualizar_id and role:
            logging.debug('actualizar_id')
            logging.debug(actualizar_id)
            logging.debug('role')
            logging.debug(role)
            #actualizar_usuario = Tabla_usuario_actualizar_update(actualizar_id,user_name,user_full,password,role)
            #exito_editar = ModelTablas.update_usuario(db, actualizar_usuario)
            id_user = config.desencriptar_desde_hex(clave_hex_hash, actualizar_id)
            id_rol = config.desencriptar_desde_hex(clave_hex_hash, role)
            user = cv.Usuario_Cv.select_by_id(id_user)
            edit_user = cv.Usuario_Cv.update_user(id_user,
                                                user_name,
                                                user_full,
                                                password,
                                                id_rol)
            if edit_user != user:
                #Ini - Cambio jul-25
                # Registrar el evento de editar usuario
                descripcion_evento = f"Editar usuario: {user_full}."
                identificacion_componente_alarma = "Editar usuario"
                EventosComercializador.add(
                    datetime.now(), current_user.Username, 77, descripcion_evento, identificacion_componente_alarma
                )
                #Fin - Cambio jul-25
                return jsonify({'estatus': True, 'status': 'success'}), 200
            else:
                return jsonify({'estatus': False, 'status': 'error'}), 500
            
    return render_template('scaizen/catalogo_usuarios_editar.html', roles=roles)

#Seccion catalogo
@app_scaizen.route('/Catalogo/factura/Alta', methods=['POST', 'GET'])
@login_required
def factura_alta():
    with VerificarPermisosUsuario("ClienteAlta", current_user.RolPerms) as contexto:
        if contexto is False:  # No tiene permisos
            return redirect("/scaizen/")
        
    if request.method == 'POST':
            with VerificarPermisosUsuario("ClienteAlta", current_user.RolPerms) as contexto:
                if contexto is False:  # No tiene permisos
                    return jsonify({'error':'El usuario actual no tiene los permisos para ejecutar esta accion.','action':'redirect'})    # Llamar al método create_user y obtener el resultado
    else:
          return render_template('scaizen/comercializador_alta_factura.html')

#Reciclar
#@app_scaizen.route('/reportes/alarmas')
#@login_required
#def reporte_alarmas():
#    return render_template('scaizen/alarmas.html')


#@app_scaizen.route('/reportes/historico')
#@login_required
#def reporte_historico():
#    return render_template('scaizen/historico.html')

#@app_scaizen.route('/reportes/balance')
#@login_required
#def reporte_balance():
#    return render_template('scaizen/balance.html')


#@app_scaizen.route('/reportes/totalizador')
#@login_required
#def reporte_totalizador():
#    return render_template('scaizen/totalizador.html')




#if __name__ == '__main__':

    #app.run(port=5000,debug=True)

