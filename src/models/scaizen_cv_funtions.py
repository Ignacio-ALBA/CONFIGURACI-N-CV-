from models import  scaizen_cv as cv, scazen_datadb as scazendb
from config_carpet.config import GlobalConfig
from datetime import datetime, timedelta, timezone
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(filename)s - line %(lineno)d : %(message)s'
)
config = GlobalConfig()


class GeneralReport():
    def __init__(self,cv_id):
        self.cv_id = cv_id
        self.controlesV = cv.ControlesVolumetricos.select_by_id(cv_id)    
        if self.controlesV:
            cvs = self.controlesV 
            self.cv_productos = cv.CvProductoBitacoraBitacoraMensual.select_by_id_cv_fk(cvs.Id_CV)

    def GiveProductsIdsAndMarcaC(self):
        productos = []
        for cv_producto in self.cv_productos:
            producto = cv.Producto.select_by_id(cv_producto.Id_PRODUCTO_fk)
            if producto:
                productos.append({
                    "id_producto_fk":producto.Id_PRODUCTO ,
                    "MarcaComercial":producto.MarcaComercial, 
                    "nombre_producto": producto.nombre_producto,
                    'UnidadDeMedida': producto.UnidadDeMedida,
                    "ClaveProducto": producto.ClaveProducto,
                    })
            else: return None
        return productos

    def GiveProducts(self):
        productos = []
        for cv_producto in self.cv_productos:
            producto = cv.Producto.select_by_id(cv_producto.Id_PRODUCTO_fk)
            producto = cv.query_to_json(producto)
            # Filtrar las claves con valor None o 'No'
            producto_filtrado = {k: v for k, v in producto.items() if v is not None and v != 'No'}
            productos.append(producto_filtrado)
        
        return productos
    
    def GiveCV(self):
        ControlesVolumetricos = {
            "Version":self.controlesV.Version, 
            "RfcContribuyente":self.controlesV.RfcContribuyente, 
            "RfcRepresentanteLegal":self.controlesV.RfcRepresentanteLegal, 
            "RfcProveedor":self.controlesV.RfcProveedor, 
            "RfcProveedores":self.controlesV.RfcProveedores, 
            "TipoCaracter":self.controlesV.TipoCaracter, 
            "ModalidadPermiso":self.controlesV.ModalidadPermiso, 
            "NumPermiso":self.controlesV.NumPermiso, 
            "NumContratoOAsignacion":self.controlesV.NumContratoOAsignacion, 
            "InstalacionAlmacenGasNatural":self.controlesV.InstalacionAlmacenGasNatural, 
            "ClaveInstalacion":self.controlesV.ClaveInstalacion, 
            "DescripcionInstalacion":self.controlesV.DescripcionInstalacion, 
            "GeolocalizacionLatitud":self.controlesV.GeolocalizacionLatitud, 
            "GeolocalizacionLongitud":self.controlesV.GeolocalizacionLongitud, 
            "NumeroPozos":self.controlesV.NumeroPozos, 
            "NumeroTanques":self.controlesV.NumeroTanques, 
            "NumeroDuctosEntradaSalida":self.controlesV.NumeroDuctosEntradaSalida, 
            "NumeroDispensarios":self.controlesV.NumeroDispensarios,
            "NumeroDuctosTransporteDistribucion":self.controlesV.NumeroDuctosTransporteDistribucion
        }
        return ControlesVolumetricos
    
    def GiveGeneralData(self):
        ControlesVolumetricos = self.GiveCV()
        productos = self.GiveProducts()
        ControlesVolumetricos["Productos"] = productos
        return ControlesVolumetricos

    def GiveProductNameById(self,name):
        productosids = {}
        productos = self.GiveProductsIdsAndMarcaC()
        if productos:
            for producto in productos:
                productosids[f'{producto["nombre_producto"]}'] = producto["id_producto_fk"]

            id = productosids[name]
            return id 
        else: return None

class MensualReport():
    def __init__(self,cv_id):
        self.cv_id_fk = cv_id
    def __AddCVMensualOfProduct(self,Producto):
        entregas_mes_id = cv.EntregasMes.add(Producto['ENTREGAS']['TotalEntregasMes'], 
                                            Producto['ENTREGAS']['SumaVolumenEntregadoMes']['ValorNumerico'], 
                                            Producto['ENTREGAS']['SumaVolumenEntregadoMes']['UnidadDeMedida'], 
                                            Producto['ENTREGAS']['TotalDocumentosMes'], 
                                            Producto['ENTREGAS']['ImporteTotalEntregasMes'])
        recepciones_mes_id = cv.RecepcionesMes.add(Producto['RECEPCIONES']['TotalRecepcionesMes'], 
                                                Producto['RECEPCIONES']['SumaVolumenRecepcionMes']['ValorNumerico'], 
                                                Producto['RECEPCIONES']['SumaVolumenRecepcionMes']['UnidadDeMedida'],
                                                Producto['RECEPCIONES']['TotalDocumentosMes'], 
                                                Producto['RECEPCIONES']['ImporteTotalRecepcionesMensual'])
        existencias_mes_id = cv.ReporteDeVolumenMensual.add(Producto['CONTROLDEEXISTENCIAS']['VolumenExistenciasMes']['ValorNumerico'], 
                                                            Producto['CONTROLDEEXISTENCIAS']['VolumenExistenciasMes']['UnidadDeMedida'], 
                                                            Producto['CONTROLDEEXISTENCIAS']['FechaYHoraEstaMedicionMes'])
        return entregas_mes_id, recepciones_mes_id, existencias_mes_id
    
    def AddMensualReportProduct(self,id_producto_fk,Producto,fecha):
        entregas_mes_id, recepciones_mes_id, existencias_mes_id = self.__AddCVMensualOfProduct(Producto)
        id_reporte_fk = cv.ReporteVolumenMensualRecepcionesMEntregasM.add(existencias_mes_id,recepciones_mes_id,entregas_mes_id)
        cv.ProductoTanqueReporteDeVolumenMensual.add_mensual_report(self.cv_id_fk, id_producto_fk, id_reporte_fk,fecha)

