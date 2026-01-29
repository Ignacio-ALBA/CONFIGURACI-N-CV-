from datetime import datetime, timezone, date
from flask_login import UserMixin
from sqlalchemy import Column, JSON ,Integer, Float, String, Text, DateTime, SmallInteger, ForeignKey, Enum, extract, desc, asc, Double,Boolean
from sqlalchemy.orm import relationship
from config_carpet.config import GlobalConfig, clave_hex_hash
from config_carpet.db_conector import connect_db
import models.scazen_datadb as scaizen_db
import json
import hashlib
import logging
import traceback
import bcrypt

config = GlobalConfig()
Base, SessionLocal, engine = connect_db(config.GET_DATABASE_URL_SCAIZEN_CV())

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

class ControlesVolumetricos(Base):
    __tablename__ = 'controles_volumetricos'

    Id_CV = Column(Integer, primary_key=True, autoincrement=True)
    Version = Column(Integer, nullable=False)
    RfcContribuyente = Column(String(45), nullable=False)
    RfcRepresentanteLegal = Column(String(45), nullable=True)
    RfcProveedor = Column(String(45), nullable=False)
    RfcProveedores = Column(String(45), nullable=True)
    TipoCaracter = Column(String(45), nullable=False)
    ModalidadPermiso = Column(String(45), nullable=True)
    NumPermiso = Column(String(45), nullable=True)
    NumContratoOAsignacion = Column(String(45), nullable=True)
    InstalacionAlmacenGasNatural = Column(String(45), nullable=True)
    ClaveInstalacion = Column(String(45), nullable=False)
    DescripcionInstalacion = Column(String(150), nullable=False)
    GeolocalizacionLatitud = Column(Float, nullable=True)
    GeolocalizacionLongitud = Column(Float, nullable=True)
    NumeroPozos = Column(Integer, nullable=False)
    NumeroTanques = Column(Integer, nullable=False)
    NumeroDuctosEntradaSalida = Column(Integer, nullable=False)
    NumeroDuctosTransporteDistribucion = Column(Integer, nullable=False)
    NumeroDispensarios = Column(Integer, nullable=False)
    Tipo = Column(String(50), nullable=False)

    def __repr__(self):
        return (f"<ControlesVolumetricos(Id_CV={self.Id_CV}, RfcContribuyente={self.RfcContribuyente}, ClaveInstalacion={self.ClaveInstalacion}, ")
    """
    @classmethod
    def add(cls, version, rfc_contribuyente, rfc_representante_legal, rfc_proveedor, rfc_proveedores,
            tipo_caracter, modalidad_permiso, num_permiso, num_contrato_o_asignacion, instalacion_almacen_gas_natural,
            clave_instalacion, descripcion_instalacion, geolocalizacion_latitud, geolocalizacion_longitud,
            numero_pozos, numero_tanques, numero_ductos_entrada_salida, numero_dispensarios, fecha_y_hora_corte):
        nuevo_control = cls(
            Version=version,
            RfcContribuyente=rfc_contribuyente,
            RfcRepresentanteLegal=rfc_representante_legal,
            RfcProveedor=rfc_proveedor,
            RfcProveedores=rfc_proveedores,
            TipoCaracter=tipo_caracter,
            ModalidadPermiso=modalidad_permiso,
            NumPermiso=num_permiso,
            NumContratoOAsignacion=num_contrato_o_asignacion,
            InstalacionAlmacenGasNatural=instalacion_almacen_gas_natural,
            ClaveInstalacion=clave_instalacion,
            DescripcionInstalacion=descripcion_instalacion,
            GeolocalizacionLatitud=geolocalizacion_latitud,
            GeolocalizacionLongitud=geolocalizacion_longitud,
            NumeroPozos=numero_pozos,
            NumeroTanques=numero_tanques,
            NumeroDuctosEntradaSalida=numero_ductos_entrada_salida,
            NumeroDispensarios=numero_dispensarios,
            FechaYHoraCorte=fecha_y_hora_corte,
          
        )

        
        result_data = add_to_table(nuevo_control)
        return result_data if result_data else None
        """
    @classmethod
    def add(cls, version, rfc_contribuyente, rfc_representante_legal, rfc_proveedor, rfc_proveedores,
            tipo_caracter, modalidad_permiso, num_permiso, num_contrato_o_asignacion, instalacion_almacen_gas_natural,
            clave_instalacion, descripcion_instalacion, geolocalizacion_latitud, geolocalizacion_longitud,
            numero_pozos, numero_tanques, numero_ductos_entrada_salida,numero_ductos_transporte_distribucion, numero_dispensarios, tipo=None):
        nuevo_control = cls(

            Version=version,
            RfcContribuyente=rfc_contribuyente,
            RfcRepresentanteLegal=rfc_representante_legal,
            RfcProveedor=rfc_proveedor,
            RfcProveedores=rfc_proveedores,
            TipoCaracter=tipo_caracter,
            ModalidadPermiso=modalidad_permiso,
            NumPermiso=num_permiso,
            NumContratoOAsignacion=num_contrato_o_asignacion,
            InstalacionAlmacenGasNatural=instalacion_almacen_gas_natural,
            ClaveInstalacion=clave_instalacion,
            DescripcionInstalacion=descripcion_instalacion,
            GeolocalizacionLatitud=geolocalizacion_latitud,
            GeolocalizacionLongitud=geolocalizacion_longitud,
            NumeroPozos=numero_pozos,
            NumeroTanques=numero_tanques,
            NumeroDuctosEntradaSalida=numero_ductos_entrada_salida,
            NumeroDuctosTransporteDistribucion = numero_ductos_transporte_distribucion,
            NumeroDispensarios=numero_dispensarios,
            Tipo =tipo
        )

        
        result_data = add_to_table(nuevo_control)
        return result_data if result_data else None

    @classmethod
    def delete(cls, id):
        session = SessionLocal()
        try:
            record = session.query(cls).filter_by(Id_CV=id).first()  # Filtro correcto
            if not record:
                return False  # No existe el registro

            session.delete(record)
            session.commit()
            return True  # Eliminación exitosa

        except Exception as e:
            session.rollback()
            logging.error(f"Error al eliminar el registro Id_CV={id}: {e}")
            return False

        finally:
            session.close()



    @classmethod
    def select_by_id(cls, id_cv):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id_CV=id_cv).first()
        session.close()
        return consulta

    

    @classmethod
    def select_all(cls):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta

    @classmethod
    def select_type(cls, tipo):
        session = SessionLocal()
        try:
            consulta = session.query(cls).filter_by(Tipo=tipo).all()  # Ejecuta la query
        finally:
            session.close()  # Cierra la sesión después de obtener los datos
        return consulta
    
class CvProductoBitacoraBitacoraMensual(Base):
    __tablename__ = 'cv_producto_bitacora_bitacoramensual'

    id = Column(Integer, primary_key=True, autoincrement=True)
    Id_CV_fk = Column(Integer, ForeignKey('controles_volumetricos.Id_CV'), nullable=False)  # Ajusta 'cv_table' al nombre correcto de la tabla relacionada.
    Id_PRODUCTO_fk  = Column(Integer, ForeignKey('producto.Id_PRODUCTO'), nullable=False)  # Ajusta 'producto' al nombre correcto de la tabla relacionada.
    Id_BITACORA_fk = Column(Integer, ForeignKey('bitacora.Id_BITACORA'), nullable=True)  # Ajusta 'bitacora' al nombre correcto de la tabla relacionada.
    Id_BITACORAMENSUAL_fk = Column(Integer, ForeignKey('bitacoramensual.Id_BITACORAMENSUAL'), nullable=True)  # Ajusta 'bitacoramensual' al nombre correcto de la tabla relacionada.
    def __repr__(self):
        return (f"<CvProductoBitacoraBitacoraMensual(id={self.id}, id_cv_fk={self.Id_CV_fk}, "
                f"id_producto_fk={self.Id_PRODUCTO_fk}, id_bitacora_fk={self.Id_BITACORA_fk}, "
                f"id_bitacoramensual_fk={self.Id_BITACORAMENSUAL_fk})>")

    @classmethod
    def add(cls, id_cv_fk, id_producto_fk, id_bitacora_fk=None, id_bitacoramensual_fk=None):
        nuevo_registro = cls(
            Id_CV_fk=id_cv_fk,
            Id_PRODUCTO_fk=id_producto_fk,
            Id_BITACORA_fk=id_bitacora_fk,
            Id_BITACORAMENSUAL_fk=id_bitacoramensual_fk
        )
        result_data = add_to_table(nuevo_registro)
        return result_data if result_data else None

    @classmethod
    def select_by_id(cls, id):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).filter_by(id=id).first()
        session.close()
        return consulta
    
    @classmethod
    def select_by_id_cv_fk(cls, id_cv_fk):
        session = SessionLocal()
        consulta = None
        consulta = session.query(cls).filter_by(Id_CV_fk=id_cv_fk).all()
        session.close()
        return consulta

    @classmethod
    def select_by_id_cv_producto(cls, id_PRODUCTO_fk):
        session = SessionLocal()
        consulta = None
        consulta = session.query(cls).filter_by(Id_PRODUCTO_fk=id_PRODUCTO_fk).all()
        session.close()
        return consulta


    @classmethod
    def select_all(cls):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).all()
        return consulta

class Bitacora(Base):
    __tablename__ = 'bitacora'

    Id_BITACORA = Column(Integer, primary_key=True, autoincrement=True)
    NumeroRegistro = Column(Integer, nullable=False)
    FechaYHoraEvento = Column(DateTime, nullable=False)
    UsuarioResponsable = Column(Integer, nullable=True)
    TipoEvento = Column(String(45), nullable=False)
    DescripcionEvento = Column(Integer, nullable=False)
    IdentificacionComponenteAlarma = Column(String(45), nullable=True)

    def __repr__(self):
        return f"<Bitacora(Id_BITACORA={self.Id_BITACORA}, NumeroRegistro={self.NumeroRegistro}, FechaYHoraEvento={self.FechaYHoraEvento}, TipoEvento={self.TipoEvento})>"

    @classmethod
    def add(cls, numero_registro, fecha_hora_evento, usuario_responsable, tipo_evento, descripcion_evento, identificacion_componente_alarma=None):
        nuevo_evento = cls(
            NumeroRegistro=numero_registro,
            FechaYHoraEvento=fecha_hora_evento,
            UsuarioResponsable=usuario_responsable,
            TipoEvento=tipo_evento,
            DescripcionEvento=descripcion_evento,
            IdentificacionComponenteAlarma=identificacion_componente_alarma
        )
        result_data = add_to_table(nuevo_evento)
        return result_data if result_data else None

    @classmethod
    def select_by_id(cls, id_bitacora):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id_BITACORA=id_bitacora).first()
        session.close()
        return consulta

    @classmethod
    def select_all(cls):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta


    @classmethod
    def get_by_tipo_by_date(cls, tipo_evento, fecha_inicio, fecha_fin):
        filters = []
        
        # Agrega los filtros obligatorios
        filters.append(cls.TipoEvento == tipo_evento)

        # Agrega los filtros opcionales de fecha
        if fecha_inicio:
            filters.append(cls.FechaYHoraEvento >= fecha_inicio,)
        if fecha_fin:
            filters.append(cls.FechaYHoraEvento <= fecha_fin)

        try:
            consulta = None
            session = SessionLocal()
            consulta = session.query(cls).filter(*filters).all()
            session.close()
            return consulta
        except Exception as e:
            print(f"Error al consultar por tipo y producto: {e}")
            return []
        
class BitacoraMensual(Base):
    __tablename__ = 'bitacoramensual'

    Id_BITACORAMENSUAL = Column(Integer, primary_key=True, autoincrement=True)
    NumeroRegistro = Column(Integer, nullable=False)
    FechaYHoraEvento = Column(DateTime, nullable=False)
    UsuarioResponsable = Column(Integer, nullable=True)
    TipoEvento = Column(String(45), nullable=False)
    DescripcionEvento = Column(Integer, nullable=True)
    IdentificacionComponenteAlarma = Column(String(45), nullable=True)

    def __repr__(self):
        return (f"<BitacoraMensual(Id_BITACORAMENSUAL={self.Id_BITACORAMENSUAL}, "
                f"NumeroRegistro={self.NumeroRegistro}, FechaYHoraEvento={self.FechaYHoraEvento}, "
                f"TipoEvento={self.TipoEvento})>")

    @classmethod
    def add(cls, numero_registro, fecha_hora_evento, usuario_responsable, tipo_evento, descripcion_evento=None, identificacion_componente_alarma=None):
        nuevo_evento = cls(
            NumeroRegistro=numero_registro,
            FechaYHoraEvento=fecha_hora_evento,
            UsuarioResponsable=usuario_responsable,
            TipoEvento=tipo_evento,
            DescripcionEvento=descripcion_evento,
            IdentificacionComponenteAlarma=identificacion_componente_alarma
        )
        result_data = add_to_table(nuevo_evento)
        return result_data if result_data else None

    @classmethod
    def select_by_id(cls, id_bitacoramensual):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id_BITACORAMENSUAL=id_bitacoramensual).first()
        session.close()
        return consulta

    @classmethod
    def select_all(cls):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta

class Producto(Base):
    __tablename__ = 'producto'

    Id_PRODUCTO = Column(Integer, primary_key=True, autoincrement=True)
    ClaveProducto = Column(String(4), nullable=True)
    ClaveSubProducto = Column(String(4), nullable=False)
    ComposOctanajeGasolina = Column(Integer, nullable=True)
    GasolinaConCombustibleNoFosil = Column(String(5), default='Sí')
    ComposDeCombustibleNoFosilEnGasolina = Column(Integer, nullable=True)
    DieselConCombustibleNoFosil = Column(Enum('Sí', 'No'), default='Sí')
    ComposDeCombustibleNoFosilEnDiesel = Column(Integer, nullable=True)
    TurbosinaConCombustibleNoFosil = Column(Enum('Sí', 'No'), default='Sí')
    ComposDeCombustibleNoFosilEnTurbosina = Column(Integer, nullable=True)
    ComposDePropanoEnGasLP = Column(Float, nullable=True)
    ComposDeButanoEnGasLp = Column(Float, nullable=True)
    DensidadDePetroleo = Column(Float, nullable=True)
    ComposDeAzufreEnPetroleo = Column(Float, nullable=True)
    Otros = Column(String(45), nullable=True)
    MarcaComercial = Column(String(150), nullable=True)
    Marcaje = Column(String(150), nullable=False)
    ConcentracionSustanciasMarcaje = Column(Integer, nullable=False)
    nombre_producto = Column(String(30), nullable=False)
    UnidadDeMedida = Column(String(6), nullable=False)

    def __repr__(self):
        return (f"<Producto(Id_PRODUCTO={self.Id_PRODUCTO}, ClaveProducto={self.ClaveProducto}, "
                f"ClaveSubProducto={self.ClaveSubProducto}>")

    @classmethod
    def add(cls, clave_producto, clave_sub_producto, compos_octanaje_gasolina, 
            gasolina_con_combustible_no_fosil, compos_de_combustible_no_fosil_en_gasolina, 
            diesel_con_combustible_no_fosil, compos_de_combustible_no_fosil_en_diesel, 
            turbosina_con_combustible_no_fosil, compos_de_combustible_no_fosil_en_turbosina, 
            compos_de_propano_en_gas_lp, compos_de_butano_en_gas_lp, densidad_de_petroleo, 
            compos_de_azufre_en_petroleo, otros, marca_comercial, marcaje, 
            concentracion_sustancias_marcaje, tanque, reporte_de_volumen_mensual):
        nuevo_producto = cls(
            ClaveProducto=clave_producto,
            ClaveSubProducto=clave_sub_producto,
            ComposOctanajeGasolina=compos_octanaje_gasolina,
            GasolinaConCombustibleNoFosil=gasolina_con_combustible_no_fosil,
            ComposDeCombustibleNoFosilEnGasolina=compos_de_combustible_no_fosil_en_gasolina,
            DieselConCombustibleNoFosil=diesel_con_combustible_no_fosil,
            ComposDeCombustibleNoFosilEnDiesel=compos_de_combustible_no_fosil_en_diesel,
            TurbosinaConCombustibleNoFosil=turbosina_con_combustible_no_fosil,
            ComposDeCombustibleNoFosilEnTurbosina=compos_de_combustible_no_fosil_en_turbosina,
            ComposDePropanoEnGasLP=compos_de_propano_en_gas_lp,
            ComposDeButanoEnGasLp=compos_de_butano_en_gas_lp,
            DensidadDePetroleo=densidad_de_petroleo,
            ComposDeAzufreEnPetroleo=compos_de_azufre_en_petroleo,
            Otros=otros,
            MarcaComercial=marca_comercial,
            Marcaje=marcaje,
            ConcentracionSustanciasMarcaje=concentracion_sustancias_marcaje,
            TANQUE=tanque,
            REPORTEDEVOLUMENMENSUAL=reporte_de_volumen_mensual
        )
        result_data = add_to_table(nuevo_producto)
        return result_data if result_data else None
    @classmethod
    def select_by_id(cls, id_producto):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id_PRODUCTO=id_producto).first()
        session.close()
        return consulta

    @classmethod
    def select_all(cls):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta

class ProductoGasNatural(Base):
    __tablename__ = 'producto_gasnatural'

    Id = Column(Integer, primary_key=True, autoincrement=True)
    Id_PRODUCTO_fk = Column(Integer,ForeignKey('producto.Id_PRODUCTO'), nullable=False)
    Id_GasNatural_fk = Column(Integer,ForeignKey('gasnatural.id_GASNATURAL'), nullable=False)

    def __repr__(self):
        return (f"<ProductoGasNatural(Id={self.Id}, Id_PRODUCTO_fk={self.Id_PRODUCTO_fk}, "
                f"Id_GasNatural_fk={self.Id_GasNatural_fk})>")

    @classmethod
    def add(cls, id_producto_fk, id_gas_natural_fk):
        nuevo_producto_gas_natural = cls(
            Id_PRODUCTO_fk=id_producto_fk,
            Id_GasNatural_fk=id_gas_natural_fk
        )
        result_data = add_to_table(nuevo_producto_gas_natural)
        return result_data if result_data else None

    @classmethod
    def select_by_id(cls, id):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id=id).first()
        session.close()
        return consulta

    @classmethod
    def select_all(cls):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta

