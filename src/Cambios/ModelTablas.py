from .entities.Tablas import Tabla_carga
from .entities.Tablas import Tabla_descargas
from .entities.Tablas import Tabla_eventos
from .entities.Tablas import Tabla_operaciones_mensuales
from .entities.Tablas import Tabla_operaciones_diarias
from .entities.Tablas import Tabla_tanques
from .entities.Tablas import Tabla_numero_tanques
from .entities.Tablas import Tabla_numero_clientes
from .entities.Tablas import Tabla_Cliente_consulta
from .entities.Tablas import Tabla_Cliente_actualizar
from .entities.Tablas import Tabla_Proveedor_actualizar
from .entities.Tablas import Tabla_numero_estaciones
from .entities.Tablas import Tabla_Estacion_actualizar
from .entities.Tablas import Tabla_numero_proveedores
from .entities.Tablas import Tabla_estaciones_consulta

from .entities.Tablas import Tabla_usuarios_consulta
from .entities.Tablas import Tabla_Usuario_actualizar
from .entities.Tablas import Tabla_informetanque_dia_inicio
from .entities.Tablas import Tabla_batch_diario_tanques
from .entities.Tablas import Tabla_batch_diario_total_tanques
from .entities.Tablas import Tabla_batch_mensual_tanques
from .entities.Tablas import Tabla_informetanque_dia_fin
from .entities.Tablas import lectura_tanque_antes_batch
from .entities.Tablas import lectura_tanque_inicio__fin_dia
from .entities.Tablas import lectura_tanque_posterior_batch
from .entities.Tablas import Tabla_distribuidor_venta_consultar
from .entities.Tablas import Tabla_Proveedores_consulta
from .entities.Tablas import batch_ucl_carga_descarga
#from .entities.Tablas import valor_tanque_inicio
#from .entities.Tablas import valor_tanque_fin
from .entities.Tablas import Tabla_User

from .entities.Tablas import Roles

from datetime import datetime

from sqlalchemy.sql import text
from sqlalchemy.exc import SQLAlchemyError


from werkzeug.security import generate_password_hash

import hashlib
import json
from models import scaizen_cv as cv
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(filename)s - line %(lineno)d : %(message)s'
)

class ModelTablas():
    
    @classmethod 
    def cargas(cls, db, carga, page_num, elementos_por_pagina):
        query_main = text("""
            SELECT COUNT(*) AS total_cargas 
            FROM ordenes_de_operacion_carga 
            JOIN batch_ucl_carga_descarga 
            ON ordenes_de_operacion_carga.id_orden_fk = batch_ucl_carga_descarga.id_orden_fk 
            WHERE ordenes_de_operacion_carga.date_created BETWEEN :fecha_inicio AND :fecha_fin 
            AND ordenes_de_operacion_carga.estado = 'finalizado' 
            AND batch_ucl_carga_descarga.tipo = 'carga'
        """)    
        params = {'fecha_inicio': carga.fecha_inicio_busqueda, 
                'fecha_fin': carga.fecha_fin_busqueda} 

        query_main_2 = text("""
            SELECT ordenes_de_operacion_carga.id_orden_fk, ordenes_de_operacion_carga.date_created, 
                ordenes_de_operacion_carga.fecha_entrega, ordenes_de_operacion_carga.ucl_operador, 
                ordenes_de_operacion_carga.cantidad_programada, ordenes_de_operacion_carga.producto, 
                batch_ucl_carga_descarga.tipo, ordenes_de_operacion_carga.estado  
            FROM ordenes_de_operacion_carga                     
            JOIN batch_ucl_carga_descarga 
            ON ordenes_de_operacion_carga.id_orden_fk = batch_ucl_carga_descarga.id_orden_fk 
            WHERE ordenes_de_operacion_carga.date_created BETWEEN :fecha_inicio_busqueda AND :fecha_fin_busqueda
            AND ordenes_de_operacion_carga.estado = 'finalizado' 
            AND batch_ucl_carga_descarga.tipo = 'carga'  
            LIMIT :elementos_por_pagina OFFSET :elementos_por_pagina_2
        """)
        params_2 = {'fecha_inicio_busqueda': carga.fecha_inicio_busqueda,
                    'fecha_fin_busqueda': carga.fecha_fin_busqueda, 
                    'elementos_por_pagina': elementos_por_pagina,
                    'elementos_por_pagina_2': (page_num - 1) * elementos_por_pagina}

        try:
            with db.engine.connect() as connection:
                # Ejecutar la primera consulta
                with connection.execute(query_main, params) as cursor:
                    consultas = cursor.fetchone()
                    total = consultas[0] if consultas else 0

                # Ejecutar la segunda consulta
                with connection.execute(query_main_2, params_2) as cursor_2:
                    rows = cursor_2.fetchall()
                    cargas = []  # Lista para almacenar objetos Tabla_carga
                
                    if rows:
                        for row in rows:
                            carga_2 = Tabla_carga(None, None, row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])                    
                            cargas.append(carga_2)
                    return cargas, total

        except Exception as ex:
            raise Exception(f"Error en la consulta de cargas: {ex}")    
  
    @classmethod 
    def descargas(self, db, descargas, page_num,elementos_por_pagina): #referencia al propio objeto, conexion a la db, para hacer la autenticacion
        
        query_main = text("""SELECT  COUNT(*) AS total_descargas   
            FROM ordenes_de_operacion_descarga
            JOIN batch_ucl_carga_descarga ON ordenes_de_operacion_descarga.id_orden_fk  = batch_ucl_carga_descarga.id_orden_fk 
            WHERE ordenes_de_operacion_descarga.date_created BETWEEN :fecha_inicio AND :fecha_fin
            AND ordenes_de_operacion_descarga.estado = 'finalizado' AND batch_ucl_carga_descarga.tipo = 'descarga' LIMIT 10 OFFSET 0""")
        params = {'fecha_inicio': descargas.fecha_inicio_busqueda, 
                'fecha_fin':  descargas.fecha_fin_busqueda} 
        
        query_main_2 = text("""SELECT ordenes_de_operacion_descarga.id_orden_fk, ordenes_de_operacion_descarga.date_created, 
            ordenes_de_operacion_descarga.fecha_recepcion,  ordenes_de_operacion_descarga.ucl_operador, ordenes_de_operacion_descarga.cantidad_programada, 
            ordenes_de_operacion_descarga.producto, batch_ucl_carga_descarga.tipo, ordenes_de_operacion_descarga.estado  
            FROM ordenes_de_operacion_descarga
            JOIN batch_ucl_carga_descarga ON ordenes_de_operacion_descarga.id_orden_fk  = batch_ucl_carga_descarga.id_orden_fk 
            WHERE ordenes_de_operacion_descarga.date_created BETWEEN :fecha_inicio AND :fecha_fin 
            AND ordenes_de_operacion_descarga.estado = 'finalizado' AND batch_ucl_carga_descarga.tipo = 'descarga' LIMIT :elementos_por_pagina OFFSET :elementos_por_pagina_2""")
        params_2 = {'fecha_inicio': descargas.fecha_inicio_busqueda, 
                'fecha_fin':  descargas.fecha_fin_busqueda,
                'elementos_por_pagina': elementos_por_pagina,
                'elementos_por_pagina_2': (page_num - 1) * elementos_por_pagina
                } 
        try:
            with db.engine.connect() as connection:
                with connection.execute(query_main, params) as cursor:
                    consultas = cursor.fetchone()
                    total =  consultas[0]

                with connection.execute(query_main_2, params_2) as cursor_2:
                    rows = cursor_2.fetchall()
                    descargas = []  # Lista para almacenar objetos Tabla_carga
                
                    if rows != None:
                        for row in rows:
                            descargas_2 = Tabla_descargas(None, None, row[0], row[1], row[2], row[3], row[4], row[5],row[6], row[7])                    
                            descargas.append(descargas_2)
        
                        return descargas,total
                    else:
                        return rows

        except Exception as ex:
            raise Exception(f"Error en la consulta de cargas: {ex}")    



#    @classmethod 
#    def eventos(self, db, eventos,page_num,elementos_por_pagina): #referencia al propio objeto, conexion a la db, para hacer la autenticacion
#        try:
#           cursor = db.connection.cursor()
#           sql_1="""SELECT COUNT(*) AS total_eventos 
#                    FROM eventos 
#                    JOIN usuarios_scaizen ON eventos.id_user_creator = usuarios_scaizen.id_user_creator 
#                    WHERE eventos.fecha BETWEEN  %s AND %s """
#           cursor.execute(sql_1, (eventos.fecha_dia_eventos,eventos.fecha_dia_eventos_2,))
#           consultas = cursor.fetchone()
#           total =  consultas[0]

#           sql_2 = """SELECT eventos.id ,eventos.fecha,usuarios_scaizen.nombre,eventos.mensaje,eventos.proceso,eventos.tipo FROM eventos 
#           JOIN usuarios_scaizen ON eventos.id_user_creator = usuarios_scaizen.id_user_creator 
#           WHERE eventos.fecha BETWEEN  %s AND %s  LIMIT %s OFFSET %s"""
#           cursor.execute(sql_2, (eventos.fecha_dia_eventos,
#                eventos.fecha_dia_eventos_2,
#                elementos_por_pagina, 
#                ((page_num - 1) * elementos_por_pagina) ))
#           rows = cursor.fetchall()
#           eventos = []
#           if rows != None:
#                for row in rows:
#                        eventos_2 = Tabla_eventos(None,None,row[0],row[1],row[2],row[3], row[4],row[5])
#                        eventos.append(eventos_2)
#                return eventos,total
#           else:
#                return rows
            
#        except Exception as ex:
#            raise Exception(ex)  
#            print("Error:", ex)
  