class MensualReportFuntions():
    def __init__(self,cv_id):
        self.cv_id_fk = cv_id
        self.general_report_instance = GeneralReport(self.cv_id_fk)
    def SetMensualData(self,fecha_inicio = None, fecha_fin = None):
        if fecha_inicio is None:
            fecha_inicio = config.GET_MESUAL_DATE_START() 
        if fecha_fin is None:
            fecha_fin = config.GET_MESUAL_DATE_END()
        fecha_objeto = datetime.strptime(fecha_fin, "%Y-%m-%d %H:%M:%S")
        reporte_existente = cv.ProductoTanqueReporteDeVolumenMensual.select_for_report_mensual(fecha_objeto.month,fecha_objeto.year,self.cv_id_fk)
        logging.debug(f"reporte_existente: {reporte_existente}")
        if reporte_existente:
            return {'error':f'El reporte para el periodo {fecha_objeto.month} {fecha_objeto.year} ya existe.'}
        
        session = cv.SessionLocal()
        logging.debug(self.general_report_instance.controlesV.Tipo)
        if self.general_report_instance.controlesV.Tipo == "distribuidor":##Funcion como un objeto por eso puede acceder a Tipo
            cargas = session.query(cv.CargaDistribuidor).filter(
                cv.CargaDistribuidor.FechaYHoraInicialEntrega.between(fecha_inicio,fecha_fin)).all()
            descargas = session.query(cv.DescargasDistribuidor).filter(
                cv.DescargasDistribuidor.FechaYHoraInicialRecepcion.between(fecha_inicio,fecha_fin)).all()
        elif self.general_report_instance.controlesV.Tipo == "comercializador":
            cargas = session.query(cv.CargasComercializador).filter(
                cv.CargasComercializador.FechaYHoraInicialEntrega.between(fecha_inicio,fecha_fin)).all()
            descargas = session.query(cv.DescargasComercializador).filter(
                cv.DescargasComercializador.FechaYHoraInicialRecepcion.between(fecha_inicio,fecha_fin)).all()
        session.close()

        if descargas:
            for descarga in descargas:
                if descarga.Temperatura is None or descarga.PresionAbsoluta is None or descarga.Costo is None:
                    faltantes = []
                    if descarga.Temperatura is None:
                        faltantes.append("Temperatura")
                    if descarga.PresionAbsoluta is None:
                        faltantes.append("Presión")
                    if descarga.Costo is None:
                        faltantes.append("Costo")

                    # Formatear la lista de `faltantes` con comas y "y" antes del último elemento
                    if len(faltantes) > 1:
                        faltantes_str = ', '.join(faltantes[:-1]) + " y " + faltantes[-1]
                    elif faltantes:
                        faltantes_str = f' {faltantes[0]} '
                    else:
                        faltantes_str = ' '
                    return {'error':f'Faltan parámetros{faltantes_str}para las ordenes de compra para el reporte en el periodo {fecha_objeto.month} {fecha_objeto.year}'}
        if cargas:
            for carga in cargas:
                if carga.Temperatura is None or carga.PresionAbsoluta is None or carga.Costo is None:
                    faltantes = []
                    if carga.Temperatura is None:
                        faltantes.append("Temperatura")
                    if carga.PresionAbsoluta is None:
                        faltantes.append("Presión")
                    if carga.Costo is None:
                        faltantes.append("Costo")

                    # Formatear la lista de `faltantes` con comas y "y" antes del último elemento
                    if len(faltantes) > 1:
                        faltantes_str = ', '.join(faltantes[:-1]) + " y " + faltantes[-1]
                    elif faltantes:
                        faltantes_str = f' {faltantes[0]} '
                    else:
                        faltantes_str = ' '
                    return {'error':f'Faltan parámetros{faltantes_str}para las ordenes de venta para el reporte en el periodo {fecha_objeto.month} {fecha_objeto.year}'}

        productos = self.general_report_instance.GiveProductsIdsAndMarcaC()
        for producto in productos:

            #entregas = scazendb.OrdenesDeOperacionCarga.get_by_date_and_producto(producto["nombre_producto"], fecha_inicio, fecha_fin)
            #recepciones = scazendb.OrdenesDeOperacionDescarga.get_by_date_and_producto(producto["nombre_producto"], fecha_inicio, fecha_fin)
            if self.general_report_instance.controlesV.Tipo == "distribuidor":
                entregas = cv.CargaDistribuidor.get_by_date_and_producto(producto["nombre_producto"], fecha_inicio, fecha_fin)
                recepciones = cv.DescargasDistribuidor.get_by_date_and_producto(producto["nombre_producto"], fecha_inicio, fecha_fin)
            elif self.general_report_instance.controlesV.Tipo == "comercializador":
                entregas = cv.CargasComercializador.get_by_date_and_producto(producto["nombre_producto"], fecha_inicio, fecha_fin)
                recepciones = cv.DescargasComercializador.get_by_date_and_producto(producto["nombre_producto"], fecha_inicio, fecha_fin)

            SumaVolumenRecepcionMes = 0
            SumaVolumenEntregadoMes = 0
            VolumenExistenciasMes = 0
            RecepcionesTotalDocumentosMes = 0
            EntregasTotalDocumentosMes = 0

            ImporteTotalEntregasMes = 0
            ImporteTotalRecepcionesMensual = 0
            logging.debug(entregas)
            logging.debug(recepciones)
            for recepcion in recepciones:
                if recepcion.Costo is None:
                    return {'error':f'Faltan parámetros costo para las ordenes de compra para el reporte en el periodo {fecha_objeto.month} {fecha_objeto.year}'}
                SumaVolumenRecepcionMes += recepcion.VolumenRecepcion
                ImporteTotalRecepcionesMensual += recepcion.Costo
                
            for entrega in entregas:
                if entrega.Costo is None:
                    {'error':f'Faltan parámetros costo para las ordenes de venta para el reporte en el periodo {fecha_objeto.month} {fecha_objeto.year}'}
                SumaVolumenEntregadoMes += entrega.VolumenEntregado
                ImporteTotalEntregasMes += entrega.Costo

            TotalRecepcionesMes = len(recepciones)
            TotalEntregasMes = len(entregas)

            volumen_existencias = SumaVolumenRecepcionMes - SumaVolumenEntregadoMes
            VolumenExistenciasMes = 0 if volumen_existencias < 0 else volumen_existencias
            #FechaYHoraEstaMedicionMes = datetime.now().astimezone().isoformat()
            FechaYHoraEstaMedicionMes = fecha_objeto.astimezone().isoformat(timespec='seconds')
            reportevolumenmensual = {
                'CONTROLDEEXISTENCIAS':{
                    'VolumenExistenciasMes':{
                        'ValorNumerico':round(VolumenExistenciasMes,3),
                        'UnidadDeMedida':producto["UnidadDeMedida"]
                        },
                    'FechaYHoraEstaMedicionMes':FechaYHoraEstaMedicionMes
                },
                'RECEPCIONES':{
                    'TotalRecepcionesMes': TotalRecepcionesMes,
                    'SumaVolumenRecepcionMes':{
                        'ValorNumerico':round(SumaVolumenRecepcionMes,0),
                        'UnidadDeMedida':producto["UnidadDeMedida"]
                        },
                    'TotalDocumentosMes': RecepcionesTotalDocumentosMes,
                    'ImporteTotalRecepcionesMensual': round(ImporteTotalRecepcionesMensual,3)
                },
                'ENTREGAS':{
                    'TotalEntregasMes': TotalEntregasMes,
                    'SumaVolumenEntregadoMes':{
                        'ValorNumerico':round(SumaVolumenEntregadoMes,0),
                        'UnidadDeMedida':producto["UnidadDeMedida"]
                    },
                    'TotalDocumentosMes': EntregasTotalDocumentosMes,
                    'ImporteTotalEntregasMes': round(ImporteTotalEntregasMes,3)
                } 
            }



            mensual_report_instance = MensualReport(self.cv_id_fk)
            mensual_report_instance.AddMensualReportProduct(producto["id_producto_fk"],reportevolumenmensual,fecha_fin)
        return {'response':True}

    def GetMensualReportAll(self,month, year):
        reports = cv.ProductoTanqueReporteDeVolumenMensual.select_for_report_mensual(month,year,self.cv_id_fk)
        productos_reports = []
        if reports:
            for report in reports:
                reportevolumenmensual = cv.ReporteVolumenMensualRecepcionesMEntregasM.select_by_id(report.Id_REPORTEVOLUMENMENSUAL_RECEPCIONES_M_ENTREGAS_M_fk)
                if reportevolumenmensual:
                    producto = cv.Producto.select_by_id(report.Id_PRODUCTO_fk)
                    recepciones = cv.RecepcionesMes.select_by_id(reportevolumenmensual.Id_RECEPCIONES_M_fk)
                    entregas = cv.EntregasMes.select_by_id(reportevolumenmensual.Id_ENTREGAS_M_fk)
                    existencias = cv.ReporteDeVolumenMensual.select_by_id(reportevolumenmensual.Id_REPORTEDEVOLUMENMENSUAL_fk)
                    productos_reports.append({'producto':producto,
                                            'recepciones':recepciones,
                                            'entregas':entregas,
                                            'existencias':existencias})
                else: return None
            return productos_reports
        else: return None

    def GetMensualReport(self,producto_id,month, year):
        report = cv.ProductoTanqueReporteDeVolumenMensual.select_by_product_for_report_mensual(producto_id,month,year,self.cv_id_fk)
        report = report[0] if report else None

        print(report)
        if report:
            reportevolumenmensual = cv.ReporteVolumenMensualRecepcionesMEntregasM.select_by_id(report.Id_REPORTEVOLUMENMENSUAL_RECEPCIONES_M_ENTREGAS_M_fk)
            
            producto = cv.Producto.select_by_id(report.Id_PRODUCTO_fk )
            recepciones = cv.RecepcionesMes.select_by_id(reportevolumenmensual.Id_RECEPCIONES_M_fk)
            entregas = cv.EntregasMes.select_by_id(reportevolumenmensual.Id_ENTREGAS_M_fk)
            existencias = cv.ReporteDeVolumenMensual.select_by_id(reportevolumenmensual.Id_REPORTEDEVOLUMENMENSUAL_fk)
            return {'producto':producto,
                    'recepciones':recepciones,
                    'entregas':entregas,
                    'existencias':existencias}
        else: return None
    
    def SetMensualOldData(self,fecha_inicio,fecha_fin):   
        productos = self.general_report_instance.GiveProductsIdsAndMarcaC()
        for producto in productos:
            entregas = scazendb.OrdenesDeOperacionCarga.get_by_date_and_producto(producto["nombre_producto"], fecha_inicio, fecha_fin)
            recepciones = scazendb.OrdenesDeOperacionDescarga.get_by_date_and_producto(producto["nombre_producto"], fecha_inicio, fecha_fin)
            TotalRecepcionesMes = len(recepciones)
            TotalEntregasMes = len(entregas)
            SumaVolumenRecepcionMes = 0
            SumaVolumenEntregadoMes = 0
            VolumenExistenciasMes = 0
            RecepcionesTotalDocumentosMes = 0
            EntregasTotalDocumentosMes = 0

            ImporteTotalEntregasMes = 7
            ImporteTotalRecepcionesMensual = 7

            for recepcion in recepciones:
                SumaVolumenRecepcionMes += recepcion.cantidad_recibida
            for entrega in entregas:
                SumaVolumenEntregadoMes += entrega.cantidad_cargada
            volumen_existencias = SumaVolumenRecepcionMes - SumaVolumenEntregadoMes
            VolumenExistenciasMes = 0 if volumen_existencias < 0 else volumen_existencias
            FechaYHoraEstaMedicionMes = fecha_fin.astimezone().isoformat()
            reportevolumenmensual = {
                'CONTROLDEEXISTENCIAS':{
                    'VolumenExistenciasMes':{
                        'ValorNumerico':round(VolumenExistenciasMes,3),
                        'UnidadDeMedida':producto["UnidadDeMedida"]
                        },
                    'FechaYHoraEstaMedicionMes':FechaYHoraEstaMedicionMes
                },
                'RECEPCIONES':{
                    'TotalRecepcionesMes': TotalRecepcionesMes,
                    'SumaVolumenRecepcionMes':{
                        'ValorNumerico':round(SumaVolumenRecepcionMes,0),
                        'UnidadDeMedida':producto["UnidadDeMedida"]
                        },
                    'TotalDocumentosMes': RecepcionesTotalDocumentosMes,
                    'ImporteTotalRecepcionesMensual': round(ImporteTotalRecepcionesMensual,3)
                },
                'ENTREGAS':{
                    'TotalEntregasMes': TotalEntregasMes,
                    'SumaVolumenEntregadoMes':{
                        'ValorNumerico':round(SumaVolumenEntregadoMes,0),
                        'UnidadDeMedida':producto["UnidadDeMedida"]
                    },
                    'TotalDocumentosMes': EntregasTotalDocumentosMes,
                    'ImporteTotalEntregasMes': round(ImporteTotalEntregasMes,3)
                } 
            }

            mensual_report_instance = MensualReport()
            mensual_report_instance.AddMensualReportProduct(producto["id_producto_fk"],reportevolumenmensual,fecha_fin)

class DailyReport():
    def __init__(self,cv_id):
        self.cv_id_fk = cv_id
        self.general_report_instanced_daily = GeneralReport(self.cv_id_fk)
    def __AddCVDailyOfTank(self,tanque_info):
        tanque_data = cv.Tanque.select_by_Codigo(tanque_info['tanque_codigo'])
        # medicion_tanque = cv.MedicionTanque.select_all(1)
        if tanque_data:     
            tanque_id = tanque_data.Id_TANQUE

            entregas_id = cv.Entregas.add(tanque_info['entregas']['TotalEntregas'],tanque_info['entregas']['SumaVolumenEntregado'],
                tanque_info['entregas']['SumaVolumenEntregado_UM'],tanque_info['entregas']['TotalDocumentos'],tanque_info['entregas']['SumaVentas'])
            
            recepciones_id = cv.Recepciones.add(tanque_info['recepciones']['TotalRecepciones'],tanque_info['recepciones']['SumaVolumenRecepciones'],
                tanque_info['recepciones']['SumaVolumenRecepciones_UM'],tanque_info['recepciones']['TotalDocumentos'],tanque_info['recepciones']['SumaCompras'])
            
            existencias_id = cv.Existencias.add(tanque_info['existencias']['VolumenExistenciasAnterior'], tanque_info['existencias']['VolumenAcumOpsRecepcion'],
                tanque_info['existencias']['VolumenAcumOpsRecepcion_UM'], tanque_info['existencias']['HoraRecepcionAcumulado'], tanque_info['existencias']['VolumenAcumOpsEntrega'], 
                tanque_info['existencias']['VolumenAcumOpsEntrega_UM'], tanque_info['existencias']['HoraEntregaAcumulado'], tanque_info['existencias']['VolumenExistencias'],
                tanque_info['existencias']['FechaYHoraEstaEdicion'], tanque_info['existencias']['FechaYHoraEdicionAnterior'])
            
            all_entrega = tanque_info['all_entrega'] 
            all_recepcion = tanque_info['all_recepcion']

            for entrega in all_entrega: 
                if self.general_report_instanced_daily.controlesV.Tipo == "distribuidor":
                    cv.CargaDistribuidor.update_id_entregas_fk(entrega.Id,entregas_id)
                elif self.general_report_instanced_daily.controlesV.Tipo == "comercializador":
                    cv.CargasComercializador.update_id_entregas_fk(entrega.Id,entregas_id)
                
            for recepcion in all_recepcion: 
                if self.general_report_instanced_daily.controlesV.Tipo == "distribuidor":
                    cv.DescargasDistribuidor.update_id_recepciones_fk(recepcion.Id,recepciones_id)
                elif self.general_report_instanced_daily.controlesV.Tipo == "comercializador":
                    cv.DescargasComercializador.update_id_recepciones_fk(recepcion.Id,recepciones_id)

        
            return existencias_id, entregas_id,recepciones_id, tanque_id
        else: return None, None, None, None

    def AddDailylReportTank(self,id_producto_fk,tanque_info,fecha):
        existencias_id, entregas_id,recepciones_id, tanque_id = self.__AddCVDailyOfTank(tanque_info)
        if any(v is not None for v in [existencias_id, entregas_id, recepciones_id, tanque_id]):
            id_reporte_tanque_fk = cv.TanqueExistenciasRecepcionesEntregas.add(tanque_id,existencias_id,recepciones_id,entregas_id)
            cv.ProductoTanqueReporteDeVolumenMensual.add_day_report(self.cv_id_fk, id_producto_fk, id_reporte_tanque_fk,fecha)
        else: return None