class GasNatural(Base):
    __tablename__ = 'gasnatural'

    id_GASNATURAL = Column(Integer, primary_key=True, autoincrement=True)
    ComposGasNaturalOCondensados = Column(String(45), nullable=False)
    FraccionMolar = Column(Float, nullable=False)
    PoderCalorifico = Column(Integer, nullable=False)
    
    def __repr__(self):
        return (f"<GasNatural(id_GASNATURAL={self.id_GASNATURAL}>")

    @classmethod
    def add(cls, compos_gas_natural_o_condensados, fraccion_molar, poder_calorifico):
        nuevo_gas_natural = cls(
            ComposGasNaturalOCondensados=compos_gas_natural_o_condensados,
            FraccionMolar=fraccion_molar,
            PoderCalorifico=poder_calorifico
        )
        result_data = add_to_table(nuevo_gas_natural)
        return result_data if result_data else None

    @classmethod
    def select_by_id(cls, id_gasnatural):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).filter_by(id_GASNATURAL=id_gasnatural).first()
        session.close()
        return consulta

    @classmethod
    def select_all(cls):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta    

class ProductoTanqueReporteDeVolumenMensual(Base):
    __tablename__ = 'producto_tanque_reportedevolumenmensual'

    Id = Column(Integer, primary_key=True, autoincrement=True)
    Id_PRODUCTO_fk = Column(Integer, nullable=False)
    Id_CV_fk = Column(Integer, ForeignKey('controles_volumetricos.Id_CV'),nullable=False)
    Id_TANQUE_EXISTENCIAS_RECEPCIONES_ENTREGAS_fk  = Column(Integer, 
        ForeignKey('tanque_existencias_recepciones_entregas.Id_TANQUE_EXISTENCIAS_RECEPCIONES_ENTREGAS'),nullable=True)
    Id_REPORTEVOLUMENMENSUAL_RECEPCIONES_M_ENTREGAS_M_fk = Column(Integer, 
        ForeignKey('reportevolumenmensual_recepciones_m_entregas_m.Id_REPORTEVOLUMENMENSUAL_RECEPCIONES_M_ENTREGAS_M'),nullable=True)
    FECHA = Column(DateTime, nullable=False)
    TIPO_REPORTE = Column(String(45), nullable=False)

    def __repr__(self):
        return (f"<ProductoTanqueReporteDeVolumenMensual(Id={self.Id}, "
                f"Id_PRODUCTO_fk={self.Id_PRODUCTO_fk}, FECHA={self.FECHA}, "
                f"TIPO_REPORTE={self.TIPO_REPORTE})>")

    @classmethod
    def add(cls, id_producto_fk, id_tanque_fk, id_reporte_fk, fecha, tipo_reporte):
        nuevo_reporte = cls(
            Id_PRODUCTO_fk=id_producto_fk,
            Id_TANQUE_EXISTENCIAS_RECEPCIONES_ENTREGAS_fk =id_tanque_fk,
            Id_REPORTEVOLUMENMENSUAL_RECEPCIONES_M_ENTREGAS_M_fk=id_reporte_fk,
            FECHA=fecha,
            TIPO_REPORTE=tipo_reporte
        )
        result_data = add_to_table(nuevo_reporte)
        return result_data if result_data else None

    @classmethod
    def add_mensual_report(cls,id_cv_fk, id_producto_fk, id_reporte_fk,fecha=None):
        if fecha is None:
            fecha = datetime.now()
        id_tanque_fk=None
        tipo_reporte="Mensual"
        nuevo_reporte = cls(
            Id_CV_fk = id_cv_fk,
            Id_PRODUCTO_fk=id_producto_fk,
            Id_TANQUE_EXISTENCIAS_RECEPCIONES_ENTREGAS_fk =id_tanque_fk,
            Id_REPORTEVOLUMENMENSUAL_RECEPCIONES_M_ENTREGAS_M_fk=id_reporte_fk,
            FECHA=fecha,
            TIPO_REPORTE=tipo_reporte
        )
        result_data = add_to_table(nuevo_reporte)
        return result_data if result_data else None

    @classmethod
    def add_day_report(cls,id_cv_fk, id_producto_fk, id_tanque_fk,fecha=None):
        if fecha is None:
            fecha = datetime.now()
        id_reporte_fk=None
        tipo_reporte="Diario"
        nuevo_reporte = cls(
            Id_CV_fk = id_cv_fk,
            Id_PRODUCTO_fk=id_producto_fk,
            Id_TANQUE_EXISTENCIAS_RECEPCIONES_ENTREGAS_fk =id_tanque_fk,
            Id_REPORTEVOLUMENMENSUAL_RECEPCIONES_M_ENTREGAS_M_fk=id_reporte_fk,
            FECHA=fecha,
            TIPO_REPORTE=tipo_reporte
        )
        result_data = add_to_table(nuevo_reporte)
        return result_data if result_data else None

    @classmethod
    def select_by_id(cls, id):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id=id).first()
        session.close()
        return consulta    

    @classmethod
    def select_all(cls):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta
    
    @classmethod
    def select_for_report_mensual(cls, month, year,cv_id):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).filter(
                extract('month', cls.FECHA) == month,
                extract('year', cls.FECHA) == year,
                cls.TIPO_REPORTE == 'Mensual',
                cls.Id_CV_fk ==cv_id
            ).all()
        session.close()
        return consulta
    
    @classmethod
    def select_by_product_for_report_mensual(cls, Id_PRODUCTO_fk, month, year,cv_id):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).filter(
                cls.Id_PRODUCTO_fk == Id_PRODUCTO_fk,
                extract('month', cls.FECHA) == month,
                extract('year', cls.FECHA) == year,
                cls.TIPO_REPORTE == 'Mensual',
                cls.Id_CV_fk ==cv_id
            ).all()
        session.close()
        return consulta
    
    @classmethod
    def select_for_report_daily(cls, date, cv_id):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).filter( cls.FECHA == date, cls.TIPO_REPORTE == 'Diario', cls.Id_CV_fk ==cv_id).all()
        session.close()
        return consulta
    
class ReporteVolumenMensualRecepcionesMEntregasM(Base):
    __tablename__ = 'reportevolumenmensual_recepciones_m_entregas_m'

    Id_REPORTEVOLUMENMENSUAL_RECEPCIONES_M_ENTREGAS_M = Column(Integer, primary_key=True, autoincrement=True)
    Id_REPORTEDEVOLUMENMENSUAL_fk = Column(Integer, ForeignKey('reportedevolumenmensual.Id_REPORTEDEVOLUMENMENSUAL'),nullable=False)
    Id_RECEPCIONES_M_fk = Column(Integer, ForeignKey('recepciones_m.Id_RECEPCIONES_M'),nullable=False)
    Id_ENTREGAS_M_fk = Column(Integer, ForeignKey('entregas_m.Id_ENTREGAS_M'),nullable=False)

    def __repr__(self):
        return (f"<ReporteVolumenMensualRecepcionesMEntregasM(Id={self.Id_REPORTEVOLUMENMENSUAL_RECEPCIONES_M_ENTREGAS_M}>")

    @classmethod
    def add(cls, id_reporte_volumen_mensual_fk, id_recepciones_m_fk, id_entregas_m_fk):
        nuevo_reporte = cls(
            Id_REPORTEDEVOLUMENMENSUAL_fk=id_reporte_volumen_mensual_fk,
            Id_RECEPCIONES_M_fk=id_recepciones_m_fk,
            Id_ENTREGAS_M_fk=id_entregas_m_fk
        )
        result_data = add_to_table(nuevo_reporte)
        return result_data.Id_REPORTEVOLUMENMENSUAL_RECEPCIONES_M_ENTREGAS_M if result_data else None

    @classmethod
    def select_by_id(cls, id):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id_REPORTEVOLUMENMENSUAL_RECEPCIONES_M_ENTREGAS_M =id).first()
        session.close()
        return consulta

    @classmethod
    def select_all(cls):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta

class EntregasMes(Base):
    __tablename__ = 'entregas_m'

    Id_ENTREGAS_M = Column(Integer, primary_key=True, autoincrement=True)
    TotalEntregasMes = Column(Integer, nullable=False)
    SumaVolumenEntregadoMes = Column(Integer, nullable=False)
    SumaVolumenEntregadoMes_UM = Column(String(45), nullable=False)
    PoderCalorifico = Column(Integer, nullable=False)
    PoderCalorifico_UM = Column(String(45), nullable=False)
    TotalDocumentosMes = Column(Integer, nullable=False)
    ImporteTotalRecepcionesMensual = Column(Float, nullable=False)
    Complemento = Column(Integer, nullable=False)

    def __repr__(self):
        return (f"<EntregasM(Id_ENTREGAS_M={self.Id_ENTREGAS_M}>")

    @classmethod
    def add(cls, total_entregas_mes, suma_volumen_entregado_mes, suma_volumen_entregado_mes_um, 
            total_documentos_mes, importe_total_recepciones_mensual,poder_calorifico = -1, poder_calorifico_um="", complemento=-1):
        nuevo_entregas_m = cls(
            TotalEntregasMes=total_entregas_mes,
            SumaVolumenEntregadoMes=suma_volumen_entregado_mes,
            SumaVolumenEntregadoMes_UM=suma_volumen_entregado_mes_um,
            PoderCalorifico=poder_calorifico,
            PoderCalorifico_UM=poder_calorifico_um,
            TotalDocumentosMes=total_documentos_mes,
            ImporteTotalRecepcionesMensual=importe_total_recepciones_mensual,
            Complemento=complemento
        )
        result_data = add_to_table(nuevo_entregas_m)
        return result_data.Id_ENTREGAS_M if result_data else None


    @classmethod
    def select_by_id(cls, id_entregas_m):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id_ENTREGAS_M=id_entregas_m).first()
        session.close()
        return consulta

    @classmethod
    def select_all(cls):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta

class RecepcionesMes(Base):
    __tablename__ = 'recepciones_m'

    Id_RECEPCIONES_M = Column(Integer, primary_key=True, autoincrement=True)
    TotalRecepcionesMes = Column(Integer, nullable=False)
    SumaVolumenRecepcionesMes = Column(Integer, nullable=False)
    SumaVolumenRecepcionesMes_UM = Column(String(45), nullable=False)
    PoderCalorifico = Column(Integer, nullable=False)
    PoderCalorifico_UM = Column(String(45), nullable=False)
    TotalDocumentosMes = Column(Integer, nullable=False)
    ImporteTotalRecepcionesMensual = Column(Float, nullable=False)
    Complemento = Column(Integer, nullable=False)

    def __repr__(self):
        return (f"<RecepcionesMes(Id_RECEPCIONES_M={self.Id_RECEPCIONES_M}>")

    @classmethod
    def add(cls, total_recepciones_mes, suma_volumen_recepciones_mes, suma_volumen_recepciones_mes_um,
            total_documentos_mes, importe_total_recepciones_mensual, poder_calorifico = -1, poder_calorifico_um = "", complemento = -1):
        nueva_recepcion_mes = cls(
            TotalRecepcionesMes=total_recepciones_mes,
            SumaVolumenRecepcionesMes=suma_volumen_recepciones_mes,
            SumaVolumenRecepcionesMes_UM=suma_volumen_recepciones_mes_um,
            PoderCalorifico=poder_calorifico,
            PoderCalorifico_UM=poder_calorifico_um,
            TotalDocumentosMes=total_documentos_mes,
            ImporteTotalRecepcionesMensual=importe_total_recepciones_mensual,
            Complemento=complemento
        )
        result_data = add_to_table(nueva_recepcion_mes)
        return result_data.Id_RECEPCIONES_M if result_data else None

    @classmethod
    def select_by_id(cls, id_recepciones_m):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id_RECEPCIONES_M=id_recepciones_m).first()
        session.close()
        return consulta

    @classmethod
    def select_all(cls):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta

class ReporteDeVolumenMensual(Base):
    __tablename__ = 'reportedevolumenmensual'

    Id_REPORTEDEVOLUMENMENSUAL = Column(Integer, primary_key=True, autoincrement=True)
    CONTROLDEEXISTENCIAS_VolumenExistenciasMes = Column(Float, nullable=False)
    CONTROLDEEXISTENCIAS_VolumenExistenciasMes_UM = Column(String(45), nullable=False)
    CONTROLDEEXISTENCIAS_FechaYHoraEstaMedicionMes = Column(DateTime, nullable=False)

    def __repr__(self):
        return (f"<ReporteDeVolumenMensual(Id_REPORTEDEVOLUMENMENSUAL={self.Id_REPORTEDEVOLUMENMENSUAL}, "
                f"VolumenExistenciasMes={self.CONTROLDEEXISTENCIAS_VolumenExistenciasMes}, "
                f"FechaYHoraEstaMedicionMes={self.CONTROLDEEXISTENCIAS_FechaYHoraEstaMedicionMes})>")

    @classmethod
    def add(cls, volumen_existencias_mes, volumen_existencias_mes_um, fecha_y_hora_esta_medicion_mes):
        nuevo_reporte = cls(
            CONTROLDEEXISTENCIAS_VolumenExistenciasMes=volumen_existencias_mes,
            CONTROLDEEXISTENCIAS_VolumenExistenciasMes_UM=volumen_existencias_mes_um,
            CONTROLDEEXISTENCIAS_FechaYHoraEstaMedicionMes=fecha_y_hora_esta_medicion_mes
        )
        result_data = add_to_table(nuevo_reporte)
        return result_data.Id_REPORTEDEVOLUMENMENSUAL if result_data else None

    @classmethod
    def select_by_id(cls, id_reporte):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id_REPORTEDEVOLUMENMENSUAL=id_reporte).first()
        session.close()
        return consulta

    @classmethod
    def select_all(cls):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta

class TanqueExistenciasRecepcionesEntregas(Base):
    __tablename__ = 'tanque_existencias_recepciones_entregas'
    Id_TANQUE_EXISTENCIAS_RECEPCIONES_ENTREGAS = Column(Integer, primary_key=True, autoincrement=True)
    Id_TANQUE_fk = Column(Integer, ForeignKey('tanque.Id_TANQUE'),nullable=False)
    Id_EXISTENCIAS_fk = Column(Integer, ForeignKey('existencias.Id_EXISTENCIAS'),nullable=True)
    Id_RECEPCIONES_fk = Column(Integer, ForeignKey('recepciones.Id_RECEPCIONES'), nullable=False)
    Id_ENTREGAS_fk = Column(Integer, ForeignKey('entregas.Id_ENTREGAS'), nullable=False)

    def __repr__(self):
        return (f"<TanqueExistenciasRecepcionesEntregas(Id={self.Id_TANQUE_EXISTENCIAS_RECEPCIONES_ENTREGAS}, "
                f"Id_TANQUE_fk={self.Id_TANQUE_fk}, Id_MedicionTanque_fk={self.Id_MedicionTanque_fk})>")

    @classmethod
    def add(cls, id_tanque, id_existencias=None, id_recepcion=None, id_entrega=None):
        nuevo_registro = cls(
            Id_TANQUE_fk=id_tanque,
            Id_EXISTENCIAS_fk=id_existencias,
            Id_RECEPCIONES_fk=id_recepcion,
            Id_ENTREGAS_fk=id_entrega
        )
        result_data = add_to_table(nuevo_registro)
        return result_data.Id_TANQUE_EXISTENCIAS_RECEPCIONES_ENTREGAS if result_data else None

    @classmethod
    def select_by_id(cls, id):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id_TANQUE_EXISTENCIAS_RECEPCIONES_ENTREGAS=id).first()
        session.close()
        return consulta


    @classmethod
    def select_all(cls):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta

#Eliminar en siguientes actualizaciones
class EntregasEntrega(Base):
    __tablename__ = 'entregas_entrega'

    Id_ENTREGAS_ENTREGA = Column(Integer, primary_key=True, autoincrement=True)
    Id_ENTREGAS_fk = Column(Integer, ForeignKey('entregas.Id_ENTREGAS'), nullable=False)
    Id_ENTREGA_fk = Column(Integer, ForeignKey('entrega.Id_ENTREGA'), nullable=True)


    def __repr__(self):
        return (f"<EntregasEntrega(id={self.id}, Id_ENTREGAS_fk={self.Id_ENTREGAS_fk}, "
                f"Id_ENTREGA_fk={self.Id_ENTREGA_fk})>")

    @classmethod
    def add(cls, id_entregas_fk, id_entrega_fk=None):
        nueva_entrega_entrega = cls(
            Id_ENTREGAS_fk=id_entregas_fk,
            Id_ENTREGA_fk=id_entrega_fk
        )
        result_data = add_to_table(nueva_entrega_entrega)
        return result_data if result_data else None

    @classmethod
    def select_by_id(cls, id):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).filter_by(id=id).first()
        session.close()
        return consulta


    @classmethod
    def select_all(cls):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta

#Eliminar en siguientes actualizaciones
class RecepcionesRecepcion(Base):
    __tablename__ = 'recepciones_recepcion'

    Id_RECEPCIONES_RECEPCION = Column(Integer, primary_key=True, autoincrement=True)
    Id_RECEPCIONES_fk = Column(Integer, ForeignKey('recepciones.Id_RECEPCIONES'), nullable=False)
    Id_RECEPCION_fk = Column(Integer, ForeignKey('recepcion.Id_RECEPCION'), nullable=False)

    def __repr__(self):
        return (f"<RecepcionesRecepcion(Id={self.Id}, Id_RECEPCIONES_fk={self.Id_RECEPCIONES_fk}, "
                f"Id_RECEPCION_fk={self.Id_RECEPCION_fk})>")

    @classmethod
    def add(cls, id_recepciones_fk, id_recepcion_fk):
        nueva_recepcion_recepcion = cls(
            Id_RECEPCIONES_fk=id_recepciones_fk,
            Id_RECEPCION_fk=id_recepcion_fk
        )
        result_data = add_to_table(nueva_recepcion_recepcion)
        return result_data if result_data else None

    @classmethod
    def select_by_id(cls, id):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id=id).first()
        session.close()
        return consulta


    @classmethod
    def select_all(cls):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta

class Existencias(Base):
    __tablename__ = 'existencias'

    Id_EXISTENCIAS = Column(Integer, primary_key=True, autoincrement=True)
    VolumenExistenciasAnterior = Column(Float, nullable=False)
    VolumenAcumOpsRecepcion = Column(Float, nullable=False)
    VolumenAcumOpsRecepcion_UM = Column(String(10), nullable=False)
    HoraRecepcionAcumulado = Column(DateTime, nullable=False)
    VolumenAcumOpsEntrega = Column(Float, nullable=False)
    VolumenAcumOpsEntrega_UM = Column(String(10), nullable=False)
    HoraEntregaAcumulado = Column(DateTime, nullable=False)
    VolumenExistencias = Column(Float, nullable=False)
    FechaYHoraEstaEdicion = Column(DateTime, nullable=False)
    FechaYHoraEdicionAnterior = Column(DateTime, nullable=False)

    def __repr__(self):
        return (f"<Existencias(Id_EXISTENCIAS={self.Id_EXISTENCIAS}>")

    @classmethod
    def add(cls, volumen_existencias_anterior, volumen_acum_ops_recepcion, 
            volumen_acum_ops_recepcion_um, hora_recepcion_acumulado, volumen_acum_ops_entrega, 
            volumen_acum_ops_entrega_um, hora_entrega_acumulado, volumen_existencias, 
            fecha_y_hora_esta_edicion, fecha_y_hora_edicion_anterior):
        nueva_existencia = cls(
            VolumenExistenciasAnterior=volumen_existencias_anterior,
            VolumenAcumOpsRecepcion=volumen_acum_ops_recepcion,
            VolumenAcumOpsRecepcion_UM=volumen_acum_ops_recepcion_um,
            HoraRecepcionAcumulado=hora_recepcion_acumulado,
            VolumenAcumOpsEntrega=volumen_acum_ops_entrega,
            VolumenAcumOpsEntrega_UM=volumen_acum_ops_entrega_um,
            HoraEntregaAcumulado=hora_entrega_acumulado,
            VolumenExistencias=volumen_existencias,
            FechaYHoraEstaEdicion=fecha_y_hora_esta_edicion,
            FechaYHoraEdicionAnterior=fecha_y_hora_edicion_anterior
        )
        result_data = add_to_table(nueva_existencia)
        return result_data.Id_EXISTENCIAS if result_data else None

    @classmethod
    def select_by_id(cls, id_existencias):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id_EXISTENCIAS=id_existencias).first()
        session.close()
        return consulta

    @classmethod
    def select_all(cls):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta

class MedicionTanque(Base):
    __tablename__ = 'mediciontanque'

    Id_MedicionTanque = Column(Integer, primary_key=True, autoincrement=True)
    SistemaMedicionTanque = Column(String(45), nullable=False)
    LocalizODescripSistMedicionTanque = Column(String(150), nullable=False)
    VigenciaCalibracionSistMedicionTanque = Column(DateTime, nullable=False)
    IncertidumbreMedicionSistMedicionTanque = Column(Float, nullable=False)

    def __repr__(self):
        return (f"<MedicionTanque(Id_MedicionTanque={self.Id_MedicionTanque}>")

    @classmethod
    def add(cls, sistema_medicion_tanque, localiz_o_descrip_sist_medicion_tanque, 
            vigencia_calibracion_sist_medicion_tanque, incertidumbre_medicion_sist_medicion_tanque):
        nueva_medicion_tanque = cls(
            SistemaMedicionTanque=sistema_medicion_tanque,
            LocalizODescripSistMedicionTanque=localiz_o_descrip_sist_medicion_tanque,
            VigenciaCalibracionSistMedicionTanque=vigencia_calibracion_sist_medicion_tanque,
            IncertidumbreMedicionSistMedicionTanque=incertidumbre_medicion_sist_medicion_tanque
        )
        result_data = add_to_table(nueva_medicion_tanque)
        return result_data if result_data else None

    @classmethod
    def select_by_id(cls, id_medicion_tanque):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id_MedicionTanque=id_medicion_tanque).first()
        session.close()
        return consulta

    @classmethod
    def select_all(cls):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta

class Tanque(Base):
    __tablename__ = 'tanque'
    Id_TANQUE = Column(Integer, primary_key=True, autoincrement=True)
    Id_MedicionTanque_fk = Column(Integer, ForeignKey('mediciontanque.Id_MedicionTanque'), nullable=False)
    ClaveIdentificacionTanque = Column(String(45), nullable=False)
    codigo = Column(String(20), nullable=False)
    Id_PRODUCTO_fk = Column(Integer, ForeignKey('producto.Id_PRODUCTO'), nullable=False)
    LocalizacionYODescripcionTanque = Column(String(150), nullable=False)
    VigenciaCalibracionTanque = Column(DateTime, nullable=False)
    CapacidadTotalTanque = Column(Float, nullable=False)
    CapacidadTotalTanque_UM = Column(String(5), nullable=False)
    CapacidadOperativaTanque = Column(Float, nullable=False)
    CapacidadOperativaTanque_UM = Column(String(5), nullable=False)
    CapacidadUtilTanque = Column(Float, nullable=False)
    CapacidadUtilTanque_UM = Column(String(11), nullable=False)
    CapacidadFondajeTanque = Column(Float, nullable=False)
    CapacidadFondajeTanque_UM = Column(String(5), nullable=False)
    CapacidadGasTalon = Column(Float, nullable=True)
    CapacidadGasTalon_UM = Column(String(5), nullable=True)
    VolumenMinimoOperacion = Column(Integer, nullable=False)
    VolumenMinimoOperacion_UM = Column(String(5), nullable=False)
    EstadoTanque = Column(String(2), nullable=False)

    def __repr__(self):
        return (f"<Tanque(Id_TANQUE={self.Id_TANQUE}, ClaveIdentificacionTanque={self.ClaveIdentificacionTanque}, "
                f"CapacidadTotalTanque={self.CapacidadTotalTanque}, EstadoTanque={self.EstadoTanque})>")

    @classmethod
    def add(cls, clave_identificacion, localizacion_descripcion, vigencia_calibracion, 
            capacidad_total, capacidad_total_um, capacidad_operativa, capacidad_operativa_um,
            capacidad_util, capacidad_util_um, capacidad_fondaje, capacidad_fondaje_um,
            capacidad_gas_talon, capacidad_gas_talon_um, volumen_minimo_operacion,
            volumen_minimo_operacion_um, estado_tanque):
        nuevo_tanque = cls(
            ClaveIdentificacionTanque=clave_identificacion,
            LocalizacionYODescripcionTanque=localizacion_descripcion,
            VigenciaCalibracionTanque=vigencia_calibracion,
            CapacidadTotalTanque=capacidad_total,
            CapacidadTotalTanque_UM=capacidad_total_um,
            CapacidadOperativaTanque=capacidad_operativa,
            CapacidadOperativaTanque_UM=capacidad_operativa_um,
            CapacidadUtilTanque=capacidad_util,
            CapacidadUtilTanque_UM=capacidad_util_um,
            CapacidadFondajeTanque=capacidad_fondaje,
            CapacidadFondajeTanque_UM=capacidad_fondaje_um,
            CapacidadGasTalon=capacidad_gas_talon,
            CapacidadGasTalon_UM=capacidad_gas_talon_um,
            VolumenMinimoOperacion=volumen_minimo_operacion,
            VolumenMinimoOperacion_UM=volumen_minimo_operacion_um,
            EstadoTanque=estado_tanque
        )
        result_data = add_to_table(nuevo_tanque)  # Asegúrate de implementar esta función
        return result_data if result_data else None

    @classmethod
    def select_by_id(cls, id):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id_TANQUE=id).first()
        session.close()
        return consulta

    @classmethod
    def select_all(cls):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta
    
    @classmethod
    def select_by_Codigo(cls,clave):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).filter_by(codigo=clave).first()
        session.close()
        return consulta
    
    @classmethod
    def get_for_Id_PRODUCTO_fk(cls, id_producto_fk):
        try:
            consulta = None
            session = SessionLocal()
            consulta = session.query(cls).filter_by(Id_PRODUCTO_fk=id_producto_fk).all()
            session.close()
            return consulta
        except Exception as e:
            print(f"Error al recuperar el tanque por producto: {e}")
            return None

class Entrega(Base):
    __tablename__ = 'entrega'

    Id_ENTREGA = Column(Integer, primary_key=True, autoincrement=True)
    Id_ENTREGAS_fk = Column(Integer, ForeignKey('entregas.Id_ENTREGAS'), nullable=False)
    NumeroDeRegistro = Column(String(10), nullable=False)
    TipoDeRegistro = Column(Integer, nullable=False)
    VolumenInicialTanque = Column(Float, nullable=False)
    VolumenInicialTanque_UM = Column(String(45), nullable=False)
    VolumenFinalTanque = Column(Float, nullable=False)
    VolumenEntregado = Column(Float, nullable=False)
    VolumenEntregado_UM = Column(String(45), nullable=False)
    Temperatura = Column(Integer, nullable=False)
    PresionAbsoluta = Column(Float, nullable=False)
    FechaYHoraInicialEntrega = Column(DateTime, nullable=False)
    FechaYHoraFinalEntrega = Column(DateTime, nullable=False)
    Complemento = Column(Integer, nullable=False)

    def __repr__(self):
        return (f"<Entrega(Id_ENTREGA={self.Id_ENTREGA}, FechaYHoraInicialEntrega={self.FechaYHoraInicialEntrega})>")

    @classmethod
    def add(cls, id_entregas_fk, numero_de_registro, tipo_de_registro, volumen_inicial_tanque, volumen_inicial_tanque_um, 
            volumen_final_tanque, volumen_entregado, volumen_entregado_um, temperatura, presion_absoluta, 
            fecha_y_hora_inicial_entrega, fecha_y_hora_final_entrega, complemento):
        nueva_entrega = cls(
            Id_ENTREGAS_fk = id_entregas_fk,
            NumeroDeRegistro=numero_de_registro,
            TipoDeRegistro=tipo_de_registro,
            VolumenInicialTanque=volumen_inicial_tanque,
            VolumenInicialTanque_UM=volumen_inicial_tanque_um,
            VolumenFinalTanque=volumen_final_tanque,
            VolumenEntregado=volumen_entregado,
            VolumenEntregado_UM=volumen_entregado_um,
            Temperatura=temperatura,
            PresionAbsoluta=presion_absoluta,
            FechaYHoraInicialEntrega=fecha_y_hora_inicial_entrega,
            FechaYHoraFinalEntrega=fecha_y_hora_final_entrega,
            Complemento=complemento
        )
        result_data = add_to_table(nueva_entrega)
        return result_data if result_data else None

    @classmethod
    def select_by_id(cls, id_entrega):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id_ENTREGA=id_entrega).first()
        session.close()
        return consulta
    
    @classmethod
    def select_by_id_entregas_fk(cls, id_entregas_fk):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id_ENTREGAS_fk=id_entregas_fk).all()
        session.close()
        return consulta
    

    @classmethod
    def select_all(cls):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta

class Entregas(Base):
    __tablename__ = 'entregas'

    Id_ENTREGAS = Column(Integer, primary_key=True, autoincrement=True)
    TotalEntregas = Column(Integer, nullable=False)
    SumaVolumenEntregado = Column(Float, nullable=False)
    SumaVolumenEntregado_UM = Column(String(45), nullable=False)
    TotalDocumentos = Column(String(45), nullable=False)
    SumaVentas = Column(Float, nullable=False)

    def __repr__(self):
        return (f"<Entregas(Id_ENTREGAS={self.Id_ENTREGAS}>")

    @classmethod
    def add(cls, total_entregas, suma_volumen_entregado, suma_volumen_entregado_um, 
            total_documentos, suma_ventas):
        nueva_entrega = cls(
            TotalEntregas=total_entregas,
            SumaVolumenEntregado=suma_volumen_entregado,
            SumaVolumenEntregado_UM=suma_volumen_entregado_um,
            TotalDocumentos=total_documentos,
            SumaVentas=suma_ventas
        )
        result_data = add_to_table(nueva_entrega)
        return result_data.Id_ENTREGAS if result_data else None

    @classmethod
    def select_by_id(cls, id_entregas):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id_ENTREGAS=id_entregas).first()
        session.close()
        return consulta


    @classmethod
    def select_all(cls):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta

class Recepcion(Base):
    __tablename__ = 'recepcion'

    Id_RECEPCION = Column(Integer, primary_key=True, autoincrement=True)
    Id_RECEPCIONES_fk = Column(Integer, ForeignKey('recepciones.Id_RECEPCIONES'), nullable=False)
    NumeroDeRegistro = Column(Integer, nullable=False)
    TipoDeRegistro = Column(String(10), nullable=False)
    VolumenInicialTanque = Column(Float, nullable=False)
    VolumenInicialTanque_UM = Column(String(45), nullable=False)
    VolumenFinalTanque = Column(Float, nullable=False)
    VolumenRecepcion = Column(Integer, nullable=False)
    VolumenRecepcion_UM = Column(String(45), nullable=False)
    Temperatura = Column(Integer, nullable=False)
    PresionAbsoluta = Column(Integer, nullable=False)
    FechaYHoraInicioRecepcion = Column(DateTime, nullable=False)
    FechaYHoraFinalRecepcion = Column(DateTime, nullable=False)
    Complemento = Column(Integer, nullable=True)

    def __repr__(self):
        return (f"<Recepcion(Id_RECEPCION={self.Id_RECEPCION}, FechaYHoraInicioRecepcion={self.FechaYHoraInicioRecepcion})>")

    @classmethod
    def add(cls, Id_recepciones_fk, numero_de_registro, volumen_punto_entrada, volumen_punto_entrada_um,
            volumen_recepcion, volumen_recepcion_um, temperatura, presion_absoluta,
            fecha_y_hora_inicio_recepcion, fecha_y_hora_final_recepcion, complemento=None):
        nueva_recepcion = cls(
            Id_RECEPCIONES_fk = Id_recepciones_fk,
            NumeroDeRegistro=numero_de_registro,
            VolumenPuntoEntrada=volumen_punto_entrada,
            VolumenPuntoEntrada_UM=volumen_punto_entrada_um,
            VolumenRecepcion=volumen_recepcion,
            VolumenRecepcion_UM=volumen_recepcion_um,
            Temperatura=temperatura,
            PresionAbsoluta=presion_absoluta,
            FechaYHoraInicioRecepcion=fecha_y_hora_inicio_recepcion,
            FechaYHoraFinalRecepcion=fecha_y_hora_final_recepcion,
            Complemento=complemento
        )
        result_data = add_to_table(nueva_recepcion)
        return result_data if result_data else None

    @classmethod
    def select_by_id(cls, id_recepcion):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id_RECEPCION=id_recepcion).first()
        session.close()
        return consulta
    
    @classmethod
    def select_by_id_recepciones_fk(cls, id_recepciones_fk):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id_RECEPCIONES_fk=id_recepciones_fk).all()
        session.close()
        return consulta


    @classmethod
    def select_all(cls):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta
        
class Recepciones(Base):
    __tablename__ = 'recepciones'

    Id_RECEPCIONES = Column(Integer, primary_key=True, autoincrement=True)
    TotalRecepciones = Column(Integer, nullable=False)
    SumaVolumenRecepcion = Column(Float, nullable=False)
    SumaVolumenRecepcion_UM = Column(String(45), nullable=False)
    TotalDocumentos = Column(String(45), nullable=False)
    SumaCompras = Column(Float, nullable=False)

    def __repr__(self):
        return (f"<Recepciones(Id_RECEPCIONES={self.Id_RECEPCIONES}>")

    @classmethod
    def add(cls, total_recepciones, suma_volumen_recepcion, suma_volumen_recepcion_um,
            total_documentos, suma_compras):
        nueva_recepcion = cls(
            TotalRecepciones=total_recepciones,
            SumaVolumenRecepcion=suma_volumen_recepcion,
            SumaVolumenRecepcion_UM=suma_volumen_recepcion_um,
            TotalDocumentos=total_documentos,
            SumaCompras=suma_compras
        )
        result_data = add_to_table(nueva_recepcion)
        return result_data.Id_RECEPCIONES if result_data else None

    @classmethod
    def select_by_id(cls, id_recepciones):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id_RECEPCIONES=id_recepciones).first()
        session.close()
        return consulta

    @classmethod
    def select_all(cls):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta

class Complemento(Base):
    __tablename__ = 'complemento'
    Id_complemento = Column(Integer, primary_key=True, autoincrement=True)
    Id_TERMINAL_ALMYTRANS_ALMYDIST_fk  = Column(Integer, nullable=False)
    Id_TRASVASE_fk  = Column(Integer, nullable=False)
    Id_DICTAMEN_fk  = Column(Integer, nullable=False)
    Id_CERTIFICADO_fk = Column(Integer, nullable=False)
    Tipo = Column(String(45), nullable=False)

    def __repr__(self):
        return (f"<Complemento(Id_complemento={self.Id_complemento}>")

    @classmethod
    def add(cls, Id_TERMINAL_ALMYTRANS_ALMYDIST_fk , id_trasvase, id_dictamen, id_certificado, tipo):
        nueva_recepcion = cls(
            Id_TERMINAL_ALMYTRANS_ALMYDIST_fk =Id_TERMINAL_ALMYTRANS_ALMYDIST_fk,
            Id_TRASVASE_fk=id_trasvase,
            Id_DICTAMEN_fk=id_dictamen,
            Id_CERTIFICADO_fk=id_certificado,
            Tipo=tipo
        )
        result_data = add_to_table(nueva_recepcion)
        return result_data if result_data else None

    @classmethod
    def select_by_id(cls, Id_complemento):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id_complemento=Id_complemento).first()
        session.close()
        return consulta

    @classmethod
    def select_by_id_tipo(cls, Id_complemento,Tipo):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id_complemento=Id_complemento,Tipo=Tipo).first()
        session.close()
        return consulta



    @classmethod
    def select_all(cls):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta
    
class Complemento_nacional_extranjero(Base):
    __tablename__ = 'complemento_nacional_extranjero'
    Id_complemento_nacional_extranjero  = Column(Integer, primary_key=True, autoincrement=True)
    Id_COMPLEMENTO_fk  = Column(Integer, nullable=False)
    Id_NACIONAL_fk   = Column(Integer, nullable=False)
    Id_EXTRANGERO_fk    = Column(Integer, nullable=False)
    ACLARACION = Column(Integer, nullable=False)
    def __repr__(self):
        return (f"<Complemento_nacional_extranjero(Id_complemento_nacional_extranjero={self.Id_complemento_nacional_extranjero})>")

    @classmethod
    def add(cls, id_complemento, id_nacional, id_extraccion, aclaracion):
        nuevo_complemento_nacional_extranjero = cls(
            Id_COMPLEMENTO_fk=id_complemento,
            Id_NACIONAL_fk=id_nacional,
            Id_EXTRANGERO_fk=id_extraccion,
            ACLARACION=aclaracion
        )
        result_data = add_to_table(nuevo_complemento_nacional_extranjero)
        return result_data.Id_complemento_nacional_extranjero if result_data else None
    
    @classmethod
    def select_by_id(cls, Id_complemento_nacional_extranjero):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id_COMPLEMENTO_fk=Id_complemento_nacional_extranjero).first()
        session.close()
        return consulta
    


    @classmethod
    def select_all(cls):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta

