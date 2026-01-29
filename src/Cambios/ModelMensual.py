from datetime import datetime, timezone
from extensions import db
from flask_sqlalchemy import SQLAlchemy

class OrdenesDeOperacionCarga(db.Model):
    __tablename__ = 'ordenes_de_operacion_carga'
    
    # Definición de las columnas
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date_created = db.Column(db.DateTime, nullable=True, default=datetime.now(timezone.utc))
    date_updated = db.Column(db.DateTime, nullable=True, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    id_user_creator = db.Column(db.Integer, nullable=True, default=-1)
    status = db.Column(db.Integer, nullable=True, default=-1)
    estado = db.Column(db.String(30), nullable=True, default='pendiente')
    id_destinatario_estacion_de_servicio_fk = db.Column(db.Integer, nullable=True, default=-1)
    id_destinatario_cliente_fk = db.Column(db.Integer, nullable=True, default=-1)
    producto = db.Column(db.String(100), nullable=True)
    cantidad_programada = db.Column(db.Float, nullable=True, default=-1)
    unidad = db.Column(db.String(100), nullable=True)
    id_operador_fk = db.Column(db.Integer, nullable=True, default=-1)
    id_autotanque_fk = db.Column(db.Integer, nullable=True, default=-1)
    fecha_entrega_programada = db.Column(db.DateTime, nullable=True)
    id_patin_fk = db.Column(db.Integer, nullable=True, default=-1)
    mas_info = db.Column(db.Text, nullable=True, default='')
    fecha_carga = db.Column(db.DateTime, nullable=True)
    cantidad_cargada = db.Column(db.Float, nullable=True, default=-1)
    fecha_entrega = db.Column(db.DateTime, nullable=True)
    cantidad_entregada = db.Column(db.Float, nullable=True, default=-1)
    cantidad_por_reingresar = db.Column(db.Float, nullable=True, default=-1)
    fecha_reingreso = db.Column(db.DateTime, nullable=True)
    cantidad_reingresada = db.Column(db.Float, nullable=True, default=-1)
    id_reingreso_fk = db.Column(db.Float, nullable=True, default=-1)
    id_nexus_fk = db.Column(db.String(100), nullable=True)
    cantidad_cargada_unidad = db.Column(db.String(100), nullable=True)
    id_instrumentacion_patin = db.Column(db.Integer, nullable=True, default=-1)
    id_instrumentacion_ucl = db.Column(db.Integer, nullable=True, default=-1)
    id_orden_fk  = db.Column(db.Integer, nullable=True, default=-1)
    ucl_operador = db.Column(db.String(100), nullable=True)
    id_tanque_fk = db.Column(db.Integer, nullable=True, default=-1)
    motivo_cancelacion = db.Column(db.Text, nullable=True)
    is_orden_finalizada_enviada_a_nexus = db.Column(db.SmallInteger, nullable=True, default=-1)
    peticion_nexus_de_finalizacion = db.Column(db.Text, nullable=True)
    respuesta_nexus_de_finalizacion = db.Column(db.Text, nullable=True)
    date_cantidad_reprogramada = db.Column(db.DateTime, nullable=True)
    cantidad_reprogramada = db.Column(db.Float, nullable=True, default=-1)
    cantidad_programada_inicial = db.Column(db.Float, nullable=True, default=-1)
    is_orden_finalizada_enviada_a_endpoint = db.Column(db.SmallInteger, nullable=False, default=-1)
    peticion_endpoint_de_finalizacion = db.Column(db.Text, nullable=True)
    respuesta_endpoint_de_finalizacion = db.Column(db.Text, nullable=True)
    endpoint_finalizacion = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f'<OrdenesDeOperacionCarga id={self.id} producto={self.producto}>'

    @classmethod
    def get_by_id(cls, id):
        """Consulta un registro por su ID primario."""
        return cls.query.filter_by(id=id).first()
    
    @classmethod
    def get_all(cls):
        """Consulta todos los registros."""
        return cls.query.all()
    
class BatchUclCargaDescarga(db.Model):
    __tablename__ = 'batch_ucl_carga_descarga'

    # Definición de columnas
    date_created = db.Column(db.DateTime, nullable=True, default=datetime.now(timezone.utc))
    date_updated = db.Column(db.DateTime, nullable=True, onupdate=datetime.now(timezone.utc))
    id_user_creator = db.Column(db.Integer, default=-1)
    status = db.Column(db.Integer, default=-1)
    id_orden_fk = db.Column(db.String(100), default='')
    fecha_inicio = db.Column(db.DateTime, nullable=True)
    fecha_fin = db.Column(db.DateTime, nullable=True)
    cantidad_solicitada = db.Column(db.Float, default=-1)
    cantidad_despachada = db.Column(db.Float, default=-1)
    cantidad_despachada_unidad = db.Column(db.String(100), default='')
    volumen_natural = db.Column(db.Float, default=-1)
    volumen_neto = db.Column(db.Float, default=-1)
    temperatura_promedio = db.Column(db.Float, default=-1)
    densidad_promedio = db.Column(db.Float, default=-1)
    ctl = db.Column(db.Float, default=-1)
    meter_factor = db.Column(db.Float, default=-1)
    batch = db.Column(db.Text, default='')
    id = db.Column(db.Integer, primary_key=True)
    id_instrumentacion_patin = db.Column(db.Integer, default=-1)
    id_instrumentacion_ucl = db.Column(db.Integer, default=-1)
    factor_de_correccion = db.Column(db.Float, default=-1)
    tipo = db.Column(db.String(100), default='')
    ucl_operador = db.Column(db.String(100), default='')
    host_ip = db.Column(db.String(100), default='')
    totalizador_apertura_fecha = db.Column(db.DateTime, nullable=True)
    totalizador_apertura_natural = db.Column(db.Float, default=-1)
    totalizador_apertura_neto = db.Column(db.Float, default=-1)
    totalizador_cierre_fecha = db.Column(db.DateTime, nullable=True)
    totalizador_cierre_natural = db.Column(db.Float, default=-1)
    totalizador_cierre_neto = db.Column(db.Float, default=-1)
    producto = db.Column(db.String(100), default='')
    id_tanque_fk = db.Column(db.Integer, default=-1)
    numero_de_bol = db.Column(db.Integer, default=-1)

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
            'fecha_inicio': self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            'fecha_fin': self.fecha_fin.isoformat() if self.fecha_fin else None,
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
        return cls.query.all()

    @classmethod
    def get_by_id_orden_fk(cls, id_orden_fk):
        return cls.query(BatchUclCargaDescarga).filter_by(id_orden_fk=id_orden_fk).all()
    
    @classmethod
    def get_by_tipo_and_producto(cls, tipo, producto, fecha_inicio=None, fecha_fin=None):
        filters = []

        """Consulta registros por tipo, producto, y un rango de fechas opcional."""
        if producto != "all":
            filters.append(cls.producto == producto)
            if tipo is not None:
                filters.append(cls.tipo == tipo)
            if fecha_inicio:
                filters.append(cls.date_created >= fecha_inicio)
            if fecha_fin:
                filters.append(cls.date_created <= fecha_fin)
                
            query = db.session.query(cls).filter(*filters).order_by(cls.date_created.desc())
            results = query.all()
            return [result.to_dict() for result in results]
        return None