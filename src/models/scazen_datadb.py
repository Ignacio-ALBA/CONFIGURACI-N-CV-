from datetime import datetime, timezone, date
from sqlalchemy import Column, Integer, Float, String, Text, DateTime, SmallInteger, ForeignKey,Boolean, DECIMAL, JSON,func
from sqlalchemy.orm import relationship, sessionmaker, joinedload
from sqlalchemy.ext.declarative import declarative_base
from config_carpet.config import GlobalConfig, clave_hex_hash
from sqlalchemy.exc import NoResultFound
from config_carpet.db_conector import connect_db
from models import scaizen_cv as cv
import json
import logging

config = GlobalConfig()
Base, SessionLocal, engine = connect_db(config.GET_DATABASE_URL_SCAIZENDB())

session = SessionLocal()

def query_to_json(query_result):
    resultado = []

    for row in query_result:
        item_dict = {}

        # Verificar si es un diccionario
        if isinstance(row, dict):
            # Procesar el diccionario
            for key, value in row.items():
                if hasattr(value, '__table__'):  # Si es un objeto de SQLAlchemy
                    nested_dict = {}
                    for column in value.__table__.columns:
                        attr_value = getattr(value, column.name, None)

                        # Manejar fechas
                        if isinstance(attr_value, (datetime, date)):
                            nested_dict[column.name] = attr_value.isoformat() if attr_value else None
                        else:
                            nested_dict[column.name] = attr_value

                    item_dict[key] = nested_dict
                else:
                    # Manejar fechas en valores simples
                    if isinstance(value, (datetime, date)):
                        item_dict[key] = value.isoformat() if value else None
                    else:
                        item_dict[key] = value

        # Verificar si es un objeto de SQLAlchemy
        elif hasattr(row, '__table__'):
            # Procesar el objeto de SQLAlchemy
            for column in row.__table__.columns:
                key = column.name
                value = getattr(row, key)

                # Si el valor es otro objeto de SQLAlchemy (relación)
                if hasattr(value, '__table__'):
                    nested_dict = {}
                    for nested_column in value.__table__.columns:
                        attr_value = getattr(value, nested_column.name, None)

                        # Manejar fechas
                        if isinstance(attr_value, (datetime, date)):
                            nested_dict[nested_column.name] = attr_value.isoformat() if attr_value else None
                        else:
                            nested_dict[nested_column.name] = attr_value

                    item_dict[key] = nested_dict
                else:
                    # Manejar fechas en valores simples
                    if isinstance(value, (datetime, date)):
                        item_dict[key] = value.isoformat() if value else None
                    else:
                        item_dict[key] = value

        resultado.append(item_dict)

    return resultado


def add_to_table(new_data_add):
    session = SessionLocal()
    try:
        session.add(new_data_add)  # Agrega el nuevo dato a la sesión
        session.commit()  # Guarda los cambios en la base de datos
        session.refresh(new_data_add)  # Refresca el objeto para obtener los datos generados por la DB
    except Exception as e:
        session.rollback()  # Revertir la transacción en caso de error
        raise e  # Lanza el error nuevamente para manejarlo fuera
    finally:
        session.close()  # Cierra la sesión
    return new_data_add  # Devuelve el objeto completo

