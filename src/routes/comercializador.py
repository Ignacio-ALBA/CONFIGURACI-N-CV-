from utilities.imports import *
from werkzeug.utils import secure_filename

app_comercializador = Blueprint('app_comercializador', __name__, url_prefix='/comercializador')

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
        estado = EventosComercializador.add(formato_fecha_hora_minuto, username, tipo_evento, descripcion_evento, identificacion_componente_alarma)
        #alarmas = EventosAlarmasDistribuidor.add(estado,None,formato_fecha_hora_minuto  )
        
    except Exception as e:
        logging.error(f"Excepción al registrar evento: {str(e)} en {Componente} por {username}.")
        descripcion_evento_distribuidor_error_registro = f"Eventos: Error al registrar evento en {Componente}"
        EventosComercializador.add(formato_fecha_hora_minuto, username, 3, descripcion_evento_distribuidor_error_registro, identificacion_componente_alarma)    
        logging.error(f"Error al registrar evento de tipo {tipo_evento} en {Componente} por {username}.")

@app_comercializador.route('/subir_factura/<string:prefijo>/<string:orden_id>', methods=['GET', 'POST'])
@login_required
def subir_factura(prefijo, orden_id):
    componente = 'comercializador/subir_factura'
    Descripcion = None
    Tipo_Evento = None
    if request.method == 'POST':
        if prefijo == "Venta":
            with VerificarPermisosUsuario("CVentasSubirFacturaXML", current_user.RolPerms) as contexto:
                if contexto is False:  # No tiene permisos
                    return jsonify({'error':'El usuario actual no tiene los permisos para ejecutar esta accion.','action':'redirect'})
        else:
            with VerificarPermisosUsuario("CComprasSubirFacturaXML", current_user.RolPerms) as contexto:
                if contexto is False:  # No tiene permisos
                    return jsonify({'error':'El usuario actual no tiene los permisos para ejecutar esta accion.','action':'redirect'})
        try:
            print("Hola")
            if 'file' not in request.files:
                return jsonify({'success': False, 'message': 'Archivo no proporcionado.'}), 400

            file = request.files['file']
            # Verificar si el archivo es un XML por su extensión y tipo MIME
            if file.filename.endswith('.xml') and file.mimetype in ['application/xml', 'text/xml']:
                # Guardar el archivo en un directorio seguro
                upload_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "facturas_xml/comercializador/descargas"))
                logging.debug(upload_dir)

                if not os.path.exists(upload_dir):
                    os.makedirs(upload_dir)

                # Asegurar el nombre del archivo
                filename = secure_filename(file.filename)
                logging.debug(filename)
                filepath = os.path.join(upload_dir, filename)

                # Comprobar si el archivo ya existe
                file.save(filepath)
                """
                if not os.path.exists(filepath):
                    file.save(filepath)
                else:
                    return jsonify({
                        'error': 'El archivo seleccionado ya se ha subido con anterioridad.'
                    }), 400
                """
                # Leer el archivo XML y extraer información
                tree = ET.parse(filepath)
                root = tree.getroot()

                # Namespace
                namespace = 'http://www.sat.gob.mx/cfd/4'
                namespace_complemento = 'http://www.sat.gob.mx/TimbreFiscalDigital'

                # Obtener el elemento Comprobante
                Comprobante = root.find(f'{{{namespace}}}Comprobante')
                Conceptos = root.find(f'{{{namespace}}}Conceptos')
                Impuestos = root.find(f'{{{namespace}}}Impuestos')
                # Obtener los elementos con las etiquetas necesarias
                Emisor = root.find(f'{{{namespace}}}Emisor')
                Receptor = root.find(f'{{{namespace}}}Receptor')
                Producto_data = Conceptos.find(f'{{{namespace}}}Concepto[1]')if Conceptos is not None else None
                Traslado_data = Conceptos.find(f'{{{namespace}}}Concepto[2]')if Conceptos is not None else None
                Complemento = root.find(f'{{{namespace}}}Complemento')
                TimbreFiscalDigital = Complemento.find(f'{{{namespace_complemento}}}TimbreFiscalDigital') if Complemento is not None else None
                print(Complemento)
                print(TimbreFiscalDigital)
                Addenda = root.find(f'{{{namespace}}}Addenda')
                AddendaMGCLO = Addenda.find('AddendaMGCLO') if Addenda is not None else None

                if prefijo == "Compra":
                    if Emisor is None or Receptor is None or Producto_data is None or Addenda is None or AddendaMGCLO is None:
                        return jsonify({
                            'error': 'El archivo seleccionado no tiene el formato correcto.'
                        }), 400


                emisor_rfc = Emisor.get('Rfc') if Emisor is not None else 'Desconocido'
                #emisor = Emisor.get('Nombre') if Receptor is not None else 'Desconocido'
                receptor_rfc = Receptor.get('Rfc') if Emisor is not None else 'Desconocido'
                #receptor = Receptor.get('Nombre') if Receptor is not None else 'Desconocido'
                producto = config.CLAVES_PRODUCTOS[Producto_data.get('ClaveProdServ')] if Producto_data is not None else 'Desconocido'
                Costo_producto = float(Producto_data.get('Importe')) if Producto_data is not None else None
                Costo_traslado = float(Traslado_data.get('Importe')) if Traslado_data is not None else None
                TotalImpuestos = float(Impuestos.get('TotalImpuestosTrasladados')) if Impuestos is not None else None
                Costo_total = (float(Costo_producto) if Costo_producto != None else 0) + (float(Costo_traslado) if Costo_traslado != None else 0) +(float(TotalImpuestos) if TotalImpuestos != None else 0)
                cantidad_nat_recibida = AddendaMGCLO.find(f'CantidadAlNatural').get('Valor') if AddendaMGCLO else 'Desconocido'
                autotanque = AddendaMGCLO.find(f'Vehiculo').get('Valor') if AddendaMGCLO else 'Desconocido'
                cantidad_neto_recibida = AddendaMGCLO.find(f'Cantidad20gC').get('Valor') if AddendaMGCLO else 'Desconocido'
                temperatura = AddendaMGCLO.find(f'TemperaturaGcentigrados').get('Valor') if AddendaMGCLO else 'Desconocido'
                autotanque = AddendaMGCLO.find(f'Vehiculo').get('Valor') if AddendaMGCLO else 'Desconocido'

                DatosOperativos = AddendaMGCLO.find(f'DatosOperativos') if AddendaMGCLO else None
                fechas = DatosOperativos.get('Valor').split(" PC:")[0] if DatosOperativos is not None  else None
                


                #CFDIS
                CFDI  =  TimbreFiscalDigital.get('UUID') if TimbreFiscalDigital is not None else 'Desconocido'
                TipoCFDI = root.get('TipoDeComprobante') if root  is not  None else 'Desconocido'
                PrecioVentaOCompraOContrap =  Producto_data.get('Importe') if Producto_data is not None else 'Desconocido'               
                FechaYHoraTransaccion = root.get(f'Fecha') if root is not None else 'Desconocido'
                if AddendaMGCLO:
                    VolumenDocumentado = AddendaMGCLO.find(f'Cantidad20gC').get('Valor') if AddendaMGCLO else 'Desconocido'
                else:
                    VolumenDocumentado = float(Producto_data.get('Cantidad')) if Producto_data is not None else None
                UNIDAD =  Producto_data.get(f'ClaveUnidad') if Producto_data else None
                TypeCFDI = None
                if TipoCFDI == 'I':
                    TypeCFDI = "Ingreso"
                elif TipoCFDI == 'E':
                    TypeCFDI = "Egreso"
                elif TipoCFDI == 'T':
                    TypeCFDI = "Traslado"
                


                UM = None
                if UNIDAD == 'LTR':
                    UM = "UM03"
                elif UNIDAD == 'M3':
                    UM = "UM04"
                    pass
                logging.debug({
                    'CFDI': CFDI,
                    'TipoCFDI': TipoCFDI,
                    'PrecioVentaOCompraOContrap': PrecioVentaOCompraOContrap,
                    'FechaYHoraTransaccion': FechaYHoraTransaccion,
                    'VolumenDocumentado': VolumenDocumentado,
                    'VolumenDocumentado_UM': UM
                })
                provedor_id = -1
                if emisor_rfc:
                    provedor_info = cv.ProveedorCV.select_by_rfc(emisor_rfc)
                    if provedor_info: provedor_id = provedor_info.Id_Proveedor

                try:   
                    CfdisComercializador_id  =cv.CfdisComercializador.add(2, CFDI,TypeCFDI,PrecioVentaOCompraOContrap, FechaYHoraTransaccion,VolumenDocumentado,UM)                
                    

                    session = cv.SessionLocal()
                    id = config.desencriptar_desde_hex(clave_hex_hash,orden_id)
                    if prefijo == "Venta":
                        consulta = session.query(cv.CargasComercializador).filter_by(Id=id).first()
                        if consulta:
                            Id_cliente_cv_fk = -1
                            Id_estacion_cv_fk = -1
                            cliente = cv.ClienteCV.select_by_rfc(receptor_rfc)
                            if cliente:
                                Id_cliente_cv_fk = cliente.Id_cliente
                            else:
                                estacion = cv.EstacionesCV.select_by_rfc(receptor_rfc)
                                if estacion:
                                    Id_estacion_cv_fk = estacion.Id_estacion

                            logging.debug(f"cfdi {CfdisComercializador_id}")
                            logging.debug(f"orden id {consulta.Id}")
                            consulta.Id_cfdi_comercializador_fk = CfdisComercializador_id
                            logging.debug(f"consulta.Id_cfdi_distribuidor_fk {consulta.Id_cfdi_comercializador_fk}")
                            consulta.Id_cliente_cv_fk = Id_cliente_cv_fk
                            consulta.Id_estacion_cv_fk = Id_estacion_cv_fk
                            consulta.Costo = Costo_producto
                            consulta.CostoTraslado = Costo_traslado
                            consulta.TotalImpuestos = TotalImpuestos
                            consulta.CostoTotal = Costo_total
                            session.commit()  

                            print(f"Consulta {consulta}")
                        else:
                            print("No se encontró la consulta con el Id especificado.") 
                    else:
                        consulta = session.query(cv.DescargasComercializador).filter_by(Id=id).first()
                        if consulta:
                            logging.debug(f"cfdi {CfdisComercializador_id}")
                            logging.debug(f"orden id {consulta.Id}")
                            consulta.Id_cfdi_comercializador_fk = CfdisComercializador_id
                            logging.debug(f"consulta.Id_cfdi_distribuidor_fk {consulta.Id_cfdi_comercializador_fk}")
                            consulta.Costo = Costo_producto
                            consulta.CostoTraslado = Costo_traslado
                            consulta.TotalImpuestos = TotalImpuestos
                            consulta.CostoTotal = Costo_total
                            session.commit()   
                    
                            print(f"Consulta {consulta}")
                        else:
                            print("No se encontró la consulta con el Id especificado.")

                except Exception as e:
                    session.rollback()
                    logging.debug(f"Error al actualizar: {e}")
                    descripcion_evento = f"Error al registrar la factura: {e}"
                    identificacion_componente_alarma = "Agregar operación"
                    EventosComercializador.add(
                        datetime.now(), current_user.Username, 11, descripcion_evento, identificacion_componente_alarma
                    )
                finally:
                    session.close()
                    descripcion_evento = f"Se ha registrado la factura de carga con éxito: {CfdisComercializador_id.Id_CFDIS_comercializador}"
                    identificacion_componente_alarma = "Agregar operación"
                    EventosComercializador.add(
                        datetime.now(), current_user.Username, 11, descripcion_evento, identificacion_componente_alarma
                    )
                return jsonify({
                    'success': True,
                    'message': f'La orden de comprar ha sido registrada con éxito y se enlazo a la factura: {filename}',
                }), 200
            else:
                return jsonify({'success': False, 'message': 'El archivo debe ser un XML válido.'}), 400
        except Exception as e:
            logging.error(f'Error procesando el archivo: {str(e)}')  # Cambié a error para mayor claridad
            error_trace = traceback.format_exc()
            logging.debug(f"Traceback: {error_trace}")
            return jsonify({'error': str(e)}), 400
    else:
        id = config.desencriptar_desde_hex(clave_hex_hash,orden_id)
        operacion = {}
        if prefijo == "Venta":
            with VerificarPermisosUsuario("CVentasSubirFacturaXML", current_user.RolPerms) as contexto:
                if contexto is False:  # No tiene permisos
                    return redirect("/scaizen/")
            operacion = cv.CargasComercializador.select_by_id(id)
            if operacion:
                if operacion.Id_cfdi_comercializador_fk != None:
                    return redirect("/scaizen/")
                operacion.Producto = config.GET_PRODUCTOS_PRODUCT_NAME(operacion.Producto)
                cliente = cv.ClienteCV.select_by_Id_cliente(operacion.Id_cliente_cv_fk)
                estacion = cv.EstacionesCV.select_by_Id_estacion(operacion.Id_estacion_cv_fk)
                operacion.id_entregas_fk = None
                operacion.Id = None
                operacion.Id_cfdi_comercializador_fk = None
                operacion.Id_cliente_cv_fk = None
                operacion.Id_estacion_cv_fk = None
                operacion.id_entregas_fk = None
                operacion.FechaYHoraInicialEntrega = operacion.FechaYHoraInicialEntrega.strftime("%d/%m/%Y %H:%M")
                operacion.FechaYHoraFinalEntrega = operacion.FechaYHoraFinalEntrega.strftime("%d/%m/%Y %H:%M")
                operacion = cv.query_to_json([operacion])[0]
                operacion['Emisor'] = "DISTRIBUIDOR DE DIESEL DE PUEBLA"
                operacion['EmisorRFC'] = 'DDP860722DN4'
                operacion['Receptor'] = cliente.Nombre_comercial if cliente and not estacion else estacion.Nombre_comercial if estacion and not cliente else "Desconocido"
                operacion['ReceptorRFC'] = cliente.RFC if cliente and not estacion else estacion.RFC if estacion and not cliente else "Desconocido"

        else:
            with VerificarPermisosUsuario("CComprasSubirFacturaXML", current_user.RolPerms) as contexto:
                if contexto is False:  # No tiene permisos
                    return redirect("/scaizen/")
            operacion = cv.DescargasComercializador.select_by_id(id)
            
            if operacion:
                if operacion.Id_cfdi_comercializador_fk != None:
                    return redirect("/scaizen/")
                operacion.Producto = config.GET_PRODUCTOS_PRODUCT_NAME(operacion.Producto)
                emisor = cv.ProveedorCV.select_by_Id_Proveedor(operacion.id_proveedor_fk)
                operacion.Id = None
                operacion.id_proveedor_fk = None
                operacion.id_recepciones_fk = None
                operacion.Id_fk = None
                operacion.Id_cfdi_comercializador_fk = None
                operacion.FechaYHoraInicialRecepcion = operacion.FechaYHoraInicialRecepcion.strftime("%d/%m/%Y %H:%M")
                operacion.FechaYHoraFinalRecepcion = operacion.FechaYHoraFinalRecepcion.strftime("%d/%m/%Y %H:%M")
                operacion = cv.query_to_json([operacion])[0]
                operacion['Emisor'] = emisor.Nombre_comercial if emisor else "Desconocido"
                operacion['EmisorRFC'] = emisor.RFC if emisor else "Desconocido"
                operacion['Receptor'] = 'DISTRIBUIDOR DE DIESEL DE PUEBLA'
                operacion['ReceptorRFC'] = 'DDP860722DN4'
        
        # Si la solicitud no es POST, también se debe manejar el caso GET (podrías querer devolver algo en este caso)
        return render_template('scaizen/subir_factura_xml.html', operacion=operacion, PRODUCTOS_NAMES = config.PRODUCTOS_NAMES,CLAVES_PRODUCTOS = config.CLAVES_PRODUCTOS,
                            CLAVES_SERVICIOS = config.CLAVES_SERVICIOS, blueprint='app_comercializador', prefijo=prefijo )

@app_comercializador.route('/compra_alta', methods=['GET', 'POST'])
@login_required
def compra_alta():
    with VerificarPermisosUsuario("CComprasAlta", current_user.RolPerms) as contexto:
        if contexto is False:  # No tiene permisos
            return redirect("/scaizen/")
    componente = 'comercializador/subir_factura'
    Descripcion = None
    Tipo_Evento = None
    if request.method == 'POST':
        with VerificarPermisosUsuario("CComprasAlta", current_user.RolPerms) as contexto:
            if contexto is False:  # No tiene permisos
                return jsonify({'error':'El usuario actual no tiene los permisos para ejecutar esta accion.','action':'redirect'})
        try:
            if 'file' not in request.files:
                return jsonify({'success': False, 'message': 'Archivo no proporcionado.'}), 400

            file = request.files['file']
            # Verificar si el archivo es un XML por su extensión y tipo MIME
            if file.filename.endswith('.xml') and file.mimetype in ['application/xml', 'text/xml']:
                # Guardar el archivo en un directorio seguro
                upload_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "facturas_xml/comercializador/descargas"))
                logging.debug(upload_dir)

                if not os.path.exists(upload_dir):
                    os.makedirs(upload_dir)

                # Asegurar el nombre del archivo
                filename = secure_filename(file.filename)
                logging.debug(filename)
                filepath = os.path.join(upload_dir, filename)

                # Comprobar si el archivo ya existe
                file.save(filepath)
                """
                if not os.path.exists(filepath):
                    file.save(filepath)
                else:
                    return jsonify({
                        'error': 'El archivo seleccionado ya se ha subido con anterioridad.'
                    }), 400
                """
                # Leer el archivo XML y extraer información
                tree = ET.parse(filepath)
                root = tree.getroot()

                # Namespace
                namespace = 'http://www.sat.gob.mx/cfd/4'
                namespace_complemento = 'http://www.sat.gob.mx/TimbreFiscalDigital'

                # Obtener el elemento Comprobante
                Comprobante = root.find(f'{{{namespace}}}Comprobante')
                Conceptos = root.find(f'{{{namespace}}}Conceptos')
                Impuestos = root.find(f'{{{namespace}}}Impuestos')
                # Obtener los elementos con las etiquetas necesarias
                Emisor = root.find(f'{{{namespace}}}Emisor')
                Receptor = root.find(f'{{{namespace}}}Receptor')
                Producto_data = Conceptos.find(f'{{{namespace}}}Concepto[1]')if Conceptos is not None else None
                Traslado_data = Conceptos.find(f'{{{namespace}}}Concepto[2]')if Conceptos is not None else None
                Complemento = root.find(f'{{{namespace}}}Complemento')
                TimbreFiscalDigital = Complemento.find(f'{{{namespace_complemento}}}TimbreFiscalDigital') if Complemento is not None else None
                print(Complemento)
                print(TimbreFiscalDigital)
                Addenda = root.find(f'{{{namespace}}}Addenda')
                AddendaMGCLO = Addenda.find('AddendaMGCLO') if Addenda is not None else None
                
                if Emisor is None or Receptor is None or Producto_data is None or Addenda is None or AddendaMGCLO is None:
                    return jsonify({
                        'error': 'El archivo seleccionado no tiene el formato correcto.'
                    }), 400

                emisor_rfc = Emisor.get('Rfc') if Emisor is not None else 'Desconocido'
                receptor = Receptor.get('Nombre') if Receptor is not None else 'Desconocido'
                producto = config.CLAVES_PRODUCTOS[Producto_data.get('ClaveProdServ')] if Producto_data is not None else 'Desconocido'
                Costo_producto = float(Producto_data.get('Importe')) if Producto_data is not None else 'Desconocido'
                Costo_traslado = float(Traslado_data.get('Importe')) if Traslado_data is not None else 'Desconocido'
                TotalImpuestos = float(Impuestos.get('TotalImpuestosTrasladados')) if Impuestos is not None else None
                Costo_total = (float(Costo_producto) if Costo_producto != None else 0) + (float(Costo_traslado) if Costo_traslado != None else 0) +(float(TotalImpuestos) if TotalImpuestos != None else 0)
                cantidad_nat_recibida = AddendaMGCLO.find(f'CantidadAlNatural').get('Valor') if AddendaMGCLO else 'Desconocido'
                autotanque = AddendaMGCLO.find(f'Vehiculo').get('Valor') if AddendaMGCLO else 'Desconocido'
                cantidad_neto_recibida = AddendaMGCLO.find(f'Cantidad20gC').get('Valor') if AddendaMGCLO else 'Desconocido'
                temperatura = AddendaMGCLO.find(f'TemperaturaGcentigrados').get('Valor') if AddendaMGCLO else 'Desconocido'
                autotanque = AddendaMGCLO.find(f'Vehiculo').get('Valor') if AddendaMGCLO else 'Desconocido'

                DatosOperativos = AddendaMGCLO.find(f'DatosOperativos') if AddendaMGCLO else None
                fechas = DatosOperativos.get('Valor').split(" PC:")[0] if DatosOperativos is not None  else None
                fecha_inicio =  fechas.split(' - ')[0] if DatosOperativos is not None  else 'Desconocida'
                fecha_fin = fechas.split(' - ')[1] if DatosOperativos is not None  else 'Desconocida'
                fecha_inicio = datetime.strptime(fecha_inicio, '%d/%m/%Y %H:%M').strftime('%Y-%m-%d %H:%M:%S')
                fecha_fin = datetime.strptime(fecha_fin, '%d/%m/%Y %H:%M').strftime('%Y-%m-%d %H:%M:%S')


                #CFDIS
                CFDI  =  TimbreFiscalDigital.get('UUID') if TimbreFiscalDigital is not None else 'Desconocido'
                TipoCFDI = root.get('TipoDeComprobante') if root  is not  None else 'Desconocido'
                PrecioVentaOCompraOContrap =  Producto_data.get('Importe') if Producto_data is not None else 'Desconocido'               
                FechaYHoraTransaccion = root.get(f'Fecha') if root is not None else 'Desconocido'
                VolumenDocumentado =AddendaMGCLO.find(f'Cantidad20gC').get('Valor') if AddendaMGCLO else 'Desconocido'
                UNIDAD =  Producto_data.get(f'ClaveUnidad') if Producto_data else None
                print(VolumenDocumentado)
                print(UNIDAD)
                TypeCFDI = None
                if TipoCFDI == 'I':
                    TypeCFDI = "Ingreso"
                elif TipoCFDI == 'E':
                    TypeCFDI = "Egreso"
                elif TipoCFDI == 'T':
                    TypeCFDI = "Traslado"

                UM = None
                if UNIDAD == 'LTR':
                    UM = "UM03"
                elif UNIDAD == 'M3':
                    UM = "UM04"
                    pass
                print({
                    'Id_descargas_comercializador_fk': 37,
                    'CFDI': CFDI,
                    'TipoCFDI': TypeCFDI,
                    'PrecioVentaOCompraOContrap': PrecioVentaOCompraOContrap,
                    'FechaYHoraTransaccion': FechaYHoraTransaccion,
                    'VolumenDocumentado': VolumenDocumentado,
                    'VolumenDocumentado_UM': UM
                })
                provedor_id = -1
                if emisor_rfc:
                    provedor_info = cv.ProveedorCV.select_by_rfc(emisor_rfc)
                    if provedor_info: provedor_id = provedor_info.Id_Proveedor
                
                try:
                    CfdisComercializador_id = cv.CfdisComercializador.add(1, CFDI, TypeCFDI, PrecioVentaOCompraOContrap, FechaYHoraTransaccion, VolumenDocumentado, UM)
                    print(f"cfdi {CfdisComercializador_id}")
                    session = cv.SessionLocal()

                    cv.DescargasComercializador.add(CfdisComercializador_id,provedor_id, autotanque, producto, 'D', 0, UM, cantidad_nat_recibida,  cantidad_nat_recibida, UM, 
                                                cantidad_neto_recibida, UM, temperatura, 1.033, Costo_producto,Costo_traslado,TotalImpuestos,Costo_total, fecha_inicio, fecha_fin, Path(filename).stem,2)
                

                    cv.CargasComercializador.add(autotanque,producto,'D',cantidad_nat_recibida,UM,0, cantidad_nat_recibida,UM,
                                            cantidad_neto_recibida,UM,temperatura,1.033,None,None,None,fecha_inicio,fecha_fin,2)
                    

                except Exception as e:
                    session.rollback()
                    logging.debug(f"Error al actualizar: {e}")
                finally:
                    session.close()
                
                # Responder con la información extraída
                """
                cv.DescargasComercializador.add(CfdisComercializador_id,provedor_id, autotanque, producto, 'D', 0, UM, cantidad_nat_recibida,  cantidad_nat_recibida, UM, 
                                                cantidad_neto_recibida, UM, temperatura, UM, Costo_producto,Costo_traslado,Costo_total, fecha_inicio, fecha_fin, Path(filename).stem)
                

                cv.CargasComercializador.add(autotanque,producto,'D',cantidad_nat_recibida,UM,0, cantidad_nat_recibida,UM,
                                            cantidad_neto_recibida,UM,temperatura,None,None,None,None,fecha_inicio,fecha_fin)
                """
                return jsonify({
                    'success': True,
                    'message': f'La orden de comprar ha sido registrada con éxito y se enlazo a la factura: {filename}',
                }), 200
            else:
                return jsonify({'success': False, 'message': 'El archivo debe ser un XML válido.'}), 400
        except Exception as e:
            logging.error(f'Error procesando el archivo: {str(e)}')  # Cambié a error para mayor claridad
            error_trace = traceback.format_exc()
            logging.debug(f"Traceback: {error_trace}")
            return jsonify({'error': str(e)}), 400
    else:
    # Si la solicitud no es POST, también se debe manejar el caso GET (podrías querer devolver algo en este caso)
        return render_template('scaizen/comercializador_alta_compra.html')

@app_comercializador.route('/consultar_compras', methods=['POST', 'GET'])
@login_required
def consultar_compras():
    
    #Ini - Cambio jul-25
    componente = 'Comercializador/consultar_compras'#checar o cambiar
    Descripcion = None
    Tipo_Evento = None
    #Fin - Cambio jul-25
    
    with VerificarPermisosUsuario("CComprasConsultar", current_user.RolPerms) as contexto:
        if contexto is False:  # No tiene permisos
            return redirect("/scaizen/")
        
    page_num = request.form.get('page', 1, type=int)
    # Acceder a los datos del formulario utilizando request.form
    if  request.method == 'POST':
        with VerificarPermisosUsuario("CComprasConsultar", current_user.RolPerms) as contexto:
            if contexto is False:  # No tiene permisos
                return jsonify({'error':'El usuario actual no tiene los permisos para ejecutar esta accion.','action':'redirect'})
        cancelar = request.form.get('cancelar')
        operacion = request.form.get('operacion')
        if operacion == 'consultar_registros':
            fecha_inicio = request.form.get('selected_start')
            fecha_fin = request.form.get('selected_end')
            elementos_por_pagina = 10
            consulta, total_consultas = cv.DescargasComercializador.select_given_between_date_for_pagination(fecha_inicio,fecha_fin,page_num,elementos_por_pagina)
        

            start_index = (page_num - 1) * elementos_por_pagina + 1
            end_index = start_index + elementos_por_pagina


            total_pages = total_consultas // elementos_por_pagina + (total_consultas % elementos_por_pagina > 0)
            # Calcular el índice del último registro
            end_index = min(start_index + elementos_por_pagina, total_consultas)
            if end_index > total_consultas:
                end_index = total_consultas

            # Crear objeto paginable
            pagination = Pagination(page=page_num, total=total_consultas, per_page=elementos_por_pagina,
                                    display_msg=f"Mostrando registros {start_index} - {end_index} de un total de <strong>({total_consultas})</strong>")
            logging.debug(consulta)
            consulta_json = cv.query_to_json(consulta)

            #Ini - Cambio jul-25
            Descripcion = f'Obtención y recuperación de registros de compras comercializador periodo {fecha_inicio}-{fecha_fin}  '
            Tipo_Evento = 3
            EventosComercializador.add(
                    datetime.now(), current_user.Username, Tipo_Evento, Descripcion, componente
                )
            #Fin - Cambio jul-25

            return jsonify({'operacion': consulta_json, 'pagination': str(pagination), 'total_pages':str(total_pages), 'mostrando':start_index,'cantidad':total_consultas ,'total_paginas':total_pages,'paginactual':page_num })
        elif operacion == 'cambiar_valor': 
            order_id = request.form.get('order_id')
            order_id = config.desencriptar_desde_hex(clave_hex_hash, order_id)
            parametro = request.form.get('parametro')
            if parametro == "presion":
                SessionLocal = cv.SessionLocal
                session = SessionLocal()
                value = parametro = request.form.get('value')
                if value == "": message = f"Valor vació"
                else:
                    try:
                        descarga = session.query(cv.DescargasComercializador).filter(cv.DescargasComercializador.Id == order_id).first()
                        if descarga:
                            if descarga.PresionAbsoluta == None:
                                descarga.PresionAbsoluta = value
                                session.commit()
                                message = f'Se actualizo correctamente la Presión para la operacion {order_id}.'
                            else: message = f'El parámetro para esa operacion ya no puede ser modificado.'
                        else: message = f'No se encontró la operacion {order_id}.'
                    except Exception as e:
                        session.rollback()
                        message = f"Error al actualizar el registro con numero {order_id}: {str(e)}"
                        error_trace = traceback.format_exc()
                        logging.error(f"Exception: {str(e)}")
                        logging.error(f"Traceback: {error_trace}")
                    finally:
                        session.close()
                        return jsonify(message)
            if parametro == "costo":
                SessionLocal = cv.SessionLocal
                session = SessionLocal()
                value = parametro = request.form.get('value')
                if value == "": message = f"Valor vació"
                else:
                    try:
                        descarga = session.query(cv.DescargasComercializador).filter(cv.DescargasComercializador.Id == order_id).first()
                        if descarga:
                            if descarga.Costo == None:
                                descarga.Costo = float(value)
                                if descarga.CostoTraslado != None:
                                    descarga.CostoTotal = descarga.Costo + descarga.CostoTraslado
                                session.commit()
                                message = f'Se actualizo correctamente el costo para la operacion {order_id}.'
                            else: message = f'El parametro para esa operacion ya no puede ser modificado.'
                        else: message = f'No se encontró la operacion {order_id}.'
                    except Exception as e:
                        session.rollback()
                        message = f"Error al actualizar el registro con numero {order_id}: {str(e)}"
                        error_trace = traceback.format_exc()
                        logging.error(f"Exception: {str(e)}")
                        logging.error(f"Traceback: {error_trace}")
                    finally:
                        session.close()
                        return jsonify(message)
            if parametro == "costotraslado":
                SessionLocal = cv.SessionLocal
                session = SessionLocal()
                value = parametro = request.form.get('value')
                if value == "": message = f"Valor vació"
                else:
                    try:
                        descarga = session.query(cv.DescargasComercializador).filter(cv.DescargasComercializador.Id == order_id).first()
                        if descarga:
                            if descarga.CostoTraslado == None:
                                descarga.CostoTraslado = float(value)
                                if descarga.Costo != None:
                                    descarga.CostoTotal = descarga.Costo + descarga.CostoTraslado
                                session.commit()
                                message = f'Se actualizo correctamente el costo de traslado para la operacion {order_id}.'
                            else: message = f'El parametro para esa operacion ya no puede ser modificado.'
                        else: message = f'No se encontró la operacion {order_id}.'
                    except Exception as e:
                        session.rollback()
                        message = f"Error al actualizar el registro con numero {order_id}: {str(e)}"
                        error_trace = traceback.format_exc()
                        logging.error(f"Exception: {str(e)}")
                        logging.error(f"Traceback: {error_trace}")
                    finally:
                        session.close()
                        return jsonify(message)
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
    return render_template('scaizen/comercializador_consultar_operaciones.html',endpoint='consultar_compras', productos_color = config.PRODUCTOS_COLOR_BY_NAME, PRODUCTOS_NAMES = config.PRODUCTOS_NAMES)

@app_comercializador.route('/consultar_ventas', methods=['POST', 'GET'])
@login_required
def consultar_ventas():
    
    #Ini - Cambio jul-25
    Componente = 'comercializador/consultar_ventas'#checar o cambiar
    Descripcion = None
    Tipo_Evento = None
    #Fin - Cambio jul-25
    
    with VerificarPermisosUsuario("CVentasConsultar", current_user.RolPerms) as contexto:
        if contexto is False:  # No tiene permisos
            return redirect("/scaizen/")
    
    page_num = request.form.get('page', 1, type=int)
    # Acceder a los datos del formulario utilizando request.form
    
    if  request.method == 'POST':
        with VerificarPermisosUsuario("CVentasConsultar", current_user.RolPerms) as contexto:
            if contexto is False:  # No tiene permisos
                return jsonify({'error':'El usuario actual no tiene los permisos para ejecutar esta accion.','action':'redirect'})
        cancelar = request.form.get('cancelar')
        operacion = request.form.get('operacion')
        if operacion == 'consultar_registros':
            page_num = request.form.get('page', 1, type=int)
            fecha_inicio = request.form.get('selected_start')
            fecha_fin = request.form.get('selected_end')
            elementos_por_pagina = 10
            consulta, total_consultas = cv.CargasComercializador.select_given_between_date_for_pagination(fecha_inicio,fecha_fin,page_num,elementos_por_pagina)
        

            start_index = (page_num - 1) * elementos_por_pagina + 1
            end_index = start_index + elementos_por_pagina


            total_pages = total_consultas // elementos_por_pagina + (total_consultas % elementos_por_pagina > 0)
            # Calcular el índice del último registro
            end_index = min(start_index + elementos_por_pagina, total_consultas)
            if end_index > total_consultas:
                end_index = total_consultas

            # Crear objeto paginable
            pagination = Pagination(page=page_num, total=total_consultas, per_page=elementos_por_pagina,
                                    display_msg=f"Mostrando registros {start_index} - {end_index} de un total de <strong>({total_consultas})</strong>")
            logging.debug(consulta)
            consulta_json = cv.query_to_json(consulta)

            #Ini - Cambio jul-25
            Descripcion = f'Obtención y recuperación de registros de ventas comercializador periodo {fecha_inicio}-{fecha_fin}  '
            Tipo_Evento = 3
            EventosComercializador.add(
                datetime.now(), current_user.Username, Tipo_Evento, Descripcion, Componente
            )
            #Fin - Cambio jul-25

            return jsonify({'operacion': consulta_json, 'pagination': str(pagination), 'total_pages':str(total_pages), 'mostrando':start_index,'cantidad':total_consultas ,'total_paginas':total_pages,'paginactual':page_num })
        elif operacion == 'cambiar_valor': 
            order_id = request.form.get('order_id')
            order_id = config.desencriptar_desde_hex(clave_hex_hash, order_id)
            parametro = request.form.get('parametro')
            if parametro == "presion":
                SessionLocal = cv.SessionLocal
                session = SessionLocal()
                try:
                    value = parametro = request.form.get('value')
                    carga = session.query(cv.CargasComercializador).filter(cv.CargasComercializador.Id == order_id).first()
                    if carga:
                        if carga.PresionAbsoluta == None:
                            carga.PresionAbsoluta = value
                            session.commit()
                            message = f'Se actualizo correctamente la Presión para la operacion {order_id}.'
                        else: message = f'El parametro para esa operacion ya no puede ser modificado.'
                    else: message = f'No se encontro la operacion {order_id}.'
                except Exception as e:
                    session.rollback()
                    message = f"Error al actualizar el registro con numero {order_id}: {str(e)}"
                    error_trace = traceback.format_exc()
                    logging.error(f"Exception: {str(e)}")
                    logging.error(f"Traceback: {error_trace}")
                finally:
                    session.close()
                    return jsonify(message)
                
            if parametro == "costo":
                SessionLocal = cv.SessionLocal
                session = SessionLocal()
                try:
                    value = parametro = request.form.get('value')
                    carga = session.query(cv.CargasComercializador).filter(cv.CargasComercializador.Id == order_id).first()
                    if carga:
                        if carga.Costo == None:
                            carga.Costo = float(value)
                            if carga.CostoTraslado != None:
                                carga.CostoTotal = carga.Costo + carga.CostoTraslado
                            session.commit()
                            message = f'Se actualizo correctamente el costo para la operacion {order_id}.'
                        else: message = f'El parametro para esa operacion ya no puede ser modificado.'
                    else: message = f'No se encontro la operacion {order_id}.'
                except Exception as e:
                    session.rollback()
                    message = f"Error al actualizar el registro con numero {order_id}: {str(e)}"
                    error_trace = traceback.format_exc()
                    logging.error(f"Exception: {str(e)}")
                    logging.error(f"Traceback: {error_trace}")
                finally:
                    session.close()
                    return jsonify(message)
            if parametro == "costotraslado":
                SessionLocal = cv.SessionLocal
                session = SessionLocal()
                try:
                    value = parametro = request.form.get('value')
                    carga = session.query(cv.CargasComercializador).filter(cv.CargasComercializador.Id == order_id).first()
                    if carga:
                        if carga.CostoTraslado == None:
                            carga.CostoTraslado = float(value)
                            if carga.Costo != None:
                                carga.CostoTotal = float(carga.Costo) + float(carga.CostoTraslado)
                            session.commit()
                            message = f'Se actualizo correctamente el costo de traslado para la operacion {order_id}.'
                        else: message = f'El parametro para esa operacion ya no puede ser modificado.'
                    else: message = f'No se encontro la operacion {order_id}.'
                except Exception as e:
                    session.rollback()
                    message = f"Error al actualizar el registro con numero {order_id}: {str(e)}"
                    error_trace = traceback.format_exc()
                    logging.error(f"Exception: {str(e)}")
                    logging.error(f"Traceback: {error_trace}")
                finally:
                    session.close()
                    return jsonify(message)
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
    
    return render_template('scaizen/comercializador_consultar_operaciones.html', endpoint='consultar_ventas', productos_color = config.PRODUCTOS_COLOR_BY_NAME, PRODUCTOS_NAMES = config.PRODUCTOS_NAMES)


def load_json_structure(file_path):
    """Lee la estructura JSON desde un archivo con codificación UTF-8."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# Reportes Diarios #
def fill_daily_data(DailyRepor):
    DataShow = []    
    for producto in DailyRepor:
        producto['tanques'] = sorted(producto['tanques'], key=lambda tanque: tanque['tanque'].codigo)
        DataShow.append({
            'ClaveProducto':producto['producto'].ClaveProducto,
            'ClaveSubProducto':producto['producto'].ClaveSubProducto,
            'ComposOctanajeGasolina':producto['producto'].ComposOctanajeGasolina,
            'GasolinaConCombustibleNoFosil':producto['producto'].GasolinaConCombustibleNoFosil,
            'ComposDeCombustibleNoFosilEnGasolina':producto['producto'].ComposDeCombustibleNoFosilEnGasolina,
            'DieselConCombustibleNoFosil':producto['producto'].DieselConCombustibleNoFosil,
            'ComposDeCombustibleNoFosilEnDiesel':producto['producto'].ComposDeCombustibleNoFosilEnDiesel,
            'Marcaje':producto['producto'].Marcaje,
            'ConcentracionSustanciasMarcaje':producto['producto'].ConcentracionSustanciasMarcaje,
            'MarcaComercial':producto['producto'].MarcaComercial,
            'nombre_producto':producto['producto'].nombre_producto,
            'tanques': sorted([{
                'Codigo':tanque['tanque'].codigo,
                'ClaveIdentificacionTanque': tanque['tanque'].ClaveIdentificacionTanque,
                'LocalizacionYODescripcionTanque':tanque['tanque'].LocalizacionYODescripcionTanque,
                'VigenciaCalibracionTanque':str(tanque['tanque'].VigenciaCalibracionTanque),
                'CapacidadTotalTanque':tanque['tanque'].CapacidadTotalTanque,
                'CapacidadOperativaTanque':tanque['tanque'].CapacidadOperativaTanque,
                'CapacidadUtilTanque':tanque['tanque'].CapacidadUtilTanque,
                'CapacidadFondajeTanque':tanque['tanque'].CapacidadFondajeTanque,
                'VolumenMinimoOperacion':tanque['tanque'].VolumenMinimoOperacion,
                'entregas':{
                    'TotalEntregas':tanque['entregas'].TotalEntregas,
                    'SumaVolumenEntregado':tanque['entregas'].SumaVolumenEntregado,
                    'SumaVolumenEntregado_UM':tanque['entregas'].SumaVolumenEntregado_UM,
                    'TotalDocumentos':tanque['entregas'].TotalDocumentos,
                    'SumaVentas':tanque['entregas'].SumaVentas
                },
                'recepciones':{
                    'TotalRecepciones':tanque['recepciones'].TotalRecepciones,
                    'SumaVolumenRecepcion':tanque['recepciones'].SumaVolumenRecepcion,
                    'SumaVolumenRecepcion_UM':tanque['recepciones'].SumaVolumenRecepcion_UM,
                    'TotalDocumentos':tanque['recepciones'].TotalDocumentos,
                    'SumaCompras':tanque['recepciones'].SumaCompras
                },
                'existencias':{
                    'VolumenExistenciasAnterior':tanque['existencias'].VolumenExistenciasAnterior,
                    'VolumenAcumOpsRecepcion':tanque['existencias'].VolumenAcumOpsRecepcion,
                    'VolumenAcumOpsRecepcion_UM':tanque['existencias'].VolumenAcumOpsRecepcion_UM,
                    'HoraRecepcionAcumulado':tanque['existencias'].HoraRecepcionAcumulado,
                    'VolumenAcumOpsEntrega':tanque['existencias'].VolumenAcumOpsEntrega,
                    'VolumenAcumOpsEntrega_UM':tanque['existencias'].VolumenAcumOpsEntrega_UM,
                    'HoraEntregaAcumulado':tanque['existencias'].HoraEntregaAcumulado,
                    'VolumenExistencias':tanque['existencias'].VolumenExistencias,
                    'FechaYHoraEstaEdicion':tanque['existencias'].FechaYHoraEstaEdicion,
                    'FechaYHoraEdicionAnterior':tanque['existencias'].FechaYHoraEdicionAnterior,
                },
                'recepcion': [{
                    'Id_RECEPCION':recepcion.Id,
                    'NumeroDeRegistro':recepcion.Id,
                    'TipoDeRegistro':recepcion.TipoDeRegistro,
                    'VolumenInicialTanque':recepcion.VolumenInicialTanque,
                    'VolumenInicialTanque_UM':recepcion.VolumenInicialTanque_UM,
                    'VolumenFinalTanque':recepcion.VolumenFinalTanque,
                    'VolumenRecepcion':recepcion.VolumenRecepcion,
                    'VolumenRecepcion_UM':recepcion.VolumenRecepcion_UM,
                    'Temperatura':recepcion.Temperatura,
                    'Costo':recepcion.Costo,
                    'PresionAbsoluta':recepcion.PresionAbsoluta,
                    'FechaYHoraInicioRecepcion':recepcion.FechaYHoraInicialRecepcion.astimezone().isoformat(),
                    'FechaYHoraFinalRecepcion':recepcion.FechaYHoraFinalRecepcion.astimezone().isoformat()
                } for recepcion in tanque['recepcion']] if len(tanque['recepcion']) > 0 else [
                    {
                    'Id_RECEPCION':'---',
                    'NumeroDeRegistro':'---',
                    'TipoDeRegistro':'---',
                    'VolumenInicialTanque':'---',
                    'VolumenInicialTanque_UM':'---',
                    'VolumenFinalTanque':'---',
                    'VolumenRecepcion':'---',
                    'VolumenRecepcion_UM':'---',
                    'Temperatura':'---',
                    'Costo':'---',
                    'PresionAbsoluta':'---',
                    'FechaYHoraInicioRecepcion':'---',
                    'FechaYHoraFinalRecepcion':'---'
                }
                ],
                'entrega': [{
                    'Id_ENTREGA':entrega.Id,
                    'NumeroDeRegistro':entrega.Id,
                    'TipoDeRegistro':entrega.TipoDeRegistro,
                    'VolumenInicialTanque':entrega.VolumenInicialTanque,
                    'VolumenInicialTanque_UM':entrega.VolumenInicialTanque_UM,
                    'VolumenFinalTanque':entrega.VolumenFinalTanque,
                    'VolumenEntregado':entrega.VolumenEntregado,
                    'VolumenEntregado_UM':entrega.VolumenEntregado_UM,
                    'Temperatura':entrega.Temperatura,
                    'Costo':entrega.Costo,
                    'PresionAbsoluta':entrega.PresionAbsoluta,
                    'FechaYHoraInicialEntrega':entrega.FechaYHoraInicialEntrega.astimezone().isoformat(),
                    'FechaYHoraFinalEntrega':entrega.FechaYHoraFinalEntrega.astimezone().isoformat()
                } for entrega in tanque['entrega']] if len(tanque['entrega']) > 0 else [
                    {
                    'Id_ENTREGA':'---',
                    'NumeroDeRegistro':'---',
                    'TipoDeRegistro':'---',
                    'VolumenInicialTanque':'---',
                    'VolumenInicialTanque_UM':'---',
                    'VolumenFinalTanque':'---',
                    'VolumenEntregado':'---',
                    'VolumenEntregado_UM':'---',
                    'Temperatura':'---',
                    'Costo':'---',
                    'PresionAbsoluta':'---',
                    'FechaYHoraInicialEntrega':'---',
                    'FechaYHoraFinalEntrega':'---'
                }
                ]
            } for tanque in producto['tanques']], key=lambda x: x['ClaveIdentificacionTanque'])
        })
        logging.debug(f"DataShow: {DataShow}")
    return DataShow

@app_comercializador.route('/diario_tanques', methods=['GET', 'POST'])
@login_required
def diario_tanques():
    with VerificarPermisosUsuario("CReportediario", current_user.RolPerms) as contexto:
        if contexto is False:  # No tiene permisos
            return redirect("/scaizen/")
    #Ini - Cambio jul-25    
    componente = 'comercializador/diario_tanques'
    Descripcion = None
    Tipo_Evento = None
    #Fin - Cambio jul-25
    GeneralReportInstance = scaizen_cv_funtions.GeneralReport(2)
    productos = GeneralReportInstance.GiveProductsIdsAndMarcaC()
    productos_options = []
    for producto in productos:
        tanques = cv.Tanque.get_for_Id_PRODUCTO_fk(producto['id_producto_fk'])
        productos_options.append({
            'producto_name':producto['nombre_producto'],
            'tanques': [tanque.codigo for tanque in tanques] 
        })
    if request.method == 'POST':
        with VerificarPermisosUsuario("CReportediario", current_user.RolPerms) as contexto:
            if contexto is False:  # No tiene permisos
                return jsonify({'error':'El usuario actual no tiene los permisos para ejecutar esta accion.','action':'redirect'})
        productoSelect = request.form.get('productoSelect')
        tanqueSelect = request.form.get('tanqueSelect')
        startDate = request.form.get('startDate')
        generar = request.form.get('generar')
        print(productoSelect)
        print(tanqueSelect)
        print(startDate)

        DailyReportFuntionsInstance= scaizen_cv_funtions.DailyReportFuntions(2)

        if generar:
            with VerificarPermisosUsuario("CReportediarioGenerar", current_user.RolPerms) as contexto:
                if contexto is False:  # No tiene permisos
                    return jsonify({'error':'El usuario actual no tiene los permisos para ejecutar esta accion.','action':'redirect'})
            startDate = datetime.strptime(startDate, "%Y-%m-%d %H:%M:%S")
            fecha_inicio = startDate
            fecha_fin = startDate.replace(hour=23, minute=59, second=59)
            fecha_inicio = fecha_inicio.strftime('%Y-%m-%d %H:%M:%S')
            fecha_fin = fecha_fin.strftime('%Y-%m-%d %H:%M:%S')
            logging.debug(f"fecha_inicio: {fecha_inicio}")
            logging.debug(f"fecha_fin: {fecha_fin}")
            return DailyReportFuntionsInstance.SetDailyData(fecha_inicio, fecha_fin)

        elif productoSelect is not None and startDate is not None and tanqueSelect is not None:
            with VerificarPermisosUsuario("CReportediarioVer", current_user.RolPerms) as contexto:
                if contexto is False:  # No tiene permisos
                    return jsonify({'error':'El usuario actual no tiene los permisos para ejecutar esta accion.','action':'redirect'})
            try:
                # Parse startDate and add time if necessary
                startDate_obj = datetime.strptime(startDate, '%Y-%m-%dT%H:%M:%S.%fZ')
                # Añadir la hora "00:00:00"
                startDate = startDate_obj.replace(hour=00, minute=00, second=00)


                DailyRepor = None
                if productoSelect == 'all' and tanqueSelect == 'all':
                    DailyRepor = DailyReportFuntionsInstance.GetDailyReportAll(startDate)
                elif productoSelect != 'all' and tanqueSelect == 'all':
                    producto_id = GeneralReportInstance.GiveProductNameById(productoSelect)
                    DailyRepor = DailyReportFuntionsInstance.GetDailyReportByProductAll(producto_id,startDate)
                elif productoSelect != 'all' and tanqueSelect != 'all':
                    producto_id = GeneralReportInstance.GiveProductNameById(productoSelect)
                    DailyRepor = DailyReportFuntionsInstance.GetDailyReportByProductAndTank(producto_id,tanqueSelect,startDate)
                elif productoSelect == 'all' and tanqueSelect != 'all':
                    DailyRepor = DailyReportFuntionsInstance.GetDailyReportByOneTank(tanqueSelect,startDate)
                if DailyRepor:
                    
                    #Ini - Cambio jul-25
                    Descripcion = f'Obtención y recuperación de reporte volumetrico diario de comercializador del día {startDate}  '
                    Tipo_Evento = 3
                    EventosComercializador.add(
                        datetime.now(), current_user.Username, Tipo_Evento, Descripcion, componente
                    )
                    #Fin - Cambio jul-25
                    
                    return fill_daily_data(DailyRepor)
                else: return jsonify({'error': 'No se encontraron datos para los parámetros proporcionados.'})
            except ValueError:
                return jsonify({'error': 'Formato de fecha inválido'}), 400
        else:  return  jsonify({'error': 'Faltan parámetros necesarios. Por favor, complete todos los campos.'})
    
    return render_template('scaizen/comercializador_reporte_diario.html', productos_options=productos_options,blueprint='app_comercializador',
                        productos_color = config.PRODUCTOS_COLOR_BY_NAME, PRODUCTOS_NAMES = config.PRODUCTOS_NAMES)

def get_comercialzador_reporte_diario(fecha_consulta):
    if fecha_consulta:
        DailyReportFuntionsInstance = DailyReportFuntions(2)
        controles = GeneralReport(2)
        diarios_controles = controles.GiveCV()
        diarios_JSON = DailyReportFuntionsInstance.GetDailyReportAll(fecha_consulta)
        fecha_start=  fecha_consulta + " 00:00:00"
        fecha_end = fecha_consulta + " 23:59:59"

        if diarios_JSON:
            id_complemento_recepcion = None
            id_complemento_entrega = None
            tipo = str('comercializador')

            for producto in diarios_JSON:
                for tanque in producto['tanques']:
                    for recepcion in tanque['recepcion']:
                        id_complemento_recepcion = 2
                        complemento_distribuidor_recepcion = Comp_Comercializador.Comp_Comercializacion_schema_json(id_complemento_recepcion,tipo,'C', recepcion,'R_cv')
                    for entrega in tanque['entrega']:
                        id_complemento_entrega = 2
                        complemento_distribuidor_entrega = Comp_Comercializador.Comp_Comercializacion_schema_json(id_complemento_entrega,tipo,'C', entrega,'E_cv')

            productos_reporte = []
            logging.debug("diarios_JSON", diarios_JSON)
            for producto in diarios_JSON:
                tanque_reporte = []
                for tanques in producto['tanques']:
                    tanque_item={
                        'ClaveIdentificacionTanque':tanques['tanque'].ClaveIdentificacionTanque,
                        'Localizaciony/oDescripcionTanque':tanques['tanque'].LocalizacionYODescripcionTanque,
                        'VigenciaCalibracionTanque':tanques['tanque'].VigenciaCalibracionTanque.strftime('%Y-%m-%d %H:%M:%S'),
                        'CapacidadTotalTanque': {
                            'ValorNumerico':tanques['tanque'].CapacidadTotalTanque,
                            'UnidadDeMedida':tanques['tanque'].CapacidadTotalTanque_UM
                        },
                        'CapacidadOperativaTanque': {
                            'ValorNumerico':tanques['tanque'].CapacidadOperativaTanque,
                            'UnidadDeMedida':tanques['tanque'].CapacidadOperativaTanque_UM
                        },
                        'CapacidadUtilTanque': {
                            'ValorNumerico':tanques['tanque'].CapacidadUtilTanque,
                            'UnidadDeMedida':tanques['tanque'].CapacidadUtilTanque_UM
                        },
                        'CapacidadFondajeTanque': {
                            'ValorNumerico':tanques['tanque'].CapacidadFondajeTanque,
                            'UnidadDeMedida':tanques['tanque'].CapacidadFondajeTanque_UM
                        },
                        'CapacidadGasTalon': {
                            'ValorNumerico':tanques['tanque'].CapacidadGasTalon ,
                            'UnidadDeMedida':tanques['tanque'].CapacidadGasTalon_UM	
                        },
                        'VolumenMinimoOperacion': {
                            'ValorNumerico':tanques['tanque'].VolumenMinimoOperacion,
                            'UnidadDeMedida':tanques['tanque'].VolumenMinimoOperacion_UM
                        },
                        'EstadoTanque':tanques['tanque'].EstadoTanque,
                        'Medidores': [{
                            'SistemaMedicionTanque':medicion.SistemaMedicionTanque,
                            'LocalizODescripSistMedicionTanque':medicion.LocalizODescripSistMedicionTanque,
                            'VigenciaCalibracionSistMedicionTanque':medicion.VigenciaCalibracionSistMedicionTanque.strftime('%Y-%m-%d %H:%M:%S'),
                            'IncertidumbreMedicionSistMedicionTanque': medicion.IncertidumbreMedicionSistMedicionTanque
                        }for medicion in tanques['medicion_tanque']],
                        'Existencias': {
                            'VolumenExistenciasAnterior':tanques['existencias'].VolumenExistenciasAnterior,
                            'VolumenAcumOpsRecepcion': {
                                'ValorNumerico':tanques['existencias'].VolumenAcumOpsRecepcion,
                                'UnidadDeMedida':tanques['existencias'].VolumenAcumOpsRecepcion_UM
                            },
                            'HoraRecepcionAcumulado':tanques['existencias'].HoraRecepcionAcumulado,
                            'VolumenAcumOpsEntrega': {
                                'ValorNumerico':tanques['existencias'].VolumenAcumOpsEntrega,
                                'UnidadDeMedida':tanques['existencias'].VolumenAcumOpsEntrega_UM
                            },
                            'HoraEntregaAcumulado':tanques['existencias'].HoraEntregaAcumulado,
                            'VolumenExistencias':tanques['existencias'].VolumenExistencias,
                            'FechaYHoraEstaMedicion':tanques['existencias'].FechaYHoraEstaEdicion,
                            'FechaYHoraMedicionAnterior':tanques['existencias'].FechaYHoraEdicionAnterior
                        },
                        'Recepciones': {
                            'TotalRecepciones':tanques['recepciones'].TotalRecepciones,
                            'SumaVolumenRecepcion': {
                                'ValorNumerico':tanques['recepciones'].SumaVolumenRecepcion,
                                'UnidadDeMedida':tanques['recepciones'].SumaVolumenRecepcion_UM
                            },
                            'TotalDocumentos':tanques['recepciones'].TotalDocumentos,
                            'SumaCompras':tanques['recepciones'].SumaCompras ,
                            'Recepcion': [{
                                'NumeroDeRegistro':recepcion.Id,
                                'TipoDeRegistro':recepcion.TipoDeRegistro,
                                'VolumenInicialTanque': {
                                    'ValorNumerico':recepcion.VolumenInicialTanque,
                                    'UnidadDeMedida': recepcion.VolumenInicialTanque_UM
                                },
                                'VolumenFinalTanque':recepcion.VolumenFinalTanque,
                                'VolumenRecepcion': {
                                    'ValorNumerico':recepcion.VolumenRecepcion,
                                    'UnidadDeMedida':recepcion.VolumenRecepcion_UM
                                },
                                'Temperatura':recepcion.Temperatura ,
                                'PresionAbsoluta':recepcion.PresionAbsoluta ,
                                'FechaYHoraInicioRecepcion':recepcion.FechaYHoraInicialRecepcion.astimezone().isoformat(),
                                'FechaYHoraFinalRecepcion':recepcion.FechaYHoraFinalRecepcion.astimezone().isoformat(), 
                                'Complemento':Comp_Comercializador.Comp_Comercializacion_schema_json(id_complemento_recepcion,tipo,'C',recepcion,'R_cv')
                            }for recepcion in tanques['recepcion']]
                        },
                        'Entregas': {
                            'TotalEntregas':tanques['entregas'].TotalEntregas,
                            'SumaVolumenEntregado': {
                                'ValorNumerico':tanques['entregas'].SumaVolumenEntregado,
                                'UnidadDeMedida': tanques['entregas'].SumaVolumenEntregado_UM
                            },
                            'TotalDocumentos':tanques['entregas'].TotalDocumentos,
                            'SumaVentas': tanques['entregas'].SumaVentas,
                            'Entrega': [{
                                'NumeroDeRegistro':entrega.Id,
                                'TipoDeRegistro':entrega.TipoDeRegistro,
                                'VolumenInicialTanque': {
                                    'ValorNumerico':entrega.VolumenInicialTanque,
                                    'UnidadDeMedida':entrega.VolumenInicialTanque_UM
                                },
                                'VolumenFinalTanque':entrega.VolumenFinalTanque,
                                'VolumenEntregado': {
                                    'ValorNumerico':entrega.VolumenEntregado,
                                    'UnidadDeMedida': entrega.VolumenEntregado_UM
                                },
                                'Temperatura':entrega.Temperatura ,
                                'PresionAbsoluta':entrega.PresionAbsoluta ,
                                'FechaYHoraInicialEntrega':entrega.FechaYHoraInicialEntrega.astimezone().isoformat(),
                                'FechaYHoraFinalEntrega': entrega.FechaYHoraFinalEntrega.astimezone().isoformat(),
                                'Complemento':Comp_Comercializador.Comp_Comercializacion_schema_json(id_complemento_entrega,tipo,'C',entrega,'E_cv')
                                
                            }for entrega in tanques['entrega']]
                        }
                    }
                    tanque_item = eliminar_claves_vacias(tanque_item)
                    tanque_reporte.append(tanque_item)
                producto_item = {
                    'ClaveProducto':producto['producto'].ClaveProducto,
                    'ClaveSubProducto':producto['producto'].ClaveSubProducto,
                    'DieselConCombustibleNoFosil':producto["producto"].DieselConCombustibleNoFosil if producto["producto"].ClaveProducto == 'PR03' else '',
                    'ComposDeCombustibleNoFosilEnDiesel':producto["producto"].ComposDeCombustibleNoFosilEnDiesel if producto["producto"].ClaveProducto == 'PR03' and producto["producto"].GasolinaConCombustibleNoFosil == 'Sí' else '',#Si DieselConCombustibleNofosil es si
                    'ComposOctanajeGasolina':producto["producto"].ComposOctanajeGasolina if producto["producto"].ClaveProducto == 'PR07' else '',
                    'GasolinaConCombustibleNoFosil':producto["producto"].GasolinaConCombustibleNoFosil if producto["producto"].ClaveProducto == 'PR07' else '',
                    'ComposDeCombustibleNoFosilEnGasolina':producto["producto"].ComposDeCombustibleNoFosilEnGasolina if producto["producto"].ClaveProducto == 'PR07' and producto["producto"].TurbosinaConCombustibleNoFosil == 'Sí' else '',#Si GasolinaConCombustibleNoFosil es si
                    'TurbosinaConCombustibleNoFosil':producto["producto"].TurbosinaConCombustibleNoFosil if producto["producto"].ClaveProducto == 'PR11' else '',
                    'ComposDeCombustibleNoFosilEnTurbosina':producto["producto"].ComposDeCombustibleNoFosilEnTurbosina if producto["producto"].ClaveProducto == 'PR11' and producto["producto"].TurbosinaConCombustibleNoFosil == 'Sí' else '',#Si TurbosinaConCombustibleNoFosil es si
                    'MarcaComercial':producto["producto"].MarcaComercial, #Si el producto o subproducto cuente con alguna marca comercial
                    'Marcaje':producto["producto"].Marcaje, #Si el producto o subproducto cuente con alguna sustancia quimica empleada como marcador
                    'ConcentracionSustanciaMarcaje':producto["producto"].ConcentracionSustanciasMarcaje,#Si Marcaje existe
                    'Tanque': tanque_reporte
                }
                producto_item = eliminar_claves_vacias(producto_item)
                productos_reporte.append(producto_item)

        return productos_reporte
    else:  []

@app_comercializador.route('/informe_de_tanque_JSON', methods=['GET','POST'])
@login_required
def informe_de_tanque_JSON():
    with VerificarPermisosUsuario("DReportediarioJSON", current_user.RolPerms) as contexto:
        if contexto is False:  # No tiene permisos
            return jsonify({'error':'El usuario actual no tiene los permisos para ejecutar esta accion.','action':'redirect'})

    componente = 'comercializador/informe_de_tanque_JSON'
    Descripcion = None
    Tipo_Evento = None

    fecha_consulta  = request.args.get('datepicker_start')
    print(type(fecha_consulta))
    
    if fecha_consulta:
        try:
            print("hola")
            DailyReportFuntionsInstance = DailyReportFuntions(2)
            controles = GeneralReport(2)
            diarios_controles = controles.GiveCV()
            diarios_JSON = DailyReportFuntionsInstance.GetDailyReportAll(fecha_consulta)
            fecha_start=  fecha_consulta + " 00:00:00"
            fecha_end = fecha_consulta + " 23:59:59"

            #print(f"fecha_inicio{fecha_start},fecha_fin{fecha_end}")
            #bitacora_JSON = cv.EventosAlarmasDistribuidor.select_events_between_dates(fecha_start,fecha_end)
            bitacora_JSON = cv.EventosComercializador.select_events_between_dates(fecha_start,fecha_end)
            
            #print("aquitadeo: "+str(type(bitacora_JSON)))
            print("aquitadeo:"+str(diarios_JSON))
            if diarios_JSON:
                id_complemento_recepcion = None
                id_complemento_entrega = None
                tipo = str('comercializador')

                for producto in diarios_JSON:
                    for tanque in producto['tanques']:
                        for recepcion in tanque['recepcion']:
                            print("====" + str(recepcion.Complemento))
                            
                            id_complemento_recepcion = 2
                            complemento_distribuidor_recepcion = Comp_Comercializador.Comp_Comercializacion_schema_json(id_complemento_recepcion,tipo,'C',recepcion,'R_cv')
                        for entrega in tanque['entrega']:
 
                            id_complemento_entrega = 2
                            print(f"aqui  {id_complemento_entrega}")
                            complemento_distribuidor_entrega = Comp_Comercializador.Comp_Comercializacion_schema_json(id_complemento_entrega,tipo,'C',entrega,'E_cv')
                        # id_complemento_entrega = 2
                           #print(f"aqui  {id_complemento_entrega}")
                print("hola2")
                gaslp = {
                    'CamposDePropanoEnGasLP':'',
                    'ComposDeButanoGasLP':''
                }

                petroleo = {
                    'DensidadDePetroleo':'',
                    'ComposDeAzufreEnPetroleo':''
                }

                gasnaturalocondensados = {
                    'ComposGasNaturalOCondensados':'', #Si seleciono contratista o asignatario en Caracter y si ClaveProducto PR09 o PR10
                    'FraccionMolar':'',
                    'PoderCalorifico':''
                }

                otros = {}
                producto_r_podercalorifico = { 
                    'ValorNumerico':'',
                    'UnidadDeMedida':''
                }
                
                producto_e_podercalorifico = { 
                    'ValorNumerico':'',
                    'UnidadDeMedida':''
                }
                productos_reporte = []

                productos_reporte = get_comercialzador_reporte_diario(fecha_consulta)
                for producto in diarios_JSON:
                    tanque_reporte = []
                    for tanques in producto['tanques']:
                        tanque_item={
                            'ClaveIdentificacionTanque':tanques['tanque'].ClaveIdentificacionTanque,
                            'Localizaciony/oDescripcionTanque':tanques['tanque'].LocalizacionYODescripcionTanque,
                            'VigenciaCalibracionTanque':tanques['tanque'].VigenciaCalibracionTanque.strftime('%Y-%m-%d %H:%M:%S'),
                            'CapacidadTotalTanque': {
                                'ValorNumerico':tanques['tanque'].CapacidadTotalTanque,
                                'UnidadDeMedida':tanques['tanque'].CapacidadTotalTanque_UM
                            },
                            'CapacidadOperativaTanque': {
                                'ValorNumerico':tanques['tanque'].CapacidadOperativaTanque,
                                'UnidadDeMedida':tanques['tanque'].CapacidadOperativaTanque_UM
                            },
                            'CapacidadUtilTanque': {
                                'ValorNumerico':tanques['tanque'].CapacidadUtilTanque,
                                'UnidadDeMedida':tanques['tanque'].CapacidadUtilTanque_UM
                            },
                            'CapacidadFondajeTanque': {
                                'ValorNumerico':tanques['tanque'].CapacidadFondajeTanque,
                                'UnidadDeMedida':tanques['tanque'].CapacidadFondajeTanque_UM
                            },
                            'CapacidadGasTalon': {
                                'ValorNumerico':tanques['tanque'].CapacidadGasTalon ,
                                'UnidadDeMedida':tanques['tanque'].CapacidadGasTalon_UM	
                            },
                            'VolumenMinimoOperacion': {
                                'ValorNumerico':tanques['tanque'].VolumenMinimoOperacion,
                                'UnidadDeMedida':tanques['tanque'].VolumenMinimoOperacion_UM
                            },
                            'EstadoTanque':tanques['tanque'].EstadoTanque,
                            'Medidores': [{
                                'SistemaMedicionTanque':medicion.SistemaMedicionTanque,
                                'LocalizODescripSistMedicionTanque':medicion.LocalizODescripSistMedicionTanque,
                                'VigenciaCalibracionSistMedicionTanque':medicion.VigenciaCalibracionSistMedicionTanque.strftime('%Y-%m-%d %H:%M:%S'),
                                'IncertidumbreMedicionSistMedicionTanque': medicion.IncertidumbreMedicionSistMedicionTanque
                            }for medicion in tanques['medicion_tanque']],
                            'Existencias': {
                                'VolumenExistenciasAnterior':tanques['existencias'].VolumenExistenciasAnterior,
                                'VolumenAcumOpsRecepcion': {
                                    'ValorNumerico':tanques['existencias'].VolumenAcumOpsRecepcion,
                                    'UnidadDeMedida':tanques['existencias'].VolumenAcumOpsRecepcion_UM
                                },
                                'HoraRecepcionAcumulado':tanques['existencias'].HoraRecepcionAcumulado,
                                'VolumenAcumOpsEntrega': {
                                    'ValorNumerico':tanques['existencias'].VolumenAcumOpsEntrega,
                                    'UnidadDeMedida':tanques['existencias'].VolumenAcumOpsEntrega_UM
                                },
                                'HoraEntregaAcumulado':tanques['existencias'].HoraEntregaAcumulado,
                                'VolumenExistencias':tanques['existencias'].VolumenExistencias,
                                'FechaYHoraEstaMedicion':tanques['existencias'].FechaYHoraEstaEdicion,
                                'FechaYHoraMedicionAnterior':tanques['existencias'].FechaYHoraEdicionAnterior
                            },
                            'Recepciones': {
                                'TotalRecepciones':tanques['recepciones'].TotalRecepciones,
                                'SumaVolumenRecepcion': {
                                    'ValorNumerico':tanques['recepciones'].SumaVolumenRecepcion,
                                    'UnidadDeMedida':tanques['recepciones'].SumaVolumenRecepcion_UM
                                },
                                'TotalDocumentos':tanques['recepciones'].TotalDocumentos,
                                'SumaCompras':tanques['recepciones'].SumaCompras ,
                                'Recepcion': [{
                                    'NumeroDeRegistro':recepcion.Id,
                                    'TipoDeRegistro':recepcion.TipoDeRegistro,
                                    'VolumenInicialTanque': {
                                        'ValorNumerico':recepcion.VolumenInicialTanque,
                                        'UnidadDeMedida': recepcion.VolumenInicialTanque_UM
                                    },
                                    'VolumenFinalTanque':recepcion.VolumenFinalTanque,
                                    'VolumenRecepcion': {
                                        'ValorNumerico':recepcion.VolumenRecepcion,
                                        'UnidadDeMedida':recepcion.VolumenRecepcion_UM
                                    },
                                    'Temperatura':recepcion.Temperatura ,
                                    'PresionAbsoluta':recepcion.PresionAbsoluta ,
                                    'FechaYHoraInicioRecepcion':recepcion.FechaYHoraInicialRecepcion.astimezone().isoformat(),
                                    'FechaYHoraFinalRecepcion':recepcion.FechaYHoraFinalRecepcion.astimezone().isoformat(), 
                                    'Complemento':Comp_Distribucion.Comp_Distribucion_schema_json(id_complemento_recepcion,tipo,'D',recepcion)
                                }for recepcion in tanques['recepcion']]
                            },
                            'Entregas': {
                                'TotalEntregas':tanques['entregas'].TotalEntregas,
                                'SumaVolumenEntregado': {
                                    'ValorNumerico':tanques['entregas'].SumaVolumenEntregado,
                                    'UnidadDeMedida': tanques['entregas'].SumaVolumenEntregado_UM
                                },
                                'TotalDocumentos':tanques['entregas'].TotalDocumentos,
                                'SumaVentas': tanques['entregas'].SumaVentas,
                                'Entrega': [{
                                    'NumeroDeRegistro':entrega.Id,
                                    'TipoDeRegistro':entrega.TipoDeRegistro,
                                    'VolumenInicialTanque': {
                                        'ValorNumerico':entrega.VolumenInicialTanque,
                                        'UnidadDeMedida':entrega.VolumenInicialTanque_UM
                                    },
                                    'VolumenFinalTanque':entrega.VolumenFinalTanque,
                                    'VolumenEntregado': {
                                        'ValorNumerico':entrega.VolumenEntregado,
                                        'UnidadDeMedida': entrega.VolumenEntregado_UM
                                    },
                                    'Temperatura':entrega.Temperatura ,
                                    'PresionAbsoluta':entrega.PresionAbsoluta ,
                                    'FechaYHoraInicialEntrega':entrega.FechaYHoraInicialEntrega.astimezone().isoformat(),
                                    'FechaYHoraFinalEntrega': entrega.FechaYHoraFinalEntrega.astimezone().isoformat(),
                                    'Complemento':Comp_Distribucion.Comp_Distribucion_schema_json(id_complemento_entrega,tipo,'C',entrega)
                                    
                                }for entrega in tanques['entrega']]
                            }
                        }
                        tanque_item = eliminar_claves_vacias(tanque_item)
                        tanque_reporte.append(tanque_item)
                    producto_item = {
                        'ClaveProducto':producto['producto'].ClaveProducto,
                        'ClaveSubProducto':producto['producto'].ClaveSubProducto,
                        'DieselConCombustibleNoFosil':producto["producto"].DieselConCombustibleNoFosil if producto["producto"].ClaveProducto == 'PR03' else '',
                        'ComposDeCombustibleNoFosilEnDiesel':producto["producto"].ComposDeCombustibleNoFosilEnDiesel if producto["producto"].ClaveProducto == 'PR03' and producto["producto"].GasolinaConCombustibleNoFosil == 'Sí' else '',#Si DieselConCombustibleNofosil es si
                        'ComposOctanajeGasolina':producto["producto"].ComposOctanajeGasolina if producto["producto"].ClaveProducto == 'PR07' else '',
                        'GasolinaConCombustibleNoFosil':producto["producto"].GasolinaConCombustibleNoFosil if producto["producto"].ClaveProducto == 'PR07' else '',
                        'ComposDeCombustibleNoFosilEnGasolina':producto["producto"].ComposDeCombustibleNoFosilEnGasolina if producto["producto"].ClaveProducto == 'PR07' and producto["producto"].TurbosinaConCombustibleNoFosil == 'Sí' else '',#Si GasolinaConCombustibleNoFosil es si
                        'TurbosinaConCombustibleNoFosil':producto["producto"].TurbosinaConCombustibleNoFosil if producto["producto"].ClaveProducto == 'PR11' else '',
                        'ComposDeCombustibleNoFosilEnTurbosina':producto["producto"].ComposDeCombustibleNoFosilEnTurbosina if producto["producto"].ClaveProducto == 'PR11' and producto["producto"].TurbosinaConCombustibleNoFosil == 'Sí' else '',#Si TurbosinaConCombustibleNoFosil es si
                        'MarcaComercial':producto["producto"].MarcaComercial, #Si el producto o subproducto cuente con alguna marca comercial
                        'Marcaje':producto["producto"].Marcaje, #Si el producto o subproducto cuente con alguna sustancia quimica empleada como marcador
                        'ConcentracionSustanciaMarcaje':producto["producto"].ConcentracionSustanciasMarcaje,#Si Marcaje existe
                        'Tanque': tanque_reporte
                    }
                    producto_item = eliminar_claves_vacias(producto_item)
                    productos_reporte.append(producto_item)

                logging.debug(f"productos_reporte: {productos_reporte}")
                bitacora_reporte= [] 
                if bitacora_JSON:
                    #print(f"aqui tadeos2s{bitacora_JSON}")
                    for bitacora in bitacora_JSON: 
                            #print(f"aqui tadeos3s{bitacora}")
                            tipos = ['7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21']
                            bitacora_item={
                                            'NumeroRegistro':bitacora['numero_registro']  ,
                                            'FechaYHoraEvento':bitacora['fecha'],
                                            'UsuarioResponsable':bitacora['UsuarioResponsable'] if bitacora['is_event'] else '',
                                            'TipoEvento':bitacora['tipo'],
                                            'DescripcionEvento':bitacora['mensaje'],
                                            **({'IdentificacionComponenteAlarma': bitacora['identificacion']} if str(bitacora['tipo']) in tipos else {})
                            }
                            bitacora_item = eliminar_claves_vacias(bitacora_item)
                            bitacora_reporte.append(bitacora_item)
                ControlesVolumetricos1 = {
                    'Version': diarios_controles["Version"],
                    'RfcContribuyente':diarios_controles["RfcContribuyente"] ,
                    'RfcRepresentanteLegal':diarios_controles["RfcRepresentanteLegal"],
                    'RfcProveedor':diarios_controles["RfcProveedor"],
                    'RfcProveedores':[diarios_controles["RfcProveedores"]],
                    'Caracter':diarios_controles["TipoCaracter"],
                    **({'ModalidadPermiso': diarios_controles["ModalidadPermiso"]} if diarios_controles["TipoCaracter"] == 'permisionario' else {}),
                    **({'NumPermiso': diarios_controles["NumPermiso"]} if diarios_controles["TipoCaracter"] == 'permisionario' else {}),
                    **({'NumContratoOAsignacion': diarios_controles["NumContratoOAsignacion"]} if diarios_controles["TipoCaracter"] in ['contratista', 'asignatario'] else {}),
                    **({'InstalacionAlmacenGasNatural': diarios_controles["InstalacionAlmacenGasNatural"]} if diarios_controles["TipoCaracter"] == 'usuario' else {}),
                    'ClaveInstalacion': diarios_controles["ClaveInstalacion"],
                    'DescripcionInstalacion':diarios_controles["DescripcionInstalacion"],
                    'Geolocalizacion': [{
                        'GeolocalizacionLatitud':diarios_controles["GeolocalizacionLatitud"],
                        'GeolocalizacionLongitud':diarios_controles["GeolocalizacionLongitud"]
                    }],
                    'NumeroPozos':diarios_controles["NumeroPozos"],
                    'NumeroTanques':diarios_controles["NumeroTanques"],
                    'NumeroDuctosEntradaSalida': diarios_controles["NumeroDuctosEntradaSalida"],
                    'NumeroDuctosTransporteDistribucion':0,
                    'NumeroDispensarios':diarios_controles["NumeroDispensarios"],
                    'FechaYHoraCorte':datetime.now().astimezone().isoformat(),
                    'Producto': productos_reporte,
                    'Bitacora': bitacora_reporte      
                }

                # Validar los datos contra el esquema
                try:
                    
                    validate(instance=ControlesVolumetricos1, schema=estructura_json_diario)
                    json_str = json.dumps(ControlesVolumetricos1, default=str)
                    fecha_actual = datetime.now().strftime("%Y_%m_%d")

                    file_name = f"D_1AC51FC0-85BF-44E7-AE79-50B030A47C78_DDP860722DN4_ADT161011FC2_{fecha_actual}.json"
                    print("Totodo bien 3")
                    response = Response(
                        json_str,
                        mimetype='application/json',
                        headers={
                            'Content-Disposition': f'attachment; filename={file_name}',
                            'Content-Type': 'application/json'  # Asegúrate de que el Content-Type sea JSON
                        }
                    )

                    #Ini - Cambio jul-25
                    Descripcion = f'Obtención y recuperación de reporte volumetrico JSON diario de comercializador del día {fecha_consulta}  '
                    Tipo_Evento = 3
                    EventosComercializador.add(
                        datetime.now(), current_user.Username, Tipo_Evento, Descripcion, componente
                    )
                    #Fin - Cambio jul-25

                    return response
                except ValidationError as e:
                    error_trace = traceback.format_exc()
                    # Logging detallado
                    logging.debug(f"ValidationError: {str(e)}")
                    logging.debug(f"Traceback: {error_trace}")
                    return jsonify({"error":str(e)}), 400
            
            else: return jsonify({'error': 'No se encontraron datos para los parámetros proporcionados, pero puedes generar para la fecha que se selecciono con el botón de "GENERAR".'})
        except ValueError as e:
            error_trace = traceback.format_exc()
            # Logging detallado
            logging.debug(f"ValueError: {str(e)}")
            logging.debug(f"Traceback: {error_trace}")
            return jsonify({'error': str(e)})
        except Exception as e:
            error_trace = traceback.format_exc()
            # Logging detallado
            logging.debug(f"Exception: {str(e)}")
            logging.debug(f"Traceback: {error_trace}")
    else:  return  jsonify({'error': 'Faltan parámetros necesarios. Por favor, complete todos los campos.'})

"""
@app_comercializador.route('/informe_de_tanque_JSON', methods=['GET','POST'])
@login_required
def informe_de_tanque_JSON():
    with VerificarPermisosUsuario("CReportediarioJSON", current_user.RolPerms) as contexto:
        if contexto is False:  # No tiene permisos
            return jsonify({'error':'El usuario actual no tiene los permisos para ejecutar esta accion.','action':'redirect'})

    componente = 'comercializador/informe_de_tanque_JSON'
    Descripcion = None
    Tipo_Evento = None

    fecha_consulta  = request.args.get('datepicker_start')
    print(type(fecha_consulta))
    
    if fecha_consulta:
        try:
            print("hola")
            DailyReportFuntionsInstance = DailyReportFuntions(2)
            controles = GeneralReport(2)
            diarios_controles = controles.GiveCV()
            diarios_JSON = DailyReportFuntionsInstance.GetDailyReportAll(fecha_consulta)
            fecha_start=  fecha_consulta + " 00:00:00"
            fecha_end = fecha_consulta + " 23:59:59"

            #print(f"fecha_inicio{fecha_start},fecha_fin{fecha_end}")
            bitacora_JSON = cv.EventosAlarmasDistribuidor.select_events_and_alarms_between_dates(fecha_start,fecha_end)
            #print("aquitadeo: "+str(type(bitacora_JSON)))
            print("aquitadeo:"+str(diarios_JSON))
            if diarios_JSON:
                id_complemento_recepcion = None
                id_complemento_entrega = None
                tipo = str('comercializador')

                for producto in diarios_JSON:
                    for tanque in producto['tanques']:
                        for recepcion in tanque['recepcion']:
                            print("====" + str(recepcion.Complemento))
                            
                            id_complemento_recepcion = 2
                            complemento_distribuidor_recepcion = Comp_Comercializador.Comp_Comercializacion_schema_json(id_complemento_recepcion,tipo,'C',recepcion,'R_cv')
                        for entrega in tanque['entrega']:
 
                            id_complemento_entrega = 2
                            print(f"aqui  {id_complemento_entrega}")
                            complemento_distribuidor_entrega = Comp_Comercializador.Comp_Comercializacion_schema_json(id_complemento_entrega,tipo,'C',entrega,'E_cv')

                gaslp = {
                    'CamposDePropanoEnGasLP':'',
                    'ComposDeButanoGasLP':''
                }

                petroleo = {
                    'DensidadDePetroleo':'',
                    'ComposDeAzufreEnPetroleo':''
                }

                gasnaturalocondensados = {
                    'ComposGasNaturalOCondensados':'', #Si seleciono contratista o asignatario en Caracter y si ClaveProducto PR09 o PR10
                    'FraccionMolar':'',
                    'PoderCalorifico':''
                }

                otros = {}
                producto_r_podercalorifico = { 
                    'ValorNumerico':'',
                    'UnidadDeMedida':''
                }
                
                producto_e_podercalorifico = { 
                    'ValorNumerico':'',
                    'UnidadDeMedida':''
                }
                productos_reporte = []
                for producto in diarios_JSON:
                    tanque_reporte = []
                    for tanques in producto['tanques']:
                        tanque_item={
                            'ClaveIdentificacionTanque':tanques['tanque'].ClaveIdentificacionTanque,
                            'Localizaciony/oDescripcionTanque':tanques['tanque'].LocalizacionYODescripcionTanque,
                            'VigenciaCalibracionTanque':tanques['tanque'].VigenciaCalibracionTanque.strftime('%Y-%m-%d %H:%M:%S'),
                            'CapacidadTotalTanque': {
                                'ValorNumerico':tanques['tanque'].CapacidadTotalTanque,
                                'UnidadDeMedida':tanques['tanque'].CapacidadTotalTanque_UM
                            },
                            'CapacidadOperativaTanque': {
                                'ValorNumerico':tanques['tanque'].CapacidadOperativaTanque,
                                'UnidadDeMedida':tanques['tanque'].CapacidadOperativaTanque_UM
                            },
                            'CapacidadUtilTanque': {
                                'ValorNumerico':tanques['tanque'].CapacidadUtilTanque,
                                'UnidadDeMedida':tanques['tanque'].CapacidadUtilTanque_UM
                            },
                            'CapacidadFondajeTanque': {
                                'ValorNumerico':tanques['tanque'].CapacidadFondajeTanque,
                                'UnidadDeMedida':tanques['tanque'].CapacidadFondajeTanque_UM
                            },
                            'CapacidadGasTalon': {
                                'ValorNumerico':tanques['tanque'].CapacidadGasTalon ,
                                'UnidadDeMedida':tanques['tanque'].CapacidadGasTalon_UM	
                            },
                            'VolumenMinimoOperacion': {
                                'ValorNumerico':tanques['tanque'].VolumenMinimoOperacion,
                                'UnidadDeMedida':tanques['tanque'].VolumenMinimoOperacion_UM
                            },
                            'EstadoTanque':tanques['tanque'].EstadoTanque,
                            'Medidores': [{
                                'SistemaMedicionTanque':medicion.SistemaMedicionTanque,
                                'LocalizODescripSistMedicionTanque':medicion.LocalizODescripSistMedicionTanque,
                                'VigenciaCalibracionSistMedicionTanque':medicion.VigenciaCalibracionSistMedicionTanque.strftime('%Y-%m-%d %H:%M:%S'),
                                'IncertidumbreMedicionSistMedicionTanque': medicion.IncertidumbreMedicionSistMedicionTanque
                            }for medicion in tanques['medicion_tanque']],
                            'Existencias': {
                                'VolumenExistenciasAnterior':tanques['existencias'].VolumenExistenciasAnterior,
                                'VolumenAcumOpsRecepcion': {
                                    'ValorNumerico':tanques['existencias'].VolumenAcumOpsRecepcion,
                                    'UnidadDeMedida':tanques['existencias'].VolumenAcumOpsRecepcion_UM
                                },
                                'HoraRecepcionAcumulado':tanques['existencias'].HoraRecepcionAcumulado,
                                'VolumenAcumOpsEntrega': {
                                    'ValorNumerico':tanques['existencias'].VolumenAcumOpsEntrega,
                                    'UnidadDeMedida':tanques['existencias'].VolumenAcumOpsEntrega_UM
                                },
                                'HoraEntregaAcumulado':tanques['existencias'].HoraEntregaAcumulado,
                                'VolumenExistencias':tanques['existencias'].VolumenExistencias,
                                'FechaYHoraEstaMedicion':tanques['existencias'].FechaYHoraEstaEdicion,
                                'FechaYHoraMedicionAnterior':tanques['existencias'].FechaYHoraEdicionAnterior
                            },
                            'Recepciones': {
                                'TotalRecepciones':tanques['recepciones'].TotalRecepciones,
                                'SumaVolumenRecepcion': {
                                    'ValorNumerico':tanques['recepciones'].SumaVolumenRecepcion,
                                    'UnidadDeMedida':tanques['recepciones'].SumaVolumenRecepcion_UM
                                },
                                'TotalDocumentos':tanques['recepciones'].TotalDocumentos,
                                'SumaCompras':tanques['recepciones'].SumaCompras ,
                                'Recepcion': [{
                                    'NumeroDeRegistro':recepcion.Id,
                                    'TipoDeRegistro':recepcion.TipoDeRegistro,
                                    'VolumenInicialTanque': {
                                        'ValorNumerico':recepcion.VolumenInicialTanque,
                                        'UnidadDeMedida': recepcion.VolumenInicialTanque_UM
                                    },
                                    'VolumenFinalTanque':recepcion.VolumenFinalTanque,
                                    'VolumenRecepcion': {
                                        'ValorNumerico':recepcion.VolumenRecepcion,
                                        'UnidadDeMedida':recepcion.VolumenRecepcion_UM
                                    },
                                    'Temperatura':recepcion.Temperatura ,
                                    'PresionAbsoluta':recepcion.PresionAbsoluta ,
                                    'FechaYHoraInicioRecepcion':recepcion.FechaYHoraInicialRecepcion.astimezone().isoformat(),
                                    'FechaYHoraFinalRecepcion':recepcion.FechaYHoraFinalRecepcion.astimezone().isoformat(), 
                                    'Complemento':Comp_Comercializador.Comp_Comercializacion_schema_json(id_complemento_recepcion,tipo,'C',recepcion,'R_cv')
                                }for recepcion in tanques['recepcion']]
                            },
                            'Entregas': {
                                'TotalEntregas':tanques['entregas'].TotalEntregas,
                                'SumaVolumenEntregado': {
                                    'ValorNumerico':tanques['entregas'].SumaVolumenEntregado,
                                    'UnidadDeMedida': tanques['entregas'].SumaVolumenEntregado_UM
                                },
                                'TotalDocumentos':tanques['entregas'].TotalDocumentos,
                                'SumaVentas': tanques['entregas'].SumaVentas,
                                'Entrega': [{
                                    'NumeroDeRegistro':entrega.Id,
                                    'TipoDeRegistro':entrega.TipoDeRegistro,
                                    'VolumenInicialTanque': {
                                        'ValorNumerico':entrega.VolumenInicialTanque,
                                        'UnidadDeMedida':entrega.VolumenInicialTanque_UM
                                    },
                                    'VolumenFinalTanque':entrega.VolumenFinalTanque,
                                    'VolumenEntregado': {
                                        'ValorNumerico':entrega.VolumenEntregado,
                                        'UnidadDeMedida': entrega.VolumenEntregado_UM
                                    },
                                    'Temperatura':entrega.Temperatura ,
                                    'PresionAbsoluta':entrega.PresionAbsoluta ,
                                    'FechaYHoraInicialEntrega':entrega.FechaYHoraInicialEntrega.astimezone().isoformat(),
                                    'FechaYHoraFinalEntrega': entrega.FechaYHoraFinalEntrega.astimezone().isoformat(),
                                    'Complemento':Comp_Comercializador.Comp_Comercializacion_schema_json(id_complemento_entrega,tipo,'C',entrega,'E_cv')
                                    
                                }for entrega in tanques['entrega']]
                            }
                        }
                        tanque_item = eliminar_claves_vacias(tanque_item)
                        tanque_reporte.append(tanque_item)
                    producto_item = {
                        'ClaveProducto':producto['producto'].ClaveProducto,
                        'ClaveSubProducto':producto['producto'].ClaveSubProducto,
                        'DieselConCombustibleNoFosil':producto["producto"].DieselConCombustibleNoFosil if producto["producto"].ClaveProducto == 'PR03' else '',
                        'ComposDeCombustibleNoFosilEnDiesel':producto["producto"].ComposDeCombustibleNoFosilEnDiesel if producto["producto"].ClaveProducto == 'PR03' and producto["producto"].GasolinaConCombustibleNoFosil == 'Sí' else '',#Si DieselConCombustibleNofosil es si
                        'ComposOctanajeGasolina':producto["producto"].ComposOctanajeGasolina if producto["producto"].ClaveProducto == 'PR07' else '',
                        'GasolinaConCombustibleNoFosil':producto["producto"].GasolinaConCombustibleNoFosil if producto["producto"].ClaveProducto == 'PR07' else '',
                        'ComposDeCombustibleNoFosilEnGasolina':producto["producto"].ComposDeCombustibleNoFosilEnGasolina if producto["producto"].ClaveProducto == 'PR07' and producto["producto"].TurbosinaConCombustibleNoFosil == 'Sí' else '',#Si GasolinaConCombustibleNoFosil es si
                        'TurbosinaConCombustibleNoFosil':producto["producto"].TurbosinaConCombustibleNoFosil if producto["producto"].ClaveProducto == 'PR11' else '',
                        'ComposDeCombustibleNoFosilEnTurbosina':producto["producto"].ComposDeCombustibleNoFosilEnTurbosina if producto["producto"].ClaveProducto == 'PR11' and producto["producto"].TurbosinaConCombustibleNoFosil == 'Sí' else '',#Si TurbosinaConCombustibleNoFosil es si
                        'MarcaComercial':producto["producto"].MarcaComercial, #Si el producto o subproducto cuente con alguna marca comercial
                        'Marcaje':producto["producto"].Marcaje, #Si el producto o subproducto cuente con alguna sustancia quimica empleada como marcador
                        'ConcentracionSustanciaMarcaje':producto["producto"].ConcentracionSustanciasMarcaje,#Si Marcaje existe
                        'Tanque': tanque_reporte
                    }
                    producto_item = eliminar_claves_vacias(producto_item)
                    productos_reporte.append(producto_item)

                logging.debug(f"productos_reporte: {productos_reporte}")
                bitacora_reporte= [] 
                if bitacora_JSON:
                    #print(f"aqui tadeos2s{bitacora_JSON}")
                    for bitacora in bitacora_JSON: 
                            #print(f"aqui tadeos3s{bitacora}")
                            tipos = ['7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21']
                            bitacora_item={
                                            'NumeroRegistro':bitacora['numero_registro']  ,
                                            'FechaYHoraEvento':bitacora['fecha'],
                                            'UsuarioResponsable':bitacora['UsuarioResponsable'] if bitacora['is_event'] else '',
                                            'TipoEvento':bitacora['tipo'],
                                            'DescripcionEvento':bitacora['mensaje'],
                                            **({'IdentificacionComponenteAlarma': bitacora['identificacion']} if str(bitacora['tipo']) in tipos else {})
                            }
                            bitacora_item = eliminar_claves_vacias(bitacora_item)
                            bitacora_reporte.append(bitacora_item)
                ControlesVolumetricos1 = {
                    'Version': diarios_controles["Version"],
                    'RfcContribuyente':diarios_controles["RfcContribuyente"] ,
                    'RfcRepresentanteLegal':diarios_controles["RfcRepresentanteLegal"],
                    'RfcProveedor':diarios_controles["RfcProveedor"],
                    'RfcProveedores':[diarios_controles["RfcProveedores"]],
                    'Caracter':diarios_controles["TipoCaracter"],
                    **({'ModalidadPermiso': diarios_controles["ModalidadPermiso"]} if diarios_controles["TipoCaracter"] == 'permisionario' else {}),
                    **({'NumPermiso': diarios_controles["NumPermiso"]} if diarios_controles["TipoCaracter"] == 'permisionario' else {}),
                    **({'NumContratoOAsignacion': diarios_controles["NumContratoOAsignacion"]} if diarios_controles["TipoCaracter"] in ['contratista', 'asignatario'] else {}),
                    **({'InstalacionAlmacenGasNatural': diarios_controles["InstalacionAlmacenGasNatural"]} if diarios_controles["TipoCaracter"] == 'usuario' else {}),
                    'ClaveInstalacion': diarios_controles["ClaveInstalacion"],
                    'DescripcionInstalacion':diarios_controles["DescripcionInstalacion"],
                    'Geolocalizacion': [{
                        'GeolocalizacionLatitud':diarios_controles["GeolocalizacionLatitud"],
                        'GeolocalizacionLongitud':diarios_controles["GeolocalizacionLongitud"]
                    }],
                    'NumeroPozos':diarios_controles["NumeroPozos"],
                    'NumeroTanques':diarios_controles["NumeroTanques"],
                    'NumeroDuctosEntradaSalida': diarios_controles["NumeroDuctosEntradaSalida"],
                    'NumeroDuctosTransporteDistribucion':0,
                    'NumeroDispensarios':diarios_controles["NumeroDispensarios"],
                    'FechaYHoraCorte':datetime.now().astimezone().isoformat(),
                    'Producto': productos_reporte,
                    'Bitacora': bitacora_reporte      
                }

                # Validar los datos contra el esquema
                try:
                    
                    validate(instance=ControlesVolumetricos1, schema=estructura_json_diario)
                    json_str = json.dumps(ControlesVolumetricos1, default=str)
                    fecha_actual = datetime.now().strftime("%Y_%m_%d")

                    file_name = f"D_1AC51FC0-85BF-44E7-AE79-50B030A47C78_DDP860722DN4_ADT161011FC2_{fecha_actual}.json"
                    print("Totodo bien 3")
                    response = Response(
                        json_str,
                        mimetype='application/json',
                        headers={
                            'Content-Disposition': f'attachment; filename={file_name}',
                            'Content-Type': 'application/json'  # Asegúrate de que el Content-Type sea JSON
                        }
                    )
                    return response
                except ValidationError as e:
                    error_trace = traceback.format_exc()
                    # Logging detallado
                    logging.debug(f"ValidationError: {str(e)}")
                    logging.debug(f"Traceback: {error_trace}")
                    return jsonify({"error":str(e)}), 400
            
            else: return jsonify({'error': 'No se encontraron datos para los parámetros proporcionados, pero puedes generar para la fecha que selecionaste.'})
        except ValueError as e:
            error_trace = traceback.format_exc()
            # Logging detallado
            logging.debug(f"ValueError: {str(e)}")
            logging.debug(f"Traceback: {error_trace}")
            return jsonify({'error': str(e)})
        except Exception as e:
            error_trace = traceback.format_exc()
            # Logging detallado
            logging.debug(f"Exception: {str(e)}")
            logging.debug(f"Traceback: {error_trace}")
    else:  return  jsonify({'error': 'Faltan parámetros necesarios. Por favor, complete todos los campos.'})

"""

@app_comercializador.route('/informe_de_tanque_XML', methods=['GET','POST'])
@login_required
def informe_de_tanque_XML():
    with VerificarPermisosUsuario("DReportediarioXML", current_user.RolPerms) as contexto:
        if contexto is False:  # No tiene permisos
            return jsonify({'error':'El usuario actual no tiene los permisos para ejecutar esta accion.','action':'redirect'})

    componente = 'comercializador/informe_de_tanque_XML'
    Descripcion = None
    Tipo_Evento = None
    
    fecha_consulta  = request.args.get('datepicker_start')
    print(fecha_consulta)
    if fecha_consulta:
        try:
            DailyReportFuntionsInstance = DailyReportFuntions(2)
            controles = GeneralReport(2)
            diarios_controles = controles.GiveCV()
            diarios_JSON = DailyReportFuntionsInstance.GetDailyReportAll(fecha_consulta)
            logging.debug("diarios_JSON", str(diarios_JSON))
            fecha_start=  fecha_consulta + " 00:00:00"
            fecha_end = fecha_consulta + " 23:59:59"
            #bitacora_XML = cv.EventosAlarmasDistribuidor.select_events_and_alarms_between_dates(fecha_start,fecha_end)
            bitacora_XML = cv.EventosComercializador.select_events_between_dates(fecha_start,fecha_end)

            if diarios_JSON:
                
                # Definir el esquema XSD
                #schema_file = 'src/static/schemes/distribuidor/Mensual.xsd'
                schema_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..","static/schemes/comercializador/Diario.xsd"))

                schema = xmlschema.XMLSchema11(schema_file)

                #complemento_distribuidor = Comp_Distribucion.Diario_Comp_Distribuidor_XML()
                #nuevo_elemento_complemento = ET.fromstring(complemento_distribuidor)

                # Crear el XML basado en el esquema

                xsi = 'http://www.w3.org/2001/XMLSchema-instance'
                ET.register_namespace('xsi', xsi)

                xsd = 'http://www.w3.org/2001/XMLSchema'
                ET.register_namespace('xsd',xsd)
                tr = 'Complemento_Transporte'
                ET.register_namespace('tr',tr)

                alm= 'Complemento_Almacenamiento'
                ET.register_namespace('alm',alm)

                CDLRGN = 'Complemento_CDLRGN'
                ET.register_namespace('CDLRGN',CDLRGN)

                co = 'Complemento_Comercializacion'
                ET.register_namespace('co',co)

                dis = 'Complemento_Distribucion'
                ET.register_namespace('dis',dis)

                exp = 'Complemento_Expendio'
                ET.register_namespace('exp',exp)

                ext = 'Complemento_Extraccion'
                ET.register_namespace('ext',ext)

                ref = 'Complemento_Refinacion'
                ET.register_namespace('ref',ref)

                covol = 'https://repositorio.cloudb.sat.gob.mx/Covol/xml/Diarios'
                ET.register_namespace('Covol', covol)


                CONTROLES_VOLUMETRICOS = ET.Element('{%s}ControlesVolumetricos' % covol )

                
                # Agregar elementos al XML
                ET.SubElement(CONTROLES_VOLUMETRICOS, '{%s}Version'% covol).text = str(diarios_controles["Version"])
                ET.SubElement(CONTROLES_VOLUMETRICOS, '{%s}RfcContribuyente'% covol).text = diarios_controles["RfcContribuyente"]
                ET.SubElement(CONTROLES_VOLUMETRICOS, '{%s}RfcRepresentanteLegal'% covol).text =diarios_controles["RfcRepresentanteLegal"]
                ET.SubElement(CONTROLES_VOLUMETRICOS, '{%s}RfcProveedor'% covol).text = diarios_controles["RfcProveedor"]
                ET.SubElement(CONTROLES_VOLUMETRICOS, '{%s}RfcProveedores'% covol).text = diarios_controles["RfcProveedores"]


                # Crear el elemento 'Caracter' y sus subelementos
                caracter = ET.SubElement(CONTROLES_VOLUMETRICOS, '{%s}Caracter'% covol)
                ET.SubElement(caracter, '{%s}TipoCaracter'% covol).text = str(diarios_controles["TipoCaracter"])
                if diarios_controles["TipoCaracter"] == 'permisionario':
                    ET.SubElement(caracter, '{%s}ModalidadPermiso'% covol).text = str(diarios_controles["ModalidadPermiso"])
                    ET.SubElement(caracter, '{%s}NumPermiso'% covol).text = str(diarios_controles["NumPermiso"])
                if diarios_controles["TipoCaracter"] in ['contratista', 'asignatario']:
                    ET.SubElement(caracter, '{%s}NumContratoOAsignacion'% covol).text = str(diarios_controles["NumContratoOAsignacion"])
                if diarios_controles["TipoCaracter"] == 'usuario':
                    ET.SubElement(caracter, '{%s}InstalacionAlmacenGasNatural'% covol).text = str(diarios_controles["InstalacionAlmacenGasNatural"])
                    
                ET.SubElement(CONTROLES_VOLUMETRICOS, '{%s}ClaveInstalacion'% covol).text = diarios_controles["ClaveInstalacion"]
                ET.SubElement(CONTROLES_VOLUMETRICOS, '{%s}DescripcionInstalacion'% covol).text = diarios_controles["DescripcionInstalacion"]

                Geolocalizacion = ET.SubElement(CONTROLES_VOLUMETRICOS, '{%s}Geolocalizacion'% covol)
                ET.SubElement(Geolocalizacion, '{%s}GeolocalizacionLatitud'% covol).text = str(diarios_controles["GeolocalizacionLatitud"])
                ET.SubElement(Geolocalizacion, '{%s}GeolocalizacionLongitud'% covol).text = str(diarios_controles["GeolocalizacionLongitud"])

                ET.SubElement(CONTROLES_VOLUMETRICOS, '{%s}NumeroPozos'% covol).text = str(diarios_controles["NumeroPozos"])
                ET.SubElement(CONTROLES_VOLUMETRICOS, '{%s}NumeroTanques'% covol).text = str(diarios_controles["NumeroTanques"])  
                ET.SubElement(CONTROLES_VOLUMETRICOS, '{%s}NumeroDuctosEntradaSalida'% covol).text = str(diarios_controles["NumeroDuctosEntradaSalida"]) 
                ET.SubElement(CONTROLES_VOLUMETRICOS, '{%s}NumeroDuctosTransporteDistribucion'% covol).text = str(diarios_controles["NumeroDuctosTransporteDistribucion"]) 
                ET.SubElement(CONTROLES_VOLUMETRICOS, '{%s}NumeroDispensarios'% covol).text = str(diarios_controles["NumeroDispensarios"]) 
                            
                # Obtener la fecha y hora actual con la zona horaria
                fecha_hora_corte = datetime.now().astimezone().strftime('%Y-%m-%dT%H:%M:%S%z')
                # Formatear la zona horaria para incluir dos puntos
                fecha_hora_corte = f"{fecha_hora_corte[:-2]}:{fecha_hora_corte[-2:]}"
                # Agregar el elemento al XML
                ET.SubElement(CONTROLES_VOLUMETRICOS, '{%s}FechaYHoraCorte' % covol).text = fecha_hora_corte
                
                print(diarios_JSON)
                for producto_ in diarios_JSON:
                    PRODUCTO = ET.SubElement(CONTROLES_VOLUMETRICOS, '{%s}PRODUCTO'% covol)
                    clave =  producto_['producto'].ClaveProducto

                    ET.SubElement(PRODUCTO, '{%s}ClaveProducto'% covol).text = clave
                    ET.SubElement(PRODUCTO, '{%s}ClaveSubProducto'% covol).text = producto_['producto'].ClaveSubProducto
                    if clave == "PR07":
                        Gasolina = ET.SubElement(PRODUCTO, '{%s}Gasolina'% covol)
                        ET.SubElement(Gasolina, '{%s}ComposOctanajeGasolina'% covol).text = str(producto_['producto'].ComposOctanajeGasolina)
                        ET.SubElement(Gasolina, '{%s}GasolinaConCombustibleNoFosil'% covol).text = producto_['producto'].GasolinaConCombustibleNoFosil
                        if producto_['producto'].GasolinaConCombustibleNoFosil == 'Si':
                            ET.SubElement(Gasolina, '{%s}ComposDeCombustibleNoFosilEnGasolina'% covol).text = str(producto_['producto'].ComposDeCombustibleNoFosilEnGasolina)
                    elif clave == "PR03":                       
                        Diesel = ET.SubElement(PRODUCTO, '{%s}Diesel'% covol)
                        ET.SubElement(Diesel, '{%s}DieselConCombustibleNoFosil'% covol).text = producto_['producto'].DieselConCombustibleNoFosil
                        if producto_['producto'].DieselConCombustibleNoFosil == 'Si':
                            ET.SubElement(Diesel, '{%s}ComposDeCombustibleNoFosilEnDiesel'% covol).text = str(producto_['producto'].ComposDeCombustibleNoFosilEnDiesel)
                    else:
                        ET.SubElement(PRODUCTO, '{%s}Otros'% covol).text =  producto_['producto'].Otros

                    #Turbosina = ET.SubElement(PRODUCTO, '{%s}Turbosina'% covol)
                    #ET.SubElement(Turbosina, '{%s}TurbosinaConCombustibleNoFosil'% covol).text = producto_['producto'].TurbosinaConCombustibleNoFosil
                    #ET.SubElement(Diesel, '{%s}ComposDeCombustibleNoFosilEnTurbosina'% covol).text = producto_['producto'].ComposDeCombustibleNoFosilEnTurbosina

                    #GasLP = ET.SubElement(PRODUCTO, '{%s}GasLP'% covol)
                    #ET.SubElement(GasLP, '{%s}ComposDePropanoEnGasLP'% covol).text = producto_['producto'].ComposDePropanoEnGasLP
                    #ET.SubElement(Diesel, '{%s}ComposDeButanoEnGasLP'% covol).text = producto_['producto'].ComposDeButanoEnGasLp

                    #Petroleo = ET.SubElement(PRODUCTO, '{%s}Petroleo'% covol)
                    #ET.SubElement(Petroleo, '{%s}DensidadDePetroleo'% covol).text = producto_['producto'].DensidadDePetroleo
                    #ET.SubElement(Petroleo, '{%s}ComposDeAzufreEnPetroleo'% covol).text = producto_['producto'].ComposDeAzufreEnPetroleo
                    ET.SubElement(PRODUCTO, '{%s}MarcaComercial'% covol).text = producto_['producto'].MarcaComercial
                    if producto_['producto'].Marcaje:
                        ET.SubElement(PRODUCTO, '{%s}Marcaje'% covol).text = producto_['producto'].Marcaje
                        if producto_['producto'].ConcentracionSustanciasMarcaje and producto_['producto'].ConcentracionSustanciasMarcaje > 0:
                            ET.SubElement(PRODUCTO, '{%s}ConcentracionSustanciaMarcaje'% covol).text = str(producto_['producto'].ConcentracionSustanciasMarcaje)

                    for tanques in producto_['tanques']:
                        TANQUE = ET.SubElement(PRODUCTO, '{%s}TANQUE'% covol)
                        ET.SubElement(TANQUE, '{%s}ClaveIdentificacionTanque'% covol).text = tanques['tanque'].ClaveIdentificacionTanque
                        ET.SubElement(TANQUE, '{%s}LocalizacionYODescripcionTanque'% covol).text = tanques['tanque'].LocalizacionYODescripcionTanque
                        ET.SubElement(TANQUE, '{%s}VigenciaCalibracionTanque'% covol).text = str(tanques['tanque'].VigenciaCalibracionTanque.strftime('%Y-%m-%d'))

                        CapacidadTotalTanque = ET.SubElement(TANQUE, '{%s}CapacidadTotalTanque'% covol)
                        ET.SubElement(CapacidadTotalTanque, '{%s}ValorNumerico'% covol).text = str(tanques['tanque'].CapacidadTotalTanque)
                        ET.SubElement(CapacidadTotalTanque, '{%s}UM'% covol).text =  str(tanques['tanque'].CapacidadTotalTanque_UM)


                        CapacidadOperativaTanque = ET.SubElement(TANQUE, '{%s}CapacidadOperativaTanque'% covol)
                        ET.SubElement(CapacidadOperativaTanque, '{%s}ValorNumerico'% covol).text = str(tanques['tanque'].CapacidadOperativaTanque)
                        ET.SubElement(CapacidadOperativaTanque, '{%s}UM'% covol).text = str(tanques['tanque'].CapacidadOperativaTanque_UM)

                        CapacidadUtilTanque = ET.SubElement(TANQUE, '{%s}CapacidadUtilTanque'% covol)
                        ET.SubElement(CapacidadUtilTanque, '{%s}ValorNumerico'% covol).text =str(tanques['tanque'].CapacidadUtilTanque)
                        ET.SubElement(CapacidadUtilTanque, '{%s}UM'% covol).text = str(tanques['tanque'].CapacidadUtilTanque_UM)

                        CapacidadFondajeTanque = ET.SubElement(TANQUE, '{%s}CapacidadFondajeTanque'% covol)
                        ET.SubElement(CapacidadFondajeTanque, '{%s}ValorNumerico'% covol).text = str(tanques['tanque'].CapacidadFondajeTanque)
                        ET.SubElement(CapacidadFondajeTanque, '{%s}UM'% covol).text =str(tanques['tanque'].CapacidadFondajeTanque_UM)

                        CapacidadGasTalon = ET.SubElement(TANQUE, '{%s}CapacidadGasTalon'% covol)
                        ET.SubElement(CapacidadGasTalon, '{%s}ValorNumerico'% covol).text = str(tanques['tanque'].CapacidadGasTalon)
                        ET.SubElement(CapacidadGasTalon, '{%s}UM'% covol).text = str(tanques['tanque'].CapacidadGasTalon_UM)

                        VolumenMinimoOperacion = ET.SubElement(TANQUE, '{%s}VolumenMinimoOperacion'% covol)
                        ValorNumerico = ET.SubElement(VolumenMinimoOperacion, '{%s}ValorNumerico'% covol).text =str(tanques['tanque'].VolumenMinimoOperacion)
                        ET.SubElement(VolumenMinimoOperacion, '{%s}UM'% covol).text = str(tanques['tanque'].VolumenMinimoOperacion_UM)

                        for medicion in tanques['medicion_tanque']:
                            ET.SubElement(TANQUE, '{%s}EstadoTanque'% covol).text = tanques['tanque'].EstadoTanque
                            MedicionTanque = ET.SubElement(TANQUE, '{%s}MedicionTanque'% covol)
                            ET.SubElement(MedicionTanque, '{%s}SistemaMedicionTanque'% covol).text =str(medicion.SistemaMedicionTanque)
                            ET.SubElement(MedicionTanque, '{%s}LocalizODescripSistMedicionTanque'% covol).text =str(medicion.LocalizODescripSistMedicionTanque)
                            ET.SubElement(MedicionTanque, '{%s}VigenciaCalibracionSistMedicionTanque'% covol).text =str(medicion.VigenciaCalibracionSistMedicionTanque.strftime('%Y-%m-%d'))
                            ET.SubElement(MedicionTanque, '{%s}IncertidumbreMedicionSistMedicionTanque'% covol).text =str(medicion.IncertidumbreMedicionSistMedicionTanque)

                        EXISTENCIAS = ET.SubElement(TANQUE, '{%s}EXISTENCIAS'% covol)
                        VolumenExistenciasAnterior = ET.SubElement(EXISTENCIAS, '{%s}VolumenExistenciasAnterior'% covol)
                        ET.SubElement(VolumenExistenciasAnterior, '{%s}ValorNumerico'% covol).text =str(tanques['existencias'].VolumenExistenciasAnterior)
                        VolumenAcumOpsRecepcion = ET.SubElement(EXISTENCIAS, '{%s}VolumenAcumOpsRecepcion'% covol)
                        ET.SubElement(VolumenAcumOpsRecepcion, '{%s}ValorNumerico'% covol).text = str(tanques['existencias'].VolumenAcumOpsRecepcion)
                        ET.SubElement(VolumenAcumOpsRecepcion, '{%s}UM'% covol).text = str(tanques['existencias'].VolumenAcumOpsRecepcion_UM)
                        
                        ET.SubElement(EXISTENCIAS, '{%s}HoraRecepcionAcumulado'% covol).text = tanques['existencias'].HoraEntregaAcumulado


                        VolumenAcumOpsEntrega = ET.SubElement(EXISTENCIAS,'{%s}VolumenAcumOpsEntrega'% covol)
                        ET.SubElement(VolumenAcumOpsEntrega, '{%s}ValorNumerico'% covol).text = str(tanques['existencias'].VolumenAcumOpsRecepcion)
                        ET.SubElement(VolumenAcumOpsEntrega, '{%s}UM'% covol).text = str(tanques['existencias'].VolumenAcumOpsRecepcion_UM)
                        
                        
                        ET.SubElement(EXISTENCIAS, '{%s}HoraEntregaAcumulado'% covol).text = tanques['existencias'].HoraRecepcionAcumulado
                        
                        VolumenExistencias = ET.SubElement(EXISTENCIAS, '{%s}VolumenExistencias'% covol)
                        ET.SubElement(VolumenExistencias, '{%s}ValorNumerico'% covol).text =str(tanques['existencias'].VolumenExistencias)
                        ET.SubElement(EXISTENCIAS, '{%s}FechaYHoraEstaMedicion'% covol).text = tanques['existencias'].FechaYHoraEstaEdicion
                        ET.SubElement(EXISTENCIAS, '{%s}FechaYHoraMedicionAnterior'% covol).text = tanques['existencias'].FechaYHoraEdicionAnterior


                        RECEPCIONES = ET.SubElement(TANQUE, '{%s}RECEPCIONES'% covol)
                        ET.SubElement(RECEPCIONES, '{%s}TotalRecepciones'% covol).text = str(tanques['recepciones'].TotalRecepciones)
                        
                        SumaVolumenRecepcion = ET.SubElement(RECEPCIONES, '{%s}SumaVolumenRecepcion'% covol)
                        ET.SubElement(SumaVolumenRecepcion, '{%s}ValorNumerico'% covol).text = str(tanques['recepciones'].SumaVolumenRecepcion)
                        ET.SubElement(SumaVolumenRecepcion, '{%s}UM'% covol).text = str(tanques['recepciones'].SumaVolumenRecepcion_UM)

                        ET.SubElement(RECEPCIONES, '{%s}TotalDocumentos'% covol).text = str(tanques['recepciones'].TotalDocumentos)
                        ET.SubElement(RECEPCIONES, '{%s}SumaCompras'% covol).text = str(tanques['recepciones'].SumaCompras)
                        logging.debug("tanques_com", str(tanques))
                        for recepcion in tanques['recepcion']:
                            RECEPCION = ET.SubElement(RECEPCIONES, '{%s}RECEPCION'% covol)
                            ET.SubElement(RECEPCION, '{%s}NumeroDeRegistro'% covol).text = str(recepcion.Id)
                            ET.SubElement(RECEPCION,'{%s}TipoDeRegistro'% covol).text = str(recepcion.TipoDeRegistro)
                            VolumenInicialTanque = ET.SubElement(RECEPCION, '{%s}VolumenInicialTanque'% covol)
                            ET.SubElement(VolumenInicialTanque, '{%s}ValorNumerico'% covol).text = str(recepcion.VolumenInicialTanque)
                            ET.SubElement(VolumenInicialTanque, '{%s}UM'% covol).text = str(recepcion.VolumenInicialTanque_UM)

                            VolumenFinalTanque = ET.SubElement(RECEPCION, '{%s}VolumenFinalTanque'% covol)
                            ET.SubElement(VolumenFinalTanque, '{%s}ValorNumerico'% covol).text=str(recepcion.VolumenFinalTanque)
                            VolumenRecepcion = ET.SubElement(RECEPCION, '{%s}VolumenRecepcion'% covol)
                            ET.SubElement(VolumenRecepcion, '{%s}ValorNumerico'% covol).text = str(recepcion.VolumenRecepcion)
                            ET.SubElement(VolumenRecepcion, '{%s}UM'% covol).text =str(recepcion.VolumenRecepcion_UM)


                            ET.SubElement(RECEPCION, '{%s}Temperatura'% covol).text =str(round(recepcion.Temperatura, 3))
                            ET.SubElement(RECEPCION, '{%s}PresionAbsoluta'% covol).text =str(recepcion.PresionAbsoluta)
                            ET.SubElement(RECEPCION, '{%s}FechaYHoraInicioRecepcion'% covol).text =str(recepcion.FechaYHoraInicialRecepcion.astimezone().isoformat())
                            ET.SubElement(RECEPCION, '{%s}FechaYHoraFinalRecepcion'% covol).text =str(recepcion.FechaYHoraFinalRecepcion.astimezone().isoformat())
                            Complemento = ET.SubElement(RECEPCION, '{%s}Complemento'% covol)
                            #Complemento.text =''
                            tipo = str('comercializador')
                            id_complemento_recepcion = 2
                            DailyReportFuntionsInstance = DailyReportFuntions(2)
                            logging.debug("recepcion_dato_original", recepcion)
                            complementos_date = DailyReportFuntionsInstance.GetComplementDailyReportAll(id_complemento_recepcion, tipo,'C',recepcion,'R_cv' )

                            logging.debug("aqui tadeo", complementos_date)

                            Complemento_Comercializacion_Recepcion = ET.SubElement(Complemento, '{%s}Complemento_Comercializacion' %covol)
                            if complementos_date:
                                for complementos in complementos_date:
                                        """
                                        terminalAlmYTrans = complementos['TERMINALALMYTRANS_TERMINALALMYDIST']

                                        Terminalalmtrans = ET.SubElement(Complemento_Comercializacion_Recepcion, '{%s}TERMINALALMYTRANS' % dis )
                                        Almacenamiento = ET.SubElement(Terminalalmtrans, '{%s}Almacenamiento' % dis)
                                        ET.SubElement(Almacenamiento, '{%s}TerminalAlm' % dis).text =  str(terminalAlmYTrans['Almacenamiento'].TerminalAlm)
                                        ET.SubElement(Almacenamiento, '{%s}PermisoAlmacenamiento' % dis).text = str(terminalAlmYTrans['Almacenamiento'].PermisoAlmacenamiento)
                                        ET.SubElement(Almacenamiento, '{%s}TarifaDeAlmacenamiento' % dis).text = str(terminalAlmYTrans['Almacenamiento'].TarifaDeAlmacenamiento )
                                        ET.SubElement(Almacenamiento, '{%s}CargoPorCapacidadAlmac' % dis).text = str(terminalAlmYTrans['Almacenamiento'].CargoPorCapacidadAlmac) 
                                        ET.SubElement(Almacenamiento, '{%s}CargoPorUsoAlmac' % dis).text = str(terminalAlmYTrans['Almacenamiento'].CargoPorUsoAlmac )
                                        ET.SubElement(Almacenamiento, '{%s}CargoVolumetricoAlmac' % dis).text = str(terminalAlmYTrans['Almacenamiento'].CargoVolumetricoAlmac) 

                                        Transporte = ET.SubElement(Terminalalmtrans, '{%s}Transporte' % dis)
                                        ET.SubElement(Transporte, '{%s}PermisoTransporte' % dis).text = str(terminalAlmYTrans['Transporte'].PermisoTransporte)
                                        ET.SubElement(Transporte, '{%s}ClaveDeVehiculo' % dis).text =str(terminalAlmYTrans['Transporte'].ClaveDeVehiculo)
                                        ET.SubElement(Transporte, '{%s}TarifaDeTransporte'% dis).text = str(terminalAlmYTrans['Transporte'].TarifaDeTransporte)
                                        ET.SubElement(Transporte, '{%s}CargoPorCapacidadTrans'% dis).text = str(terminalAlmYTrans['Transporte'].CargoPorCapacidadTrans)
                                        ET.SubElement(Transporte, '{%s}CargoPorUsoTrans'% dis).text = str(terminalAlmYTrans['Transporte'].CargoPorUsoTrans)
                                        ET.SubElement(Transporte, '{%s}CargoVolumetricoTrans'% dis).text =str(terminalAlmYTrans['Transporte'].CargoVolumetricoTrans)
                                        ET.SubElement(Transporte, '{%s}TarifaDeSuministro'% dis).text = str(terminalAlmYTrans['Transporte'].CargoVolumetricoTrans)

                                        for trasvase in complementos['TRASVASE']:

                                            Trasvase = ET.SubElement(Complemento_Comercializacion_Recepcion, '{%s}TRASVASE'% dis)
                                            ET.SubElement(Trasvase, '{%s}NombreTrasvase' % dis).text =  str(trasvase['TRASVASE'].NombreTrasvase)
                                            ET.SubElement(Trasvase, '{%s}RfcTrasvase' % dis).text = str(trasvase['TRASVASE'].RfcTrasvase)
                                            ET.SubElement(Trasvase, '{%s}PermisoTrasvase' % dis).text =str(trasvase['TRASVASE'].PermisoTrasvase)
                                            ET.SubElement(Trasvase, '{%s}DescripcionTrasvase' % dis).text =  str(trasvase['TRASVASE'].DescripcionTrasvase)
                                            ET.SubElement(Trasvase, '{%s}CfdiTrasvase' % dis).text = str(trasvase['TRASVASE'].CfdiTrasvase)

                                        dictamen =complementos['DICTAMEN']
                                        Dictamen = ET.SubElement(Complemento_Comercializacion_Recepcion, '{%s}DICTAMEN'% dis)
                                        ET.SubElement(Dictamen, '{%s}RfcDictamen' % dis).text = str(dictamen['DICTAMEN'].RfcDictamen)
                                        ET.SubElement(Dictamen, '{%s}LoteDictamen' % dis).text = str(dictamen['DICTAMEN'].LoteDictamen)
                                        ET.SubElement(Dictamen, '{%s}NumeroFolioDictamen' % dis).text = str(dictamen['DICTAMEN'].NumeroFolioDictamen)
                                        ET.SubElement(Dictamen, '{%s}FechaEmisionDictamen' % dis).text =str(dictamen['DICTAMEN'].ResultadoDictamen)
                                        ET.SubElement(Dictamen, '{%s}ResultadoDictamen' % dis).text = str(dictamen['DICTAMEN'].ResultadoDictamen)
                                        """
                                        certificado = complementos['CERTIFICADO']

                                        Certificado = ET.SubElement(Complemento_Comercializacion_Recepcion, '{%s}CERTIFICADO' % dis)
                                        ET.SubElement(Certificado, '{%s}RfcCertificado' % dis).text = str(certificado['CERTIFICADO'].RfcCertificado)
                                        ET.SubElement(Certificado, '{%s}NumeroFolioCertificado' % dis).text = str(certificado['CERTIFICADO'].NumeroFolioCertificado)
                                        ET.SubElement(Certificado, '{%s}FechaEmisionCertificado' % dis).text = str(certificado['CERTIFICADO'].FechaEmisionCertificado)
                                        ET.SubElement(Certificado, '{%s}ResultadoCertificado' % dis).text = str(certificado['CERTIFICADO'].ResultadoCertificado)   

                                        for nacional in complementos['NACIONAL']:
                                            Nacional = ET.SubElement(Complemento_Comercializacion_Recepcion, '{%s}NACIONAL' % dis)

                                            ET.SubElement(Nacional, '{%s}RfcClienteOProveedor' % dis).text =str(nacional['NACIONAL'].RFC)
                                            ET.SubElement(Nacional, '{%s}NombreClienteOProveedor' % dis).text = str(nacional['NACIONAL'].Nombre_comercial)
                                            if nacional['NACIONAL'].PermisoClienteOProveedor is not None and nacional['NACIONAL'].PermisoClienteOProveedor != '':
                                                ET.SubElement(Nacional, '{%s}PermisoClienteOProveedor' % dis).text = str(nacional['NACIONAL'].PermisoClienteOProveedor)

                                            for cfdi in nacional['cfdis']:
                                                CFDIs = ET.SubElement(Nacional, '{%s}CFDIs' % dis)
                                                ET.SubElement(CFDIs, '{%s}CFDI' % dis).text = str(cfdi.CFDI)
                                                ET.SubElement(CFDIs, '{%s}TipoCFDI' % dis).text = str(cfdi.TipoCFDI)
                                                ET.SubElement(CFDIs, '{%s}PrecioVentaOCompraOContrap' % dis).text = str(cfdi.PrecioVentaOCompraOContrap)
                                                ET.SubElement(CFDIs, '{%s}FechaYHoraTransaccion' % dis).text = str(cfdi.FechaYHoraTransaccion.astimezone().isoformat())
                                                VolumenDocumentado = ET.SubElement(CFDIs, '{%s}VolumenDocumentado' % dis)
                                                ET.SubElement(VolumenDocumentado, '{%s}ValorNumerico' % dis).text = str(cfdi.VolumenDocumentado)
                                                ET.SubElement(VolumenDocumentado, '{%s}UM' % dis).text = str(cfdi.VolumenDocumentado_UM)
                                        """
                                        for extranjero in complementos['EXTRANJERO']:
                                            Extranjero = ET.SubElement(Complemento_Comercializacion_Recepcion, '{%s}EXTRANJERO' % dis)

                                            ET.SubElement(Extranjero, '{%s}PermisoImportacionOExportacion' % dis).text = str(extranjero['EXTRANJERO'].PermisoImportacionOExportacion)
                                            for pedimentos in extranjero['pedimentos']:
                                                Pedimentos = ET.SubElement(Extranjero, '{%s}PEDIMENTOS' % dis)
                                                ET.SubElement(Pedimentos, '{%s}PuntoDeInternacionOExtraccion' % dis).text = str(pedimentos.PuntoDeInternacionOExtraccion)
                                                ET.SubElement(Pedimentos, '{%s}PaisOrigenODestino' % dis).text = str(pedimentos.PaisOrigenODestino)
                                                ET.SubElement(Pedimentos, '{%s}MedioDeTransEntraOSaleAduana' % dis).text = str(pedimentos.MedioDeTransEntraOSaleAducto)
                                                ET.SubElement(Pedimentos, '{%s}PedimentoAduanal' % dis).text =str(pedimentos.PedimentosAduanal)
                                                ET.SubElement(Pedimentos, '{%s}Incoterms'% dis).text = str(pedimentos.Incoterms)
                                                ET.SubElement(Pedimentos, '{%s}PrecioDeImportacionOExportacion' % dis).text = str(pedimentos.PrecioDeImportacionOExportacion) 

                                                Volumen_documentado = ET.SubElement(Pedimentos, '{%s}VolumenDocumentado'% dis)
                                                ET.SubElement(Volumen_documentado, '{%s}ValorNumerico' % dis).text =str(pedimentos.VolumenDocumentado)
                                                ET.SubElement(Volumen_documentado, '{%s}UM' % dis).text = str(pedimentos.VolumenDocumentado_UM)
                                        """
                                        Aclarcion = ET.SubElement(Complemento_Comercializacion_Recepcion, '{%s}ACLARACION' % dis)
                                        ET.SubElement(Aclarcion, '{%s}Aclaracion' % dis).text = str(complementos['ACLARACION']['ACLARACION'])


                        ENTREGAS = ET.SubElement(TANQUE, '{%s}ENTREGAS'% covol)
                        ET.SubElement(ENTREGAS, '{%s}TotalEntregas'% covol).text =str(tanques['entregas'].TotalEntregas)
                        SumaVolumenEntregado = ET.SubElement(ENTREGAS, '{%s}SumaVolumenEntregado'% covol) 
                        ET.SubElement(SumaVolumenEntregado, '{%s}ValorNumerico'% covol).text =str(tanques['entregas'].SumaVolumenEntregado)
                        ET.SubElement(SumaVolumenEntregado, '{%s}UM'% covol).text =  str(tanques['entregas'].SumaVolumenEntregado_UM)
                        ET.SubElement(ENTREGAS,'{%s}TotalDocumentos'% covol).text = str(tanques['entregas'].TotalDocumentos)
                        ET.SubElement(ENTREGAS,'{%s}SumaVentas'% covol).text =str(tanques['entregas'].SumaVentas)
                        
                        for entrega in tanques['entrega']:
                            ENTREGA = ET.SubElement(ENTREGAS,'{%s}ENTREGA'% covol)
                            ET.SubElement(ENTREGA,'{%s}NumeroDeRegistro'% covol).text = str(entrega.Id )
                            ET.SubElement(ENTREGA,'{%s}TipoDeRegistro'% covol).text = str(entrega.TipoDeRegistro)

                            VolumenInicialTanque = ET.SubElement(ENTREGA,'{%s}VolumenInicialTanque'% covol)
                            ET.SubElement(VolumenInicialTanque,'{%s}ValorNumerico'% covol).text= str(entrega.VolumenInicialTanque)
                            ET.SubElement(VolumenInicialTanque,'{%s}UM'% covol).text =str(entrega.VolumenInicialTanque_UM)

                            VolumenFinalTanque = ET.SubElement(ENTREGA,'{%s}VolumenFinalTanque'% covol)
                            ET.SubElement(VolumenFinalTanque,'{%s}ValorNumerico'% covol).text =str(entrega.VolumenFinalTanque)
                            VolumenEntregado = ET.SubElement(ENTREGA,'{%s}VolumenEntregado'% covol)
                            ET.SubElement(VolumenEntregado,'{%s}ValorNumerico'% covol).text=str(entrega.VolumenEntregado)
                            ET.SubElement(VolumenEntregado,'{%s}UM'% covol).text =  str(entrega.VolumenEntregado_UM)
                            ET.SubElement(ENTREGA,'{%s}Temperatura'% covol).text = str(round(entrega.Temperatura, 3))
                            ET.SubElement(ENTREGA,'{%s}PresionAbsoluta'% covol).text =str(entrega.PresionAbsoluta) 
                            ET.SubElement(ENTREGA,'{%s}FechaYHoraInicialEntrega'% covol).text  = str(entrega.FechaYHoraInicialEntrega.astimezone().isoformat())
                            ET.SubElement(ENTREGA,'{%s}FechaYHoraFinalEntrega'% covol).text = str(entrega.FechaYHoraFinalEntrega.astimezone().isoformat())
                            #Complemento_Distribucion = ET.SubElement(ENTREGA, '{%s}Complemento_Distribucion'%dis)
                            #complemento_elem_entrega.append(nuevo_elemento_complemento)
                            Complemento = ET.SubElement(ENTREGA, '{%s}Complemento'% covol)

                            tipo = str('comercializador')
                            id_complemento_entrega = 2
                            DailyReportFuntionsInstance = DailyReportFuntions(2)
                            complementos_date = DailyReportFuntionsInstance.GetComplementDailyReportAll(id_complemento_entrega,tipo,'C',entrega,'E_cv')

                            Complemento_Comercializacion_Entrega = ET.SubElement(Complemento, '{%s}Complemento_Comercializacion' %covol)
                            if complementos_date:
                                for complementos in complementos_date:
                                        """
                                        terminalAlmYTrans = complementos['TERMINALALMYTRANS_TERMINALALMYDIST']

                                        Terminalalmtrans = ET.SubElement(Complemento_Comercializacion_Entrega, '{%s}TERMINALALMYTRANS' % dis )
                                        Almacenamiento = ET.SubElement(Terminalalmtrans, '{%s}Almacenamiento' % dis)
                                        ET.SubElement(Almacenamiento, '{%s}TerminalAlm' % dis).text = str(terminalAlmYTrans['Almacenamiento'].TerminalAlm)
                                        ET.SubElement(Almacenamiento, '{%s}PermisoAlmacenamiento' % dis).text = str(terminalAlmYTrans['Almacenamiento'].PermisoAlmacenamiento)
                                        ET.SubElement(Almacenamiento, '{%s}TarifaDeAlmacenamiento' % dis).text = str(terminalAlmYTrans['Almacenamiento'].TarifaDeAlmacenamiento)
                                        ET.SubElement(Almacenamiento, '{%s}CargoPorCapacidadAlmac' % dis).text = str(terminalAlmYTrans['Almacenamiento'].CargoPorCapacidadAlmac) 
                                        ET.SubElement(Almacenamiento, '{%s}CargoPorUsoAlmac' % dis).text = str(terminalAlmYTrans['Almacenamiento'].CargoPorUsoAlmac)
                                        ET.SubElement(Almacenamiento, '{%s}CargoVolumetricoAlmac' % dis).text = str(terminalAlmYTrans['Almacenamiento'].CargoVolumetricoAlmac) 

                                        Transporte = ET.SubElement(Terminalalmtrans, '{%s}Transporte' % dis)
                                        ET.SubElement(Transporte, '{%s}PermisoTransporte' % dis).text =str(terminalAlmYTrans['Transporte'].PermisoTransporte)
                                        ET.SubElement(Transporte, '{%s}ClaveDeVehiculo' % dis).text =str(terminalAlmYTrans['Transporte'].ClaveDeVehiculo)
                                        ET.SubElement(Transporte, '{%s}TarifaDeTransporte'% dis).text = str(terminalAlmYTrans['Transporte'].TarifaDeTransporte)
                                        ET.SubElement(Transporte, '{%s}CargoPorCapacidadTrans'% dis).text = str(terminalAlmYTrans['Transporte'].CargoPorCapacidadTrans)
                                        ET.SubElement(Transporte, '{%s}CargoPorUsoTrans'% dis).text = str(terminalAlmYTrans['Transporte'].CargoPorUsoTrans)
                                        ET.SubElement(Transporte, '{%s}CargoVolumetricoTrans'% dis).text = str(terminalAlmYTrans['Transporte'].CargoVolumetricoTrans)
                                        ET.SubElement(Transporte, '{%s}TarifaDeSuministro'% dis).text = str(terminalAlmYTrans['Transporte'].CargoVolumetricoTrans)

                                        for trasvase in complementos['TRASVASE']:

                                            Trasvase = ET.SubElement(Complemento_Comercializacion_Entrega, '{%s}TRASVASE'% dis)
                                            ET.SubElement(Trasvase, '{%s}NombreTrasvase' % dis).text =  str(trasvase['TRASVASE'].NombreTrasvase)
                                            ET.SubElement(Trasvase, '{%s}RfcTrasvase' % dis).text = str(trasvase['TRASVASE'].RfcTrasvase)
                                            ET.SubElement(Trasvase, '{%s}PermisoTrasvase' % dis).text =str(trasvase['TRASVASE'].PermisoTrasvase)
                                            ET.SubElement(Trasvase, '{%s}DescripcionTrasvase' % dis).text =  str(trasvase['TRASVASE'].DescripcionTrasvase)
                                            ET.SubElement(Trasvase, '{%s}CfdiTrasvase' % dis).text = str(trasvase['TRASVASE'].CfdiTrasvase)

                                        dictamen =complementos['DICTAMEN']
                                        Dictamen = ET.SubElement(Complemento_Comercializacion_Entrega, '{%s}DICTAMEN'% dis)
                                        ET.SubElement(Dictamen, '{%s}RfcDictamen' % dis).text = str(dictamen['DICTAMEN'].RfcDictamen)
                                        ET.SubElement(Dictamen, '{%s}LoteDictamen' % dis).text = str(dictamen['DICTAMEN'].LoteDictamen)
                                        ET.SubElement(Dictamen, '{%s}NumeroFolioDictamen' % dis).text = str(dictamen['DICTAMEN'].NumeroFolioDictamen)
                                        ET.SubElement(Dictamen, '{%s}FechaEmisionDictamen' % dis).text =str(dictamen['DICTAMEN'].FechaEmisionDictamen)
                                        ET.SubElement(Dictamen, '{%s}ResultadoDictamen' % dis).text = str(dictamen['DICTAMEN'].ResultadoDictamen)
                                        """
                                        certificado = complementos['CERTIFICADO']

                                        Certificado = ET.SubElement(Complemento_Comercializacion_Entrega, '{%s}CERTIFICADO' % dis)
                                        ET.SubElement(Certificado, '{%s}RfcCertificado' % dis).text = str(certificado['CERTIFICADO'].RfcCertificado)
                                        ET.SubElement(Certificado, '{%s}NumeroFolioCertificado' % dis).text = str(certificado['CERTIFICADO'].NumeroFolioCertificado)
                                        ET.SubElement(Certificado, '{%s}FechaEmisionCertificado' % dis).text = str(certificado['CERTIFICADO'].FechaEmisionCertificado)
                                        ET.SubElement(Certificado, '{%s}ResultadoCertificado' % dis).text = str(certificado['CERTIFICADO'].ResultadoCertificado)   

                                        #logging.debug("complementos_comp", complementos)

                                        for nacional in complementos['NACIONAL']:
                                            Nacional = ET.SubElement(Complemento_Comercializacion_Entrega, '{%s}NACIONAL' % dis)

                                            #logging.debug("cont_nacional", nacional)

                                            ET.SubElement(Nacional, '{%s}RfcClienteOProveedor' % dis).text = str(nacional['NACIONAL'].RFC)
                                            #logging.debug("pasamos RFC", "RFC_PASS")
                                            ET.SubElement(Nacional, '{%s}NombreClienteOProveedor' % dis).text = str(nacional['NACIONAL'].Nombre_comercial)
                                            if nacional['NACIONAL'].PermisoClienteOProveedor is not None and nacional['NACIONAL'].PermisoClienteOProveedor != '':
                                                ET.SubElement(Nacional, '{%s}PermisoClienteOProveedor' % dis).text = str(nacional['NACIONAL'].PermisoClienteOProveedor)
                                            for cfdi in nacional['cfdis']:
                                                CFDIs = ET.SubElement(Nacional, '{%s}CFDIs' % dis)

                                                ET.SubElement(CFDIs, '{%s}CFDI' % dis).text = str(cfdi.CFDI)
                                                ET.SubElement(CFDIs, '{%s}TipoCFDI' % dis).text = str(cfdi.TipoCFDI)
                                                ET.SubElement(CFDIs, '{%s}PrecioVentaOCompraOContrap' % dis).text = str(cfdi.PrecioVentaOCompraOContrap)
                                                ET.SubElement(CFDIs, '{%s}FechaYHoraTransaccion' % dis).text = str(cfdi.FechaYHoraTransaccion.astimezone().isoformat())
                                                VolumenDocumentado = ET.SubElement(CFDIs, '{%s}VolumenDocumentado' % dis)
                                                ET.SubElement(VolumenDocumentado, '{%s}ValorNumerico' % dis).text = str(cfdi.VolumenDocumentado)
                                                ET.SubElement(VolumenDocumentado, '{%s}UM' % dis).text = str(cfdi.VolumenDocumentado_UM)

                                        """
                                        for extranjero in complementos['EXTRANJERO']:
                                            Extranjero = ET.SubElement(Complemento_Comercializacion_Entrega, '{%s}EXTRANJERO' % dis)
                                            ET.SubElement(Extranjero, '{%s}PermisoImportacionOExportacion' % dis).text = str(extranjero['EXTRANJERO'].PermisoImportacionOExportacion)
                                            for pedimentos in extranjero['pedimentos']:
                                                Pedimentos = ET.SubElement(Extranjero, '{%s}PEDIMENTOS' % dis)
                                                ET.SubElement(Pedimentos, '{%s}PuntoDeInternacionOExtraccion' % dis).text = str(pedimentos.PuntoDeInternacionOExtraccion)
                                                ET.SubElement(Pedimentos, '{%s}PaisOrigenODestino' % dis).text = str(pedimentos.PaisOrigenODestino)
                                                ET.SubElement(Pedimentos, '{%s}MedioDeTransEntraOSaleAduana' % dis).text =str(pedimentos.MedioDeTransEntraOSaleAducto)
                                                ET.SubElement(Pedimentos, '{%s}PedimentoAduanal' % dis).text =str(pedimentos.PedimentosAduanal)
                                                ET.SubElement(Pedimentos, '{%s}Incoterms'% dis).text = str(pedimentos.Incoterms)
                                                ET.SubElement(Pedimentos, '{%s}PrecioDeImportacionOExportacion' % dis).text = str(pedimentos.PrecioDeImportacionOExportacion) 

                                                Volumen_documentado = ET.SubElement(Pedimentos, '{%s}VolumenDocumentado'% dis)
                                                ET.SubElement(Volumen_documentado, '{%s}ValorNumerico' % dis).text =str(pedimentos.VolumenDocumentado)
                                                ET.SubElement(Volumen_documentado, '{%s}UM' % dis).text = str(pedimentos.VolumenDocumentado_UM)
                                        """
                                        Aclarcion = ET.SubElement(Complemento_Comercializacion_Entrega, '{%s}ACLARACION' % dis)
                                        ET.SubElement(Aclarcion, '{%s}Aclaracion' % dis).text = str(complementos['ACLARACION']['ACLARACION'])
                
                DailyReportFuntionsInstance = DailyReportFuntions(2)
                controles = GeneralReport(2)
                diarios_controles = controles.GiveCV()
                diarios_JSON = DailyReportFuntionsInstance.GetDailyReportAll(fecha_consulta)
                if diarios_JSON:
                    for producto_ in diarios_JSON:
                        PRODUCTO = ET.SubElement(CONTROLES_VOLUMETRICOS, '{%s}PRODUCTO'% covol)
                        clave =  producto_['producto'].ClaveProducto

                        ET.SubElement(PRODUCTO, '{%s}ClaveProducto'% covol).text = clave
                        ET.SubElement(PRODUCTO, '{%s}ClaveSubProducto'% covol).text = producto_['producto'].ClaveSubProducto
                        if clave == "PR07":
                            Gasolina = ET.SubElement(PRODUCTO, '{%s}Gasolina'% covol)
                            ET.SubElement(Gasolina, '{%s}ComposOctanajeGasolina'% covol).text = str(producto_['producto'].ComposOctanajeGasolina)
                            ET.SubElement(Gasolina, '{%s}GasolinaConCombustibleNoFosil'% covol).text = producto_['producto'].GasolinaConCombustibleNoFosil
                            if producto_['producto'].GasolinaConCombustibleNoFosil == 'Si':
                                ET.SubElement(Gasolina, '{%s}ComposDeCombustibleNoFosilEnGasolina'% covol).text = str(producto_['producto'].ComposDeCombustibleNoFosilEnGasolina)
                        elif clave == "PR03":                       
                            Diesel = ET.SubElement(PRODUCTO, '{%s}Diesel'% covol)
                            ET.SubElement(Diesel, '{%s}DieselConCombustibleNoFosil'% covol).text = producto_['producto'].DieselConCombustibleNoFosil
                            if producto_['producto'].DieselConCombustibleNoFosil == 'Si':
                                ET.SubElement(Diesel, '{%s}ComposDeCombustibleNoFosilEnDiesel'% covol).text = str(producto_['producto'].ComposDeCombustibleNoFosilEnDiesel)
                        else:
                            ET.SubElement(PRODUCTO, '{%s}Otros'% covol).text =  producto_['producto'].Otros

                        #Turbosina = ET.SubElement(PRODUCTO, '{%s}Turbosina'% covol)
                        #ET.SubElement(Turbosina, '{%s}TurbosinaConCombustibleNoFosil'% covol).text = producto_['producto'].TurbosinaConCombustibleNoFosil
                        #ET.SubElement(Diesel, '{%s}ComposDeCombustibleNoFosilEnTurbosina'% covol).text = producto_['producto'].ComposDeCombustibleNoFosilEnTurbosina

                        #GasLP = ET.SubElement(PRODUCTO, '{%s}GasLP'% covol)
                        #ET.SubElement(GasLP, '{%s}ComposDePropanoEnGasLP'% covol).text = producto_['producto'].ComposDePropanoEnGasLP
                        #ET.SubElement(Diesel, '{%s}ComposDeButanoEnGasLP'% covol).text = producto_['producto'].ComposDeButanoEnGasLp

                        #Petroleo = ET.SubElement(PRODUCTO, '{%s}Petroleo'% covol)
                        #ET.SubElement(Petroleo, '{%s}DensidadDePetroleo'% covol).text = producto_['producto'].DensidadDePetroleo
                        #ET.SubElement(Petroleo, '{%s}ComposDeAzufreEnPetroleo'% covol).text = producto_['producto'].ComposDeAzufreEnPetroleo
                        ET.SubElement(PRODUCTO, '{%s}MarcaComercial'% covol).text = producto_['producto'].MarcaComercial
                        if producto_['producto'].Marcaje:
                            ET.SubElement(PRODUCTO, '{%s}Marcaje'% covol).text = producto_['producto'].Marcaje
                            if producto_['producto'].ConcentracionSustanciasMarcaje and producto_['producto'].ConcentracionSustanciasMarcaje > 0:
                                ET.SubElement(PRODUCTO, '{%s}ConcentracionSustanciaMarcaje'% covol).text = str(producto_['producto'].ConcentracionSustanciasMarcaje)

                        for tanques in producto_['tanques']:
                            TANQUE = ET.SubElement(PRODUCTO, '{%s}TANQUE'% covol)
                            ET.SubElement(TANQUE, '{%s}ClaveIdentificacionTanque'% covol).text = tanques['tanque'].ClaveIdentificacionTanque
                            ET.SubElement(TANQUE, '{%s}LocalizacionYODescripcionTanque'% covol).text = tanques['tanque'].LocalizacionYODescripcionTanque
                            ET.SubElement(TANQUE, '{%s}VigenciaCalibracionTanque'% covol).text = str(tanques['tanque'].VigenciaCalibracionTanque.strftime('%Y-%m-%d'))

                            CapacidadTotalTanque = ET.SubElement(TANQUE, '{%s}CapacidadTotalTanque'% covol)
                            ET.SubElement(CapacidadTotalTanque, '{%s}ValorNumerico'% covol).text = str(tanques['tanque'].CapacidadTotalTanque)
                            ET.SubElement(CapacidadTotalTanque, '{%s}UM'% covol).text =  str(tanques['tanque'].CapacidadTotalTanque_UM)


                            CapacidadOperativaTanque = ET.SubElement(TANQUE, '{%s}CapacidadOperativaTanque'% covol)
                            ET.SubElement(CapacidadOperativaTanque, '{%s}ValorNumerico'% covol).text = str(tanques['tanque'].CapacidadOperativaTanque)
                            ET.SubElement(CapacidadOperativaTanque, '{%s}UM'% covol).text = str(tanques['tanque'].CapacidadOperativaTanque_UM)

                            CapacidadUtilTanque = ET.SubElement(TANQUE, '{%s}CapacidadUtilTanque'% covol)
                            ET.SubElement(CapacidadUtilTanque, '{%s}ValorNumerico'% covol).text =str(tanques['tanque'].CapacidadUtilTanque)
                            ET.SubElement(CapacidadUtilTanque, '{%s}UM'% covol).text = str(tanques['tanque'].CapacidadUtilTanque_UM)

                            CapacidadFondajeTanque = ET.SubElement(TANQUE, '{%s}CapacidadFondajeTanque'% covol)
                            ET.SubElement(CapacidadFondajeTanque, '{%s}ValorNumerico'% covol).text = str(tanques['tanque'].CapacidadFondajeTanque)
                            ET.SubElement(CapacidadFondajeTanque, '{%s}UM'% covol).text =str(tanques['tanque'].CapacidadFondajeTanque_UM)

                            CapacidadGasTalon = ET.SubElement(TANQUE, '{%s}CapacidadGasTalon'% covol)
                            ET.SubElement(CapacidadGasTalon, '{%s}ValorNumerico'% covol).text = str(tanques['tanque'].CapacidadGasTalon)
                            ET.SubElement(CapacidadGasTalon, '{%s}UM'% covol).text = str(tanques['tanque'].CapacidadGasTalon_UM)

                            VolumenMinimoOperacion = ET.SubElement(TANQUE, '{%s}VolumenMinimoOperacion'% covol)
                            ValorNumerico = ET.SubElement(VolumenMinimoOperacion, '{%s}ValorNumerico'% covol).text =str(tanques['tanque'].VolumenMinimoOperacion)
                            ET.SubElement(VolumenMinimoOperacion, '{%s}UM'% covol).text = str(tanques['tanque'].VolumenMinimoOperacion_UM)

                            for medicion in tanques['medicion_tanque']:
                                ET.SubElement(TANQUE, '{%s}EstadoTanque'% covol).text = tanques['tanque'].EstadoTanque
                                MedicionTanque = ET.SubElement(TANQUE, '{%s}MedicionTanque'% covol)
                                ET.SubElement(MedicionTanque, '{%s}SistemaMedicionTanque'% covol).text =str(medicion.SistemaMedicionTanque)
                                ET.SubElement(MedicionTanque, '{%s}LocalizODescripSistMedicionTanque'% covol).text =str(medicion.LocalizODescripSistMedicionTanque)
                                ET.SubElement(MedicionTanque, '{%s}VigenciaCalibracionSistMedicionTanque'% covol).text =str(medicion.VigenciaCalibracionSistMedicionTanque.strftime('%Y-%m-%d'))
                                ET.SubElement(MedicionTanque, '{%s}IncertidumbreMedicionSistMedicionTanque'% covol).text =str(medicion.IncertidumbreMedicionSistMedicionTanque)

                            EXISTENCIAS = ET.SubElement(TANQUE, '{%s}EXISTENCIAS'% covol)
                            VolumenExistenciasAnterior = ET.SubElement(EXISTENCIAS, '{%s}VolumenExistenciasAnterior'% covol)
                            ET.SubElement(VolumenExistenciasAnterior, '{%s}ValorNumerico'% covol).text =str(tanques['existencias'].VolumenExistenciasAnterior)
                            VolumenAcumOpsRecepcion = ET.SubElement(EXISTENCIAS, '{%s}VolumenAcumOpsRecepcion'% covol)
                            ET.SubElement(VolumenAcumOpsRecepcion, '{%s}ValorNumerico'% covol).text = str(tanques['existencias'].VolumenAcumOpsRecepcion)
                            ET.SubElement(VolumenAcumOpsRecepcion, '{%s}UM'% covol).text = str(tanques['existencias'].VolumenAcumOpsRecepcion_UM)
                            
                            ET.SubElement(EXISTENCIAS, '{%s}HoraRecepcionAcumulado'% covol).text = tanques['existencias'].HoraEntregaAcumulado


                            VolumenAcumOpsEntrega = ET.SubElement(EXISTENCIAS,'{%s}VolumenAcumOpsEntrega'% covol)
                            ET.SubElement(VolumenAcumOpsEntrega, '{%s}ValorNumerico'% covol).text = str(tanques['existencias'].VolumenAcumOpsRecepcion)
                            ET.SubElement(VolumenAcumOpsEntrega, '{%s}UM'% covol).text = str(tanques['existencias'].VolumenAcumOpsRecepcion_UM)
                            
                            
                            ET.SubElement(EXISTENCIAS, '{%s}HoraEntregaAcumulado'% covol).text = tanques['existencias'].HoraRecepcionAcumulado
                            
                            VolumenExistencias = ET.SubElement(EXISTENCIAS, '{%s}VolumenExistencias'% covol)
                            ET.SubElement(VolumenExistencias, '{%s}ValorNumerico'% covol).text =str(tanques['existencias'].VolumenExistencias)
                            ET.SubElement(EXISTENCIAS, '{%s}FechaYHoraEstaMedicion'% covol).text = tanques['existencias'].FechaYHoraEstaEdicion
                            ET.SubElement(EXISTENCIAS, '{%s}FechaYHoraMedicionAnterior'% covol).text = tanques['existencias'].FechaYHoraEdicionAnterior


                            RECEPCIONES = ET.SubElement(TANQUE, '{%s}RECEPCIONES'% covol)
                            ET.SubElement(RECEPCIONES, '{%s}TotalRecepciones'% covol).text = str(tanques['recepciones'].TotalRecepciones)
                            
                            SumaVolumenRecepcion = ET.SubElement(RECEPCIONES, '{%s}SumaVolumenRecepcion'% covol)
                            ET.SubElement(SumaVolumenRecepcion, '{%s}ValorNumerico'% covol).text = str(tanques['recepciones'].SumaVolumenRecepcion)
                            ET.SubElement(SumaVolumenRecepcion, '{%s}UM'% covol).text = str(tanques['recepciones'].SumaVolumenRecepcion_UM)

                            ET.SubElement(RECEPCIONES, '{%s}TotalDocumentos'% covol).text = str(tanques['recepciones'].TotalDocumentos)
                            ET.SubElement(RECEPCIONES, '{%s}SumaCompras'% covol).text = str(tanques['recepciones'].SumaCompras)
                            
                            for recepcion in tanques['recepcion']:
                                RECEPCION = ET.SubElement(RECEPCIONES, '{%s}RECEPCION'% covol)
                                ET.SubElement(RECEPCION, '{%s}NumeroDeRegistro'% covol).text = str(recepcion.Id)
                                #ET.SubElement(RECEPCION,'{%s}TipoDeRegistro'% covol).text = str(recepcion.TipoDeRegistro)
                                VolumenInicialTanque = ET.SubElement(RECEPCION, '{%s}VolumenInicialTanque'% covol)
                                ET.SubElement(VolumenInicialTanque, '{%s}ValorNumerico'% covol).text = str(recepcion.VolumenInicialTanque)
                                ET.SubElement(VolumenInicialTanque, '{%s}UM'% covol).text = str(recepcion.VolumenInicialTanque_UM)

                                VolumenFinalTanque = ET.SubElement(RECEPCION, '{%s}VolumenFinalTanque'% covol)
                                ET.SubElement(VolumenFinalTanque, '{%s}ValorNumerico'% covol).text=str(recepcion.VolumenFinalTanque)
                                VolumenRecepcion = ET.SubElement(RECEPCION, '{%s}VolumenRecepcion'% covol)
                                ET.SubElement(VolumenRecepcion, '{%s}ValorNumerico'% covol).text = str(recepcion.VolumenRecepcion)
                                ET.SubElement(VolumenRecepcion, '{%s}UM'% covol).text =str(recepcion.VolumenRecepcion_UM)


                                ET.SubElement(RECEPCION, '{%s}Temperatura'% covol).text =str(round(recepcion.Temperatura, 3))
                                ET.SubElement(RECEPCION, '{%s}PresionAbsoluta'% covol).text =str(recepcion.PresionAbsoluta)
                                ET.SubElement(RECEPCION, '{%s}FechaYHoraInicioRecepcion'% covol).text =str(recepcion.FechaYHoraInicialRecepcion.astimezone().isoformat())
                                ET.SubElement(RECEPCION, '{%s}FechaYHoraFinalRecepcion'% covol).text =str(recepcion.FechaYHoraFinalRecepcion.astimezone().isoformat())
                                Complemento = ET.SubElement(RECEPCION, '{%s}Complemento'% covol)
                                #Complemento.text =''
                                tipo = str('comercializador')
                                id_complemento_recepcion =2
                                DailyReportFuntionsInstance = DailyReportFuntions(2)
                                complementos_date = DailyReportFuntionsInstance.GetComplementDailyReportAll(id_complemento_recepcion,tipo,'C',recepcion,'R_cv')

                                print(f"aqui tadeo{recepcion.Complemento}")

                                Complemento_Comercializacion_Recepcion = ET.SubElement(Complemento, '{%s}Complemento_Comercializacion' %covol)
                                if complementos_date:
                                    for complementos in complementos_date:
                                            """
                                            terminalAlmYTrans = complementos['TERMINALALMYTRANS_TERMINALALMYDIST']

                                            Terminalalmtrans = ET.SubElement(Complemento_Comercializacion_Recepcion, '{%s}TERMINALALMYTRANS' % dis )
                                            Almacenamiento = ET.SubElement(Terminalalmtrans, '{%s}Almacenamiento' % dis)
                                            ET.SubElement(Almacenamiento, '{%s}TerminalAlm' % dis).text =  str(terminalAlmYTrans['Almacenamiento'].TerminalAlm)
                                            ET.SubElement(Almacenamiento, '{%s}PermisoAlmacenamiento' % dis).text = str(terminalAlmYTrans['Almacenamiento'].PermisoAlmacenamiento)
                                            ET.SubElement(Almacenamiento, '{%s}TarifaDeAlmacenamiento' % dis).text = str(terminalAlmYTrans['Almacenamiento'].TarifaDeAlmacenamiento )
                                            ET.SubElement(Almacenamiento, '{%s}CargoPorCapacidadAlmac' % dis).text = str(terminalAlmYTrans['Almacenamiento'].CargoPorCapacidadAlmac) 
                                            ET.SubElement(Almacenamiento, '{%s}CargoPorUsoAlmac' % dis).text = str(terminalAlmYTrans['Almacenamiento'].CargoPorUsoAlmac )
                                            ET.SubElement(Almacenamiento, '{%s}CargoVolumetricoAlmac' % dis).text = str(terminalAlmYTrans['Almacenamiento'].CargoVolumetricoAlmac) 

                                            Transporte = ET.SubElement(Terminalalmtrans, '{%s}Transporte' % dis)
                                            ET.SubElement(Transporte, '{%s}PermisoTransporte' % dis).text = str(terminalAlmYTrans['Transporte'].PermisoTransporte)
                                            ET.SubElement(Transporte, '{%s}ClaveDeVehiculo' % dis).text =str(terminalAlmYTrans['Transporte'].ClaveDeVehiculo)
                                            ET.SubElement(Transporte, '{%s}TarifaDeTransporte'% dis).text = str(terminalAlmYTrans['Transporte'].TarifaDeTransporte)
                                            ET.SubElement(Transporte, '{%s}CargoPorCapacidadTrans'% dis).text = str(terminalAlmYTrans['Transporte'].CargoPorCapacidadTrans)
                                            ET.SubElement(Transporte, '{%s}CargoPorUsoTrans'% dis).text = str(terminalAlmYTrans['Transporte'].CargoPorUsoTrans)
                                            ET.SubElement(Transporte, '{%s}CargoVolumetricoTrans'% dis).text =str(terminalAlmYTrans['Transporte'].CargoVolumetricoTrans)
                                            ET.SubElement(Transporte, '{%s}TarifaDeSuministro'% dis).text = str(terminalAlmYTrans['Transporte'].CargoVolumetricoTrans)

                                            for trasvase in complementos['TRASVASE']:

                                                Trasvase = ET.SubElement(Complemento_Comercializacion_Recepcion, '{%s}TRASVASE'% dis)
                                                ET.SubElement(Trasvase, '{%s}NombreTrasvase' % dis).text =  str(trasvase['TRASVASE'].NombreTrasvase)
                                                ET.SubElement(Trasvase, '{%s}RfcTrasvase' % dis).text = str(trasvase['TRASVASE'].RfcTrasvase)
                                                ET.SubElement(Trasvase, '{%s}PermisoTrasvase' % dis).text =str(trasvase['TRASVASE'].PermisoTrasvase)
                                                ET.SubElement(Trasvase, '{%s}DescripcionTrasvase' % dis).text =  str(trasvase['TRASVASE'].DescripcionTrasvase)
                                                ET.SubElement(Trasvase, '{%s}CfdiTrasvase' % dis).text = str(trasvase['TRASVASE'].CfdiTrasvase)

                                            dictamen =complementos['DICTAMEN']
                                            Dictamen = ET.SubElement(Complemento_Comercializacion_Recepcion, '{%s}DICTAMEN'% dis)
                                            ET.SubElement(Dictamen, '{%s}RfcDictamen' % dis).text = str(dictamen['DICTAMEN'].RfcDictamen)
                                            ET.SubElement(Dictamen, '{%s}LoteDictamen' % dis).text = str(dictamen['DICTAMEN'].LoteDictamen)
                                            ET.SubElement(Dictamen, '{%s}NumeroFolioDictamen' % dis).text = str(dictamen['DICTAMEN'].NumeroFolioDictamen)
                                            ET.SubElement(Dictamen, '{%s}FechaEmisionDictamen' % dis).text =str(dictamen['DICTAMEN'].ResultadoDictamen)
                                            ET.SubElement(Dictamen, '{%s}ResultadoDictamen' % dis).text = str(dictamen['DICTAMEN'].ResultadoDictamen)
                                            """
                                            certificado = complementos['CERTIFICADO']

                                            Certificado = ET.SubElement(Complemento_Comercializacion_Recepcion, '{%s}CERTIFICADO' % dis)
                                            ET.SubElement(Certificado, '{%s}RfcCertificado' % dis).text = str(certificado['CERTIFICADO'].RfcCertificado)
                                            ET.SubElement(Certificado, '{%s}NumeroFolioCertificado' % dis).text = str(certificado['CERTIFICADO'].NumeroFolioCertificado)
                                            ET.SubElement(Certificado, '{%s}FechaEmisionCertificado' % dis).text = str(certificado['CERTIFICADO'].FechaEmisionCertificado)
                                            ET.SubElement(Certificado, '{%s}ResultadoCertificado' % dis).text = str(certificado['CERTIFICADO'].ResultadoCertificado)   

                                            for nacional in complementos['NACIONAL']:
                                                Nacional = ET.SubElement(Complemento_Comercializacion_Recepcion, '{%s}NACIONAL' % dis)

                                                ET.SubElement(Nacional, '{%s}RfcClienteOProveedor' % dis).text =str(nacional['NACIONAL'].RFC)
                                                ET.SubElement(Nacional, '{%s}NombreClienteOProveedor' % dis).text = str(nacional['NACIONAL'].Nombre_comercial)
                                                if nacional['NACIONAL'].PermisoClienteOProveedor is not None and nacional['NACIONAL'].PermisoClienteOProveedor != '':
                                                    ET.SubElement(Nacional, '{%s}PermisoClienteOProveedor' % dis).text = str(nacional['NACIONAL'].PermisoClienteOProveedor)

                                                for cfdi in nacional['cfdis']:
                                                    CFDIs = ET.SubElement(Nacional, '{%s}CFDIs' % dis)
                                                    ET.SubElement(CFDIs, '{%s}CFDI' % dis).text = str(cfdi.CFDI)
                                                    ET.SubElement(CFDIs, '{%s}TipoCFDI' % dis).text = str(cfdi.TipoCFDI)
                                                    ET.SubElement(CFDIs, '{%s}PrecioVentaOCompraOContrap' % dis).text = str(cfdi.PrecioVentaOCompraOContrap)
                                                    ET.SubElement(CFDIs, '{%s}FechaYHoraTransaccion' % dis).text = str(cfdi.FechaYHoraTransaccion.astimezone().isoformat())
                                                    VolumenDocumentado = ET.SubElement(CFDIs, '{%s}VolumenDocumentado' % dis)
                                                    ET.SubElement(VolumenDocumentado, '{%s}ValorNumerico' % dis).text = str(cfdi.VolumenDocumentado)
                                                    ET.SubElement(VolumenDocumentado, '{%s}UM' % dis).text = str(cfdi.VolumenDocumentado_UM)
                                            """
                                            for extranjero in complementos['EXTRANJERO']:
                                                Extranjero = ET.SubElement(Complemento_Comercializacion_Recepcion, '{%s}EXTRANJERO' % dis)

                                                ET.SubElement(Extranjero, '{%s}PermisoImportacionOExportacion' % dis).text = str(extranjero['EXTRANJERO'].PermisoImportacionOExportacion)
                                                for pedimentos in extranjero['pedimentos']:
                                                    Pedimentos = ET.SubElement(Extranjero, '{%s}PEDIMENTOS' % dis)
                                                    ET.SubElement(Pedimentos, '{%s}PuntoDeInternacionOExtraccion' % dis).text = str(pedimentos.PuntoDeInternacionOExtraccion)
                                                    ET.SubElement(Pedimentos, '{%s}PaisOrigenODestino' % dis).text = str(pedimentos.PaisOrigenODestino)
                                                    ET.SubElement(Pedimentos, '{%s}MedioDeTransEntraOSaleAduana' % dis).text = str(pedimentos.MedioDeTransEntraOSaleAducto)
                                                    ET.SubElement(Pedimentos, '{%s}PedimentoAduanal' % dis).text =str(pedimentos.PedimentosAduanal)
                                                    ET.SubElement(Pedimentos, '{%s}Incoterms'% dis).text = str(pedimentos.Incoterms)
                                                    ET.SubElement(Pedimentos, '{%s}PrecioDeImportacionOExportacion' % dis).text = str(pedimentos.PrecioDeImportacionOExportacion) 

                                                    Volumen_documentado = ET.SubElement(Pedimentos, '{%s}VolumenDocumentado'% dis)
                                                    ET.SubElement(Volumen_documentado, '{%s}ValorNumerico' % dis).text =str(pedimentos.VolumenDocumentado)
                                                    ET.SubElement(Volumen_documentado, '{%s}UM' % dis).text = str(pedimentos.VolumenDocumentado_UM)
                                            """
                                            Aclarcion = ET.SubElement(Complemento_Comercializacion_Recepcion, '{%s}ACLARACION' % dis)
                                            ET.SubElement(Aclarcion, '{%s}Aclaracion' % dis).text = str(complementos['ACLARACION']['ACLARACION'])


                            ENTREGAS = ET.SubElement(TANQUE, '{%s}ENTREGAS'% covol)
                            ET.SubElement(ENTREGAS, '{%s}TotalEntregas'% covol).text =str(tanques['entregas'].TotalEntregas)
                            SumaVolumenEntregado = ET.SubElement(ENTREGAS, '{%s}SumaVolumenEntregado'% covol) 
                            ET.SubElement(SumaVolumenEntregado, '{%s}ValorNumerico'% covol).text =str(tanques['entregas'].SumaVolumenEntregado)
                            ET.SubElement(SumaVolumenEntregado, '{%s}UM'% covol).text =  str(tanques['entregas'].SumaVolumenEntregado_UM)
                            ET.SubElement(ENTREGAS,'{%s}TotalDocumentos'% covol).text = str(tanques['entregas'].TotalDocumentos)
                            ET.SubElement(ENTREGAS,'{%s}SumaVentas'% covol).text =str(tanques['entregas'].SumaVentas)
                            
                            for entrega in tanques['entrega']:
                                ENTREGA = ET.SubElement(ENTREGAS,'{%s}ENTREGA'% covol)
                                ET.SubElement(ENTREGA,'{%s}NumeroDeRegistro'% covol).text = str(entrega.Id )
                                #ET.SubElement(ENTREGA,'{%s}TipoDeRegistro'% covol).text = str(entrega.TipoDeRegistro)

                                VolumenInicialTanque = ET.SubElement(ENTREGA,'{%s}VolumenInicialTanque'% covol)
                                ET.SubElement(VolumenInicialTanque,'{%s}ValorNumerico'% covol).text= str(entrega.VolumenInicialTanque)
                                ET.SubElement(VolumenInicialTanque,'{%s}UM'% covol).text =str(entrega.VolumenInicialTanque_UM)

                                VolumenFinalTanque = ET.SubElement(ENTREGA,'{%s}VolumenFinalTanque'% covol)
                                ET.SubElement(VolumenFinalTanque,'{%s}ValorNumerico'% covol).text =str(entrega.VolumenFinalTanque)
                                VolumenEntregado = ET.SubElement(ENTREGA,'{%s}VolumenEntregado'% covol)
                                ET.SubElement(VolumenEntregado,'{%s}ValorNumerico'% covol).text=str(entrega.VolumenEntregado)
                                ET.SubElement(VolumenEntregado,'{%s}UM'% covol).text =  str(entrega.VolumenEntregado_UM)
                                ET.SubElement(ENTREGA,'{%s}Temperatura'% covol).text = str(round(entrega.Temperatura, 3))
                                ET.SubElement(ENTREGA,'{%s}PresionAbsoluta'% covol).text =str(entrega.PresionAbsoluta) 
                                ET.SubElement(ENTREGA,'{%s}FechaYHoraInicialEntrega'% covol).text  = str(entrega.FechaYHoraInicialEntrega.astimezone().isoformat())
                                ET.SubElement(ENTREGA,'{%s}FechaYHoraFinalEntrega'% covol).text = str(entrega.FechaYHoraFinalEntrega.astimezone().isoformat())
                                #Complemento_Distribucion = ET.SubElement(ENTREGA, '{%s}Complemento_Distribucion'%dis)
                                #complemento_elem_entrega.append(nuevo_elemento_complemento)
                                Complemento = ET.SubElement(ENTREGA, '{%s}Complemento'% covol)

                                tipo = str('comercializador')
                                id_complemento_entrega =2
                                DailyReportFuntionsInstance = DailyReportFuntions(2)
                                complementos_date = DailyReportFuntionsInstance.GetComplementDailyReportAll(id_complemento_entrega,tipo,'C',entrega,'E_cv')

                                logging.debug("complementos_date", complementos_date)
                                logging.debug("complementos_date", type(complementos_date))

                                Complemento_Comercializacion_Entrega = ET.SubElement(Complemento, '{%s}Complemento_Comercializacion' %covol)
                                if complementos_date:
                                    for complementos in complementos_date:
                                            """
                                            terminalAlmYTrans = complementos['TERMINALALMYTRANS_TERMINALALMYDIST']

                                            Terminalalmtrans = ET.SubElement(Complemento_Comercializacion_Entrega, '{%s}TERMINALALMYTRANS' % dis )
                                            Almacenamiento = ET.SubElement(Terminalalmtrans, '{%s}Almacenamiento' % dis)
                                            ET.SubElement(Almacenamiento, '{%s}TerminalAlm' % dis).text = str(terminalAlmYTrans['Almacenamiento'].TerminalAlm)
                                            ET.SubElement(Almacenamiento, '{%s}PermisoAlmacenamiento' % dis).text = str(terminalAlmYTrans['Almacenamiento'].PermisoAlmacenamiento)
                                            ET.SubElement(Almacenamiento, '{%s}TarifaDeAlmacenamiento' % dis).text = str(terminalAlmYTrans['Almacenamiento'].TarifaDeAlmacenamiento)
                                            ET.SubElement(Almacenamiento, '{%s}CargoPorCapacidadAlmac' % dis).text = str(terminalAlmYTrans['Almacenamiento'].CargoPorCapacidadAlmac) 
                                            ET.SubElement(Almacenamiento, '{%s}CargoPorUsoAlmac' % dis).text = str(terminalAlmYTrans['Almacenamiento'].CargoPorUsoAlmac)
                                            ET.SubElement(Almacenamiento, '{%s}CargoVolumetricoAlmac' % dis).text = str(terminalAlmYTrans['Almacenamiento'].CargoVolumetricoAlmac) 

                                            Transporte = ET.SubElement(Terminalalmtrans, '{%s}Transporte' % dis)
                                            ET.SubElement(Transporte, '{%s}PermisoTransporte' % dis).text =str(terminalAlmYTrans['Transporte'].PermisoTransporte)
                                            ET.SubElement(Transporte, '{%s}ClaveDeVehiculo' % dis).text =str(terminalAlmYTrans['Transporte'].ClaveDeVehiculo)
                                            ET.SubElement(Transporte, '{%s}TarifaDeTransporte'% dis).text = str(terminalAlmYTrans['Transporte'].TarifaDeTransporte)
                                            ET.SubElement(Transporte, '{%s}CargoPorCapacidadTrans'% dis).text = str(terminalAlmYTrans['Transporte'].CargoPorCapacidadTrans)
                                            ET.SubElement(Transporte, '{%s}CargoPorUsoTrans'% dis).text = str(terminalAlmYTrans['Transporte'].CargoPorUsoTrans)
                                            ET.SubElement(Transporte, '{%s}CargoVolumetricoTrans'% dis).text = str(terminalAlmYTrans['Transporte'].CargoVolumetricoTrans)
                                            ET.SubElement(Transporte, '{%s}TarifaDeSuministro'% dis).text = str(terminalAlmYTrans['Transporte'].CargoVolumetricoTrans)

                                            for trasvase in complementos['TRASVASE']:

                                                Trasvase = ET.SubElement(Complemento_Comercializacion_Entrega, '{%s}TRASVASE'% dis)
                                                ET.SubElement(Trasvase, '{%s}NombreTrasvase' % dis).text =  str(trasvase['TRASVASE'].NombreTrasvase)
                                                ET.SubElement(Trasvase, '{%s}RfcTrasvase' % dis).text = str(trasvase['TRASVASE'].RfcTrasvase)
                                                ET.SubElement(Trasvase, '{%s}PermisoTrasvase' % dis).text =str(trasvase['TRASVASE'].PermisoTrasvase)
                                                ET.SubElement(Trasvase, '{%s}DescripcionTrasvase' % dis).text =  str(trasvase['TRASVASE'].DescripcionTrasvase)
                                                ET.SubElement(Trasvase, '{%s}CfdiTrasvase' % dis).text = str(trasvase['TRASVASE'].CfdiTrasvase)

                                            dictamen =complementos['DICTAMEN']
                                            Dictamen = ET.SubElement(Complemento_Comercializacion_Entrega, '{%s}DICTAMEN'% dis)
                                            ET.SubElement(Dictamen, '{%s}RfcDictamen' % dis).text = str(dictamen['DICTAMEN'].RfcDictamen)
                                            ET.SubElement(Dictamen, '{%s}LoteDictamen' % dis).text = str(dictamen['DICTAMEN'].LoteDictamen)
                                            ET.SubElement(Dictamen, '{%s}NumeroFolioDictamen' % dis).text = str(dictamen['DICTAMEN'].NumeroFolioDictamen)
                                            ET.SubElement(Dictamen, '{%s}FechaEmisionDictamen' % dis).text =str(dictamen['DICTAMEN'].FechaEmisionDictamen)
                                            ET.SubElement(Dictamen, '{%s}ResultadoDictamen' % dis).text = str(dictamen['DICTAMEN'].ResultadoDictamen)
                                            """
                                            certificado = complementos['CERTIFICADO']
                                            #logging.debug("complementos_TYPE", type(complementos))
                                            Certificado = ET.SubElement(Complemento_Comercializacion_Entrega, '{%s}CERTIFICADO' % dis)
                                            ET.SubElement(Certificado, '{%s}RfcCertificado' % dis).text = str(certificado['CERTIFICADO'].RfcCertificado)
                                            ET.SubElement(Certificado, '{%s}NumeroFolioCertificado' % dis).text = str(certificado['CERTIFICADO'].NumeroFolioCertificado)
                                            ET.SubElement(Certificado, '{%s}FechaEmisionCertificado' % dis).text = str(certificado['CERTIFICADO'].FechaEmisionCertificado)
                                            ET.SubElement(Certificado, '{%s}ResultadoCertificado' % dis).text = str(certificado['CERTIFICADO'].ResultadoCertificado)   

                                            logging.debug("complementos_comp", str(complementos))
                                            #logging.debug("complementos_keys", complementos.keys())
                                            logging.debug("complementos_nacional_1", complementos['NACIONAL'])
                                            for nacional in complementos['NACIONAL']:
                                            #for nacional in complementos:    
                                                logging.debug("nacional_comp", str(nacional))
                                                logging.debug("nacional_NA", nacional['NACIONAL'])
                                                Nacional = ET.SubElement(Complemento_Comercializacion_Entrega, '{%s}NACIONAL' % dis)

                                                ET.SubElement(Nacional, '{%s}RfcClienteOProveedor' % dis).text = str(nacional['NACIONAL'].RFC)
                                                ET.SubElement(Nacional, '{%s}NombreClienteOProveedor' % dis).text = str(nacional['NACIONAL'].Nombre_comercial)
                                                if nacional['NACIONAL'].PermisoClienteOProveedor is not None and nacional['NACIONAL'].PermisoClienteOProveedor != '':
                                                    ET.SubElement(Nacional, '{%s}PermisoClienteOProveedor' % dis).text = str(nacional['NACIONAL'].PermisoClienteOProveedor)
                                                # ET.SubElement(Nacional, '{%s}RfcClienteOProveedor' % dis).text = "abcd881122ff4"
                                                # ET.SubElement(Nacional, '{%s}NombreClienteOProveedor' % dis).text = "Hola mundo"
                                                # ET.SubElement(Nacional, '{%s}PermisoClienteOProveedor' % dis).text = "operador"
                                                for cfdi in nacional['cfdis']:
                                                    CFDIs = ET.SubElement(Nacional, '{%s}CFDIs' % dis)

                                                    ET.SubElement(CFDIs, '{%s}CFDI' % dis).text = str(cfdi.CFDI)
                                                    ET.SubElement(CFDIs, '{%s}TipoCFDI' % dis).text = str(cfdi.TipoCFDI)
                                                    ET.SubElement(CFDIs, '{%s}PrecioVentaOCompraOContrap' % dis).text = str(cfdi.PrecioVentaOCompraOContrap)
                                                    ET.SubElement(CFDIs, '{%s}FechaYHoraTransaccion' % dis).text = str(cfdi.FechaYHoraTransaccion.astimezone().isoformat())
                                                    VolumenDocumentado = ET.SubElement(CFDIs, '{%s}VolumenDocumentado' % dis)
                                                    ET.SubElement(VolumenDocumentado, '{%s}ValorNumerico' % dis).text = str(cfdi.VolumenDocumentado)
                                                    ET.SubElement(VolumenDocumentado, '{%s}UM' % dis).text = str(cfdi.VolumenDocumentado_UM)

                                            """
                                            for extranjero in complementos['EXTRANJERO']:
                                                Extranjero = ET.SubElement(Complemento_Comercializacion_Entrega, '{%s}EXTRANJERO' % dis)
                                                ET.SubElement(Extranjero, '{%s}PermisoImportacionOExportacion' % dis).text = str(extranjero['EXTRANJERO'].PermisoImportacionOExportacion)
                                                for pedimentos in extranjero['pedimentos']:
                                                    Pedimentos = ET.SubElement(Extranjero, '{%s}PEDIMENTOS' % dis)
                                                    ET.SubElement(Pedimentos, '{%s}PuntoDeInternacionOExtraccion' % dis).text = str(pedimentos.PuntoDeInternacionOExtraccion)
                                                    ET.SubElement(Pedimentos, '{%s}PaisOrigenODestino' % dis).text = str(pedimentos.PaisOrigenODestino)
                                                    ET.SubElement(Pedimentos, '{%s}MedioDeTransEntraOSaleAduana' % dis).text =str(pedimentos.MedioDeTransEntraOSaleAducto)
                                                    ET.SubElement(Pedimentos, '{%s}PedimentoAduanal' % dis).text =str(pedimentos.PedimentosAduanal)
                                                    ET.SubElement(Pedimentos, '{%s}Incoterms'% dis).text = str(pedimentos.Incoterms)
                                                    ET.SubElement(Pedimentos, '{%s}PrecioDeImportacionOExportacion' % dis).text = str(pedimentos.PrecioDeImportacionOExportacion) 

                                                    Volumen_documentado = ET.SubElement(Pedimentos, '{%s}VolumenDocumentado'% dis)
                                                    ET.SubElement(Volumen_documentado, '{%s}ValorNumerico' % dis).text =str(pedimentos.VolumenDocumentado)
                                                    ET.SubElement(Volumen_documentado, '{%s}UM' % dis).text = str(pedimentos.VolumenDocumentado_UM)
                                            """
                                            Aclarcion = ET.SubElement(Complemento_Comercializacion_Entrega, '{%s}ACLARACION' % dis)
                                            ET.SubElement(Aclarcion, '{%s}Aclaracion' % dis).text = str(complementos['ACLARACION']['ACLARACION'])


                for bitacora in bitacora_XML:
                    print(bitacora)

                    fecha_str = bitacora['fecha']
                    fecha_dt = datetime.fromisoformat(fecha_str)  # Convertir la cadena a datetime

                    BITACORA = ET.SubElement(CONTROLES_VOLUMETRICOS, '{%s}BITACORA' % covol)
                    ET.SubElement(BITACORA, '{%s}NumeroRegistro' % covol).text = str( bitacora['numero_registro'])
                    ET.SubElement(BITACORA, '{%s}FechaYHoraEvento' % covol).text = fecha_dt.astimezone().isoformat()
                    usuario_responsable = bitacora.get('UsuarioResponsable', None)
                    if usuario_responsable is not None and bitacora.get('is_event'):
                        ET.SubElement(BITACORA, '{%s}UsuarioResponsable' % covol).text = str(bitacora.get('UsuarioResponsable', '')) if bitacora.get('is_event') else ''
                    
                    ET.SubElement(BITACORA, '{%s}TipoEvento' % covol).text = str(bitacora['tipo'])
                    ET.SubElement(BITACORA, '{%s}DescripcionEvento' % covol).text =  str(bitacora['mensaje'])
                    tipos = ['7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21']
                    if str(bitacora['tipo']) in tipos:
                        ET.SubElement(BITACORA, '{%s}IdentificacionComponenteAlarma' % covol).text =str( bitacora['identificacion'] )


                # Convertir el árbol a un string XML
                #xml_str = ET.tostring(CONTROLES_VOLUMETRICOS, method='html', xml_declaration=True, encoding='UTF-8')
                xml_str = ET.tostring(CONTROLES_VOLUMETRICOS, xml_declaration=True, encoding='utf-8').decode('utf-8')

                # Validar el XML contra el esquema XSD
                try:
                    xml_doc = ET.fromstring(xml_str)
                    #schema.validate(xml_doc)
                except xmlschema.XMLSchemaValidationError as e:
                    error_trace = traceback.format_exc()
                    # Logging detallado
                    logging.debug(f"ValidationError: {str(e)}")
                    logging.debug(f"Traceback: {error_trace}")
                    return f"El XML no es válido: {e}", 400

                # Crear una respuesta Flask con el archivo XML como descarga
                fecha_actual = datetime.now().strftime("%Y_%m_%d")
                file_name = f"D_1AC51FC0-85BF-44E7-AE79-50B030A47C78_DDP860722DN4_ADT161011FC2_{fecha_actual}.xml"
                
                #Ini - Cambio jul-25
                Descripcion = f'Obtención y recuperación de reporte volumetrico XML diario de comercializador del día {fecha_consulta}  '
                Tipo_Evento = 3
                EventosComercializador.add(
                    datetime.now(), current_user.Username, Tipo_Evento, Descripcion, componente
                )
                #Fin - Cambio jul-25
                
                return Response(xml_str, mimetype='application/xml', headers={
                    'Content-Disposition': f'attachment;filename={file_name}'
                })
            else: return jsonify({'error': 'No se encontraron datos para los parámetros proporcionados, pero puedes generar para la fecha que se selecciono con el botón de "GENERAR".'})
        except ValueError as e:
            error_trace = traceback.format_exc()
            # Logging detallado
            logging.debug(f"ValueError: {str(e)}")
            logging.debug(f"Traceback: {error_trace}")
            return jsonify({'error': str(e)})
        except Exception as e:
            error_trace = traceback.format_exc()
            # Logging detallado
            logging.debug(f"Exception: {str(e)}")
            logging.debug(f"Traceback: {error_trace}")
        
    else:  return  jsonify({'error': f'Faltan parámetros necesarios. Por favor, complete todos los campos.'})

def generate_daily_pdf(DailyRepor,periodo):
    General_Report = scaizen_cv_funtions.GeneralReport(2)
    informacion_reporte = cv.ControlesVolumetricos.select_by_id(2)
    SelloDigital = cv.Configuraciones.select_by_clave('SelloDigital')
    SelloDigital = SelloDigital.valor if SelloDigital and hasattr(SelloDigital, 'valor') else ""
    pdf = PDF(data_report=informacion_reporte,headerpage='Reporte Volumétrico Diario',periodo=periodo,SelloDigital=SelloDigital)

    componente = 'comercializador/diario_tanques'
    Descripcion = None
    Tipo_Evento = None

    # Add a page
    pdf.add_page()
    #pdf.add_page()
    for i, producto in enumerate(DailyRepor):
        producto['tanques'] = sorted(producto['tanques'], key=lambda tanque: tanque['tanque'].ClaveIdentificacionTanque)
        for tanque in producto['tanques']:
            # Existencias table
            
            pdf.tanque_text(tanque['tanque'])
            pdf.producto_text(producto["producto"])
            pdf.add_page()
            #pdf.section_title_table(f"TANQUE {tanque['tanque'].ClaveIdentificacionTanque}")
            #headers = ['Volumen Inicial de Tanque', 'Volumen Recepción / Descargas (Recibido)', 'Volumen Final de Tanque']
            headers_R_E = ['Fecha y hora', 'Vol. Natural', 'Vol. Neto','No','Vol. Natural','Vol. Neto','Temp','Presión Abs','Costo','Fecha y hora','Vol. Natural', 'Vol. Neto']\
            #Tabla de recepciones
            rows = []
            sizes = [12, 9, 9, 5, 9, 9, 5, 7, 7, 12, 9, 9] #Porcentaje
            for recepcion in tanque['recepcion']:
                row = [recepcion.FechaYHoraInicialRecepcion.strftime("%Y-%m-%d %H:%M:%S"),recepcion.VolumenInicialTanque,'',recepcion.Id,recepcion.VolumenRecepcion,recepcion.VolumenRecepcionNeto,
                    round(recepcion.Temperatura,2),round(recepcion.PresionAbsoluta,2),round(recepcion.Costo,2),recepcion.FechaYHoraFinalRecepcion.strftime("%Y-%m-%d %H:%M:%S"),recepcion.VolumenFinalTanque,'']
                rows.append(row)
            if not rows:
                rows = [['---' for _ in range(12)]]
            headers_sizes = [30,43,30] #Porcentaje
            headers = ['Volumen Inicial de Tanque','Volumen Recepción / Descargas (Recibido)','Volumen Final de Tanque']
            pdf.table_headers(headers_sizes,headers)
            pdf.create_table_tank(sizes,headers_R_E, rows)
            pdf.ln()
            row_height = 6  # Ajusta según la altura de cada fila
            table_height = len(rows) * row_height + 20  # 20 es un margen adicional para el encabezado

            pdf.check_page_break(table_height)
            
            #Tabla de entregas
            rows = []
            for entrega in tanque['entrega']:
                row = [entrega.FechaYHoraInicialEntrega.strftime("%Y-%m-%d %H:%M:%S"),entrega.VolumenInicialTanque,'',entrega.Id,entrega.VolumenEntregado,entrega.VolumenEntregadoNeto,
                    round(entrega.Temperatura,2),round(entrega.PresionAbsoluta,2),round(entrega.Costo,2),entrega.FechaYHoraFinalEntrega.strftime("%Y-%m-%d %H:%M:%S"),entrega.VolumenFinalTanque,'']
                rows.append(row)
            if not rows:
                rows = [['---' for _ in range(12)]]
            headers_sizes = [30,43,30] #Porcentaje
            headers = ['Volumen Inicial de Tanque','Volumen Entrega / Cargas (Salidas)','Volumen Final de Tanque']
            
            pdf.table_headers(headers_sizes,headers)
            pdf.create_table_tank(sizes,headers_R_E, rows)
            pdf.ln()
            row_height = 6  # Ajusta según la altura de cada fila
            table_height = len(rows) * row_height + 20  # 20 es un margen adicional para el encabezado

            pdf.check_page_break(table_height)
            
            #Tabla de exixtencias, total de recepciones y total de entregas
            sizes2 = [9,9,9,9,7,7,9,9,9,9,9,9] #Porcentaje
            headers = ['Volumen Anterior','Volumen en Recepciones','Volumen en Entregas','Volumen Existente','Total de Recepciones','Total de Documentos',
                    'Volumen Recibido','Compras','Total de Entregas','Total de Documentos','Volumen Entregado','Ventas']
            rows = [[tanque['existencias'].VolumenExistenciasAnterior,tanque['existencias'].VolumenAcumOpsRecepcion,tanque['existencias'].VolumenAcumOpsEntrega,tanque['existencias'].VolumenExistencias,
                    tanque['recepciones'].TotalRecepciones,tanque['recepciones'].TotalDocumentos,tanque['recepciones'].SumaVolumenRecepcion,tanque['recepciones'].SumaCompras,
                    tanque['entregas'].TotalEntregas,tanque['entregas'].TotalDocumentos,tanque['entregas'].SumaVolumenEntregado,tanque['entregas'].SumaVentas]]
            headers_sizes = [35,32,35] #Porcentaje
            headers2 = ['Existencias','	Recepciones (Recibido)','Entregas (Salidas)']
            pdf.table_headers(headers_sizes,headers2)
            pdf.create_table_tank(sizes2,headers, rows)
            pdf.ln()
            #pdf.check_page_break(50)
            if i < len(DailyRepor) - 1:
                pdf.add_page()

    # Generar el PDF en memoria
    pdf_output = pdf.output(dest='S').encode('latin1')

    #Ini - Cambio jul-25
    Descripcion = f'Obtención y recuperación de reporte volumetrico PDF diario de comercializador del periodo {periodo}  '
    Tipo_Evento = 3
    EventosComercializador.add(
        datetime.now(), current_user.Username, Tipo_Evento, Descripcion, componente
    )
    #Fin - Cambio jul-25

    return pdf_output

@app_comercializador.route('/informe_de_tanque_PDF', methods=['GET','POST'])
@login_required
def informe_de_tanque_PDF():
    with VerificarPermisosUsuario("CReportediarioPDF", current_user.RolPerms) as contexto:
        if contexto is False:  # No tiene permisos
            return jsonify({'error':'El usuario actual no tiene los permisos para ejecutar esta accion.','action':'redirect'})
    GeneralReportInstance = scaizen_cv_funtions.GeneralReport(2)

    productoSelect = request.args.get('productoSelect')
    tanqueSelect = request.args.get('tanqueSelect')
    startDate = request.args.get('startDate')
    if productoSelect and startDate and tanqueSelect:
        try:
            # Parse startDate and add time if necessary
            startDate_obj = datetime.strptime(startDate, '%Y-%m-%dT%H:%M:%S.%fZ')
            # Añadir la hora "00:00:00"
            startDate = startDate_obj.replace(hour=00, minute=00, second=00)

            DailyReportFuntionsInstance = scaizen_cv_funtions.DailyReportFuntions(2)
            DailyRepor = None
            if productoSelect == 'all' and tanqueSelect == 'all':
                DailyRepor = DailyReportFuntionsInstance.GetDailyReportAll(startDate)
            elif productoSelect != 'all' and tanqueSelect == 'all':
                producto_id = GeneralReportInstance.GiveProductNameById(productoSelect)
                DailyRepor = DailyReportFuntionsInstance.GetDailyReportByProductAll(producto_id,startDate)
            elif productoSelect != 'all' and tanqueSelect != 'all':
                producto_id = GeneralReportInstance.GiveProductNameById(productoSelect)
                DailyRepor = DailyReportFuntionsInstance.GetDailyReportByProductAndTank(producto_id,tanqueSelect,startDate)
            elif productoSelect == 'all' and tanqueSelect != 'all':
                DailyRepor = DailyReportFuntionsInstance.GetDailyReportByOneTank(tanqueSelect,startDate)
            if DailyRepor:
                periodo = startDate_obj.strftime("%Y-%m-%d")
                pdf_output = generate_daily_pdf(DailyRepor,periodo)
                filename = f'Reporte_diario_{startDate_obj.strftime("%Y%m%d")}_{datetime.now().strftime("%Y%m%d%H%M%S")}.pdf'
                return Response(pdf_output, mimetype='application/pdf', headers={
                        'Content-Disposition': f'attachment;filename={filename}'
                })
            else: return jsonify({'error': 'No se encontraron datos para los parámetros proporcionados.'})
        except ValueError as e:
            print(ValueError)
            return jsonify({'error': f'Formato de fecha inválido: {e}'}), 400
    else:  return  jsonify({'error': 'Faltan parámetros necesarios. Por favor, complete todos los campos2.'})

# Reportes mensuales #
def eliminar_claves_vacias(d):
    if not isinstance(d, dict):
        return d

    # Recorrer todas las claves y valores del diccionario
    return {k: eliminar_claves_vacias(v) for k, v in d.items() if v not in (None, '', [], {})}

def fill_mensual_data(producto):

    control_volumetrico = {
        'ClaveProducto': producto["producto"].ClaveProducto,
        'ClaveSubProducto': producto["producto"].ClaveSubProducto,
        'MarcaComercial':producto["producto"].MarcaComercial,
        'nombre_producto': producto["producto"].nombre_producto,
        'GasolinaConCombustibleNoFosil':producto["producto"].GasolinaConCombustibleNoFosil,
        'ComposDeCombustibleNoFosilEnGasolina':producto["producto"].ComposDeCombustibleNoFosilEnGasolina,
        'ComposOctanajeGasolina':producto["producto"].ComposOctanajeGasolina,
        'DieselConCombustibleNoFosil':producto["producto"].DieselConCombustibleNoFosil,
        'ComposDeCombustibleNoFosilEnDiesel':producto["producto"].ComposDeCombustibleNoFosilEnDiesel,
        'REPORTEDEVOLUMENMENSUAL':{
            'CONTROLDEEXISTENCIAS':{
                'VolumenExistenciasMes':{'ValorNumerico':round(producto["existencias"].CONTROLDEEXISTENCIAS_VolumenExistenciasMes,3)},
                'FechaYHoraEstaMedicionMes':producto["existencias"].CONTROLDEEXISTENCIAS_FechaYHoraEstaMedicionMes
            },
            'RECEPCIONES':{
                'TotalRecepcionesMes': producto["recepciones"].TotalRecepcionesMes,
                'SumaVolumenRecepcionMes':{
                    'ValorNumerico':round(producto["recepciones"].SumaVolumenRecepcionesMes,0),
                    'UnidadDeMedida':producto["recepciones"].SumaVolumenRecepcionesMes_UM
                    },
                'TotalDocumentosMes': producto["recepciones"].TotalDocumentosMes,
                'ImporteTotalRecepcionesMensual': round(producto["recepciones"].ImporteTotalRecepcionesMensual,3)
            },
            'ENTREGAS':{
                'TotalEntregasMez': producto["entregas"].TotalEntregasMes,
                'SumaVolumenEntregadoMes':{
                    'ValorNumerico':round(producto["entregas"].SumaVolumenEntregadoMes,0),
                    'UnidadDeMedida':producto["entregas"].SumaVolumenEntregadoMes_UM
                },
                'TotalDocumentosMes': producto["entregas"].TotalDocumentosMes,
                'ImporteTotalEntregasMes': round(producto["entregas"].ImporteTotalRecepcionesMensual,3)
            } 
        },
        'VolumenUnidadDeMedida': "Litro(s)"
        }
    return control_volumetrico

def REPORTE_MENSUAL_COMBINADO_JSON(productos_data,fecha_corte):

    componente = 'distribuidor/REPORTE_MENSUAL_JSON'
    Descripcion = None
    Tipo_Evento = None

    informacion_reporte = cv.ControlesVolumetricos.select_by_id(1)

    date_start = fecha_corte.replace(day=1)

    #bitacora_JSON = cv.EventosAlarmasDistribuidor.select_events_and_alarms_between_dates(date_start,fecha_corte)
    bitacora_JSON = cv.EventosComercializador.select_events_between_dates(date_start,fecha_corte)

    
    for producto in productos_data[0]:
        #id_complemento_recepcion = producto["recepciones"].Complemento
        logging.debug(f"recepciones {producto}")
        logging.debug(cv.query_to_json([producto]))
        id_complemento_recepcion = 1
        id_complemento_entrega = 1
        
    caracter  = {
        'Caracter':informacion_reporte.TipoCaracter,#Requerida
        'ModalidadPermiso':informacion_reporte.ModalidadPermiso if informacion_reporte.TipoCaracter == 'permisionario' else '',#Si seleciono permisionario en Caracter
        'NumPermiso': informacion_reporte.NumPermiso if informacion_reporte.TipoCaracter in ['contratista','asignatario'] else '',#Si seleciono contratista o asignatario en Caracter
        'NumContratoOAsignacion':informacion_reporte.NumContratoOAsignacion if informacion_reporte.TipoCaracter in ['contratista','asignatario'] else '',#Si seleciono contratista o asignatario en Caracter
        'InstalacionAlmacenGasNatural': informacion_reporte.InstalacionAlmacenGasNatural if informacion_reporte.TipoCaracter == 'usuario' else '' #Si seleciono usuario en Caracter
    }

    gaslp = {
        'CamposDePropanoEnGasLP':'',
        'ComposDeButanoGasLP':''
    }

    petroleo = {
        'DensidadDePetroleo':'',
        'ComposDeAzufreEnPetroleo':''
    }

    gasnaturalocondensados = {
        'ComposGasNaturalOCondensados':'', #Si seleciono contratista o asignatario en Caracter y si ClaveProducto PR09 o PR10
        'FraccionMolar':'',
        'PoderCalorifico':''
    }

    otros = {}
    producto_r_podercalorifico = { 
        'ValorNumerico':'',
        'UnidadDeMedida':''
    }
    
    producto_e_podercalorifico = { 
        'ValorNumerico':'',
        'UnidadDeMedida':''
    }

    productos_reporte = []
    
    for producto in productos_data[0]:
        tipo = str('comercializador')
        id_complemento_recepcion = 1
        id_complemento_entrega = 1

        cargas = cv.CargaDistribuidor.get_by_date_and_producto(producto["producto"].nombre_producto, date_start, fecha_corte)
        descargas = cv.DescargasDistribuidor.get_by_date_and_producto(producto["producto"].nombre_producto, date_start, fecha_corte)
        complemento_distribuidor_recepcion = []
        complemento_distribuidor_entrega = []
        for carga in cargas:
            complemento = Comp_Distribucion.Comp_Distribucion_schema_json(id_complemento_recepcion,tipo,'C',carga)
            #logging.debug("complemento C")
            #logging.debug(complemento)
            if complemento:
                complemento_distribuidor_entrega.append(complemento)
            else: return jsonify(complemento)
        #id_complemento_entrega = producto["entregas"].Complemento
        print(f"entregas {producto['entregas']}")
        for descarga in descargas:
            complemento = Comp_Distribucion.Comp_Distribucion_schema_json(id_complemento_entrega,tipo,'D',descarga)
            #logging.debug("complemento D")
            #logging.debug(complemento)
            if complemento:
                complemento_distribuidor_recepcion.append(complemento)
            else: return jsonify(complemento)


        tipo = str('comercializador')
        id_complemento_recepcion = 2
        id_complemento_entrega = 2
        cargas_c = cv.CargasComercializador.get_by_date_and_producto(producto["producto"].nombre_producto, date_start, fecha_corte)
        descargas_c = cv.DescargasComercializador.get_by_date_and_producto(producto["producto"].nombre_producto, date_start, fecha_corte)
        for carga_c in cargas_c:
            complemento = Comp_Comercializador.Comp_Comercializacion_schema_json(id_complemento_recepcion,tipo,'C',carga_c,'R_cv')
            logging.debug("complemento C")
            logging.debug(carga_c)
            logging.debug(complemento)
            if complemento:
                complemento_distribuidor_entrega.append(complemento)
            else: return jsonify(complemento)
        #id_complemento_entrega = producto["entregas"].Complemento
        print(f"entregas {producto['entregas']}")
        for descarga_c in descargas_c:
            complemento = Comp_Comercializador.Comp_Comercializacion_schema_json(id_complemento_entrega,tipo,'C',descarga_c,'E_cv')
            #logging.debug("complemento D")
            logging.debug(complemento)
            if complemento:
                complemento_distribuidor_recepcion.append(complemento)
            else: return jsonify(complemento)


        producto_item = {
                'ClaveProducto':producto["producto"].ClaveProducto,
                'ClaveSubProducto':producto["producto"].ClaveSubProducto,
                'ReporteDeVolumenMensual':{
                    'ControlDeExistencias':{
                        'VolumenExistenciasMes':round(producto["existencias"].CONTROLDEEXISTENCIAS_VolumenExistenciasMes,5),
                        'FechaYHoraEstaMedicionMes':producto["existencias"].CONTROLDEEXISTENCIAS_FechaYHoraEstaMedicionMes
                    },
                    'Recepciones':{
                        'TotalRecepcionesMes':producto["recepciones"].TotalRecepcionesMes,
                        'SumaVolumenRecepcionMes':{
                            'ValorNumerico':round(producto["recepciones"].SumaVolumenRecepcionesMes,5),
                            'UnidadDeMedida':producto["recepciones"].SumaVolumenRecepcionesMes_UM
                        },
                        'PoderCalorifico':producto_r_podercalorifico if producto["producto"].ClaveProducto == 'PR09' and informacion_reporte.TipoCaracter in ['permisionarios','usuarios'] else '',# Si permisionarios y usuarios en caracter que hayan seleccionado el producto PR09
                        'TotalDocumentosMes':producto["recepciones"].TotalDocumentosMes,
                        'ImporteTotalRecepcionesMensual':round(producto["recepciones"].ImporteTotalRecepcionesMensual,3),
                        'Complemento':complemento_distribuidor_recepcion if complemento_distribuidor_recepcion !=[] else [Comp_Distribucion.Comp_Distribucion_schema_json(id_complemento_recepcion,tipo,'D',None)]
                    },
                    'Entregas':{
                            'TotalEntregasMes':producto["entregas"].TotalEntregasMes,
                            'SumaVolumenEntregadoMes':{
                                'ValorNumerico':round(producto["entregas"].SumaVolumenEntregadoMes,5),
                                'UnidadDeMedida':producto["entregas"].SumaVolumenEntregadoMes_UM                            
                            },
                            'PoderCalorifico':producto_e_podercalorifico if producto["producto"].ClaveProducto == 'PR09' and informacion_reporte.TipoCaracter in ['permisionarios','usuarios'] else '',
                            'TotalDocumentosMes':producto["entregas"].TotalDocumentosMes,
                            'ImporteTotalEntregasMes':round(producto["entregas"].ImporteTotalRecepcionesMensual,3),
                            'Complemento': complemento_distribuidor_entrega if complemento_distribuidor_entrega !=[] else [Comp_Distribucion.Comp_Distribucion_schema_json(id_complemento_recepcion,tipo,'C',None)]
                        }
                },
                'DieselConCombustibleNoFosil':producto["producto"].DieselConCombustibleNoFosil if producto["producto"].ClaveProducto == 'PR03' else '',
                'ComposDeCombustibleNoFosilEnDiesel':producto["producto"].ComposDeCombustibleNoFosilEnDiesel if producto["producto"].ClaveProducto == 'PR03' and producto["producto"].GasolinaConCombustibleNoFosil == 'Sí' else '',#Si DieselConCombustibleNofosil es si
                'ComposOctanajeGasolina':producto["producto"].ComposOctanajeGasolina if producto["producto"].ClaveProducto == 'PR07' else '',
                'GasolinaConCombustibleNoFosil':producto["producto"].GasolinaConCombustibleNoFosil if producto["producto"].ClaveProducto == 'PR07' else '',
                'ComposDeCombustibleNoFosilEnGasolina':producto["producto"].ComposDeCombustibleNoFosilEnGasolina if producto["producto"].ClaveProducto == 'PR07' and producto["producto"].TurbosinaConCombustibleNoFosil == 'Sí' else '',#Si GasolinaConCombustibleNoFosil es si
                'TurbosinaConCombustibleNoFosil':producto["producto"].TurbosinaConCombustibleNoFosil if producto["producto"].ClaveProducto == 'PR11' else '',
                'ComposDeCombustibleNoFosilEnTurbosina':producto["producto"].ComposDeCombustibleNoFosilEnTurbosina if producto["producto"].ClaveProducto == 'PR11' and producto["producto"].TurbosinaConCombustibleNoFosil == 'Sí' else '',#Si TurbosinaConCombustibleNoFosil es si
                #'Gasolina':gasolina if producto["producto"].ClaveProducto == 'PR07' else '',#Si ClaveProducto es PR07
                #'Diesel':diesel if producto["producto"].ClaveProducto == 'PR03' else '',#Si ClaveProducto es PR03
                #'Turbosina':turbosina if producto["producto"].ClaveProducto == 'PR11' else '', #Si ClaveProducto PR11
                #'GasLP':gaslp if producto["producto"].ClaveProducto == 'PR12' else '',#Si ClaveProducto PR12
                #'Petroleo': petroleo if producto["producto"].ClaveProducto == 'PR08' and informacion_reporte.TipoCaracter in ['contratista','asignatario']  else '', #Si ClaveProducto PR08
                #'GasNaturalOCondensados':gasnaturalocondensados if producto["producto"].ClaveProducto in ['PR09','PR10'] and informacion_reporte.TipoCaracter in ['contratista','asignatario']  else '',
                #'Otros':otros if producto["producto"].ClaveProducto in ['PR15','PR20'] and informacion_reporte.TipoCaracter == 'SP20' else '',#Si ClaveProducto PR15, PR20 y ClaveSubProducto SP20
                'MarcaComercial':producto["producto"].MarcaComercial, #Si el producto o subproducto cuente con alguna marca comercial
                'Marcaje':producto["producto"].Marcaje, #Si el producto o subproducto cuente con alguna sustancia quimica empleada como marcador
                'ConcentracionSustanciaMarcaje':producto["producto"].ConcentracionSustanciasMarcaje#Si Marcaje existe
            }
        producto_item = eliminar_claves_vacias(producto_item)
        productos_reporte.append(producto_item)

        bitacora_reporte= [] 
        if bitacora_JSON:
            #print(f"aqui tadeos2s{bitacora_JSON}")
            for bitacora in bitacora_JSON: 
                #print(f"aqui tadeos3s{bitacora}")
                tipos = ['7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21']

                bitacora_item={
                                'NumeroRegistro':bitacora['numero_registro']  ,
                                'FechaYHoraEvento':bitacora['fecha'],
                                'UsuarioResponsable':bitacora['UsuarioResponsable'] if bitacora['is_event'] else '',
                                'TipoEvento':bitacora['tipo'],
                                'DescripcionEvento':bitacora['mensaje'],
                                **({'IdentificacionComponenteAlarma': bitacora['identificacion']} if str(bitacora['tipo']) in tipos else {})
                            }
                bitacora_item = eliminar_claves_vacias(bitacora_item)
                bitacora_reporte.append(bitacora_item)
        
    #bitacora_JSON = cv.EventosAlarmasDistribuidor.select_events_and_alarms_between_dates(date_start,fecha_corte)
    bitacora_JSON = cv.EventosComercializador.select_events_between_dates(date_start,fecha_corte)



    tipo = str('comercializador')
    id_complemento_recepcion = 2
    id_complemento_entrega = 2
    for producto in productos_data[1]:
        
        cargas = cv.CargasComercializador.get_by_date_and_producto(producto["producto"].nombre_producto, date_start, fecha_corte)
        descargas = cv.DescargasComercializador.get_by_date_and_producto(producto["producto"].nombre_producto, date_start, fecha_corte)
        complemento_distribuidor_recepcion = []
        complemento_distribuidor_entrega = []
        for carga in cargas:
            complemento = Comp_Comercializador.Comp_Comercializacion_schema_json(id_complemento_recepcion,tipo,'C',carga,'R_cv')
            #logging.debug("complemento C")
            logging.debug(complemento)
            if complemento:
                complemento_distribuidor_entrega.append(complemento)
            else: return jsonify(complemento)
        #id_complemento_entrega = producto["entregas"].Complemento
        print(f"entregas {producto['entregas']}")
        for descarga in descargas:
            complemento = Comp_Comercializador.Comp_Comercializacion_schema_json(id_complemento_entrega,tipo,'C',descarga,'E_cv')
            #logging.debug("complemento D")
            #logging.debug(complemento)
            if complemento:
                complemento_distribuidor_recepcion.append(complemento)
            else: return jsonify(complemento)

        producto_item = {
                'ClaveProducto':producto["producto"].ClaveProducto,
                'ClaveSubProducto':producto["producto"].ClaveSubProducto,
                'ReporteDeVolumenMensual':{
                    'ControlDeExistencias':{
                        'VolumenExistenciasMes':round(producto["existencias"].CONTROLDEEXISTENCIAS_VolumenExistenciasMes,5),
                        'FechaYHoraEstaMedicionMes':producto["existencias"].CONTROLDEEXISTENCIAS_FechaYHoraEstaMedicionMes
                    },
                    'Recepciones':{
                        'TotalRecepcionesMes':producto["recepciones"].TotalRecepcionesMes,
                        'SumaVolumenRecepcionMes':{
                            'ValorNumerico':round(producto["recepciones"].SumaVolumenRecepcionesMes,5),
                            'UnidadDeMedida':producto["recepciones"].SumaVolumenRecepcionesMes_UM
                        },
                        'PoderCalorifico':producto_r_podercalorifico if producto["producto"].ClaveProducto == 'PR09' and informacion_reporte.TipoCaracter in ['permisionarios','usuarios'] else '',# Si permisionarios y usuarios en caracter que hayan seleccionado el producto PR09
                        'TotalDocumentosMes':producto["recepciones"].TotalDocumentosMes,
                        'ImporteTotalRecepcionesMensual':round(producto["recepciones"].ImporteTotalRecepcionesMensual,3),
                        'Complemento':complemento_distribuidor_recepcion if complemento_distribuidor_recepcion !=[] else [Comp_Distribucion.Comp_Distribucion_schema_json(id_complemento_recepcion,tipo,'D',None)]
                    },
                    'Entregas':{
                            'TotalEntregasMes':producto["entregas"].TotalEntregasMes,
                            'SumaVolumenEntregadoMes':{
                                'ValorNumerico':round(producto["entregas"].SumaVolumenEntregadoMes,5),
                                'UnidadDeMedida':producto["entregas"].SumaVolumenEntregadoMes_UM                            
                            },
                            'PoderCalorifico':producto_e_podercalorifico if producto["producto"].ClaveProducto == 'PR09' and informacion_reporte.TipoCaracter in ['permisionarios','usuarios'] else '',
                            'TotalDocumentosMes':producto["entregas"].TotalDocumentosMes,
                            'ImporteTotalEntregasMes':round(producto["entregas"].ImporteTotalRecepcionesMensual,3),
                            'Complemento':complemento_distribuidor_entrega if complemento_distribuidor_entrega !=[] else [Comp_Distribucion.Comp_Distribucion_schema_json(id_complemento_recepcion,tipo,'C',None)]
                        }
                },
                'DieselConCombustibleNoFosil':producto["producto"].DieselConCombustibleNoFosil if producto["producto"].ClaveProducto == 'PR03' else '',
                'ComposDeCombustibleNoFosilEnDiesel':producto["producto"].ComposDeCombustibleNoFosilEnDiesel if producto["producto"].ClaveProducto == 'PR03' and producto["producto"].GasolinaConCombustibleNoFosil == 'Sí' else '',#Si DieselConCombustibleNofosil es si
                'ComposOctanajeGasolina':producto["producto"].ComposOctanajeGasolina if producto["producto"].ClaveProducto == 'PR07' else '',
                'GasolinaConCombustibleNoFosil':producto["producto"].GasolinaConCombustibleNoFosil if producto["producto"].ClaveProducto == 'PR07' else '',
                'ComposDeCombustibleNoFosilEnGasolina':producto["producto"].ComposDeCombustibleNoFosilEnGasolina if producto["producto"].ClaveProducto == 'PR07' and producto["producto"].TurbosinaConCombustibleNoFosil == 'Sí' else '',#Si GasolinaConCombustibleNoFosil es si
                'TurbosinaConCombustibleNoFosil':producto["producto"].TurbosinaConCombustibleNoFosil if producto["producto"].ClaveProducto == 'PR11' else '',
                'ComposDeCombustibleNoFosilEnTurbosina':producto["producto"].ComposDeCombustibleNoFosilEnTurbosina if producto["producto"].ClaveProducto == 'PR11' and producto["producto"].TurbosinaConCombustibleNoFosil == 'Sí' else '',#Si TurbosinaConCombustibleNoFosil es si
                #'Gasolina':gasolina if producto["producto"].ClaveProducto == 'PR07' else '',#Si ClaveProducto es PR07
                #'Diesel':diesel if producto["producto"].ClaveProducto == 'PR03' else '',#Si ClaveProducto es PR03
                #'Turbosina':turbosina if producto["producto"].ClaveProducto == 'PR11' else '', #Si ClaveProducto PR11
                #'GasLP':gaslp if producto["producto"].ClaveProducto == 'PR12' else '',#Si ClaveProducto PR12
                #'Petroleo': petroleo if producto["producto"].ClaveProducto == 'PR08' and informacion_reporte.TipoCaracter in ['contratista','asignatario']  else '', #Si ClaveProducto PR08
                #'GasNaturalOCondensados':gasnaturalocondensados if producto["producto"].ClaveProducto in ['PR09','PR10'] and informacion_reporte.TipoCaracter in ['contratista','asignatario']  else '',
                #'Otros':otros if producto["producto"].ClaveProducto in ['PR15','PR20'] and informacion_reporte.TipoCaracter == 'SP20' else '',#Si ClaveProducto PR15, PR20 y ClaveSubProducto SP20
                'MarcaComercial':producto["producto"].MarcaComercial, #Si el producto o subproducto cuente con alguna marca comercial
                'Marcaje':producto["producto"].Marcaje, #Si el producto o subproducto cuente con alguna sustancia quimica empleada como marcador
                'ConcentracionSustanciaMarcaje':producto["producto"].ConcentracionSustanciasMarcaje#Si Marcaje existe
            }
        producto_item = eliminar_claves_vacias(producto_item)
        productos_reporte.append(producto_item)

        bitacora_reporte= [] 
        if bitacora_JSON:
            #print(f"aqui tadeos2s{bitacora_JSON}")
            for bitacora in bitacora_JSON: 
                #print(f"aqui tadeos3s{bitacora}")
                tipos = ['7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21']

                bitacora_item={
                                'NumeroRegistro':bitacora['numero_registro']  ,
                                'FechaYHoraEvento':bitacora['fecha'],
                                'UsuarioResponsable':bitacora['UsuarioResponsable'] if bitacora['is_event'] else '',
                                'TipoEvento':bitacora['tipo'],
                                'DescripcionEvento':bitacora['mensaje'],
                                **({'IdentificacionComponenteAlarma': bitacora['identificacion']} if str(bitacora['tipo']) in tipos else {})
                            }
                bitacora_item = eliminar_claves_vacias(bitacora_item)
                bitacora_reporte.append(bitacora_item)
        

    print(informacion_reporte.NumeroDuctosTransporteDistribucion)
    ControlesVolumetricos = {
        'Version':'1.0',
        'RfcContribuyente':informacion_reporte.RfcContribuyente,
        'RfcRepresentanteLegal': informacion_reporte.RfcRepresentanteLegal,
        'RfcProveedor': informacion_reporte.RfcProveedor,
        'RfcProveedores':[informacion_reporte.RfcProveedores],
        'Caracter':informacion_reporte.TipoCaracter,
        'Sello': cv.Configuraciones.select_by_clave('SelloDigial').Valor,
        'ModalidadPermiso':informacion_reporte.ModalidadPermiso if informacion_reporte.TipoCaracter == 'permisionario' else '',#Si seleciono permisionario en Caracter
        'NumPermiso': informacion_reporte.NumPermiso if informacion_reporte.TipoCaracter in ['contratista','asignatario'] else '',#Si seleciono contratista o asignatario en Caracter
        'NumContratoOAsignacion':informacion_reporte.NumContratoOAsignacion if informacion_reporte.TipoCaracter in ['contratista','asignatario'] else '',#Si seleciono contratista o asignatario en Caracter
        'InstalacionAlmacenGasNatural': informacion_reporte.InstalacionAlmacenGasNatural if informacion_reporte.TipoCaracter == 'usuario' else '', #Si seleciono usuario en Caracter
        'ClaveInstalacion': informacion_reporte.ClaveInstalacion,
        'DescripcionInstalacion': informacion_reporte.DescripcionInstalacion,
        'Geolocalizacion': [{
            'GeolocalizacionLatitud': informacion_reporte.GeolocalizacionLatitud,
            'GeolocalizacionLongitud':informacion_reporte.GeolocalizacionLongitud
        }],
        'NumeroPozos': informacion_reporte.NumeroPozos,
        'NumeroTanques':informacion_reporte.NumeroTanques,
        'NumeroDuctosEntradaSalida': informacion_reporte.NumeroDuctosEntradaSalida,
        'NumeroDuctosTransporteDistribucion': informacion_reporte.NumeroDuctosTransporteDistribucion,
        'NumeroDispensarios':informacion_reporte.NumeroDispensarios,
        'FechaYHoraReporteMes':fecha_corte.astimezone().isoformat() ,
        'Producto': productos_reporte,
        'BitacoraMensual': bitacora_reporte        
    }
    
    ControlesVolumetricos = eliminar_claves_vacias(ControlesVolumetricos)
    logging.debug(ControlesVolumetricos)
    try:
        validate(instance=ControlesVolumetricos, schema=estructura_json_mensual)
        json_str = json.dumps(ControlesVolumetricos)
        file_name = f"Reporte_mensual_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        response = Response(
            json_str,
            mimetype='application/json',
            headers={
                'Content-Disposition': f'attachment; filename={file_name}',
                'Content-Type': 'application/json'  # Asegúrate de que el Content-Type sea JSON
            }
        )
        return response
    except ValidationError as e:
        error_trace = traceback.format_exc()
        # Logging detallado
        logging.debug(f"ValidationError: {str(e)}")
        logging.debug(f"Traceback: {error_trace}")
        return jsonify({"error": str(e)}), 400



def REPORTE_MENSUAL_COMBINADO_XML(productos_data, fecha_corte):

    componente = 'comercializador/REPORTE_MENSUAL_XML'
    Descripcion = None
    Tipo_Evento = None
    tipo = str('comercializador')
    id_complemento_recepcion = 1
    id_complemento_entrega = 1
    DailyReportFuntionsInstance = DailyReportFuntions(1)


    # Obtener información del reporte
    informacion_reporte = cv.ControlesVolumetricos.select_by_id(1)
    
    date_start = fecha_corte.replace(day=1)
    #bitacora_XML = cv.EventosAlarmasDistribuidor.select_events_and_alarms_between_dates(date_start,fecha_corte)
    bitacora_XML = cv.EventosComercializador.select_events_between_dates(date_start,fecha_corte)


    schema_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..","static/schemes/distribuidor/Mensual.xsd"))

    schema = xmlschema.XMLSchema11(schema_file)
    
    xsi = 'http://www.w3.org/2001/XMLSchema-instance'
    ET.register_namespace('xsi', xsi)

    xsd = 'http://www.w3.org/2001/XMLSchema'
    ET.register_namespace('xsd',xsd)
                
    tr = 'Complemento_Transporte'
    ET.register_namespace('tr',tr)

    alm= 'Complemento_Almacenamiento'
    ET.register_namespace('alm',alm)

    CDLRGN = 'Complemento_CDLRGN'
    ET.register_namespace('CDLRGN',CDLRGN)

    co = 'Complemento_Comercializacion'
    ET.register_namespace('co',co)

    dis = 'Complemento_Distribucion'
    ET.register_namespace('dis',dis)

    exp = 'Complemento_Expendio'
    ET.register_namespace('exp',exp)

    ext = 'Complemento_Extraccion'
    ET.register_namespace('ext',ext)

    ref = 'Complemento_Refinacion'
    ET.register_namespace('ref',ref)

    covol = 'https://repositorio.cloudb.sat.gob.mx/Covol/xml/Mensuales'
    ET.register_namespace('Covol', covol)

    # Crear el elemento raíz
    root = ET.Element('{%s}ControlesVolumetricos' % covol)

    # Agregar el elemento 'Version'
    ET.SubElement(root, '{%s}Version'% covol).text = "1.0"
        
    # Agregar nodos de información principal
    ET.SubElement(root, '{%s}RfcContribuyente'% covol).text = str(informacion_reporte.RfcContribuyente)
    ET.SubElement(root, '{%s}RfcRepresentanteLegal'% covol).text = str(informacion_reporte.RfcRepresentanteLegal)
    ET.SubElement(root, '{%s}RfcProveedor'% covol).text = str(informacion_reporte.RfcProveedor)
    ET.SubElement(root, '{%s}RfcProveedores'% covol).text = str(informacion_reporte.RfcProveedores)

    # Crear el elemento 'Caracter' y sus subelementos
    caracter = ET.SubElement(root, '{%s}Caracter'% covol)
    ET.SubElement(caracter, '{%s}TipoCaracter'% covol).text = str(informacion_reporte.TipoCaracter)
    if informacion_reporte.TipoCaracter == 'permisionario':
        ET.SubElement(caracter, '{%s}ModalidadPermiso'% covol).text = str(informacion_reporte.ModalidadPermiso)
        ET.SubElement(caracter, '{%s}NumPermiso'% covol).text = str(informacion_reporte.NumPermiso)
    if informacion_reporte.TipoCaracter in ['contratista', 'asignatario']:
        ET.SubElement(caracter, '{%s}NumContratoOAsignacion'% covol).text = str(informacion_reporte.NumContratoOAsignacion)
    if informacion_reporte.TipoCaracter == 'usuario':
        ET.SubElement(caracter, '{%s}InstalacionAlmacenGasNatural'% covol).text = str(informacion_reporte.InstalacionAlmacenGasNatural)
        
    ET.SubElement(root, '{%s}ClaveInstalacion'% covol).text = str(informacion_reporte.ClaveInstalacion)
    ET.SubElement(root, '{%s}DescripcionInstalacion'% covol).text = str(informacion_reporte.DescripcionInstalacion)
    # Geolocalización
    geolocalizacion = ET.SubElement(root, '{%s}Geolocalizacion'% covol)
    ET.SubElement(geolocalizacion, '{%s}GeolocalizacionLatitud'% covol).text = str(informacion_reporte.GeolocalizacionLatitud)
    ET.SubElement(geolocalizacion, '{%s}GeolocalizacionLongitud'% covol).text = str(informacion_reporte.GeolocalizacionLongitud)

    ET.SubElement(root, '{%s}NumeroPozos'% covol).text = str(informacion_reporte.NumeroPozos)
    ET.SubElement(root, '{%s}NumeroTanques'% covol).text = str(informacion_reporte.NumeroTanques)
    ET.SubElement(root, '{%s}NumeroDuctosEntradaSalida'% covol).text = str(informacion_reporte.NumeroDuctosEntradaSalida)
    ET.SubElement(root, '{%s}NumeroDuctosTransporteDistribucion'% covol).text = str(informacion_reporte.NumeroDuctosTransporteDistribucion)
    ET.SubElement(root, '{%s}NumeroDispensarios'% covol).text = str(informacion_reporte.NumeroDispensarios)
    
    # Obtener la fecha y hora actual con la zona horaria
    fecha_hora_corte = fecha_corte.astimezone().strftime('%Y-%m-%dT%H:%M:%S%z')
    # Formatear la zona horaria para incluir dos puntos
    fecha_hora_corte = f"{fecha_hora_corte[:-2]}:{fecha_hora_corte[-2:]}"
    # Agregar el elemento al XML
    
    ET.SubElement(root, '{%s}FechaYHoraReporteMes'% covol).text =fecha_hora_corte #str (datetime.now().astimezone().isoformat() )
    # Productos
    for producto in productos_data[0]:
        tipo = str('comercializador')
        id_complemento_recepcion = 1
        id_complemento_entrega = 1

        cargas = cv.CargaDistribuidor.get_by_date_and_producto(producto["producto"].nombre_producto, date_start, fecha_corte)
        descargas = cv.DescargasDistribuidor.get_by_date_and_producto(producto["producto"].nombre_producto, date_start, fecha_corte)
        complemento_distribuidor_recepcion = []
        complemento_distribuidor_entrega = []
        for carga in cargas:
            #complementos_date = DailyReportFuntionsInstance.GetComplementDailyReportAll(id_complemento_entrega,tipo,'C',entrega,'E_cv')
            #complemento = Comp_Distribucion.Comp_Distribucion_schema_json(id_complemento_recepcion,tipo,'C',carga)
            complemento = DailyReportFuntionsInstance.GetComplementDailyReportAll(id_complemento_entrega,tipo,'C',carga,'E_cv')
            #logging.debug("complemento C")
            #logging.debug(complemento)
            if complemento:
                complemento_distribuidor_entrega.append(complemento[0])
            else: 
                logging.debug(complemento)
                return jsonify(complemento)
        #id_complemento_entrega = producto["entregas"].Complemento
        print(f"entregas {producto['entregas']}")
        for descarga in descargas:
            #complemento = Comp_Distribucion.Comp_Distribucion_schema_json(id_complemento_entrega,tipo,'D',descarga)
            complemento = DailyReportFuntionsInstance.GetComplementDailyReportAll(id_complemento_entrega,tipo,'D',descarga,'R_cv')
            #logging.debug("complemento D")
            #logging.debug(complemento)
            if complemento:
                complemento_distribuidor_recepcion.append(complemento[0])
            else: 
                logging.debug(complemento)
                return jsonify(complemento)
            

        producto_item = ET.SubElement(root, '{%s}PRODUCTO'% covol)

        #producto_item = ET.SubElement(productos_reporte, '{%s}Producto'% covol)
        clave =  producto['producto'].ClaveProducto

        ET.SubElement(producto_item, '{%s}ClaveProducto'% covol).text = clave 
        ET.SubElement(producto_item, '{%s}ClaveSubProducto'% covol).text = str(producto["producto"].ClaveSubProducto)
    
        if clave == "PR07":
                        Gasolina = ET.SubElement(producto_item, '{%s}Gasolina'% covol)
                        ET.SubElement(Gasolina, '{%s}ComposOctanajeGasolina'% covol).text = str(producto['producto'].ComposOctanajeGasolina)
                        ET.SubElement(Gasolina, '{%s}GasolinaConCombustibleNoFosil'% covol).text = producto['producto'].GasolinaConCombustibleNoFosil
                        if producto['producto'].GasolinaConCombustibleNoFosil == 'Si':
                            ET.SubElement(Gasolina, '{%s}ComposDeCombustibleNoFosilEnGasolina'% covol).text = str(producto['producto'].ComposDeCombustibleNoFosilEnGasolina)
        elif clave == "PR03":                       
                        Diesel = ET.SubElement(producto_item, '{%s}Diesel'% covol)
                        ET.SubElement(Diesel, '{%s}DieselConCombustibleNoFosil'% covol).text = producto['producto'].DieselConCombustibleNoFosil
                        if producto['producto'].DieselConCombustibleNoFosil == 'Si':
                            ET.SubElement(Diesel, '{%s}ComposDeCombustibleNoFosilEnDiesel'% covol).text = str(producto['producto'].ComposDeCombustibleNoFosilEnDiesel)
        else:
                        ET.SubElement(producto_item, '{%s}Otros'% covol).text =  producto['producto'].Otros

        ET.SubElement(producto_item, '{%s}MarcaComercial'% covol).text = str(producto["producto"].MarcaComercial)
        if producto['producto'].Marcaje:
            ET.SubElement(producto_item, '{%s}Marcaje'% covol).text = producto['producto'].Marcaje
            if producto['producto'].ConcentracionSustanciasMarcaje and producto['producto'].ConcentracionSustanciasMarcaje > 0:
                ET.SubElement(producto_item, '{%s}ConcentracionSustanciaMarcaje'% covol).text = str(producto['producto'].ConcentracionSustanciasMarcaje)

        reporte_volumen_mensual = ET.SubElement(producto_item, '{%s}REPORTEDEVOLUMENMENSUAL'% covol)
            
        # Control de existencias
        existencias = ET.SubElement(reporte_volumen_mensual, '{%s}CONTROLDEEXISTENCIAS'% covol)
        volumen_existencias_mes = ET.SubElement(existencias, '{%s}VolumenExistenciasMes'% covol)
        ET.SubElement(volumen_existencias_mes, '{%s}ValorNumerico'% covol).text = str(round(producto["existencias"].CONTROLDEEXISTENCIAS_VolumenExistenciasMes, 3))
        ET.SubElement(existencias, '{%s}FechaYHoraEstaMedicionMes'% covol).text = str(producto["existencias"].CONTROLDEEXISTENCIAS_FechaYHoraEstaMedicionMes)
            
        # Recepciones
        recepciones = ET.SubElement(reporte_volumen_mensual, '{%s}RECEPCIONES'% covol)
        ET.SubElement(recepciones, '{%s}TotalRecepcionesMes'% covol).text = str(producto["recepciones"].TotalRecepcionesMes)
        suma_volumen_recepcion_mes = ET.SubElement(recepciones, '{%s}SumaVolumenRecepcionMes'% covol)
        ET.SubElement(suma_volumen_recepcion_mes, '{%s}ValorNumerico'% covol).text = str(round(producto["recepciones"].SumaVolumenRecepcionesMes, 0))
        ET.SubElement(suma_volumen_recepcion_mes, '{%s}UM'% covol).text = str(producto["recepciones"].SumaVolumenRecepcionesMes_UM)
        if producto["producto"].ClaveProducto == 'PR09' and informacion_reporte.TipoCaracter in ['permisionarios','usuarios']:
            PoderCalorifico = ET.SubElement(recepciones, 'PoderCalorifico'% covol)
            ET.SubElement(PoderCalorifico, '{%s}ValorNumerico'% covol).text = str(producto["recepciones"].PoderCalorifico)
            ET.SubElement(PoderCalorifico, '{%s}UM'% covol).text = str(producto["recepciones"].PoderCalorifico_UM)
        ET.SubElement(recepciones, '{%s}TotalDocumentosMes'% covol).text = str(producto["recepciones"].TotalDocumentosMes)
        ET.SubElement(recepciones, '{%s}ImporteTotalRecepcionesMensual'% covol).text = str(producto["recepciones"].ImporteTotalRecepcionesMensual)
        #complemento_elem_recepciones = ET.SubElement(recepciones, 'Complemento'% covol)
        #complemento_elem_recepciones.append(nuevo_elemento_complemento)
        Complemento = ET.SubElement(recepciones, '{%s}Complemento'% covol)
        
        tipo = str('comercializador')
        id_complemento_recepcion = 1
        DailyReportFuntionsInstance = DailyReportFuntions(1)
        recepcion = producto["recepciones"]
        #complementos_date = DailyReportFuntionsInstance.GetComplementDailyReportAll(id_complemento_recepcion,tipo,'D',recepcion,'R_cv')

        if any(complemento_distribuidor_recepcion):
            for complementos in complemento_distribuidor_recepcion:
                
                Complemento_Distribucion_Recepcion = ET.SubElement(Complemento, '{%s}Complemento_Distribucion' %covol)
                """
                terminalAlmYTrans = complementos['TERMINALALMYTRANS_TERMINALALMYDIST']

                Terminalalmtrans = ET.SubElement(Complemento_Distribucion_Recepcion, '{%s}TERMINALALMYTRANS' % dis )
                Almacenamiento = ET.SubElement(Terminalalmtrans, '{%s}Almacenamiento' % dis)
                ET.SubElement(Almacenamiento, '{%s}TerminalAlm' % dis).text =  str(terminalAlmYTrans['Almacenamiento'].TerminalAlm)
                ET.SubElement(Almacenamiento, '{%s}PermisoAlmacenamiento' % dis).text = str(terminalAlmYTrans['Almacenamiento'].PermisoAlmacenamiento)
                ET.SubElement(Almacenamiento, '{%s}TarifaDeAlmacenamiento' % dis).text = str(terminalAlmYTrans['Almacenamiento'].TarifaDeAlmacenamiento )
                ET.SubElement(Almacenamiento, '{%s}CargoPorCapacidadAlmac' % dis).text = str(terminalAlmYTrans['Almacenamiento'].CargoPorCapacidadAlmac) 
                ET.SubElement(Almacenamiento, '{%s}CargoPorUsoAlmac' % dis).text = str(terminalAlmYTrans['Almacenamiento'].CargoPorUsoAlmac )
                ET.SubElement(Almacenamiento, '{%s}CargoVolumetricoAlmac' % dis).text = str(terminalAlmYTrans['Almacenamiento'].CargoVolumetricoAlmac) 

                Transporte = ET.SubElement(Terminalalmtrans, '{%s}Transporte' % dis)
                ET.SubElement(Transporte, '{%s}PermisoTransporte' % dis).text = str(terminalAlmYTrans['Transporte'].PermisoTransporte)
                ET.SubElement(Transporte, '{%s}ClaveDeVehiculo' % dis).text =str(terminalAlmYTrans['Transporte'].ClaveDeVehiculo)
                ET.SubElement(Transporte, '{%s}TarifaDeTransporte'% dis).text = str(terminalAlmYTrans['Transporte'].TarifaDeTransporte)
                ET.SubElement(Transporte, '{%s}CargoPorCapacidadTrans'% dis).text = str(terminalAlmYTrans['Transporte'].CargoPorCapacidadTrans)
                ET.SubElement(Transporte, '{%s}CargoPorUsoTrans'% dis).text = str(terminalAlmYTrans['Transporte'].CargoPorUsoTrans)
                ET.SubElement(Transporte, '{%s}CargoVolumetricoTrans'% dis).text =str(terminalAlmYTrans['Transporte'].CargoVolumetricoTrans)
                ET.SubElement(Transporte, '{%s}TarifaDeSuministro'% dis).text = str(terminalAlmYTrans['Transporte'].CargoVolumetricoTrans)

                for trasvase in complementos['TRASVASE']:

                                Trasvase = ET.SubElement(Complemento_Distribucion_Recepcion, '{%s}TRASVASE'% dis)
                                ET.SubElement(Trasvase, '{%s}NombreTrasvase' % dis).text =  str(trasvase['TRASVASE'].NombreTrasvase)
                                ET.SubElement(Trasvase, '{%s}RfcTrasvase' % dis).text = str(trasvase['TRASVASE'].RfcTrasvase)
                                ET.SubElement(Trasvase, '{%s}PermisoTrasvase' % dis).text =str(trasvase['TRASVASE'].PermisoTrasvase)
                                ET.SubElement(Trasvase, '{%s}DescripcionTrasvase' % dis).text =  str(trasvase['TRASVASE'].DescripcionTrasvase)
                                ET.SubElement(Trasvase, '{%s}CfdiTrasvase' % dis).text = str(trasvase['TRASVASE'].CfdiTrasvase)

                dictamen =complementos['DICTAMEN']
                Dictamen = ET.SubElement(Complemento_Distribucion_Recepcion, '{%s}DICTAMEN'% dis)
                ET.SubElement(Dictamen, '{%s}RfcDictamen' % dis).text = str(dictamen['DICTAMEN'].RfcDictamen)
                ET.SubElement(Dictamen, '{%s}LoteDictamen' % dis).text = str(dictamen['DICTAMEN'].LoteDictamen)
                ET.SubElement(Dictamen, '{%s}NumeroFolioDictamen' % dis).text = str(dictamen['DICTAMEN'].NumeroFolioDictamen)
                ET.SubElement(Dictamen, '{%s}FechaEmisionDictamen' % dis).text =str(dictamen['DICTAMEN'].ResultadoDictamen)
                ET.SubElement(Dictamen, '{%s}ResultadoDictamen' % dis).text = str(dictamen['DICTAMEN'].ResultadoDictamen)
                """
                certificado = complementos['CERTIFICADO']

                Certificado = ET.SubElement(Complemento_Distribucion_Recepcion, '{%s}CERTIFICADO' % dis)
                ET.SubElement(Certificado, '{%s}RfcCertificado' % dis).text = str(certificado['CERTIFICADO'].RfcCertificado)
                ET.SubElement(Certificado, '{%s}NumeroFolioCertificado' % dis).text = str(certificado['CERTIFICADO'].NumeroFolioCertificado)
                ET.SubElement(Certificado, '{%s}FechaEmisionCertificado' % dis).text = str(certificado['CERTIFICADO'].FechaEmisionCertificado)
                ET.SubElement(Certificado, '{%s}ResultadoCertificado' % dis).text = str(certificado['CERTIFICADO'].ResultadoCertificado)   

                if 'NACIONAL' in complementos and complementos['NACIONAL']:
                    for nacional in complementos['NACIONAL']:
                        Nacional = ET.SubElement(Complemento_Distribucion_Recepcion, '{%s}NACIONAL' % dis)

                        ET.SubElement(Nacional, '{%s}RfcClienteOProveedor' % dis).text =str(nacional['NACIONAL'].RFC)
                        ET.SubElement(Nacional, '{%s}NombreClienteOProveedor' % dis).text = str(nacional['NACIONAL'].Nombre_comercial)
                        if nacional['NACIONAL'].PermisoClienteOProveedor is not None and nacional['NACIONAL'].PermisoClienteOProveedor != '':
                            ET.SubElement(Nacional, '{%s}PermisoClienteOProveedor' % dis).text = str(nacional['NACIONAL'].PermisoClienteOProveedor)

                        for cfdi in nacional['cfdis']:
                            CFDIs = ET.SubElement(Nacional, '{%s}CFDIs' % dis)
                            ET.SubElement(CFDIs, '{%s}CFDI' % dis).text = str(cfdi.CFDI)
                            ET.SubElement(CFDIs, '{%s}TipoCFDI' % dis).text = str(cfdi.TipoCFDI)
                            ET.SubElement(CFDIs, '{%s}PrecioVentaOCompraOContrap' % dis).text = str(cfdi.PrecioVentaOCompraOContrap)
                            ET.SubElement(CFDIs, '{%s}FechaYHoraTransaccion' % dis).text = str(cfdi.FechaYHoraTransaccion.astimezone().isoformat())
                            VolumenDocumentado = ET.SubElement(CFDIs, '{%s}VolumenDocumentado' % dis)
                            ET.SubElement(VolumenDocumentado, '{%s}ValorNumerico' % dis).text = str(cfdi.VolumenDocumentado)
                            ET.SubElement(VolumenDocumentado, '{%s}UM' % dis).text = str(cfdi.VolumenDocumentado_UM)
                """
                for extranjero in complementos['EXTRANJERO']:
                        Extranjero = ET.SubElement(Complemento_Distribucion_Recepcion, '{%s}EXTRANJERO' % dis)

                        ET.SubElement(Extranjero, '{%s}PermisoImportacionOExportacion' % dis).text = str(extranjero['EXTRANJERO'].PermisoImportacionOExportacion)
                        for pedimentos in extranjero['pedimentos']:
                                    Pedimentos = ET.SubElement(Extranjero, '{%s}PEDIMENTOS' % dis)
                                    ET.SubElement(Pedimentos, '{%s}PuntoDeInternacionOExtraccion' % dis).text = str(pedimentos.PuntoDeInternacionOExtraccion)
                                    ET.SubElement(Pedimentos, '{%s}PaisOrigenODestino' % dis).text = str(pedimentos.PaisOrigenODestino)
                                    ET.SubElement(Pedimentos, '{%s}MedioDeTransEntraOSaleAduana' % dis).text = str(pedimentos.MedioDeTransEntraOSaleAducto)
                                    ET.SubElement(Pedimentos, '{%s}PedimentoAduanal' % dis).text =str(pedimentos.PedimentosAduanal)
                                    ET.SubElement(Pedimentos, '{%s}Incoterms'% dis).text = str(pedimentos.Incoterms)
                                    ET.SubElement(Pedimentos, '{%s}PrecioDeImportacionOExportacion' % dis).text = str(pedimentos.PrecioDeImportacionOExportacion) 

                                    Volumen_documentado = ET.SubElement(Pedimentos, '{%s}VolumenDocumentado'% dis)
                                    ET.SubElement(Volumen_documentado, '{%s}ValorNumerico' % dis).text =str(pedimentos.VolumenDocumentado)
                                    ET.SubElement(Volumen_documentado, '{%s}UM' % dis).text = str(pedimentos.VolumenDocumentado_UM)
                """
                Aclarcion = ET.SubElement(Complemento_Distribucion_Recepcion, '{%s}ACLARACION' % dis)
                ET.SubElement(Aclarcion, '{%s}Aclaracion' % dis).text = str(complementos['ACLARACION']['ACLARACION'])
        else:
            complemento_distribuidor_recepcion = DailyReportFuntionsInstance.GetComplementDailyReportAll(id_complemento_entrega,tipo,'D',None,None)
            for complementos in complemento_distribuidor_recepcion:
                Complemento_Distribucion_Recepcion = ET.SubElement(Complemento, '{%s}Complemento_Distribucion' %covol)
                certificado = complementos['CERTIFICADO']

                Certificado = ET.SubElement(Complemento_Distribucion_Recepcion, '{%s}CERTIFICADO' % dis)
                ET.SubElement(Certificado, '{%s}RfcCertificado' % dis).text = str(certificado['CERTIFICADO'].RfcCertificado)
                ET.SubElement(Certificado, '{%s}NumeroFolioCertificado' % dis).text = str(certificado['CERTIFICADO'].NumeroFolioCertificado)
                ET.SubElement(Certificado, '{%s}FechaEmisionCertificado' % dis).text = str(certificado['CERTIFICADO'].FechaEmisionCertificado)
                ET.SubElement(Certificado, '{%s}ResultadoCertificado' % dis).text = str(certificado['CERTIFICADO'].ResultadoCertificado)

        logging.debug('Complemento_Distribucion_Recepcion')
        logging.debug(Complemento_Distribucion_Recepcion)
        # Entregas
        entregas = ET.SubElement(reporte_volumen_mensual, '{%s}ENTREGAS'% covol)
        ET.SubElement(entregas, '{%s}TotalEntregasMes'% covol).text = str(producto["entregas"].TotalEntregasMes)
        suma_volumen_entregado_mes = ET.SubElement(entregas, '{%s}SumaVolumenEntregadoMes'% covol)
        ET.SubElement(suma_volumen_entregado_mes, '{%s}ValorNumerico'% covol).text = str(round(producto["entregas"].SumaVolumenEntregadoMes, 0))
        ET.SubElement(suma_volumen_entregado_mes, '{%s}UM'% covol).text = str(producto["entregas"].SumaVolumenEntregadoMes_UM)
        if producto["producto"].ClaveProducto == 'PR09' and informacion_reporte.TipoCaracter in ['permisionarios','usuarios']:
            PoderCalorifico = ET.SubElement(entregas, '{%s}PoderCalorifico'% covol)
            ET.SubElement(PoderCalorifico, '{%s}ValorNumerico'% covol).text = str(producto["recepciones"].PoderCalorifico)
            ET.SubElement(PoderCalorifico, '{%s}UM').text = str(producto["recepciones"].PoderCalorifico_UM)
        ET.SubElement(entregas, '{%s}TotalDocumentosMes'% covol).text = str(producto["entregas"].TotalDocumentosMes)
        ET.SubElement(entregas, '{%s}ImporteTotalEntregasMes'% covol).text = str(producto["entregas"].ImporteTotalRecepcionesMensual)
        #complemento_elem_entregas = ET.SubElement(entregas, '{%s}Complemento'% covol)
        #complemento_elem_entregas.append(nuevo_elemento_complemento)
        
        Complemento = ET.SubElement(entregas, '{%s}Complemento'% covol)
        
                
        tipo = str('comercializador')
        id_complemento_entrega = 1
        DailyReportFuntionsInstance = DailyReportFuntions(1)
        entrega = producto["entregas"]
        #complementos_date = DailyReportFuntionsInstance.GetComplementDailyReportAll(id_complemento_entrega,tipo,'C',entrega,'E_cv')
        

        if complemento_distribuidor_entrega:
            for complementos in complemento_distribuidor_entrega:
                Complemento_Distribucion_Entrega = ET.SubElement(Complemento, '{%s}Complemento_Distribucion' %covol)
                """
                terminalAlmYTrans = complementos['TERMINALALMYTRANS_TERMINALALMYDIST']

                Terminalalmtrans = ET.SubElement(Complemento_Distribucion_Entrega, '{%s}TERMINALALMYTRANS' % dis )
                Almacenamiento = ET.SubElement(Terminalalmtrans, '{%s}Almacenamiento' % dis)
                ET.SubElement(Almacenamiento, '{%s}TerminalAlm' % dis).text =  str(terminalAlmYTrans['Almacenamiento'].TerminalAlm)
                ET.SubElement(Almacenamiento, '{%s}PermisoAlmacenamiento' % dis).text = str(terminalAlmYTrans['Almacenamiento'].PermisoAlmacenamiento)
                ET.SubElement(Almacenamiento, '{%s}TarifaDeAlmacenamiento' % dis).text = str(terminalAlmYTrans['Almacenamiento'].TarifaDeAlmacenamiento )
                ET.SubElement(Almacenamiento, '{%s}CargoPorCapacidadAlmac' % dis).text = str(terminalAlmYTrans['Almacenamiento'].CargoPorCapacidadAlmac) 
                ET.SubElement(Almacenamiento, '{%s}CargoPorUsoAlmac' % dis).text = str(terminalAlmYTrans['Almacenamiento'].CargoPorUsoAlmac )
                ET.SubElement(Almacenamiento, '{%s}CargoVolumetricoAlmac' % dis).text = str(terminalAlmYTrans['Almacenamiento'].CargoVolumetricoAlmac) 

                Transporte = ET.SubElement(Terminalalmtrans, '{%s}Transporte' % dis)
                ET.SubElement(Transporte, '{%s}PermisoTransporte' % dis).text = str(terminalAlmYTrans['Transporte'].PermisoTransporte)
                ET.SubElement(Transporte, '{%s}ClaveDeVehiculo' % dis).text =str(terminalAlmYTrans['Transporte'].ClaveDeVehiculo)
                ET.SubElement(Transporte, '{%s}TarifaDeTransporte'% dis).text = str(terminalAlmYTrans['Transporte'].TarifaDeTransporte)
                ET.SubElement(Transporte, '{%s}CargoPorCapacidadTrans'% dis).text = str(terminalAlmYTrans['Transporte'].CargoPorCapacidadTrans)
                ET.SubElement(Transporte, '{%s}CargoPorUsoTrans'% dis).text = str(terminalAlmYTrans['Transporte'].CargoPorUsoTrans)
                ET.SubElement(Transporte, '{%s}CargoVolumetricoTrans'% dis).text =str(terminalAlmYTrans['Transporte'].CargoVolumetricoTrans)
                ET.SubElement(Transporte, '{%s}TarifaDeSuministro'% dis).text = str(terminalAlmYTrans['Transporte'].CargoVolumetricoTrans)

                for trasvase in complementos['TRASVASE']:

                                Trasvase = ET.SubElement(Complemento_Distribucion_Entrega, '{%s}TRASVASE'% dis)
                                ET.SubElement(Trasvase, '{%s}NombreTrasvase' % dis).text =  str(trasvase['TRASVASE'].NombreTrasvase)
                                ET.SubElement(Trasvase, '{%s}RfcTrasvase' % dis).text = str(trasvase['TRASVASE'].RfcTrasvase)
                                ET.SubElement(Trasvase, '{%s}PermisoTrasvase' % dis).text =str(trasvase['TRASVASE'].PermisoTrasvase)
                                ET.SubElement(Trasvase, '{%s}DescripcionTrasvase' % dis).text =  str(trasvase['TRASVASE'].DescripcionTrasvase)
                                ET.SubElement(Trasvase, '{%s}CfdiTrasvase' % dis).text = str(trasvase['TRASVASE'].CfdiTrasvase)

                dictamen =complementos['DICTAMEN']
                Dictamen = ET.SubElement(Complemento_Distribucion_Entrega, '{%s}DICTAMEN'% dis)
                ET.SubElement(Dictamen, '{%s}RfcDictamen' % dis).text = str(dictamen['DICTAMEN'].RfcDictamen)
                ET.SubElement(Dictamen, '{%s}LoteDictamen' % dis).text = str(dictamen['DICTAMEN'].LoteDictamen)
                ET.SubElement(Dictamen, '{%s}NumeroFolioDictamen' % dis).text = str(dictamen['DICTAMEN'].NumeroFolioDictamen)
                ET.SubElement(Dictamen, '{%s}FechaEmisionDictamen' % dis).text =str(dictamen['DICTAMEN'].ResultadoDictamen)
                ET.SubElement(Dictamen, '{%s}ResultadoDictamen' % dis).text = str(dictamen['DICTAMEN'].ResultadoDictamen)
                """
                certificado = complementos['CERTIFICADO']

                Certificado = ET.SubElement(Complemento_Distribucion_Entrega, '{%s}CERTIFICADO' % dis)
                ET.SubElement(Certificado, '{%s}RfcCertificado' % dis).text = str(certificado['CERTIFICADO'].RfcCertificado)
                ET.SubElement(Certificado, '{%s}NumeroFolioCertificado' % dis).text = str(certificado['CERTIFICADO'].NumeroFolioCertificado)
                ET.SubElement(Certificado, '{%s}FechaEmisionCertificado' % dis).text = str(certificado['CERTIFICADO'].FechaEmisionCertificado)
                ET.SubElement(Certificado, '{%s}ResultadoCertificado' % dis).text = str(certificado['CERTIFICADO'].ResultadoCertificado)   
                
                for nacional in complementos['NACIONAL']:
                    Nacional = ET.SubElement(Complemento_Distribucion_Entrega, '{%s}NACIONAL' % dis)

                    ET.SubElement(Nacional, '{%s}RfcClienteOProveedor' % dis).text =str(nacional['NACIONAL'].RFC)
                    ET.SubElement(Nacional, '{%s}NombreClienteOProveedor' % dis).text = str(nacional['NACIONAL'].Nombre_comercial)
                    if nacional['NACIONAL'].PermisoClienteOProveedor is not None and nacional['NACIONAL'].PermisoClienteOProveedor != '':
                        ET.SubElement(Nacional, '{%s}PermisoClienteOProveedor' % dis).text = str(nacional['NACIONAL'].PermisoClienteOProveedor)

                    for cfdi in nacional['cfdis']:
                            CFDIs = ET.SubElement(Nacional, '{%s}CFDIs' % dis)
                            ET.SubElement(CFDIs, '{%s}CFDI' % dis).text = str(cfdi.CFDI)
                            ET.SubElement(CFDIs, '{%s}TipoCFDI' % dis).text = str(cfdi.TipoCFDI)
                            ET.SubElement(CFDIs, '{%s}PrecioVentaOCompraOContrap' % dis).text = str(cfdi.PrecioVentaOCompraOContrap)
                            ET.SubElement(CFDIs, '{%s}FechaYHoraTransaccion' % dis).text = str(cfdi.FechaYHoraTransaccion.astimezone().isoformat())
                            VolumenDocumentado = ET.SubElement(CFDIs, '{%s}VolumenDocumentado' % dis)
                            ET.SubElement(VolumenDocumentado, '{%s}ValorNumerico' % dis).text = str(cfdi.VolumenDocumentado)
                            ET.SubElement(VolumenDocumentado, '{%s}UM' % dis).text = str(cfdi.VolumenDocumentado_UM)
                """
                for extranjero in complementos['EXTRANJERO']:
                        Extranjero = ET.SubElement(Complemento_Distribucion_Entrega, '{%s}EXTRANJERO' % dis)

                        ET.SubElement(Extranjero, '{%s}PermisoImportacionOExportacion' % dis).text = str(extranjero['EXTRANJERO'].PermisoImportacionOExportacion)
                        for pedimentos in extranjero['pedimentos']:
                                    Pedimentos = ET.SubElement(Extranjero, '{%s}PEDIMENTOS' % dis)
                                    ET.SubElement(Pedimentos, '{%s}PuntoDeInternacionOExtraccion' % dis).text = str(pedimentos.PuntoDeInternacionOExtraccion)
                                    ET.SubElement(Pedimentos, '{%s}PaisOrigenODestino' % dis).text = str(pedimentos.PaisOrigenODestino)
                                    ET.SubElement(Pedimentos, '{%s}MedioDeTransEntraOSaleAduana' % dis).text = str(pedimentos.MedioDeTransEntraOSaleAducto)
                                    ET.SubElement(Pedimentos, '{%s}PedimentoAduanal' % dis).text =str(pedimentos.PedimentosAduanal)
                                    ET.SubElement(Pedimentos, '{%s}Incoterms'% dis).text = str(pedimentos.Incoterms)
                                    ET.SubElement(Pedimentos, '{%s}PrecioDeImportacionOExportacion' % dis).text = str(pedimentos.PrecioDeImportacionOExportacion) 

                                    Volumen_documentado = ET.SubElement(Pedimentos, '{%s}VolumenDocumentado'% dis)
                                    ET.SubElement(Volumen_documentado, '{%s}ValorNumerico' % dis).text =str(pedimentos.VolumenDocumentado)
                                    ET.SubElement(Volumen_documentado, '{%s}UM' % dis).text = str(pedimentos.VolumenDocumentado_UM)
                """
                Aclarcion = ET.SubElement(Complemento_Distribucion_Entrega, '{%s}ACLARACION' % dis)
                ET.SubElement(Aclarcion, '{%s}Aclaracion' % dis).text = str(complementos['ACLARACION']['ACLARACION'])
        else:
            complemento_distribuidor_entrega = DailyReportFuntionsInstance.GetComplementDailyReportAll(id_complemento_entrega,tipo,'C',None,None)
            for complementos in complemento_distribuidor_entrega:
                Complemento_Distribucion_Entrega = ET.SubElement(Complemento, '{%s}Complemento_Distribucion' %covol)
                certificado = complementos['CERTIFICADO']

                Certificado = ET.SubElement(Complemento_Distribucion_Entrega, '{%s}CERTIFICADO' % dis)
                ET.SubElement(Certificado, '{%s}RfcCertificado2' % dis).text = str(certificado['CERTIFICADO'].RfcCertificado)
                ET.SubElement(Certificado, '{%s}NumeroFolioCertificado2' % dis).text = str(certificado['CERTIFICADO'].NumeroFolioCertificado)
                ET.SubElement(Certificado, '{%s}FechaEmisionCertificado2' % dis).text = str(certificado['CERTIFICADO'].FechaEmisionCertificado)
                ET.SubElement(Certificado, '{%s}ResultadoCertificado2' % dis).text = str(certificado['CERTIFICADO'].ResultadoCertificado)

    
    tipo = str('comercializador')
    id_complemento_recepcion = 2
    id_complemento_entrega = 2
    DailyReportFuntionsInstance = DailyReportFuntions(2)

    for producto in productos_data[1]:
        cargas = cv.CargasComercializador.get_by_date_and_producto(producto["producto"].nombre_producto, date_start, fecha_corte)
        descargas = cv.DescargasComercializador.get_by_date_and_producto(producto["producto"].nombre_producto, date_start, fecha_corte)
        complemento_distribuidor_recepcion = []
        complemento_distribuidor_entrega = []
        for carga in cargas:
            #complementos_date = DailyReportFuntionsInstance.GetComplementDailyReportAll(id_complemento_entrega,tipo,'C',entrega)
            #complemento = Comp_Distribucion.Comp_Distribucion_schema_json(id_complemento_recepcion,tipo,'C',carga)
            complemento = DailyReportFuntionsInstance.GetComplementDailyReportAll(id_complemento_entrega,tipo,'C',carga,'E_cv')
            #logging.debug("complemento C")
            #logging.debug(complemento)
            if complemento:
                complemento_distribuidor_entrega.append(complemento[0])
            else: 
                logging.debug(complemento)
                return jsonify(complemento)
        #id_complemento_entrega = producto["entregas"].Complemento
        print(f"entregas {producto['entregas']}")
        for descarga in descargas:
            #complemento = Comp_Distribucion.Comp_Distribucion_schema_json(id_complemento_entrega,tipo,'D',descarga)
            complemento = DailyReportFuntionsInstance.GetComplementDailyReportAll(id_complemento_entrega,tipo,'D',descarga,'r_cv')
            #logging.debug("complemento D")
            #logging.debug(complemento)
            if complemento:
                complemento_distribuidor_recepcion.append(complemento[0])
            else:
                logging.debug(complemento)
                return jsonify(complemento)

        producto_item = ET.SubElement(root, '{%s}PRODUCTO'% covol)

        #producto_item = ET.SubElement(productos_reporte, '{%s}Producto'% covol)
        clave =  producto['producto'].ClaveProducto

        ET.SubElement(producto_item, '{%s}ClaveProducto'% covol).text = clave 
        ET.SubElement(producto_item, '{%s}ClaveSubProducto'% covol).text = str(producto["producto"].ClaveSubProducto)
    
        if clave == "PR07":
                        Gasolina = ET.SubElement(producto_item, '{%s}Gasolina'% covol)
                        ET.SubElement(Gasolina, '{%s}ComposOctanajeGasolina'% covol).text = str(producto['producto'].ComposOctanajeGasolina)
                        ET.SubElement(Gasolina, '{%s}GasolinaConCombustibleNoFosil'% covol).text = producto['producto'].GasolinaConCombustibleNoFosil
                        if producto['producto'].GasolinaConCombustibleNoFosil == 'Si':
                            ET.SubElement(Gasolina, '{%s}ComposDeCombustibleNoFosilEnGasolina'% covol).text = str(producto['producto'].ComposDeCombustibleNoFosilEnGasolina)
        elif clave == "PR03":                       
                        Diesel = ET.SubElement(producto_item, '{%s}Diesel'% covol)
                        ET.SubElement(Diesel, '{%s}DieselConCombustibleNoFosil'% covol).text = producto['producto'].DieselConCombustibleNoFosil
                        if producto['producto'].DieselConCombustibleNoFosil == 'Si':
                            ET.SubElement(Diesel, '{%s}ComposDeCombustibleNoFosilEnDiesel'% covol).text = str(producto['producto'].ComposDeCombustibleNoFosilEnDiesel)
        else:
                        ET.SubElement(producto_item, '{%s}Otros'% covol).text =  producto['producto'].Otros

        ET.SubElement(producto_item, '{%s}MarcaComercial'% covol).text = str(producto["producto"].MarcaComercial)
        if producto['producto'].Marcaje:
            ET.SubElement(producto_item, '{%s}Marcaje'% covol).text = producto['producto'].Marcaje
            if producto['producto'].ConcentracionSustanciasMarcaje and producto['producto'].ConcentracionSustanciasMarcaje > 0:
                ET.SubElement(producto_item, '{%s}ConcentracionSustanciaMarcaje'% covol).text = str(producto['producto'].ConcentracionSustanciasMarcaje)

        reporte_volumen_mensual = ET.SubElement(producto_item, '{%s}REPORTEDEVOLUMENMENSUAL'% covol)
            
        # Control de existencias
        existencias = ET.SubElement(reporte_volumen_mensual, '{%s}CONTROLDEEXISTENCIAS'% covol)
        volumen_existencias_mes = ET.SubElement(existencias, '{%s}VolumenExistenciasMes'% covol)
        ET.SubElement(volumen_existencias_mes, '{%s}ValorNumerico'% covol).text = str(round(producto["existencias"].CONTROLDEEXISTENCIAS_VolumenExistenciasMes, 3))
        ET.SubElement(existencias, '{%s}FechaYHoraEstaMedicionMes'% covol).text = str(producto["existencias"].CONTROLDEEXISTENCIAS_FechaYHoraEstaMedicionMes)
            
        # Recepciones
        recepciones = ET.SubElement(reporte_volumen_mensual, '{%s}RECEPCIONES'% covol)
        ET.SubElement(recepciones, '{%s}TotalRecepcionesMes'% covol).text = str(producto["recepciones"].TotalRecepcionesMes)
        suma_volumen_recepcion_mes = ET.SubElement(recepciones, '{%s}SumaVolumenRecepcionMes'% covol)
        ET.SubElement(suma_volumen_recepcion_mes, '{%s}ValorNumerico'% covol).text = str(round(producto["recepciones"].SumaVolumenRecepcionesMes, 0))
        ET.SubElement(suma_volumen_recepcion_mes, '{%s}UM'% covol).text = str(producto["recepciones"].SumaVolumenRecepcionesMes_UM)
        if producto["producto"].ClaveProducto == 'PR09' and informacion_reporte.TipoCaracter in ['permisionarios','usuarios']:
            PoderCalorifico = ET.SubElement(recepciones, 'PoderCalorifico'% covol)
            ET.SubElement(PoderCalorifico, '{%s}ValorNumerico'% covol).text = str(producto["recepciones"].PoderCalorifico)
            ET.SubElement(PoderCalorifico, '{%s}UM'% covol).text = str(producto["recepciones"].PoderCalorifico_UM)
        ET.SubElement(recepciones, '{%s}TotalDocumentosMes'% covol).text = str(producto["recepciones"].TotalDocumentosMes)
        ET.SubElement(recepciones, '{%s}ImporteTotalRecepcionesMensual'% covol).text = str(producto["recepciones"].ImporteTotalRecepcionesMensual)
        #complemento_elem_recepciones = ET.SubElement(recepciones, 'Complemento'% covol)
        #complemento_elem_recepciones.append(nuevo_elemento_complemento)
        Complemento = ET.SubElement(recepciones, '{%s}Complemento'% covol)
        
        tipo = str('comercializador')
        id_complemento_recepcion = 2
        DailyReportFuntionsInstance = DailyReportFuntions(2)
        recepcion = producto["recepciones"]
        #complementos_date = DailyReportFuntionsInstance.GetComplementDailyReportAll(id_complemento_recepcion,tipo,'D',recepcion,'R_cv')

        
        if any(complemento_distribuidor_recepcion):
            for complementos in complemento_distribuidor_recepcion:
                Complemento_Comercializacion_Recepcion = ET.SubElement(Complemento, '{%s}Complemento_Comercializacion' %covol)
                """
                terminalAlmYTrans = complementos['TERMINALALMYTRANS_TERMINALALMYDIST']

                Terminalalmtrans = ET.SubElement(Complemento_Distribucion_Recepcion, '{%s}TERMINALALMYDIST' % dis )
                Almacenamiento = ET.SubElement(Terminalalmtrans, '{%s}Almacenamiento' % dis)
                ET.SubElement(Almacenamiento, '{%s}TerminalAlm' % dis).text =  str(terminalAlmYTrans['Almacenamiento'].TerminalAlm)
                ET.SubElement(Almacenamiento, '{%s}PermisoAlmacenamiento' % dis).text = str(terminalAlmYTrans['Almacenamiento'].PermisoAlmacenamiento)
                ET.SubElement(Almacenamiento, '{%s}TarifaDeAlmacenamiento' % dis).text = str(terminalAlmYTrans['Almacenamiento'].TarifaDeAlmacenamiento )
                ET.SubElement(Almacenamiento, '{%s}CargoPorCapacidadAlmac' % dis).text = str(terminalAlmYTrans['Almacenamiento'].CargoPorCapacidadAlmac) 
                ET.SubElement(Almacenamiento, '{%s}CargoPorUsoAlmac' % dis).text = str(terminalAlmYTrans['Almacenamiento'].CargoPorUsoAlmac )
                ET.SubElement(Almacenamiento, '{%s}CargoVolumetricoAlmac' % dis).text = str(terminalAlmYTrans['Almacenamiento'].CargoVolumetricoAlmac) 

                Transporte = ET.SubElement(Terminalalmtrans, '{%s}Transporte' % dis)
                ET.SubElement(Transporte, '{%s}PermisoTransporte' % dis).text = str(terminalAlmYTrans['Transporte'].PermisoTransporte)
                ET.SubElement(Transporte, '{%s}ClaveDeVehiculo' % dis).text =str(terminalAlmYTrans['Transporte'].ClaveDeVehiculo)
                ET.SubElement(Transporte, '{%s}TarifaDeTransporte'% dis).text = str(terminalAlmYTrans['Transporte'].TarifaDeTransporte)
                ET.SubElement(Transporte, '{%s}CargoPorCapacidadTrans'% dis).text = str(terminalAlmYTrans['Transporte'].CargoPorCapacidadTrans)
                ET.SubElement(Transporte, '{%s}CargoPorUsoTrans'% dis).text = str(terminalAlmYTrans['Transporte'].CargoPorUsoTrans)
                ET.SubElement(Transporte, '{%s}CargoVolumetricoTrans'% dis).text =str(terminalAlmYTrans['Transporte'].CargoVolumetricoTrans)
                ET.SubElement(Transporte, '{%s}TarifaDeSuministro'% dis).text = str(terminalAlmYTrans['Transporte'].CargoVolumetricoTrans)

                for trasvase in complementos['TRASVASE']:
                                Trasvase = ET.SubElement(Complemento_Distribucion_Recepcion, '{%s}TRASVASE'% dis)
                                ET.SubElement(Trasvase, '{%s}NombreTrasvase' % dis).text =  str(trasvase['TRASVASE'].NombreTrasvase)
                                ET.SubElement(Trasvase, '{%s}RfcTrasvase' % dis).text = str(trasvase['TRASVASE'].RfcTrasvase)
                                ET.SubElement(Trasvase, '{%s}PermisoTrasvase' % dis).text =str(trasvase['TRASVASE'].PermisoTrasvase)
                                ET.SubElement(Trasvase, '{%s}DescripcionTrasvase' % dis).text =  str(trasvase['TRASVASE'].DescripcionTrasvase)
                                ET.SubElement(Trasvase, '{%s}CfdiTrasvase' % dis).text = str(trasvase['TRASVASE'].CfdiTrasvase)

                dictamen =complementos['DICTAMEN']
                Dictamen = ET.SubElement(Complemento_Distribucion_Recepcion, '{%s}DICTAMEN'% dis)
                ET.SubElement(Dictamen, '{%s}RfcDictamen' % dis).text = str(dictamen['DICTAMEN'].RfcDictamen)
                ET.SubElement(Dictamen, '{%s}LoteDictamen' % dis).text = str(dictamen['DICTAMEN'].LoteDictamen)
                ET.SubElement(Dictamen, '{%s}NumeroFolioDictamen' % dis).text = str(dictamen['DICTAMEN'].NumeroFolioDictamen)
                ET.SubElement(Dictamen, '{%s}FechaEmisionDictamen' % dis).text =str(dictamen['DICTAMEN'].ResultadoDictamen)
                ET.SubElement(Dictamen, '{%s}ResultadoDictamen' % dis).text = str(dictamen['DICTAMEN'].ResultadoDictamen)
                """                            
                certificado = complementos['CERTIFICADO']

                Certificado = ET.SubElement(Complemento_Comercializacion_Recepcion, '{%s}CERTIFICADO' % co)
                ET.SubElement(Certificado, '{%s}RfcCertificado' % co).text = str(certificado['CERTIFICADO'].RfcCertificado)
                ET.SubElement(Certificado, '{%s}NumeroFolioCertificado' % co).text = str(certificado['CERTIFICADO'].NumeroFolioCertificado)
                ET.SubElement(Certificado, '{%s}FechaEmisionCertificado' % co).text = str(certificado['CERTIFICADO'].FechaEmisionCertificado)
                ET.SubElement(Certificado, '{%s}ResultadoCertificado' % co).text = str(certificado['CERTIFICADO'].ResultadoCertificado)   

                for nacional in complementos['NACIONAL']:
                    Nacional = ET.SubElement(Complemento_Comercializacion_Recepcion, '{%s}NACIONAL' % co)

                    ET.SubElement(Nacional, '{%s}RfcClienteOProveedor' % co).text =str(nacional['NACIONAL'].RFC)
                    ET.SubElement(Nacional, '{%s}NombreClienteOProveedor' % co).text = str(nacional['NACIONAL'].Nombre_comercial)
                    if nacional['NACIONAL'].PermisoClienteOProveedor is not None and nacional['NACIONAL'].PermisoClienteOProveedor != '':
                        ET.SubElement(Nacional, '{%s}PermisoClienteOProveedor' % co).text = str(nacional['NACIONAL'].PermisoClienteOProveedor)

                    for cfdi in nacional['cfdis']:
                            CFDIs = ET.SubElement(Nacional, '{%s}CFDIs' % co)
                            ET.SubElement(CFDIs, '{%s}CFDI' % co).text = str(cfdi.CFDI)
                            ET.SubElement(CFDIs, '{%s}TipoCFDI' % co).text = str(cfdi.TipoCFDI)
                            ET.SubElement(CFDIs, '{%s}PrecioVentaOCompraOContrap' % co).text = str(cfdi.PrecioVentaOCompraOContrap)
                            ET.SubElement(CFDIs, '{%s}FechaYHoraTransaccion' % co).text = str(cfdi.FechaYHoraTransaccion.astimezone().isoformat())
                            VolumenDocumentado = ET.SubElement(CFDIs, '{%s}VolumenDocumentado' % co)
                            ET.SubElement(VolumenDocumentado, '{%s}ValorNumerico' % co).text = str(cfdi.VolumenDocumentado)
                            ET.SubElement(VolumenDocumentado, '{%s}UM' % co).text = str(cfdi.VolumenDocumentado_UM)
                
                """
                for extranjero in complementos['EXTRANJERO']:
                    Extranjero = ET.SubElement(Complemento_Distribucion_Recepcion, '{%s}EXTRANJERO' % dis)

                    ET.SubElement(Extranjero, '{%s}PermisoImportacionOExportacion' % dis).text = str(extranjero['EXTRANJERO'].PermisoImportacionOExportacion)
                    for pedimentos in extranjero['pedimentos']:
                            Pedimentos = ET.SubElement(Extranjero, '{%s}PEDIMENTOS' % dis)
                            ET.SubElement(Pedimentos, '{%s}PuntoDeInternacionOExtraccion' % dis).text = str(pedimentos.PuntoDeInternacionOExtraccion)
                            ET.SubElement(Pedimentos, '{%s}PaisOrigenODestino' % dis).text = str(pedimentos.PaisOrigenODestino)
                            ET.SubElement(Pedimentos, '{%s}MedioDeTransEntraOSaleAduana' % dis).text = str(pedimentos.MedioDeTransEntraOSaleAducto)
                            ET.SubElement(Pedimentos, '{%s}PedimentoAduanal' % dis).text =str(pedimentos.PedimentosAduanal)
                            ET.SubElement(Pedimentos, '{%s}Incoterms'% dis).text = str(pedimentos.Incoterms)
                            ET.SubElement(Pedimentos, '{%s}PrecioDeImportacionOExportacion' % dis).text = str(pedimentos.PrecioDeImportacionOExportacion) 

                            Volumen_documentado = ET.SubElement(Pedimentos, '{%s}VolumenDocumentado'% dis)
                            ET.SubElement(Volumen_documentado, '{%s}ValorNumerico' % dis).text =str(pedimentos.VolumenDocumentado)
                            ET.SubElement(Volumen_documentado, '{%s}UM' % dis).text = str(pedimentos.VolumenDocumentado_UM)
                """                                        
                Aclarcion = ET.SubElement(Complemento_Comercializacion_Recepcion, '{%s}ACLARACION' % co)
                ET.SubElement(Aclarcion, '{%s}Aclaracion' % co).text = str(complementos['ACLARACION']['ACLARACION'])
        else:
            complemento_distribuidor_recepcion = DailyReportFuntionsInstance.GetComplementDailyReportAll(id_complemento_entrega,tipo,'D',None,None)
            for complementos in complemento_distribuidor_recepcion:
                Complemento_Comercializacion_Recepcion = ET.SubElement(Complemento, '{%s}Complemento_Comercializacion' %covol)
                certificado = complementos['CERTIFICADO']

                Certificado = ET.SubElement(Complemento_Comercializacion_Recepcion, '{%s}CERTIFICADO' % co)
                ET.SubElement(Certificado, '{%s}RfcCertificado' % co).text = str(certificado['CERTIFICADO'].RfcCertificado)
                ET.SubElement(Certificado, '{%s}NumeroFolioCertificado' % co).text = str(certificado['CERTIFICADO'].NumeroFolioCertificado)
                ET.SubElement(Certificado, '{%s}FechaEmisionCertificado' % co).text = str(certificado['CERTIFICADO'].FechaEmisionCertificado)
                ET.SubElement(Certificado, '{%s}ResultadoCertificado' % co).text = str(certificado['CERTIFICADO'].ResultadoCertificado)

        # Entregas
        entregas = ET.SubElement(reporte_volumen_mensual, '{%s}ENTREGAS'% covol)
        ET.SubElement(entregas, '{%s}TotalEntregasMes'% covol).text = str(producto["entregas"].TotalEntregasMes)
        suma_volumen_entregado_mes = ET.SubElement(entregas, '{%s}SumaVolumenEntregadoMes'% covol)
        ET.SubElement(suma_volumen_entregado_mes, '{%s}ValorNumerico'% covol).text = str(round(producto["entregas"].SumaVolumenEntregadoMes, 0))
        ET.SubElement(suma_volumen_entregado_mes, '{%s}UM'% covol).text = str(producto["entregas"].SumaVolumenEntregadoMes_UM)
        if producto["producto"].ClaveProducto == 'PR09' and informacion_reporte.TipoCaracter in ['permisionarios','usuarios']:
            PoderCalorifico = ET.SubElement(entregas, '{%s}PoderCalorifico'% covol)
            ET.SubElement(PoderCalorifico, '{%s}ValorNumerico'% covol).text = str(producto["recepciones"].PoderCalorifico)
            ET.SubElement(PoderCalorifico, '{%s}UM').text = str(producto["recepciones"].PoderCalorifico_UM)
        ET.SubElement(entregas, '{%s}TotalDocumentosMes'% covol).text = str(producto["entregas"].TotalDocumentosMes)
        ET.SubElement(entregas, '{%s}ImporteTotalEntregasMes'% covol).text = str(producto["entregas"].ImporteTotalRecepcionesMensual)
        #complemento_elem_entregas = ET.SubElement(entregas, '{%s}Complemento'% covol)
        #complemento_elem_entregas.append(nuevo_elemento_complemento)
        
        Complemento = ET.SubElement(entregas, '{%s}Complemento'% covol)
        
                
        tipo = str('comercializador')
        id_complemento_entrega = 2
        DailyReportFuntionsInstance = DailyReportFuntions(2)
        entrega = producto["entregas"]
        

        if complemento_distribuidor_entrega:
            for complementos in complemento_distribuidor_entrega:
                Complemento_Comercializacion_Entrega = ET.SubElement(Complemento, '{%s}Complemento_Comercializacion' %covol)
                """
                terminalAlmYTrans = complementos['TERMINALALMYTRANS_TERMINALALMYDIST']

                Terminalalmtrans = ET.SubElement(Complemento_Distribucion_Recepcion, '{%s}TERMINALALMYDIST' % dis )
                Almacenamiento = ET.SubElement(Terminalalmtrans, '{%s}Almacenamiento' % dis)
                ET.SubElement(Almacenamiento, '{%s}TerminalAlm' % dis).text =  str(terminalAlmYTrans['Almacenamiento'].TerminalAlm)
                ET.SubElement(Almacenamiento, '{%s}PermisoAlmacenamiento' % dis).text = str(terminalAlmYTrans['Almacenamiento'].PermisoAlmacenamiento)
                ET.SubElement(Almacenamiento, '{%s}TarifaDeAlmacenamiento' % dis).text = str(terminalAlmYTrans['Almacenamiento'].TarifaDeAlmacenamiento )
                ET.SubElement(Almacenamiento, '{%s}CargoPorCapacidadAlmac' % dis).text = str(terminalAlmYTrans['Almacenamiento'].CargoPorCapacidadAlmac) 
                ET.SubElement(Almacenamiento, '{%s}CargoPorUsoAlmac' % dis).text = str(terminalAlmYTrans['Almacenamiento'].CargoPorUsoAlmac )
                ET.SubElement(Almacenamiento, '{%s}CargoVolumetricoAlmac' % dis).text = str(terminalAlmYTrans['Almacenamiento'].CargoVolumetricoAlmac) 

                Transporte = ET.SubElement(Terminalalmtrans, '{%s}Transporte' % dis)
                ET.SubElement(Transporte, '{%s}PermisoTransporte' % dis).text = str(terminalAlmYTrans['Transporte'].PermisoTransporte)
                ET.SubElement(Transporte, '{%s}ClaveDeVehiculo' % dis).text =str(terminalAlmYTrans['Transporte'].ClaveDeVehiculo)
                ET.SubElement(Transporte, '{%s}TarifaDeTransporte'% dis).text = str(terminalAlmYTrans['Transporte'].TarifaDeTransporte)
                ET.SubElement(Transporte, '{%s}CargoPorCapacidadTrans'% dis).text = str(terminalAlmYTrans['Transporte'].CargoPorCapacidadTrans)
                ET.SubElement(Transporte, '{%s}CargoPorUsoTrans'% dis).text = str(terminalAlmYTrans['Transporte'].CargoPorUsoTrans)
                ET.SubElement(Transporte, '{%s}CargoVolumetricoTrans'% dis).text =str(terminalAlmYTrans['Transporte'].CargoVolumetricoTrans)
                ET.SubElement(Transporte, '{%s}TarifaDeSuministro'% dis).text = str(terminalAlmYTrans['Transporte'].CargoVolumetricoTrans)

                for trasvase in complementos['TRASVASE']:

                        Trasvase = ET.SubElement(Complemento_Distribucion_Recepcion, '{%s}TRASVASE'% dis)
                        ET.SubElement(Trasvase, '{%s}NombreTrasvase' % dis).text =  str(trasvase['TRASVASE'].NombreTrasvase)
                        ET.SubElement(Trasvase, '{%s}RfcTrasvase' % dis).text = str(trasvase['TRASVASE'].RfcTrasvase)
                        ET.SubElement(Trasvase, '{%s}PermisoTrasvase' % dis).text =str(trasvase['TRASVASE'].PermisoTrasvase)
                        ET.SubElement(Trasvase, '{%s}DescripcionTrasvase' % dis).text =  str(trasvase['TRASVASE'].DescripcionTrasvase)
                        ET.SubElement(Trasvase, '{%s}CfdiTrasvase' % dis).text = str(trasvase['TRASVASE'].CfdiTrasvase)

                dictamen =complementos['DICTAMEN']
                Dictamen = ET.SubElement(Complemento_Distribucion_Recepcion, '{%s}DICTAMEN'% dis)
                ET.SubElement(Dictamen, '{%s}RfcDictamen' % dis).text = str(dictamen['DICTAMEN'].RfcDictamen)
                ET.SubElement(Dictamen, '{%s}LoteDictamen' % dis).text = str(dictamen['DICTAMEN'].LoteDictamen)
                ET.SubElement(Dictamen, '{%s}NumeroFolioDictamen' % dis).text = str(dictamen['DICTAMEN'].NumeroFolioDictamen)
                ET.SubElement(Dictamen, '{%s}FechaEmisionDictamen' % dis).text =str(dictamen['DICTAMEN'].ResultadoDictamen)
                ET.SubElement(Dictamen, '{%s}ResultadoDictamen' % dis).text = str(dictamen['DICTAMEN'].ResultadoDictamen)
                """                            
                certificado = complementos['CERTIFICADO']

                Certificado = ET.SubElement(Complemento_Comercializacion_Entrega, '{%s}CERTIFICADO' % co)
                ET.SubElement(Certificado, '{%s}RfcCertificado' % co).text = str(certificado['CERTIFICADO'].RfcCertificado)
                ET.SubElement(Certificado, '{%s}NumeroFolioCertificado' % co).text = str(certificado['CERTIFICADO'].NumeroFolioCertificado)
                ET.SubElement(Certificado, '{%s}FechaEmisionCertificado' % co).text = str(certificado['CERTIFICADO'].FechaEmisionCertificado)
                ET.SubElement(Certificado, '{%s}ResultadoCertificado' % co).text = str(certificado['CERTIFICADO'].ResultadoCertificado)   

                for nacional in complementos['NACIONAL']:
                    Nacional = ET.SubElement(Complemento_Comercializacion_Entrega, '{%s}NACIONAL' % co)

                    ET.SubElement(Nacional, '{%s}RfcClienteOProveedor' % co).text =str(nacional['NACIONAL'].RFC)
                    ET.SubElement(Nacional, '{%s}NombreClienteOProveedor' % co).text = str(nacional['NACIONAL'].Nombre_comercial)
                    if nacional['NACIONAL'].PermisoClienteOProveedor is not None and nacional['NACIONAL'].PermisoClienteOProveedor != '':
                        ET.SubElement(Nacional, '{%s}PermisoClienteOProveedor' % co).text = str(nacional['NACIONAL'].PermisoClienteOProveedor)

                    for cfdi in nacional['cfdis']:
                            CFDIs = ET.SubElement(Nacional, '{%s}CFDIs' % co)
                            ET.SubElement(CFDIs, '{%s}CFDI' % co).text = str(cfdi.CFDI)
                            ET.SubElement(CFDIs, '{%s}TipoCFDI' % co).text = str(cfdi.TipoCFDI)
                            ET.SubElement(CFDIs, '{%s}PrecioVentaOCompraOContrap' % co).text = str(cfdi.PrecioVentaOCompraOContrap)
                            ET.SubElement(CFDIs, '{%s}FechaYHoraTransaccion' % co).text = str(cfdi.FechaYHoraTransaccion.astimezone().isoformat())
                            VolumenDocumentado = ET.SubElement(CFDIs, '{%s}VolumenDocumentado' % co)
                            ET.SubElement(VolumenDocumentado, '{%s}ValorNumerico' % co).text = str(cfdi.VolumenDocumentado)
                            ET.SubElement(VolumenDocumentado, '{%s}UM' % co).text = str(cfdi.VolumenDocumentado_UM)
                """
                for extranjero in complementos['EXTRANJERO']:
                    Extranjero = ET.SubElement(Complemento_Distribucion_Recepcion, '{%s}EXTRANJERO' % dis)

                    ET.SubElement(Extranjero, '{%s}PermisoImportacionOExportacion' % dis).text = str(extranjero['EXTRANJERO'].PermisoImportacionOExportacion)
                    for pedimentos in extranjero['pedimentos']:
                                    Pedimentos = ET.SubElement(Extranjero, '{%s}PEDIMENTOS' % dis)
                                    ET.SubElement(Pedimentos, '{%s}PuntoDeInternacionOExtraccion' % dis).text = str(pedimentos.PuntoDeInternacionOExtraccion)
                                    ET.SubElement(Pedimentos, '{%s}PaisOrigenODestino' % dis).text = str(pedimentos.PaisOrigenODestino)
                                    ET.SubElement(Pedimentos, '{%s}MedioDeTransEntraOSaleAduana' % dis).text = str(pedimentos.MedioDeTransEntraOSaleAducto)
                                    ET.SubElement(Pedimentos, '{%s}PedimentoAduanal' % dis).text =str(pedimentos.PedimentosAduanal)
                                    ET.SubElement(Pedimentos, '{%s}Incoterms'% dis).text = str(pedimentos.Incoterms)
                                    ET.SubElement(Pedimentos, '{%s}PrecioDeImportacionOExportacion' % dis).text = str(pedimentos.PrecioDeImportacionOExportacion) 

                                    Volumen_documentado = ET.SubElement(Pedimentos, '{%s}VolumenDocumentado'% dis)
                                    ET.SubElement(Volumen_documentado, '{%s}ValorNumerico' % dis).text =str(pedimentos.VolumenDocumentado)
                                    ET.SubElement(Volumen_documentado, '{%s}UM' % dis).text = str(pedimentos.VolumenDocumentado_UM)
                """                           
                Aclarcion = ET.SubElement(Complemento_Comercializacion_Entrega, '{%s}ACLARACION' % co)
                ET.SubElement(Aclarcion, '{%s}Aclaracion' % co).text = str(complementos['ACLARACION']['ACLARACION'])
        else:
            complemento_distribuidor_entrega = DailyReportFuntionsInstance.GetComplementDailyReportAll(id_complemento_entrega,tipo,'C',None,None)
            for complementos in complemento_distribuidor_entrega:
                Complemento_Comercializacion_Entrega = ET.SubElement(Complemento, '{%s}Complemento_Comercializacion' %covol)
                certificado = complementos['CERTIFICADO']

                Certificado = ET.SubElement(Complemento_Comercializacion_Entrega, '{%s}CERTIFICADO' % co)
                ET.SubElement(Certificado, '{%s}RfcCertificado' % co).text = str(certificado['CERTIFICADO'].RfcCertificado)
                ET.SubElement(Certificado, '{%s}NumeroFolioCertificado' % co).text = str(certificado['CERTIFICADO'].NumeroFolioCertificado)
                ET.SubElement(Certificado, '{%s}FechaEmisionCertificado' % co).text = str(certificado['CERTIFICADO'].FechaEmisionCertificado)
                ET.SubElement(Certificado, '{%s}ResultadoCertificado' % co).text = str(certificado['CERTIFICADO'].ResultadoCertificado) 
    

    for bitacora in bitacora_XML:
        BITACORA = ET.SubElement(root, '{%s}BITACORA'% covol)
        BITACORAMENSUAL = ET.SubElement(BITACORA, '{%s}BITACORAMENSUAL'% covol)
        
        fecha_str = bitacora['fecha']
        fecha_dt = datetime.fromisoformat(fecha_str)  # Convertir la cadena a datetime

        ET.SubElement(BITACORAMENSUAL, '{%s}NumeroRegistro'% covol).text =  str( bitacora['numero_registro'])
        ET.SubElement(BITACORAMENSUAL, '{%s}FechaYHoraEvento'% covol).text =fecha_dt.astimezone().isoformat()
        usuario_responsable = bitacora.get('UsuarioResponsable', None)
        if usuario_responsable is not None and bitacora.get('is_event'):
                ET.SubElement(BITACORAMENSUAL, '{%s}UsuarioResponsable' % covol).text = str(bitacora.get('UsuarioResponsable', '')) if bitacora.get('is_event') else ''
                    
        ET.SubElement(BITACORAMENSUAL, '{%s}TipoEvento'% covol).text = str(bitacora['tipo'])
        ET.SubElement(BITACORAMENSUAL, '{%s}DescripcionEvento'% covol).text =  str(bitacora['mensaje'])
        tipos = ['7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21']
        if str(bitacora['tipo']) in tipos:
            ET.SubElement(BITACORAMENSUAL, '{%s}IdentificacionComponenteAlarma'% covol).text = str( bitacora['identificacion'] )
    # Convertir el árbol de elementos a una cadena XML
        xml_str = ET.tostring(root, encoding='utf-8').decode('utf-8')

    # Validar el XML contra el esquema XSD
    try:
        xml_doc = ET.fromstring(xml_str)
        schema.validate(xml_doc)
    except xmlschema.XMLSchemaValidationError as e:
        error_trace = traceback.format_exc()
        # Logging detallado
        logging.debug(f"ValidationError: {str(e)}")
        logging.debug(f"Traceback: {error_trace}")
        return f"El XML no es válido: {e}", 400
        return f"El XML no es válido: {e}", 400

    
    # Crear el archivo XML de respuesta
    file_name = f"Reporte_mensual_{datetime.now().strftime('%Y%m%d%H%M%S')}.xml"
    response = Response(
        xml_str,
        mimetype='application/xml',
        headers={
            'Content-Disposition': f'attachment; filename={file_name}',
            'Content-Type': 'application/xml'
        }
    )
    return response


def REPORTE_MENSUAL_JSON(productos_data,fecha_corte):

    componente = 'comercializador/REPORTE_MENSUAL_JSON'
    Descripcion = None
    Tipo_Evento = None

    informacion_reporte = cv.ControlesVolumetricos.select_by_id(2)

    date_start = fecha_corte.replace(day=1)

    #bitacora_JSON = cv.EventosAlarmasDistribuidor.select_events_and_alarms_between_dates(date_start,fecha_corte)
    bitacora_JSON = cv.EventosAlarmasDEventosComercializadoristribuidor.select_events_between_dates(date_start,fecha_corte)


    tipo = str('comercializador')
    id_complemento_recepcion = 2
    id_complemento_entrega = 2
    for producto in productos_data:
        #id_complemento_recepcion = producto["recepciones"].Complemento
        print(f"recepciones {producto['recepciones']}")
        id_complemento_recepcion = 2
        id_complemento_entrega = 2

    caracter  = {
        'Caracter':informacion_reporte.TipoCaracter,#Requerida
        'ModalidadPermiso':informacion_reporte.ModalidadPermiso if informacion_reporte.TipoCaracter == 'permisionario' else '',#Si seleciono permisionario en Caracter
        'NumPermiso': informacion_reporte.NumPermiso if informacion_reporte.TipoCaracter in ['contratista','asignatario'] else '',#Si seleciono contratista o asignatario en Caracter
        'NumContratoOAsignacion':informacion_reporte.NumContratoOAsignacion if informacion_reporte.TipoCaracter in ['contratista','asignatario'] else '',#Si seleciono contratista o asignatario en Caracter
        'InstalacionAlmacenGasNatural': informacion_reporte.InstalacionAlmacenGasNatural if informacion_reporte.TipoCaracter == 'usuario' else '' #Si seleciono usuario en Caracter
    }

    gaslp = {
        'CamposDePropanoEnGasLP':'',
        'ComposDeButanoGasLP':''
    }

    petroleo = {
        'DensidadDePetroleo':'',
        'ComposDeAzufreEnPetroleo':''
    }

    gasnaturalocondensados = {
        'ComposGasNaturalOCondensados':'', #Si seleciono contratista o asignatario en Caracter y si ClaveProducto PR09 o PR10
        'FraccionMolar':'',
        'PoderCalorifico':''
    }

    otros = {}
    producto_r_podercalorifico = { 
        'ValorNumerico':'',
        'UnidadDeMedida':''
    }
    
    producto_e_podercalorifico = { 
        'ValorNumerico':'',
        'UnidadDeMedida':''
    }

    productos_reporte = []
    
    for producto in productos_data:
        
        cargas = cv.CargasComercializador.get_by_date_and_producto(producto["producto"].nombre_producto, date_start, fecha_corte)
        descargas = cv.DescargasComercializador.get_by_date_and_producto(producto["producto"].nombre_producto, date_start, fecha_corte)
        complemento_distribuidor_recepcion = []
        complemento_distribuidor_entrega = []
        for carga in cargas:
            complemento = Comp_Comercializador.Comp_Comercializacion_schema_json(id_complemento_recepcion,tipo,'C',carga,'r_cv')
            #logging.debug("complemento C")
            logging.debug(complemento)
            if complemento:
                complemento_distribuidor_entrega.append(complemento)
            else: return jsonify(complemento)
        #id_complemento_entrega = producto["entregas"].Complemento
        print(f"entregas {producto['entregas']}")
        for descarga in descargas:
            complemento = Comp_Comercializador.Comp_Comercializacion_schema_json(id_complemento_entrega,tipo,'C',descarga,'E_cv')
            #logging.debug("complemento D")
            #logging.debug(complemento)
            if complemento:
                complemento_distribuidor_recepcion.append(complemento)
            else: return jsonify(complemento)

        producto_item = {
                'ClaveProducto':producto["producto"].ClaveProducto,
                'ClaveSubProducto':producto["producto"].ClaveSubProducto,
                'ReporteDeVolumenMensual':{
                    'ControlDeExistencias':{
                        'VolumenExistenciasMes':round(producto["existencias"].CONTROLDEEXISTENCIAS_VolumenExistenciasMes,5),
                        'FechaYHoraEstaMedicionMes':producto["existencias"].CONTROLDEEXISTENCIAS_FechaYHoraEstaMedicionMes
                    },
                    'Recepciones':{
                        'TotalRecepcionesMes':producto["recepciones"].TotalRecepcionesMes,
                        'SumaVolumenRecepcionMes':{
                            'ValorNumerico':round(producto["recepciones"].SumaVolumenRecepcionesMes,5),
                            'UnidadDeMedida':producto["recepciones"].SumaVolumenRecepcionesMes_UM
                        },
                        'PoderCalorifico':producto_r_podercalorifico if producto["producto"].ClaveProducto == 'PR09' and informacion_reporte.TipoCaracter in ['permisionarios','usuarios'] else '',# Si permisionarios y usuarios en caracter que hayan seleccionado el producto PR09
                        'TotalDocumentosMes':producto["recepciones"].TotalDocumentosMes,
                        'ImporteTotalRecepcionesMensual':round(producto["recepciones"].ImporteTotalRecepcionesMensual,3),
                        'Complemento':complemento_distribuidor_recepcion if complemento_distribuidor_recepcion !=[] else [Comp_Distribucion.Comp_Distribucion_schema_json(id_complemento_recepcion,tipo,'D',None)]
                    },
                    'Entregas':{
                            'TotalEntregasMes':producto["entregas"].TotalEntregasMes,
                            'SumaVolumenEntregadoMes':{
                                'ValorNumerico':round(producto["entregas"].SumaVolumenEntregadoMes,5),
                                'UnidadDeMedida':producto["entregas"].SumaVolumenEntregadoMes_UM                            
                            },
                            'PoderCalorifico':producto_e_podercalorifico if producto["producto"].ClaveProducto == 'PR09' and informacion_reporte.TipoCaracter in ['permisionarios','usuarios'] else '',
                            'TotalDocumentosMes':producto["entregas"].TotalDocumentosMes,
                            'ImporteTotalEntregasMes':round(producto["entregas"].ImporteTotalRecepcionesMensual,3),
                            'Complemento':complemento_distribuidor_entrega if complemento_distribuidor_entrega !=[] else [Comp_Distribucion.Comp_Distribucion_schema_json(id_complemento_recepcion,tipo,'C',None)]
                        }
                },
                'DieselConCombustibleNoFosil':producto["producto"].DieselConCombustibleNoFosil if producto["producto"].ClaveProducto == 'PR03' else '',
                'ComposDeCombustibleNoFosilEnDiesel':producto["producto"].ComposDeCombustibleNoFosilEnDiesel if producto["producto"].ClaveProducto == 'PR03' and producto["producto"].GasolinaConCombustibleNoFosil == 'Sí' else '',#Si DieselConCombustibleNofosil es si
                'ComposOctanajeGasolina':producto["producto"].ComposOctanajeGasolina if producto["producto"].ClaveProducto == 'PR07' else '',
                'GasolinaConCombustibleNoFosil':producto["producto"].GasolinaConCombustibleNoFosil if producto["producto"].ClaveProducto == 'PR07' else '',
                'ComposDeCombustibleNoFosilEnGasolina':producto["producto"].ComposDeCombustibleNoFosilEnGasolina if producto["producto"].ClaveProducto == 'PR07' and producto["producto"].TurbosinaConCombustibleNoFosil == 'Sí' else '',#Si GasolinaConCombustibleNoFosil es si
                'TurbosinaConCombustibleNoFosil':producto["producto"].TurbosinaConCombustibleNoFosil if producto["producto"].ClaveProducto == 'PR11' else '',
                'ComposDeCombustibleNoFosilEnTurbosina':producto["producto"].ComposDeCombustibleNoFosilEnTurbosina if producto["producto"].ClaveProducto == 'PR11' and producto["producto"].TurbosinaConCombustibleNoFosil == 'Sí' else '',#Si TurbosinaConCombustibleNoFosil es si
                #'Gasolina':gasolina if producto["producto"].ClaveProducto == 'PR07' else '',#Si ClaveProducto es PR07
                #'Diesel':diesel if producto["producto"].ClaveProducto == 'PR03' else '',#Si ClaveProducto es PR03
                #'Turbosina':turbosina if producto["producto"].ClaveProducto == 'PR11' else '', #Si ClaveProducto PR11
                #'GasLP':gaslp if producto["producto"].ClaveProducto == 'PR12' else '',#Si ClaveProducto PR12
                #'Petroleo': petroleo if producto["producto"].ClaveProducto == 'PR08' and informacion_reporte.TipoCaracter in ['contratista','asignatario']  else '', #Si ClaveProducto PR08
                #'GasNaturalOCondensados':gasnaturalocondensados if producto["producto"].ClaveProducto in ['PR09','PR10'] and informacion_reporte.TipoCaracter in ['contratista','asignatario']  else '',
                #'Otros':otros if producto["producto"].ClaveProducto in ['PR15','PR20'] and informacion_reporte.TipoCaracter == 'SP20' else '',#Si ClaveProducto PR15, PR20 y ClaveSubProducto SP20
                'MarcaComercial':producto["producto"].MarcaComercial, #Si el producto o subproducto cuente con alguna marca comercial
                'Marcaje':producto["producto"].Marcaje, #Si el producto o subproducto cuente con alguna sustancia quimica empleada como marcador
                'ConcentracionSustanciaMarcaje':producto["producto"].ConcentracionSustanciasMarcaje#Si Marcaje existe
            }
        producto_item = eliminar_claves_vacias(producto_item)
        productos_reporte.append(producto_item)

        bitacora_reporte= [] 
        if bitacora_JSON:
            #print(f"aqui tadeos2s{bitacora_JSON}")
            for bitacora in bitacora_JSON: 
                #print(f"aqui tadeos3s{bitacora}")
                tipos = ['7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21']

                bitacora_item={
                                'NumeroRegistro':bitacora['numero_registro']  ,
                                'FechaYHoraEvento':bitacora['fecha'],
                                'UsuarioResponsable':bitacora['UsuarioResponsable'] if bitacora['is_event'] else '',
                                'TipoEvento':bitacora['tipo'],
                                'DescripcionEvento':bitacora['mensaje'],
                                **({'IdentificacionComponenteAlarma': bitacora['identificacion']} if str(bitacora['tipo']) in tipos else {})
                            }
                bitacora_item = eliminar_claves_vacias(bitacora_item)
                bitacora_reporte.append(bitacora_item)
        
    print(informacion_reporte.NumeroDuctosTransporteDistribucion)
    ControlesVolumetricos = {
        'Version':'1.0',
        'RfcContribuyente':informacion_reporte.RfcContribuyente,
        'RfcRepresentanteLegal': informacion_reporte.RfcRepresentanteLegal,
        'RfcProveedor': informacion_reporte.RfcProveedor,
        'RfcProveedores':[informacion_reporte.RfcProveedores],
        'Caracter':informacion_reporte.TipoCaracter,
        'ModalidadPermiso':informacion_reporte.ModalidadPermiso if informacion_reporte.TipoCaracter == 'permisionario' else '',#Si seleciono permisionario en Caracter
        'NumPermiso': informacion_reporte.NumPermiso if informacion_reporte.TipoCaracter in ['contratista','asignatario'] else '',#Si seleciono contratista o asignatario en Caracter
        'NumContratoOAsignacion':informacion_reporte.NumContratoOAsignacion if informacion_reporte.TipoCaracter in ['contratista','asignatario'] else '',#Si seleciono contratista o asignatario en Caracter
        'InstalacionAlmacenGasNatural': informacion_reporte.InstalacionAlmacenGasNatural if informacion_reporte.TipoCaracter == 'usuario' else '', #Si seleciono usuario en Caracter
        'ClaveInstalacion': informacion_reporte.ClaveInstalacion,
        'DescripcionInstalacion': informacion_reporte.DescripcionInstalacion,
        'Geolocalizacion': [{
            'GeolocalizacionLatitud': informacion_reporte.GeolocalizacionLatitud,
            'GeolocalizacionLongitud':informacion_reporte.GeolocalizacionLongitud
        }],
        'NumeroPozos': informacion_reporte.NumeroPozos,
        'NumeroTanques':informacion_reporte.NumeroTanques,
        'NumeroDuctosEntradaSalida': informacion_reporte.NumeroDuctosEntradaSalida,
        'NumeroDuctosTransporteDistribucion': informacion_reporte.NumeroDuctosTransporteDistribucion,
        'NumeroDispensarios':informacion_reporte.NumeroDispensarios,
        'FechaYHoraReporteMes':fecha_corte.astimezone().isoformat() ,
        'Producto': productos_reporte,
        'BitacoraMensual': bitacora_reporte        
    }
    
    ControlesVolumetricos = eliminar_claves_vacias(ControlesVolumetricos)
    logging.debug(ControlesVolumetricos)
    try:
        validate(instance=ControlesVolumetricos, schema=estructura_json_mensual)
        json_str = json.dumps(ControlesVolumetricos)
        file_name = f"Reporte_mensual_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        response = Response(
            json_str,
            mimetype='application/json',
            headers={
                'Content-Disposition': f'attachment; filename={file_name}',
                'Content-Type': 'application/json'  # Asegúrate de que el Content-Type sea JSON
            }
        )
        return response
    except ValidationError as e:
        error_trace = traceback.format_exc()
        # Logging detallado
        logging.debug(f"ValidationError: {str(e)}")
        logging.debug(f"Traceback: {error_trace}")
        return jsonify({"error": str(e)}), 400

def REPORTE_MENSUAL_XML(productos_data, fecha_corte):

    componente = 'comercializador/REPORTE_MENSUAL_XML'
    Descripcion = None
    Tipo_Evento = None
    tipo = str('comercializador')
    id_complemento_recepcion = 2
    id_complemento_entrega = 2
    DailyReportFuntionsInstance = DailyReportFuntions(2)


    # Obtener información del reporte
    informacion_reporte = cv.ControlesVolumetricos.select_by_id(2)
    
    date_start = fecha_corte.replace(day=1)
    bitacora_XML = cv.EventosComercializador.select_events_between_dates(date_start,fecha_corte)

    schema_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..","static/schemes/comercializador/Mensual.xsd"))

    schema = xmlschema.XMLSchema11(schema_file)
    
    xsi = 'http://www.w3.org/2001/XMLSchema-instance'
    ET.register_namespace('xsi', xsi)

    xsd = 'http://www.w3.org/2001/XMLSchema'
    ET.register_namespace('xsd',xsd)
                
    tr = 'Complemento_Transporte'
    ET.register_namespace('tr',tr)

    alm= 'Complemento_Almacenamiento'
    ET.register_namespace('alm',alm)

    CDLRGN = 'Complemento_CDLRGN'
    ET.register_namespace('CDLRGN',CDLRGN)

    co = 'Complemento_Comercializacion'
    ET.register_namespace('co',co)

    dis = 'Complemento_Distribucion'
    ET.register_namespace('dis',dis)

    exp = 'Complemento_Expendio'
    ET.register_namespace('exp',exp)

    ext = 'Complemento_Extraccion'
    ET.register_namespace('ext',ext)

    ref = 'Complemento_Refinacion'
    ET.register_namespace('ref',ref)

    covol = 'https://repositorio.cloudb.sat.gob.mx/Covol/xml/Mensuales'
    ET.register_namespace('Covol', covol)

    # Crear el elemento raíz
    root = ET.Element('{%s}ControlesVolumetricos' % covol)

    # Agregar el elemento 'Version'
    ET.SubElement(root, '{%s}Version'% covol).text = "1.0"
        
    # Agregar nodos de información principal
    ET.SubElement(root, '{%s}RfcContribuyente'% covol).text = str(informacion_reporte.RfcContribuyente)
    ET.SubElement(root, '{%s}RfcRepresentanteLegal'% covol).text = str(informacion_reporte.RfcRepresentanteLegal)
    ET.SubElement(root, '{%s}RfcProveedor'% covol).text = str(informacion_reporte.RfcProveedor)
    ET.SubElement(root, '{%s}RfcProveedores'% covol).text = str(informacion_reporte.RfcProveedores)

    # Crear el elemento 'Caracter' y sus subelementos
    caracter = ET.SubElement(root, '{%s}Caracter'% covol)
    ET.SubElement(caracter, '{%s}TipoCaracter'% covol).text = str(informacion_reporte.TipoCaracter)
    if informacion_reporte.TipoCaracter == 'permisionario':
        ET.SubElement(caracter, '{%s}ModalidadPermiso'% covol).text = str(informacion_reporte.ModalidadPermiso)
        ET.SubElement(caracter, '{%s}NumPermiso'% covol).text = str(informacion_reporte.NumPermiso)
    if informacion_reporte.TipoCaracter in ['contratista', 'asignatario']:
        ET.SubElement(caracter, '{%s}NumContratoOAsignacion'% covol).text = str(informacion_reporte.NumContratoOAsignacion)
    if informacion_reporte.TipoCaracter == 'usuario':
        ET.SubElement(caracter, '{%s}InstalacionAlmacenGasNatural'% covol).text = str(informacion_reporte.InstalacionAlmacenGasNatural)
        
    ET.SubElement(root, '{%s}ClaveInstalacion'% covol).text = str(informacion_reporte.ClaveInstalacion)
    ET.SubElement(root, '{%s}DescripcionInstalacion'% covol).text = str(informacion_reporte.DescripcionInstalacion)
    # Geolocalización
    geolocalizacion = ET.SubElement(root, '{%s}Geolocalizacion'% covol)
    ET.SubElement(geolocalizacion, '{%s}GeolocalizacionLatitud'% covol).text = str(informacion_reporte.GeolocalizacionLatitud)
    ET.SubElement(geolocalizacion, '{%s}GeolocalizacionLongitud'% covol).text = str(informacion_reporte.GeolocalizacionLongitud)

    ET.SubElement(root, '{%s}NumeroPozos'% covol).text = str(informacion_reporte.NumeroPozos)
    ET.SubElement(root, '{%s}NumeroTanques'% covol).text = str(informacion_reporte.NumeroTanques)
    ET.SubElement(root, '{%s}NumeroDuctosEntradaSalida'% covol).text = str(informacion_reporte.NumeroDuctosEntradaSalida)
    ET.SubElement(root, '{%s}NumeroDuctosTransporteDistribucion'% covol).text = str(informacion_reporte.NumeroDuctosTransporteDistribucion)
    ET.SubElement(root, '{%s}NumeroDispensarios'% covol).text = str(informacion_reporte.NumeroDispensarios)
    
    # Obtener la fecha y hora actual con la zona horaria
    fecha_hora_corte = fecha_corte.astimezone().strftime('%Y-%m-%dT%H:%M:%S%z')
    # Formatear la zona horaria para incluir dos puntos
    fecha_hora_corte = f"{fecha_hora_corte[:-2]}:{fecha_hora_corte[-2:]}"
    # Agregar el elemento al XML
    
    ET.SubElement(root, '{%s}FechaYHoraReporteMes'% covol).text =fecha_hora_corte #str (datetime.now().astimezone().isoformat() )
    # Productos
    for producto in productos_data:
        cargas = cv.CargasComercializador.get_by_date_and_producto(producto["producto"].nombre_producto, date_start, fecha_corte)
        descargas = cv.DescargasComercializador.get_by_date_and_producto(producto["producto"].nombre_producto, date_start, fecha_corte)
        complemento_distribuidor_recepcion = []
        complemento_distribuidor_entrega = []
        for carga in cargas:
            #complementos_date = DailyReportFuntionsInstance.GetComplementDailyReportAll(id_complemento_entrega,tipo,'C',entrega)
            #complemento = Comp_Distribucion.Comp_Distribucion_schema_json(id_complemento_recepcion,tipo,'C',carga)
            complemento = DailyReportFuntionsInstance.GetComplementDailyReportAll(id_complemento_entrega,tipo,'C',carga,'E_cv')
            #logging.debug("complemento C")
            #logging.debug(complemento)
            if complemento:
                complemento_distribuidor_entrega.append(complemento[0])
            else: 
                logging.debug(complemento)
                return jsonify(complemento)
        #id_complemento_entrega = producto["entregas"].Complemento
        print(f"entregas {producto['entregas']}")
        for descarga in descargas:
            #complemento = Comp_Distribucion.Comp_Distribucion_schema_json(id_complemento_entrega,tipo,'D',descarga)
            complemento = DailyReportFuntionsInstance.GetComplementDailyReportAll(id_complemento_entrega,tipo,'D',descarga,'R_cv')
            #logging.debug("complemento D")
            #logging.debug(complemento)
            if complemento:
                complemento_distribuidor_recepcion.append(complemento[0])
            else:
                logging.debug(complemento)
                return jsonify(complemento)

        producto_item = ET.SubElement(root, '{%s}PRODUCTO'% covol)

        #producto_item = ET.SubElement(productos_reporte, '{%s}Producto'% covol)
        clave =  producto['producto'].ClaveProducto

        ET.SubElement(producto_item, '{%s}ClaveProducto'% covol).text = clave 
        ET.SubElement(producto_item, '{%s}ClaveSubProducto'% covol).text = str(producto["producto"].ClaveSubProducto)
    
        if clave == "PR07":
                        Gasolina = ET.SubElement(producto_item, '{%s}Gasolina'% covol)
                        ET.SubElement(Gasolina, '{%s}ComposOctanajeGasolina'% covol).text = str(producto['producto'].ComposOctanajeGasolina)
                        ET.SubElement(Gasolina, '{%s}GasolinaConCombustibleNoFosil'% covol).text = producto['producto'].GasolinaConCombustibleNoFosil
                        if producto['producto'].GasolinaConCombustibleNoFosil == 'Si':
                            ET.SubElement(Gasolina, '{%s}ComposDeCombustibleNoFosilEnGasolina'% covol).text = str(producto['producto'].ComposDeCombustibleNoFosilEnGasolina)
        elif clave == "PR03":                       
                        Diesel = ET.SubElement(producto_item, '{%s}Diesel'% covol)
                        ET.SubElement(Diesel, '{%s}DieselConCombustibleNoFosil'% covol).text = producto['producto'].DieselConCombustibleNoFosil
                        if producto['producto'].DieselConCombustibleNoFosil == 'Si':
                            ET.SubElement(Diesel, '{%s}ComposDeCombustibleNoFosilEnDiesel'% covol).text = str(producto['producto'].ComposDeCombustibleNoFosilEnDiesel)
        else:
                        ET.SubElement(producto_item, '{%s}Otros'% covol).text =  producto['producto'].Otros

        ET.SubElement(producto_item, '{%s}MarcaComercial'% covol).text = str(producto["producto"].MarcaComercial)
        if producto['producto'].Marcaje:
            ET.SubElement(producto_item, '{%s}Marcaje'% covol).text = producto['producto'].Marcaje
            if producto['producto'].ConcentracionSustanciasMarcaje and producto['producto'].ConcentracionSustanciasMarcaje > 0:
                ET.SubElement(producto_item, '{%s}ConcentracionSustanciaMarcaje'% covol).text = str(producto['producto'].ConcentracionSustanciasMarcaje)

        reporte_volumen_mensual = ET.SubElement(producto_item, '{%s}REPORTEDEVOLUMENMENSUAL'% covol)
            
        # Control de existencias
        existencias = ET.SubElement(reporte_volumen_mensual, '{%s}CONTROLDEEXISTENCIAS'% covol)
        volumen_existencias_mes = ET.SubElement(existencias, '{%s}VolumenExistenciasMes'% covol)
        ET.SubElement(volumen_existencias_mes, '{%s}ValorNumerico'% covol).text = str(round(producto["existencias"].CONTROLDEEXISTENCIAS_VolumenExistenciasMes, 3))
        ET.SubElement(existencias, '{%s}FechaYHoraEstaMedicionMes'% covol).text = str(producto["existencias"].CONTROLDEEXISTENCIAS_FechaYHoraEstaMedicionMes)
            
        # Recepciones
        recepciones = ET.SubElement(reporte_volumen_mensual, '{%s}RECEPCIONES'% covol)
        ET.SubElement(recepciones, '{%s}TotalRecepcionesMes'% covol).text = str(producto["recepciones"].TotalRecepcionesMes)
        suma_volumen_recepcion_mes = ET.SubElement(recepciones, '{%s}SumaVolumenRecepcionMes'% covol)
        ET.SubElement(suma_volumen_recepcion_mes, '{%s}ValorNumerico'% covol).text = str(round(producto["recepciones"].SumaVolumenRecepcionesMes, 0))
        ET.SubElement(suma_volumen_recepcion_mes, '{%s}UM'% covol).text = str(producto["recepciones"].SumaVolumenRecepcionesMes_UM)
        if producto["producto"].ClaveProducto == 'PR09' and informacion_reporte.TipoCaracter in ['permisionarios','usuarios']:
            PoderCalorifico = ET.SubElement(recepciones, 'PoderCalorifico'% covol)
            ET.SubElement(PoderCalorifico, '{%s}ValorNumerico'% covol).text = str(producto["recepciones"].PoderCalorifico)
            ET.SubElement(PoderCalorifico, '{%s}UM'% covol).text = str(producto["recepciones"].PoderCalorifico_UM)
        ET.SubElement(recepciones, '{%s}TotalDocumentosMes'% covol).text = str(producto["recepciones"].TotalDocumentosMes)
        ET.SubElement(recepciones, '{%s}ImporteTotalRecepcionesMensual'% covol).text = str(producto["recepciones"].ImporteTotalRecepcionesMensual)
        #complemento_elem_recepciones = ET.SubElement(recepciones, 'Complemento'% covol)
        #complemento_elem_recepciones.append(nuevo_elemento_complemento)
        Complemento = ET.SubElement(recepciones, '{%s}Complemento'% covol)
        
        tipo = str('comercializador')
        id_complemento_recepcion = 2
        DailyReportFuntionsInstance = DailyReportFuntions(2)
        recepcion = producto["recepciones"]
        #complementos_date = DailyReportFuntionsInstance.GetComplementDailyReportAll(id_complemento_recepcion,tipo,'D',recepcion,'R_cv')

        
        if any(complemento_distribuidor_recepcion):
            for complementos in complemento_distribuidor_recepcion:
                Complemento_Comercializacion_Recepcion = ET.SubElement(Complemento, '{%s}Complemento_Comercializacion' %covol)
                """
                terminalAlmYTrans = complementos['TERMINALALMYTRANS_TERMINALALMYDIST']

                Terminalalmtrans = ET.SubElement(Complemento_Distribucion_Recepcion, '{%s}TERMINALALMYDIST' % dis )
                Almacenamiento = ET.SubElement(Terminalalmtrans, '{%s}Almacenamiento' % dis)
                ET.SubElement(Almacenamiento, '{%s}TerminalAlm' % dis).text =  str(terminalAlmYTrans['Almacenamiento'].TerminalAlm)
                ET.SubElement(Almacenamiento, '{%s}PermisoAlmacenamiento' % dis).text = str(terminalAlmYTrans['Almacenamiento'].PermisoAlmacenamiento)
                ET.SubElement(Almacenamiento, '{%s}TarifaDeAlmacenamiento' % dis).text = str(terminalAlmYTrans['Almacenamiento'].TarifaDeAlmacenamiento )
                ET.SubElement(Almacenamiento, '{%s}CargoPorCapacidadAlmac' % dis).text = str(terminalAlmYTrans['Almacenamiento'].CargoPorCapacidadAlmac) 
                ET.SubElement(Almacenamiento, '{%s}CargoPorUsoAlmac' % dis).text = str(terminalAlmYTrans['Almacenamiento'].CargoPorUsoAlmac )
                ET.SubElement(Almacenamiento, '{%s}CargoVolumetricoAlmac' % dis).text = str(terminalAlmYTrans['Almacenamiento'].CargoVolumetricoAlmac) 

                Transporte = ET.SubElement(Terminalalmtrans, '{%s}Transporte' % dis)
                ET.SubElement(Transporte, '{%s}PermisoTransporte' % dis).text = str(terminalAlmYTrans['Transporte'].PermisoTransporte)
                ET.SubElement(Transporte, '{%s}ClaveDeVehiculo' % dis).text =str(terminalAlmYTrans['Transporte'].ClaveDeVehiculo)
                ET.SubElement(Transporte, '{%s}TarifaDeTransporte'% dis).text = str(terminalAlmYTrans['Transporte'].TarifaDeTransporte)
                ET.SubElement(Transporte, '{%s}CargoPorCapacidadTrans'% dis).text = str(terminalAlmYTrans['Transporte'].CargoPorCapacidadTrans)
                ET.SubElement(Transporte, '{%s}CargoPorUsoTrans'% dis).text = str(terminalAlmYTrans['Transporte'].CargoPorUsoTrans)
                ET.SubElement(Transporte, '{%s}CargoVolumetricoTrans'% dis).text =str(terminalAlmYTrans['Transporte'].CargoVolumetricoTrans)
                ET.SubElement(Transporte, '{%s}TarifaDeSuministro'% dis).text = str(terminalAlmYTrans['Transporte'].CargoVolumetricoTrans)

                for trasvase in complementos['TRASVASE']:
                                Trasvase = ET.SubElement(Complemento_Distribucion_Recepcion, '{%s}TRASVASE'% dis)
                                ET.SubElement(Trasvase, '{%s}NombreTrasvase' % dis).text =  str(trasvase['TRASVASE'].NombreTrasvase)
                                ET.SubElement(Trasvase, '{%s}RfcTrasvase' % dis).text = str(trasvase['TRASVASE'].RfcTrasvase)
                                ET.SubElement(Trasvase, '{%s}PermisoTrasvase' % dis).text =str(trasvase['TRASVASE'].PermisoTrasvase)
                                ET.SubElement(Trasvase, '{%s}DescripcionTrasvase' % dis).text =  str(trasvase['TRASVASE'].DescripcionTrasvase)
                                ET.SubElement(Trasvase, '{%s}CfdiTrasvase' % dis).text = str(trasvase['TRASVASE'].CfdiTrasvase)

                dictamen =complementos['DICTAMEN']
                Dictamen = ET.SubElement(Complemento_Distribucion_Recepcion, '{%s}DICTAMEN'% dis)
                ET.SubElement(Dictamen, '{%s}RfcDictamen' % dis).text = str(dictamen['DICTAMEN'].RfcDictamen)
                ET.SubElement(Dictamen, '{%s}LoteDictamen' % dis).text = str(dictamen['DICTAMEN'].LoteDictamen)
                ET.SubElement(Dictamen, '{%s}NumeroFolioDictamen' % dis).text = str(dictamen['DICTAMEN'].NumeroFolioDictamen)
                ET.SubElement(Dictamen, '{%s}FechaEmisionDictamen' % dis).text =str(dictamen['DICTAMEN'].ResultadoDictamen)
                ET.SubElement(Dictamen, '{%s}ResultadoDictamen' % dis).text = str(dictamen['DICTAMEN'].ResultadoDictamen)
                """                            
                certificado = complementos['CERTIFICADO']

                Certificado = ET.SubElement(Complemento_Comercializacion_Recepcion, '{%s}CERTIFICADO' % co)
                ET.SubElement(Certificado, '{%s}RfcCertificado' % co).text = str(certificado['CERTIFICADO'].RfcCertificado)
                ET.SubElement(Certificado, '{%s}NumeroFolioCertificado' % co).text = str(certificado['CERTIFICADO'].NumeroFolioCertificado)
                ET.SubElement(Certificado, '{%s}FechaEmisionCertificado' % co).text = str(certificado['CERTIFICADO'].FechaEmisionCertificado)
                ET.SubElement(Certificado, '{%s}ResultadoCertificado' % co).text = str(certificado['CERTIFICADO'].ResultadoCertificado)   

                for nacional in complementos['NACIONAL']:
                    Nacional = ET.SubElement(Complemento_Comercializacion_Recepcion, '{%s}NACIONAL' % co)

                    ET.SubElement(Nacional, '{%s}RfcClienteOProveedor' % co).text =str(nacional['NACIONAL'].RFC)
                    ET.SubElement(Nacional, '{%s}NombreClienteOProveedor' % co).text = str(nacional['NACIONAL'].Nombre_comercial)
                    if nacional['NACIONAL'].PermisoClienteOProveedor is not None:
                        ET.SubElement(Nacional, '{%s}PermisoClienteOProveedor' % co).text = str(nacional['NACIONAL'].PermisoClienteOProveedor)

                    for cfdi in nacional['cfdis']:
                            CFDIs = ET.SubElement(Nacional, '{%s}CFDIs' % co)
                            ET.SubElement(CFDIs, '{%s}CFDI' % co).text = str(cfdi.CFDI)
                            ET.SubElement(CFDIs, '{%s}TipoCFDI' % co).text = str(cfdi.TipoCFDI)
                            ET.SubElement(CFDIs, '{%s}PrecioVentaOCompraOContrap' % co).text = str(cfdi.PrecioVentaOCompraOContrap)
                            ET.SubElement(CFDIs, '{%s}FechaYHoraTransaccion' % co).text = str(cfdi.FechaYHoraTransaccion.astimezone().isoformat())
                            VolumenDocumentado = ET.SubElement(CFDIs, '{%s}VolumenDocumentado' % co)
                            ET.SubElement(VolumenDocumentado, '{%s}ValorNumerico' % co).text = str(cfdi.VolumenDocumentado)
                            ET.SubElement(VolumenDocumentado, '{%s}UM' % co).text = str(cfdi.VolumenDocumentado_UM)
                
                """
                for extranjero in complementos['EXTRANJERO']:
                    Extranjero = ET.SubElement(Complemento_Distribucion_Recepcion, '{%s}EXTRANJERO' % dis)

                    ET.SubElement(Extranjero, '{%s}PermisoImportacionOExportacion' % dis).text = str(extranjero['EXTRANJERO'].PermisoImportacionOExportacion)
                    for pedimentos in extranjero['pedimentos']:
                            Pedimentos = ET.SubElement(Extranjero, '{%s}PEDIMENTOS' % dis)
                            ET.SubElement(Pedimentos, '{%s}PuntoDeInternacionOExtraccion' % dis).text = str(pedimentos.PuntoDeInternacionOExtraccion)
                            ET.SubElement(Pedimentos, '{%s}PaisOrigenODestino' % dis).text = str(pedimentos.PaisOrigenODestino)
                            ET.SubElement(Pedimentos, '{%s}MedioDeTransEntraOSaleAduana' % dis).text = str(pedimentos.MedioDeTransEntraOSaleAducto)
                            ET.SubElement(Pedimentos, '{%s}PedimentoAduanal' % dis).text =str(pedimentos.PedimentosAduanal)
                            ET.SubElement(Pedimentos, '{%s}Incoterms'% dis).text = str(pedimentos.Incoterms)
                            ET.SubElement(Pedimentos, '{%s}PrecioDeImportacionOExportacion' % dis).text = str(pedimentos.PrecioDeImportacionOExportacion) 

                            Volumen_documentado = ET.SubElement(Pedimentos, '{%s}VolumenDocumentado'% dis)
                            ET.SubElement(Volumen_documentado, '{%s}ValorNumerico' % dis).text =str(pedimentos.VolumenDocumentado)
                            ET.SubElement(Volumen_documentado, '{%s}UM' % dis).text = str(pedimentos.VolumenDocumentado_UM)
                """                                        
                Aclarcion = ET.SubElement(Complemento_Comercializacion_Recepcion, '{%s}ACLARACION' % co)
                ET.SubElement(Aclarcion, '{%s}Aclaracion' % co).text = str(complementos['ACLARACION']['ACLARACION'])
        else:
            complemento_distribuidor_recepcion = DailyReportFuntionsInstance.GetComplementDailyReportAll(id_complemento_entrega,tipo,'C',None,None)
            for complementos in complemento_distribuidor_recepcion:
                Complemento_Comercializacion_Recepcion = ET.SubElement(Complemento, '{%s}Complemento_Comercializacion' %covol)
                certificado = complementos['CERTIFICADO']

                Certificado = ET.SubElement(Complemento_Comercializacion_Recepcion, '{%s}CERTIFICADO' % co)
                ET.SubElement(Certificado, '{%s}RfcCertificado' % co).text = str(certificado['CERTIFICADO'].RfcCertificado)
                ET.SubElement(Certificado, '{%s}NumeroFolioCertificado' % co).text = str(certificado['CERTIFICADO'].NumeroFolioCertificado)
                ET.SubElement(Certificado, '{%s}FechaEmisionCertificado' % co).text = str(certificado['CERTIFICADO'].FechaEmisionCertificado)
                ET.SubElement(Certificado, '{%s}ResultadoCertificado' % co).text = str(certificado['CERTIFICADO'].ResultadoCertificado)

        # Entregas
        entregas = ET.SubElement(reporte_volumen_mensual, '{%s}ENTREGAS'% covol)
        ET.SubElement(entregas, '{%s}TotalEntregasMes'% covol).text = str(producto["entregas"].TotalEntregasMes)
        suma_volumen_entregado_mes = ET.SubElement(entregas, '{%s}SumaVolumenEntregadoMes'% covol)
        ET.SubElement(suma_volumen_entregado_mes, '{%s}ValorNumerico'% covol).text = str(round(producto["entregas"].SumaVolumenEntregadoMes, 0))
        ET.SubElement(suma_volumen_entregado_mes, '{%s}UM'% covol).text = str(producto["entregas"].SumaVolumenEntregadoMes_UM)
        if producto["producto"].ClaveProducto == 'PR09' and informacion_reporte.TipoCaracter in ['permisionarios','usuarios']:
            PoderCalorifico = ET.SubElement(entregas, '{%s}PoderCalorifico'% covol)
            ET.SubElement(PoderCalorifico, '{%s}ValorNumerico'% covol).text = str(producto["recepciones"].PoderCalorifico)
            ET.SubElement(PoderCalorifico, '{%s}UM').text = str(producto["recepciones"].PoderCalorifico_UM)
        ET.SubElement(entregas, '{%s}TotalDocumentosMes'% covol).text = str(producto["entregas"].TotalDocumentosMes)
        ET.SubElement(entregas, '{%s}ImporteTotalEntregasMes'% covol).text = str(producto["entregas"].ImporteTotalRecepcionesMensual)
        #complemento_elem_entregas = ET.SubElement(entregas, '{%s}Complemento'% covol)
        #complemento_elem_entregas.append(nuevo_elemento_complemento)
        
        Complemento = ET.SubElement(entregas, '{%s}Complemento'% covol)
        
                
        tipo = str('comercializador')
        id_complemento_entrega = 2
        DailyReportFuntionsInstance = DailyReportFuntions(2)
        entrega = producto["entregas"]
        

        if complemento_distribuidor_entrega:
            for complementos in complemento_distribuidor_entrega:
                Complemento_Comercializacion_Entrega = ET.SubElement(Complemento, '{%s}Complemento_Comercializacion' %covol)
                """
                terminalAlmYTrans = complementos['TERMINALALMYTRANS_TERMINALALMYDIST']

                Terminalalmtrans = ET.SubElement(Complemento_Distribucion_Recepcion, '{%s}TERMINALALMYDIST' % dis )
                Almacenamiento = ET.SubElement(Terminalalmtrans, '{%s}Almacenamiento' % dis)
                ET.SubElement(Almacenamiento, '{%s}TerminalAlm' % dis).text =  str(terminalAlmYTrans['Almacenamiento'].TerminalAlm)
                ET.SubElement(Almacenamiento, '{%s}PermisoAlmacenamiento' % dis).text = str(terminalAlmYTrans['Almacenamiento'].PermisoAlmacenamiento)
                ET.SubElement(Almacenamiento, '{%s}TarifaDeAlmacenamiento' % dis).text = str(terminalAlmYTrans['Almacenamiento'].TarifaDeAlmacenamiento )
                ET.SubElement(Almacenamiento, '{%s}CargoPorCapacidadAlmac' % dis).text = str(terminalAlmYTrans['Almacenamiento'].CargoPorCapacidadAlmac) 
                ET.SubElement(Almacenamiento, '{%s}CargoPorUsoAlmac' % dis).text = str(terminalAlmYTrans['Almacenamiento'].CargoPorUsoAlmac )
                ET.SubElement(Almacenamiento, '{%s}CargoVolumetricoAlmac' % dis).text = str(terminalAlmYTrans['Almacenamiento'].CargoVolumetricoAlmac) 

                Transporte = ET.SubElement(Terminalalmtrans, '{%s}Transporte' % dis)
                ET.SubElement(Transporte, '{%s}PermisoTransporte' % dis).text = str(terminalAlmYTrans['Transporte'].PermisoTransporte)
                ET.SubElement(Transporte, '{%s}ClaveDeVehiculo' % dis).text =str(terminalAlmYTrans['Transporte'].ClaveDeVehiculo)
                ET.SubElement(Transporte, '{%s}TarifaDeTransporte'% dis).text = str(terminalAlmYTrans['Transporte'].TarifaDeTransporte)
                ET.SubElement(Transporte, '{%s}CargoPorCapacidadTrans'% dis).text = str(terminalAlmYTrans['Transporte'].CargoPorCapacidadTrans)
                ET.SubElement(Transporte, '{%s}CargoPorUsoTrans'% dis).text = str(terminalAlmYTrans['Transporte'].CargoPorUsoTrans)
                ET.SubElement(Transporte, '{%s}CargoVolumetricoTrans'% dis).text =str(terminalAlmYTrans['Transporte'].CargoVolumetricoTrans)
                ET.SubElement(Transporte, '{%s}TarifaDeSuministro'% dis).text = str(terminalAlmYTrans['Transporte'].CargoVolumetricoTrans)

                for trasvase in complementos['TRASVASE']:

                        Trasvase = ET.SubElement(Complemento_Distribucion_Recepcion, '{%s}TRASVASE'% dis)
                        ET.SubElement(Trasvase, '{%s}NombreTrasvase' % dis).text =  str(trasvase['TRASVASE'].NombreTrasvase)
                        ET.SubElement(Trasvase, '{%s}RfcTrasvase' % dis).text = str(trasvase['TRASVASE'].RfcTrasvase)
                        ET.SubElement(Trasvase, '{%s}PermisoTrasvase' % dis).text =str(trasvase['TRASVASE'].PermisoTrasvase)
                        ET.SubElement(Trasvase, '{%s}DescripcionTrasvase' % dis).text =  str(trasvase['TRASVASE'].DescripcionTrasvase)
                        ET.SubElement(Trasvase, '{%s}CfdiTrasvase' % dis).text = str(trasvase['TRASVASE'].CfdiTrasvase)

                dictamen =complementos['DICTAMEN']
                Dictamen = ET.SubElement(Complemento_Distribucion_Recepcion, '{%s}DICTAMEN'% dis)
                ET.SubElement(Dictamen, '{%s}RfcDictamen' % dis).text = str(dictamen['DICTAMEN'].RfcDictamen)
                ET.SubElement(Dictamen, '{%s}LoteDictamen' % dis).text = str(dictamen['DICTAMEN'].LoteDictamen)
                ET.SubElement(Dictamen, '{%s}NumeroFolioDictamen' % dis).text = str(dictamen['DICTAMEN'].NumeroFolioDictamen)
                ET.SubElement(Dictamen, '{%s}FechaEmisionDictamen' % dis).text =str(dictamen['DICTAMEN'].ResultadoDictamen)
                ET.SubElement(Dictamen, '{%s}ResultadoDictamen' % dis).text = str(dictamen['DICTAMEN'].ResultadoDictamen)
                """                            
                certificado = complementos['CERTIFICADO']

                Certificado = ET.SubElement(Complemento_Comercializacion_Entrega, '{%s}CERTIFICADO' % co)
                ET.SubElement(Certificado, '{%s}RfcCertificado' % co).text = str(certificado['CERTIFICADO'].RfcCertificado)
                ET.SubElement(Certificado, '{%s}NumeroFolioCertificado' % co).text = str(certificado['CERTIFICADO'].NumeroFolioCertificado)
                ET.SubElement(Certificado, '{%s}FechaEmisionCertificado' % co).text = str(certificado['CERTIFICADO'].FechaEmisionCertificado)
                ET.SubElement(Certificado, '{%s}ResultadoCertificado' % co).text = str(certificado['CERTIFICADO'].ResultadoCertificado)   

                for nacional in complementos['NACIONAL']:
                    Nacional = ET.SubElement(Complemento_Comercializacion_Entrega, '{%s}NACIONAL' % co)

                    ET.SubElement(Nacional, '{%s}RfcClienteOProveedor' % co).text =str(nacional['NACIONAL'].RFC)
                    ET.SubElement(Nacional, '{%s}NombreClienteOProveedor' % co).text = str(nacional['NACIONAL'].Nombre_comercial)
                    if nacional['NACIONAL'].PermisoClienteOProveedor is not None:
                        ET.SubElement(Nacional, '{%s}PermisoClienteOProveedor' % co).text = str(nacional['NACIONAL'].PermisoClienteOProveedor)

                    for cfdi in nacional['cfdis']:
                            CFDIs = ET.SubElement(Nacional, '{%s}CFDIs' % co)
                            ET.SubElement(CFDIs, '{%s}CFDI' % co).text = str(cfdi.CFDI)
                            ET.SubElement(CFDIs, '{%s}TipoCFDI' % co).text = str(cfdi.TipoCFDI)
                            ET.SubElement(CFDIs, '{%s}PrecioVentaOCompraOContrap' % co).text = str(cfdi.PrecioVentaOCompraOContrap)
                            ET.SubElement(CFDIs, '{%s}FechaYHoraTransaccion' % co).text = str(cfdi.FechaYHoraTransaccion.astimezone().isoformat())
                            VolumenDocumentado = ET.SubElement(CFDIs, '{%s}VolumenDocumentado' % co)
                            ET.SubElement(VolumenDocumentado, '{%s}ValorNumerico' % co).text = str(cfdi.VolumenDocumentado)
                            ET.SubElement(VolumenDocumentado, '{%s}UM' % co).text = str(cfdi.VolumenDocumentado_UM)
                """
                for extranjero in complementos['EXTRANJERO']:
                    Extranjero = ET.SubElement(Complemento_Distribucion_Recepcion, '{%s}EXTRANJERO' % dis)

                    ET.SubElement(Extranjero, '{%s}PermisoImportacionOExportacion' % dis).text = str(extranjero['EXTRANJERO'].PermisoImportacionOExportacion)
                    for pedimentos in extranjero['pedimentos']:
                                    Pedimentos = ET.SubElement(Extranjero, '{%s}PEDIMENTOS' % dis)
                                    ET.SubElement(Pedimentos, '{%s}PuntoDeInternacionOExtraccion' % dis).text = str(pedimentos.PuntoDeInternacionOExtraccion)
                                    ET.SubElement(Pedimentos, '{%s}PaisOrigenODestino' % dis).text = str(pedimentos.PaisOrigenODestino)
                                    ET.SubElement(Pedimentos, '{%s}MedioDeTransEntraOSaleAduana' % dis).text = str(pedimentos.MedioDeTransEntraOSaleAducto)
                                    ET.SubElement(Pedimentos, '{%s}PedimentoAduanal' % dis).text =str(pedimentos.PedimentosAduanal)
                                    ET.SubElement(Pedimentos, '{%s}Incoterms'% dis).text = str(pedimentos.Incoterms)
                                    ET.SubElement(Pedimentos, '{%s}PrecioDeImportacionOExportacion' % dis).text = str(pedimentos.PrecioDeImportacionOExportacion) 

                                    Volumen_documentado = ET.SubElement(Pedimentos, '{%s}VolumenDocumentado'% dis)
                                    ET.SubElement(Volumen_documentado, '{%s}ValorNumerico' % dis).text =str(pedimentos.VolumenDocumentado)
                                    ET.SubElement(Volumen_documentado, '{%s}UM' % dis).text = str(pedimentos.VolumenDocumentado_UM)
                """                           
                Aclarcion = ET.SubElement(Complemento_Comercializacion_Entrega, '{%s}ACLARACION' % co)
                ET.SubElement(Aclarcion, '{%s}Aclaracion' % co).text = str(complementos['ACLARACION']['ACLARACION'])
        else:
            complemento_distribuidor_entrega = DailyReportFuntionsInstance.GetComplementDailyReportAll(id_complemento_entrega,tipo,'C',None,None)
            for complementos in complemento_distribuidor_entrega:
                Complemento_Comercializacion_Entrega = ET.SubElement(Complemento, '{%s}Complemento_Comercializacion' %covol)
                certificado = complementos['CERTIFICADO']

                Certificado = ET.SubElement(Complemento_Comercializacion_Entrega, '{%s}CERTIFICADO' % co)
                ET.SubElement(Certificado, '{%s}RfcCertificado' % co).text = str(certificado['CERTIFICADO'].RfcCertificado)
                ET.SubElement(Certificado, '{%s}NumeroFolioCertificado' % co).text = str(certificado['CERTIFICADO'].NumeroFolioCertificado)
                ET.SubElement(Certificado, '{%s}FechaEmisionCertificado' % co).text = str(certificado['CERTIFICADO'].FechaEmisionCertificado)
                ET.SubElement(Certificado, '{%s}ResultadoCertificado' % co).text = str(certificado['CERTIFICADO'].ResultadoCertificado) 
    
    for bitacora in bitacora_XML:
        BITACORA = ET.SubElement(root, '{%s}BITACORA'% covol)
        BITACORAMENSUAL = ET.SubElement(BITACORA, '{%s}BITACORAMENSUAL'% covol)
        
        #fecha_str = bitacora['fecha']
        #fecha_dt = datetime.fromisoformat(fecha_str)  # Convertir la cadena a datetime

        ET.SubElement(BITACORAMENSUAL, '{%s}NumeroRegistro'% covol).text =  str( bitacora.Id_Eventos_Comercializador )
        ET.SubElement(BITACORAMENSUAL, '{%s}FechaYHoraEvento'% covol).text = str( bitacora.FechaYHoraEvento.astimezone().isoformat())
        usuario_responsable = bitacora.UsuarioResponsable
        if usuario_responsable is not None and bitacora.get('is_event'):
                ET.SubElement(BITACORAMENSUAL, '{%s}UsuarioResponsable' % covol).text = str(bitacora.UsuarioResponsable) if bitacora.get('is_event') else ''
                    
        ET.SubElement(BITACORAMENSUAL, '{%s}TipoEvento'% covol).text = str(bitacora.TipoEvento)
        ET.SubElement(BITACORAMENSUAL, '{%s}DescripcionEvento'% covol).text =  str(bitacora.DescripcionEvento)
        tipos = ['7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21']
        if str(bitacora.TipoEvento) in tipos:
            ET.SubElement(BITACORAMENSUAL, '{%s}IdentificacionComponenteAlarma'% covol).text = str( bitacora.IdentificacionCOmponenteAlarma )
    # Convertir el árbol de elementos a una cadena XML
        xml_str = ET.tostring(root, encoding='utf-8')#.decode('utf-8')

    # Validar el XML contra el esquema XSD
    try:
        xml_doc = ET.fromstring(xml_str)
        schema.validate(xml_doc)
    except xmlschema.XMLSchemaValidationError as e:
        error_trace = traceback.format_exc()
        # Logging detallado
        logging.debug(f"ValidationError: {str(e)}")
        logging.debug(f"Traceback: {error_trace}")
        return f"El XML no es válido: {e}", 400
        return f"El XML no es válido: {e}", 400

    
    # Crear el archivo XML de respuesta
    file_name = f"Reporte_mensual_{datetime.now().strftime('%Y%m%d%H%M%S')}.xml"
    response = Response(
        xml_str,
        mimetype='application/xml',
        headers={
            'Content-Disposition': f'attachment; filename={file_name}',
            'Content-Type': 'application/xml'
        }
    )
    return response

@app_comercializador.route('/control_mensual_volumetrico', methods=['GET','POST'])
@login_required
def control_mensual_volumetrico():
    with VerificarPermisosUsuario("CReportemensual", current_user.RolPerms) as contexto:
        if contexto is False:  # No tiene permisos
            return jsonify({'error':'El usuario actual no tiene los permisos para ejecutar esta accion.','action':'redirect'})
    #Ini - Cambio jul-25
    componente = 'comercializador/consultar_ventas'#checar o cambiar
    Descripcion = None
    Tipo_Evento = None
    #Fin - Cambio jul-25    
    # Obtener el año actual y el rango de años
    
    anio_actual = datetime.now().year
    years = list(range(anio_actual - 4, anio_actual + 1))

    if request.method == 'POST':
        with VerificarPermisosUsuario("CReportemensualVer", current_user.RolPerms) as contexto:
            if contexto is False:  # No tiene permisos
                return redirect("/scaizen/")
        # Obtener los parámetros del formulario
        producto = request.form.get('producto')
        month = request.form.get('month')
        year = request.form.get('year')
        generar = request.form.get('generar')
        GenerateMensualReportInstance = scaizen_cv_funtions.MensualReportFuntions(2)
        # Verificar que todos los parámetros estén presentes
        if generar:
            fecha_inicio = datetime(int(year), int(month),1,0,0,0,0)
            ultimo_dia_mes= calendar.monthrange(int(year), int(month))[1]
            fecha_fin = datetime(int(year), int(month), ultimo_dia_mes, 23, 59, 59)
            fecha_inicio = fecha_inicio.strftime('%Y-%m-%d %H:%M:%S')
            fecha_fin = fecha_fin.strftime('%Y-%m-%d %H:%M:%S')
            return GenerateMensualReportInstance.SetMensualData(fecha_inicio, fecha_fin)
        if producto and month and year:
            try:
                if producto != "all":
                    scaizen_funtions = scaizen_cv_funtions.GeneralReport(2)
                    producto_id = scaizen_funtions.GiveProductNameById(producto)
                    report = GenerateMensualReportInstance.GetMensualReport(producto_id,month,year)
                    if report:
                        control_volumetrico =fill_mensual_data(report)
                        return jsonify({'data': [control_volumetrico]})
                    else: return jsonify({'error': 'Datos no encontrados'})
                else:
                    controles_volumetricos = []
                    reports = GenerateMensualReportInstance.GetMensualReportAll(month,year)
                    if reports:
                        #Ini - Cambio jul-25
                        Descripcion = f'Obtención y recuperación de reporte volumetrico mensual de comercializador del mes {month}-{year}  '
                        Tipo_Evento = 3
                        EventosComercializador.add(
                            datetime.now(), current_user.Username, Tipo_Evento, Descripcion, componente
                        )
                        #Fin - Cambio jul-25
                        for report in reports:
                            control_volumetrico = fill_mensual_data(report)
                            controles_volumetricos.append(control_volumetrico)
                        return jsonify({'data': controles_volumetricos})
                    else: return jsonify({'error': 'No se encontraron datos para los parámetros proporcionados.'})
            except ValueError:
                return jsonify({'error': 'Formato de fecha inválido'}), 400
        # Si los parámetros no están presentes, mostrar la plantilla de formulario vacío
        return render_template('scaizen/orden_mes.html', years=years,blueprint='app_comercializador',productos_color = config.PRODUCTOS_COLOR_BY_NAME, PRODUCTOS_NAMES = config.PRODUCTOS_NAMES)
    # Si la solicitud no es POST, renderizar la plantilla
    
    return render_template('scaizen/comercializador_reporte_mensual.html', years=years,blueprint='app_comercializador',
                        productos_color = config.PRODUCTOS_COLOR_BY_NAME, PRODUCTOS_NAMES = config.PRODUCTOS_NAMES)

def generate_mensual_pdf(productos,periodo):
    
    #Ini - Cambio jul-25
    componente = 'comercializador/generate_mensual_pdf'
    Descripcion = None
    Tipo_Evento = None
    #Fin - Cambio jul-25
    
    informacion_reporte = cv.ControlesVolumetricos.select_by_id(2)
    SelloDigital = cv.Configuraciones.select_by_clave('SelloDigital')
    SelloDigital = SelloDigital.valor if SelloDigital and hasattr(SelloDigital, 'valor') else ""
    pdf = PDF(data_report=informacion_reporte,headerpage='Reporte Volumétrico Mensual',periodo=periodo,SelloDigital=SelloDigital)


    # Add a page
    pdf.add_page()
    for i, producto in enumerate(productos):
        pdf.producto_text(producto["producto"])
        # Existencias table
        pdf.section_title_table("Existencias")
        headers = ['Volumen', 'Fecha y Hora']
        rows = [[f'{round(producto["existencias"].CONTROLDEEXISTENCIAS_VolumenExistenciasMes,0)} Litro(s)',
                str(producto["existencias"].CONTROLDEEXISTENCIAS_FechaYHoraEstaMedicionMes)]]
        pdf.create_table(headers, rows)

        # Recepciones table
        pdf.section_title_table("Recepciones")
        headers = ['Total de Recepciones', 'Volumen', 'Total de documentos', 'Importe Total de Recepciones']
        rows = [[str(producto["recepciones"].TotalRecepcionesMes), f'{round(producto["recepciones"].SumaVolumenRecepcionesMes,0)} Litro(s)', 
                str(producto["recepciones"].TotalDocumentosMes), str(round(producto["recepciones"].ImporteTotalRecepcionesMensual,3))]]
        pdf.create_table(headers, rows)

        # Entregas table
        pdf.section_title_table("Entregas")
        headers = ['Total de Entregas', 'Volumen', 'Total de documentos', 'Importe Total de Entregas']
        rows = [[str(producto["entregas"].TotalEntregasMes), f'{round(producto["entregas"].SumaVolumenEntregadoMes,0)} Litro(s)', 
                str(producto["entregas"].TotalDocumentosMes), str(round(producto["entregas"].ImporteTotalRecepcionesMensual,3))]]
        pdf.create_table(headers, rows)
        if i < len(productos) - 1:
            pdf.add_page()

    # Generar el PDF en memoria
    pdf_output = pdf.output(dest='S').encode('latin1')

    #Ini - Cambio jul-25
    Descripcion = f'Obtención y recuperación de PDF de reporte volumetrico mensual del periodo {periodo}'
    Tipo_Evento = 3
    EventosComercializador.add(
        datetime.now(), current_user.Username, Tipo_Evento, Descripcion, componente
    )
    #Fin - Cambio jul-25

    return pdf_output
    
@app_comercializador.route('/informe_mensual_pdf', methods=['GET','POST'])
@login_required
def informe_mensual_pdf():
    with VerificarPermisosUsuario("CReportemensualPDF", current_user.RolPerms) as contexto:
            if contexto is False:  # No tiene permisos
                return jsonify({'error':'El usuario actual no tiene los permisos para ejecutar esta accion.','action':'redirect'})
            
    producto = request.args.get('producto')
    month = request.args.get('month')
    year = request.args.get('year')
    if producto and month and year:
        GenerateMensualReportInstance = scaizen_cv_funtions.MensualReportFuntions(2)
        try:
            if producto != "all":
                scaizen_funtions = scaizen_cv_funtions.GeneralReport(2)
                producto_id = scaizen_funtions.GiveProductNameById(producto)
                reports = GenerateMensualReportInstance.GetMensualReport(producto_id,month,year)
                reports = [reports]
            else:
                reports = GenerateMensualReportInstance.GetMensualReportAll(month,year)
                
            
            if reports:
                meses = {
                    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
                    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
                    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
                }
                periodo = f"{meses[int(month)]} {year}"
                pdf_output = generate_mensual_pdf(reports,periodo)
                filename = f'Reporte_mensual_{meses[int(month)]}_{year}_{datetime.now().strftime("%Y%m%d%H%M%S")}.pdf'
                return Response(pdf_output, mimetype='application/pdf', headers={
                        'Content-Disposition': f'attachment;filename={filename}'
                })
            else: return jsonify({'error': 'No se encontraron datos para los parámetros proporcionados.'})
        except ValueError:
            return jsonify({'error': 'El formato de la fecha es inválido. Por favor, revise los valores de mes y año.'})
        
    else:  return  jsonify({'error': 'Faltan parámetros necesarios. Por favor, complete todos los campos.'})

@app_comercializador.route('/informe_mensual_json', methods=['GET','POST'])
@login_required
def informe_mensual_json():
    with VerificarPermisosUsuario("DReportemensualJSON", current_user.RolPerms) as contexto:
        if contexto is False:  # No tiene permisos
            return jsonify({'error':'El usuario actual no tiene los permisos para ejecutar esta accion.','action':'redirect'})
    componente = 'comercializador/informe_mensual_json'
    Descripcion = None
    Tipo_Evento = None

    month = request.args.get('month')
    year = request.args.get('year')
    if month and year:
        GenerateMensualReportInstance = scaizen_cv_funtions.MensualReportFuntions(1)
        try:
            productos_data = []
            productos_data1 = GenerateMensualReportInstance.GetMensualReportAll(month,year)
            GenerateMensualReportInstance = scaizen_cv_funtions.MensualReportFuntions(2)
            productos_data2 = GenerateMensualReportInstance.GetMensualReportAll(month,year)
            if productos_data1:
                productos_data.append(productos_data1)
            else: 
                productos_data.append([])
            
            if productos_data2:
                productos_data.append(productos_data2)
            else: 
                productos_data.append([])

            logging.debug(f"productos_data: {productos_data}")
            if productos_data:
                ultimo_dia_mes= calendar.monthrange(int(year), int(month))[1]
                fecha_corte = datetime(int(year), int(month), ultimo_dia_mes, 23, 59, 59)

                #Ini - Cambio jul-25
                Descripcion = f'Obtención y recuperación de JSON de reporte volumetrico mensual del mes {month}-{year} '
                Tipo_Evento = 3
                EventosComercializador.add(
                    datetime.now(), current_user.Username, Tipo_Evento, Descripcion, componente
                )
                #Fin - Cambio jul-25
                                    
                return REPORTE_MENSUAL_COMBINADO_JSON(productos_data,fecha_corte)
            else: return jsonify({'error': 'No se encontraron datos para los parámetros proporcionados, pero puedes generar para la fecha que selecionaste.'})
        except ValueError as e:
            error_trace = traceback.format_exc()
            # Logging detallado
            logging.debug(f"ValueError: {str(e)}")
            logging.debug(f"Traceback: {error_trace}")
            return jsonify({'error': str(e)})
        except Exception as e:
            error_trace = traceback.format_exc()
            # Logging detallado
            logging.debug(f"ValueError: {str(e)}")
            logging.debug(f"Traceback: {error_trace}")
    else:  return  jsonify({'error': 'Faltan parámetros necesarios. Por favor, complete todos los campos.'})

@app_comercializador.route('/informe_mensual_xml', methods=['GET','POST'])
@login_required
def informe_mensual_xml():
    with VerificarPermisosUsuario("CReportemensualXML", current_user.RolPerms) as contexto:
        if contexto is False:  # No tiene permisos
            return jsonify({'error':'El usuario actual no tiene los permisos para ejecutar esta accion.','action':'redirect'})
    
    #Ini - Cambio jul-25
    componente = 'comercializador/informe_mensual_xml'
    Descripcion = None
    Tipo_Evento = None
    #Fin - Cambio jul-25

    month = request.args.get('month')
    year = request.args.get('year')
    if month and year:
        GenerateMensualReportInstance = scaizen_cv_funtions.MensualReportFuntions(2)
        try:
            productos_data = []
            productos_data1 = GenerateMensualReportInstance.GetMensualReportAll(month,year)
            GenerateMensualReportInstance = scaizen_cv_funtions.MensualReportFuntions(2)
            productos_data2 = GenerateMensualReportInstance.GetMensualReportAll(month,year)
            if productos_data1:
                productos_data.append(productos_data1)
            else: 
                productos_data.append([])
            
            if productos_data2:
                productos_data.append(productos_data2)
            else: 
                productos_data.append([])
                #siuuuuuuuu
            if productos_data:
                ultimo_dia_mes= calendar.monthrange(int(year), int(month))[1]
                fecha_corte = datetime(int(year), int(month), ultimo_dia_mes, 23, 59, 59)
                
                #Ini - Cambio jul-25
                Descripcion = f'Obtención y recuperación de XML de reporte volumetrico mensual del mes {month}-{year} '
                Tipo_Evento = 3
                EventosComercializador.add(
                    datetime.now(), current_user.Username, Tipo_Evento, Descripcion, componente
                )
                #Fin - Cambio jul-25
                
                return REPORTE_MENSUAL_COMBINADO_XML(productos_data,fecha_corte)
            else: return jsonify({'error': 'No se encontraron datos para los parámetros proporcionados.'})
        except ValueError:
            return jsonify({'error': 'El formato de la fecha es inválido. Por favor, revise los valores de mes y año.'})
        
    else:  return  jsonify({'error': 'Faltan parámetros necesarios. Por favor, complete todos los campos.'})

def generate_alarms_events_pdf(data,periodo,type):
    componente = 'comercializador/generate_alarms_events_pdf'
    Descripcion = None
    Tipo_Evento = None

    informacion_reporte = cv.ControlesVolumetricos.select_by_id(2)
    if type == 'alarmas':
        type_label = 'Alarmas'
    else:
        type_label = 'Eventos'
    SelloDigital = cv.Configuraciones.select_by_clave('SelloDigital')
    SelloDigital = SelloDigital.valor if SelloDigital and hasattr(SelloDigital, 'valor') else ""
    pdf = PDF(data_report=informacion_reporte,headerpage=f'Reporte de {type_label}',periodo=periodo,SelloDigital=SelloDigital)


    # Add a page
    pdf.add_page()
    headers = ['Número', 'Fecha y Hora','Usuario','Tipo','Descripción']
    """,'Identificación']"""
    pdf.section_title_table(type_label)
    rows = []
    for i, item in enumerate(data):
        if type == 'alarmas':
            row =[item.id,item.fecha.astimezone().isoformat(),item.proceso,item.tipo,item.mensaje] 
            """,item.identificacion]"""
        else:
            row =[item['id'],item['fecha'].astimezone().isoformat(),item['usuario'] if item['usuario'] !=None else 'Desconocido', item['tipo'],item['mensaje']]
            """,item['identificacion']]"""
        rows.append(row)
    sizes = [7,16,11,7,47+12]
    """,32]"""
    colums_align = {'5':'L'}
    pdf.create_table_tank(sizes,headers, rows,colums_align=colums_align)

    # Generar el PDF en memoria
    pdf_output = pdf.output(dest='S').encode('latin1')
    return pdf_output


#Reporte PDF de alarmas y venetos#
@app_comercializador.route('/alarms_events_mensual_pdf', methods=['GET','POST'])
@login_required
def alarms_events_mensual_pdf():
    #Ini - Cambio jul-25
    componente = 'comercializador/alarms_events_mensual_pdf'
    Descripcion = None
    Tipo_Evento = None
    #Fin - Cambio jul-25

    datepicker_start = request.args.get('datepicker_start')
    datepicker_end = request.args.get('datepicker_end')
    type = request.args.get('type')
    if datepicker_start and datepicker_end:
        try:
            #Ini - Cambio jul-25
            Descripcion = f'Obtención y recuperación de registros de {type} comercializador periodo {datepicker_start}-{datepicker_end}  '
            Tipo_Evento = 3
            EventosComercializador.add(
                datetime.now(), current_user.Username, Tipo_Evento, Descripcion, componente
            )
            #Fin - Cambio jul-25
            if type == 'alarmas':
                with VerificarPermisosUsuario("CReportedealarmasPDF", current_user.RolPerms) as contexto:
                    if contexto is False:  # No tiene permisos
                        return jsonify({'error':'El usuario actual no tiene los permisos para ejecutar esta accion.','action':'redirect'})
                events = scaizen_db.Evento.select_alarms_given_between_date(datepicker_start, datepicker_end)
            elif type == 'eventos':
                with VerificarPermisosUsuario("CReportedeeventosPDF", current_user.RolPerms) as contexto:
                    if contexto is False:  # No tiene permisos
                        return jsonify({'error':'El usuario actual no tiene los permisos para ejecutar esta accion.','action':'redirect'})
                events = cv.EventosComercializador.select_events_between_dates((datepicker_start, datepicker_end))
            if events:
                periodo = f"{datepicker_start} al {datepicker_end}"
                pdf_output = generate_alarms_events_pdf(events,periodo,type)
                filename = f'Reporte_{type}_{datepicker_start}_{datepicker_end}_{datetime.now().strftime("%Y%m%d%H%M%S")}.pdf'
                return Response(pdf_output, mimetype='application/pdf', headers={
                        'Content-Disposition': f'attachment;filename={filename}'
                    })
            else: return jsonify({'error': 'No se encontraron datos para los parámetros proporcionados.'})
        except ValueError:
            return jsonify({'error': 'El formato de la fecha es inválido. Por favor, revise los valores de mes y año.'})
            
    else:  return  jsonify({'error': 'Faltan parámetros necesarios. Por favor, complete todos los campos.'})



# Reportes eventos #
# Reportes eventos #
@app_comercializador.route('/eventos', methods=['GET','POST'])
@login_required
def eventos():
    with VerificarPermisosUsuario("DReportedeeventos", current_user.RolPerms) as contexto:
        if contexto is False:  # No tiene permisos
            return redirect("/scaizen/")
    componente = 'comercializador/eventos'
    Descripcion = None
    Tipo_Evento = None
    if request.method == 'POST':
        with VerificarPermisosUsuario("DReportedeeventosVer", current_user.RolPerms) as contexto:
            if contexto is False:  # No tiene permisos
                return redirect("/scaizen/")
        # Obtener los parámetros enviados a través de la URL
        datepicker_start = request.form.get('datepicker_start')
        datepicker_end = request.form.get('datepicker_end')
        page_num = request.form.get('page',1,type=int)
        print(datepicker_start)
        print(datepicker_end)
        if datepicker_start and datepicker_end and page_num:
            try:
                elementos_por_pagina=100
                start_index = (page_num - 1) * elementos_por_pagina + 1
                end_index = start_index + elementos_por_pagina

                events, total  = cv.EventosComercializador.select_given_between_date_for_pagination(datepicker_start, datepicker_end,page_num,elementos_por_pagina)

                total_pages = total // elementos_por_pagina+(total % elementos_por_pagina>0)

                #Calcular el índice del último registro
                end_index = min(start_index + elementos_por_pagina,total)
                if end_index > total:
                    ende_index = total
                pagination = Pagination(page=page_num,total=total,per_page=elementos_por_pagina,
                                        display_msg=f"Mostrando registros {start_index} - {end_index} de un total de <strong>({total})</strong>")
                if events:
                    #events_json = scaizen_db.query_to_json(events)
                    events_json=events
                    return jsonify({'data': events_json,'pagination':str(pagination),'total_pages':str(total_pages),'mostrando':start_index,'cantidad':total,'total_paginas':total_pages,'paginactual':page_num})
                #else: return jsonify({'error': 'No se encontraron datos para los parámetros proporcionados.'})
            except ValueError:
                return jsonify({'error': 'El formato de la fecha es inválido. Por favor, revise los valores de mes y año.'})
        else:
            return jsonify({'error': 'Faltan parámetros necesarios. Por favor, complete todos los campos.'})
    else:
        return render_template('scaizen/alarmas_eventos.html',blueprint='app_comercializador',type='eventos')







@app_comercializador.route('/registrar_alarma_evento', methods=['POST', 'GET'])
@login_required
def registrar_alarma_evento():
    """
    Endpoint para registrar una nueva alarma o evento.
    El tipo de registro depende del parámetro 'clase' en el request.
    """
    componente = 'comercializador/registrar'
    Descripcion = None
    Tipo_Evento = None

    # Obtener los datos del request
    data = request.form.to_dict()
    logging.debug(f"Datos recibidos: {data}")
    clase = data['clase']  # Puede ser 'alarma' o 'evento'
    tipo = data['tipo']
    fecha_hora = data['fecha_hora']
    responsables = data['responsable']
    descripcion = data['descripcion']
    identificacion = data['identificacion']  # Opcional para alarmas

    #usuario = current_user.Username  # Usuario actual

    if not all([clase, tipo, fecha_hora, responsables, descripcion]):
        return jsonify({'error': 'Faltan parámetros necesarios. Por favor, complete todos los campos obligatorios.'}), 400

    try:
        if clase == 'alarma':
            # Registrar una nueva alarma
            nueva_alarma = scaizen_db.Alarma.add(
                date_updated=datetime.now(),
                id_user_creator=current_user.id,
                status=1,
                fecha=fecha_hora,
                proceso=responsables,
                mensaje=descripcion,
                tipo=tipo,
                identificacion=identificacion,
                componente=data['componente'],
                direccion_ip=request.remote_addr
            )
            if not nueva_alarma or not hasattr(nueva_alarma, 'id'):
                return jsonify({'error': 'Error al registrar la alarma.'}), 500
            return jsonify({'success': 'Alarma registrada exitosamente.'}), 201

        elif clase == 'evento':
            # Registrar un nuevo evento
            nuevo_evento = cv.EventosComercializador.add(
                fecha=fecha_hora,
                usuario_responsable=responsables,
                tipo=tipo,
                mensaje=descripcion,
                identificacion=identificacion,
                direccion_ip=request.remote_addr
            )
            logging.debug(f"Nuevo evento registrado: {nuevo_evento}")

            if not nuevo_evento:
                return jsonify({'error': 'Error al registrar el evento.'}), 500


            return jsonify({'success': 'Evento registrado exitosamente.'}), 201

        else:
            return jsonify({'error': 'El valor de "clase" debe ser "alarma" o "evento".'}), 400

    except Exception as e:
        logging.error(f"Error al registrar {clase}: {str(e)}")
        return jsonify({'error': f'Error al registrar {clase}: {str(e)}'}), 500