class DailyReportFuntions():
    def __init__(self,cv_id):
        self.cv_id_fk = cv_id
        self.general_report_instanced_daily = GeneralReport(self.cv_id_fk)

    def SetDailyData(self,date_start = None, date_end = None):
        if date_start is None:
            date_start = config.GET_DIARIO_DATE_START()
        if date_end is None:
            date_end = config.GET_DIARIO_DATE_END()
        #date_start = "2024-08-6 00:00:00"
        #date_end = "2024-08-6 23:59:59"
        reporte_existente = cv.ProductoTanqueReporteDeVolumenMensual.select_for_report_daily(date_end,self.cv_id_fk)
        logging.debug(f"reporte_existente: {reporte_existente}")
        if reporte_existente:
            return {'error':f'El reporte para la fecha {date_end} ya existe.'}

        session = cv.SessionLocal()
        if self.general_report_instanced_daily.controlesV.Tipo == "distribuidor":
            cargas = session.query(cv.CargaDistribuidor).filter(
                cv.CargaDistribuidor.FechaYHoraInicialEntrega.between(date_start,date_end)).all()
            descargas = session.query(cv.DescargasDistribuidor).filter(
                cv.DescargasDistribuidor.FechaYHoraInicialRecepcion.between(date_start,date_end)).all()
        elif self.general_report_instanced_daily.controlesV.Tipo == "comercializador":
            cargas = session.query(cv.CargasComercializador).filter(
            cv.CargasComercializador.FechaYHoraInicialEntrega.between(date_start,date_end)).all()
            descargas = session.query(cv.DescargasComercializador).filter(
                cv.DescargasComercializador.FechaYHoraInicialRecepcion.between(date_start,date_end)).all()
        session.close()


        if descargas:
            for descarga in descargas:
                if descarga.Temperatura is None or descarga.PresionAbsoluta is None or descarga.Costo is None:
                    faltantes = []
                    if descarga.Temperatura is None:
                        faltantes.append("Temperatura")
                    if descarga.PresionAbsoluta is None:
                        faltantes.append("Presión")
                    if descarga.Costo is None:
                        faltantes.append("Costo")

                    # Formatear la lista de `faltantes` con comas y "y" antes del último elemento
                    if len(faltantes) > 1:
                        faltantes_str = ', '.join(faltantes[:-1]) + " y " + faltantes[-1]
                    elif faltantes:
                        faltantes_str = f' {faltantes[0]} '
                    else:
                        faltantes_str = ' '
                    #return {'error':f'Faltan parámetros{faltantes_str}para las ordenes de compra para el reporte reporte de la fecha {date_end}'}
        if cargas:
            for carga in cargas:
                if carga.Temperatura is None or carga.PresionAbsoluta is None or carga.Costo is None:
                    faltantes = []
                    if carga.Temperatura is None:
                        faltantes.append("Temperatura")
                    if carga.PresionAbsoluta is None:
                        faltantes.append("Presión")
                    if carga.Costo is None:
                        faltantes.append("Costo")

                    # Formatear la lista de `faltantes` con comas y "y" antes del último elemento
                    if len(faltantes) > 1:
                        faltantes_str = ', '.join(faltantes[:-1]) + " y " + faltantes[-1]
                    elif faltantes:
                        faltantes_str = f' {faltantes[0]} '
                    else:
                        faltantes_str = ' '
                    #return {'error':f'Faltan parámetros{faltantes_str}para las ordenes de venta para el reporte de la fecha {date_end}'}

        date_reporte_anterior_obj = datetime.strptime(date_end, "%Y-%m-%d %H:%M:%S")
        date_reporte_anterior = config.GET_DIARIO_DATE_END_BEFORE(date_reporte_anterior_obj)
        reportes_anteriores = cv.ProductoTanqueReporteDeVolumenMensual.select_for_report_daily(date_reporte_anterior,self.cv_id_fk)
        logging.debug(f"reportes_anteriores: {reportes_anteriores}")

        if not reportes_anteriores:
            return {'error':'No existe un reporte previo a esta fecha {date_end}'}

        products = self.general_report_instanced_daily.GiveProductsIdsAndMarcaC()
        for producto in products:
            #tanques = scazendb.Tanque.get_for_product(producto["id_producto_fk"])
            tanques = cv.Tanque.get_for_Id_PRODUCTO_fk(producto["id_producto_fk"])
            if not tanques:
                return {'response': False}
            for tanque in tanques:
                logging.debug(f"Tanque: {tanque.codigo}")
                logging.debug(f"Producto: {tanque.Id_PRODUCTO_fk}")
                logging.debug(f"date_start: {date_start}")
                logging.debug(f"date_end: {date_end}")

                #entregas = cv.CargaDistribuidor.get_by_for_tanque_product_date(tanque.codigo,tanque.producto,date_start,date_end)
                #recepciones = cv.DescargasDistribuidor.get_by_for_tanque_product_date(tanque.codigo,tanque.producto,date_start,date_end)
                if self.general_report_instanced_daily.controlesV.Tipo == "distribuidor":   
                    entregas = cv.CargaDistribuidor.get_by_for_tanque_product_date(tanque.codigo,producto["nombre_producto"],date_start,date_end)
                    recepciones = cv.DescargasDistribuidor.get_by_for_tanque_product_date(tanque.codigo,producto["nombre_producto"],date_start,date_end)
                elif self.general_report_instanced_daily.controlesV.Tipo == "comercializador":
                    entregas = cv.CargasComercializador.get_by_date_and_producto(producto["nombre_producto"],date_start,date_end)
                    recepciones = cv.DescargasComercializador.get_by_date_and_producto(producto["nombre_producto"],date_start,date_end)

                logging.debug(f"entregas: {entregas}")
                logging.debug(f"recepciones: {recepciones}")

                TotalRecepciones = len(recepciones)
                TotalDocumentosEntregas = len(entregas)

                TotalEntregas = len(entregas) 
                TotalDocumentosRecepciones = len(recepciones)

                SumaVolumen_UM = 'UM03'

                SumaVolumenRecepciones = 0
                SumaCompras = 0
                for recepcion in recepciones:
                    if recepcion.Temperatura is None or recepcion.PresionAbsoluta is None or recepcion.Costo is None:
                        faltantes = []
                        if recepcion.Temperatura is None:
                            faltantes.append("Temperatura")
                        if recepcion.PresionAbsoluta is None:
                            faltantes.append("Presión")
                        if recepcion.Costo is None:
                            faltantes.append("Costo")

                        # Formatear la lista de `faltantes` con comas y "y" antes del último elemento
                        if len(faltantes) > 1:
                            faltantes_str = ', '.join(faltantes[:-1]) + " y " + faltantes[-1]
                        elif faltantes:
                            faltantes_str = f' {faltantes[0]} '
                        else:
                            faltantes_str = ' '
                        #return {'error':f'Faltan parámetros{faltantes_str}para las ordenes de compra para el reporte reporte de la fecha {date_end}'}
                    SumaVolumenRecepciones +=  recepcion.VolumenRecepcion
                    SumaCompras += recepcion.Costo

                SumaVolumenEntregado = 0
                SumaVentas = 0
                for entrega in entregas:
                    if entrega.Temperatura is None or entrega.PresionAbsoluta is None or entrega.Costo is None:
                        faltantes = []
                        if entrega.Temperatura is None:
                            faltantes.append("Temperatura")
                        if entrega.PresionAbsoluta is None:
                            faltantes.append("Presión")
                        if entrega.Costo is None:
                            faltantes.append("Costo")

                        # Formatear la lista de `faltantes` con comas y "y" antes del último elemento
                        if len(faltantes) > 1:
                            faltantes_str = ', '.join(faltantes[:-1]) + " y " + faltantes[-1]
                        elif faltantes:
                            faltantes_str = f' {faltantes[0]} '
                        else:
                            faltantes_str = ' '
                        #return {'error':f'Faltan parámetros{faltantes_str}para las ordenes de venta para el reporte reporte de la fecha {date_end}'}
                    SumaVolumenEntregado +=  entrega.VolumenEntregado
                    SumaVentas += entrega.Costo

                entregas_total = {
                    'TotalEntregas':TotalEntregas,
                    'SumaVolumenEntregado':SumaVolumenEntregado,
                    'SumaVolumenEntregado_UM':SumaVolumen_UM,
                    'TotalDocumentos':TotalDocumentosEntregas,
                    'SumaVentas':SumaVentas
                }

                recepciones_total = {
                    'TotalRecepciones':TotalRecepciones,
                    'SumaVolumenRecepciones':SumaVolumenRecepciones,
                    'SumaVolumenRecepciones_UM':SumaVolumen_UM,
                    'TotalDocumentos':TotalDocumentosRecepciones,
                    'SumaCompras':SumaCompras
                }
                date_end_obj = datetime.strptime(date_end, "%Y-%m-%d %H:%M:%S")
                date_reporte_anterior = config.GET_DIARIO_DATE_END_BEFORE(date_end_obj)
                date_end_obj = date_end_obj.replace(tzinfo=timezone.utc)
                
                reporte_anterior_existencias = None
                
                if reportes_anteriores:
                    cv_tanque = cv.Tanque.select_by_Codigo(tanque.codigo)
                    for reporte in reportes_anteriores:  
                        tanque_existencias_recepciones_entregas = cv.TanqueExistenciasRecepcionesEntregas.select_by_id(reporte.Id_TANQUE_EXISTENCIAS_RECEPCIONES_ENTREGAS_fk)
                        if tanque_existencias_recepciones_entregas and  tanque_existencias_recepciones_entregas.Id_TANQUE_fk == cv_tanque.Id_TANQUE:
                            reporte_anterior_existencias = cv.Existencias.select_by_id(tanque_existencias_recepciones_entregas.Id_EXISTENCIAS_fk)
                
                if reporte_anterior_existencias is None:
                    return {'error':'No existe un reporte previo a esta fecha {date_end}'}
                
                VolumenExistenciasAnterior = 0
                FechaYHoraEdicionAnterior = ''
                logging.debug(f"reporte_anterior_existencias{reporte_anterior_existencias}")
                if reporte_anterior_existencias:
                    VolumenExistenciasAnterior = reporte_anterior_existencias.VolumenExistencias
                    FechaYHoraEdicionAnterior = reporte_anterior_existencias.FechaYHoraEstaEdicion

                calculo_VolumenExistencias = (VolumenExistenciasAnterior + SumaVolumenRecepciones) - SumaVolumenEntregado
                #7, 8 y 9
                VolumenExistencias = calculo_VolumenExistencias if calculo_VolumenExistencias > 0 else 0

                # ...existing code...
                identificacion_componente_alarma = "Inconsistencia en la información volumerica."
                if VolumenExistenciasAnterior > 0:  # Evitar división por cero
                    diferencia_porcentual = abs((VolumenExistencias - VolumenExistenciasAnterior) / VolumenExistenciasAnterior) * 100
                    productos_liquidos = ["PR03", "PR07", "PR08", "PR11","PR13"]
                    productos_gaseosos = ["PR09", "PR12"]
                    if (producto["ClaveProducto"] in productos_liquidos and diferencia_porcentual > 0.5) or (producto["ClaveProducto"] in productos_gaseosos and diferencia_porcentual > 1):
                        logging.warning(f"Alarma: Diferencia de volumen excede el límite permitido ({diferencia_porcentual:.2f}%) para el periodo.")
                        descripcion_evento = f"Diferencia de volumen excedida: {diferencia_porcentual:.2f}%."
                        scazendb.Alarma.add(
                            datetime.now(), -1, 1, datetime.now(), 'Sistema', descripcion_evento, 
                            7, identificacion_componente_alarma, "Vigencia de la calibración del sistema de medición del tanque"
                        )

                if VolumenExistencias == VolumenExistenciasAnterior and (SumaVolumenRecepciones > 0 or SumaVolumenEntregado > 0):
                    descripcion_evento = "El volumen de existencias registrado al corte del día es igual al registrado en el corte del día anterior, pero existen registros de entradas o salidas."
                    scazendb.Alarma.add(
                        datetime.now(), -1, 1, datetime.now(), 'Sistema', descripcion_evento, 
                        8, identificacion_componente_alarma, "Vigencia de la calibración del sistema de medición del tanque"
                    )

                if VolumenExistencias < 0:
                    descripcion_evento = f"El volumen de existencias registrado ({VolumenExistencias}) para el producto {producto['nombre_producto']} y sistema de medición {SumaVolumen_UM} es menor a cero."
                    scazendb.Alarma.add(
                        datetime.now(), -1, 1, datetime.now(), 'Sistema', descripcion_evento, 
                        9, identificacion_componente_alarma, "Vigencia de la calibración del sistema de medición del tanque"
                    )

                if VolumenExistencias != VolumenExistenciasAnterior and SumaVolumenRecepciones == 0 and SumaVolumenEntregado == 0:
                    descripcion_evento = "El volumen de existencias registrado en el corte del día varía con respecto al corte del día anterior, pero no existen registros de entradas o salidas en el corte del día."
                    scazendb.Alarma.add(
                        datetime.now(), -1, 1, datetime.now(), 'Sistema', descripcion_evento, 
                        10, identificacion_componente_alarma, "Vigencia de la calibración del sistema de medición del tanque"
                    )

                if SumaVolumenEntregado > (SumaVolumenRecepciones + VolumenExistenciasAnterior):
                    descripcion_evento = (
                        f"El volumen de salidas ({SumaVolumenEntregado}) en un lapso de 24 horas "
                        f"es mayor al volumen de entradas ({SumaVolumenRecepciones}) más el volumen de existencias del corte del día anterior ({VolumenExistenciasAnterior})."
                    )
                    scazendb.Alarma.add(
                        datetime.now(), -1, 1, datetime.now(), 'Sistema', descripcion_evento, 
                        11, identificacion_componente_alarma, "Vigencia de la calibración del sistema de medición del tanque"
                    )
                                
                existencias = {
                    'VolumenExistenciasAnterior':VolumenExistenciasAnterior,
                    'VolumenAcumOpsRecepcion':SumaVolumenRecepciones,
                    'VolumenAcumOpsRecepcion_UM':SumaVolumen_UM,
                    'HoraRecepcionAcumulado':date_end_obj.astimezone().isoformat(timespec='seconds').split('T')[1],
                    'VolumenAcumOpsEntrega':SumaVolumenEntregado,
                    'VolumenAcumOpsEntrega_UM':SumaVolumen_UM,
                    'HoraEntregaAcumulado':date_end_obj.astimezone().isoformat(timespec='seconds').split('T')[1],
                    'VolumenExistencias':VolumenExistencias,
                    'FechaYHoraEstaEdicion':date_end_obj.astimezone().isoformat(),
                    'FechaYHoraEdicionAnterior':FechaYHoraEdicionAnterior
                }

                tanque_info = {
                    'tanque_codigo':tanque.codigo,
                    'all_entrega':entregas,
                    'all_recepcion':recepciones,
                    'entregas':entregas_total,
                    'recepciones':recepciones_total,
                    'existencias':existencias
                }
                Daily_report_instance = DailyReport(self.cv_id_fk)
                Daily_report_instance.AddDailylReportTank(producto["id_producto_fk"],tanque_info,date_end_obj)
        return {'response': True}

    def __OrderDataReport(self,reports):
        productos_reports = []
        productos_dict = {}
        if reports:
            for report in reports:
                reportetanque = cv.TanqueExistenciasRecepcionesEntregas.select_by_id(report.Id_TANQUE_EXISTENCIAS_RECEPCIONES_ENTREGAS_fk)
                tanque = cv.Tanque.select_by_id(reportetanque.Id_TANQUE_fk)
                medicion_tanque = cv.MedicionTanque.select_by_id(tanque.Id_MedicionTanque_fk)
                if medicion_tanque and medicion_tanque.VigenciaCalibracionSistMedicionTanque < datetime.now():
                    descripcion_evento = f"La vigencia de la calibración del sistema de medición del tanque {tanque.codigo} ha expirado."
                    #scazendb.Alarma.add(
                    #    datetime.now(), -1, 1, datetime.now(), 'Sistema', descripcion_evento, 
                    #    1, tanque.codigo, "Vigencia de la calibración del sistema de medición del tanque"
                    #)

                existencias = cv.Existencias.select_by_id(reportetanque.Id_EXISTENCIAS_fk)
                recepciones = cv.Recepciones.select_by_id(reportetanque.Id_RECEPCIONES_fk)
                entregas = cv.Entregas.select_by_id(reportetanque.Id_ENTREGAS_fk)


                if self.general_report_instanced_daily.controlesV.Tipo == "distribuidor":
                    recepciones_all = cv.DescargasDistribuidor.select_by_id_recepciones_fk(reportetanque.Id_RECEPCIONES_fk)
                    entregas_all = cv.CargaDistribuidor.select_by_id_entregas_fk(reportetanque.Id_ENTREGAS_fk)
                elif self.general_report_instanced_daily.controlesV.Tipo == "comercializador":
                    recepciones_all = cv.DescargasComercializador.select_by_id_recepciones_fk(reportetanque.Id_RECEPCIONES_fk)
                    entregas_all = cv.CargasComercializador.select_by_id_entregas_fk(reportetanque.Id_ENTREGAS_fk)

                id_producto = report.Id_PRODUCTO_fk

                
                if id_producto not in productos_dict:
                    producto = cv.Producto.select_by_id(id_producto)
                    productos_dict[id_producto] = {
                        'producto': producto,
                        'tanques': []
                    }

                productos_dict[id_producto]['tanques'].append({
                    'tanque': tanque,
                    'medicion_tanque': [medicion_tanque],
                    'existencias': existencias,
                    'recepciones': recepciones,
                    'entregas': entregas,
                    'recepcion': recepciones_all,
                    'entrega': entregas_all
                })

            productos_reports = [reportes for reportes in productos_dict.values()]
            return productos_reports
        
    def __OrderDataReportComplement(self,reports,tipo_operacion,operacion,recepcion_entrega=None):
        complementos = []
        complementos_distribuidor = {}
        logging.debug("recepcion_dato_2", type(operacion))
        if reports:
                    
                    Terminalalmytrans = cv.TerminalAlmYTransTerminalAlmYDist.select_by_id(reports.Id_TERMINAL_ALMYTRANS_ALMYDIST_fk)
                    if Terminalalmytrans:
                            Almacenamiento = cv.Almacenamiento.select_by_id(Terminalalmytrans.Almacenamiento)
                            Transporte = cv.Transporte.select_by_id(Terminalalmytrans.Transporte)
                    Trasvase = cv.Trasvase.select_by_id(reports.Id_TRASVASE_fk)
                    Dictamen = cv.Dictamen.select_by_id(reports.Id_DICTAMEN_fk)

                    

                    Certificado =cv.Certificado.select_by_id(reports.Id_CERTIFICADO_fk)
                    id_complemento_nacional_extranjero = cv.Complemento_nacional_extranjero.select_by_id(reports.Id_complemento)

                    #Nacional_cfdis = cv.Nacional.select_by_id(id_complemento_nacional_extranjero.Id_NACIONAL_fk)
                    Nacional_cfdis = operacion
                    Cliente_Proveedor = None
                    cfdis = None
                    #logging.debug("Nacional_cfdis", str(Nacional_cfdis))
                    #logging.debug(cv.query_to_json([Nacional_cfdis]))
                    if Nacional_cfdis != None:
                        if tipo_operacion == 'D' or (recepcion_entrega == 'R_cv' and recepcion_entrega != None):
                            Cliente_Proveedor = cv.ProveedorCV.select_by_Id_Proveedor(Nacional_cfdis.id_proveedor_fk)
                        else:
                            logging.debug("Nacional_cfdis", str(Nacional_cfdis))
                            # logging.debug("parametros:", tipo_operacion)
                            # logging.debug("Id_cliente_cv_fk:", Nacional_cfdis.Id_cliente_cv_fk)
                            # logging.debug("Id_estacion_cv_fk:", Nacional_cfdis.Id_estacion_cv_fk)

                            if Nacional_cfdis.Id_cliente_cv_fk != -1:
                                Cliente_Proveedor = cv.ClienteCV.select_by_Id_cliente(Nacional_cfdis.Id_cliente_cv_fk)
                            elif Nacional_cfdis.Id_estacion_cv_fk != -1:
                                Cliente_Proveedor = cv.EstacionesCV.select_by_Id_estacion(Nacional_cfdis.Id_estacion_cv_fk)
                                #logging.debug("Cliente_Proveedor", Cliente_Proveedor)

                        
                        tipo_complemento =  reports.Tipo
                        if tipo_complemento == 'distribuidor':
                                    #cfdis = cv.CfdisDistribuidor.select_by_id_nacional_fk(Nacional_cfdis.Id_NACIONAL)
                                    cfdis = cv.CfdisDistribuidor.select_by_id(Nacional_cfdis.Id_cfdi_distribuidor_fk)
                        elif tipo_complemento == 'comercializador':
                                    #cfdis = cv.CfdisComercializador.select_by_id_nacional_fk(Nacional_cfdis.Id_NACIONAL)
                                    cfdis = cv.CfdisComercializador.select_by_id(Nacional_cfdis.Id_cfdi_comercializador_fk)


                    Extranjero =cv.Extranjero.select_by_id(id_complemento_nacional_extranjero.Id_EXTRANGERO_fk )
                    if Extranjero:
                            pedimentos = cv.Pedimentos.select_by_id_pedimentos_fk(Extranjero.Id_PEDIMENTOS_fk)
                        
                    Aclaracion =id_complemento_nacional_extranjero.ACLARACION

                    id_complemento = reports.Id_complemento
                    if id_complemento not in complementos_distribuidor:
                                id_complement = cv.Complemento.select_by_id(id_complemento)
                                complementos_distribuidor[id_complemento]={
                                'Complemento':id_complement,
                                'TERMINALALMYTRANS_TERMINALALMYDIST': [],
                                'TRASVASE':[],
                                'DICTAMEN':[],
                                'CERTIFICADO':[],
                                'NACIONAL':[],
                                'EXTRANJERO':[],
                                'ACLARACION':[]
                                }

                    complementos_distribuidor[id_complemento]['TERMINALALMYTRANS_TERMINALALMYDIST']={
                                        'TERMINALALMYTRANS': Terminalalmytrans,
                                        'Almacenamiento':Almacenamiento,
                                        'Transporte':Transporte
                    }
                    complementos_distribuidor[id_complemento]['TRASVASE'].append({
                                    'TRASVASE': Trasvase
                            })
                    complementos_distribuidor[id_complemento]['DICTAMEN']={
                                    'DICTAMEN': Dictamen
                                }
                    complementos_distribuidor[id_complemento]['CERTIFICADO']={
                                    'CERTIFICADO': Certificado
                                }
                    complementos_distribuidor[id_complemento]['NACIONAL'].append({
                                        'NACIONAL': Cliente_Proveedor,
                                        'cfdis':[cfdis]
                                })
                    complementos_distribuidor[id_complemento]['EXTRANJERO'].append({
                                        'EXTRANJERO': Extranjero,
                                        'pedimentos':pedimentos
                                })
                    complementos_distribuidor[id_complemento]['ACLARACION']={
                                    'ACLARACION': Aclaracion
                                }

                    complementos = [complemento for complemento in complementos_distribuidor.values()]
                    return complementos

        else: return None

    def __OrderDataReportByTank(self,reports,tank):
        productos_reports = []
        productos_dict = {}
        if reports:
            for report in reports:
                reportetanque = cv.TanqueExistenciasRecepcionesEntregas.select_by_id(report.Id_TANQUE_EXISTENCIAS_RECEPCIONES_ENTREGAS_fk)
                tanque = cv.Tanque.select_by_id(reportetanque.Id_TANQUE_fk)
                if tanque  and tanque.ClaveIdentificacionTanque == tank:
                    medicion_tanque = cv.MedicionTanque.select_by_id(tanque.Id_MedicionTanque_fk)

                    existencias = cv.Existencias.select_by_id(reportetanque.Id_EXISTENCIAS_fk)
                    recepciones = cv.Recepciones.select_by_id(reportetanque.Id_RECEPCIONES_fk)
                    entregas = cv.Entregas.select_by_id(reportetanque.Id_ENTREGAS_fk)

                    if self.general_report_instanced_daily.controlesV.Tipo == "distribuidor":
                        recepciones_all = cv.DescargasDistribuidor.select_by_id_recepciones_fk(reportetanque.Id_RECEPCIONES_fk)
                        entregas_all = cv.CargaDistribuidor.select_by_id_entregas_fk(reportetanque.Id_ENTREGAS_fk)
                    elif self.general_report_instanced_daily.controlesV.Tipo == "comercializador":
                        recepciones_all = cv.DescargasComercializador.select_by_id_recepciones_fk(reportetanque.Id_RECEPCIONES_fk)
                        entregas_all = cv.CargasComercializador.select_by_id_entregas_fk(reportetanque.Id_ENTREGAS_fk)
                        id_producto = report.Id_PRODUCTO_fk

                    if id_producto not in productos_dict:
                        producto = cv.Producto.select_by_id(id_producto)
                        productos_dict[id_producto] = {
                            'producto': producto,
                            'tanques': []
                        }

                    productos_dict[id_producto]['tanques'].append({
                        'tanque': tanque,
                        'medicion_tanque': medicion_tanque,
                        'existencias': existencias,
                        'recepciones': recepciones,
                        'entregas': entregas,
                        'recepcion': recepciones_all,
                        'entrega': entregas_all
                    })

                    productos_reports = [reportes for reportes in productos_dict.values()]
                    return productos_reports
        else: return None
        
    def GetDailyReportAll(self, date):
        logging.exception("GetDailyReportAll: ", date, "id: ", self.cv_id_fk)
        reports = cv.ProductoTanqueReporteDeVolumenMensual.select_for_report_daily(date,self.cv_id_fk)
        logging.debug("reports_content", reports)
        logging.exception("__OrderDataReport: ", self.__OrderDataReport(reports))
        return self.__OrderDataReport(reports)
            
    def GetComplementDailyReportAll(self, date,date2,tipo_operacion,operacion,recepcion_entrega=None):
        reports = cv.Complemento.select_by_id_tipo(date,date2)
        #logging.debug("reports_content", reports)

        return self.__OrderDataReportComplement(reports,tipo_operacion,operacion,recepcion_entrega)

    def GetDailyReportByProductAll(self, product_id, date):
        SessionLocal = cv.SessionLocal
        session = SessionLocal()
        tabla = cv.ProductoTanqueReporteDeVolumenMensual
        reports = session.query(tabla).filter(
            tabla.FECHA == date, 
            tabla.TIPO_REPORTE == 'Diario',
            tabla.Id_PRODUCTO_fk == product_id,
            tabla.Id_CV_fk == self.cv_id_fk
        ).all()
        session.close()
        return self.__OrderDataReport(reports)
    
    def GetDailyReportByProductAndTank(self, product_id,tank, date):
        SessionLocal = cv.SessionLocal
        session = SessionLocal()
        tabla = cv.ProductoTanqueReporteDeVolumenMensual
        reports = session.query(tabla).filter(
            tabla.FECHA == date, 
            tabla.TIPO_REPORTE == 'Diario',
            tabla.Id_PRODUCTO_fk == product_id,
            tabla.Id_CV_fk == self.cv_id_fk
        ).all()
        session.close()
        return self.__OrderDataReportByTank(reports,tank)
    
    def GetDailyReportByOneTank(self,tank, date):
        SessionLocal = cv.SessionLocal
        session = SessionLocal()
        tabla = cv.ProductoTanqueReporteDeVolumenMensual
        reports = session.query(tabla).filter(
            tabla.FECHA == date, 
            tabla.TIPO_REPORTE == 'Diario',
            tabla.Id_CV_fk == self.cv_id_fk
        ).all()
        session.close()
        return self.__OrderDataReportByTank(reports,tank)



