
#Saber si se encuentra activo
from flask_login import UserMixin
from werkzeug.security import check_password_hash #, generate_password_hash

class Tabla_carga(UserMixin): 
    def __init__(self,fecha_inicio,fecha_fin,id_orden_fk,date_created, fecha_entrega,
                  ucl_operador,cantidad_programada, producto, tipo, estado) -> None:
        """
        Constructor de la clase Tabla_descargas.

        Parámetros:
        - fecha_inicio (str): Fecha de inicio para la búsqueda.
        - fecha_fin (str): Fecha de fin para la búsqueda.
        - id_instrumentacion_ucl (int): Identificador de instrumentación UCL.
        - date_created (str): Fecha de creación.
        - fecha_entrega (str): Fecha de entrega.
        - ucl_operador (str): Operador UCL.
        - cantidad_programada (int): Cantidad programada.
        - producto (str): Producto relacionado con la descarga.
        - tipo (str): Tipo de descarga.
        - estado (str): Estado de la descarga.
        """
        self.fecha_inicio_busqueda = fecha_inicio
        self.fecha_fin_busqueda = fecha_fin
        self.id_orden_fk_carga = id_orden_fk
        self.date_created_carga = date_created 
        self.fecha_entrega_carga = fecha_entrega
        self.ucl_operador_carga = ucl_operador
        self.cantidad_programada_carga = cantidad_programada
        self.producto_carga = producto
        self.tipo_carga = tipo
        self.estado_carga = estado

class Tabla_descargas(UserMixin): 
    def __init__(self,fecha_inicio,fecha_fin,id_orden_fk,date_created, fecha_recepcion,
                  ucl_operador,cantidad_programada, producto, tipo, estado) -> None:
        """
        Constructor de la clase Tabla_descargas.

        Parámetros:
        - fecha_inicio (str): Fecha de inicio para la búsqueda.
        - fecha_fin (str): Fecha de fin para la búsqueda.
        - id_instrumentacion_ucl (int): Identificador de instrumentación UCL.
        - date_created (str): Fecha de creación.
        - fecha_recepcion (str): Fecha de recepción.
        - ucl_operador (str): Operador UCL.
        - cantidad_programada (int): Cantidad programada.
        - producto (str): Producto relacionado con la descarga.
        - tipo (str): Tipo de descarga.
        - estado (str): Estado de la descarga.
        """
        
        self.fecha_inicio_busqueda = fecha_inicio
        self.fecha_fin_busqueda = fecha_fin
        self.id_orden_fk_descargas= id_orden_fk
        self.date_created_descargas = date_created 
        self.fecha_recepcion_descargas = fecha_recepcion
        self.ucl_operador_descargas = ucl_operador
        self.cantidad_programada_descargas = cantidad_programada
        self.producto_descargas = producto
        self.tipo_descargas = tipo
        self.estado_descargas = estado

class Tabla_eventos(UserMixin): 
      def __init__(self,fecha_dia,fecha_dia_2,id, fecha, nombre, mensaje, proceso, tipo) -> None:
        
        self.fecha_dia_eventos= fecha_dia
        self.fecha_dia_eventos_2 = fecha_dia_2
        self.id_eventos = id
        self.fecha_eventos = fecha
        self.nombre_eventos = nombre
        self.mensaje_eventos = mensaje
        self.proceso_eventos = proceso
        self.tipo_eventos = tipo


class Tabla_operaciones_mensuales(UserMixin): 
      def __init__(self,fecha_inicio, fecha_fin, id_orden_fk,date_created, date_updated,nombre_comercial,ucl_operador,
      cantidad_programada,volumen_natural,volumen_neto,temperatura_promedio,producto, tipo,estado   ) -> None:
        
        #Debes añadir lo del bash
        self.fecha_inicio_busqueda = fecha_inicio 
        self.fecha_fin_busqueda =  fecha_fin

        self.id_orden_fk_diario = id_orden_fk
        self.date_created_dia_diario = date_created
        self.date_updated_diario = date_updated
        self.nombre_comercial_diario = nombre_comercial
        self.ucl_operador_diario = ucl_operador
        self.cantidad_programada_diario = cantidad_programada
        self.volumen_natural_diario = volumen_natural
        self.volumen_neto_diario = volumen_neto
        self.temperatura_promedio_diario = temperatura_promedio
        self.producto_diario = producto
        self.tipo_diario =  tipo
        self.estado_diario = estado