class Dictamen(Base):
    __tablename__ = 'dictamen'
    Id_Dictamen = Column(Integer, primary_key=True, autoincrement=True)
    RfcDictamen = Column(String(45), nullable=False)
    LoteDictamen = Column(Integer, nullable=False)
    NumeroFolioDictamen = Column(String(454), nullable=False)
    FechaEmisionDictamen = Column(DateTime, nullable=False)
    ResultadoDictamen = Column(String(150), nullable=False)
    def __repr__(self):
        return (f"<Dictamen(Id_Dictamen={self.Id_Dictamen}, RfcDictamen={self.RfcDictamen})>")

    @classmethod
    def add(cls, rfc_dictamen, lote_dictamen, numero_folio_dictamen, fecha_emision_dictamen, resultado_dictamen):
        nuevo_dictamen = cls(
            RfcDictamen=rfc_dictamen,
            LoteDictamen=lote_dictamen,
            NumeroFolioDictamen=numero_folio_dictamen,
            FechaEmisionDictamen=fecha_emision_dictamen,
            ResultadoDictamen=resultado_dictamen,
        )
        result_data = add_to_table(nuevo_dictamen)
        return result_data.Id_Dictamen if result_data else None

    @classmethod
    def select_by_id(cls, Id_Dictamen):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id_Dictamen=Id_Dictamen).first()
        session.close()
        return consulta

    @classmethod
    def select_all(cls):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta
    
class Certificado(Base):
    __tablename__ = 'certificado'
    Id_CERTIFICADO = Column(Integer, primary_key=True, autoincrement=True)
    RfcCertificado = Column(String(150), nullable=False)
    NumeroFolioCertificado = Column(Integer, nullable=False)
    FechaEmisionCertificado = Column(DateTime, nullable=False)
    ResultadoCertificado = Column(String(150), nullable=False)

    def __repr__(self):
        return (f"<Certificado(Id_CERTIFICADO={self.Id_CERTIFICADO}, RfcCertificado={self.RfcCertificado})>")

    @classmethod
    def add(cls, rfc_certificado, numero_folio_certificado, fecha_emision_certificado, resultado_certificado):
        nuevo_certificado = cls(
            RfcCertificado=rfc_certificado,
            NumeroFolioCertificado=numero_folio_certificado,
            FechaEmisionCertificado=fecha_emision_certificado,
            ResultadoCertificado=resultado_certificado,
        )
        result_data = add_to_table(nuevo_certificado)
        return result_data.Id_CERTIFICADO if result_data else None

    @classmethod
    def select_by_id(cls, Id_CERTIFICADO ):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id_CERTIFICADO =Id_CERTIFICADO).first()
        session.close()
        return consulta

    @classmethod
    def select_all(cls):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta
    
class Almacenamiento(Base):
    __tablename__ = 'almacenamiento'
    Id_Almacenamiento = Column(Integer, primary_key=True, autoincrement=True)
    TerminalAlm = Column(String(150), nullable=False)
    PermisoAlmacenamiento = Column(String(50), nullable=False)
    TarifaDeAlmacenamiento = Column(Float, nullable=False)
    CargoPorCapacidadAlmac = Column(Float, nullable=False)
    CargoPorUsoAlmac = Column(Float, nullable=False)
    CargoVolumetricoAlmac = Column(Float, nullable=False)

    def __repr__(self):
        return (f"<Almacenamiento(Id_Almacenamiento={self.Id_Almacenamiento}, TerminalAlm={self.TerminalAlm})>")

    @classmethod
    def add(cls, terminal_alm, permiso_almacenamiento, tarifa_almacenamiento, cargo_capacidad, cargo_uso, cargo_volumetrico):
        nuevo_almacenamiento = cls(
            TerminalAlm=terminal_alm,
            PermisoAlmacenamiento=permiso_almacenamiento,
            TarifaDeAlmacenamiento=tarifa_almacenamiento,
            CargoPorCapacidadAlmac=cargo_capacidad,
            CargoPorUsoAlmac=cargo_uso,
            CargoVolumetricoAlmac=cargo_volumetrico,
        )
        result_data = add_to_table(nuevo_almacenamiento)
        return result_data if result_data else None

    @classmethod
    def select_by_id(cls, Id_Almacenamiento ):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id_Almacenamiento = Id_Almacenamiento ).first()
        session.close()
        return consulta

    @classmethod
    def select_all(cls):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta
    
class Cfdis(Base):
    __tablename__ = 'cfdis'
    Id_CFDIS = Column(Integer, primary_key=True, autoincrement=True)
    CFDI = Column(String(45), nullable=False)
    TipoCFDI = Column(String(45), nullable=False)
    PrecioVentaOCompraOContrap = Column(Float, nullable=False)
    FechaYHoraTransaccion = Column(DateTime, nullable=False)
    VolumenDocumentado = Column(Integer, nullable=False)
    VolumenDocumentado_UM = Column(String(45), nullable=False)

    def __repr__(self):
        return (f"<Cfdis(Id_CFDIS={self.Id_CFDIS}, CFDI={self.CFDI})>")

    @classmethod
    def add(cls, cfdi, tipo_cfdi, precio_venta_compra, fecha_transaccion, volumen_documentado, volumen_documentado_um):
        nuevo_cfdi = cls(
            CFDI=cfdi,
            TipoCFDI=tipo_cfdi,
            PrecioVentaOCompraOContrap=precio_venta_compra,
            FechaYHoraTransaccion=fecha_transaccion,
            VolumenDocumentado=volumen_documentado,
            VolumenDocumentado_UM=volumen_documentado_um
        )
        result_data = add_to_table(nuevo_cfdi)
        return result_data.Id_CFDIS if result_data else None
    
    @classmethod
    def select_by_id(cls, Id_CFDIS ):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id_CFDIS =Id_CFDIS ).first()
        session.close()
        return consulta

    @classmethod
    def select_all(cls):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta

class Transporte(Base):
    __tablename__ = 'transporte'
    Id_Transporte = Column(Integer, primary_key=True, autoincrement=True)
    PermisoTransporte = Column(String(150), nullable=False)
    ClaveDeVehiculo = Column(String(45), nullable=False)
    TarifaDeTransporte = Column(Float, nullable=False)
    CargoPorCapacidadTrans = Column(Float, nullable=False)
    CargoPorUsoTrans = Column(Float, nullable=False)
    CargoVolumetricoTrans = Column(Integer, nullable=False)
    TarfiaDeSuministro = Column(Float, nullable=False)

    def __repr__(self):
        return (f"<Transporte(Id_Transporte={self.Id_Transporte}, PermisoTransporte={self.PermisoTransporte})>")

    @classmethod
    def add(cls, permiso_transporte, clave_vehiculo, tarifa_transporte, cargo_capacidad, cargo_uso, cargo_volumetrico, tarifa_suministro):
        nuevo_transporte = cls(
            PermisoTransporte=permiso_transporte,
            ClaveDeVehiculo=clave_vehiculo,
            TarifaDeTransporte=tarifa_transporte,
            CargoPorCapacidadTrans=cargo_capacidad,
            CargoPorUsoTrans=cargo_uso,
            CargoVolumetricoTrans=cargo_volumetrico,
            TarfiaDeSuministro=tarifa_suministro,
        )
        result_data = add_to_table(nuevo_transporte)
        return result_data if result_data else None
    
    @classmethod
    def select_by_id(cls, Id_Transporte):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id_Transporte = Id_Transporte ).first()
        session.close()
        return consulta

    @classmethod
    def select_all(cls):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta

class Trasvase(Base):
    __tablename__ = 'trasvase'
    Id_Trasvase = Column(Integer, primary_key=True, autoincrement=True)
    NombreTrasvase = Column(String(150), nullable=False) 
    RfcTrasvase = Column(String(13), nullable=False)      
    PermisoTrasvase = Column(String(50), nullable=False)  
    DescripcionTrasvase = Column(String(255), nullable=False)  
    CfdiTrasvase = Column(String(45), nullable=False)    
    def __repr__(self):
        return (f"<Trasvase(Id_Trasvase={self.Id_Trasvase}, NombreTrasvase={self.NombreTrasvase})>")

    @classmethod
    def add(cls, nombre_trasvase, rfc_trasvase, permiso_trasvase, descripcion_trasvase, cfdi_trasvase):
        nuevo_trasvase = cls(
            NombreTrasvase=nombre_trasvase,
            RfcTrasvase=rfc_trasvase,
            PermisoTrasvase=permiso_trasvase,
            DescripcionTrasvase=descripcion_trasvase,
            CfdiTrasvase=cfdi_trasvase,
        )
        result_data = add_to_table(nuevo_trasvase)
        return result_data if result_data else None
    
    @classmethod
    def select_by_id(cls, Id_Trasvase ):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id_Trasvase = Id_Trasvase).first()
        session.close()
        return consulta

    @classmethod
    def select_all(cls):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta

class Nacional(Base):
    __tablename__ = 'nacional'
    Id_NACIONAL = Column(Integer, primary_key=True, autoincrement=True)
    Id_cliente_cv_fk = Column(Integer,  nullable=True)
    Id_proveedor_cv_fk = Column(Integer, nullable=True)



    def __repr__(self):
        return f"<Nacional(Id_NACIONAL={self.Id_NACIONAL}, Id_cliente_cv_fk={self.Id_cliente_cv_fk},Id_proveedor_cv_fk={self.Id_proveedor_cv_fk})>"

    @classmethod
    def add(cls, Id_cliente_cv_fk,Id_proveedor_cv_fk):
        nuevo_nacional = cls(
            Id_cliente_cv_fk=Id_cliente_cv_fk,
            Id_proveedor_cv_fk=Id_proveedor_cv_fk
            )
        result_data = add_to_table(nuevo_nacional)
        return result_data if result_data else None

    @classmethod
    def select_by_id(cls, Id_NACIONAL):
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id_NACIONAL=Id_NACIONAL).first()
        session.close()
        return consulta

    @classmethod
    def select_all(cls):
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta
    
class Nacional_CFDI(Base):
    __tablename__ = 'nacional_cfdis'
    Id_nacional_cfdis  = Column(Integer, primary_key=True, autoincrement=True)
    Id_NACIONAL_fk  = Column(String(150), nullable=False)
    Id_cfdis_distribuidor_fk = Column(String(150), nullable=True)
    Id_cfdis_comercializador_fk  = Column(String(150), nullable=True)

    def __repr__(self):
        return f"<Nacional(Id_NACIONAL_fk={self.Id_NACIONAL_fk},d_cfdis_distribuidor_fk={self.Id_cfdis_distribuidor_fk},Id_cfdis_comercializador_fk={self.Id_cfdis_comercializador_fk})>"

    @classmethod
    def add(cls, Id_nacional_cfdis, Id_NACIONAL_fk,Id_cfdis_distribuidor_fk, Id_cfdis_comercializador_fk):
        nuevo_nacional_cfdis = cls(
            Id_nacional_cfdis=Id_nacional_cfdis,
            Id_NACIONAL_fk=Id_NACIONAL_fk,
            Id_cfdis_distribuidor_fk=Id_cfdis_distribuidor_fk,
            Id_cfdis_comercializador_fk = Id_cfdis_comercializador_fk
        )
        result_data = add_to_table(nuevo_nacional_cfdis)
        return result_data if result_data else None

    @classmethod
    def select_by_id(cls, Id_NACIONAL,Tipo):
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id_NACIONAL=Id_NACIONAL,Tipo=Tipo).first()
        session.close()
        return consulta

    @classmethod
    def select_all(cls):
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta

class Extranjero(Base):
    __tablename__ = 'extranjero'
    Id_EXTRANJERO = Column(Integer, primary_key=True, autoincrement=True)
    PermisoImportacionOExportacion = Column(String(45), nullable=False)
    Id_PEDIMENTOS_fk = Column(String(45), nullable=False)

    def __repr__(self):
        return f"<Extranjero(Id_EXTRANJERO={self.Id_EXTRANJERO}, PermisoImportacionOExportacion={self.PermisoImportacionOExportacion}),Id_PEDIMENTOS_fk={self.Id_PEDIMENTOS_fk}>"

    @classmethod
    def add(cls, permiso_importacion_o_exportacion,Id_PEDIMENTOS_fk):
        nuevo_extranjero = cls(
            PermisoImportacionOExportacion=permiso_importacion_o_exportacion,
            Id_PEDIMENTOS_fk= Id_PEDIMENTOS_fk
        )
        result_data = add_to_table(nuevo_extranjero)
        return result_data if result_data else None

    @classmethod
    def select_by_id(cls, Id_EXTRANJERO):
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id_EXTRANJERO=Id_EXTRANJERO).first()
        session.close()
        return consulta

    @classmethod
    def select_all(cls):
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta

class Pedimentos(Base):
    __tablename__ = 'pedimentos'
    Id_PEDIMENTOS = Column(Integer, primary_key=True, autoincrement=True)
    Id_extranjero_fk =  Column(Integer, ForeignKey('extranjero.Id_EXTRANJERO'), nullable=True)
    PuntoDeInternacionOExtraccion = Column(Integer, nullable=False)
    PaisOrigenODestino = Column(String(45), nullable=False)
    MedioDeTransEntraOSaleAducto = Column(Integer, nullable=False)
    PedimentosAduanal = Column(String(45), nullable=False)
    Incoterms = Column(String(45), nullable=False)
    PrecioDeImportacionOExportacion = Column(Float, nullable=False)
    VolumenDocumentado = Column(Integer, nullable=False)
    VolumenDocumentado_UM = Column(String(45), nullable=False)

    def __repr__(self):
        return (f"<Pedimentos(Id_PEDIMENTOS={self.Id_PEDIMENTOS}, "
                f"PuntoDeInternacionOExtraccion={self.PuntoDeInternacionOExtraccion}, "
                f"PaisOrigenODestino={self.PaisOrigenODestino})>")

    @classmethod
    def add(cls,id_extranjero_fk, punto_de_internacion_o_extraccion, pais_origen_o_destino,
             medio_de_trans_entra_o_sale_aducto, pedimentos_aduanal, 
             incoterms, precio_de_importacion_o_exportacion, 
             volumen_documentado, volumen_documentado_um):
        nuevo_pedimento = cls(
            Id_extranjero_fk=id_extranjero_fk,
            PuntoDeInternacionOExtraccion=punto_de_internacion_o_extraccion,
            PaisOrigenODestino=pais_origen_o_destino,
            MedioDeTransEntraOSaleAducto=medio_de_trans_entra_o_sale_aducto,
            PedimentosAduanal=pedimentos_aduanal,
            Incoterms=incoterms,
            PrecioDeImportacionOExportacion=precio_de_importacion_o_exportacion,
            VolumenDocumentado=volumen_documentado,
            VolumenDocumentado_UM=volumen_documentado_um
        )
        result_data = add_to_table(nuevo_pedimento)
        return result_data if result_data else None

    @classmethod
    def select_by_id(cls, Id_PEDIMENTOS):
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id_PEDIMENTOS=Id_PEDIMENTOS).first()
        session.close()
        return consulta

    @classmethod
    def select_by_id_pedimentos_fk(cls, id_extranjero_fk):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id_extranjero_fk =id_extranjero_fk).all() 
        session.close()
        return consulta

    @classmethod
    def select_all(cls):
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta

class ExtranjeroPedimentos(Base):
    __tablename__ = 'extranjero_pedimentos'
    Id_extranjero_pedimentos = Column(Integer, primary_key=True, autoincrement=True)
    Id_EXTRANJERO_fk = Column(Integer, ForeignKey('extranjero.Id_EXTRANJERO'), nullable=False)
    Id_PEDIMENTOS_fk = Column(Integer, ForeignKey('pedimentos.Id_PEDIMENTOS'), nullable=False)

    # Relaciones con las tablas relacionadas
    extranjero = relationship("Extranjero", backref="extranjero_pedimentos")
    pedimentos = relationship("Pedimentos", backref="extranjero_pedimentos")

    def __repr__(self):
        return (f"<ExtranjeroPedimentos(Id_extranjero_pedimentos={self.Id_extranjero_pedimentos}, "
                f"Id_EXTRANJERO_fk={self.Id_EXTRANJERO_fk}, Id_PEDIMENTOS_fk={self.Id_PEDIMENTOS_fk})>")

    @classmethod
    def add(cls, id_extranjero, id_pedimentos):
        nuevo_extranjero_pedimentos = cls(
            Id_EXTRANJERO_fk=id_extranjero,
            Id_PEDIMENTOS_fk=id_pedimentos
        )
        result_data = add_to_table(nuevo_extranjero_pedimentos)
        return result_data.Id_extranjero_pedimentos if result_data else None

    @classmethod
    def select_by_id(cls, Id_extranjero_pedimentos):
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id_extranjero_pedimentos=Id_extranjero_pedimentos).first()
        session.close()
        return consulta

    @classmethod
    def select_all(cls):
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta

class TerminalAlmYTransTerminalAlmYDist(Base):
    __tablename__ = 'terminalalmytrans_terminalalmydist'
    
    Id_Terminal_Almytrans_Almydist = Column(Integer, primary_key=True, autoincrement=True)
    Almacenamiento = Column(Integer, nullable=False)  
    Transporte = Column(Integer, nullable=False)  

    def __repr__(self):
        return (f"<TerminalAlmYTransTerminalAlmYDist(Id_Terminal_Almytrans_Almydist={self.Id_Terminal_Almytrans_Almydist}, "
                f"Almacenamiento={self.Almacenamiento}, Transporte={self.Transporte} )>")

    @classmethod
    def add(cls, almacenamiento, transporte):
        nuevo_registro = cls(
            Almacenamiento=almacenamiento,
            Transporte=transporte,
        )
        result_data = add_to_table(nuevo_registro)
        return result_data if result_data else None

    @classmethod
    def select_by_id(cls, id_Terminal_Almytrans_Almydist):
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id_Terminal_Almytrans_Almydist =id_Terminal_Almytrans_Almydist).first()
        session.close()
        return consulta

    @classmethod
    def select_all(cls):
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta

class EventosComercializador(Base):
    __tablename__ = 'eventos_comercializador'
    
    Id_Eventos_Comercializador = Column(Integer, primary_key=True, autoincrement=True)
    #NumeroRegistro = Column(Integer, nullable=False)
    FechaYHoraEvento = Column(DateTime, nullable=False)
    UsuarioResponsable = Column(String(45), default=None)
    TipoEvento = Column(Integer, nullable=False)
    DescripcionEvento = Column(String(150), default=None)
    IdentificacionCOmponenteAlarma = Column(String(45), default=None)

    def __repr__(self):
        return (f"<EventosComercializador(Id_Eventos_Comercializador={self.Id_Eventos_Comercializador}, "
                f"FechaYHoraEvento={self.FechaYHoraEvento})>")

    @classmethod
    def add(cls, fecha_y_hora_evento, usuario_responsable=None, 
            tipo_evento=None, descripcion_evento=None, identificacion_componente_alarma=None):
        nuevo_evento = cls(
            FechaYHoraEvento=fecha_y_hora_evento,
            UsuarioResponsable=usuario_responsable,
            TipoEvento=tipo_evento,
            DescripcionEvento=descripcion_evento,
            IdentificacionCOmponenteAlarma=identificacion_componente_alarma
        )
        result_data = add_to_table(nuevo_evento)
        return result_data.Id_Eventos_Comercializador if result_data else None

    @classmethod
    def select_by_id(cls, Id_Eventos_Comercializador):
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id_Eventos_Comercializador=Id_Eventos_Comercializador).first()
        session.close()
        return consulta

    @classmethod
    def select_all(cls):
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta

    @classmethod
    def select_events_between_dates(cls, fecha_inicio, fecha_fin):
        session = SessionLocal()
        consulta = (
            session.query(cls)
            .filter(cls.FechaYHoraEvento.between(fecha_inicio, fecha_fin))
            .order_by(cls.Id_Eventos_Comercializador.desc())
        ).all()
        session.close()
        return consulta
    
    @classmethod
    def select_given_between_date_for_pagination(cls, fecha_inicio, fecha_fin,page_num=1,elementos_por_pagina=100):
        session = SessionLocal()
        try:
            total_eventos = (session.query(cls)
                        .filter(cls.FechaYHoraEvento.between(fecha_inicio, fecha_fin))
                        .count())

            
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').replace(hour=23, minute=59, second=59)


            # Consulta con límite y offset para paginación
            consulta = (session.query(cls)
                        .filter(cls.FechaYHoraEvento.between(fecha_inicio, fecha_fin))
                        .order_by(cls.Id_Eventos_Comercializador.desc())
                        .limit(elementos_por_pagina)
                        .offset((page_num - 1) * elementos_por_pagina)  # Saltar elementos de páginas anteriores
                        .all())
            
            data =[]
            for item in consulta:
                data_item = {'id': item.Id_Eventos_Comercializador,
                            'fecha': item.FechaYHoraEvento,
                            'usuario': item.UsuarioResponsable,
                            'tipo': item.TipoEvento,
                            'mensaje': item.DescripcionEvento, 
                            'identificacion': item.IdentificacionCOmponenteAlarma
                            }
                data.append(data_item)

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
        
        logging.debug(consulta)

        return data, total_eventos

class EventosAlarmasDistribuidor(Base):
    __tablename__ = 'eventos_alarmas_distribuidor'
    
    Id_EVENTOS_ALARMAS_DISTRIBUIDOR = Column(Integer, primary_key=True, autoincrement=True)
    Id_EVENTO_fk = Column(Integer, nullable=False)
    Id_ALARMAS_fk = Column(Integer, nullable=False)
    Fecha = Column(DateTime, nullable=False)

    def __repr__(self):
        return (f"<EventosAlarmasDistribuidor(Id_EVENTOS_ALARMAS_DISTRIBUIDOR={self.Id_EVENTOS_ALARMAS_DISTRIBUIDOR}, "
                f"Id_EVENTO_fk={self.Id_EVENTO_fk}, Id_ALARMAS_fk={self.Id_ALARMAS_fk}, Fecha={self.Fecha})>")

    @classmethod
    def add(cls, id_evento, id_alarmas, fecha):
        nuevo_evento_alarmas = cls(
            Id_EVENTO_fk=id_evento,
            Id_ALARMAS_fk=id_alarmas,
            Fecha=fecha
        )
        result_data = add_to_table(nuevo_evento_alarmas)
        return result_data.Id_EVENTOS_ALARMAS_DISTRIBUIDOR if result_data else None

    @classmethod
    def select_by_id(cls, Id_EVENTOS_ALARMAS_DISTRIBUIDOR):
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id_EVENTOS_ALARMAS_DISTRIBUIDOR=Id_EVENTOS_ALARMAS_DISTRIBUIDOR).first()
        session.close()
        return consulta

    @classmethod
    def select_events_and_alarms_between_dates(cls,fecha_inicio,fecha_fin):
        session = SessionLocal()
        consulta = (session.query(cls)
                            .filter(cls.Fecha.between(fecha_inicio, fecha_fin))
                            .order_by(cls.Id_EVENTOS_ALARMAS_DISTRIBUIDOR.desc())).all()
        session.close()
        resultado = []
        if consulta:
            for item in consulta:
                if item.Id_ALARMAS_fk != None:
                    alarm = scaizen_db.Alarma.select_by_id(item.Id_ALARMAS_fk)
                    if alarm:
                        alarm_dic = query_to_json([alarm])[0]
                        alarm_dic["is_event"] = False
                        alarm_dic["numero_registro"] = item.Id_EVENTOS_ALARMAS_DISTRIBUIDOR
                        resultado.append(alarm_dic)
                elif item.Id_EVENTO_fk != None:
                    event = EventosDistribuidor.select_by_id(item.Id_EVENTO_fk)
                    if event:
                        event_dic = query_to_json([event])[0]
                        event_dic["is_event"] = True
                        event_dic["numero_registro"] = item.Id_EVENTOS_ALARMAS_DISTRIBUIDOR
                        resultado.append(event_dic)
        else: resultado = None
        return resultado
    
    @classmethod
    def select_all(cls):
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta

class EventosDistribuidor(Base):
    __tablename__ = 'eventos_distribuidor'
    
    Id_EVENTOS_DISTRIBUIDOR = Column(Integer, primary_key=True, autoincrement=True)
    #NumeroRegistro = Column(Integer, nullable=False)
    fecha = Column(DateTime, nullable=False)
    UsuarioResponsable = Column(String(11), default=None)
    tipo = Column(Integer, nullable=False)
    mensaje = Column(String(11), nullable=False)
    identificacion = Column(String(45), default=None)
    direccion_ip = Column(String(40), default=None)

    def __repr__(self):
        return (f"<EventosDistribuidor(Id_EVENTOS_DISTRIBUIDOR={self.Id_EVENTOS_DISTRIBUIDOR}, "
                f"FechaYHoraEvento={self.fecha})>")

    @classmethod
    def add(cls,  fecha, usuario_responsable, tipo, mensaje, identificacion, direccion_ip=None):
        nuevo_evento_distribuidor = cls(
            fecha=fecha,
            UsuarioResponsable=usuario_responsable,
            tipo=tipo,
            mensaje=mensaje,
            identificacion=identificacion,
            direccion_ip=direccion_ip
        )
        result_data = add_to_table(nuevo_evento_distribuidor)
        if result_data:
            EventosAlarmasDistribuidor.add(result_data.Id_EVENTOS_DISTRIBUIDOR, None, fecha)
        return result_data.Id_EVENTOS_DISTRIBUIDOR if result_data else None

    @classmethod
    def select_by_id(cls, Id_EVENTOS_DISTRIBUIDOR):
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id_EVENTOS_DISTRIBUIDOR=Id_EVENTOS_DISTRIBUIDOR).first()
        session.close()
        return consulta
    @classmethod
    def select_by_id_date(cls, fecha):
        session = SessionLocal()
        consulta = session.query(cls).filter_by(fecha=fecha).first()
        session.close()
        return consulta

    @classmethod
    def select_all(cls):
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta
    
    @classmethod
    def select_given_between_date_for_pagination(cls, fecha_inicio, fecha_fin,page_num=1,elementos_por_pagina=100):
        session = SessionLocal()
        try:
            total_eventos = (session.query(cls)
                        .filter(cls.fecha.between(fecha_inicio, fecha_fin))
                        .count())
            
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').replace(hour=23, minute=59, second=59)

            # Consulta con límite y offset para paginación
            consulta = (session.query(cls)
                        .filter(cls.fecha.between(fecha_inicio, fecha_fin))
                        .order_by(cls.Id_EVENTOS_DISTRIBUIDOR.desc())
                        .limit(elementos_por_pagina)
                        .offset((page_num - 1) * elementos_por_pagina)  # Saltar elementos de páginas anteriores
                        .all())
            
            data =[]
            for item in consulta:
                data_item = {'id': item.Id_EVENTOS_DISTRIBUIDOR,
                            'fecha': item.fecha,
                            'usuario': item.UsuarioResponsable,
                            'tipo': item.tipo,
                            'mensaje': item.mensaje, 
                            'identificacion': item.identificacion
                            }
                data.append(data_item)

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
        
        logging.debug(data)

        return data, total_eventos
    
    @classmethod
    def select_given_between_date(cls, fecha_inicio, fecha_fin):
        session = SessionLocal()
        try:
            consulta = (session.query(cls)
                        .filter(cls.fecha.between(fecha_inicio, fecha_fin))
                        .order_by(cls.Id_EVENTOS_DISTRIBUIDOR.desc())
                        .all())
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

            data =[]
            for item in consulta:
                data_item = {'id': item.Id_EVENTOS_DISTRIBUIDOR,
                            'fecha': item.fecha,
                            'usuario': item.UsuarioResponsable,
                            'tipo': item.tipo,
                            'mensaje': item.mensaje, 
                            'identificacion': item.identificacion
                            }
                data.append(data_item)

        #return resultado
        return data

class CargasComercializador(Base):
    __tablename__ = 'cargas_comercializador'

    Id = Column(Integer, primary_key=True, autoincrement=True)
    #Id_ENTREGAS_fk = Column(Integer, ForeignKey('entregas.Id_ENTREGAS'), nullable=True)
    id_entregas_fk = Column(Integer, nullable=True)
    Id_cfdi_comercializador_fk = Column(Integer, nullable=False)
    Autotanque = Column(String(20), nullable=False)
    Producto = Column(String, nullable=False)
    TipoDeRegistro = Column(String(10), nullable=False)
    VolumenInicialTanque = Column(Float, nullable=False)
    VolumenInicialTanque_UM = Column(String(45), nullable=False)
    VolumenFinalTanque = Column(Float, nullable=False)
    VolumenEntregado = Column(Float, nullable=False)
    VolumenEntregado_UM = Column(String(45), nullable=False)
    VolumenEntregadoNeto = Column(Float, nullable=False)
    VolumenEntregadoNeto_UM = Column(String(45), nullable=False)
    Temperatura = Column(Integer, nullable=False)
    PresionAbsoluta = Column(Float, nullable=True)
    Costo = Column(Double, nullable=True)
    CostoTraslado = Column(Double, nullable=True)
    TotalImpuestos = Column(Double, nullable=True)
    CostoTotal = Column(Double, nullable=True)
    FechaYHoraInicialEntrega = Column(DateTime, nullable=False)
    FechaYHoraFinalEntrega = Column(DateTime, nullable=False)
    ArchivoFacturaNombreXML = Column(String(200), nullable=True)
    Complemento = Column(String(200), nullable=True)
    Id_cliente_cv_fk = Column(Integer, nullable=True)
    Id_estacion_cv_fk = Column(Integer, nullable=True)

    def __repr__(self):
        return (f"<Entrega(Id={self.Id}, FechaYHoraInicialEntrega={self.FechaYHoraInicialEntrega})>")

    @classmethod
    def add(cls,
            autotanque,
            producto, 
            tipo_de_registro, 
            volumen_inicial_tanque, 
            volumen_inicial_tanque_um, 
            volumen_final_tanque, 
            volumen_entregado, 
            volumen_entregado_um, 
            volumen_entregado_neto, 
            volumen_entregado_neto_um,
            temperatura, 
            presion_absoluta, 
            costo, 
            costotraslado, 
            costototal, 
            fecha_y_hora_inicial_entrega, 
            fecha_y_hora_final_entrega,
            complemento):
        nueva_entrega = cls(
            Autotanque = autotanque,
            Producto=producto,
            TipoDeRegistro=tipo_de_registro,
            VolumenInicialTanque=volumen_inicial_tanque,
            VolumenInicialTanque_UM=volumen_inicial_tanque_um,
            VolumenFinalTanque=volumen_final_tanque,
            VolumenEntregado=volumen_entregado,
            VolumenEntregado_UM=volumen_entregado_um,
            VolumenEntregadoNeto=volumen_entregado_neto,
            VolumenEntregadoNeto_UM=volumen_entregado_neto_um,
            Temperatura=temperatura,
            PresionAbsoluta=presion_absoluta,
            Costo=costo,
            CostoTraslado = costotraslado,
            CostoTotal = costototal,
            FechaYHoraInicialEntrega=fecha_y_hora_inicial_entrega,
            FechaYHoraFinalEntrega=fecha_y_hora_final_entrega,
            Complemento = complemento
        )
        result_data = add_to_table(nueva_entrega)
        return result_data if result_data else None


    @classmethod
    def select_by_id(cls, Id):
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id=Id).first()
        session.close()
        return consulta
    
    @classmethod
    def select_by_id_entregas_fk(cls, id_entregas_fk):
        session = SessionLocal()
        consulta = session.query(cls).filter_by(id_entregas_fk=id_entregas_fk).all()
        session.close()
        return consulta
    
    @classmethod
    def select_all(cls):
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta
    
    @classmethod
    def select_given_between_date_for_pagination(cls, fecha_inicio, fecha_fin, page_num=1, elementos_por_pagina=50):
        session = SessionLocal()
        try:
            # Contar el número total de registros en el rango de fechas
            total_descargas = (session.query(cls)
                            .filter(cls.FechaYHoraInicialEntrega.between(fecha_inicio, fecha_fin))
                            .count())
            
            # Consulta con límite y offset para paginación
            consulta = (session.query(cls)
                        .filter(cls.FechaYHoraInicialEntrega.between(fecha_inicio, fecha_fin))
                        .order_by(cls.Id.desc())
                        .limit(elementos_por_pagina)
                        .offset((page_num - 1) * elementos_por_pagina)  # Saltar elementos de páginas anteriores
                        .all())
            
            data_return = []
            # Aplicar hash a Id_RECEPCION para cada registro
            for registro in consulta:
                data = {
                    'registro': None,
                    'proveedor':'Desconocido',
                    'NoConsecutivo':0
                }
                data['NoConsecutivo'] = registro.Id
                registro.Id = config.encriptar_a_hex(clave_hex_hash, registro.Id)  # Generar hash SHA-256
                data['registro'] = registro
                cliente_info = ClienteCV.select_by_Id_cliente(registro.Id_cliente_cv_fk)
                estacion_info = EstacionesCV.select_by_Id_estacion(registro.Id_estacion_cv_fk)
                if cliente_info: 
                    data['cliente'] = cliente_info.Nombre_comercial
                    data['rfc'] = cliente_info.RFC
                if estacion_info:
                    data['cliente'] = estacion_info.Nombre_comercial
                    data['rfc'] = estacion_info.RFC
                data_return.append(data)

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
            
        return data_return, total_descargas
    
    @classmethod
    def get_by_date_and_producto(cls, producto, fecha_inicio=None, fecha_fin=None):
        """Consulta registros por tipo y producto con fechas opcionales."""
        filters = []
        filters.append(cls.Producto == producto)
        filters.append(cls.FechaYHoraInicialEntrega.between(fecha_inicio,fecha_fin))
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
    def update_id_entregas_fk(cls, id, id_entregas_fk):
        session = SessionLocal()
        recepcion = recepcion = session.query(cls).filter_by(Id=id).first()
        if recepcion:
            logging.debug(f"id: {id},id_entregas_fk: {id_entregas_fk}")
            try:
                recepcion.id_entregas_fk = id_entregas_fk
                session.commit()  # Confirmamos los cambios en la base de datos
                return recepcion  # Devolvemos el objeto actualizado
            except Exception as e:
                session.rollback()  # Deshacemos cualquier cambio en caso de error
                raise e  # Opcional: se puede personalizar la excepción o devolver un mensaje
            finally:
                session.close()  # Cerramos la sesión en todos los casos
        else:
            logging.debug("No se encontro para update_id_entregas_fk")
            return None  # Retornamos None si no se encontró el registro
    