class Cv_configuration():
    def __init__(self):
        self.cv_Configuration = None

    def Select_cv(dato):
        registros = cv.ControlesVolumetricos.select_type(dato)

        if not registros:
            return []

        data = []

        for registro in registros:
            cv_dict = {
                'Id_CV': registro.Id_CV,
                'Version': registro.Version,
                'RfcContribuyente': registro.RfcContribuyente,
                'RfcRepresentanteLegal': registro.RfcRepresentanteLegal,
                'RfcProveedor': registro.RfcProveedor,
                'RfcProveedores': registro.RfcProveedores,
                'TipoCaracter': registro.TipoCaracter,
                'ModalidadPermiso': registro.ModalidadPermiso,
                'NumPermiso': registro.NumPermiso,
                'NumContratoOAsignacion': registro.NumContratoOAsignacion,
                'InstalacionAlmacenGasNatural': registro.InstalacionAlmacenGasNatural,
                'ClaveInstalacion': registro.ClaveInstalacion,
                'DescripcionInstalacion': registro.DescripcionInstalacion,
                'GeolocalizacionLatitud': registro.GeolocalizacionLatitud,
                'GeolocalizacionLongitud': registro.GeolocalizacionLongitud,
                'NumeroPozos': registro.NumeroPozos,
                'NumeroTanques': registro.NumeroTanques,
                'NumeroDuctosEntradaSalida': registro.NumeroDuctosEntradaSalida,
                'NumeroDuctosTransporteDistribucion': registro.NumeroDuctosTransporteDistribucion,
                'NumeroDispensarios': registro.NumeroDispensarios,
                'Tipo': registro.Tipo,
                ##'anexos': []
                'total_anexos':0
            }

            anexos = cv.CvProductoBitacoraBitacoraMensual \
                .select_by_id_cv_fk(registro.Id_CV)

            #for anexo in anexos:
            cv_dict['total_anexos'] =len(anexos)
            """    cv_dict['anexos'].append({
                    'id': anexo.id,
                    'id_producto_fk': anexo.id_producto_fk,
                    'id_bitacora_fk': anexo.id_bitacora_fk,
                    'id_bitacoramensual_fk': anexo.id_bitacoramensual_fk,
                })
            """
            data.append(cv_dict)

        return data

    def Add_cv(self,data):
            Actividad = data.get("Actividad")
            Version = data.get("Version")
            RfcContribuyente = data.get("RfcContribuyente")
            RfcRepresentanteLegal = data.get("RfcRepresentanteLegal")
            RfcProveedor = data.get("RfcProveedor")
            RfcProveedores = data.get("RfcProveedores")
            
            Caracter = data.get("Caracter",{})#es un dict

            TipoCaracter = Caracter["TipoCaracter"]
            ModalidadPermiso = Caracter["ModalidadPermiso"]
            NumPermiso =  Caracter["NumPermiso"]
            NumContratoOAsignacion = Caracter["NumContratoOAsignacion"]
            InstalacionAlmacenGasNatural = Caracter["InstalacionAlmacenGasNatural"]
            
            ClaveInstalacion = data.get("ClaveInstalacion")
            DescripcionInstalacion = data.get("DescripcionInstalacion")
            
            Geolocalizacion = data.get("Geolocalizacion")#es un dict

            GeolocalizacionLatitud = Geolocalizacion.get("GeolocalizacionLatitud")
            GeolocalizacionLongitud = Geolocalizacion.get("GeolocalizacionLongitud")

            NumeroPozos= data.get("NumeroPozos")
            NumeroTanques =data.get("NumeroTanques")
            NumeroDuctosEntradaSalida = data.get("NumeroDuctosEntradaSalida")
            NumeroDuctosTransporte = data.get("NumeroDuctosTransporte")
            NumeroDispensario=data.get("NumeroDispensario")
            #FechaYHoraCorte=data.get("FechaYHoraCorte")

            result = cv.ControlesVolumetricos.add(
                Version,RfcContribuyente,RfcRepresentanteLegal,RfcProveedor,RfcProveedores,
                TipoCaracter,ModalidadPermiso,NumPermiso,NumContratoOAsignacion,InstalacionAlmacenGasNatural,
                ClaveInstalacion,DescripcionInstalacion,
                GeolocalizacionLatitud,GeolocalizacionLongitud,
                NumeroPozos,NumeroTanques,NumeroDuctosEntradaSalida,NumeroDuctosTransporte,NumeroDispensario,Actividad
                )
            return result
    def Delete_cv(self,data):
        result = cv.ControlesVolumetricos.delete(data)
        return result   
    def Update_cv(self,id, data):

        def filter_dict(data, allowed_fields):
            return {k: v for k, v in data.items() if k in allowed_fields and v is not None}

        CAMPOS_PERMITIDOS_CV = {
            "Actividad","Version","RfcContribuyente","RfcRepresentanteLegal",
            "RfcProveedor","RfcProveedores","ClaveInstalacion","DescripcionInstalacion",
            "NumeroPozos","NumeroTanques","NumeroDuctosEntradaSalida",
            "NumeroDuctosTransporte","NumeroDispensario","Caracter","Geolocalizacion"
        }

        CAMPOS_PERMITIDOS_CARACTER = {
            "TipoCaracter","ModalidadPermiso","NumPermiso",
            "NumContratoOAsignacion","InstalacionAlmacenGasNatural"
        }

        CAMPOS_PERMITIDOS_GEO = {"GeolocalizacionLatitud","GeolocalizacionLongitud"}

        # Primer filtro
        data = filter_dict(data, CAMPOS_PERMITIDOS_CV)

        # Segundo filtro anidado: Caracter
        if "Caracter" in data and isinstance(data["Caracter"], dict):
            data["Caracter"] = filter_dict(data["Caracter"], CAMPOS_PERMITIDOS_CARACTER)

        # Segundo filtro anidado: Geolocalizacion
        if "Geolocalizacion" in data and isinstance(data["Geolocalizacion"], dict):
            data["Geolocalizacion"] = filter_dict(data["Geolocalizacion"], CAMPOS_PERMITIDOS_GEO)


        Actividad = data.get("Actividad")
        Version = data.get("Version")
        RfcContribuyente = data.get("RfcContribuyente")
        RfcRepresentanteLegal = data.get("RfcRepresentanteLegal")
        RfcProveedor = data.get("RfcProveedor")
        RfcProveedores = data.get("RfcProveedores")
            
        Caracter = data.get("Caracter",{})#es un dict

        TipoCaracter = Caracter["TipoCaracter"]
        ModalidadPermiso = Caracter["ModalidadPermiso"]
        NumPermiso =  Caracter["NumPermiso"]
        NumContratoOAsignacion = Caracter["NumContratoOAsignacion"]
        InstalacionAlmacenGasNatural = Caracter["InstalacionAlmacenGasNatural"]
            
        ClaveInstalacion = data.get("ClaveInstalacion")
        DescripcionInstalacion = data.get("DescripcionInstalacion")
            
        Geolocalizacion = data.get("Geolocalizacion")#es un dict

        GeolocalizacionLatitud = Geolocalizacion.get("GeolocalizacionLatitud")
        GeolocalizacionLongitud = Geolocalizacion.get("GeolocalizacionLongitud")

        NumeroPozos= data.get("NumeroPozos")
        NumeroTanques =data.get("NumeroTanques")
        NumeroDuctosEntradaSalida = data.get("NumeroDuctosEntradaSalida")
        NumeroDuctosTransporte = data.get("NumeroDuctosTransporte")
        NumeroDispensario=data.get("NumeroDispensario")




        if data and "Caracter" in data and "Geolocalizacion" in data:
            result = cv.ControlesVolumetricos.update(id,Version,RfcContribuyente,RfcRepresentanteLegal,RfcProveedor,RfcProveedores,
                TipoCaracter,ModalidadPermiso,NumPermiso,NumContratoOAsignacion,InstalacionAlmacenGasNatural,
                ClaveInstalacion,DescripcionInstalacion,
                GeolocalizacionLatitud,GeolocalizacionLongitud,
                NumeroPozos,NumeroTanques,NumeroDuctosEntradaSalida,NumeroDuctosTransporte,NumeroDispensario,Actividad
            )
        else:
            result = None


        return result