#        finally:
#            cursor.close()#Cierro la conexión    
   
    @classmethod
    def tanques(self,db,page_num,elementos_por_pagina):
        query_main = text(""" SELECT COUNT(*) AS Total_tanques 
                        FROM telemedicion_tanques
                        JOIN tanques ON telemedicion_tanques.id_tanque_fk = tanques.id WHERE telemedicion_tanques.id_tanque_fk = tanques.id;
                        """)
        query_main_2 = text("""SELECT telemedicion_tanques.id, tanques.producto, tanques.tipo_venta, tanques.tipo_a_recibo, telemedicion_tanques.codigo
            FROM telemedicion_tanques
            JOIN tanques ON telemedicion_tanques.id_tanque_fk = tanques.id WHERE telemedicion_tanques.id_tanque_fk = tanques.id LIMIT :elementos_por_pagina OFFSET :elementos_por_pagina_2
              """)
        params_2 = {'elementos_por_pagina': elementos_por_pagina,
                'elementos_por_pagina_2': (page_num - 1) * elementos_por_pagina
                } 
        try:
            with db.engine.connect() as connection:
                with connection.execute(query_main) as cursor:
                    consultas = cursor.fetchone()
                    total =  consultas[0]
                with connection.execute(query_main_2,params_2) as cursor_2:
                    rows = cursor_2.fetchall()
                    tanques = []
                    if rows != None:
                        for row in rows:
                                tanques_2 = Tabla_tanques(row[0],row[1],row[2],row[3], row[4])
                                tanques.append(tanques_2)
                        return tanques,total
                    else:
                        return rows

        except Exception as ex:
            raise Exception(ex)    
  
    
    @classmethod
    def numero_tanques(self,db):
        query_main = text("SELECT id, codigo FROM tanques")
        try:
            with db.engine.connect() as connection:
                with connection.execute(query_main) as cursor:
                    rows = cursor.fetchall()
                    cantidad_tanques = []
                    if rows != None:
                        for row in rows:
                                cantidad_tanques_2 = Tabla_numero_tanques(row[0],row[1] )
                                cantidad_tanques.append(cantidad_tanques_2)
                        return cantidad_tanques 
                    else:
                        return rows
        except Exception as ex:
            raise Exception(ex)    
        finally:
            cursor.close()#Cierro la conexión   


    @classmethod
    def comercializadora_reporte_diario_tanque(self,db,busqueda_tanque):
        query_main = text("""SELECT id_orden_fk, estado, 'carga' AS tipo, fecha_carga AS fecha 
                            FROM `ordenes_de_operacion_carga` 
                            WHERE id_tanque_fk = :id AND estado = 'finalizado' AND
                            fecha_carga BETWEEN :fecha_inicio AND :fecha_fin UNION
                                            
                            SELECT id_orden_fk, estado, 'descarga' AS tipo, fecha_recepcion AS fecha 
                            FROM `ordenes_de_operacion_descarga` 
                            WHERE id_tanque_fk = :id AND estado = 'finalizado' AND fecha_recepcion BETWEEN :fecha_inicio AND :fecha_fin UNION 
                                            
                            SELECT id_orden_fk, estado, 'reingreso' AS tipo, fecha_recepcion AS fecha 
                            FROM `ordenes_de_operacion_reingreso` WHERE id_tanque_fk = :id AND estado = 'finalizado' AND fecha_recepcion BETWEEN :fecha_inicio AND :fecha_fin
                            
                            ORDER BY fecha;
                            """)
        params = {'id': busqueda_tanque.id_tanque, 
                'fecha_inicio': busqueda_tanque.fecha_start,
                'fecha_fin': busqueda_tanque.fecha_end,
                } 
        try:

            diario_tanques = []
            total_tanques = []
            with db.engine.connect() as connection:
                with connection.execute(query_main,params) as cursor:
                    consultas = cursor.fetchall() 

                    if consultas != None:
                        for operaciones_carga_descarga in consultas:
                                id_orden_fk   = operaciones_carga_descarga[0]
                                query_main_2 = text("""SELECT batch_ucl_carga_descarga.batch, batch_ucl_carga_descarga.tipo
                                FROM batch_ucl_carga_descarga WHERE id_orden_fk = :id_orden_fk """)
                                params_2 = {
                                    'id_orden_fk':id_orden_fk
                                }
                                with connection.execute(query_main_2, params_2) as cursor_2:
                                        consultas_2 = cursor_2.fetchall()
                                        
                                        if consultas_2:
                                            for consulta in consultas_2:      
                                        
                                                batch_data = consulta[0]
                                                # Procesa la cadena batch_data para extraer información
                                                data = {}
                                                lines = batch_data.split('\n')
                                                for line in lines:
                                                    if 'Número de BOL' in line:
                                                        data['numero_bol'] = line.split(':')[1].strip()
                                                    elif 'Fecha de inicio' in line:
                                                        data['fecha_inicio'] = line.split(':', 1)[1].strip()
                                                    elif 'Fecha de término' in line:
                                                        data['fecha_termino'] = line.split(':', 1)[1].strip()
                                                    elif 'Volumen natural' in line:
                                                        try:
                                                            data['volumen_natural'] = float(line.split(':')[1].strip())
                                                        except ValueError:
                                                            data['volumen_natural'] = None
                                                            print(f"Error al convertir volumen natural: {line}")
                                                    elif 'Volumen neto' in line:
                                                        try:
                                                            data['volumen_neto'] = float(line.split(':')[1].strip())
                                                        except ValueError:
                                                            data['volumen_neto'] = None
                                                            print(f"Error al convertir volumen neto: {line}")
                                                    elif 'Temperatura' in line:
                                                        try:
                                                            data['temperatura'] = float(line.split(':')[1].strip().replace(',', '.'))
                                                        except ValueError:
                                                            data['temperatura'] = None
                                                            print(f"Error al convertir temperatura: {line}")
                                                    elif 'Densidad' in line:
                                                        try:
                                                            data['densidad'] = float(line.split(':')[1].strip().replace(',', '.'))
                                                        except ValueError:
                                                            data['densidad'] = None
                                                            print(f"Error al convertir densidad: {line}")   

                                            # Crear la instancia de Tabla_batch_diario_tanques
                                            diario_tanques_2 = Tabla_batch_diario_tanques(
                                                None,
                                                None,
                                                None,
                                                data.get('numero_bol'),
                                                data.get('fecha_inicio'),
                                                data.get('fecha_termino'),
                                                data.get('volumen_natural'),
                                                data.get('volumen_neto'),
                                                data.get('temperatura'),
                                                data.get('densidad'),
                                                consulta[1]
                                            )
                                            diario_tanques.append(diario_tanques_2)
                                        
                                        total_volumen_natural_carga = 0.0
                                        total_volumen_neto_carga = 0.0

                                        total_volumen_natural_descarga = 0.0
                                        total_volumen_neto_descarga = 0.0
                                        # Inicializar variables
                                        temperaturas_promedio_carga = 0.0
                                        temperaturas_promedio_descarga = 0.0
                                        conteo_carga = 0
                                        conteo_descarga = 0

                                        # Procesar datos
                                        for diario in diario_tanques:       
                                            if diario.tipo == "carga":
                                                total_volumen_natural_carga += diario.volumen_natural
                                                total_volumen_neto_carga += diario.volumen_neto
                                                temperaturas_promedio_carga += diario.temperatura
                                                conteo_carga += 1    
                                            elif diario.tipo == "descarga":
                                                total_volumen_natural_descarga += diario.volumen_natural
                                                total_volumen_neto_descarga += diario.volumen_neto
                                                temperaturas_promedio_descarga += diario.temperatura
                                                conteo_descarga += 1

                                        # Calcular promedios
                                        if conteo_carga > 0:
                                            temperaturas_promedio_carga_1 = temperaturas_promedio_carga / conteo_carga
                                        else:
                                            temperaturas_promedio_carga_1 = None  # O algún valor predeterminado adecuado

                                        if conteo_descarga > 0:
                                            temperaturas_promedio_descarga_1 = temperaturas_promedio_descarga / conteo_descarga
                                        else:
                                            temperaturas_promedio_descarga_1 = None  # O algún valor predeterminado adecuado

                                        total = Tabla_batch_diario_total_tanques(
                                                total_volumen_natural_carga,
                                                total_volumen_neto_carga,
                                                total_volumen_natural_descarga,
                                                total_volumen_neto_descarga,
                                                temperaturas_promedio_carga_1,
                                                temperaturas_promedio_descarga_1
                                            )
                                        total_tanques.append(total)
                                        query_main_3 = text("""SELECT telemedicion_tanques.id_instrumentacion_fk 
                                                                FROM tanques JOIN telemedicion_tanques ON tanques.id = telemedicion_tanques.id_tanque_fk 
                                                                WHERE  telemedicion_tanques.id_tanque_fk  = :id;""")
                                        params_3 = {'id':busqueda_tanque.id_tanque}
                                        with connection.execute(query_main_3, params_3) as cursor_3:
                                                    consultas_3 = cursor_3.fetchall()  # Usa fetchall para manejar múltiples filas
                                                    if consultas_3:
                                                        for consulta_3 in consultas_3:
                                                            id_instrumento_fk = consulta_3[0]
                                                            for diario in diario_tanques:       
                                                                fecha_inicio = diario.fecha_inicio                        
                                                                fecha_fin = diario.fecha_termino                        

                                                                query_main_3 = text("SELECT json FROM rt_tanques WHERE JSON_UNQUOTE(JSON_EXTRACT(json, '$.timestamp')) < '2024-08-05 18:00:51' AND id_instrumento_fk= :id LIMIT 1;""")
                                                                params_3 = {'id':busqueda_tanque.id_tanque,
                                                                            'fecha_buscar':fecha_inicio }

        except Exception as ex:
            raise RuntimeError(f"Error al ejecutar la consulta: {ex}")





    @classmethod
    def comercializadora_diario_tanques(self, db, busqueda_tanque):
        query_main = text("""SELECT batch_ucl_carga_descarga.batch, batch_ucl_carga_descarga.tipo
                    FROM tanques 
                    JOIN batch_ucl_carga_descarga 
                    ON tanques.id = batch_ucl_carga_descarga.id_tanque_fk 
                    WHERE tanques.id = :id
                    AND batch_ucl_carga_descarga.fecha_inicio BETWEEN :fecha_inicio AND :fecha_fin
                    AND batch_ucl_carga_descarga.fecha_fin BETWEEN :fecha_inicio AND :fecha_fin;""")
        params = {'id': busqueda_tanque.id_tanque, 
                'fecha_inicio': busqueda_tanque.fecha_start,
                'fecha_fin': busqueda_tanque.fecha_end,
                } 
 


            # Inicializar variables
        diario_tanques = []
        total_tanques = []
        lectura_anterior_batch = []
        lectura_posterior_batch = []
        lectura_tanque_inicio__fin_dia_1  =[]
        try:
            with db.engine.connect() as connection:
                with connection.execute(query_main,params) as cursor:
                    consultas = cursor.fetchall()  # Usa fetchall para manejar múltiples filas
                    
                    diario_tanques = []
                    total_tanques = []
                    total_volumen_natural = 0.0
                    total_volumen_neto = 0.0
                    if consultas:
                        for consulta in consultas:
                            batch_data = consulta[0]

                            # Procesa la cadena batch_data para extraer información
                            data = {}
                            lines = batch_data.split('\n')
                            for line in lines:
                                if 'Número de BOL' in line:
                                    data['numero_bol'] = line.split(':')[1].strip()
                                elif 'Fecha de inicio' in line:
                                    data['fecha_inicio'] = line.split(':', 1)[1].strip()
                                elif 'Fecha de término' in line:
                                    data['fecha_termino'] = line.split(':', 1)[1].strip()
                                elif 'Volumen natural' in line:
                                    try:
                                        data['volumen_natural'] = float(line.split(':')[1].strip())
                                    except ValueError:
                                        data['volumen_natural'] = None
                                        print(f"Error al convertir volumen natural: {line}")
                                elif 'Volumen neto' in line:
                                    try:
                                        data['volumen_neto'] = float(line.split(':')[1].strip())
                                    except ValueError:
                                        data['volumen_neto'] = None
                                        print(f"Error al convertir volumen neto: {line}")
                                elif 'Temperatura' in line:
                                    try:
                                        data['temperatura'] = float(line.split(':')[1].strip().replace(',', '.'))
                                    except ValueError:
                                        data['temperatura'] = None
                                        print(f"Error al convertir temperatura: {line}")
                                elif 'Densidad' in line:
                                    try:
                                        data['densidad'] = float(line.split(':')[1].strip().replace(',', '.'))
                                    except ValueError:
                                        data['densidad'] = None
                                        print(f"Error al convertir densidad: {line}")
                            
                            # Convertir fechas a tipo datetime si es necesario
                            data['fecha_inicio'] = data.get('fecha_inicio')
                            data['fecha_termino'] = data.get('fecha_termino')
        
                            # Crear la instancia de Tabla_batch_diario_tanques
                            diario_tanques_2 = Tabla_batch_diario_tanques(
                                None,
                                None,
                                None,
                                data.get('numero_bol'),
                                data.get('fecha_inicio'),
                                data.get('fecha_termino'),
                                data.get('volumen_natural'),
                                data.get('volumen_neto'),
                                data.get('temperatura'),
                                data.get('densidad'),
                                consulta[1]
                            )
                            diario_tanques.append(diario_tanques_2)
                        total_volumen_natural_carga = 0.0
                        total_volumen_neto_carga = 0.0

                        total_volumen_natural_descarga = 0.0
                        total_volumen_neto_descarga = 0.0
                        # Inicializar variables
                        temperaturas_promedio_carga = 0.0
                        temperaturas_promedio_descarga = 0.0
                        conteo_carga = 0
                        conteo_descarga = 0

                        # Procesar datos
                        for diario in diario_tanques:       
                            if diario.tipo == "carga":
                                total_volumen_natural_carga += diario.volumen_natural
                                total_volumen_neto_carga += diario.volumen_neto
                                temperaturas_promedio_carga += diario.temperatura
                                conteo_carga += 1    
                            elif diario.tipo == "descarga":
                                total_volumen_natural_descarga += diario.volumen_natural
                                total_volumen_neto_descarga += diario.volumen_neto
                                temperaturas_promedio_descarga += diario.temperatura
                                conteo_descarga += 1

                        # Calcular promedios
                        if conteo_carga > 0:
                            temperaturas_promedio_carga_1 = temperaturas_promedio_carga / conteo_carga
                        else:
                            temperaturas_promedio_carga_1 = None  # O algún valor predeterminado adecuado

                        if conteo_descarga > 0:
                            temperaturas_promedio_descarga_1 = temperaturas_promedio_descarga / conteo_descarga
                        else:
                            temperaturas_promedio_descarga_1 = None  # O algún valor predeterminado adecuado
                        total = Tabla_batch_diario_total_tanques(
                                total_volumen_natural_carga,
                                total_volumen_neto_carga,
                                total_volumen_natural_descarga,
                                total_volumen_neto_descarga,
                                temperaturas_promedio_carga_1,
                                temperaturas_promedio_descarga_1
                            )
                        total_tanques.append(total)
                

                    query_main_2 = text("""SELECT tanques.id, telemedicion_tanques.id_instrumentacion_fk 
                                FROM tanques JOIN telemedicion_tanques ON tanques.id = telemedicion_tanques.id_tanque_fk 
                                WHERE  telemedicion_tanques.id_tanque_fk  = :id;""")
                    params_2 = {'id':busqueda_tanque.id_tanque}
  # Ejecutar segunda consulta
                    with connection.execute(query_main_2, params_2) as cursor_2:
                        consultas_2 = cursor_2.fetchall()  # Usa fetchall para manejar múltiples filas
                        if consultas_2:
                            for consulta_2 in consultas_2:
                                id_instrumento_fk = consulta_2[1]
                                for diario in diario_tanques:       
                                    fecha_inicio = diario.fecha_inicio

                                    query_main_3 = text("""SELECT rt_tanques.fecha, rt_tanques.json 
                                    FROM telemedicion_tanques JOIN rt_tanques ON telemedicion_tanques.id_instrumentacion_fk = rt_tanques.id_instrumento_fk 
                                    WHERE telemedicion_tanques.id_instrumentacion_fk = :id_instrumentacion_fk
                                    AND rt_tanques.fecha < :fecha_inicio AND rt_tanques.fecha >= TIMESTAMPADD(MINUTE, -3, :fecha_inicio) 
                                    ORDER BY ABS(TIMESTAMPDIFF(SECOND, rt_tanques.fecha, :fecha_inicio)) ASC LIMIT 1;
                                    """)
                                    params_3 = {
                                        'id_instrumentacion_fk': id_instrumento_fk,
                                        'fecha_inicio': fecha_inicio
                                    }

                                    with connection.execute(query_main_3, params_3) as cursor_3:
                                        consultas_3 = cursor_3.fetchall() 
                                        if consultas_3:
                                            for consulta_3 in consultas_3:
                                                batch_data_anterior = consulta_3[1]

                                                data = json.loads(batch_data_anterior)
                                                # Extraer información del JSON
                                                timestamp_1 = data.get('timestamp')
                                                ucl_telemedicion_data_1 = data.get('ucl_telemedicion', {}).get('data', {})
                                                rtd_data_1 = data.get('rtd', {}).get('data', {})
                                                
                                                lectura_anterior = lectura_tanque_antes_batch(
                                                    timestamp_1,
                                                    ucl_telemedicion_data_1.get('volumen_natural'),
                                                    ucl_telemedicion_data_1.get('volumen_neto'),
                                                    rtd_data_1.get('temperatura')
                                                )       
                                                lectura_anterior_batch.append(lectura_anterior)
                                    query_main_4 = text("""SELECT rt_tanques.fecha, rt_tanques.json 
                                                    FROM telemedicion_tanques 
                                                    JOIN rt_tanques 
                                                    ON telemedicion_tanques.id_instrumentacion_fk = rt_tanques.id_instrumento_fk 
                                                    WHERE telemedicion_tanques.id_instrumentacion_fk = :id_instrumentacion_fk 
                                                    AND rt_tanques.fecha > :fecha_inicio
                                                    AND rt_tanques.fecha <= TIMESTAMPADD(MINUTE, 3, :fecha_inicio)
                                                    ORDER BY ABS(TIMESTAMPDIFF(SECOND, rt_tanques.fecha, TIMESTAMPADD(MINUTE, 3, :fecha_inicio))) ASC 
                                                    LIMIT 1;
                                    """ )
                                    params_4 = {
                                        'id_instrumentacion_fk': id_instrumento_fk,
                                        'fecha_inicio': fecha_inicio
                                    }

                                    with connection.execute(query_main_4, params_4) as cursor_4:
                                        consultas_4 = cursor_4.fetchall() 
                                        if consultas_4:
                                            for consulta_4 in consultas_4:
                                                batch_data_anterior_2 = consulta_4[1]

                                                data_2 = json.loads(batch_data_anterior_2)
                                                # Extraer información del JSON
                                                timestamp_2 = data_2.get('timestamp')
                                                ucl_telemedicion_data_2 = data_2.get('ucl_telemedicion', {}).get('data', {})
                                                rtd_data_2 = data_2.get('rtd', {}).get('data', {})
                                                
                                                lectura_posterior_batch1 = lectura_tanque_posterior_batch(
                                                    timestamp_2,
                                                    ucl_telemedicion_data_2.get('volumen_natural'),
                                                    ucl_telemedicion_data_2.get('volumen_neto'),
                                                    rtd_data_2.get('temperatura')
                                                )       
                                                lectura_posterior_batch.append(lectura_posterior_batch1)
                                    #query_main_5 = text("""SELECT rt_tanques.fecha, rt_tanques.json
                                    #                     FROM telemedicion_tanques JOIN rt_tanques ON telemedicion_tanques.id_instrumentacion_fk = rt_tanques.id_instrumento_fk 
                                    #                    WHERE telemedicion_tanques.id_instrumentacion_fk = :id_instrumentacion_fk AND rt_tanques.fecha BETWEEN :fecha_inicio AND :fecha_fin;
                                    #                        """)
                                    query_main_5 = text("""
                                                    WITH MinDate AS (
                                                        SELECT MIN(rt_tanques.fecha) AS min_fecha
                                                        FROM telemedicion_tanques
                                                        JOIN rt_tanques ON telemedicion_tanques.id_instrumentacion_fk = rt_tanques.id_instrumento_fk
                                                        WHERE telemedicion_tanques.id_instrumentacion_fk = :id_instrumentacion_fk
                                                        AND rt_tanques.fecha BETWEEN :fecha_inicio AND :fecha_fin
                                                    )
                                                    SELECT rt_tanques.fecha, rt_tanques.json
                                                    FROM rt_tanques
                                                    JOIN MinDate ON rt_tanques.fecha = MinDate.min_fecha
                                                    WHERE rt_tanques.id_instrumento_fk = :id_instrumentacion_fk;
                                             """)
                                    params_5 = {
                                        'id_instrumentacion_fk': id_instrumento_fk,
                                        'fecha_inicio': busqueda_tanque.fecha_start,
                                        'fecha_fin': busqueda_tanque.fecha_end,
                                    }
                                    with connection.execute(query_main_5, params_5) as cursor_5:
                                        consultas_5 = cursor_5.fetchall() 
                                        if consultas_5:
                                            for consulta_5 in consultas_5:
                                                batch_data_anterior_3 = consulta_5[1]

                                                data_3 = json.loads(batch_data_anterior_3)
                                                # Extraer información del JSON
                                                timestamp_3 = data_3.get('timestamp')
                                                ucl_telemedicion_data_3 = data_3.get('ucl_telemedicion', {}).get('data', {})
                                                rtd_data_3 = data_3.get('rtd', {}).get('data', {})
                                                
                                                lectura_tanque_inicio__fin_dia_2 = lectura_tanque_inicio__fin_dia(
                                                    timestamp_3,
                                                    ucl_telemedicion_data_3.get('volumen_natural'),
                                                    ucl_telemedicion_data_3.get('volumen_neto'),
                                                    rtd_data_3.get('temperatura')
                                                )       
                                                lectura_tanque_inicio__fin_dia_1.append(lectura_tanque_inicio__fin_dia_2)

                                    query_main_6 = text("""
                                                    WITH MaxDate  AS (
                                                        SELECT MAX(rt_tanques.fecha) AS max_fecha
                                                        FROM telemedicion_tanques
                                                        JOIN rt_tanques ON telemedicion_tanques.id_instrumentacion_fk = rt_tanques.id_instrumento_fk
                                                        WHERE telemedicion_tanques.id_instrumentacion_fk = :id_instrumentacion_fk
                                                        AND rt_tanques.fecha BETWEEN :fecha_inicio AND :fecha_fin
                                                    )
                                                    SELECT rt_tanques.fecha, rt_tanques.json
                                                    FROM rt_tanques
                                                    JOIN MaxDate ON rt_tanques.fecha = MaxDate.max_fecha
                                                    WHERE rt_tanques.id_instrumento_fk = :id_instrumentacion_fk;
                                             """)
                                    params_6 = {
                                        'id_instrumentacion_fk': id_instrumento_fk,
                                        'fecha_inicio': busqueda_tanque.fecha_start,
                                        'fecha_fin': busqueda_tanque.fecha_end,
                                    }                                    
                                    with connection.execute(query_main_6, params_6) as cursor_6:
                                        consultas_6 = cursor_6.fetchall() 
                                        if consultas_6:
                                            for consulta_6 in consultas_6:
                                                batch_data_anterior_4 = consulta_5[1]

                                                data_4 = json.loads(batch_data_anterior_4)
                                                # Extraer información del JSON
                                                timestamp_4 = data_4.get('timestamp')
                                                ucl_telemedicion_data_4 = data_4.get('ucl_telemedicion', {}).get('data', {})
                                                rtd_data_4 = data_4.get('rtd', {}).get('data', {})
                                                
                                                lectura_tanque_inicio__fin_dia_3 = lectura_tanque_inicio__fin_dia(
                                                    timestamp_4,
                                                    ucl_telemedicion_data_4.get('volumen_natural'),
                                                    ucl_telemedicion_data_4.get('volumen_neto'),
                                                    rtd_data_4.get('temperatura')
                                                )       
                                                lectura_tanque_inicio__fin_dia_1.append(lectura_tanque_inicio__fin_dia_3)

                    return diario_tanques,total_tanques, lectura_anterior_batch, lectura_posterior_batch,lectura_tanque_inicio__fin_dia_1
        except Exception as ex:
            raise RuntimeError(f"Error al ejecutar la consulta: {ex}")

    @classmethod
    def comercializadora_mensual_tanques(cls, db, mensual_tanques):
        query_main = text( """SELECT batch_ucl_carga_descarga.batch, batch_ucl_carga_descarga.tipo
                    FROM tanques 
                    JOIN batch_ucl_carga_descarga 
                    ON tanques.id = batch_ucl_carga_descarga.id_tanque_fk 
                    WHERE tanques.id = :id
                    AND batch_ucl_carga_descarga.fecha_inicio BETWEEN :fecha_inicio AND :fecha_fin
                    AND batch_ucl_carga_descarga.fecha_fin BETWEEN :fecha_inicio AND :fecha_fin;""")
        params = {'id': mensual_tanques.id_tanque, 
                'fecha_inicio': mensual_tanques.fecha_start,
                'fecha_fin': mensual_tanques.fecha_end} 
        try:
            with db.engine.connect() as connection:
                with connection.execute(query_main,params) as cursor:
                    consultas = cursor.fetchall()

                    def convert_to_datetime(date_str):
                        if date_str:
                            try:
                                return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                            except ValueError:
                                print(f"Error al convertir la fecha: {date_str}")
                                return None
                        return None

                    # Inicializa variables
                    recepcion_total_volumen_registros_descargas = 0
                    recepcion_total_volumen_natural_descargas = 0
                    recepcion_total_volumen_neto_descargas = 0
                    temperaturas_promedio_descarga = 0
                    conteo_temperaturas_descarga = 0
                    
                    recepcion_total_volumen_registros_cargas = 0
                    recepcion_volumen_natural_carga = 0
                    recepcion_volumen_neto_carga = 0
                    temperaturas_promedio_carga = 0
                    conteo_temperaturas_carga = 0

                    data = {
                        'fecha_inicio': None,
                        'fecha_termino': None,
                        'volumen_natural': 0,
                        'volumen_neto': 0,
                        'temperatura': 0
                    }

                    for consulta in consultas:
                        batch_data = consulta[0]
                        tipo = consulta[1]

                        # Procesa la cadena batch_data para extraer información
                        lines = batch_data.split('\n')
                        for line in lines:
                            if 'Número de BOL' in line:
                                data['numero_bol'] = line.split(':')[1].strip()
                            elif 'Fecha de inicio' in line:
                                data['fecha_inicio'] = line.split(':')[1].strip()
                            elif 'Fecha de término' in line:
                                data['fecha_termino'] = line.split(':')[1].strip()
                            elif 'Volumen natural' in line:
                                try:
                                    data['volumen_natural'] = float(line.split(':')[1].strip())
                                except ValueError:
                                    data['volumen_natural'] = 0
                                    print(f"Error al convertir volumen natural: {line}")
                            elif 'Volumen neto' in line:
                                try:
                                    data['volumen_neto'] = float(line.split(':')[1].strip())
                                except ValueError:
                                    data['volumen_neto'] = 0
                                    print(f"Error al convertir volumen neto: {line}")
                            elif 'Temperatura' in line:
                                try:
                                    data['temperatura'] = float(line.split(':')[1].strip().replace(',', '.'))
                                except ValueError:
                                    data['temperatura'] = 0
                                    print(f"Error al convertir temperatura: {line}")
                            elif 'Densidad' in line:
                                try:
                                    data['densidad'] = float(line.split(':')[1].strip().replace(',', '.'))
                                except ValueError:
                                    data['densidad'] = 0
                                    print(f"Error al convertir densidad: {line}")

                        data['fecha_inicio'] = convert_to_datetime(data.get('fecha_inicio'))
                        data['fecha_termino'] = convert_to_datetime(data.get('fecha_termino'))

                        if tipo == "descarga":
                            if data.get('numero_bol') is not None:
                                recepcion_total_volumen_registros_descargas += 1

                            if data.get('volumen_natural') is not None:
                                recepcion_total_volumen_natural_descargas += data['volumen_natural']
                            if data.get('volumen_neto') is not None:
                                recepcion_total_volumen_neto_descargas += data['volumen_neto']
                            if data.get('temperatura') is not None:
                                temperaturas_promedio_descarga += data['temperatura']
                                conteo_temperaturas_descarga += 1
                        elif tipo == "carga":
                            if data.get('numero_bol') is not None:
                                recepcion_total_volumen_registros_cargas += 1

                            if data.get('volumen_natural') is not None:
                                recepcion_volumen_natural_carga += data['volumen_natural']
                            if data.get('volumen_neto') is not None:
                                recepcion_volumen_neto_carga += data['volumen_neto']
                            if data.get('temperatura') is not None:
                                temperaturas_promedio_carga += data['temperatura']
                                conteo_temperaturas_carga += 1

                    # Evita división por cero
                    temperaturas_promedio_carga = (temperaturas_promedio_carga / conteo_temperaturas_carga) if conteo_temperaturas_carga > 0 else 0
                    temperaturas_promedio_descarga = (temperaturas_promedio_descarga / conteo_temperaturas_descarga) if conteo_temperaturas_descarga > 0 else 0

                    # Asigna valores finales
                    volumen_final_natural = data.get('volumen_natural', 0)
                    volumen_final_neto = data.get('volumen_neto', 0)

                    total = Tabla_batch_mensual_tanques(None, None, None, data.get('fecha_inicio'), data.get('fecha_termino'), None,
                                                        volumen_final_natural, volumen_final_neto, data.get('temperatura', 0),
                                                        recepcion_total_volumen_registros_descargas, recepcion_total_volumen_natural_descargas, recepcion_total_volumen_neto_descargas, temperaturas_promedio_descarga,
                                                        recepcion_total_volumen_registros_cargas, recepcion_volumen_natural_carga, recepcion_volumen_neto_carga, temperaturas_promedio_carga)
                    return [total]
        except Exception as ex:
            raise RuntimeError(f"Error al ejecutar la consulta: {ex}")