class Tabla_operaciones_diarias(UserMixin): 
      def __init__(self,fecha_inicio,fecha_fin, id_orden_fk,date_created, date_updated,nombre_comercial,ucl_operador,
      cantidad_programada,volumen_natural,volumen_neto,temperatura_promedio,producto, tipo,estado   ) -> None:
        
        #Debes añadir lo del bash
        self.fecha_inicio_busqueda = fecha_inicio 
        self.fecha_fin_busqueda =  fecha_fin

        self.id_orden_fk_diario = id_orden_fk
        self.date_created_dia_diario = date_created
        self.date_updated_diario = date_updated
        self.nombre_comercial_diario = nombre_comercial
        self.ucl_operador_diario = ucl_operador
        self.cantidad_programada_diario = cantidad_programada
        self.volumen_natural_diario = volumen_natural
        self.volumen_neto_diario = volumen_neto
        self.temperatura_promedio_diario = temperatura_promedio
        self.producto_diario = producto
        self.tipo_diario =  tipo
        self.estado_diario = estado
        




class Tabla_tanques(UserMixin): 
    def __init__(self,id_tanque, producto_tanque, tipo_venta_tanque, tipo_a_recibo_tanque, codigo_tanque) -> None:
        self.id_tanque = id_tanque
        self.producto_tanque = producto_tanque
        self.tipo_venta_tanque = tipo_venta_tanque
        self.tipo_a_recibo_tanque = tipo_a_recibo_tanque
        self.codigo_tanque = codigo_tanque


class Tabla_numero_tanques(UserMixin):
    def __init__(self,id_tanque,codigo):
        self.id_tanque = id_tanque
        self.codigo = codigo

class Tabla_batch_diario_tanques(UserMixin):
    def __init__(self,id_tanque,fecha_startDate, fecha_endDate,numero_bol,fecha_inicio,fecha_termino,volumen_natural,volumen_neto,temperatura,densidad,tipo):
            self.id_tanque = id_tanque
            self.fecha_start = fecha_startDate
            self.fecha_end = fecha_endDate
            self.numero_bol = numero_bol
            self.fecha_inicio = fecha_inicio
            self.fecha_termino = fecha_termino
            self.volumen_natural = volumen_natural
            self.volumen_neto = volumen_neto
            self.temperatura = temperatura
            self.densidad = densidad
            self.tipo = tipo
class Tabla_batch_diario_total_tanques(UserMixin):   
    def __init__(self,total_volumen_natural_carga,total_cartotal_volumen_neto_cargas,
                 total_volumen_natural_descarga,total_volumen_neto_descarga,
                 temperaturas_promedio_carga_1,temperaturas_promedio_descarga_1):
            self.total_volumen_natural_carga = total_volumen_natural_carga
            self.total_volumen_neto_carga = total_cartotal_volumen_neto_cargas
            self.total_volumen_natural_descarga = total_volumen_natural_descarga
            self.total_volumen_neto_descarga = total_volumen_neto_descarga
            self.temperaturas_promedio_carga_1 = temperaturas_promedio_carga_1
            self.temperaturas_promedio_descarga_1 = temperaturas_promedio_descarga_1

class batch_ucl_carga_descarga(UserMixin):
    def __init__(self,fecha_batch,fecha_batch_2 ,id_tanque_fk ,id,volumen_natural,volumen_neto,temperatura_promedio,tipo,totalizador_apertura_fecha,totalizador_cierre_fecha) -> None:
        self.fecha_batch = fecha_batch
        self.fecha_batch_2 = fecha_batch_2



        self.id_tanque_fk_batch = id_tanque_fk
        self.id_batch = id
        self.volumen_natural_batch = volumen_natural
        self.volumen_neto_batch = volumen_neto
        self.temperatura_batch = temperatura_promedio
        self.tipo_batch = tipo
        self.totalizador_apertura_fecha_batch = totalizador_apertura_fecha
        self.totalizador_cierre_fecha_batch = totalizador_cierre_fecha 