class Producto_configuration():
    def __init__(self):
        self.cv_Configuration = None
    def map_producto(scout):

        scouts= cv.CvProductoBitacoraBitacoraMensual.scout_select(scout)
        data = []
        logging.info(scouts)
        for scout_obj, id_producto in scouts:
            map_data = cv.Producto.select_producto(id_producto)            
            if map_data:
                ##voy agregando datos
                data.extend([
                    {
                        'Id_PRODUCTO': map_[0],
                        'ClaveProducto': map_[1]
                    }
                    for map_ in map_data
            ])
        logging.info(data)
        #logging.info(scouts)

        return data


    def Select_producto(id):
        producto = cv.Producto.select_by_id(id)
        if not producto:
            return {}

        data = {
            'Id_PRODUCTO': producto.Id_PRODUCTO,
            'ClaveProducto': producto.ClaveProducto,
            'ClaveSubProducto': producto.ClaveSubProducto,
            'ComposOctanajeGasolina': producto.ComposOctanajeGasolina,
            'GasolinaConCombustibleNoFosil': producto.GasolinaConCombustibleNoFosil,
            'ComposDeCombustibleNoFosilEnGasolina': producto.ComposDeCombustibleNoFosilEnGasolina,
            'DieselConCombustibleNoFosil': producto.DieselConCombustibleNoFosil,
            'ComposDeCombustibleNoFosilEnDiesel': producto.ComposDeCombustibleNoFosilEnDiesel,
            'TurbosinaConCombustibleNoFosil': producto.TurbosinaConCombustibleNoFosil,
            'ComposDeCombustibleNoFosilEnTurbosina': producto.ComposDeCombustibleNoFosilEnTurbosina,
            'ComposDePropanoEnGasLP': producto.ComposDePropanoEnGasLP,
            'ComposDeButanoEnGasLp': producto.ComposDeButanoEnGasLp,
            'DensidadDePetroleo': producto.DensidadDePetroleo,
            'ComposDeAzufreEnPetroleo': producto.ComposDeAzufreEnPetroleo,
            'Otros': producto.Otros,
            'MarcaComercial': producto.MarcaComercial,
            'Marcaje': producto.Marcaje,
            'ConcentracionSustanciasMarcaje': producto.ConcentracionSustanciasMarcaje,
            'nombre_producto': producto.nombre_producto,
            'UnidadDeMedida': producto.UnidadDeMedida,
            'Tanque': 0,
            'Ducto': 0,
            'Pozo': 0,
            'Dispensario': 0
        }

        numero_tanques = cv.Tanque.get_for_Id_PRODUCTO_fk(producto.Id_PRODUCTO)
        for t in numero_tanques:
         logging.info(f"Tanque ID: {t.Id_TANQUE}")
        
        logging.info(numero_tanques)
        data['Tanque'] = len(numero_tanques)

        return data


    def Add_cv(self,data):
            Actividad = data.get("Actividad")
            Version = data.get("Version")
            RfcContribuyente = data.get("RfcContribuyente")
            RfcRepresentanteLegal = data.get("RfcRepresentanteLegal")
            RfcProveedor = data.get("RfcProveedor")
            RfcProveedores = data.get("RfcProveedores")
            
            Caracter = data.get("Caracter",{})#es un dict

            TipoCaracter = Caracter["TipoCaracter"]
            ModalidadPermiso = Caracter["ModalidadPermiso"]
            NumPermiso =  Caracter["NumPermiso"]
            NumContratoOAsignacion = Caracter["NumContratoOAsignacion"]
            InstalacionAlmacenGasNatural = Caracter["InstalacionAlmacenGasNatural"]
            
            ClaveInstalacion = data.get("ClaveInstalacion")
            DescripcionInstalacion = data.get("DescripcionInstalacion")
            
            Geolocalizacion = data.get("Geolocalizacion")#es un dict

            GeolocalizacionLatitud = Geolocalizacion.get("GeolocalizacionLatitud")
            GeolocalizacionLongitud = Geolocalizacion.get("GeolocalizacionLongitud")

            NumeroPozos= data.get("NumeroPozos")
            NumeroTanques =data.get("NumeroTanques")
            NumeroDuctosEntradaSalida = data.get("NumeroDuctosEntradaSalida")
            NumeroDuctosTransporte = data.get("NumeroDuctosTransporte")
            NumeroDispensario=data.get("NumeroDispensario")
            #FechaYHoraCorte=data.get("FechaYHoraCorte")

            result = cv.ControlesVolumetricos.add(
                Version,RfcContribuyente,RfcRepresentanteLegal,RfcProveedor,RfcProveedores,
                TipoCaracter,ModalidadPermiso,NumPermiso,NumContratoOAsignacion,InstalacionAlmacenGasNatural,
                ClaveInstalacion,DescripcionInstalacion,
                GeolocalizacionLatitud,GeolocalizacionLongitud,
                NumeroPozos,NumeroTanques,NumeroDuctosEntradaSalida,NumeroDuctosTransporte,NumeroDispensario,Actividad
                )
            return result
    def Delete_cv(self,data):
        result = cv.ControlesVolumetricos.delete(data)
        return result   
    def Update_cv(self,id, data):

        def filter_dict(data, allowed_fields):
            return {k: v for k, v in data.items() if k in allowed_fields and v is not None}

        CAMPOS_PERMITIDOS_CV = {
            "Actividad","Version","RfcContribuyente","RfcRepresentanteLegal",
            "RfcProveedor","RfcProveedores","ClaveInstalacion","DescripcionInstalacion",
            "NumeroPozos","NumeroTanques","NumeroDuctosEntradaSalida",
            "NumeroDuctosTransporte","NumeroDispensario","Caracter","Geolocalizacion"
        }

        CAMPOS_PERMITIDOS_CARACTER = {
            "TipoCaracter","ModalidadPermiso","NumPermiso",
            "NumContratoOAsignacion","InstalacionAlmacenGasNatural"
        }

        CAMPOS_PERMITIDOS_GEO = {"GeolocalizacionLatitud","GeolocalizacionLongitud"}

        # Primer filtro
        data = filter_dict(data, CAMPOS_PERMITIDOS_CV)

        # Segundo filtro anidado: Caracter
        if "Caracter" in data and isinstance(data["Caracter"], dict):
            data["Caracter"] = filter_dict(data["Caracter"], CAMPOS_PERMITIDOS_CARACTER)

        # Segundo filtro anidado: Geolocalizacion
        if "Geolocalizacion" in data and isinstance(data["Geolocalizacion"], dict):
            data["Geolocalizacion"] = filter_dict(data["Geolocalizacion"], CAMPOS_PERMITIDOS_GEO)


        Actividad = data.get("Actividad")
        Version = data.get("Version")
        RfcContribuyente = data.get("RfcContribuyente")
        RfcRepresentanteLegal = data.get("RfcRepresentanteLegal")
        RfcProveedor = data.get("RfcProveedor")
        RfcProveedores = data.get("RfcProveedores")
            
        Caracter = data.get("Caracter",{})#es un dict

        TipoCaracter = Caracter["TipoCaracter"]
        ModalidadPermiso = Caracter["ModalidadPermiso"]
        NumPermiso =  Caracter["NumPermiso"]
        NumContratoOAsignacion = Caracter["NumContratoOAsignacion"]
        InstalacionAlmacenGasNatural = Caracter["InstalacionAlmacenGasNatural"]
            
        ClaveInstalacion = data.get("ClaveInstalacion")
        DescripcionInstalacion = data.get("DescripcionInstalacion")
            
        Geolocalizacion = data.get("Geolocalizacion")#es un dict

        GeolocalizacionLatitud = Geolocalizacion.get("GeolocalizacionLatitud")
        GeolocalizacionLongitud = Geolocalizacion.get("GeolocalizacionLongitud")

        NumeroPozos= data.get("NumeroPozos")
        NumeroTanques =data.get("NumeroTanques")
        NumeroDuctosEntradaSalida = data.get("NumeroDuctosEntradaSalida")
        NumeroDuctosTransporte = data.get("NumeroDuctosTransporte")
        NumeroDispensario=data.get("NumeroDispensario")




        if data and "Caracter" in data and "Geolocalizacion" in data:
            result = cv.ControlesVolumetricos.update(id,Version,RfcContribuyente,RfcRepresentanteLegal,RfcProveedor,RfcProveedores,
                TipoCaracter,ModalidadPermiso,NumPermiso,NumContratoOAsignacion,InstalacionAlmacenGasNatural,
                ClaveInstalacion,DescripcionInstalacion,
                GeolocalizacionLatitud,GeolocalizacionLongitud,
                NumeroPozos,NumeroTanques,NumeroDuctosEntradaSalida,NumeroDuctosTransporte,NumeroDispensario,Actividad
            )
        else:
            result = None


        return result