#        finally:
#           if cursor:
#                cursor.close()

    @classmethod
    def create_distribuidor_venta(cls,db,distribuidor_venta):
        query_main = text("""INSERT INTO ventas_cv
                          (Id_Proveedor,Id_estacion_cv,Id_cliente_cv,Producto,Cantidad,Autotanque, Fecha, Costo,Estatus,Informacion_adicional)
                          VALUES (:Id_proveedor_cv,:Id_estacion_cv,:Id_cliente,:tipo_producto,:cantidad,:autotanque,:fecha,:costo,:estatus,:informacion); """)
        params = {
                'Id_proveedor_cv':distribuidor_venta.id_proveedor,
                'Id_estacion_cv':distribuidor_venta.id_estacion,
                'Id_cliente':distribuidor_venta.id_cliente,
                'tipo_producto':distribuidor_venta.tipo_producto,
                'cantidad':distribuidor_venta.cantidad,
                'autotanque':distribuidor_venta.autotanque,
                'fecha':distribuidor_venta.fecha,
                'costo':distribuidor_venta.costo,
                'estatus':distribuidor_venta.estatus,
                'informacion':distribuidor_venta.informacion

        } 
        try:
            with cv.SessionLocal() as connection:
                result = connection.execute(query_main, params)
                print("Filas insertadas:", result.rowcount)
                connection.commit()  # Confirmar la transacción

                return True  # Retornar True si la inserción fue exitosa
        
        except Exception as ex:
            print(f"Error al ejecutar la consulta: {ex}")
            return False  # Retornar False si hubo algún error durante la inserción
    

    @classmethod
    def consultar_distribuidor_ventas(cls, db, consultar_ventas, page_num, elementos_por_pagina):
        query_main = text("""
            SELECT * FROM ventas_cv 
            WHERE Estatus = 'Cerrado' AND Fecha BETWEEN :fecha_inicio AND :fecha_fin
            LIMIT :elementos_por_pagina OFFSET :elementos_por_pagina_2
        """)

        params = {
            'fecha_inicio': consultar_ventas.fecha_inicio_busqueda,
            'fecha_fin': consultar_ventas.fecha_fin_busqueda,
            'elementos_por_pagina': elementos_por_pagina,
            'elementos_por_pagina_2': (page_num - 1) * elementos_por_pagina
        }

        nombre_proveedor = None
        nombre_estacion = None
        nombre_cliente = None
        rfc_proveedor = None
        rfc_cliente = None
        cantidad_clientes = []

        try:
            with cv.SessionLocal() as connection:
                # Ejecuta la consulta principal
                result = connection.execute(query_main, params)
                rows = result.fetchall()

                for row in rows:
                    id_proveedor = row[1]
                    id_estacion = row[2]
                    id_cliente = row[3]
                    
                     # Consulta para nombre del proveedor
                query_main_1a = text("""
                    SELECT Nombre_comercial         
                    FROM proveedor_cv 
                    WHERE Id_Proveedor = :id_proveedor
                """)
                params_1a = {'id_proveedor': id_proveedor}
                result_1a = connection.execute(query_main_1a, params_1a)
                nombre_proveedor = result_1a.scalar()

                # Consulta para RFC del proveedor
                query_main_1b = text("""
                    SELECT RFC         
                    FROM proveedor_cv 
                    WHERE Id_Proveedor = :id_proveedor
                """)
                params_1b = {'id_proveedor': id_proveedor}
                result_1b = connection.execute(query_main_1b, params_1b)
                rfc_proveedor = result_1b.scalar()

                # Consulta para estación
                query_main_2 = text("""
                    SELECT Nombre_comercial         
                    FROM estaciones_cv 
                    WHERE Id_estacion = :id_estacion
                """)
                params_2 = {'id_estacion': id_estacion}
                result_2 = connection.execute(query_main_2, params_2)
                nombre_estacion = result_2.scalar()

                # Consulta para nombre del cliente
                query_main_3a = text("""
                    SELECT Nombre_comercial         
                    FROM cliente_cv 
                    WHERE Id_cliente = :id_cliente
                """)
                params_3a = {'id_cliente': id_cliente}
                result_3a = connection.execute(query_main_3a, params_3a)
                nombre_cliente = result_3a.scalar()

                # Consulta para RFC del cliente
                query_main_3b = text("""
                    SELECT RFC         
                    FROM cliente_cv 
                    WHERE Id_cliente = :id_cliente
                """)
                params_3b = {'id_cliente': id_cliente}
                result_3b = connection.execute(query_main_3b, params_3b)
                rfc_cliente = result_3b.scalar()

                cantidad_clientes_2 = Tabla_distribuidor_venta_consultar(
                    None, None, 
                    row[0], 
                    nombre_proveedor,
                    rfc_proveedor,  # Nuevo campo RFC proveedor
                    nombre_estacion, 
                    nombre_cliente,
                    rfc_cliente,    # Nuevo campo RFC cliente
                    row[4], row[5], row[6], row[7], row[8], row[9], row[10]
                )
                cantidad_clientes.append(cantidad_clientes_2)
                # Total de registros
                total = len(rows)  # Asume que el total es el número de filas recuperadas

                return cantidad_clientes, total

        except SQLAlchemyError as e:
            raise Exception("Error al consultar distribuidor de ventas: " + str(e))

        except Exception as ex:
            raise Exception("Error inesperado: " + str(ex))

    @classmethod
    def venta_cancelada(cls, db, cancelar_1):
        query_main = text("""
            UPDATE ventas_cv SET Estatus = 'Cancelado'
            WHERE Id_ventas = :Id_ventas;
        """)
        
        params = {
            'Id_ventas':cancelar_1.id_venta
        }
        try:
            with cv.SessionLocal() as connection:
                result = connection.execute(query_main, params)
                print("Filas canceladas:", result.rowcount)
                connection.commit()  # Confirmar la transacción
                return True  # Retornar True si la inserción fue exitosa
        except Exception as ex:
            print(f"Error al ejecutar la consulta: {ex}")
            return False  # Retornar False si hubo algún error durante la inserción



    @classmethod
    def create_proveedor(cls, db, crear_proveedor):
        query_main = text("""
            INSERT INTO proveedor_cv
            (Codigo_interno,Nombre_comercial,Razon_social,RFC,Dirección,Telefono,Email,Información_adicional)
            VALUES (:Codigo_interno,:Nombre_comercial,:Razon_social,:RFC,:Direccion,:Telefono,:Email,:Informacion_adicional);
        """)
        
        params = {
            'Codigo_interno': crear_proveedor.codigo,
            'Nombre_comercial': crear_proveedor.nombre_comercial,
            'Razon_social': crear_proveedor.razon,  # Ejemplo de valor para Telefono, asegúrate de usar el valor correcto
            'RFC': crear_proveedor.rfc,
            'Direccion': crear_proveedor.direccion,
            'Telefono':crear_proveedor.telefono,  # Ejemplo de valor para Cambio_contraseña, asegúrate de usar el valor correcto
            'Email': crear_proveedor.email,
            'Informacion_adicional':crear_proveedor.informacion
        }

        try:
            with cv.SessionLocal() as connection:
                result = connection.execute(query_main, params)
                print("Filas insertadas:", result.rowcount)
                connection.commit()  # Confirmar la transacción

                return True  # Retornar True si la inserción fue exitosa
        
        except Exception as ex:
            print(f"Error al ejecutar la consulta: {ex}")
            return False  # Retornar False si hubo algún error durante la inserción

    @classmethod
    def consulta_proveedores(self,db,page_num,elementos_por_pagina):
        query_main = text("SELECT * FROM proveedor_cv")
        try:
            with cv.SessionLocal() as connection:
                with connection.execute(query_main) as cursor:
                    rows = cursor.fetchall()
                    cantidad_clientes = []
                    if rows != None:
                        for row in rows:
                                cantidad_clientes_2 = Tabla_Proveedores_consulta(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8])
                                cantidad_clientes.append(cantidad_clientes_2)
                        total = len(rows)
                        return cantidad_clientes,total 
                    else:
                        return rows

        except Exception as ex:
            raise Exception(ex)    
        finally:
            cursor.close()#Cierro la conexión   

    @classmethod
    def eliminar_proveedor(self, db, delete):
        # Consulta para eliminar un cliente basado en el ID
        query_main = text("DELETE FROM proveedor_cv WHERE Id_Proveedor  = :eliminar_proveedor;")
        params = {'eliminar_proveedor': delete.id_proveedor}

        # Consulta para actualizar registros en la tabla ventas_cv
        # Reemplaza 'Id_cliente_cv' con el nombre correcto de la columna si es necesario
        query_main_update = text("UPDATE ventas_cv SET Id_Proveedor = NULL WHERE Id_Proveedor = :eliminar_Id_proveedor_cv;")
        params_update = {'eliminar_Id_proveedor_cv': delete.id_proveedor}
        try:
            with cv.SessionLocal() as connection_update:
                result_update = connection_update.execute(query_main_update, params_update)
                print("Filas actualizadas en ventas_cv:", result_update.rowcount)
                connection_update.commit()  # Confirmar la transacción
            # Ejecutar la consulta de eliminación en la tabla cliente_cv
            with cv.SessionLocal() as connection:
                result = connection.execute(query_main, params)
                print("Filas eliminadas en estaciones_cv:", result.rowcount)
                connection.commit()  # Confirmar la transacción
            # Ejecutar la consulta de actualización en la tabla ventas_cv

            return True  # Retornar True si la operación fue exitosa

        except Exception as ex:
            print(f"Error al ejecutar la consulta: {ex}")
            return False  # Retornar False si hubo algún error durante la operación

    @classmethod
    def consulta_proveedores_especifico(self,db,especifico):
        query_main = text("SELECT * FROM proveedor_cv WHERE Id_Proveedor  = :Id_Proveedor")
         
        params = {
            'Id_Proveedor': especifico.id_update
        }
        try:
            with cv.SessionLocal() as connection:
                with connection.execute(query_main,params) as cursor:
                    rows = cursor.fetchall()
                    cantidad_clientes = []
                    if rows != None:
                        for row in rows:
                                cantidad_clientes_2 = Tabla_Proveedor_actualizar(None,row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8])
                                cantidad_clientes.append(cantidad_clientes_2)
                        return cantidad_clientes 
                    else:
                        return rows

        except Exception as ex:
            raise Exception(ex)    
        finally:
            cursor.close()#Cierro la conexión   




    @classmethod
    def update_proveedor(cls, db, actualizar_estacion):
        query_main = text("""
            UPDATE proveedor_cv SET Codigo_interno = :Codigo_interno,
                Nombre_comercial = :Nombre_comercial,
                Razon_Social = :Razon_Social,        
                RFC = :RFC,
                Dirección = :Direccion, 
                Telefono = :Telefono,
                Email = :Email,
                 Información_adicional = :Informacion_adicional
            WHERE Id_Proveedor   = :Id_proveedor ;
        """)
        
        params = {
            'Id_proveedor':actualizar_estacion.id_update,
            'Codigo_interno': actualizar_estacion.codigo,
            'Nombre_comercial': actualizar_estacion.nombre_comercial,
            'Razon_Social': actualizar_estacion.razon_social,
            'RFC': actualizar_estacion.rfc,
            'Direccion': actualizar_estacion.direccion,
            'Telefono':actualizar_estacion.telefono,  # Ejemplo de valor para Cambio_contraseña, asegúrate de usar el valor correcto
            'Email': actualizar_estacion.email,
            'Informacion_adicional':actualizar_estacion.informacion
        }

        try:
            with cv.SessionLocal() as connection:
                result = connection.execute(query_main, params)
                print("Filas actualizadas:", result.rowcount)
                connection.commit()  # Confirmar la transacción

                return True  # Retornar True si la inserción fue exitosa
        
        except Exception as ex:
            print(f"Error al ejecutar la consulta: {ex}")
            return False  # Retornar False si hubo algún error durante la inserción











    @classmethod
    def create_client(cls, db, crear_cliente):
        query_main = text("""
            INSERT INTO cliente_cv
            (Codigo_interno,Nombre_comercial,Razon_social,RFC,Regimen_fiscal,Direccion,Codigo_postal,Telefono,Email,Informacion_adicional)
            VALUES (:Codigo_interno,:Nombre_comercial,:Razon_social,:RFC,:Regimen_fiscal,:Direccion,:Codigo_postal,:Telefono,:Email,:Informacion_adicional);
        """)
        
        params = {
            'Codigo_interno': crear_cliente.codigo,
            'Nombre_comercial': crear_cliente.nombre_comercial,
            'Razon_social': crear_cliente.razon,  # Ejemplo de valor para Telefono, asegúrate de usar el valor correcto
            'RFC': crear_cliente.rfc,
            'Regimen_fiscal': crear_cliente.regimen,
            'Direccion': crear_cliente.direccion,
            'Codigo_postal': crear_cliente.cod_pos, 
            'Telefono':crear_cliente.telefono,  # Ejemplo de valor para Cambio_contraseña, asegúrate de usar el valor correcto
            'Email': crear_cliente.email,
            'Informacion_adicional':crear_cliente.informacion
        }

        try:
            with cv.SessionLocal() as connection:
                result = connection.execute(query_main, params)
                print("Filas insertadas:", result.rowcount)
                connection.commit()  # Confirmar la transacción

                return True  # Retornar True si la inserción fue exitosa
        
        except Exception as ex:
            print(f"Error al ejecutar la consulta: {ex}")
            return False  # Retornar False si hubo algún error durante la inserción



    @classmethod
    def numero_clientes(self,db):
        query_main = text("SELECT Id_cliente , Nombre_comercial	 FROM cliente_cv")
        try:
            with cv.SessionLocal() as connection:
                with connection.execute(query_main) as cursor:
                    rows = cursor.fetchall()
                    cantidad_clientes = []
                    if rows != None:
                        for row in rows:
                                cantidad_clientes_2 = Tabla_numero_clientes(row[0],row[1] )
                                cantidad_clientes.append(cantidad_clientes_2)
                        return cantidad_clientes 
                    else:
                        return rows

        except Exception as ex:
            raise Exception(ex)    
        #finally:
        #    cursor.close()#Cierro la conexión   


    @classmethod
    def consulta_clientes(self,db, page_num, elementos_por_pagina):
        query_main = text("SELECT * FROM cliente_cv LIMIT :elementos_por_pagina OFFSET :elementos_por_pagina_2")
        params = {
                 'elementos_por_pagina': elementos_por_pagina,
                 'elementos_por_pagina_2': (page_num - 1) * elementos_por_pagina
        }
        try:
            with cv.SessionLocal() as connection:
                with connection.execute(query_main,params) as cursor:
                    rows = cursor.fetchall()

                    cantidad_clientes = []
                    if rows != None:
                        for row in rows:
                                logging.debug("row_conten:", row)
                                cantidad_clientes_2 = Tabla_Cliente_consulta(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10])
                                cantidad_clientes.append(cantidad_clientes_2)
                        total = len(rows)
                        return cantidad_clientes,total 
                    else:
                        return rows

        except Exception as ex:
            raise Exception(ex)    
 


    @classmethod
    def consulta_clientes_especifico(self,db,especifico):
        query_main = text("SELECT * FROM cliente_cv WHERE Id_cliente = :id_cliente ")
         
        params = {
            'id_cliente': especifico.id_update
        }
        try:
            with cv.SessionLocal() as connection:
                with connection.execute(query_main,params) as cursor:
                    rows = cursor.fetchall()
                    cantidad_clientes = []
                    if rows != None:
                        for row in rows:
                                cantidad_clientes_2 = Tabla_Cliente_actualizar(None,row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10])
                                cantidad_clientes.append(cantidad_clientes_2)
                        return cantidad_clientes 
                    else:
                        return rows

        except Exception as ex:
            raise Exception(ex)    
        finally:
            cursor.close()#Cierro la conexión   
    
    @classmethod
    def update_client(cls, db, crear_cliente):
        query_main = text("""
            UPDATE cliente_cv SET Codigo_interno = :Codigo_interno,Nombre_comercial = :Nombre_comercial,
                Razon_social = :Razon_social,RFC = :RFC, Regimen_fiscal = :Regimen_fiscal,
                Direccion = :Direccion, Codigo_postal = :Codigo_postal, Telefono = :Telefono,
                Email = :Email,Informacion_adicional = :Informacion_adicional
            WHERE id_cliente = :id_cliente;
        """)
        
        params = {
            'id_cliente':crear_cliente.id_update,
            'Codigo_interno': crear_cliente.codigo,
            'Nombre_comercial': crear_cliente.nombre_comercial,
            'Razon_social': crear_cliente.razon,  # Ejemplo de valor para Telefono, asegúrate de usar el valor correcto
            'RFC': crear_cliente.rfc,
            'Regimen_fiscal': crear_cliente.regimen,
            'Direccion': crear_cliente.direccion,
            'Codigo_postal': crear_cliente.cod_pos,
            'Telefono':crear_cliente.telefono,  # Ejemplo de valor para Cambio_contraseña, asegúrate de usar el valor correcto
            'Email': crear_cliente.email,
            'Informacion_adicional':crear_cliente.informacion
        }

        try:
            with cv.SessionLocal() as connection:
                result = connection.execute(query_main, params)
                print("Filas actualizadas:", result.rowcount)
                connection.commit()  # Confirmar la transacción

                return True  # Retornar True si la inserción fue exitosa
        
        except Exception as ex:
            print(f"Error al ejecutar la consulta: {ex}")
            return False  # Retornar False si hubo algún error durante la inserción



    @classmethod
    def eliminar_clientes(cls, db, delete):
        # Consulta para actualizar registros en la tabla ventas_cv
        query_update = text("UPDATE ventas_cv SET Id_cliente_cv = '0' WHERE Id_cliente_cv = :eliminar_Id_cliente_cv;")
        params_update = {'eliminar_Id_cliente_cv': delete.id_cliente}
        
        # Consulta para eliminar un cliente basado en el ID
        query_delete = text("DELETE FROM cliente_cv WHERE Id_cliente = :eliminar_cliente;")
        params_delete = {'eliminar_cliente': delete.id_cliente}

        try:
            # Ejecutar la consulta de actualización en la tabla ventas_cv
            with cv.SessionLocal() as connection:
                result_update = connection.execute(query_update, params_update)
                print("Filas actualizadas en ventas_cv:", result_update.rowcount)
                
                # Ejecutar la consulta de eliminación en la tabla cliente_cv
                result_delete = connection.execute(query_delete, params_delete)
                print("Filas eliminadas en cliente_cv:", result_delete.rowcount)
                
                # Confirmar la transacción
                connection.commit()

            return True  # Retornar True si la operación fue exitosa

        except Exception as ex:
            print(f"Error al ejecutar la consulta: {ex}")
            return False  # Retornar False si hubo algún error durante la operación

    def create_estation(cls, db, crear_estacion):
        query_main = text("""
           INSERT INTO estaciones_cv
            (Codigo_interno, Permiso_cre, Número_de_estación, Nombre_comercial, RFC, Nombre_del_gerente, Dirección, Teléfono, Email,  Información_adicional)
            VALUES (:Codigo_interno, :Permiso_cre, :Numero_de_estacion, :Nombre_comercial, :RFC, :Nombre_del_gerente, :Dirección, :Teléfono, :Email,  :Información_adicional)

        """)
        
        params = {
            'Codigo_interno': crear_estacion.codigo,
            'Permiso_cre': crear_estacion.Permiso,
            'Numero_de_estacion': crear_estacion.estacion,
            'Nombre_comercial': crear_estacion.comercial,
            'RFC': crear_estacion.RFC,
            'Nombre_del_gerente': crear_estacion.gerente,
            'Dirección': crear_estacion.direccion,
            'Teléfono': crear_estacion.telefono,
            'Email': crear_estacion.email,
            #'Id_cliente_cv': crear_estacion.cliente,
            'Información_adicional': crear_estacion.informacion
        }
 
        try:
            # Conectar a la base de datos usando el engine
            with cv.SessionLocal() as connection:
                # Ejecutar la consulta
                result = connection.execute(query_main, params)
                print("Filas insertadas:", result.rowcount)
                connection.commit()  # Confirmar la transacción

                # No es necesario el commit explícito aquí
                return True  # Retornar True si la inserción fue exitosa
        
        except Exception as ex:
            logging.error(f"Error al ejecutar la consulta: {ex}")
            return False  # Retornar False si hubo algún error durante la inserción

    @classmethod
    def numero_estaciones(self,db):
        query_main = text("SELECT Id_estacion , Nombre_comercial FROM estaciones_cv")
        try:
            with cv.SessionLocal() as connection:
                with connection.execute(query_main) as cursor:
                    rows = cursor.fetchall()
                    cantidad_clientes = []
                    if rows != None:
                        for row in rows:
                                cantidad_clientes_2 = Tabla_numero_estaciones(row[0],row[1] )
                                cantidad_clientes.append(cantidad_clientes_2)
                        return cantidad_clientes 
                    else:
                        return rows

        except Exception as ex:
            raise Exception(ex)    
        finally:
            cursor.close()#Cierro la conexión   

    @classmethod
    def eliminar_estacion(self, db, delete):
        # Consulta para eliminar un cliente basado en el ID
        query_main = text("DELETE FROM estaciones_cv WHERE Id_estacion = :eliminar_estacion;")
        params = {'eliminar_estacion': delete.id_estacion}

        # Consulta para actualizar registros en la tabla ventas_cv
        # Reemplaza 'Id_cliente_cv' con el nombre correcto de la columna si es necesario
        query_main_update = text("UPDATE ventas_cv SET Id_estacion_cv = NULL WHERE Id_estacion_cv = :eliminar_Id_estacion_cv;")
        params_update = {'eliminar_Id_estacion_cv': delete.id_estacion}
        try:
            with cv.SessionLocal() as connection_update:
                result_update = connection_update.execute(query_main_update, params_update)
                print("Filas actualizadas en ventas_cv:", result_update.rowcount)
                connection_update.commit()  # Confirmar la transacción
            # Ejecutar la consulta de eliminación en la tabla cliente_cv
            with cv.SessionLocal() as connection:
                result = connection.execute(query_main, params)
                print("Filas eliminadas en estaciones_cv:", result.rowcount)
                connection.commit()  # Confirmar la transacción
            # Ejecutar la consulta de actualización en la tabla ventas_cv

            return True  # Retornar True si la operación fue exitosa

        except Exception as ex:
            print(f"Error al ejecutar la consulta: {ex}")
            return False  # Retornar False si hubo algún error durante la operación

    

    @classmethod
    def consulta_estaciones_especifico(self,db,especifico):
        query_main = text("SELECT * FROM estaciones_cv WHERE Id_estacion = :Id_estacion ")
         
        params = {
            'Id_estacion': especifico.id_update
        }
        try:
            with cv.SessionLocal() as connection:
                with connection.execute(query_main,params) as cursor:
                    rows = cursor.fetchall()
                    cantidad_clientes = []
                    if rows != None:
                        for row in rows:
                                cantidad_clientes_2 = Tabla_Estacion_actualizar(None,row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12])
                                cantidad_clientes.append(cantidad_clientes_2)
                        return cantidad_clientes 
                    else:
                        return rows

        except Exception as ex:
            raise Exception(ex)    
        finally:
            cursor.close()#Cierro la conexión   



    @classmethod
    def update_station(cls, db, actualizar_estacion):
        query_main = text("""
            UPDATE estaciones_cv SET Codigo_interno = :Codigo_interno,
                Permiso_cre = :Permiso_cre,
                Número_de_estación = :Número_de_estación,          
                Nombre_comercial = :Nombre_comercial,          
                RFC = :RFC, Regimen_fiscal = :regimen,
                Nombre_del_gerente = :gerente, Dirección = :Direccion,
                Codigo_postal = :cod_pos, Teléfono = :Telefono,
                Email = :Email, Información_adicional = :Informacion_adicional
            WHERE Id_estacion  = :Id_estacion ;
        """)
        
        params = {
            'Id_estacion':actualizar_estacion.id_update,
            'Codigo_interno': actualizar_estacion.codigo,
            'Permiso_cre': actualizar_estacion.permiso_cre,
            'Número_de_estación': actualizar_estacion.numero_estacion,
            'Nombre_comercial': actualizar_estacion.nombre_comercial,
            'RFC': actualizar_estacion.rfc,
            'regimen': actualizar_estacion.regimen,
            'gerente': actualizar_estacion.gerente,
            'Direccion': actualizar_estacion.direccion,
            'cod_pos': actualizar_estacion.cod_pos,
            'Telefono':actualizar_estacion.telefono,  # Ejemplo de valor para Cambio_contraseña, asegúrate de usar el valor correcto
            'Email': actualizar_estacion.email,
            'Informacion_adicional':actualizar_estacion.informacion
        }

        try:
            with cv.SessionLocal() as connection:
                result = connection.execute(query_main, params)
                print("Filas actualizadas:", result.rowcount)
                connection.commit()  # Confirmar la transacción

                return True  # Retornar True si la inserción fue exitosa
        
        except Exception as ex:
            print(f"Error al ejecutar la consulta: {ex}")
            logging.debug(ex)
            return False  # Retornar False si hubo algún error durante la inserción












    @classmethod
    def numero_proveedores(self,db):
        query_main = text("SELECT Id_Proveedor , Nombre_comercial FROM proveedor_cv")
        try:
            with cv.SessionLocal() as connection:
                with connection.execute(query_main) as cursor:
                    rows = cursor.fetchall()
                    cantidad_clientes = []
                    if rows != None:
                        for row in rows:
                                cantidad_clientes_2 = Tabla_numero_proveedores(row[0],row[1] )
                                cantidad_clientes.append(cantidad_clientes_2)
                        return cantidad_clientes 
                    else:
                        return rows

        except Exception as ex:
            raise Exception(ex)    



    @classmethod
    def consulta_tanques(cls, db, page_num, elementos_por_pagina):
        # Corregimos la consulta SQL, eliminando el 'WHERE'
        query_main = text("""
            SELECT * 
            FROM estaciones_cv 
            LIMIT :elementos_por_pagina OFFSET :elementos_por_pagina_2
        """)

        # Parámetros que se pasarán a la consulta
        params = {
            'elementos_por_pagina': elementos_por_pagina,
            'elementos_por_pagina_2': (page_num - 1) * elementos_por_pagina
        }

        # Verificamos los valores de los parámetros antes de ejecutar la consulta
        print(f"Parámetros de la consulta: {params}")

        try:
            # Establecemos una conexión con la base de datos
            with db.SessionLocal() as connection:  
                # Ejecutamos la consulta pasando los parámetros correctamente
                result = connection.execute(query_main, params)
                rows = result.fetchall()

                # Verificamos si hemos recibido registros
                if rows:  # Si hay registros
                    cantidad_clientes = []
                    for row in rows:
                        cantidad_clientes_2 = Tabla_estaciones_consulta(
                            row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11]
                        )
                        cantidad_clientes.append(cantidad_clientes_2)

                    total = len(rows)
                    return cantidad_clientes, total
                else:
                    return [], 0  # Si no hay registros, retornamos vacío

        except Exception as ex:
            # Captura la excepción y retorna un valor predeterminado
            print(f"Error al consultar los tanques: {ex}")
            return [], 0  # En caso de error, retornamos vacío y total 0



    @classmethod
    def consulta_usuarios(self,db,page_num,elementos_por_pagina):
        query_main = text("SELECT Id,Nombre, nombre_completo,Tipo_usuario FROM usuarios_cv")
        try:
            with cv.SessionLocal() as connection:
                with connection.execute(query_main) as cursor:
                    rows = cursor.fetchall()
                    cantidad_clientes = []
                    if rows != None:
                        for row in rows:
                                cantidad_clientes_2 = Tabla_usuarios_consulta(row[0],row[1],row[2],row[3])
                                cantidad_clientes.append(cantidad_clientes_2)
                        total = len(rows)
                        return cantidad_clientes,total 
                    else:
                        return rows

        except Exception as ex:
            raise Exception(ex)    
        finally:
            cursor.close()#Cierro la conexión   



    @classmethod
    def update_usuario(cls, db, actualizar_estacion):
        query_main = text("""
            UPDATE usuarios_cv SET Nombre = :Nombre,
                nombre_completo = :nombre_completo,
                Password = :Password,          
                Tipo_usuario = :Tipo_usuario          
            WHERE Id = :Id_usuario;
        """)
        
        # Generar hash seguro de la contraseña
        hash_python = generate_password_hash(actualizar_estacion.contraseña)
        
        params = {
            'Id_usuario':actualizar_estacion.id_update,
            'Nombre': actualizar_estacion.Nombre,
            'nombre_completo':actualizar_estacion.nombre_completo,
            'Password':hash_python,
            'Tipo_usuario':actualizar_estacion.Tipo_usuario

        } 
        try:
            with cv.SessionLocal() as connection:
                result = connection.execute(query_main, params)
                print("Filas actualizadas:", result.rowcount)
                connection.commit()  # Confirmar la transacción

                return True  # Retornar True si la inserción fue exitosa
        
        except Exception as ex:
            print(f"Error al ejecutar la consulta: {ex}")
            return False  # Retornar False si hubo algún error durante la inserción
    

    @classmethod
    def rol_perfiles(self,db):
            query_main = text("""SELECT COUNT(*) AS total 
                        FROM  ref_roles;
                        """)
            query_main_2 = text("""SELECT id, nombre
                                FROM ref_roles; 
                                """)
            try:#checa bien lo del nombre del cliente
                with db.engine.connect() as connection:
                     with connection.execute(query_main) as cursor:

                        consultas = cursor.fetchone()
                        total =  consultas[0]
                        
                     with connection.execute(query_main_2) as cursor_2:
                        rows = cursor_2.fetchall()
                        roles = []
                        if rows != None:
                            for row in rows:
                                    perfil_roll = Roles(row[0],row[1],None)
                                    roles.append(perfil_roll)
                            return roles,total
                        else:
                            return rows
                
            except Exception as ex:
                raise Exception(ex)    