class primera_lectura_del_dia(UserMixin):
    def __init__(self,fecha,vol_nat, vol_neto,temp) -> None:
        self.fecha= fecha,
        self.vol_nat = vol_nat
        self.vol_neto = vol_neto
        self.temp = temp
class lectura_tanque_inicio__fin_dia(UserMixin):
    def __init__(self,fecha,vol_nat, vol_neto,temp)-> None:
        self.fecha= fecha,
        self.vol_nat = vol_nat
        self.vol_neto = vol_neto
        self.temp = temp


class lectura_tanque_antes_batch(UserMixin):
    def __init__(self,fecha,vol_nat, vol_neto,temp)-> None:
        self.fecha= fecha,
        self.vol_nat = vol_nat
        self.vol_neto = vol_neto
        self.temp = temp


class lectura_tanque_posterior_batch(UserMixin):
    def __init__(self,fecha,vol_nat, vol_neto,temp)-> None:
        self.fecha= fecha,
        self.vol_nat = vol_nat
        self.vol_neto = vol_neto
        self.temp = temp














class Tabla_batch_mensual_tanques(UserMixin):
    def __init__(self,id_tanque,fecha_startDate, fecha_endDate,
                 numero_bol,
                fecha_start_batch,fecha_end_batch,
                inicio_volumen_natural,inicio_volumen_neto,inicio_temperatura,
                recepcion_total_voluemn_registros_descargas,recepcion_total_volumen_natural_descargas,recepcion_total_volumen_neto_descargas,recepcion_total_temperatura_descargas,
                entrega_total_volumen_registros_cargas,entrega_total_volumen_natural_cargas,entrega_total_volumen_neto_cargas,entrega_total_temperatura_cargas
                
                 ):
        self.id_tanque = id_tanque
        self.fecha_start = fecha_startDate
        self.fecha_end = fecha_endDate
        self.fecha_start_batch = fecha_start_batch
        self.fecha_end_batch = fecha_end_batch        
        self.numero_bol = numero_bol
        self.inicio_volumen_natural = inicio_volumen_natural
        self.inicio_volumen_neto = inicio_volumen_neto
        self.inicio_temperatura = inicio_temperatura

        self.recepcion_total_voluemn_registros_descargas  = recepcion_total_voluemn_registros_descargas
        self.recepcion_total_volumen_natural_descargas = recepcion_total_volumen_natural_descargas
        self.recepcion_total_volumen_neto_descargas = recepcion_total_volumen_neto_descargas
        self.recepcion_total_temperatura_descargas = recepcion_total_temperatura_descargas

        self.entrega_total_volumen_registros_cargas = entrega_total_volumen_registros_cargas
        self.entrega_total_volumen_natural_cargas = entrega_total_volumen_natural_cargas
        self.entrega_total_volumen_neto_cargas = entrega_total_volumen_neto_cargas
        self.entrega_total_temperatura_cargas = entrega_total_temperatura_cargas

class Tabla_distribuidor_venta(UserMixin):
    def __init__(self,id_proveedor,id_estacion, id_cliente,tipo_producto,cantidad, autotanque,fecha,costo,estatus ,informacion) -> None:
        self.id_proveedor = id_proveedor
        self.id_estacion =id_estacion,
        self.id_cliente = id_cliente,
        self.tipo_producto = tipo_producto,
        self.cantidad = cantidad,
        self.autotanque = autotanque,
        self.fecha = fecha, 
        self.costo = costo,
        self.estatus = estatus,
        self.informacion = informacion