class Terminal_configuration():
    def __init__(self):
        self.cv_Configuration = None
    def map_terminal(scout,type_):
        if type_=="tanque":
                scouts= cv.Tanque.scout_select(scout)
                data = []
                logging.info(scouts)
                for id_tanque, codigo in scouts:
                    data.append({
                        'Id_TANQUE': id_tanque,
                        'codigo': codigo
                    })
                return data
        elif type_ =="pozo":
                scouts= cv.Pozo.scout_select(scout)
                data = []
                logging.info(scouts)
                for id_pozo, codigo in scouts:
                    data.append({
                        'Id_POZO': id_pozo,
                        'ClavePozo': codigo
                    })
                return data
        elif type_ =="ducto":
                scouts= cv.Ducto.scout_select(scout)
                data = []
                logging.info(scouts)
                for id_ducto, codigo in scouts:
                    data.append({
                        'Id_DUCTO': id_ducto,
                        'ClaveIdentificacionDucto': codigo
                    })
                return data
        elif type_ =="dispensario":
                scouts= cv.Dispensario.scout_select(scout)
                data = []
                logging.info(scouts)
                for id_dispensario, codigo in scouts:
                    data.append({
                        'Id_DISPENSARIO': id_dispensario,
                        'ClaveDispensario': codigo
                    })
                return data

    def Select_terminal(id,type_):
            if type_=="tanque":
                    tanque= cv.Tanque.select_by_id(id)

                    data = []
                    if tanque:
                        data = {'Id_TANQUE':tanque.Id_TANQUE ,
                                'Id_MedicionTanque_fk':tanque.Id_MedicionTanque_fk,
                                'ClaveIdentificacionTanque':tanque.ClaveIdentificacionTanque,
                                'codigo':tanque.codigo,
                                'Id_PRODUCTO_fk':None,
                                'LocalizacionYODescripcionTanque':tanque.LocalizacionYODescripcionTanque,
                                'VigenciaCalibracionTanque':tanque.VigenciaCalibracionTanque,
                                'CapacidadTotalTanque':tanque.CapacidadTotalTanque,
                                'CapacidadTotalTanque_UM':tanque.CapacidadTotalTanque_UM,
                                'CapacidadOperativaTanque':tanque.CapacidadOperativaTanque,
                                'CapacidadOperativaTanque_UM':tanque.CapacidadOperativaTanque_UM,
                                'CapacidadUtilTanque':tanque.CapacidadUtilTanque,
                                'CapacidadUtilTanque_UM':tanque.CapacidadUtilTanque_UM,
                                'CapacidadFondajeTanque':tanque.CapacidadFondajeTanque,
                                'CapacidadFondajeTanque_UM':tanque.CapacidadFondajeTanque_UM,
                                'CapacidadGasTalon':tanque.CapacidadGasTalon,
                                'CapacidadGasTalon_UM':tanque.CapacidadGasTalon_UM,
                                'VolumenMinimoOperacion':tanque.VolumenMinimoOperacion,
                                'VolumenMinimoOperacion_UM':tanque.VolumenMinimoOperacion_UM,
                                'EstadoTanque':tanque.EstadoTanque,
                                'Numero_Medidores':1
                                }
                        ##modificar
                        #data['Numero_Medidores']=len(tanque.Id_MedicionTanque_fk)

                        return data


    def Add_cv(self,data):
            Actividad = data.get("Actividad")
            Version = data.get("Version")
            RfcContribuyente = data.get("RfcContribuyente")
            RfcRepresentanteLegal = data.get("RfcRepresentanteLegal")
            RfcProveedor = data.get("RfcProveedor")
            RfcProveedores = data.get("RfcProveedores")
            
            Caracter = data.get("Caracter",{})#es un dict

            TipoCaracter = Caracter["TipoCaracter"]
            ModalidadPermiso = Caracter["ModalidadPermiso"]
            NumPermiso =  Caracter["NumPermiso"]
            NumContratoOAsignacion = Caracter["NumContratoOAsignacion"]
            InstalacionAlmacenGasNatural = Caracter["InstalacionAlmacenGasNatural"]
            
            ClaveInstalacion = data.get("ClaveInstalacion")
            DescripcionInstalacion = data.get("DescripcionInstalacion")
            
            Geolocalizacion = data.get("Geolocalizacion")#es un dict

            GeolocalizacionLatitud = Geolocalizacion.get("GeolocalizacionLatitud")
            GeolocalizacionLongitud = Geolocalizacion.get("GeolocalizacionLongitud")

            NumeroPozos= data.get("NumeroPozos")
            NumeroTanques =data.get("NumeroTanques")
            NumeroDuctosEntradaSalida = data.get("NumeroDuctosEntradaSalida")
            NumeroDuctosTransporte = data.get("NumeroDuctosTransporte")
            NumeroDispensario=data.get("NumeroDispensario")
            #FechaYHoraCorte=data.get("FechaYHoraCorte")

            result = cv.ControlesVolumetricos.add(
                Version,RfcContribuyente,RfcRepresentanteLegal,RfcProveedor,RfcProveedores,
                TipoCaracter,ModalidadPermiso,NumPermiso,NumContratoOAsignacion,InstalacionAlmacenGasNatural,
                ClaveInstalacion,DescripcionInstalacion,
                GeolocalizacionLatitud,GeolocalizacionLongitud,
                NumeroPozos,NumeroTanques,NumeroDuctosEntradaSalida,NumeroDuctosTransporte,NumeroDispensario,Actividad
                )
            return result
    def Delete_cv(self,data):
        result = cv.ControlesVolumetricos.delete(data)
        return result   
    def Update_cv(self,id, data):

        def filter_dict(data, allowed_fields):
            return {k: v for k, v in data.items() if k in allowed_fields and v is not None}

        CAMPOS_PERMITIDOS_CV = {
            "Actividad","Version","RfcContribuyente","RfcRepresentanteLegal",
            "RfcProveedor","RfcProveedores","ClaveInstalacion","DescripcionInstalacion",
            "NumeroPozos","NumeroTanques","NumeroDuctosEntradaSalida",
            "NumeroDuctosTransporte","NumeroDispensario","Caracter","Geolocalizacion"
        }

        CAMPOS_PERMITIDOS_CARACTER = {
            "TipoCaracter","ModalidadPermiso","NumPermiso",
            "NumContratoOAsignacion","InstalacionAlmacenGasNatural"
        }

        CAMPOS_PERMITIDOS_GEO = {"GeolocalizacionLatitud","GeolocalizacionLongitud"}

        # Primer filtro
        data = filter_dict(data, CAMPOS_PERMITIDOS_CV)

        # Segundo filtro anidado: Caracter
        if "Caracter" in data and isinstance(data["Caracter"], dict):
            data["Caracter"] = filter_dict(data["Caracter"], CAMPOS_PERMITIDOS_CARACTER)

        # Segundo filtro anidado: Geolocalizacion
        if "Geolocalizacion" in data and isinstance(data["Geolocalizacion"], dict):
            data["Geolocalizacion"] = filter_dict(data["Geolocalizacion"], CAMPOS_PERMITIDOS_GEO)


        Actividad = data.get("Actividad")
        Version = data.get("Version")
        RfcContribuyente = data.get("RfcContribuyente")
        RfcRepresentanteLegal = data.get("RfcRepresentanteLegal")
        RfcProveedor = data.get("RfcProveedor")
        RfcProveedores = data.get("RfcProveedores")
            
        Caracter = data.get("Caracter",{})#es un dict

        TipoCaracter = Caracter["TipoCaracter"]
        ModalidadPermiso = Caracter["ModalidadPermiso"]
        NumPermiso =  Caracter["NumPermiso"]
        NumContratoOAsignacion = Caracter["NumContratoOAsignacion"]
        InstalacionAlmacenGasNatural = Caracter["InstalacionAlmacenGasNatural"]
            
        ClaveInstalacion = data.get("ClaveInstalacion")
        DescripcionInstalacion = data.get("DescripcionInstalacion")
            
        Geolocalizacion = data.get("Geolocalizacion")#es un dict

        GeolocalizacionLatitud = Geolocalizacion.get("GeolocalizacionLatitud")
        GeolocalizacionLongitud = Geolocalizacion.get("GeolocalizacionLongitud")

        NumeroPozos= data.get("NumeroPozos")
        NumeroTanques =data.get("NumeroTanques")
        NumeroDuctosEntradaSalida = data.get("NumeroDuctosEntradaSalida")
        NumeroDuctosTransporte = data.get("NumeroDuctosTransporte")
        NumeroDispensario=data.get("NumeroDispensario")




        if data and "Caracter" in data and "Geolocalizacion" in data:
            result = cv.ControlesVolumetricos.update(id,Version,RfcContribuyente,RfcRepresentanteLegal,RfcProveedor,RfcProveedores,
                TipoCaracter,ModalidadPermiso,NumPermiso,NumContratoOAsignacion,InstalacionAlmacenGasNatural,
                ClaveInstalacion,DescripcionInstalacion,
                GeolocalizacionLatitud,GeolocalizacionLongitud,
                NumeroPozos,NumeroTanques,NumeroDuctosEntradaSalida,NumeroDuctosTransporte,NumeroDispensario,Actividad
            )
        else:
            result = None


        return result