#            finally:
#                cursor.close()#Cierro la conexión      



    @classmethod
    def create_user(cls, db, crear_usuario):
        query_main = text("""
            INSERT INTO usuarios_cv
            (Nombre, nombre_completo, Telefono, Password, Tipo_usuario, Cambio_contraseña, Estatus_usuario)
            VALUES (:Nombre, :nombre_completo, :Telefono, :Password, :Tipo_usuario, :Cambio_contraseña, :Estatus_usuario)
        """)
        
        # Generar hash seguro de la contraseña
        hash_python = generate_password_hash(crear_usuario.password_user)
        
        params = {
            'Nombre': crear_usuario.nombre_user,
            'nombre_completo': crear_usuario.nombre_completo,
            'Telefono': 0,  # Ejemplo de valor para Telefono, asegúrate de usar el valor correcto
            'Password': hash_python,
            'Tipo_usuario': crear_usuario.tipo_usuario_user,
            'Cambio_contraseña': 0,  # Ejemplo de valor para Cambio_contraseña, asegúrate de usar el valor correcto
            'Estatus_usuario': crear_usuario.estatus_usuario_user
        }
        
        try:
            with cv.SessionLocal() as connection:
                result = connection.execute(query_main, params)
                print("Filas insertadas:", result.rowcount)
                connection.commit()  # Confirmar la transacción

                return True  # Retornar True si la inserción fue exitosa
        
        except Exception as ex:
            print(f"Error al ejecutar la consulta: {ex}")
            return False  # Retornar False si hubo algún error durante la inserción
    

    @classmethod
    def consulta_usuario_especifico(self,db,especifico):
        query_main = text("SELECT * FROM usuarios_cv WHERE Id = :id_cliente ")
         
        params = {
            'id_cliente': especifico.id_update
        }
        try:
            with cv.SessionLocal() as connection:
                with connection.execute(query_main,params) as cursor:
                    rows = cursor.fetchall()
                    cantidad_clientes = []
                    if rows != None:
                        for row in rows:
                                cantidad_clientes_2 = Tabla_Usuario_actualizar(None,row[0], row[1], row[2], row[3])
                                cantidad_clientes.append(cantidad_clientes_2)
                        return cantidad_clientes 
                    else:
                        return rows

        except Exception as ex:
            raise Exception(ex)    
        finally:
            cursor.close()#Cierro la conexión  





    @classmethod
    def eliminar_Usuario(cls, db, delete):
 
        # Consulta para eliminar un cliente basado en el ID
        query_delete = text("DELETE FROM usuarios_cv WHERE Id  = :eliminar_usuarios;")
        params_delete = {'eliminar_usuarios': delete.id_cliente}

        try:
            # Ejecutar la consulta de actualización en la tabla ventas_cv
            with cv.SessionLocal() as connection:

                # Ejecutar la consulta de eliminación en la tabla cliente_cv
                result_delete = connection.execute(query_delete, params_delete)
                print("Filas eliminadas en cliente_cv:", result_delete.rowcount)
                
                # Confirmar la transacción
                connection.commit()
                connection.close()

            return True  # Retornar True si la operación fue exitosa

        except Exception as ex:
            print(f"Error al ejecutar la consulta: {ex}")
            return False  # Retornar False si hubo algún error durante la operación