class DescargasComercializador(Base):
    __tablename__ = 'descargas_comercializador'

    Id = Column(Integer, primary_key=True, autoincrement=True)
    id_recepciones_fk = Column(Integer, nullable=True)
    Id_cfdi_comercializador_fk = Column(Integer, nullable=False)
    id_proveedor_fk = Column(Integer, nullable=False)
    Autotanque = Column(String(20), nullable=False)
    Producto = Column(String, nullable=False)
    TipoDeRegistro = Column(String(10), nullable=False)
    VolumenInicialTanque = Column(Float, nullable=False)
    VolumenInicialTanque_UM = Column(String(45), nullable=False)
    VolumenFinalTanque = Column(Float, nullable=False)
    VolumenRecepcion = Column(Float, nullable=False)
    VolumenRecepcion_UM = Column(String(45), nullable=False)
    VolumenRecepcionNeto = Column(Float, nullable=False)
    VolumenRecepcionNeto_UM = Column(String(45), nullable=False)
    Temperatura = Column(Integer, nullable=False)
    PresionAbsoluta = Column(Float, nullable=True)
    Costo = Column(Double, nullable=False)
    CostoTraslado = Column(Double, nullable=True)
    TotalImpuestos = Column(Double, nullable=True)
    CostoTotal = Column(Double, nullable=True)
    FechaYHoraInicialRecepcion = Column(DateTime, nullable=False)
    FechaYHoraFinalRecepcion = Column(DateTime, nullable=False)
    ArchivoFacturaNombreXML = Column(String(200), nullable=False)
    Complemento = Column(String(200), nullable=True)



    def __repr__(self):
        return (f"<Entrega(Id={self.Id}, FechaYHoraInicialEntrega={self.FechaYHoraInicialRecepcion})>")

    @classmethod
    def add(cls, 
            Id_cfdi_comercializador_fk,
            id_proveedor_fk, 
            autotanque, 
            producto, 
            tipo_de_registro, 
            volumen_inicial_tanque, 
            volumen_inicial_tanque_um, 
            volumen_final_tanque, 
            volumen_recepcion, 
            volumen_recepcion_um, 
            volumen_recepcion_neto, 
            volumen_recepcion_neto_um,
            temperatura, 
            presion_absoluta, 
            costo, 
            costotraslado, 
            totalimpuestos,
            costototal, 
            fecha_y_hora_inicial_entrega, 
            fecha_y_hora_final_entrega, 
            archivo_factura_nombre_xml,
            complemento):
        nueva_entrega = cls(
            Id_cfdi_comercializador_fk = Id_cfdi_comercializador_fk,
            id_proveedor_fk=id_proveedor_fk,
            Autotanque = autotanque,
            Producto=producto,
            TipoDeRegistro=tipo_de_registro,
            VolumenInicialTanque=volumen_inicial_tanque,
            VolumenInicialTanque_UM=volumen_inicial_tanque_um,
            VolumenFinalTanque=volumen_final_tanque,
            VolumenRecepcion=volumen_recepcion,
            VolumenRecepcion_UM=volumen_recepcion_um,
            VolumenRecepcionNeto=volumen_recepcion_neto,
            VolumenRecepcionNeto_UM=volumen_recepcion_neto_um,
            Temperatura=temperatura,
            PresionAbsoluta=presion_absoluta,
            Costo=costo,
            CostoTraslado = costotraslado,
            TotalImpuestos= totalimpuestos,
            CostoTotal = costototal,
            FechaYHoraInicialRecepcion=fecha_y_hora_inicial_entrega,
            FechaYHoraFinalRecepcion=fecha_y_hora_final_entrega,
            ArchivoFacturaNombreXML=archivo_factura_nombre_xml,
            Complemento = complemento
        )
        result_data = add_to_table(nueva_entrega)
        return result_data if result_data else None

    @classmethod
    def select_by_id(cls, Id):
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id=Id).first()
        session.close()
        return consulta
    
    @classmethod
    def select_by_id_recepciones_fk(cls, id_recepciones_fk):
        session = SessionLocal()
        consulta = session.query(cls).filter_by(id_recepciones_fk=id_recepciones_fk).all()
        session.close()
        return consulta
    
    @classmethod
    def select_all(cls):
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta
    
    @classmethod
    def select_given_between_date_for_pagination(cls, fecha_inicio, fecha_fin, page_num=1, elementos_por_pagina=100):
        session = SessionLocal()
        try:
            # Contar el número total de registros en el rango de fechas
            total_descargas = (session.query(cls)
                            .filter(cls.FechaYHoraInicialRecepcion.between(fecha_inicio, fecha_fin))
                            .count())
            
            # Consulta con límite y offset para paginación
            consulta = (session.query(cls)
                        .filter(cls.FechaYHoraInicialRecepcion.between(fecha_inicio, fecha_fin))
                        .order_by(cls.Id.desc())
                        .limit(elementos_por_pagina)
                        .offset((page_num - 1) * elementos_por_pagina)  # Saltar elementos de páginas anteriores
                        .all())
            
            data_return = []
            # Aplicar hash a Id_RECEPCION para cada registro
            for registro in consulta:
                data = {
                    'registro': None,
                    'proveedor':'Desconocido',
                    'NoConsecutivo':0
                }
                data['NoConsecutivo'] = registro.Id
                registro.Id = config.encriptar_a_hex(clave_hex_hash, registro.Id)  # Generar hash SHA-256
                data['registro'] = registro
                proveedor_info = ProveedorCV.select_by_Id_Proveedor(registro.id_proveedor_fk)
                if proveedor_info: 
                    data['proveedor'] = proveedor_info.Nombre_comercial
                    data['rfc'] = proveedor_info.RFC
                data_return.append(data)

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
        
        return data_return, total_descargas

    @classmethod
    def get_by_date_and_producto(cls, producto, fecha_inicio=None, fecha_fin=None):
        """Consulta registros por tipo y producto con fechas opcionales."""
        filters = []
        filters.append(cls.Producto == producto)
        filters.append(cls.FechaYHoraInicialRecepcion.between(fecha_inicio,fecha_fin))
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
    def update_id_recepciones_fk(cls,id,id_recepciones_fk):
        session = SessionLocal()
        recepcion = recepcion = session.query(cls).filter_by(Id=id).first()
        if recepcion:
            logging.debug(f"id: {id},id_recepciones_fk: {id_recepciones_fk}")
            try:
                recepcion.id_recepciones_fk = id_recepciones_fk
                session.commit()  # Confirmamos los cambios en la base de datos
                return recepcion  # Devolvemos el objeto actualizado
            except Exception as e:
                session.rollback()  # Deshacemos cualquier cambio en caso de error
                raise e  # Opcional: se puede personalizar la excepción o devolver un mensaje
            finally:
                session.close()  # Cerramos la sesión en todos los casos
        else:
            logging.debug("No se encontro para update_id_recepciones_fk")
            return None  # Retornamos None si no se encontró el registro
        
class CargaDistribuidor(Base):
    __tablename__ = 'carga_distribuidor'

    Id = Column(Integer, primary_key=True, autoincrement=True)
    Id_fk = Column(Integer, nullable=False)
    id_entregas_fk = Column(Integer, nullable=True)
    Id_cfdi_distribuidor_fk = Column(Integer,nullable=True)
    NumeroDeOrden_Distribuidor = Column(Integer, nullable=False)
    Autotanque = Column(String(20), nullable=False)
    Producto = Column(String, nullable=False)
    TanqueCodigo = Column(String(20), nullable=False)
    TipoDeRegistro = Column(String(10), nullable=False)
    VolumenInicialTanque = Column(Float, nullable=False)
    VolumenInicialTanque_UM = Column(String(45), nullable=False)
    VolumenFinalTanque = Column(Float, nullable=False)
    VolumenEntregado = Column(Float, nullable=False)
    VolumenEntregado_UM = Column(String(45), nullable=False)
    VolumenEntregadoNeto = Column(Float, nullable=False)
    VolumenEntregadoNeto_UM = Column(String(45), nullable=False)
    Temperatura = Column(Integer, nullable=False)
    PresionAbsoluta = Column(Float, nullable=True)
    Costo = Column(Double, nullable=True)
    CostoTraslado = Column(Double, nullable=True)
    TotalImpuestos = Column(Double, nullable=True)
    CostoTotal = Column(Double, nullable=True)
    FechaYHoraInicialEntrega = Column(DateTime, nullable=False)
    FechaYHoraFinalEntrega = Column(DateTime, nullable=False)
    ArchivoFacturaNombreXML = Column(String(200), nullable=True)
    Complemento = Column(String(200), nullable=True)
    Id_cliente_cv_fk = Column(Integer, nullable=True)
    Id_estacion_cv_fk = Column(Integer, nullable=True)
    id_complemento = Column(Integer, nullable=True)
    Orden_Complemento = Column(Integer, nullable=True)

    def __repr__(self):
        return (f"<Entrega(Id={self.Id},TanqueCodigo={self.TanqueCodigo}, Producto={self.Producto}, FechaYHoraInicialEntrega={self.FechaYHoraInicialEntrega})>")

    @classmethod
    def add(cls, id_fk, numero_orden, autotanque,producto,tanquecodigo, tipo_de_registro, volumen_inicial_tanque, volumen_inicial_tanque_um, 
            volumen_final_tanque, volumen_entregado, volumen_entregado_um, volumen_entregado_neto, volumen_entregado_neto_um,
            temperatura, presion_absoluta, costo, costotraslado,totalimpuestos, costototal, fecha_y_hora_inicial_entrega, fecha_y_hora_final_entrega, Id_cliente_cv_fk, Id_estacion_cv_fk,Id_cfdi_distribuidor_fk = None, ArchivoFacturaNombreXML = None,Orden_Complemento = -1):
        
        nueva_entrega = cls(
            Id_fk = id_fk,
            NumeroDeOrden_Distribuidor = numero_orden,
            Autotanque = autotanque,
            Producto=producto,
            TanqueCodigo= tanquecodigo,
            TipoDeRegistro=tipo_de_registro,
            VolumenInicialTanque=volumen_inicial_tanque,
            VolumenInicialTanque_UM=volumen_inicial_tanque_um,
            VolumenFinalTanque=volumen_final_tanque,
            VolumenEntregado=volumen_entregado,
            VolumenEntregado_UM=volumen_entregado_um,
            VolumenEntregadoNeto=volumen_entregado_neto,
            VolumenEntregadoNeto_UM=volumen_entregado_neto_um,
            Temperatura=temperatura,
            PresionAbsoluta=presion_absoluta,
            Costo=costo,
            CostoTraslado = costotraslado,
            TotalImpuestos= totalimpuestos,
            CostoTotal = costototal,
            FechaYHoraInicialEntrega=fecha_y_hora_inicial_entrega,
            FechaYHoraFinalEntrega=fecha_y_hora_final_entrega,
            Id_cliente_cv_fk = Id_cliente_cv_fk,
            Id_estacion_cv_fk = Id_estacion_cv_fk,
            ArchivoFacturaNombreXML = ArchivoFacturaNombreXML,
            Id_cfdi_distribuidor_fk=Id_cfdi_distribuidor_fk if Id_cfdi_distribuidor_fk is not None else -1,
            Orden_Complemento = Orden_Complemento,
            Complemento = 1,
            id_complemento = 1
        )
        result_data = add_to_table(nueva_entrega)
        return result_data if result_data else None
    
    @classmethod
    def load_data(cls):
        logging.debug(f"Iniciando la recuperacion de cargas del distribuidor.....")
        
        SessionScaizen = scaizen_db.SessionLocal  # Session para la base de datos Scaizen
        session_cv = SessionLocal()  # Session para la base de datos de destino
        session_scaizen_db = SessionScaizen()  # Session para la base de datos Scaizen

        try:
            # Obtener IDs de la segunda tabla
            ids_tabla2 = {registro.Id_fk for registro in session_cv.query(cls.Id_fk).all()}
            logging.debug(f"ids_tabla2: {ids_tabla2}")
            
            TablaCargas = scaizen_db.OrdenesDeOperacionCarga

            # Consultar registros de la primera tabla que no están en la segunda tabla
            nuevos_registros = (session_scaizen_db.query(TablaCargas)
                                .filter(~TablaCargas.id.in_(ids_tabla2), 
                                        TablaCargas.estado == 'finalizado', 
                                        TablaCargas.id_tanque_fk > 0)
                                .order_by(asc(TablaCargas.fecha_carga))  # Orden ascendente por fecha_recepcion
                                .all())

            nuevos_registros_mapeados = []
            for registro in nuevos_registros:
                orden = scaizen_db.BatchUclCargaDescarga.get_by_id_orden_fk(registro.id_orden_fk)
                if orden:
                    logging.debug(f"Procesando orden numero {registro.id_orden_fk} con tanque {registro.id_tanque_fk}: {registro}")
                    
                    telemedicon_tanque = scaizen_db.Telemedicion_tanques.get_for_id_tanque_fk(registro.id_tanque_fk)
                    logging.debug(f"telemedicon_tanque {telemedicon_tanque}: {telemedicon_tanque}")
                    
                    if telemedicon_tanque:
                        logging.debug(f'registro.id_tanque_fk: {registro.id_tanque_fk}')
                        logging.debug(f'telemedicon_tanque: {telemedicon_tanque}')
                        
                        medicion_tanque_start = scaizen_db.Rt_tanques.get_for_id_instrumentacion_fk_start(telemedicon_tanque.id_instrumentacion_fk, orden.fecha_inicio)
                        medicion_tanque_end = scaizen_db.Rt_tanques.get_for_id_instrumentacion_end(telemedicon_tanque.id_instrumentacion_fk,orden.fecha_fin)
                        VolumenInicialTanque = 0 
                        VolumenFinalTanque = 0
                        if medicion_tanque_start:
                            MTanqueJsonStart = medicion_tanque_start.json
                            VolumenInicialTanque = MTanqueJsonStart['ucl_telemedicion']['data']['volumen_natural']
                        if medicion_tanque_end:
                            MTanqueJsonEnd = medicion_tanque_end.json
                            VolumenFinalTanque =MTanqueJsonEnd['ucl_telemedicion']['data']['volumen_natural']

                        Id_cliente_cv_fk = -1
                        Id_estacion_cv_fk = -1
                        cliente_info = None
                        estacion_servicio_info = None

                        if registro.id_destinatario_cliente_fk > 0:
                            cliente_info = scaizen_db.Cliente.select_cliente_by_id(registro.id_destinatario_cliente_fk)
                            if cliente_info:
                                cliente =  ClienteCV.select_by_rfc(cliente_info.rfc)
                                if cliente: Id_cliente_cv_fk = cliente.Id_cliente
                        else:
                            estacion_servicio_info  = scaizen_db.EstacionesDeServicio.select_by_id(registro.id_destinatario_estacion_de_servicio_fk)
                            if estacion_servicio_info:
                                estacion_servicio = EstacionesCV.select_by_rfc(estacion_servicio_info.rfc)
                                if estacion_servicio: Id_estacion_cv_fk = estacion_servicio.Id_estacion
                        
                        autotanque_info = scaizen_db.Autotanque.select_autotanque_by_id(registro.id_autotanque_fk)
                        
                        # Mapear los datos
                        nuevos_registros_mapeados.append({
                            'Id_fk': registro.id,
                            'NumeroDeOrden_Distribuidor': registro.id_orden_fk,
                            'Autotanque': autotanque_info.numero if autotanque_info else 'Desconocido',
                            'Producto': orden.producto,
                            'TanqueCodigo': scaizen_db.Tanque.get_for_id(registro.id_tanque_fk).codigo,
                            'TipoDeRegistro': 'D',
                            'VolumenInicialTanque': VolumenInicialTanque,
                            'VolumenInicialTanque_UM': 'UM04',
                            'VolumenFinalTanque': VolumenFinalTanque,
                            'VolumenEntregado': orden.volumen_natural,
                            'VolumenEntregado_UM': 'UM04',
                            'VolumenEntregadoNeto': orden.volumen_neto,
                            'VolumenEntregadoNeto_UM': 'UM04',
                            'Temperatura': orden.temperatura_promedio,
                            'PresionAbsoluta': 1.033,
                            'Costo': None,
                            'FechaYHoraInicialEntrega': orden.fecha_inicio,
                            'FechaYHoraFinalEntrega': orden.fecha_fin,
                            'Id_cliente_cv_fk': Id_cliente_cv_fk,
                            'Id_estacion_cv_fk': Id_estacion_cv_fk,
                            'Complemento': 1
                        })

            # Insertar los registros mapeados
            if nuevos_registros_mapeados:
                session_cv.bulk_insert_mappings(cls, nuevos_registros_mapeados)
                session_cv.commit()

        except Exception as e:
            error_trace = traceback.format_exc()
            logging.error(f"Exception: {str(e)}")
            logging.error(f"Traceback: {error_trace}")
            session_cv.rollback()
        finally:
            logging.debug(f"Finalizando la recuperacion de cargas del distribuidor.")
            session_cv.close()
            session_scaizen_db.close()


    @classmethod
    def select_by_id(cls, Id):
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id=Id).first()
        session.close()
        return consulta
    
    @classmethod
    def select_by_id_entregas_fk(cls, id_entregas_fk):
        session = SessionLocal()
        consulta = session.query(cls).filter_by(id_entregas_fk=id_entregas_fk).all()
        session.close()
        return consulta
    
    @classmethod
    def select_all(cls):
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta
    
    @classmethod
    def select_given_between_date_for_pagination(cls, fecha_inicio, fecha_fin, page_num=1, elementos_por_pagina=50):
        session = SessionLocal()
        try:
            # Contar el número total de registros en el rango de fechas
            total_descargas = (session.query(cls)
                            .filter(cls.FechaYHoraInicialEntrega.between(fecha_inicio, fecha_fin))
                            .count())
            
            # Consulta con límite y offset para paginación
            consulta = (session.query(cls)
                        .filter(cls.FechaYHoraInicialEntrega.between(fecha_inicio, fecha_fin))
                        .order_by(cls.Id.desc())
                        .limit(elementos_por_pagina)
                        .offset((page_num - 1) * elementos_por_pagina)  # Saltar elementos de páginas anteriores
                        .all())
            
            data_return = []
            # Aplicar hash a Id_RECEPCION para cada registro
            for registro in consulta:
                data = {
                    'registro': None,
                    'proveedor':'Desconocido',
                    'NoConsecutivo':0
                }
                data['NoConsecutivo'] = registro.Id
                registro.Id = config.encriptar_a_hex(clave_hex_hash, registro.Id)  # Generar hash SHA-256
                data['registro'] = registro
                cliente_info = ClienteCV.select_by_Id_cliente(registro.Id_cliente_cv_fk)
                estacion_info = EstacionesCV.select_by_Id_estacion(registro.Id_estacion_cv_fk)
                if cliente_info: 
                    data['cliente'] = cliente_info.Nombre_comercial
                    data['rfc'] = cliente_info.RFC
                if estacion_info: 
                    data['cliente'] = estacion_info.Nombre_comercial
                    data['rfc'] = estacion_info.RFC
                data_return.append(data)

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
        
        return data_return, total_descargas
    @classmethod
    def get_by_date_and_producto(cls, producto, fecha_inicio=None, fecha_fin=None):
        """Consulta registros por tipo y producto con fechas opcionales."""
        filters = []
        filters.append(cls.Producto == producto)
        filters.append(cls.FechaYHoraInicialEntrega.between(fecha_inicio,fecha_fin))
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
        filters.append(cls.TanqueCodigo == tanque)
        filters.append(cls.Producto == product)
        filters.append(cls.FechaYHoraInicialEntrega.between(date_start,date_end))
        try:
            session = SessionLocal()
            consulta = session.query(cls).filter(*filters).all()
            session.close()
            return consulta
        except Exception as e:
            logging.debug(f"Error al consultar en órdenes de operación carga: {e}")
            return None
    
    @classmethod
    def update_id_entregas_fk(cls, id, id_entregas_fk):
        session = SessionLocal()
        recepcion = recepcion = session.query(cls).filter_by(Id=id).first()
        if recepcion:
            logging.debug(f"id: {id},id_entregas_fk: {id_entregas_fk}")
            try:
                recepcion.id_entregas_fk = id_entregas_fk
                session.commit()  # Confirmamos los cambios en la base de datos
                return recepcion  # Devolvemos el objeto actualizado
            except Exception as e:
                session.rollback()  # Deshacemos cualquier cambio en caso de error
                raise e  # Opcional: se puede personalizar la excepción o devolver un mensaje
            finally:
                session.close()  # Cerramos la sesión en todos los casos
        else:
            logging.debug("No se encontro para update_id_entregas_fk")
            return None  # Retornamos None si no se encontró el registro
                