class Medidore_configuration():
    def __init__(self):
        self.cv_Configuration = None
    def map_medidores(scout,type_):
        if type_=="medidor_tanque":
                scouts= cv.MedicionTanque.scout_select(scout)
                data = []
                logging.info(scouts)
                for id_medicion_tanque, SistemaMedicionTanque in scouts:
                    data.append({
                        'Id_MedicionTanque': id_medicion_tanque,
                        'SistemaMedicionTanque': SistemaMedicionTanque
                    })
                return data
        
        elif type_ =="medidor_pozo":
                scouts= cv.MedicionPozo.scout_select(scout)
                data = []
                logging.info(scouts)
                for id_medicion_pozo, SistemaMedicionPozo in scouts:
                    data.append({
                        'Id_MedicionPozo': id_medicion_pozo,
                        'SistemaMedicionPozo': SistemaMedicionPozo
                    })
                return data
        elif type_ =="medidor_ducto":
                scouts= cv.MedicionDucto.scout_select(scout)
                data = []
                logging.info(scouts)
                for id_medicion_ducto, SistemaMedicionDucto in scouts:
                    data.append({
                        'Id_MedicionDucto': id_medicion_ducto,
                        'SistemaMedicionDucto': SistemaMedicionDucto
                    })
                return data
        elif type_ =="medidor_dispensario":
                scouts= cv.MedicionDispensario.scout_select(scout)
                data = []
                logging.info(scouts)
                for id_medicion_dispensario, SistemaMedicionDispensario in scouts:
                    data.append({
                        'Id_MedicionDispensario': id_medicion_dispensario,
                        'SistemaMedicionDispensario': SistemaMedicionDispensario
                    })
                return data


    def Select_medidores(id,type_):
            if type_=="medidores_tanque":
                    medicion= cv.MedicionTanque.select_by_id(id)

                    data = []
                    if medicion:
                        data = {'Id_MedicionTanque':medicion.Id_MedicionTanque ,
                                'SistemaMedicionTanque':medicion.SistemaMedicionTanque,
                                'LocalizODescripSistMedicionTanque':medicion.LocalizODescripSistMedicionTanque,
                                'VigenciaCalibracionSistMedicionTanque':medicion.VigenciaCalibracionSistMedicionTanque,
                                'IncertidumbreMedicionSistMedicionTanque':medicion.IncertidumbreMedicionSistMedicionTanque,

                                }
                        ##modificar
                        #data['Numero_Medidores']=len(tanque.Id_MedicionTanque_fk)

                        return data
            elif type_=="medidores_pozo":
                    medicion= cv.MedicionPozo.select_by_id(id)

                    data = []
                    if medicion:
                        data = {'Id_MedicionPozo':medicion.Id_MedicionPozo ,
                                'SistemaMedicionPozo':medicion.SistemaMedicionPozo,
                                'LocalizODescripSistMedicionPozo':medicion.LocalizODescripSistMedicionPozo,
                                'VigenciaCalibracionSistMedicionPozo':medicion.VigenciaCalibracionSistMedicionPozo,
                                'IncertidumbreMedicionSistMedicionPozo':medicion.IncertidumbreMedicionSistMedicionPozo,

                                }
                        ##modificar
                        #data['Numero_Medidores']=len(tanque.Id_MedicionTanque_fk)

                        return data
                
            elif type_=="medidores_ducto":
                    medicion= cv.MedicionDucto.select_by_id(id)

                    data = []
                    if medicion:
                        data = {'Id_MedicionDucto':medicion.Id_MedicionDucto ,
                                'SistemaMedicionDucto':medicion.SistemaMedicionDucto,
                                'LocalizODescripSistMedicionDucto':medicion.LocalizODescripSistMedicionDucto,
                                'VigenciaCalibracionSistMedicionDucto':medicion.VigenciaCalibracionSistMedicionDucto,
                                'IncertidumbreMedicionSistMedicionDucto':medicion.IncertidumbreMedicionSistMedicionDucto,

                                }
                        ##modificar
                        #data['Numero_Medidores']=len(tanque.Id_MedicionTanque_fk)

                        return data
            elif type_=="medidores_dispensario":
                    medicion= cv.MedicionDispensario.select_by_id(id)

                    data = []
                    if medicion:
                        data = {'Id_MedicionDispensario':medicion.Id_MedicionDispensario  ,
                                'SistemaMedicionDispensario':medicion.SistemaMedicionPozo,
                                'LocalizODescripSistMedicionDispensario':medicion.LocalizODescripSistMedicionDispensario,
                                'VigenciaCalibracionSistMedicionDispensario':medicion.VigenciaCalibracionSistMedicionDispensario,
                                'IncertidumbreMedicionSistMedicionDispensario':medicion.IncertidumbreMedicionSistMedicionDispensario,

                                }
                        ##modificar
                        #data['Numero_Medidores']=len(tanque.Id_MedicionTanque_fk)

                        return data
 
    def Add_cv(self,data):
            Actividad = data.get("Actividad")
            Version = data.get("Version")
            RfcContribuyente = data.get("RfcContribuyente")
            RfcRepresentanteLegal = data.get("RfcRepresentanteLegal")
            RfcProveedor = data.get("RfcProveedor")
            RfcProveedores = data.get("RfcProveedores")
            
            Caracter = data.get("Caracter",{})#es un dict

            TipoCaracter = Caracter["TipoCaracter"]
            ModalidadPermiso = Caracter["ModalidadPermiso"]
            NumPermiso =  Caracter["NumPermiso"]
            NumContratoOAsignacion = Caracter["NumContratoOAsignacion"]
            InstalacionAlmacenGasNatural = Caracter["InstalacionAlmacenGasNatural"]
            
            ClaveInstalacion = data.get("ClaveInstalacion")
            DescripcionInstalacion = data.get("DescripcionInstalacion")
            
            Geolocalizacion = data.get("Geolocalizacion")#es un dict

            GeolocalizacionLatitud = Geolocalizacion.get("GeolocalizacionLatitud")
            GeolocalizacionLongitud = Geolocalizacion.get("GeolocalizacionLongitud")

            NumeroPozos= data.get("NumeroPozos")
            NumeroTanques =data.get("NumeroTanques")
            NumeroDuctosEntradaSalida = data.get("NumeroDuctosEntradaSalida")
            NumeroDuctosTransporte = data.get("NumeroDuctosTransporte")
            NumeroDispensario=data.get("NumeroDispensario")
            #FechaYHoraCorte=data.get("FechaYHoraCorte")

            result = cv.ControlesVolumetricos.add(
                Version,RfcContribuyente,RfcRepresentanteLegal,RfcProveedor,RfcProveedores,
                TipoCaracter,ModalidadPermiso,NumPermiso,NumContratoOAsignacion,InstalacionAlmacenGasNatural,
                ClaveInstalacion,DescripcionInstalacion,
                GeolocalizacionLatitud,GeolocalizacionLongitud,
                NumeroPozos,NumeroTanques,NumeroDuctosEntradaSalida,NumeroDuctosTransporte,NumeroDispensario,Actividad
                )
            return result
    def Delete_cv(self,data):
        result = cv.ControlesVolumetricos.delete(data)
        return result   
    def Update_cv(self,id, data):

        def filter_dict(data, allowed_fields):
            return {k: v for k, v in data.items() if k in allowed_fields and v is not None}

        CAMPOS_PERMITIDOS_CV = {
            "Actividad","Version","RfcContribuyente","RfcRepresentanteLegal",
            "RfcProveedor","RfcProveedores","ClaveInstalacion","DescripcionInstalacion",
            "NumeroPozos","NumeroTanques","NumeroDuctosEntradaSalida",
            "NumeroDuctosTransporte","NumeroDispensario","Caracter","Geolocalizacion"
        }

        CAMPOS_PERMITIDOS_CARACTER = {
            "TipoCaracter","ModalidadPermiso","NumPermiso",
            "NumContratoOAsignacion","InstalacionAlmacenGasNatural"
        }

        CAMPOS_PERMITIDOS_GEO = {"GeolocalizacionLatitud","GeolocalizacionLongitud"}

        # Primer filtro
        data = filter_dict(data, CAMPOS_PERMITIDOS_CV)

        # Segundo filtro anidado: Caracter
        if "Caracter" in data and isinstance(data["Caracter"], dict):
            data["Caracter"] = filter_dict(data["Caracter"], CAMPOS_PERMITIDOS_CARACTER)

        # Segundo filtro anidado: Geolocalizacion
        if "Geolocalizacion" in data and isinstance(data["Geolocalizacion"], dict):
            data["Geolocalizacion"] = filter_dict(data["Geolocalizacion"], CAMPOS_PERMITIDOS_GEO)


        Actividad = data.get("Actividad")
        Version = data.get("Version")
        RfcContribuyente = data.get("RfcContribuyente")
        RfcRepresentanteLegal = data.get("RfcRepresentanteLegal")
        RfcProveedor = data.get("RfcProveedor")
        RfcProveedores = data.get("RfcProveedores")
            
        Caracter = data.get("Caracter",{})#es un dict

        TipoCaracter = Caracter["TipoCaracter"]
        ModalidadPermiso = Caracter["ModalidadPermiso"]
        NumPermiso =  Caracter["NumPermiso"]
        NumContratoOAsignacion = Caracter["NumContratoOAsignacion"]
        InstalacionAlmacenGasNatural = Caracter["InstalacionAlmacenGasNatural"]
            
        ClaveInstalacion = data.get("ClaveInstalacion")
        DescripcionInstalacion = data.get("DescripcionInstalacion")
            
        Geolocalizacion = data.get("Geolocalizacion")#es un dict

        GeolocalizacionLatitud = Geolocalizacion.get("GeolocalizacionLatitud")
        GeolocalizacionLongitud = Geolocalizacion.get("GeolocalizacionLongitud")

        NumeroPozos= data.get("NumeroPozos")
        NumeroTanques =data.get("NumeroTanques")
        NumeroDuctosEntradaSalida = data.get("NumeroDuctosEntradaSalida")
        NumeroDuctosTransporte = data.get("NumeroDuctosTransporte")
        NumeroDispensario=data.get("NumeroDispensario")




        if data and "Caracter" in data and "Geolocalizacion" in data:
            result = cv.ControlesVolumetricos.update(id,Version,RfcContribuyente,RfcRepresentanteLegal,RfcProveedor,RfcProveedores,
                TipoCaracter,ModalidadPermiso,NumPermiso,NumContratoOAsignacion,InstalacionAlmacenGasNatural,
                ClaveInstalacion,DescripcionInstalacion,
                GeolocalizacionLatitud,GeolocalizacionLongitud,
                NumeroPozos,NumeroTanques,NumeroDuctosEntradaSalida,NumeroDuctosTransporte,NumeroDispensario,Actividad
            )
        else:
            result = None


        return result