#Reciblar o eliminar
#    @classmethod
#    def informe_de_tanques_inicio(self, db, infotanque_inicio):
#        try:
#            cursor = db.connection.cursor()
#            # 1. Obtener valores del tanque al inicio y al fin del día
#            sql_1 = """ SELECT tanques.nivel_actual_fecha_actualizacion, tanques.volumen_natural, tanques.volumen_neto, tanques.temperatura 
#                    FROM tanques 
#                    WHERE tanques.id = %s AND tanques.nivel_actual_fecha_actualizacion BETWEEN %s AND %s LIMIT 1"""
#            cursor.execute(sql_1, (infotanque_inicio.id_tanque_informe,infotanque_inicio.fecha_informe,infotanque_inicio.fecha_informe_2,))
#            mediciones = cursor.fetchall()

#            medicion_dia = []
#            if mediciones:
#                for medicion in mediciones:
#                    medicion_dia_2 = Tabla_informetanque_dia_inicio(None, None, None,medicion[0], medicion[1], medicion[2], medicion[3])
#                    medicion_dia.append(medicion_dia_2)
 
#                return medicion_dia
          

#        except Exception as ex:
            # Manejar la excepción de manera adecuada (registrar, notificar, etc.)
#            raise Exception(ex)

#        finally:
#            cursor.close()
    