class DescargasDistribuidor(Base):
    __tablename__ = 'descargas_distribuidor'

    Id = Column(Integer, primary_key=True, autoincrement=True)
    Id_fk = Column(Integer, nullable=True)
    id_recepciones_fk = Column(Integer, nullable=True)
    Id_cfdi_distribuidor_fk = Column(Integer,nullable=True)
    NumeroDeOrden_Distribuidor = Column(Integer, nullable=False)
    id_proveedor_fk = Column(Integer, nullable=False)
    Autotanque = Column(String(20), nullable=False)
    Producto = Column(String, nullable=False)
    TanqueCodigo = Column(String(20), nullable=False)
    TipoDeRegistro = Column(String(10), nullable=False)
    VolumenInicialTanque = Column(Float, nullable=False)
    VolumenInicialTanque_UM = Column(String(45), nullable=False)
    VolumenFinalTanque = Column(Float, nullable=False)
    VolumenRecepcion = Column(Float, nullable=False)
    VolumenRecepcion_UM = Column(String(45), nullable=False)
    VolumenRecepcionNeto = Column(Float, nullable=False)
    VolumenRecepcionNeto_UM = Column(String(45), nullable=False)
    Temperatura = Column(Integer, nullable=False)
    PresionAbsoluta = Column(Float, nullable=True)
    Costo = Column(Double, nullable=False)
    CostoTraslado = Column(Double, nullable=True)
    TotalImpuestos = Column(Double, nullable=True)
    CostoTotal = Column(Double, nullable=True)
    FechaYHoraInicialRecepcion = Column(DateTime, nullable=False)
    FechaYHoraFinalRecepcion = Column(DateTime, nullable=False)
    ArchivoFacturaNombreXML = Column(String(200), nullable=False)
    Complemento = Column(String(200), nullable=True)

    def __repr__(self):
        return (f"<Recepcion(Id={self.Id},TanqueCodigo={self.TanqueCodigo}, Producto={self.Producto}, FechaYHoraInicialEntrega={self.FechaYHoraInicialRecepcion})>")

    @classmethod
    def add(cls,Id_cfdi_distribuidor_fk,id_proveedor_fk, autotanque, producto, tanquecodigo, tipo_de_registro, volumen_inicial_tanque, volumen_inicial_tanque_um, 
            volumen_final_tanque, volumen_recepcion, volumen_recepcion_um, volumen_recepcion_neto, volumen_recepcion_neto_um,
            temperatura, presion_absoluta, costo,costotraslado, totalimpuestos,costototal, fecha_y_hora_inicial_entrega, fecha_y_hora_final_entrega, archivo_factura_nombre_xml,complemento):
        nueva_entrega = cls(
            Id_cfdi_distribuidor_fk = Id_cfdi_distribuidor_fk,
            id_proveedor_fk=id_proveedor_fk,
            Autotanque = autotanque,
            Producto=producto,
            TanqueCodigo= tanquecodigo,
            TipoDeRegistro=tipo_de_registro,
            VolumenInicialTanque=volumen_inicial_tanque,
            VolumenInicialTanque_UM=volumen_inicial_tanque_um,
            VolumenFinalTanque=volumen_final_tanque,
            VolumenRecepcion=volumen_recepcion,
            VolumenRecepcion_UM=volumen_recepcion_um,
            VolumenRecepcionNeto=volumen_recepcion_neto,
            VolumenRecepcionNeto_UM=volumen_recepcion_neto_um,
            Temperatura=temperatura,
            PresionAbsoluta=presion_absoluta,
            Costo=costo,
            CostoTraslado = costotraslado,
            TotalImpuestos= totalimpuestos,
            CostoTotal = costototal,
            FechaYHoraInicialRecepcion=fecha_y_hora_inicial_entrega,
            FechaYHoraFinalRecepcion=fecha_y_hora_final_entrega,
            ArchivoFacturaNombreXML=archivo_factura_nombre_xml,
            Complemento = complemento
        )
        result_data = add_to_table(nueva_entrega)
        return result_data if result_data else None
    
    
    @classmethod
    def load_data(cls):
        logging.debug(f"Iniciando la recuperacion de descargas del distribuidor.....")
        
        SessionScaizen = scaizen_db.SessionLocal  # Session para la base de datos Scaizen
        session_cv = SessionLocal()  # Session para la base de datos de destino
        session_scaizen_db = SessionScaizen()  # Session para la base de datos Scaizen

        try:
            # Obtener IDs de la segunda tabla
            ids_tabla2 = {registro.Id_fk for registro in session_cv.query(cls.Id_fk).all()}
            logging.debug(f"ids_tabla2: {ids_tabla2}")
            
            TablaDescargas = scaizen_db.OrdenesDeOperacionDescarga

            # Consultar registros de la primera tabla que no están en la segunda tabla
            nuevos_registros = (session_scaizen_db.query(TablaDescargas)
                                .filter(~TablaDescargas.id.in_(ids_tabla2), 
                                        TablaDescargas.estado == 'finalizado', 
                                        TablaDescargas.id_tanque_fk > 0)
                                .order_by(asc(TablaDescargas.fecha_recepcion))  # Orden ascendente por fecha_recepcion
                                .all())

            nuevos_registros_mapeados = []
            for registro in nuevos_registros:
                orden = scaizen_db.BatchUclCargaDescarga.get_by_id_orden_fk(registro.id_orden_fk)
                if orden:
                    logging.debug(f"Procesando orden numero {registro.id_orden_fk} con tanque {registro.id_tanque_fk}: {registro}")
                    
                    telemedicon_tanque = scaizen_db.Telemedicion_tanques.get_for_id_tanque_fk(registro.id_tanque_fk)
                    logging.debug(f"telemedicon_tanque {telemedicon_tanque}: {telemedicon_tanque}")
                    
                    if telemedicon_tanque:
                        logging.debug(f'registro.id_tanque_fk: {registro.id_tanque_fk}')
                        logging.debug(f'telemedicon_tanque: {telemedicon_tanque}')
                        
                        medicion_tanque_start = scaizen_db.Rt_tanques.get_for_id_instrumentacion_fk_start(telemedicon_tanque.id_instrumentacion_fk, orden.fecha_inicio)
                        logging.debug(f'medicion_tanque_start: {medicion_tanque_start}')
                        
                        VolumenInicialTanque = 0
                        VolumenFinalTanque = 0
                        
                        if medicion_tanque_start:
                            MTanqueJsonStart = medicion_tanque_start.json
                            VolumenInicialTanque = MTanqueJsonStart['ucl_telemedicion']['data']['volumen_natural']
                        
                        VolumenFinalTanque = VolumenInicialTanque + orden.cantidad_despachada
                        id_proveedor_fk = -1
                        proveedor_info = scaizen_db.Proveedores.select_proveedor_by_id(registro.id_proveedor_fk)
                        if proveedor_info:
                            proveedor = ProveedorCV.select_by_rfc(proveedor_info.rfc)
                            if proveedor: id_proveedor_fk = proveedor.Id_Proveedor
                        
                        # Mapear los datos
                        nuevos_registros_mapeados.append({
                            'Id_fk': registro.id,
                            'NumeroDeOrden_Distribuidor': registro.id_orden_fk,
                            'id_proveedor_fk': id_proveedor_fk,
                            'Autotanque': scaizen_db.Autotanque.select_autotanque_by_id(registro.autotanque).numero if isinstance(registro.autotanque, int) else registro.autotanque,
                            'Producto': orden.producto,
                            'TanqueCodigo': scaizen_db.Tanque.get_for_id(registro.id_tanque_fk).codigo,
                            'TipoDeRegistro': 'D',
                            'VolumenInicialTanque': VolumenInicialTanque,
                            'VolumenInicialTanque_UM': 'UM04',
                            'VolumenFinalTanque': VolumenFinalTanque,
                            'VolumenRecepcion': orden.volumen_natural,
                            'VolumenRecepcion_UM': 'UM04',
                            'VolumenRecepcionNeto': orden.volumen_neto,
                            'VolumenRecepcionNeto_UM': 'UM04',
                            'Temperatura': orden.temperatura_promedio,
                            'PresionAbsoluta': 1.033,
                            'Costo': registro.monto_facturado,
                            'FechaYHoraInicialRecepcion': orden.fecha_inicio,
                            'FechaYHoraFinalRecepcion': orden.fecha_fin
                        })

            # Insertar los registros mapeados
            if nuevos_registros_mapeados:
                session_cv.bulk_insert_mappings(cls, nuevos_registros_mapeados)
                session_cv.commit()

        except Exception as e:
            error_trace = traceback.format_exc()
            logging.error(f"Exception: {str(e)}")
            logging.error(f"Traceback: {error_trace}")
            session_cv.rollback()
        finally:
            logging.debug(f"Finalizando la recuperacion de descargas del distribuidor.")
            session_cv.close()
            session_scaizen_db.close()

    @classmethod
    def select_by_id(cls, Id):
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id=Id).first()
        session.close()
        return consulta
    
    @classmethod
    def select_by_id_recepciones_fk(cls, id_recepciones_fk):
        session = SessionLocal()
        consulta = session.query(cls).filter_by(id_recepciones_fk=id_recepciones_fk).all()
        session.close()
        return consulta
    
    @classmethod
    def select_all(cls):
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta
    
    @classmethod
    def select_given_between_date_for_pagination(cls, fecha_inicio, fecha_fin, page_num=1, elementos_por_pagina=100):
        session = SessionLocal()
        try:
            # Contar el número total de registros en el rango de fechas
            total_descargas = (session.query(cls)
                            .filter(cls.FechaYHoraInicialRecepcion.between(fecha_inicio, fecha_fin))
                            .count())
            
            # Consulta con límite y offset para paginación
            consulta = (session.query(cls)
                        .filter(cls.FechaYHoraInicialRecepcion.between(fecha_inicio, fecha_fin))
                        .order_by(cls.Id.desc())
                        .limit(elementos_por_pagina)
                        .offset((page_num - 1) * elementos_por_pagina)  # Saltar elementos de páginas anteriores
                        .all())
            
            
            data_return = []
            # Aplicar hash a Id_RECEPCION para cada registro
            for registro in consulta:
                data = {
                    'registro': None,
                    'proveedor':'Desconocido',
                    'NoConsecutivo':0
                }
                data['NoConsecutivo'] = registro.Id
                registro.Id = config.encriptar_a_hex(clave_hex_hash, registro.Id)  # Generar hash SHA-256
                data['registro'] = registro
                proveedor_info = ProveedorCV.select_by_Id_Proveedor(registro.id_proveedor_fk)
                
                if proveedor_info:
                    data['proveedor'] = proveedor_info.Nombre_comercial
                    data['rfc'] = proveedor_info.RFC
                data_return.append(data)

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
        
        return data_return, total_descargas

    @classmethod
    def get_by_date_and_producto(cls, producto, fecha_inicio=None, fecha_fin=None):
        """Consulta registros por tipo y producto con fechas opcionales."""
        filters = []
        filters.append(cls.Producto == producto)
        filters.append(cls.FechaYHoraInicialRecepcion.between(fecha_inicio,fecha_fin))
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
        filters.append(cls.TanqueCodigo == tanque)
        filters.append(cls.Producto == product)
        filters.append(cls.FechaYHoraInicialRecepcion.between(date_start,date_end))
        try:
            session = SessionLocal()
            consulta = session.query(cls).filter(*filters).all()
            session.close()
            return consulta
        except Exception as e:
            logging.debug(f"Error al consultar en órdenes de operación carga: {e}")
            return None
    
    @classmethod
    def update_id_recepciones_fk(cls,id,id_recepciones_fk):
        session = SessionLocal()
        recepcion = recepcion = session.query(cls).filter_by(Id=id).first()
        if recepcion:
            logging.debug(f"id: {id},id_recepciones_fk: {id_recepciones_fk}")
            try:
                recepcion.id_recepciones_fk = id_recepciones_fk
                session.commit()  # Confirmamos los cambios en la base de datos
                return recepcion  # Devolvemos el objeto actualizado
            except Exception as e:
                session.rollback()  # Deshacemos cualquier cambio en caso de error
                raise e  # Opcional: se puede personalizar la excepción o devolver un mensaje
            finally:
                session.close()  # Cerramos la sesión en todos los casos
        else:
            logging.debug("No se encontro para update_id_recepciones_fk")
            return None  # Retornamos None si no se encontró el registro
        
class CfdisComercializador(Base):
    __tablename__= 'cfdis_comercializador'
    Id_CFDIS_comercializador = Column(Integer,primary_key=True, autoincrement=True)
    Id_nacional_fk = Column(Integer, ForeignKey('nacional.Id_NACIONAL'), nullable=False)
    #Id_extranjero_fk = Column(Integer, ForeignKey('extranjero.Id_EXTRANJERO'), nullable=True)
    #Id_descargas_comercializador_fk = Column(Integer,ForeignKey('descargas_comercializador.Id'), nullable=True)
    CFDI = Column(String(45),nullable=False)
    TipoCFDI = Column(String(45),nullable=False)
    PrecioVentaOCompraOContrap = Column(Float,nullable=False)
    FechaYHoraTransaccion = Column(DateTime,nullable=False)
    VolumenDocumentado = Column(Float,nullable=False)
    VolumenDocumentado_UM = Column(String(45),nullable=False)


    def __repr__(self):
        return (f"<CFDI(Id_CFDIS_comercializador={self.Id_CFDIS_comercializador}, CFDI={self.CFDI})>")



    @classmethod
    def add(cls,Id_nacional_fk,CFDI,
            TipoCFDI,PrecioVentaOCompraOContrap,FechaYHoraTransaccion,
            VolumenDocumentado,VolumenDocumentado_UM):
        nuevo_cfdi = cls(
            Id_nacional_fk=Id_nacional_fk,
            CFDI = CFDI,
            TipoCFDI = TipoCFDI,
            PrecioVentaOCompraOContrap=PrecioVentaOCompraOContrap,
            FechaYHoraTransaccion = FechaYHoraTransaccion,
            VolumenDocumentado = VolumenDocumentado,
            VolumenDocumentado_UM = VolumenDocumentado_UM
        )
        result_data = add_to_table(nuevo_cfdi)
        return result_data.Id_CFDIS_comercializador  if result_data else None


    @classmethod
    def select_by_id(cls, Id):
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id_CFDIS_comercializador=Id).first()
        session.close()
        return consulta

    @classmethod
    def select_by_id_nacional_fk(cls, id_nacional_fk):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id_nacional_fk=id_nacional_fk).all() 
        session.close()
        return consulta

    @classmethod
    def select_all(cls):
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta

class CfdisDistribuidor(Base):
    __tablename__= 'cfdis_distribuidor'
    Id_CFDIS_distribuidor   = Column(Integer,primary_key=True, autoincrement=True)
    Id_nacional_fk = Column(Integer, ForeignKey('nacional.Id_NACIONAL'), nullable=True)

    CFDI = Column(String(45),nullable=False)
    TipoCFDI = Column(String(45),nullable=False)
    PrecioVentaOCompraOContrap = Column(Float,nullable=False)
    FechaYHoraTransaccion = Column(DateTime,nullable=False)
    VolumenDocumentado = Column(Float,nullable=False)
    VolumenDocumentado_UM = Column(String(45),nullable=False)

    def __repr__(self):
        return (f"<CFDI(Id_CFDIS={self.Id_CFDIS_distribuidor}, CFDI={self.CFDI})>")

    @classmethod
    def add(cls,Id_nacional_fk,CFDI, TipoCFDI,PrecioVentaOCompraOContrap, FechaYHoraTransaccion, VolumenDocumentado,VolumenDocumentado_UM):
        nuevo_cfdi = cls(
            Id_nacional_fk =Id_nacional_fk,
            CFDI = CFDI,
            TipoCFDI = TipoCFDI,
            PrecioVentaOCompraOContrap=PrecioVentaOCompraOContrap,
            FechaYHoraTransaccion = FechaYHoraTransaccion,
            VolumenDocumentado = VolumenDocumentado,
            VolumenDocumentado_UM = VolumenDocumentado_UM
        )
        result_data = add_to_table(nuevo_cfdi)
        return result_data.Id_CFDIS_distribuidor if result_data else None


    @classmethod
    def select_by_id(cls, Id):
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id_CFDIS_distribuidor=Id).first()
        session.close()
        return consulta

    @classmethod
    def select_by_id_nacional_fk(cls, id_nacional_fk):
        consulta = None
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id_nacional_fk=id_nacional_fk).all() 
        session.close()
        return consulta

    @classmethod
    def select_all(cls):
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta
    
class ProveedorCV(Base):
    __tablename__ = 'proveedor_cv'

    Id_Proveedor = Column(Integer, primary_key=True)
    Codigo_interno = Column(Integer, nullable=False)
    Nombre_comercial = Column(String(150), nullable=False)
    Razon_Social = Column(String(150), nullable=False)
    RFC = Column(String(150), nullable=False)
    Dirección = Column(String(150), nullable=False)
    Telefono = Column(String(150), nullable=False)
    Email = Column(String(150), nullable=False)
    Información_adicional = Column(String(150), nullable=False)
    PermisoClienteOProveedor = Column(String(150),nullable=True)
    @classmethod
    def select_all(cls):
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta

    @classmethod
    def select_by_Id_Proveedor(cls, id_proveedor):
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id_Proveedor=id_proveedor).first()
        session.close()
        return consulta

    @classmethod
    def select_by_rfc(cls, rfc):
        session = SessionLocal()
        consulta = session.query(cls).filter_by(RFC=rfc).first()
        session.close()
        return consulta

    @classmethod
    def select_by_comercial_name(cls, nombre_comercial):
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Nombre_comercial=nombre_comercial).first()
        session.close()
        return consulta
    
    @classmethod
    def select_given_between_date_for_pagination(cls, page_num=1,elementos_por_pagina=100):
        session = SessionLocal()
        try:
                        # Contar el número total de registros en el rango de fechas
            total_proveedor = (session.query(cls).count())
            # Consulta con límite y offset para paginación
            consulta = (session.query(cls)
                        .order_by(cls.Id_Proveedor.desc())
                        .limit(elementos_por_pagina)
                        .offset((page_num - 1) * elementos_por_pagina)  # Saltar elementos de páginas anteriores
                        .all())
 
            data =[]

            for item in consulta:
                data_item = {'Id_proveedor': item.Id_Proveedor,
                         'codigo': item.Codigo_interno,
                         'nombre_comercial': item.Nombre_comercial,
                         'razon': item.Razon_Social,
                         'rfc': item.RFC,
                         'direccion': item.Dirección,
                         'telefono': item.Telefono,
                         'email': item.Email,
                         'informacion': item.Información_adicional,
                         'permisoclienteoproveedor':item.PermisoClienteOProveedor,
                            }
                data.append(data_item)
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
        
        logging.debug(consulta)

        return data,total_proveedor