class Complementos_configuration():
    # cargar bajo demanda (lazy loading) o precargar todo (eager loading).
    def Select_complemento(dato):
        registros = cv.Complemento.select_by_tipo(dato)

        if not registros:
            return []

        data = [] 
        
        terminal_alm_trans=cv.TerminalAlmYTransTerminalAlmYDist.select_by_id(registros.Id_TERMINAL_ALMYTRANS_ALMYDIST_fk)
        
        almacen= 0
        transporte= 0
        if terminal_alm_trans:
            almacen= terminal_alm_trans.Almacenamiento
            transporte=terminal_alm_trans.Transporte

        if registros:
            complementos={
                'Id_complemento':registros.Id_complemento,
                'Id_Almacenamiento':almacen,
                'Id_Transporte':transporte ,
                'Id_TRASVASE':registros.Id_TRASVASE_fk,
                'Id_DICTAMEN':registros.Id_DICTAMEN_fk,
                'Id_CERTIFICADO':registros.Id_CERTIFICADO_fk,
                'List_Nac':[],
                'List_Ext':[],
                'Aclaracion':[]
            }
            id= registros.Id_complemento    
            comp_naci_extra =cv.Complemento_nacional_extranjero.select_all_by_id_complement(id)
            for dato in comp_naci_extra:
                complementos['List_Nac'].append(dato.Id_NACIONAL_fk )                
                complementos['List_Ext'].append(dato.Id_EXTRANGERO_fk )
                complementos['Aclaracion'].append(dato.ACLARACION)

            data.append(complementos)

        return data


class Complementos_almacen_configuration():
    def Select_almacen(dato):
        registros = cv.Almacen.select_by_id(dato)

        if not registros:
            return []

        data = [] 
        if registros:
            almacen={
                'terminal':registros.TerminalAlm,
                'permiso':registros.PermisoAlmacenamiento,
                'tarifaDeAlm':registros.TarifaDeAlmacenamiento,
                'cargoPorCapacidad':registros.CargoPorCapacidadAlmac,
                'cargoPorUso':registros.CargoPorUsoAlmac,
                'cargoVolumetrico':registros.CargoVolumetricoAlmac
            }
            data.append(almacen)
        return data