#    @classmethod
#    def informe_de_tanques_fin(self, db, infotanque_fin):
#        try:
#            cursor = db.connection.cursor()
#            # 1. Obtener valores del tanque al inicio y al fin del día
#            sql_1 = """ SELECT tanques.nivel_actual_fecha_actualizacion, tanques.volumen_natural, tanques.volumen_neto, tanques.temperatura 
#                    FROM tanques 
#                    WHERE tanques.id = %s AND tanques.nivel_actual_fecha_actualizacion BETWEEN %s AND %s LIMIT 1"""
#            cursor.execute(sql_1, ('2',infotanque_fin.fecha_informe,  infotanque_fin.fecha_informe_2,))
#            mediciones_2 = cursor.fetchall()

#            medicion_dia_fin = []
#            if mediciones_2:
#                for medicion in mediciones_2:
#                    medicion_dia_fin_2 = Tabla_informetanque_dia_fin(None, None, None,medicion[0], medicion[1], medicion[2], medicion[3])
#                    medicion_dia_fin.append(medicion_dia_fin_2)
#                return medicion_dia_fin
          

#        except Exception as ex:
            # Manejar la excepción de manera adecuada (registrar, notificar, etc.)
#            raise Exception(ex)

#        finally:
#            cursor.close()


#    @classmethod
##    def informe_de_tanques_batch(self, db, fecha):
#        cursor = db.connection.cursor()
#        try:

            # 2. Obtener información de la carga/descarga
