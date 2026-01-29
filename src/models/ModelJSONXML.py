
from sqlalchemy.sql import text
from sqlalchemy.exc import SQLAlchemyError


class ModelJSONXML():

    @classmethod 
    def get_tanques_by_producto(self,db,producto):
        query_main = text("SELECT * FROM tanques WHERE producto = :producto")
        params = {'producto' : producto}
        try:    
            with db.engine.connect() as connection:
                    with connection.execute(query_main, params) as cursor:
                        # Obtener todos los resultados
                        tanques = cursor.fetchall()           
                        return tanques
        except Exception as ex:
                raise Exception(f"Error en la consulta: {ex}")    
    
    @classmethod 
    def get_telemedicion_by_tanque(self,db,id_tanque):
        query_main = text("SELECT * FROM telemedicion_tanques WHERE id_tanque_fk =:id_tanque")
        params = {'id_tanque' : id_tanque}

        try:    
            with db.engine.connect() as connection:
                    with connection.execute(query_main, params) as cursor:
                        telemedicion_tanque = cursor.fetchall()
                        return telemedicion_tanque
        except Exception as ex:
                raise Exception(f"Error en la consulta: {ex}")   

    @classmethod 
    def get_servo_by_tanque(self,db,id_servo_fk):
        query_main= text("SELECT * FROM dispositivo_servo WHERE id = :id_servo_fk")
        params = {'id_servo_fk' : id_servo_fk}

        try:
            with db.engine.connect() as connection:
                    with connection.execute(query_main, params) as cursor:
                        dispositivo_servo = cursor.fetchall()
                        return dispositivo_servo
        except Exception as ex:
                raise Exception(f"Error en la consulta: {ex}")  

    @classmethod 
    def get_order_carga_by_date_and_tank(self,db,dato1, fecha_inicio, fecha_fin):
        query_main = text("SELECT * FROM ordenes_de_operacion_carga WHERE id_tanque_fk =:id_tanque_fk  AND estado = 'finalizado' AND fecha_carga BETWEEN :fecha_inicio AND :fecha_fin")
        params = {'id_tanque_fk':dato1,
                'fecha_inicio':fecha_inicio,
                'fecha_fin':fecha_fin}
        try:
            # Consulta SQL para obtener las órdenes de carga
            with db.engine.connect() as connection:
                    with connection.execute(query_main, params) as cursor:
                        # Obtener todos los resultados
                        ordenes_carga = cursor.fetchall()
                        return ordenes_carga
        except Exception as ex:
                raise Exception(f"Error en la consulta: {ex}")  
    
    @classmethod 
    def get_order_descargas_by_date_and_tank(self,db,dato1, fecha_inicio, fecha_fin):
        query_main = text("SELECT * FROM ordenes_de_operacion_descarga WHERE id_tanque_fk = :id_tanque_fk AND estado = 'finalizado' AND fecha_recepcion BETWEEN :fecha_inicio AND :fecha_fin")
        params = {'id_tanque_fk':dato1,
                'fecha_inicio':fecha_inicio,
                'fecha_fin':fecha_fin}    
        try:
            with db.engine.connect() as connection:
                    with connection.execute(query_main, params) as cursor:
                        # Obtener todos los resultados
                        ordenes_carga = cursor.fetchall()
                        return ordenes_carga
        except Exception as ex:
                raise Exception(f"Error en la consulta: {ex}")  

    @classmethod 
    def get_batch_by_id_orden_fk(self,db,id_orden_fk):
        query_main = text("SELECT * FROM batch_ucl_carga_descarga WHERE id_orden_fk = :id_orden_fk; ")
        params = {'id_orden_fk':id_orden_fk}
        try:
            with db.engine.connect() as connection:
                    with connection.execute(query_main, params) as cursor:            
                        resultados_batch = cursor.fetchall()
                        return resultados_batch
        except Exception as ex:
                raise Exception(f"Error en la consulta: {ex}")  

    @classmethod 
    def get_last_lecture_before_order(self,db,id_instrumento_fk,fecha_inicio):
        query_main=text("SELECT * FROM rt_tanques WHERE id_instrumento_fk = :id_instrumento_fk AND fecha < :fecha_inicio  ORDER BY fecha ASC LIMIT 1")
        params = {'id_instrumento_fk':id_instrumento_fk,
                    'fecha_inicio':fecha_inicio}
        try:
            with db.engine.connect() as connection:
                    with connection.execute(query_main, params) as cursor:            
                        resultados_lectura = cursor.fetchall()
                        return resultados_lectura
        except Exception as ex:
                raise Exception(f"Error en la consulta: {ex}")  

    @classmethod 
    def get_last_lecture_after_order(self,db,id_instrumento_fk,fecha_inicio):
        query_main=text("SELECT * FROM rt_tanques WHERE id_instrumento_fk = :id_instrumento_fk AND fecha > :fecha_inicio ORDER BY fecha DESC LIMIT 1")
        params = {'id_instrumento_fk':id_instrumento_fk,
                    'fecha_inicio':fecha_inicio}
        try:
            with db.engine.connect() as connection:
                    with connection.execute(query_main, params) as cursor:            
                        resultados_lectura = cursor.fetchall()
                        return resultados_lectura
        except Exception as ex:
                raise Exception(f"Error en la consulta: {ex}")