class Tabla_distribuidor_venta_consultar(UserMixin):
    def __init__(self,fecha_inicio,fecha_fin ,id,id_proveedor,rfc_proveedor,id_estacion, id_cliente,rfc_cliente,tipo_producto,cantidad, autotanque,fecha,costo,estatus ,informacion) -> None:
        self.fecha_inicio_busqueda = fecha_inicio 
        self.fecha_fin_busqueda =  fecha_fin
        
        self.id = id
        self.id_proveedor=id_proveedor
        self.rfc_proveedor = rfc_proveedor,
        self.id_estacion =id_estacion,
        self.id_cliente = id_cliente,
        self.rfc_cliente = rfc_cliente,
        self.tipo_producto = tipo_producto,
        self.cantidad = cantidad,
        self.autotanque = autotanque,
        self.fecha = fecha, 
        self.costo = costo,
        self.estatus = estatus,
         # Agregamos los nuevos atributos
        # self.tipo_registro = tipo_registro,
        self.informacion = informacion

class Cancelar_Venta(UserMixin):
    def __init__(self,id_venta) -> None:
        self.id_venta = id_venta




class Tabla_Proveedores(UserMixin):
    def __init__(self,codigo,nombre_comercial,razon,rfc,direccion,telefono,email,informacion) -> None:
            self.codigo = codigo
            self.nombre_comercial = nombre_comercial
            self.razon = razon
            self.rfc = rfc
            self.direccion = direccion
            self.telefono =telefono
            self.email = email
            self.informacion = informacion


class Tabla_Proveedores_consulta(UserMixin):
    def __init__(self,id,codigo,nombre_comercial,razon,rfc,direccion,telefono,email,informacion) -> None:
            self.id = id
            self.codigo = codigo
            self.nombre_comercial = nombre_comercial
            self.razon = razon
            self.rfc = rfc
            self.direccion = direccion
            self.telefono =telefono
            self.email = email
            self.informacion = informacion





class Tabla_Cliente(UserMixin):
    def __init__(self,codigo,nombre_comercial,razon,rfc,direccion,telefono,email,informacion) -> None:
            self.codigo = codigo
            self.nombre_comercial = nombre_comercial
            self.razon = razon
            self.rfc = rfc
            self.direccion = direccion
            self.telefono =telefono
            self.email = email
            self.informacion = informacion


class Tabla_numero_clientes(UserMixin):
    def __init__(self,id_cliente,codigo_cliente):
        self.id_cliente = id_cliente
        self.codigo_cliente = codigo_cliente


class Tabla_Cliente_consulta(UserMixin):
    def __init__(self,id,codigo,nombre_comercial,razon,rfc,direccion,telefono,email,informacion) -> None:
            self.id = id
            self.codigo = codigo
            self.nombre_comercial = nombre_comercial
            self.razon = razon
            self.rfc = rfc
            self.direccion = direccion
            self.telefono =telefono
            self.email = email
            self.informacion = informacion

class Tabla_Cliente_actualizar(UserMixin):
    def __init__(self,id_update,id,codigo,nombre_comercial,razon,rfc,direccion,telefono,email,informacion) -> None:
            self.id_update = id_update
            self.id = id
            self.codigo = codigo
            self.nombre_comercial = nombre_comercial
            self.razon = razon
            self.rfc = rfc
            self.direccion = direccion
            self.telefono =telefono
            self.email = email
            self.informacion = informacion



class Tabla_Cliente_actualizar_update(UserMixin):
    def __init__(self,id_update,codigo,nombre_comercial,razon,rfc,direccion,telefono,email,informacion) -> None:
            self.id_update = id_update
            self.codigo = codigo
            self.nombre_comercial = nombre_comercial
            self.razon = razon
            self.rfc = rfc
            self.direccion = direccion
            self.telefono =telefono
            self.email = email
            self.informacion = informacion

 

class Eliminar_Cliente(UserMixin):
    def __init__(self,id_cliente) -> None:
        self.id_cliente = id_cliente