class ClienteCV(Base):
    __tablename__ = 'cliente_cv'

    Id_cliente = Column(Integer, primary_key=True)
    Codigo_interno = Column(Integer, nullable=False)
    Nombre_comercial = Column(String(100), nullable=False)
    Razon_social = Column(String(100), nullable=False)
    RFC = Column(String(13), nullable=False)
    Regimen_fiscal = Column(String(45), nullable=False)
    Direccion = Column(String(150), nullable=False)
    Codigo_postal = Column(String(5), nullable=False)
    Telefono = Column(String(10), nullable=False)
    Email = Column(String(45), nullable=False)
    Informacion_adicional = Column(String(150), nullable=False)
    PermisoClienteOProveedor = Column(String(150),nullable=True)

    @classmethod
    def select_all(cls):
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta

    @classmethod
    def select_by_Id_cliente(cls, id_cliente):
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id_cliente=id_cliente).first()
        session.close()
        return consulta

    @classmethod
    def select_by_rfc(cls, rfc):
        session = SessionLocal()
        consulta = session.query(cls).filter_by(RFC=rfc).first()
        session.close()
        return consulta

    @classmethod
    def select_by_comercial_name(cls, nombre_comercial):
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Nombre_comercial=nombre_comercial).first()
        session.close()
        return consulta

    @classmethod
    def select_for_pagination(cls,page_num=1, elementos_por_pagina=100):
        session = SessionLocal()
        try:
            # Contar el número total de registros en el rango de fechas
            total_usuarios= (session.query(cls).count())
            # Consulta con límite y offset para paginación
            consulta = (session.query(cls)
                    .order_by(cls.Id_cliente.desc())
                    .limit(elementos_por_pagina)
                    .offset((page_num - 1) * elementos_por_pagina)  # Skip elements from previous pages
                    .all())

            # Aplicar hash a Id_RECEPCION para cada registro
            for registro in consulta:
                registro.Id_cliente = config.encriptar_a_hex(clave_hex_hash, registro.Id_cliente)  # Generar hash SHA-256

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
        
        return consulta, total_usuarios
    



    @classmethod
    def select_given_between_date_for_pagination(cls, page_num=1,elementos_por_pagina=100):
        session = SessionLocal()
        try:
                        # Contar el número total de registros en el rango de fechas
            total_clientes = (session.query(cls).count())
            # Consulta con límite y offset para paginación
            consulta = (session.query(cls)
                        .order_by(cls.Id_cliente.desc())
                        .limit(elementos_por_pagina)
                        .offset((page_num - 1) * elementos_por_pagina)  # Saltar elementos de páginas anteriores
                        .all())
 
            data =[]
            for item in consulta:
                data_item = {'id_cliente': item.Id_cliente,
                         'codigo': item.Codigo_interno,
                         'nombre_comercial': item.Nombre_comercial,
                         'razon': item.Razon_social,
                         'rfc': item.RFC,
                         'regimen': item.Regimen_fiscal,
                         'direccion': item.Direccion,
                         'cod_pos': item.Codigo_postal,
                         'telefono': item.Telefono,
                         'email': item.Email,
                         'informacion': item.Informacion_adicional,
                         'permisoclienteoproveedor':item.PermisoClienteOProveedor,

                            }
                data.append(data_item)
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
        
        logging.debug(consulta)

        return data,total_clientes









class EstacionesCV(Base):
    __tablename__ = 'estaciones_cv'

    Id_estacion = Column(Integer, primary_key=True)
    Codigo_interno = Column(Integer, nullable=False)
    Permiso_cre = Column(String(11), nullable=False)
    Número_de_estación = Column(Integer, nullable=True)  # Cambiado a nullable=True para manejar el DEFAULT NULL
    Nombre_comercial = Column(String(150), nullable=False)
    RFC = Column(String(13), nullable=False)
    Regimen_fiscal = Column(String(45), nullable=False)
    Nombre_del_gerente = Column(String(45), nullable=False)
    Dirección = Column(String(150), nullable=False)
    Codigo_postal = Column(Integer, nullable=False)
    Teléfono = Column(Integer, nullable=False)  # Manteniendo como Integer, puedes cambiar a String si deseas
    Email = Column(String(45), nullable=False)
    Información_adicional = Column(String(150), nullable=False)
    PermisoClienteOProveedor = Column(String(150), nullable=False)

    @classmethod
    def add(cls, codigo_interno, permiso_cre, numero_de_estacion, nombre_comercial, rfc, regimen, 
            nombre_del_gerente, direccion, cod_pos, telefono, email, informacion_adicional):
        nueva_estacion = cls(
            Codigo_interno=codigo_interno,
            Permiso_cre=permiso_cre,
            Número_de_estación=numero_de_estacion,
            Nombre_comercial=nombre_comercial,
            RFC=rfc,
            Regimen_fiscal=regimen,
            Nombre_del_gerente=nombre_del_gerente,
            Dirección=direccion,
            Codigo_postal=cod_pos,
            Teléfono=telefono,
            Email=email,
            Información_adicional=informacion_adicional,
            PermisoClienteOProveedor=permiso_cre
        )
        result_data = add_to_table(nueva_estacion)
        return result_data.Id_estacion if result_data else None
    
    @classmethod
    def select_all(cls):
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta

    @classmethod
    def select_by_Id_estacion(cls, id_estacion):
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id_estacion=id_estacion).first()
        session.close()
        return consulta

    @classmethod
    def select_by_rfc(cls, rfc):
        session = SessionLocal()
        consulta = session.query(cls).filter_by(RFC=rfc).first()
        session.close()
        return consulta


    @classmethod
    def select_given_between_date_for_pagination(cls, page_num=1,elementos_por_pagina=10):
        session = SessionLocal()
        try:
                        # Contar el número total de registros en el rango de fechas
            total_estaciones = (session.query(cls).count())
            # Consulta con límite y offset para paginación
            consulta = (session.query(cls)
                        .order_by(cls.Id_estacion.desc())
                        .limit(elementos_por_pagina)
                        .offset((page_num - 1) * elementos_por_pagina)  # Saltar elementos de páginas anteriores
                        .all())

            data =[]
            for item in consulta:
                data_item = {'id_estaciones': item.Id_estacion,
                            'codigo_interno': item.Codigo_interno,
                            'Permiso_cre': item.Permiso_cre,
                            'Numero_de_estacion': item.Número_de_estación,
                            'Nombre_comercial': item.Nombre_comercial, 
                            'RFC': item.RFC,
                            'regimen': item.Regimen_fiscal,
                            'Nombre_del_gerente':item.Nombre_del_gerente,
                            'Direccion':item.Dirección,
                            'cod_pos': item.Codigo_postal,
                            'Telefono':item.Teléfono,
                            'Email':item.Email,
                            'Informacion_adicional':item.Información_adicional,
                            'PermisoClienteOProveedor':item.PermisoClienteOProveedor
                            }
                data.append(data_item)
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
        
        logging.debug(consulta)

        return data,total_estaciones

    @classmethod
    def select_by_comercial_name(cls, nombre_comercial):
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Nombre_comercial=nombre_comercial).first()
        session.close()
        return consulta

class Usuario_Cv(Base):
    __tablename__ = 'usuarios_cv'

    Id  = Column(Integer, primary_key=True, autoincrement=True)  # Cambiado a 'id'
    Nombre = Column(String, nullable=False)  # Cambiado a 'String'
    nombre_completo = Column(String, nullable=False)
    Telefono = Column(String, nullable=True)
    Password = Column(String, nullable=False)
    Tipo_usuario = Column(String, nullable=True)
    IdRol_fk = Column(Integer, ForeignKey('roles.IdRol'), nullable=False)
    Cambio_contraseña = Column(Boolean , nullable=False)  # Cambiado a 'cambio_contrasena'
    Estatus_usuario = Column(Enum('activo', 'inactivo', 'borrado', name='estatus_usuario'))  # Consistencia en el nombre
    ultimo_cambio_pwd = Column(DateTime, nullable=True, default=datetime.now())  # Cambiado a 'ultimo_cambio_pwd'
    
    @classmethod
    def add(cls,nombre,nombre_completo,telefono,password,IdRol_fk,estatus_usuario):
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        nuevo_usuario=cls(
                    Nombre= nombre,
                    nombre_completo = nombre_completo,
                    Telefono = telefono,
                    Password = hashed_password,
                    IdRol_fk = IdRol_fk,
                    Cambio_contraseña = 1,
                    Estatus_usuario = estatus_usuario
        )
        result_data = add_to_table(nuevo_usuario)
        return result_data.Id if result_data else None

    @classmethod
    def delete(cls, id):
        session = SessionLocal()
        try:
            # Obtener el registro por ID
            record = session.query(cls).filter_by(Id=id).first()
            if record:
                session.delete(record)
                session.commit()
                
                # Verificar si el registro aún existe
                check_record = session.query(cls).filter_by(Id=id).first()
                return check_record is None  # Si no existe, devuelve True
            return False  # No se encontró el registro inicial
        except Exception as e:
            session.rollback()
            logging.debug(f"Error al eliminar el registro: {e}")
            return False
        finally:
            session.close()
        
    @classmethod
    def update(cls, id,nombre = None,nombre_completo = None,telefono = None, password = None, id_rol = None,cambio_contraseña = None, estatus_usuario = None, ultimo_cambio_pwd = None): 
        session = SessionLocal()
        try:
            consulta = session.query(cls).filter_by(Id=id).first()    
            if consulta:
                if nombre  is not None:consulta.Nombre = nombre
                if nombre_completo  is not None:consulta.nombre_completo = nombre_completo
                if telefono  is not None: consulta.Telefono = telefono
                if password  is not None:
                    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                    consulta.Password = hashed_password
                if id_rol  is not None: consulta.IdRol_fk = id_rol
                if cambio_contraseña is not None:  consulta.Cambio_contraseña = cambio_contraseña
                if estatus_usuario  is not None:  consulta.Estatus_usuario = estatus_usuario
                if ultimo_cambio_pwd is not None: consulta.ultimo_cambio_pwd = datetime.now()
                session.commit()  # Guardar cambios
                session.refresh(consulta)

            else:
                raise ValueError("Usuario no encontrado")  
        except Exception as e:
            session.rollback()  # Revertir cambios en caso de error
            raise e  
        finally:
            session.close()  # Cerrar la sesión
        return consulta if consulta else None
    
    @classmethod
    def update_user(cls, id,nombre,nombre_completo,password, id_rol): 
        session = SessionLocal()
        try:
            consulta = session.query(cls).filter_by(Id=id).first()    
            if consulta:
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                consulta.Nombre = nombre
                consulta.nombre_completo = nombre_completo
                consulta.Password = hashed_password
                consulta.IdRol_fk = id_rol
                session.commit()  # Guardar cambios
                session.refresh(consulta)

            else:
                raise ValueError("Usuario no encontrado")  
        except Exception as e:
            session.rollback()  # Revertir cambios en caso de error
            raise e  
        finally:
            session.close()  # Cerrar la sesión
        return consulta if consulta else None

    @classmethod
    def change_password(cls, id, pwd, admin=False): 
        session = SessionLocal()
        try:
            consulta = session.query(cls).filter_by(Id=id).first()    
            if consulta:
                hashed_password = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt())
                changepwd = 0
                if admin:
                    changepwd = 1
                consulta.Cambio_contraseña = changepwd
                consulta.Password = hashed_password
                session.commit()  # Guardar cambios
            else:
                raise ValueError("Usuario no encontrado")  
        except Exception as e:
            session.rollback()  # Revertir cambios en caso de error
            raise e  
        finally:
            session.close()  # Cerrar la sesión

    @classmethod
    def select_by_id(cls,id_usuario):
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Id = id_usuario).first()
        session.close()
        return consulta
    
    @classmethod
    def select_by_name(cls,nombre):
        session = SessionLocal()
        consulta = session.query(cls).filter_by(Nombre = nombre).first()
        session.close()
        return consulta
    
    @classmethod
    def select_all(cls):
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta
    
    @classmethod
    def select_for_pagination(cls,page_num=1, elementos_por_pagina=100):
        session = SessionLocal()
        try:
            # Contar el número total de registros en el rango de fechas
            total_usuarios= (session.query(cls).count())
            # Consulta con límite y offset para paginación
            consulta = (session.query(cls)
                    .order_by(cls.Id.desc())
                    .limit(elementos_por_pagina)
                    .offset((page_num - 1) * elementos_por_pagina)  # Skip elements from previous pages
                    .all())

            data_return = []
            # Aplicar hash a Id_RECEPCION para cada registro
            for registro in consulta:
                data = {
                    'usuario': None,
                    'rol':'Desconocido'
                }
                registro.Id = config.encriptar_a_hex(clave_hex_hash, registro.Id)  # Generar hash SHA-256
                rol = Roles.select_by_IdRol(registro.IdRol_fk)
                data['rol'] = rol.NombreRol if rol else "Desconocido" if registro.IdRol_fk != None else "Sin Rol Asignado"
                registro.IdRol_fk = config.encriptar_a_hex(clave_hex_hash, registro.IdRol_fk)  # Generar hash SHA-256
                registro.Password = None
                data['usuario'] = registro
                data_return.append(data)

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
        
        return data_return, total_usuarios

class Roles(Base):
    __tablename__ = 'roles'

    IdRol = Column(Integer, primary_key=True)
    NombreRol = Column(String(100), unique=True, nullable=False)
    Descripcion = Column(String(400), unique=True, nullable=False)
    Permisos = Column(JSON, nullable=False)

    @classmethod
    def add(cls,nombrerol,descripcion, permisos):
        nuevo_rol=cls(
            NombreRol = nombrerol,
            Descripcion= descripcion,
            Permisos = permisos
        )
        result_data = add_to_table(nuevo_rol)
        return result_data if result_data else None
    
    @classmethod
    def delete(cls, IdRol):
        try:
            session = SessionLocal()
            consulta = session.query(cls).filter_by(IdRol=IdRol).first()
            if consulta:
                session.delete(consulta)
                session.commit()
            verificar = session.query(cls).filter_by(IdRol=IdRol).first()
        except Exception as e:
            session.rollback()
            print(f"Error: {e}")
            verificar = e
        finally:
            session.close()
        return verificar

    @classmethod
    def update(cls, id,nombreRol = None,descripcion = None,permisos = None): 
        session = SessionLocal()
        try:
            consulta = session.query(cls).filter_by(IdRol=id).first()    
            if consulta:
                if nombreRol: consulta.NombreRol = nombreRol
                if descripcion: consulta.Descripcion = descripcion
                #if permisos: consulta.Permisos = permisos
                if permisos is not None:
                    consulta.Permisos = permisos
                session.commit()  # Guardar cambios
                session.refresh(consulta)

            else:
                raise ValueError("Rol no encontrado")  
        except Exception as e:
            session.rollback()  # Revertir cambios en caso de error
            raise e  
        finally:
            session.close()  # Cerrar la sesión
        return consulta if consulta else None

    @classmethod
    def select_by_IdRol(cls, IdRol):
        session = SessionLocal()
        consulta = session.query(cls).filter_by(IdRol=IdRol).first()
        session.close()
        return consulta
    
    @classmethod
    def select_all(cls):
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta
    
    @classmethod
    def select_for_pagination(cls,page_num=1, elementos_por_pagina=100):
        session = SessionLocal()
        try:
            # Contar el número total de registros en el rango de fechas
            total_roles= (session.query(cls).count())
            # Consulta con límite y offset para paginación
            consulta = (session.query(cls)
                    .order_by(cls.IdRol.desc())
                    .limit(elementos_por_pagina)
                    .offset((page_num - 1) * elementos_por_pagina)  # Skip elements from previous pages
                    .all())
            perms_permitidos = config.PERMISOS_VALIDOS
            numero_perms_permitidos = config.CONTAR_NUMERO_PERMISOS(perms_permitidos)
            logging.debug('numero_perms_permitidos')
            logging.debug(numero_perms_permitidos)
            for registro in consulta:
                numero_perms = config.CONTAR_NUMERO_PERMISOS(registro.Permisos)
                logging.debug('numero_perms')
                logging.debug(numero_perms)
                registro.IdRol = config.encriptar_a_hex(clave_hex_hash, registro.IdRol)
                if numero_perms ==  numero_perms_permitidos:  registro.Permisos = {"Todos":{"label":"Todos"}}
                else: 
                    registro.Permisos = config.FILTER_JSON(perms_permitidos,registro.Permisos)
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
        
        return consulta, total_roles

class UsuarioActual(UserMixin):
    def __init__(self,User, Rol):
        super().__init__()
        self.id = User.Id
        self.Username = User.Nombre
        self.FullName = User.nombre_completo
        self.RolName = Rol.NombreRol if Rol else "Sin Rol"
        self.RolPerms = Rol.Permisos if Rol else {}
        self.Cambio_contraseña = User.Cambio_contraseña
        self.Cambio_contraseña = User.Cambio_contraseña
        self.ultimo_cambio_pwd = User.ultimo_cambio_pwd

class Configuraciones(Base):
    __tablename__ = 'configuraciones'

    id = Column(Integer, primary_key=True, autoincrement=True)
    clave = Column(String(100), nullable=False)
    valor = Column(Text, nullable=False)
    descripcion = Column(Text, nullable=True)
    tipo = Column(String(50), nullable=False, default='texto')
    creado_en = Column(DateTime, nullable=False, default=datetime.now)
    actualizado_en = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return (f"<Configuraciones(id={self.id}, clave={self.clave}, tipo={self.tipo}, creado_en={self.creado_en})>")

    @classmethod
    def add(cls, clave, valor, descripcion=None, tipo='texto'):
        nueva_configuracion = cls(
            clave=clave,
            valor=valor,
            descripcion=descripcion,
            tipo=tipo
        )
        result_data = add_to_table(nueva_configuracion)
        return result_data.id if result_data else None

    @classmethod
    def select_by_id(cls, id):
        session = SessionLocal()
        consulta = session.query(cls).filter_by(id=id).first()
        session.close()
        return consulta

    @classmethod
    def select_by_clave(cls, clave):
        session = SessionLocal()
        consulta = session.query(cls).filter_by(clave=clave).first()
        session.close()
        return consulta

    @classmethod
    def select_all(cls):
        session = SessionLocal()
        consulta = session.query(cls).all()
        session.close()
        return consulta

    @classmethod
    def update(cls, id, clave=None, valor=None, descripcion=None, tipo=None):
        session = SessionLocal()
        try:
            consulta = session.query(cls).filter_by(id=id).first()
            if consulta:
                if clave is not None:
                    consulta.clave = clave
                if valor is not None:
                    consulta.valor = valor
                if descripcion is not None:
                    consulta.descripcion = descripcion
                if tipo is not None:
                    consulta.tipo = tipo
                session.commit()
                session.refresh(consulta)
            else:
                raise ValueError("Configuración no encontrada")
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
        return consulta if consulta else None

    @classmethod
    def delete(cls, id):
        session = SessionLocal()
        try:
            consulta = session.query(cls).filter_by(id=id).first()
            if consulta:
                session.delete(consulta)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