#            sql_2 = """SELECT id, volumen_natural, volumen_neto, temperatura_promedio, tipo, totalizador_apertura_fecha, totalizador_cierre_fecha 
##                    FROM batch_ucl_carga_descarga 
#                    WHERE totalizador_apertura_fecha BETWEEN %s AND %s AND totalizador_cierre_fecha  BETWEEN %s AND %s AND id_tanque_fk = %s """
#            cursor.execute(sql_2, (fecha.fecha_batch,fecha.fecha_batch_2,fecha.fecha_batch,fecha.fecha_batch_2,fecha.id_tanque_fk_batch,))
#            batch_mediciones = cursor.fetchall()

#            Inicio_electura = []
##            Batch = []
#            Fin_electura = []

##            if batch_mediciones != None:
#                    for batch_medicion in batch_mediciones:
#                            batch_mediciones_2 = batch_ucl_carga_descarga(None,None,None,batch_medicion[0],batch_medicion[1],batch_medicion[2],batch_medicion[3],batch_medicion[4],
#                                                                                            batch_medicion[5],batch_medicion[6])
#                            Batch.append(batch_mediciones_2)



                            # 3. Obtener última medición antes de la fecha de inicio de carga/descarga
#                           sql_3 = """SELECT nivel_actual_fecha_actualizacion, volumen_natural, volumen_neto, temperatura 
#                                    FROM tanques 
##                                    WHERE nivel_actual_fecha_actualizacion < (SELECT MAX(totalizador_apertura_fecha)  
#                                                                              FROM batch_ucl_carga_descarga 
#                                                                              WHERE totalizador_apertura_fecha BETWEEN  %s AND %s  
#                                                                              AND totalizador_cierre_fecha BETWEEN %s AND %s 
#                                                                              AND id_tanque_fk = %s ) 
#                                    LIMIT 1"""
#                            cursor.execute(sql_3, (batch_medicion[5],batch_medicion[6],batch_medicion[5],batch_medicion[6]  ,fecha.id_tanque_fk_batch,))
#                            Medicion_inicio = cursor.fetchone() 
#                            if Medicion_inicio:
#                                        print(Medicion_inicio)
#                                       Medicion_inicio_2 = valor_tanque_inicio(None,None,Medicion_inicio[0],Medicion_inicio[1],Medicion_inicio[2],Medicion_inicio[3] )
#                                        Inicio_electura.append(Medicion_inicio_2)
#                            else:
#                                 print("Error en medición inicio",Medicion_inicio )




                            # 4. Obtener última medición después de la fecha de fin de carga/descarga