class Tabla_Estacion_alta(UserMixin):
        def __init__(self,id,codigo,Permiso,estacion,comercial,RFC,gerente,direccion,telefono,email,informacion) -> None:
             self.id = id
             self.codigo = codigo
             self.Permiso = Permiso
             self.estacion = estacion
             self.comercial = comercial
             self.RFC = RFC
             self.gerente = gerente
             self.direccion = direccion
             self.telefono = telefono
             self.email = email
            # self.cliente = cliente
             self.informacion = informacion
class Tabla_estaciones_consulta(UserMixin):
    def __init__(self, id, codigo, Permiso_cre, Numero_de_estacion, Nombre_comercial, RFC, Nombre_del_gerente, Direccion, Telefono, Email, Informacion_adicional,PermisoClienteOProveedor) -> None:
        self.id = id
        self.codigo  = codigo
        self.Permiso_cre = Permiso_cre
        self.Numero_de_estacion = Numero_de_estacion
        self.Nombre_comercial = Nombre_comercial
        self.RFC = RFC
        self.Nombre_del_gerente = Nombre_del_gerente
        self.Direccion = Direccion
        self.Telefono = Telefono
        self.Email = Email
        #self.Id_cliente_cv = Id_cliente_cv
        self.Informacion_adicional = Informacion_adicional
        self.PermisoClienteOProveedor = PermisoClienteOProveedor

class Tabla_numero_estaciones(UserMixin):
    def __init__(self,id_estacion,codigo_estacion):
        self.id_estacion = id_estacion
        self.codigo_estacion = codigo_estacion


class EliminarEstacion(UserMixin):
    def __init__(self,id_cliente) -> None:
        self.id_estacion = id_cliente

class Tabla_Estacion_actualizar(UserMixin):
    def __init__(self,id_update,id,codigo,permiso_cre,numero_estacion, nombre_comercial,rfc,gerente,direccion,telefono,email,informacion) -> None:
            self.id_update = id_update
            self.id = id
            self.codigo = codigo
            self.permiso_cre = permiso_cre
            self.numero_estacion = numero_estacion
            self.nombre_comercial = nombre_comercial
            self.rfc = rfc
            self.gerente = gerente
            self.direccion = direccion
            self.telefono =telefono
            self.email = email
            self.informacion = informacion



class Tabla_Estacion_actualizar_update(UserMixin):
    def __init__(self,id_update,codigo,permiso_cre,numero_estacion, nombre_comercial,rfc,gerente,direccion,telefono,email,informacion) -> None:
            self.id_update = id_update
            self.codigo = codigo
            self.permiso_cre = permiso_cre
            self.numero_estacion = numero_estacion
            self.nombre_comercial = nombre_comercial
            self.rfc = rfc
            self.gerente = gerente
            self.direccion = direccion
            self.telefono =telefono
            self.email = email
            self.informacion = informacion


class Tabla_usuarios_consulta(UserMixin):
    def __init__(self, id, Nombre, nombre_completo, Tipo_usuario) -> None:
        self.id = id 
        self.Nombre = Nombre
        self.nombre_completo = nombre_completo
        self.Tipo_usuario = Tipo_usuario
 


class Tabla_Usuario_actualizar(UserMixin):
    def __init__(self,id_update,id, Nombre, nombre_completo, Tipo_usuario) -> None:
            self.id_update = id_update
            self.id = id
            self.Nombre = Nombre
            self.nombre_completo = nombre_completo
            self.Tipo_usuario = Tipo_usuario
class Tabla_usuario_actualizar_update(UserMixin):
    def __init__(self,id_update, Nombre, nombre_completo,contraseña, Tipo_usuario) -> None:
            self.id_update = id_update
            self.Nombre = Nombre
            self.nombre_completo = nombre_completo
            self.contraseña = contraseña
            self.Tipo_usuario = Tipo_usuario


class Eliminar_Usuario(UserMixin):
    def __init__(self,id_cliente) -> None:
        self.id_cliente = id_cliente
























class Tabla_numero_proveedores(UserMixin):
    def __init__(self,id_proveedor,codigo_proveedor):
        self.id_proveedor = id_proveedor
        self.codigo_proveedor = codigo_proveedor
        