class OrdenesDeOperacionCarga(Base):
    __tablename__ = 'ordenes_de_operacion_carga'

    # Definición de columnas
    date_created = Column(DateTime, nullable=True, default=datetime.now(timezone.utc))
    date_updated = Column(DateTime, nullable=True, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    id_user_creator = Column(Integer, default=-1)
    status = Column(Integer, default=-1)
    estado = Column(String(30), default='pendiente')
    id_destinatario_estacion_de_servicio_fk = Column(Integer, default=-1)
    id_destinatario_cliente_fk = Column(Integer, default=-1)
    producto = Column(String(100), default='')
    cantidad_programada = Column(Float, default=-1)
    unidad = Column(String(100), default='')
    id_operador_fk = Column(Integer, default=-1)
    id_autotanque_fk = Column(Integer, default=-1)
    fecha_entrega_programada = Column(DateTime, nullable=True)
    id_patin_fk = Column(Integer, default=-1)
    mas_info = Column(Text, default='')
    fecha_carga = Column(DateTime, nullable=True)
    cantidad_cargada = Column(Float, default=-1)
    fecha_entrega = Column(DateTime, nullable=True)
    cantidad_entregada = Column(Float, default=-1)
    cantidad_por_reingresar = Column(Float, default=-1)
    fecha_reingreso = Column(DateTime, nullable=True)
    cantidad_reingresada = Column(Float, default=-1)
    id_reingreso_fk = Column(Float, default=-1)
    id_nexus_fk = Column(String(100), default='')
    id = Column(Integer, primary_key=True)
    cantidad_cargada_unidad = Column(String(100), default='')
    id_instrumentacion_patin = Column(Integer, default=-1)
    id_instrumentacion_ucl = Column(Integer, default=-1)
    id_orden_fk = Column(Integer, default=-1)
    ucl_operador = Column(String(100), default='')
    id_tanque_fk = Column(Integer, default=-1)
    motivo_cancelacion = Column(Text, nullable=True)
    is_orden_finalizada_enviada_a_nexus = Column(Boolean, default=False)
    peticion_nexus_de_finalizacion = Column(Text, nullable=True)
    respuesta_nexus_de_finalizacion = Column(Text, nullable=True)
    date_cantidad_reprogramada = Column(DateTime, nullable=True)
    cantidad_reprogramada = Column(Float, default=-1)
    cantidad_programada_inicial = Column(Float, default=-1)
    is_orden_finalizada_enviada_a_endpoint = Column(Boolean, default=False)
    peticion_endpoint_de_finalizacion = Column(Text, nullable=True)
    respuesta_endpoint_de_finalizacion = Column(Text, nullable=True)
    endpoint_finalizacion = Column(String(512), nullable=True)
    subtipo = Column(Integer, default=1)  # tinyint(4) en MySQL

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<OrdenesDeOperacionCarga id={self.id} producto={self.producto} estado={self.estado}>"

    def to_dict(self):
        """Convierte la instancia del modelo a un diccionario."""
        return {
            'date_created': self.date_created.isoformat() if self.date_created else None,
            'date_updated': self.date_updated.isoformat() if self.date_updated else None,
            'id_user_creator': self.id_user_creator,
            'status': self.status,
            'estado': self.estado,
            'id_destinatario_estacion_de_servicio_fk': self.id_destinatario_estacion_de_servicio_fk,
            'id_destinatario_cliente_fk': self.id_destinatario_cliente_fk,
            'producto': self.producto,
            'cantidad_programada': self.cantidad_programada,
            'unidad': self.unidad,
            'id_operador_fk': self.id_operador_fk,
            'id_autotanque_fk': self.id_autotanque_fk,
            'fecha_entrega_programada': self.fecha_entrega_programada.isoformat() if self.fecha_entrega_programada else None,
            'id_patin_fk': self.id_patin_fk,
            'mas_info': self.mas_info,
            'fecha_carga': self.fecha_carga.isoformat() if self.fecha_carga else None,
            'cantidad_cargada': self.cantidad_cargada,
            'fecha_entrega': self.fecha_entrega.isoformat() if self.fecha_entrega else None,
            'cantidad_entregada': self.cantidad_entregada,
            'cantidad_por_reingresar': self.cantidad_por_reingresar,
            'fecha_reingreso': self.fecha_reingreso.isoformat() if self.fecha_reingreso else None,
            'cantidad_reingresada': self.cantidad_reingresada,
            'id_reingreso_fk': self.id_reingreso_fk,
            'id_nexus_fk': self.id_nexus_fk,
            'id': self.id,
            'cantidad_cargada_unidad': self.cantidad_cargada_unidad,
            'id_instrumentacion_patin': self.id_instrumentacion_patin,
            'id_instrumentacion_ucl': self.id_instrumentacion_ucl,
            'id_orden_fk': self.id_orden_fk,
            'ucl_operador': self.ucl_operador,
            'id_tanque_fk': self.id_tanque_fk,
            'motivo_cancelacion': self.motivo_cancelacion,
            'is_orden_finalizada_enviada_a_nexus': self.is_orden_finalizada_enviada_a_nexus,
            'peticion_nexus_de_finalizacion': self.peticion_nexus_de_finalizacion,
            'respuesta_nexus_de_finalizacion': self.respuesta_nexus_de_finalizacion,
            'date_cantidad_reprogramada': self.date_cantidad_reprogramada.isoformat() if self.date_cantidad_reprogramada else None,
            'cantidad_reprogramada': self.cantidad_reprogramada,
            'cantidad_programada_inicial': self.cantidad_programada_inicial,
            'is_orden_finalizada_enviada_a_endpoint': self.is_orden_finalizada_enviada_a_endpoint,
            'peticion_endpoint_de_finalizacion': self.peticion_endpoint_de_finalizacion,
            'respuesta_endpoint_de_finalizacion': self.respuesta_endpoint_de_finalizacion,
            'endpoint_finalizacion': self.endpoint_finalizacion,
            'subtipo': self.subtipo
        }

    @classmethod
    def get_all(cls):
        """Consulta todos los registros."""
        try:
            consulta = None
            session = SessionLocal()
            consulta = session.query(cls).all()
            session.close()
            return consulta
        except Exception as e:
            print(f"Error al consultar todos los registros: {e}")
            return None

    @classmethod
    def get_by_id_orden_fk(cls, id_orden_fk):
        """Consulta registros por ID de orden."""
        try:
            consulta = None
            session = SessionLocal()
            consulta = session.query(cls).filter_by(id_orden_fk=id_orden_fk).first()
            session.close()
            return consulta

        except Exception as e:
            print(f"Error al consultar por ID de orden: {e}")
            return None
    
    @classmethod
    def get_by_date_and_producto(cls, producto, fecha_inicio=None, fecha_fin=None):
        """Consulta registros por tipo y producto con fechas opcionales."""
        filters = []
        
        # Agrega los filtros obligatorios
        filters.append(cls.producto == producto)
        filters.append(cls.estado == "finalizado")

        # Agrega los filtros opcionales de fecha
        #if fecha_inicio:
            #filters.append(cls.date_updated >= fecha_inicio)
        #if fecha_fin:
            #filters.append(cls.date_updated <= fecha_fin)

        filters.append(cls.date_updated.between(fecha_inicio,fecha_fin))
        try:
            consulta = None
            session = SessionLocal()
            consulta = session.query(cls).filter(*filters).all()
            session.close()
            return consulta
        except Exception as e:
            print(f"Error al consultar por tipo y producto: {e}")
            return None

    @classmethod
    def get_by_for_tanque_product_date(cls, tanque, product, date_start=None, date_end=None):
        filters = []
        filters.append(cls.id_tanque_fk == tanque)
        filters.append(cls.producto == product)
        filters.append(cls.estado == "finalizado")
        
        #if date_start:
            #filters.append(cls.date_updated >= date_start)
        #if date_end:
            #filters.append(cls.date_updated <= date_end) 
        filters.append(cls.date_updated.between(date_start,date_end))
        try:
                session = SessionLocal()
                consulta = session.query(cls).filter(*filters).all()
                session.close()
                return consulta
        except Exception as e:
            print(f"Error al consultar en órdenes de operación carga: {e}")
            return None
        
    @classmethod
    def select_given_between_date_for_pagination(cls, fecha_inicio, fecha_fin, page_num=1, elementos_por_pagina=50):
        session = SessionLocal()
        sessioncv = cv.SessionLocal()
        results = sessioncv.query(cv.CargaDistribuidor.NumeroDeOrden_Distribuidor, cv.CargaDistribuidor.Orden_Complemento).all()
        if results:
            orden_number, order_complemento = zip(*results)
        else:
            orden_number, order_complemento = [], []
        logging.debug(orden_number)
        try:
            # Contar el número total de registros en el rango de fechas
            total_cargas = (session.query(cls)
            .filter(cls.fecha_carga.between(fecha_inicio, fecha_fin), 
                    cls.estado == "finalizado",
                    ~cls.id_orden_fk.in_(orden_number),~cls.id_orden_fk.in_(order_complemento))
            .count())
            
            # Consulta con límite y offset para paginación
            consulta = (session.query(cls)
            .filter(cls.fecha_carga.between(fecha_inicio, fecha_fin),
                    cls.estado == "finalizado",
                    ~cls.id_orden_fk.in_(orden_number),~cls.id_orden_fk.in_(order_complemento))
            .order_by(cls.id.desc())
            .limit(elementos_por_pagina)
            .offset((page_num - 1) * elementos_por_pagina)  # Saltar elementos de páginas anteriores
            .all())
            
            data_return = []
            # Aplicar hash a Id_RECEPCION para cada registro
            for registro in consulta:
                data = {
                    'registro': None,
                    'NoConsecutivo':0
                }
                data['NoConsecutivo'] = registro.id
                registro.id = config.encriptar_a_hex(clave_hex_hash, registro.id_orden_fk)  # Generar hash SHA-256
                fecha = registro.fecha_carga.strftime("%d/%m/%Y %H:%M:%S")
                registro.fecha_carga = fecha
                data['registro'] = registro
                cliente_info = Cliente.select_cliente_by_id(registro.id_destinatario_cliente_fk)
                estacion_info = EstacionesDeServicio.select_by_id(registro.id_destinatario_estacion_de_servicio_fk)
                autotanque = Autotanque.select_autotanque_by_id(registro.id_autotanque_fk)
                if cliente_info: data['cliente'] = cliente_info.nombre_comercial
                if estacion_info: data['cliente'] = estacion_info.nombre_comercial
                if autotanque: data['autotanque'] = autotanque.numero

                batch = BatchUclCargaDescarga.get_by_id_orden_fk(registro.id_orden_fk)
                
                data['volumen_natural'] = format(batch.volumen_natural,".3f") if batch else None
                data['volumen_neto'] = format(batch.volumen_neto,".3f") if batch else None
                data['temperatura_promedio'] = format(batch.temperatura_promedio,".1f") if batch else None
                    
                data_return.append(data)

        except Exception as e:
            session.rollback()
            sessioncv.rollback()
            raise e
        finally:
            session.close()
            sessioncv.close()
        
        return data_return, total_cargas

class OrdenesDeOperacionDescarga(Base):
    __tablename__ = 'ordenes_de_operacion_descarga'

    # Definición de columnas
    date_created = Column(DateTime, nullable=True, default=datetime.now(timezone.utc))
    date_updated = Column(DateTime, nullable=True, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    id_user_creator = Column(Integer, default=-1)
    status = Column(Integer, default=-1)
    estado = Column(String(30), default='pendiente')
    id_proveedor_fk = Column(Integer, default=-1)
    producto = Column(String(100), default='')
    cantidad_programada = Column(Float, default=-1)
    unidad = Column(String(100), default='')
    fecha_recepcion_programada = Column(DateTime, nullable=True)
    id_patin_fk = Column(Integer, default=-1)
    mas_info = Column(Text, default='')
    fecha_recepcion = Column(DateTime, nullable=True)
    cantidad_recibida = Column(Float, default=-1)
    id_nexus_fk = Column(String(100), default='')
    id = Column(Integer, primary_key=True)
    cantidad_recibida_unidad = Column(String(100), default='')
    id_instrumentacion_patin = Column(Integer, default=-1)
    id_instrumentacion_ucl = Column(Integer, default=-1)
    id_orden_fk = Column(Integer, default=-1)
    ucl_operador = Column(String(100), default='')
    id_tanque_fk = Column(Integer, default=-1)
    motivo_cancelacion = Column(Text, nullable=True)
    is_orden_finalizada_enviada_a_nexus = Column(Boolean, default=False)
    peticion_nexus_de_finalizacion = Column(Text, nullable=True)
    respuesta_nexus_de_finalizacion = Column(Text, nullable=True)
    autotanque = Column(String(18), default='N/A', nullable=False)
    date_cantidad_reprogramada = Column(DateTime, nullable=True)
    cantidad_reprogramada = Column(Float, default=-1)
    cantidad_programada_inicial = Column(Float, default=-1)
    is_orden_finalizada_enviada_a_endpoint = Column(Boolean, default=False)
    peticion_endpoint_de_finalizacion = Column(Text, nullable=True)
    respuesta_endpoint_de_finalizacion = Column(Text, nullable=True)
    endpoint_finalizacion = Column(String(512), nullable=True)
    subtipo = Column(Integer, default=1)  # tinyint(4) en MySQL
    monto_facturado = Column(DECIMAL(10, 0), nullable=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<OrdenesDeOperacionDescarga id={self.id} producto={self.producto} estado={self.estado}>"

    def to_dict(self):
        """Convierte la instancia del modelo a un diccionario."""
        return {
            'date_created': self.date_created.isoformat() if self.date_created else None,
            'date_updated': self.date_updated.isoformat() if self.date_updated else None,
            'id_user_creator': self.id_user_creator,
            'status': self.status,
            'estado': self.estado,
            'id_proveedor_fk': self.id_proveedor_fk,
            'producto': self.producto,
            'cantidad_programada': self.cantidad_programada,
            'unidad': self.unidad,
            'fecha_recepcion_programada': self.fecha_recepcion_programada.isoformat() if self.fecha_recepcion_programada else None,
            'id_patin_fk': self.id_patin_fk,
            'mas_info': self.mas_info,
            'fecha_recepcion': self.fecha_recepcion.isoformat() if self.fecha_recepcion else None,
            'cantidad_recibida': self.cantidad_recibida,
            'id_nexus_fk': self.id_nexus_fk,
            'id': self.id,
            'cantidad_recibida_unidad': self.cantidad_recibida_unidad,
            'id_instrumentacion_patin': self.id_instrumentacion_patin,
            'id_instrumentacion_ucl': self.id_instrumentacion_ucl,
            'id_orden_fk': self.id_orden_fk,
            'ucl_operador': self.ucl_operador,
            'id_tanque_fk': self.id_tanque_fk,
            'motivo_cancelacion': self.motivo_cancelacion,
            'is_orden_finalizada_enviada_a_nexus': self.is_orden_finalizada_enviada_a_nexus,
            'peticion_nexus_de_finalizacion': self.peticion_nexus_de_finalizacion,
            'respuesta_nexus_de_finalizacion': self.respuesta_nexus_de_finalizacion,
            'autotanque': self.autotanque,
            'date_cantidad_reprogramada': self.date_cantidad_reprogramada.isoformat() if self.date_cantidad_reprogramada else None,
            'cantidad_reprogramada': self.cantidad_reprogramada,
            'cantidad_programada_inicial': self.cantidad_programada_inicial,
            'is_orden_finalizada_enviada_a_endpoint': self.is_orden_finalizada_enviada_a_endpoint,
            'peticion_endpoint_de_finalizacion': self.peticion_endpoint_de_finalizacion,
            'respuesta_endpoint_de_finalizacion': self.respuesta_endpoint_de_finalizacion,
            'endpoint_finalizacion': self.endpoint_finalizacion,
            'subtipo': self.subtipo,
            'monto_facturado': float(self.monto_facturado) if self.monto_facturado else None
        }

    @classmethod
    def get_all(cls):
        """Consulta todos los registros."""
        try:
            consulta = None
            session = SessionLocal()
            consulta = session.query(cls).all()
            session.close()
            return consulta
        except Exception as e:
            print(f"Error al consultar todos los registros: {e}")
            return None

    @classmethod
    def get_by_id_orden_fk(cls, id_orden_fk):
        """Consulta registros por ID de orden."""
        try:
            consulta = None
            session = SessionLocal()
            consulta = session.query(cls).filter_by(id_orden_fk=id_orden_fk).all()
            session.close()
            return consulta
        except Exception as e:
            print(f"Error al consultar por ID de orden: {e}")
            return None
    @classmethod
    def get_by_date_and_producto(cls, producto, fecha_inicio=None, fecha_fin=None):
        """Consulta registros por tipo y producto con fechas opcionales."""
        filters = []
        
        # Agrega los filtros obligatorios
        filters.append(cls.producto == producto)
        filters.append(cls.estado == "finalizado")

        # Agrega los filtros opcionales de fecha
        #if fecha_inicio:
            #filters.append(cls.date_updated >= fecha_inicio)
        #if fecha_fin:
            #filters.append(cls.date_updated <= fecha_fin)
        filters.append(cls.date_updated.between(fecha_inicio,fecha_fin))
        try:
            # Aplica los filtros almacenados en la lista
            consulta = None
            session = SessionLocal()
            consulta = session.query(cls).filter(*filters).all()
            session.close()
            return consulta
        except Exception as e:
            print(f"Error al consultar por tipo y producto: {e}")
            return None

    
            
    @classmethod
    def get_by_for_tanque_product_date(cls, tanque, product, date_start=None, date_end=None):
            filters = []
            filters.append(cls.id_tanque_fk == tanque)
            filters.append(cls.producto == product)
            filters.append(cls.estado == "finalizado")
            
            #if date_start:
                #filters.append(cls.date_updated >= date_start)
            #if date_end:
                #filters.append(cls.date_updated <= date_end) 
            filters.append(cls.date_updated.between(date_start,date_end))
            try:
                session = SessionLocal()
                consulta = session.query(cls).filter(*filters).all()
                session.close()
                return consulta
            except Exception as e:
                print(f"Error al consultar en órdenes de operación carga: {e}")
                return None

class BatchUclCargaDescarga(Base):
    __tablename__ = 'batch_ucl_carga_descarga'

    # Definición de columnas
    id = Column(Integer, primary_key=True)
    date_created = Column(DateTime, nullable=True, default=datetime.now(timezone.utc))
    date_updated = Column(DateTime, nullable=True, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    id_user_creator = Column(Integer, default=-1)
    status = Column(Integer, default=-1)
    id_orden_fk = Column(String(100), default='')
    fecha_inicio = Column(DateTime, nullable=True)
    fecha_fin = Column(DateTime, nullable=True)
    cantidad_solicitada = Column(Float, default=-1)
    cantidad_despachada = Column(Float, default=-1)
    cantidad_despachada_unidad = Column(String(100), default='')
    volumen_natural = Column(Float, default=-1)
    volumen_neto = Column(Float, default=-1)
    temperatura_promedio = Column(Float, default=-1)
    densidad_promedio = Column(Float, default=-1)
    ctl = Column(Float, default=-1)
    meter_factor = Column(Float, default=-1)
    batch = Column(Text, default='')
    id_instrumentacion_patin = Column(Integer, default=-1)
    id_instrumentacion_ucl = Column(Integer, default=-1)
    factor_de_correccion = Column(Float, default=-1)
    tipo = Column(String(100), default='')
    ucl_operador = Column(String(100), default='')
    host_ip = Column(String(100), default='')
    totalizador_apertura_fecha = Column(DateTime, nullable=True)
    totalizador_apertura_natural = Column(Float, default=-1)
    totalizador_apertura_neto = Column(Float, default=-1)
    totalizador_cierre_fecha = Column(DateTime, nullable=True)
    totalizador_cierre_natural = Column(Float, default=-1)
    totalizador_cierre_neto = Column(Float, default=-1)
    producto = Column(String(100), default='')
    id_tanque_fk = Column(Integer, default=-1)
    numero_de_bol = Column(Integer, default=-1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<BatchUclCargaDescarga id={self.id} order_id={self.id_orden_fk} producto={self.producto} tipo={self.tipo}>"
    
    def to_dict(self):
        """Convierte la instancia del modelo a un diccionario."""
        return {
            'id': self.id,
            'date_created': self.date_created.isoformat() if self.date_created else None,
            'date_updated': self.date_updated.isoformat() if self.date_updated else None,
            'id_user_creator': self.id_user_creator,
            'status': self.status,
            'id_orden_fk': self.id_orden_fk,
            'cantidad_solicitada': self.cantidad_solicitada,
            'cantidad_despachada': self.cantidad_despachada,
            'cantidad_despachada_unidad': self.cantidad_despachada_unidad,
            'volumen_natural': self.volumen_natural,
            'volumen_neto': self.volumen_neto,
            'temperatura_promedio': self.temperatura_promedio,
            'densidad_promedio': self.densidad_promedio,
            'ctl': self.ctl,
            'meter_factor': self.meter_factor,
            'batch': self.batch,
            'id_instrumentacion_patin': self.id_instrumentacion_patin,
            'id_instrumentacion_ucl': self.id_instrumentacion_ucl,
            'factor_de_correccion': self.factor_de_correccion,
            'tipo': self.tipo,
            'ucl_operador': self.ucl_operador,
            'host_ip': self.host_ip,
            'totalizador_apertura_fecha': self.totalizador_apertura_fecha.isoformat() if self.totalizador_apertura_fecha else None,
            'totalizador_apertura_natural': self.totalizador_apertura_natural,
            'totalizador_apertura_neto': self.totalizador_apertura_neto,
            'totalizador_cierre_fecha': self.totalizador_cierre_fecha.isoformat() if self.totalizador_cierre_fecha else None,
            'totalizador_cierre_natural': self.totalizador_cierre_natural,
            'totalizador_cierre_neto': self.totalizador_cierre_neto,
            'producto': self.producto,
            'id_tanque_fk': self.id_tanque_fk,
            'numero_de_bol': self.numero_de_bol
        }

    @classmethod
    def get_all(cls):
        """Consulta todos los registros."""
        try:
            consulta = None
            session = SessionLocal()
            consulta = session.query(cls).all()
            session.close()
            return consulta
        except Exception as e:
            print(f"Error al consultar todos los registros: {e}")
            return None

    @classmethod
    def get_by_id_orden_fk(cls, id_orden_fk):
        """Consulta registros por ID de orden."""
        try:
            consulta = None
            session = SessionLocal()
            consulta = session.query(cls).filter_by(id_orden_fk=id_orden_fk).first()
            session.close()
            return consulta
        except Exception as e:
            print(f"Error al consultar por ID de orden: {e}")
            return None

    @classmethod
    def get_by_tipo_and_producto(cls, tipo, producto, fecha_inicio=None, fecha_fin=None):
        """Consulta registros por tipo y producto con fechas opcionales."""
        filters = []
        
        # Agrega los filtros obligatorios
        filters.append(cls.tipo == tipo)
        filters.append(cls.producto == producto)

        # Agrega los filtros opcionales de fecha
        #if fecha_inicio:
            #filters.append(cls.date_updated >= fecha_inicio)
        #if fecha_fin:
            #filters.append(cls.date_updated <= fecha_fin)
        filters.append(cls.date_updated.between(fecha_inicio,fecha_fin))
        try:
            # Aplica los filtros almacenados en la lista   
            consulta = None
            session = SessionLocal()
            consulta = session.query(cls).filter(*filters).all()
            session.close()
            return consulta
        except Exception as e:
            print(f"Error al consultar por tipo y producto: {e}")
            return None

class Tanque(Base):
    __tablename__ = 'tanques'

    date_created = Column(DateTime, nullable=True, default=datetime.now(timezone.utc))
    date_updated = Column(DateTime, nullable=True, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    id_user_creator = Column(Integer, default=-1)
    status = Column(Integer, default=-1)
    codigo = Column(String(100), nullable=False)
    nombre = Column(String(100))
    tipo_venta = Column(Integer)
    tipo_a_recibo = Column(Integer)
    url_foto = Column(String(100))
    capacidad_maxima = Column(Integer)
    nivel_actual = Column(Float)
    producto = Column(String(100))
    direccion = Column(String(100))
    coordenadas_gps = Column(String(100))
    densidad = Column(String(100))
    id_vp_fk_entrada = Column(Integer)
    id_vp_fk_salida = Column(Integer)
    file1_url = Column(String(100))
    file1_nombre = Column(String(100))
    file2_url = Column(String(100))
    file2_nombre = Column(String(100))
    file3_url = Column(String(100))
    file3_nombre = Column(String(100))
    mas_info = Column(Text)
    id_nexus_fk = Column(String(100))
    id = Column(Integer, primary_key=True)
    capacidad_actual = Column(DECIMAL(15, 3))
    nivel_min_producto = Column(DECIMAL(15, 3))
    nivel_max_producto = Column(DECIMAL(15, 3))
    factor_de_correccion = Column(DECIMAL(15, 3))
    nivel_lo = Column(DECIMAL(15, 3))
    nivel_lo_lo = Column(DECIMAL(15, 3))
    nivel_hi = Column(DECIMAL(15, 3))
    nivel_hi_hi = Column(DECIMAL(15, 3))
    volumen_natural_total = Column(DECIMAL(15, 3))
    volumen_natural = Column(DECIMAL(15, 3))
    volumen_neto = Column(DECIMAL(15, 3))
    volumen_neto_disponible = Column(DECIMAL(15, 3))
    volumen_max_producto = Column(DECIMAL(15, 3))
    volumen_min_producto = Column(DECIMAL(15, 3))
    nivel_actual_fecha_actualizacion = Column(DateTime, nullable=True, default=datetime.now(timezone.utc))
    nivel_actual_unidad = Column(String(100))
    temperatura = Column(Float)
    temperatura_unidad = Column(String(100))
    subtipo = Column(SmallInteger, default=1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<Tanque id={self.id}, codigo={self.codigo}>"

    def to_dict(self):
        return {
            'date_created': self.date_created.isoformat() if self.date_created else None,
            'date_updated': self.date_updated.isoformat() if self.date_updated else None,
            'id_user_creator': self.id_user_creator,
            'status': self.status,
            'codigo': self.codigo,
            'nombre': self.nombre,
            'tipo_venta': self.tipo_venta,
            'tipo_a_recibo': self.tipo_a_recibo,
            'url_foto': self.url_foto,
            'capacidad_maxima': self.capacidad_maxima,
            'nivel_actual': self.nivel_actual,
            'producto': self.producto,
            'direccion': self.direccion,
            'coordenadas_gps': self.coordenadas_gps,
            'densidad': self.densidad,
            'id_vp_fk_entrada': self.id_vp_fk_entrada,
            'id_vp_fk_salida': self.id_vp_fk_salida,
            'file1_url': self.file1_url,
            'file1_nombre': self.file1_nombre,
            'file2_url': self.file2_url,
            'file2_nombre': self.file2_nombre,
            'file3_url': self.file3_url,
            'file3_nombre': self.file3_nombre,
            'mas_info': self.mas_info,
            'id_nexus': self.id_nexus,
            'id': self.id,
            'capacidad_actual': self.capacidad_actual,
            'nivel_min_producto': self.nivel_min_producto,
            'nivel_max_producto': self.nivel_max_producto,
            'factor_de_correccion': self.factor_de_correccion,
            'nivel_lo': self.nivel_lo,
            'nivel_lo_lo': self.nivel_lo_lo,
            'nivel_hi': self.nivel_hi,
            'nivel_hi_hi': self.nivel_hi_hi,
            'volumen_natural_total': self.volumen_natural_total,
            'volumen_natural': self.volumen_natural,
            'volumen_neto': self.volumen_neto,
            'volumen_neto_disponible': self.volumen_neto_disponible,
            'volumen_max_producto': self.volumen_max_producto,
            'volumen_min_producto': self.volumen_min_producto,
            'nivel_actual_fecha_actualizacion': self.nivel_actual_fecha_actualizacion,
            'nivel_actual_unidad': self.nivel_actual_unidad,
            'temperatura': self.temperatura,
            'temperatura_unidad': self.temperatura_unidad
        }

    @classmethod
    def get_all(cls):
        try:
            consulta = None
            session = SessionLocal()
            consulta = session.query(cls).all()
            session.close()
            return consulta
        except Exception as e:
            print(f"Error al consultar todos los registros: {e}")
            return None
        
    @classmethod
    def get_for_id(cls, id):
        try:
            consulta = None
            session = SessionLocal()
            consulta = session.query(cls).filter_by(id=id).first()
            session.close()
            return consulta
        except Exception as e:
            print(f"Error al recuperar dato por id: {e}")
            return None
        
    @classmethod
    def get_for_product(cls, producto):
        try:
            consulta = None
            session = SessionLocal()
            consulta = session.query(cls).filter_by(producto=producto).all()
            session.close()
            return consulta
        except Exception as e:
            print(f"Error al recuperar el tanque por producto: {e}")
            return None
        
    @classmethod
    def get_for_codigo(cls, codigo):
        try:
            consulta = None
            session = SessionLocal()
            consulta = session.query(cls).filter_by(codigo=codigo).first()
            session.close()
            return consulta
        except Exception as e:
            logging.debug(f"Error al recuperar el tanque por codigo: {e}")
            return None

class MedicionTanque(Base):
    __tablename__ = 'dispositivo_mdp'

    date_created = Column(DateTime, nullable=True, default=datetime.now(timezone.utc))
    date_updated = Column(DateTime, nullable=True, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    id_user_creator = Column(Integer, default=-1)
    status = Column(Integer, default=-1)
    codigo = Column(String(100), nullable=False)  # Asegúrate de que sea obligatorio si lo necesitas
    url_foto = Column(String(100))
    marca = Column(String(100))
    modelo = Column(String(100))
    mas_info = Column(String(100), default='')
    id_instrumentacion_fk = Column(Integer)
    id = Column(Integer, primary_key=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<MedicionTanque id_instrumentacion_fk={self.id_instrumentacion_fk} >"

    def to_dict(self):
        return {
            'date_created': self.date_created.isoformat() if self.date_created else None,
            'date_updated': self.date_updated.isoformat() if self.date_updated else None,
            'id_user_creator': self.id_user_creator,
            'status': self.status,
            'codigo': self.codigo,
            'url_foto': self.url_foto,
            'marca': self.marca,
            'modelo': self.modelo,
            'mas_info': self.mas_info,
            'id_instrumentacion_fk': self.id_instrumentacion_fk,
            'id': self.id
        }

    @classmethod
    def get_all(cls):
        try:
            consulta = None
            session = SessionLocal()
            consulta = session.query(cls).all()
            session.close()
            return consulta
        except Exception as e:
            print(f"Error al consultar todos los registros: {e}")
            return None
    #Checar
    @classmethod
    def get_for_id(cls, id_instrumentacion_fk):
        try:
            consulta = None
            session = SessionLocal()
            consulta = session.query(cls).filter_by(id_instrumentacion_fk=id_instrumentacion_fk).one_or_none()
            session.close()
            return consulta           
        except Exception as e:
            print(f"Error al recuperar dato por id: {e}")
            return None

    @classmethod
    def get_for_codigo(cls, codigo):
        try:
            consulta = None
            session = SessionLocal()
            consulta = session.query(cls).filter_by(codigo=codigo).all()
            session.close()
            return consulta 
        except Exception as e:
            print(f"Error al recuperar dato por codigo: {e}")
            return None

class Telemedicion_tanques(Base):
    __tablename__= 'telemedicion_tanques'
    date_created = Column(DateTime, nullable=True)
    date_updated = Column(DateTime, nullable=True)
    id_user_creator = Column(Integer, default=-1)
    status = Column(Integer, default=-1)
    codigo = Column(String(100), default='')
    url_foto = Column(String(100), default='')
    id_tanque_fk = Column(Integer, default=-1)
    id_ucl_fk = Column(Integer, default=-1)
    id_rtd_fk = Column(Integer, default=-1)
    id_servo_fk = Column(Integer, default=-1)
    file1_url = Column(String(100), default='')
    file1_nombre = Column(String(100), default='')
    file2_url = Column(String(100), default='')
    file2_nombre = Column(String(100), default='')
    file3_url = Column(String(100), default='')
    file3_nombre = Column(String(100), default='')
    mas_info = Column(Text, default='')
    id_instrumentacion_fk = Column(Integer, default=-1)
    id = Column(Integer, primary_key=True)
    puerto = Column(Integer, default=-1)


    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<telemedicion_tanques id_instrumentacion_fk={self.id_instrumentacion_fk} >"

    
    def to_dict(self):
        return {
            'date_created': self.date_created.isoformat() if self.date_created else None,
            'date_updated' :   self.date_updated.isoformat() if self.date_updated else None,
            'id_user_creator' :  self.id_user_creator,
            'status' :   self.status,
            'codigo' :  self.codigo,
            'url_foto' :   self.url_foto,
            'id_tanque_fk' :  self.id_tanque_fk,
            'id_ucl_fk' : self.id_ucl_fk,
            'Id_PRODUCTO_fk' : self.Id_PRODUCTO_fk,
            'id_servo_fk':  self.id_servo_fk,
            'file1_url' : self.file1_url,
            'file1_nombre' :  self.file1_nombre,
            'file2_url' :  self.file2_url,
            'file2_nombre': self.file2_nombre,
            'file3_url':  self.file3_url,
            'file3_nombre': self.file3_nombre,
            'mas_info' : self.mas_info,
            'id_instrumentacion_fk' : self.id_instrumentacion_fk,
            'id' :  self.id,
            'puerto' : self.puerto
        }
    @classmethod
    def get_all(cls):
        try:
            consulta = None
            session = SessionLocal()
            consulta = session.query(cls).all()
            session.close()
            return consulta
        except Exception as e:
            print(f"Error al consultar todos los registros: {e}")
            return None
    #Checar
    @classmethod
    def get_for_id_tanque_fk(cls, id):
        try:
            consulta = None
            session = SessionLocal()
            consulta = session.query(cls).filter_by(id_tanque_fk=id).one_or_none()
            session.close()
            return consulta           
        except Exception as e:
            print(f"Error al recuperar dato por id: {e}")
            return None
        
    @classmethod
    def get_for_codigo(cls, codigo):
        try:
            consulta = None
            session = SessionLocal()
            consulta = session.query(cls).filter_by(codigo=codigo).one_or_none()
            session.close()
            return consulta           
        except Exception as e:
            print(f"Error al recuperar dato por id: {e}")
            return None

class Rt_tanques(Base):
    __tablename__ = 'rt_tanques'

    date_created = Column(DateTime, nullable=True, default=datetime.now(timezone.utc))
    date_updated = Column(DateTime, nullable=True, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    id_user_creator = Column(Integer, default=-1)
    status = Column(Integer, default=-1)
    fecha = Column(DateTime, nullable=True, default=datetime.now(timezone.utc))
    id_instrumento_fk = Column(Integer)
    json = Column(JSON)
    id = Column(Integer, primary_key=True)


    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<rt_tanques id_instrumentacion_fk={self.id_instrumento_fk} >"

    
    def to_dict(self):
        return {
            'date_created': self.date_created.isoformat() if self.date_created else None,
            'date_updated': self.date_updated.isoformat() if self.date_updated else None,
            'id_user_creator': self.id_user_creator,
            'status': self.status,
            'fecha': self.codigo,
            'id_instrumento_fk': self.url_foto,
            'json': self.json,
            'id': self.id,
         }
 
    @classmethod
    def get_all(cls):
        try:
            consulta = None
            session = SessionLocal()
            consulta = session.query(cls).all()
            session.close()
            return consulta
        except Exception as e:
            print(f"Error al consultar todos los registros: {e}")
            return None
    #Checar
    @classmethod 
    def get_for_id_instrumentacion_fk_start(cls, id_instrumentacion_fk,fecha):
        try:
            consulta = None
            session = SessionLocal()
            consulta = session.query(cls).filter(cls.id_instrumento_fk  == id_instrumentacion_fk, cls.fecha >= fecha).first()
            session.close()
            return consulta           
        except Exception as e:
            print(f"Error al recuperar dato por id: {e}")
            return None
        
    @classmethod 
    def get_for_id_instrumentacion_end(cls, id_instrumentacion_fk,fecha):
        try:
            consulta = None
            session = SessionLocal()
            consulta = session.query(cls).filter(cls.id_instrumento_fk  == id_instrumentacion_fk, cls.fecha <= fecha).first()
            session.close()
            return consulta           
        except Exception as e:
            logging.debug(f"Error al recuperar dato por id: {e}")
            return None
        
class Usuario(Base):
    __tablename__ = 'usuarios'

    date_created = Column(DateTime, default=datetime.now(timezone.utc))
    date_updated = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    id_user_creator = Column(Integer, default=-1)
    status = Column(Integer, default=-1)
    token = Column(String(32), default='')
    username = Column(String(100), default='')
    nombre = Column(String(100), default='')
    salt_token = Column(String(64), default='')
    password = Column(String(64), default='')
    id = Column(Integer, primary_key=True)

    def __repr__(self):
        return f'<Usuario {self.username}>'
    
class Evento(Base):
    __tablename__ = 'eventos'

    date_created = Column(DateTime, default=datetime.now(timezone.utc))
    date_updated = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    id_user_creator = Column(Integer, default=-1)
    status = Column(Integer, default=-1)
    fecha = Column(DateTime, nullable=True)
    proceso = Column(String(32), default='')
    mensaje = Column(String(512), default='')
    tipo = Column(String(32), default='')
    id = Column(Integer, primary_key=True)

    def __repr__(self):
        return f'<Evento {self.id}>'
    
    @classmethod
    def select_alarms_given_between_date(cls, fecha_inicio, fecha_fin):
        session = SessionLocal()
        try:
            consulta = (session.query(cls, Usuario.nombre.label('usuario'))
                        .join(Usuario, cls.id_user_creator == Usuario.id, isouter=True)
                        .filter(cls.fecha.between(fecha_inicio, fecha_fin), cls.tipo == 'Alarma')
                        .order_by(cls.id.desc())
                        .all())
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

        # Procesamiento de resultados
        resultado = []
        for evento, usuario in consulta:
            usuario_final = usuario if usuario else evento.proceso
            resultado.append({
                'alarma': evento,
                'usuario': usuario_final
            })

        #return resultado
        return resultado
    
    @classmethod
    def select_events_given_between_date(cls, fecha_inicio, fecha_fin):
        session = SessionLocal()
        try:
            consulta = (session.query(cls, Usuario.nombre.label('usuario'))
                        .join(Usuario, cls.id_user_creator == Usuario.id, isouter=True)
                        .filter(cls.fecha.between(fecha_inicio, fecha_fin), cls.tipo == 'Evento')
                        .order_by(cls.id.desc())
                        .all())
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

        # Procesamiento de resultados
        resultado = []
        for evento, usuario in consulta:
            usuario_final = usuario if usuario else evento.proceso
            resultado.append({
                'evento': evento,
                'usuario': usuario_final
            })

        #return resultado
        return resultado

    @classmethod
    def select_events_given_between_date_for_pagination(cls, fecha_inicio, fecha_fin,page_num=1,elementos_por_pagina=100):
        session = SessionLocal()
        try:
            total_eventos = (session.query(cls)
                        .filter(cls.fecha.between(fecha_inicio, fecha_fin), cls.tipo == 'Evento')
                        .count())
            
            # Consulta con límite y offset para paginación
            consulta = (session.query(cls, Usuario.nombre.label('usuario'))
                        .join(Usuario, cls.id_user_creator == Usuario.id, isouter=True)
                        .filter(cls.fecha.between(fecha_inicio, fecha_fin), cls.tipo == 'Evento')
                        .order_by(cls.id.desc())
                        .limit(elementos_por_pagina)
                        .offset((page_num - 1) * elementos_por_pagina)  # Saltar elementos de páginas anteriores
                        .all())
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

        # Procesamiento de resultados
        resultado = []
        for evento, usuario in consulta:
            usuario_final = usuario if usuario else evento.proceso
            resultado.append({
                'evento': evento,
                'usuario': usuario_final
            })

        return resultado, total_eventos
    
class Cliente(Base):
    __tablename__ = 'clientes'

    date_created = Column(DateTime, nullable=True)
    date_updated = Column(DateTime, nullable=True)
    id_user_creator = Column(Integer, default=-1)
    status = Column(Integer, default=-1)
    codigo = Column(String(100), default='')
    url_foto = Column(String(100), default='')
    razon_social = Column(String(512), default='')
    rfc = Column(String(18), default='')
    direccion = Column(String(512), default='')
    ciudad = Column(String(100), default='')
    estado = Column(String(100), default='')
    pais = Column(String(100), default='')
    cp = Column(String(100), default='')
    nombre_comercial = Column(String(100), default='')
    telefono = Column(String(100), default='')
    email = Column(String(100), default='')
    mas_info = Column(Text, default='')
    id_nexus_fk = Column(String(100), default='')
    id = Column(Integer, primary_key=True)

    def __repr__(self):
        return f"<Cliente(id={self.id}, razon_social={self.razon_social})>"

    @classmethod
    def select_cliente_by_id(cls, cliente_id):
        """Obtiene un cliente por su ID."""
        session = SessionLocal()
        consulta = session.query(cls).filter(cls.id == cliente_id).first()
        session.close()
        return consulta
    
class Proveedores(Base):
    __tablename__ = 'proveedores'

    date_created = Column(DateTime, nullable=True)
    date_updated = Column(DateTime, nullable=True)
    id_user_creator = Column(Integer, default=-1)
    status = Column(Integer, default=-1)
    codigo = Column(String(100), default='')
    url_foto = Column(String(100), default='')
    razon_social = Column(String(512), default='')
    rfc = Column(String(18), default='')
    direccion = Column(String(512), default='')
    ciudad = Column(String(100), default='')
    estado = Column(String(100), default='')
    pais = Column(String(100), default='')
    cp = Column(String(100), default='')
    nombre_comercial = Column(String(100), default='')
    telefono = Column(String(100), default='')
    email = Column(String(100), default='')
    mas_info = Column(Text, default='')
    id_nexus_fk = Column(String(100), default='')
    id = Column(Integer, primary_key=True)

    def __repr__(self):
        return f"<Proveedor(id={self.id}, razon_social={self.razon_social})>"

    @classmethod
    def select_proveedor_by_id(cls, proveedor_id):
        """Obtiene un proveedor por su ID."""
        session = SessionLocal()
        consulta = session.query(cls).filter(cls.id == proveedor_id).first()
        session.close()
        return consulta
    
class Autotanque(Base):
    __tablename__ = 'autotanques'

    date_created = Column(DateTime, nullable=True)
    date_updated = Column(DateTime, nullable=True)
    id_user_creator = Column(Integer, default=-1)
    status = Column(Integer, default=-1)
    codigo = Column(String(100), default='')
    url_foto = Column(String(100), default='')
    numero = Column(String(100), default='')
    modelo = Column(String(100), default='')
    capacidad = Column(Integer, default=-1)
    producto = Column(String(100), default='')
    placas = Column(String(100), default='')
    mas_info = Column(Text, default='')
    id_operador_fk = Column(Integer, default=-1)
    id_nexus_fk = Column(String(100), default='')
    id = Column(Integer, primary_key=True)
    capacidad_maxima_compartimento1 = Column(Integer, default=-1)
    capacidad_maxima_compartimento2 = Column(Integer, default=-1)
    capacidad_maxima_compartimento3 = Column(Integer, default=-1)
    capacidad_maxima_compartimento4 = Column(Integer, default=-1)

    def __repr__(self):
        return f"<Autotanque(id={self.id}, modelo={self.modelo}, capacidad={self.capacidad})>"

    @classmethod
    def select_autotanque_by_id(cls, autotanque_id):
        """Obtiene un autotanque por su ID."""
        session = SessionLocal()
        consulta = session.query(cls).filter(cls.id == autotanque_id).first()
        session.close()
        return consulta

class EstacionesDeServicio(Base):
    __tablename__ = 'estaciones_de_servicio'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date_created = Column(DateTime, nullable=True)
    date_updated = Column(DateTime, nullable=True)
    id_user_creator = Column(Integer, default=-1)
    status = Column(Integer, default=-1)
    codigo = Column(String(100), default='')
    url_foto = Column(String(100), default='')
    nombre_comercial = Column(String(100), default='')
    rfc = Column(String(18), default='')
    nombre_gerente = Column(String(100), default='')
    numero_estacion = Column(String(100), default='')
    coordenadas_gps = Column(String(100), default='')
    direccion = Column(String(512), default='')
    ciudad = Column(String(100), default='')
    estado = Column(String(100), default='')
    cp = Column(String(100), default='')
    telefono = Column(String(100), default='')
    email = Column(String(100), default='')
    mas_info = Column(Text, default='')
    id_cliente_fk = Column(Integer, default=-1)
    id_nexus_fk = Column(String(100), default='')
    codigo_cre = Column(String(100), default='')

    def __repr__(self):
        return f"<EstacionesDeServicio(nombre_comercial={self.nombre_comercial}, codigo={self.codigo})>"
    
    @classmethod
    def select_by_id(cls, id):
        """Obtiene un autotanque por su ID."""
        session = SessionLocal()
        consulta = session.query(cls).filter(cls.id == id).first()
        session.close()
        return consulta

class Alarma(Base):
    __tablename__ = 'alarmas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date_created = Column(DateTime, default=func.now())  # Agrega la fecha actual como valor por defecto
    date_updated = Column(DateTime, onupdate=func.now())  # Actualiza el timestamp automáticamente en updates
    id_user_creator = Column(Integer, nullable=True, default=-1)
    status = Column(Integer, nullable=True, default=-1)
    on_board = Column(Boolean, nullable=True, default=True)
    fecha = Column(DateTime, nullable=True)
    proceso = Column(String(32), nullable=True)
    componente = Column(String(200), nullable=True)
    mensaje = Column(String(512), nullable=True)
    tipo = Column(Integer, nullable=True)
    identificacion = Column(String(200), nullable=True)
    direccion_ip = Column(String(40), default=None)

    def __repr__(self):
        return f'<Alarma {self.id}>'
    
    @classmethod
    def select_by_id(cls, id):
        """Obtiene un cliente por su ID."""
        session = SessionLocal()
        consulta = session.query(cls).filter(cls.id == id).first()
        session.close()
        return consulta
    
    @classmethod
    def add(cls,date_updated,id_user_creator, status, fecha, proceso, mensaje, tipo, identificacion,componente,direccion_ip=None):
        # Crea una nueva instancia del modelo Alarma
        nueva_alarma = Alarma(
            date_updated = date_updated,
            id_user_creator=id_user_creator,
            status=status,
            fecha=fecha,
            proceso=proceso,
            mensaje=mensaje,
            tipo=tipo,
            identificacion=identificacion,
            componente=componente,
            direccion_ip=direccion_ip
        )
        result_data = add_to_table(nueva_alarma)
        if result_data:
            cv.EventosAlarmasDistribuidor.add(None, result_data.id, fecha)
        return result_data if result_data else None
    
    
    @classmethod
    def select_alarms_given_between_date(cls, fecha_inicio, fecha_fin):
        session = SessionLocal()
        try:
            consulta = (session.query(cls)
                        .filter(cls.fecha.between(fecha_inicio, fecha_fin))
                        .order_by(cls.id.desc())
                        .all())
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


        #return resultado
        return consulta
    
    @classmethod
    def select_alarms_given_between_date_for_pagination(cls, fecha_inicio, fecha_fin,page_num=1,elementos_por_pagina=100):
        session = SessionLocal()
        try:
            total_eventos = (session.query(cls)
                        .filter(cls.fecha.between(fecha_inicio, fecha_fin))
                        .count())
            
            # Consulta con límite y offset para paginación
            consulta = (session.query(cls)
                        .filter(cls.fecha.between(fecha_inicio, fecha_fin))
                        .order_by(cls.id.desc())
                        .limit(elementos_por_pagina)
                        .offset((page_num - 1) * elementos_por_pagina)  # Saltar elementos de páginas anteriores
                        .all())
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
        
        logging.debug(consulta)

        return consulta, total_eventos

    @classmethod
    def select_by_message_and_status(cls, mensaje):
        session = SessionLocal()
        try:
            consulta = (session.query(cls)
                        .filter(cls.mensaje == mensaje, cls.status == 1)
                        .order_by(cls.id.desc())
                        .all())
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
        return consulta
    
    @classmethod
    def update_status__by_message(cls, mensaje, status):
        session = SessionLocal()
        try:
            alarmas_a_actualizar = (session.query(cls)
                                    .filter(cls.mensaje == mensaje, cls.status == 1)
                                    .all())
            for alarma in alarmas_a_actualizar:
                alarma.status = status
                alarma.date_updated =  datetime.now()
            session.commit()
            return len(alarmas_a_actualizar)
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def select_most_recent_alarms(cls, num_elementos):
        session = SessionLocal()
        try:
            consulta = (session.query(cls)
                        .filter(cls.on_board == True)
                        .order_by(cls.fecha.desc())
                        .limit(num_elementos)
                        .all())
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
        return consulta

class Patines(Base):
    __tablename__ = 'patines'

    id = Column(Integer, primary_key=True, nullable=False)
    date_created = Column(DateTime, default=func.now(), nullable=True)
    date_updated = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=True)
    id_user_creator = Column(Integer, default=-1, nullable=True)
    status = Column(Integer, default=-1, nullable=True)
    codigo = Column(String(100), default='', nullable=True)
    url_foto = Column(String(100), default='', nullable=True)
    tipo_carga = Column(Integer, default=0, nullable=True)
    id_ba_fk = Column(Integer, default=-1, nullable=True)
    id_ucl_fk = Column(Integer, default=-1, nullable=True)
    id_mdp_fk = Column(Integer, default=-1, nullable=True)
    id_rtd_fk = Column(Integer, default=-1, nullable=True)
    id_vcf_autotanque_fk = Column(Integer, default=-1, nullable=True)
    id_permisivo_tierra_fk = Column(Integer, default=-1, nullable=True)
    id_permisivo_sobrellenado_fk = Column(Integer, default=-1, nullable=True)
    tipo_descarga = Column(Integer, default=0, nullable=True)
    id_sf1_fk = Column(Integer, default=-1, nullable=True)
    id_sf2_fk = Column(Integer, default=-1, nullable=True)
    id_sf3_fk = Column(Integer, default=-1, nullable=True)
    file1_url = Column(String(100), default='', nullable=True)
    file1_nombre = Column(String(100), default='', nullable=True)
    file2_url = Column(String(100), default='', nullable=True)
    file2_nombre = Column(String(100), default='', nullable=True)
    file3_url = Column(String(100), default='', nullable=True)
    file3_nombre = Column(String(100), default='', nullable=True)
    mas_info = Column(Text, default='', nullable=True)
    id_instrumentacion_fk = Column(Integer, default=-1, nullable=True)
    id_sf4_fk = Column(Integer, default=-1, nullable=True)
    id_sf5_fk = Column(Integer, default=-1, nullable=True)
    id_sf6_fk = Column(Integer, default=-1, nullable=True)
    producto1 = Column(String(100), default='', nullable=True)
    producto2 = Column(String(100), default='', nullable=True)
    puerto = Column(Integer, default=-1, nullable=True)
    id_vp1_fk_entrada = Column(Integer, default=-1, nullable=True)
    id_vp2_fk_entrada = Column(Integer, default=-1, nullable=True)
    id_vp1_fk_salida = Column(Integer, default=-1, nullable=True)
    id_vp2_fk_salida = Column(Integer, default=-1, nullable=True)
    id_vp3_fk_salida = Column(Integer, default=-1, nullable=True)
    id_vp4_fk_salida = Column(Integer, default=-1, nullable=True)
    id_ba_relevo_fk = Column(Integer, nullable=True)
    id_ba_secundaria_fk = Column(Integer, default=-1, nullable=False)

    def __repr__(self):
        return f"<Patines(id={self.id}, codigo='{self.codigo}')>"

    @classmethod
    def select_by_id(cls,patines_id):
        session = SessionLocal()
        try:
            return session.query(Patines).filter(Patines.id == patines_id).first()
        except Exception as e:
            print(f"Error al seleccionar todas las entradas: {e}")
            return []
        finally:
            session.close()
        
    @classmethod
    def select_all(cls):
        session = SessionLocal()
        try:
            return session.query(cls).all()
        except Exception as e:
            print(f"Error al seleccionar todas las entradas: {e}")
            return []
        finally:
            session.close()

    @classmethod
    def select_all_descargas(cls):
        session = SessionLocal()
        try:
            return session.query(cls).filter(cls.tipo_descarga == 1).all()
        except Exception as e:
            print(f"Error al seleccionar todas las entradas: {e}")
            return []
        finally:
            session.close()

    @classmethod
    def select_all_cargas(cls):
        session = SessionLocal()
        try:
            return session.query(cls).filter(cls.tipo_carga == 1).all()
        except Exception as e:
            print(f"Error al seleccionar todas las entradas: {e}")
            return []
        finally:
            session.close()

class DispositivoUCL(Base):
    __tablename__ = 'dispositivo_ucl'

    id = Column(Integer, primary_key=True, nullable=False)
    date_created = Column(DateTime, default=func.now(), nullable=True)
    date_updated = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=True)
    id_user_creator = Column(Integer, default=-1, nullable=True)
    status = Column(Integer, default=-1, nullable=True)
    codigo = Column(String(100), default='', nullable=True)
    url_foto = Column(String(100), default='', nullable=True)
    marca = Column(String(100), default='', nullable=True)
    modelo = Column(String(100), default='', nullable=True)
    mas_info = Column(Text, default='', nullable=True)
    id_instrumentacion_fk = Column(Integer, default=-1, nullable=True)

    def __repr__(self):
        return f"<DispositivoUCL(id={self.id}, codigo='{self.codigo}', marca='{self.marca}')>"

    @classmethod
    def select_by_id(cls, dispositivo_id):
        session = SessionLocal()
        try:
            return session.query(cls).filter(cls.id == dispositivo_id).first()
        except Exception as e:
            print(f"Error al seleccionar el dispositivo: {e}")
            return None
        finally:
            session.close()

    @classmethod
    def select_all(cls):
        session = SessionLocal()
        try:
            return session.query(cls).all()
        except Exception as e:
            print(f"Error al seleccionar todos los dispositivos: {e}")
            return []
        finally:
            session.close()

    @classmethod
    def select_by_id_instrumentacion_fk(cls, id_instrumentacion_fk):
        session = SessionLocal()
        try:
            return session.query(cls).filter(cls.id_instrumentacion_fk == id_instrumentacion_fk).first()
        except Exception as e:
            print(f"Error al seleccionar el dispositivo: {e}")
            return None
        finally:
            session.close()

class DispositivoBA(Base):
    __tablename__ = 'dispositivo_ba'

    id = Column(Integer, primary_key=True, nullable=False)
    date_created = Column(DateTime, default=func.now(), nullable=True)
    date_updated = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=True)
    id_user_creator = Column(Integer, default=-1, nullable=True)
    status = Column(Integer, default=-1, nullable=True)
    codigo = Column(String(100), default='', nullable=True)
    url_foto = Column(String(100), default='', nullable=True)
    marca = Column(String(100), default='', nullable=True)
    modelo = Column(String(100), default='', nullable=True)
    mas_info = Column(Text, default='', nullable=True)
    id_instrumentacion_fk = Column(Integer, default=-1, nullable=True)

    def __repr__(self):
        return f"<DispositivoBA(id={self.id}, codigo='{self.codigo}', marca='{self.marca}')>"

    @classmethod
    def select_by_id(cls, dispositivo_id):
        session = SessionLocal()
        try:
            return session.query(cls).filter(cls.id == dispositivo_id).first()
        except Exception as e:
            print(f"Error al seleccionar el dispositivo: {e}")
            return None
        finally:
            session.close()

    @classmethod
    def select_all(cls):
        session = SessionLocal()
        try:
            return session.query(cls).all()
        except Exception as e:
            print(f"Error al seleccionar todos los dispositivos: {e}")
            return []
        finally:
            session.close()