#                           sql_4 = """SELECT nivel_actual_fecha_actualizacion, volumen_natural, volumen_neto, temperatura 
#                                            FROM tanques 
#                                            WHERE nivel_actual_fecha_actualizacion > (SELECT MAX(totalizador_apertura_fecha)  
#                                                                                        FROM batch_ucl_carga_descarga 
#                                                                                        WHERE totalizador_apertura_fecha BETWEEN  %s AND %s  
#                                                                                        AND totalizador_cierre_fecha BETWEEN %s AND %s 
#                                                                                        AND id_tanque_fk = %s) 
#                                            LIMIT 1"""
#                            cursor.execute(sql_4, (batch_medicion[5],batch_medicion[6],batch_medicion[5],batch_medicion[6],fecha.id_tanque_fk_batch,))
#                            Medicion_fin = cursor.fetchone()
#                            if Medicion_fin:
#                                    Medicion_fin_2 = valor_tanque_fin(None,None,Medicion_fin[0],Medicion_fin[1],Medicion_fin[2],Medicion_fin[3] )
#                                    Fin_electura.append(Medicion_fin_2)
#                            else:
#                                 print("Error en medición fin",Medicion_fin )



#                    return Inicio_electura,Batch,Fin_electura
#            else:
#                    return batch_mediciones

#        except Exception as ex:
            # Manejar la excepción de manera adecuada (registrar, notificar, etc.)
#            raise Exception(ex)

#        finally:
#            cursor.close()

    #Reciblar
#    @classmethod
#    def operaciones_diarias_cargas(self,db, diarios, page_num,elementos_por_pagina):
#            try:#checa bien lo del nombre del cliente
#                cursor = db.connection.cursor()
#                sql_1 = """SELECT COUNT(*) AS ordenes_cargas
#                        FROM ordenes_de_operacion 
#                        JOIN ordenes_de_operacion_carga ON ordenes_de_operacion.id_carga = ordenes_de_operacion_carga.id
#                        JOIN batch_ucl_carga_descarga ON ordenes_de_operacion_carga.id_orden_fk  = batch_ucl_carga_descarga.id_orden_fk 
#                        JOIN clientes ON  clientes.id = ordenes_de_operacion_carga.id_destinatario_cliente_fk
#                        WHERE ordenes_de_operacion_carga.estado='finalizado' AND ordenes_de_operacion.date_created BETWEEN %s AND %s
#                        """
#                cursor.execute(sql_1,(diarios.fecha_inicio_busqueda, diarios.fecha_fin_busqueda))
#                consultas = cursor.fetchone()
#                total =  consultas[0]



#                sql_2 = """SELECT ordenes_de_operacion_carga.id_orden_fk, DATE(ordenes_de_operacion.date_created),
#                        DATE(ordenes_de_operacion.date_updated),clientes.nombre_comercial,
#                        batch_ucl_carga_descarga.ucl_operador, ordenes_de_operacion_carga.cantidad_programada, 
#                        batch_ucl_carga_descarga.volumen_natural, batch_ucl_carga_descarga.volumen_neto,
#                        batch_ucl_carga_descarga.temperatura_promedio,  ordenes_de_operacion_carga.producto,batch_ucl_carga_descarga.tipo,
#                        ordenes_de_operacion_carga.estado
#                        FROM ordenes_de_operacion 
#                        JOIN ordenes_de_operacion_carga ON ordenes_de_operacion.id_carga = ordenes_de_operacion_carga.id
#                        JOIN batch_ucl_carga_descarga ON ordenes_de_operacion_carga.id_orden_fk  = batch_ucl_carga_descarga.id_orden_fk 
#                        JOIN clientes ON  clientes.id = ordenes_de_operacion_carga.id_destinatario_cliente_fk
#                        WHERE ordenes_de_operacion_carga.estado='finalizado'  AND ordenes_de_operacion.date_created BETWEEN %s AND %s 
#                        LIMIT %s OFFSET %s  """
                
#                cursor.execute(sql_2, (
#                    diarios.fecha_inicio_busqueda, 
#                    diarios.fecha_fin_busqueda, 
#                    elementos_por_pagina, 
#                    ((page_num - 1) * elementos_por_pagina)
#                    ))
#                rows = cursor.fetchall()
#                diarios = []
#                if rows != None:
#                    for row in rows:
#                            diarios_2 = Tabla_operaciones_diarias(None,None,row[0],row[1],row[2],row[3], row[4],row[5], row[6], row[7], row[8], row[9], row[10],
#                                                                row[11])
#                            diarios.append(diarios_2)
#                    return diarios,total
#                else:
#                    return rows
#                
#            except Exception as ex:
#                raise Exception(ex)    
#            finally:
#                cursor.close()#Cierro la conexión 


#    @classmethod
#    def operaciones_diarias_descargas(self,db, diarios, page_num,elementos_por_pagina):
 #           try:#checa bien lo del nombre del cliente
#                cursor = db.connection.cursor()
#                sql_1 = """SELECT COUNT(*) AS ordenes_descargas
#                        FROM ordenes_de_operacion 
#                        JOIN ordenes_de_operacion_descarga ON ordenes_de_operacion.id_carga = ordenes_de_operacion_descarga.id
#                        JOIN batch_ucl_carga_descarga ON ordenes_de_operacion_descarga.id_orden_fk  = batch_ucl_carga_descarga.id_orden_fk 
#                        JOIN proveedores ON  proveedores.id = ordenes_de_operacion_descarga.id_proveedor_fk
#                        WHERE ordenes_de_operacion_descarga.estado='finalizado' AND ordenes_de_operacion.date_created BETWEEN %s AND %s
#                        """
#                cursor.execute(sql_1,(diarios.fecha_inicio_busqueda, diarios.fecha_fin_busqueda))
#                consultas = cursor.fetchone()
#                total =  consultas[0]


#                sql_2 = """SELECT ordenes_de_operacion_descarga.id_orden_fk, ordenes_de_operacion.date_created, ordenes_de_operacion.date_updated,proveedores.nombre_comercial,
#                        batch_ucl_carga_descarga.ucl_operador, ordenes_de_operacion_descarga.cantidad_programada, batch_ucl_carga_descarga.volumen_natural, batch_ucl_carga_descarga.volumen_neto,batch_ucl_carga_descarga.temperatura_promedio,  ordenes_de_operacion_descarga.producto,batch_ucl_carga_descarga.tipo,
#                        ordenes_de_operacion_descarga.estado
#                        FROM ordenes_de_operacion 
#                        JOIN ordenes_de_operacion_descarga ON ordenes_de_operacion.id_carga = ordenes_de_operacion_descarga.id
#                        JOIN batch_ucl_carga_descarga ON ordenes_de_operacion_descarga.id_orden_fk  = batch_ucl_carga_descarga.id_orden_fk 
#                        JOIN proveedores ON  proveedores.id = ordenes_de_operacion_descarga.id_proveedor_fk
#                        WHERE ordenes_de_operacion_descarga.estado='finalizado' and ordenes_de_operacion.date_created BETWEEN %s AND %s
#                        LIMIT %s OFFSET %s"""
#                cursor.execute(sql_2, (
#                    diarios.fecha_inicio_busqueda, 
#                    diarios.fecha_fin_busqueda, 
#                    elementos_por_pagina, 
#                    ((page_num - 1) * elementos_por_pagina)
#                    ))
#               rows = cursor.fetchall()
#                diarios = []
#                if rows != None:
#                    for row in rows:
#                            diarios_3 = Tabla_operaciones_diarias(None,None,row[0],row[1],row[2],row[3], row[4],row[5], row[6], row[7], row[8], row[9], row[10],
#                                                                row[11])
#                            diarios.append(diarios_3)
#                    return diarios,total
#                else:
#                    return rows
#                
##            except Exception as ex:
#                raise Exception(ex)    
#            finally:
#                cursor.close()#Cierro la conexión                


#    @classmethod
#    def operaciones_mensuales_cargas(self,db, diarios, page_num,elementos_por_pagina):
#            try:#checa bien lo del nombre del cliente
#                cursor = db.connection.cursor()
#                sql_1 = """SELECT COUNT(*) AS ordenes_cargas
#                        FROM ordenes_de_operacion 
#                        JOIN ordenes_de_operacion_carga ON ordenes_de_operacion.id_carga = ordenes_de_operacion_carga.id
#                        JOIN batch_ucl_carga_descarga ON ordenes_de_operacion_carga.id_orden_fk  = batch_ucl_carga_descarga.id_orden_fk 
#                        JOIN clientes ON  clientes.id = ordenes_de_operacion_carga.id_destinatario_cliente_fk
#                        WHERE ordenes_de_operacion_carga.estado='finalizado' AND ordenes_de_operacion.date_created BETWEEN %s AND %s
#                        """
#                cursor.execute(sql_1,(diarios.fecha_inicio_busqueda, diarios.fecha_fin_busqueda))

#                consultas = cursor.fetchone()
#                total =  consultas[0]



#               sql_2 = """SELECT ordenes_de_operacion_carga.id_orden_fk, DATE(ordenes_de_operacion.date_created),
#                       DATE(ordenes_de_operacion.date_updated),clientes.nombre_comercial,
#                        batch_ucl_carga_descarga.ucl_operador, ordenes_de_operacion_carga.cantidad_programada, 
#                        batch_ucl_carga_descarga.volumen_natural, batch_ucl_carga_descarga.volumen_neto,
#                        batch_ucl_carga_descarga.temperatura_promedio,  ordenes_de_operacion_carga.producto,batch_ucl_carga_descarga.tipo,
#                        ordenes_de_operacion_carga.estado
#                        FROM ordenes_de_operacion 
#                        JOIN ordenes_de_operacion_carga ON ordenes_de_operacion.id_carga = ordenes_de_operacion_carga.id
#                        JOIN batch_ucl_carga_descarga ON ordenes_de_operacion_carga.id_orden_fk  = batch_ucl_carga_descarga.id_orden_fk 
#                        JOIN clientes ON  clientes.id = ordenes_de_operacion_carga.id_destinatario_cliente_fk
##                        WHERE ordenes_de_operacion_carga.estado='finalizado'  AND ordenes_de_operacion.date_created BETWEEN %s AND %s 
#                        LIMIT %s OFFSET %s  """
                
#                cursor.execute(sql_2, (
#                    diarios.fecha_inicio_busqueda, 
#                    diarios.fecha_fin_busqueda, 
#                    elementos_por_pagina, 
#                    ((page_num - 1) * elementos_por_pagina)
#                    ))
#                rows = cursor.fetchall()
#                diarios = []
#                if rows != None:
##                    for row in rows:
#                           diarios_2 = Tabla_operaciones_mensuales(None,None,row[0],row[1],row[2],row[3], row[4],row[5], row[6], row[7], row[8], row[9], row[10],
#                                                                row[11])
#                            diarios.append(diarios_2)
#                    return diarios,total
#                else:
#                    return rows
                
#            except Exception as ex:
#                raise Exception(ex)    
#            finally:
#                cursor.close()#Cierro la conexión 





    