class EliminarProveedor(UserMixin):
    def __init__(self,id_cliente) -> None:
        self.id_proveedor = id_cliente

class Tabla_Proveedor_actualizar(UserMixin):
    def __init__(self,id_update,id,codigo,nombre_comercial,razon_social,rfc,direccion,telefono,email,informacion) -> None:
            self.id_update = id_update
            self.id = id
            self.codigo = codigo
            self.nombre_comercial = nombre_comercial
            self.razon_social = razon_social
            self.rfc = rfc
            self.direccion = direccion
            self.telefono =telefono
            self.email = email
            self.informacion = informacion



class Tabla_Proveedor_actualizar_update(UserMixin):
    def __init__(self,id_update,codigo,nombre_comercial,razon_social,rfc,direccion,telefono,email,informacion) -> None:
            self.id_update = id_update
            self.codigo = codigo
            self.nombre_comercial = nombre_comercial
            self.razon_social = razon_social
            self.rfc = rfc
            self.direccion = direccion
            self.telefono =telefono
            self.email = email
            self.informacion = informacion
















class Roles(UserMixin):
    def __init__(self, id, nombre, status ) -> None:
        
        self.id_roll = id
        self.nombre_roll = nombre
        self.status_roll = status



class Alta_Roles(UserMixin):
    def __init__(self,date_created,date_updated,id_user_creator,status,token, descripcion,nombre,id ) -> None:

        self.date_alta = date_created
        self.date_updated_alta = date_updated
        self.id_user_creator_alta = id_user_creator
        self.status_alta = status
        self.token_alta = token
        self.descripcion_alta =descripcion
        self.nombre_alta = nombre
        self.id_alta = id


class Tabla_User(UserMixin):#Para el manejo de usaurios y autenticacion

    def __init__(self, Id, Nombre, nombre_completo, Telefono, Password, Tipo_usuario, Cambio_contraseña, Estatus_usuario  ) -> None:
        self.id = Id
        self.nombre_user = Nombre
        self.nombre_completo = nombre_completo
        self.telefono_user = Telefono
        self.password_user = Password
        self.tipo_usuario_user = Tipo_usuario
        self.cambio_contraseña_user = Cambio_contraseña
        self.estatus_usuario_user = Estatus_usuario


#RECICLAR CODIGO O ELIMINAR
class Tabla_informetanque_dia_inicio(UserMixin):
    #Aqui almacenare medicion de inicio del dia a las 00:00:00 del dia y la medicion del fin del dia a las 23:59:59
    def __init__(self, fecha,fecha_2,id_tanque,nivel_actual_fecha_actualizacion,volumen_natural,volumen_neto,temperatura ) -> None:
        self.fecha_informe = fecha   
        self.fecha_informe_2 = fecha_2   

        self.id_tanque_informe  = id_tanque
        self.nivel_actual_fecha_actualizacion_informe = nivel_actual_fecha_actualizacion
        self.volumen_natural_informe = volumen_natural
        self.volumen_neto_informe = volumen_neto
        self.temperatura_informe  = temperatura
class Tabla_informetanque_dia_fin(UserMixin):
    #Aqui almacenare medicion de inicio del dia a las 00:00:00 del dia y la medicion del fin del dia a las 23:59:59
    def __init__(self, fecha,fecha_2,id_tanque,nivel_actual_fecha_actualizacion,volumen_natural,volumen_neto,temperatura ) -> None:
        self.fecha_informe = fecha   
        self.fecha_informe_2 = fecha_2   

        self.id_tanque_informe  = id_tanque
        self.nivel_actual_fecha_actualizacion_informe = nivel_actual_fecha_actualizacion
        self.volumen_natural_informe = volumen_natural
        self.volumen_neto_informe = volumen_neto
        self.temperatura_informe  = temperatura        

    #Aqui se alamacenaran los resultados encontrados en el dia seleccionado 

        
    #Aqui se almacenara la lectura y la información previa al inicio de la carga/descarga



    #Aqui se almacenara la lectura y la información posterior al fin de la carga/descarga


