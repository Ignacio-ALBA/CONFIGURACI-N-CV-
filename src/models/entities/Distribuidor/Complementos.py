from lxml import etree
from lxml.etree import Element, SubElement, tostring
import xmlschema
import os
import json
from jsonschema import validate, ValidationError
import logging
import traceback
from models.scaizen_cv_funtions import *
from flask import Flask, jsonify

class Comp_Distribucion():

    @classmethod 
    def load_json_structure(cls,file_path):
        """Lee la estructura JSON desde un archivo con codificación UTF-8."""
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)


    @classmethod 
    def Comp_Distribucion_schema_json(cls,id_complemento,tipo,tipo_operacion,operacion):
        try:
            complemendo_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),"..", "..", "..","static/schemes/distribuidor/complemento/Comp-Distribucion.schema.json"))
            estructura = cls.load_json_structure(complemendo_dir)
            DailyReportFuntionsInstance = DailyReportFuntions(1)
            print("Holacomplemento")

            complementos_date = DailyReportFuntionsInstance.GetComplementDailyReportAll(id_complemento,tipo,tipo_operacion,operacion)
            if complementos_date:
                    for complementos in complementos_date:
                        TerminalAlmYTrans_reporte = {}
                        TerminalAlmYTrans = complementos['TERMINALALMYTRANS_TERMINALALMYDIST']
                        print(f"aqui53 {TerminalAlmYTrans}")
                        TerminalAlmYTrans_item = {
                                    "Almacenamiento":{
                                        "TerminalAlm": TerminalAlmYTrans['Almacenamiento'].TerminalAlm,
                                        "PermisoAlmacenamiento":TerminalAlmYTrans['Almacenamiento'].PermisoAlmacenamiento,
                                        "TarifaDeAlmacenamiento":TerminalAlmYTrans['Almacenamiento'].TarifaDeAlmacenamiento,
                                        "CargoPorCapacidadAlmac":TerminalAlmYTrans['Almacenamiento'].CargoPorCapacidadAlmac ,
                                        "CargoPorUsoAlmac":TerminalAlmYTrans['Almacenamiento'].CargoPorUsoAlmac ,
                                        "CargoVolumetricoAlmac":TerminalAlmYTrans['Almacenamiento'].CargoVolumetricoAlmac 
                                    },
                                    "Transporte":{
                                        "PermisoTransporte":TerminalAlmYTrans['Transporte'].PermisoTransporte,
                                        "ClaveDeVehiculo": TerminalAlmYTrans['Transporte'].ClaveDeVehiculo,
                                        "TarifaDeTransporte": TerminalAlmYTrans['Transporte'].TarifaDeTransporte ,
                                        "CargoPorCapacidadTrans":  TerminalAlmYTrans['Transporte'].CargoPorCapacidadTrans ,
                                        "CargoPorUsoTrans":  TerminalAlmYTrans['Transporte'].CargoPorUsoTrans,
                                        "CargoVolumetricoTrans": TerminalAlmYTrans['Transporte'].CargoVolumetricoTrans,
                                        "TarifaDeSuministro": TerminalAlmYTrans['Transporte'].TarfiaDeSuministro
                                    }
                        }
                        TerminalAlmYTrans_reporte = TerminalAlmYTrans_item
                        
                        Trasvase_reporte = []
                        for trasvase in complementos['TRASVASE']:
                            Trasvase_item = {
                                "NombreTrasvase":str( trasvase['TRASVASE'].NombreTrasvase),
                                "RfcTrasvase": str(trasvase['TRASVASE'].RfcTrasvase),
                                "PermisoTrasvase": str(trasvase['TRASVASE'].PermisoTrasvase),
                                "DescripcionTrasvase": str(trasvase['TRASVASE'].DescripcionTrasvase),
                                "CfdiTrasvase":str(trasvase['TRASVASE'].CfdiTrasvase)
                            }
                            Trasvase_reporte.append(Trasvase_item)

                        Dictamen_reporte = {}
                        Dictamen =complementos['DICTAMEN']
                        Dictamen_item={
                                "RfcDictamen":Dictamen['DICTAMEN'].RfcDictamen,
                                "LoteDictamen":str(Dictamen['DICTAMEN'].LoteDictamen),
                                "NumeroFolioDictamen":str(Dictamen['DICTAMEN'].NumeroFolioDictamen),
                                "FechaEmisionDictamen":str(Dictamen['DICTAMEN'].ResultadoDictamen),
                                "ResultadoDictamen":str(Dictamen['DICTAMEN'].ResultadoDictamen)
                        }
                        Dictamen_reporte=Dictamen_item

                        Certificado_reporte = {}
                        certificado = complementos['CERTIFICADO']
                        Certifiado_item={
                                "RfcCertificado":certificado['CERTIFICADO'].RfcCertificado,
                                "NumeroFolioCertificado":str(certificado['CERTIFICADO'].NumeroFolioCertificado),
                                "FechaEmisionCertificado":str(certificado['CERTIFICADO'].FechaEmisionCertificado),
                                "ResultadoCertificado":str(certificado['CERTIFICADO'].ResultadoCertificado)                          
                        }
                        Certificado_reporte=Certifiado_item

                        Nacional_reporte =[]
                        for nacional in complementos['NACIONAL']:
                            if  nacional['NACIONAL'] != None:
                                logging.debug("nacional")
                                logging.debug(nacional)
                                Nacional_item={
                                    "RfcClienteOProveedor":str(nacional['NACIONAL'].RFC),
                                    "NombreClienteOProveedor":str(nacional['NACIONAL'].Nombre_comercial),
                                    #cliente o proveedor
                                    **({ "PermisoClienteOProveedor": str(nacional['NACIONAL'].PermisoClienteOProveedor) } if nacional['NACIONAL'].PermisoClienteOProveedor is not None and nacional['NACIONAL'].PermisoClienteOProveedor != ''  else {}),
                                    "CFDIs":[{
                                        "Cfdi":cfdi.CFDI,
                                        "TipoCfdi":cfdi.TipoCFDI,
                                        "PrecioVentaOCompraOContrap":cfdi.PrecioVentaOCompraOContrap,
                                        "FechaYHoraTransaccion":str(cfdi.FechaYHoraTransaccion.astimezone().isoformat()),
                                        "VolumenDocumentado":{
                                            "ValorNumerico": cfdi.VolumenDocumentado ,
                                            "UnidadDeMedida":str(cfdi.VolumenDocumentado_UM)
                                        }
                                    } for cfdi in nacional['cfdis'] if cfdi != None]
                                }
                                Nacional_reporte.append(Nacional_item)

                        Extranjero_reporte = []
                        for extranjero in complementos['EXTRANJERO']:
                            Extranjero_item={ 
                                "PermisoImportacionOExportacion":str(extranjero['EXTRANJERO'].PermisoImportacionOExportacion),
                                "Pedimentos":[{
                                    "PuntoDeInternacionOExtraccion":str(pedimentos.PuntoDeInternacionOExtraccion),
                                    "PaisOrigenODestino":str(pedimentos.PaisOrigenODestino),
                                    "MedioDeTransEntraOSaleAduana":str(pedimentos.MedioDeTransEntraOSaleAducto),
                                    "PedimentoAduanal":str(pedimentos.PedimentosAduanal),
                                    "Incoterms":str(pedimentos.Incoterms),
                                    "PrecioDeImportacionOExportacion":pedimentos.PrecioDeImportacionOExportacion,
                                    "VolumenDocumentado":{
                                        "ValorNumerico": pedimentos.VolumenDocumentado,
                                        "UnidadDeMedida":str(pedimentos.VolumenDocumentado_UM)
                                    }
                                }for pedimentos in extranjero['pedimentos']]
                            }
                            Extranjero_reporte.append(Extranjero_item)
                            
                            aclaracion = complementos['ACLARACION']['ACLARACION']
                    Comp_Distribucion = {
                                "TipoComplemento": 'Distribucion',
                                #"TerminalAlmYTrans":TerminalAlmYTrans_reporte,
                                #"Trasvase":Trasvase_reporte,
                                #"Dictamen":Dictamen_reporte,
                                "Certificado":Certificado_reporte,
                                **({"Nacional": Nacional_reporte} if Nacional_reporte else {}),
                                #"Extranjero":Extranjero_reporte,
                                "Aclaracion":aclaracion
                    }
                    try:
                        # Validar el complemento contra el esquema
                        validate(instance=Comp_Distribucion, schema=estructura)
                        logging.debug("exito al validar")
                        return Comp_Distribucion  # Retorna el complemento válido
                    except ValidationError as e:
                        logging.debug("Error al validar complemento distribuidor:", e)
                        return None  # Retorna None o maneja el error de acuerdo a tus necesidades
        except ValueError as e:
            error_trace = traceback.format_exc()
            # Logging detallado
            logging.debug(f"ValueError: {str(e)}")
            logging.debug(f"Traceback: {error_trace}")
            return jsonify({'error': str(e)})



    """
    @classmethod 
    def Diario_Comp_Distribuidor_XML(cls):
        #schema_file = "src/static/schemes/distribuidor/complemento/diario/Comercializacion.xsd"
        schema_file = os.path.abspath(os.path.join(os.path.dirname(__file__),"..", "..", "..","static/schemes/distribuidor/complemento/diario/Distribucion.xsd"))
        schema = xmlschema.XMLSchema(schema_file)
        # Crear el elemento raíz
        complemento_distribuidor= etree.Element(
            '{https://repositorio.cloudb.sat.gob.mx/Covol/xml/Diarios/Distribucion.xsd}Distribucion'
        )
        terminal_alm_y_trans = etree.SubElement(complemento_distribuidor, 'TERMINALALMYTRANS')

        almacenamiento = etree.SubElement(terminal_alm_y_trans, 'Almacenamiento')
        etree.SubElement(almacenamiento, 'TerminalAlm').text = 'Terminal de almacenamiento Pájaros vinculada a ductos de petrolíferos a través de un conjunto de instalaciones de almacenamiento, ubicada en la Zona Industrial Coatzacoalcos'
        etree.SubElement(almacenamiento, 'PermisoAlmacenamiento').text = 'LP/12345/ALM/2015'
        etree.SubElement(almacenamiento, 'TarifaDeAlmacenamiento').text = str(58.69800)
        etree.SubElement(almacenamiento, 'CargoPorCapacidadAlmac').text = str(15.63100) 
        etree.SubElement(almacenamiento, 'CargoPorUsoAlmac').text = str(13.94600) 
        etree.SubElement(almacenamiento, 'CargoVolumetricoAlmac').text = str(29.12000) 

        transporte = etree.SubElement(terminal_alm_y_trans, 'Transporte')
        etree.SubElement(transporte, 'PermisoTransporte').text = 'PL/99990/TRA/DUC/2030'
        etree.SubElement(transporte, 'ClaveDeVehiculo').text = '456TRD'
        etree.SubElement(transporte, 'TarifaDeTransporte').text = str(4.46500) 
        etree.SubElement(transporte, 'CargoPorCapacidadTrans').text =str(0.99200)
        etree.SubElement(transporte, 'CargoPorUsoTrans').text = str(0.03600)
        etree.SubElement(transporte, 'CargoVolumetricoTrans').text = str(3.43700)
        etree.SubElement(transporte,'TarifaDeSuministro').text=str(23.32200) 

        trasvase = etree.SubElement(complemento_distribuidor, 'TRASVASE')
        trasvase_item = etree.SubElement(trasvase, 'TrasvaseItem')
        etree.SubElement(trasvase_item, 'NombreTrasvase').text = 'Servicios de Trasvase del Noreste, S.A. de C.V.'
        etree.SubElement(trasvase_item, 'RfcTrasvase').text = 'STN9506184R6'
        etree.SubElement(trasvase_item, 'PermisoTrasvase').text = 'SCT-DGDFM-111A/0001'
        etree.SubElement(trasvase_item, 'DescripcionTrasvase').text = 'Servicio de transbordo y trasvase de petrolíferos a través de ferrocarril, ubicado en Av. México 101.'
        etree.SubElement(trasvase_item, 'CfdiTrasvase').text = '123e4567-e89b-12d3-a456-426614174000'

        dictamen = etree.SubElement(complemento_distribuidor, 'DICTAMEN')
        etree.SubElement(dictamen, 'RfcDictamen').text = 'GEO9506184R6'
        etree.SubElement(dictamen, 'LoteDictamen').text = '435'
        etree.SubElement(dictamen, 'NumeroFolioDictamen').text = 'GEO9506184R6000232020'
        etree.SubElement(dictamen, 'FechaEmisionDictamen').text = '2020-10-31'
        etree.SubElement(dictamen, 'ResultadoDictamen').text = 'se aplicó el método de muestreo ISO 4257 al lote 435 y se determinó composición de propano en 60% y butano en 40%.'

        certificado = etree.SubElement(complemento_distribuidor, 'CERTIFICADO')
        etree.SubElement(certificado, 'RfcCertificado').text = 'EVA9612104R6'
        etree.SubElement(certificado, 'NumeroFolioCertificado').text = 'EVA9612104R6000232020'
        etree.SubElement(certificado, 'FechaEmisionCertificado').text = '2020-11-12'
        etree.SubElement(certificado, 'ResultadoCertificado').text = 'se acredita la correcta operación y funcionamiento de los equipos y programas informáticos para llevar controles volumétricos.'

        nacional = etree.SubElement(complemento_distribuidor, 'NACIONAL')
        cliente_o_proveedor = etree.SubElement(nacional, 'ClienteOProveedor')
        etree.SubElement(cliente_o_proveedor, 'RfcClienteOProveedor').text = 'CABL840215RF4'
        etree.SubElement(cliente_o_proveedor, 'NombreClienteOProveedor').text = 'Petromexico S.A. de C.V.'
        etree.SubElement(cliente_o_proveedor, 'PermisoClienteOProveedor').text = 'H/88888/COM/2021'
        cfdi = etree.SubElement(cliente_o_proveedor, 'CFDIs')
        cfdi_item = etree.SubElement(cfdi, 'CFDI')
        etree.SubElement(cfdi_item, 'TipoCFDI').text = 'Ingreso'
        etree.SubElement(cfdi_item, 'PrecioVentaOCompraOContrap').text =str(1380000.00000)
        etree.SubElement(cfdi_item, 'FechaYHoraTransaccion').text = '2020-10-31T11:59:45-0100'
        volumen_documentado = etree.SubElement(cfdi_item, 'VolumenDocumentado')
        etree.SubElement(volumen_documentado, 'ValorNumerico').text =str(20000.00000) 
        etree.SubElement(volumen_documentado, 'UM').text = 'UM03'

        extranjero = etree.SubElement(complemento_distribuidor, 'EXTRANJERO')
        importacion_o_exportacion = etree.SubElement(extranjero, 'ImportacionOExportacion')
        etree.SubElement(importacion_o_exportacion, 'PermisoImportacionOExportacion').text = '1234C123456789'
        pedimentos = etree.SubElement(importacion_o_exportacion, 'PEDIMENTOS')
        pedimento = etree.SubElement(pedimentos, 'Pedimento')
        etree.SubElement(pedimento, 'PuntoDeInternacionOExtraccion').text = '280'
        etree.SubElement(pedimento, 'PaisOrigenODestino').text = 'USA'
        etree.SubElement(pedimento, 'MedioDeTransEntraOSaleAduana').text = '3'
        etree.SubElement(pedimento, 'PedimentoAduanal').text = '20  28  3454  0123456'
        etree.SubElement(pedimento, 'Incoterms').text = 'DAT'
        etree.SubElement(pedimento, 'PrecioDeImportacionOExportacion').text = str(1000432.340)
        volumen_documentado_extranjero = etree.SubElement(pedimento, 'VolumenDocumentado')
        etree.SubElement(volumen_documentado_extranjero, 'ValorNumerico').text = str(1500000.000)
        etree.SubElement(volumen_documentado_extranjero, 'UM').text = 'UM03'
        # Aclaración
        etree.SubElement(complemento_distribuidor, 'ACLARACION').text = 'La inconsistencia en el volumen se debe a cambios de presión y temperatura dentro del tanque de almacenamiento TQS-ALM-0070, la lectura correcta de VolumenInicialTanque debería ser 14,000 litros, mismos que se entregaron.'

        # Convertir a string
        xml_string = etree.tostring(complemento_distribuidor, pretty_print=True, xml_declaration=True, encoding='UTF-8')
        # Validar el XML contra el esquema
        try:
            schema.validate(etree.fromstring(xml_string))
            print("El XML es válido.")
        except xmlschema.XMLSchemaValidationError as e:
            print(f"Error de validación: {e}")

        return xml_string




    @classmethod 
    def Mensual_Comp_Distribuidor_XML(cls):
        #schema_file = "src/static/schemes/distribuidor/complemento/mensual/Comercializacion.xsd"
        schema_file = os.path.abspath(os.path.join(os.path.dirname(__file__),"..", "..", "..","static/schemes/distribuidor/complemento/mensual/Distribucion.xsd"))
        schema = xmlschema.XMLSchema(schema_file)
        # Crear el elemento raíz
        complemento_distribuidor= etree.Element(
            '{https://repositorio.cloudb.sat.gob.mx/Covol/xml/Mensuales}Complemento_Distribucion'
        )
        terminal_alm_y_trans = etree.SubElement(complemento_distribuidor, 'TERMINALALMYTRANS')

        
        almacenamiento = etree.SubElement(terminal_alm_y_trans, 'Almacenamiento')
        etree.SubElement(almacenamiento, 'TerminalAlm').text = ''
        etree.SubElement(almacenamiento, 'PermisoAlmacenamiento').text = ''
        etree.SubElement(almacenamiento, 'TarifaDeAlmacenamiento').text = ''
        etree.SubElement(almacenamiento, 'CargoPorCapacidadAlmac').text = ''
        etree.SubElement(almacenamiento, 'CargoPorUsoAlmac').text = ''
        etree.SubElement(almacenamiento, 'CargoVolumetricoAlmac').text = ''

        transporte = etree.SubElement(terminal_alm_y_trans, 'Transporte')
        etree.SubElement(transporte, 'PermisoTransporte').text = ''
        etree.SubElement(transporte, 'ClaveDeVehiculo').text = ''
        etree.SubElement(transporte, 'TarifaDeTransporte').text = ''
        etree.SubElement(transporte, 'CargoPorCapacidadTrans').text = ''
        etree.SubElement(transporte, 'CargoPorUsoTrans').text = ''
        etree.SubElement(transporte, 'CargoVolumetricoTrans').text = ''
        etree.SubElement(transporte,'TarifaDeSuministro').text= ''

        trasvase = etree.SubElement(complemento_distribuidor, 'TRASVASE')
        trasvase_item = etree.SubElement(trasvase, 'TrasvaseItem')
        etree.SubElement(trasvase_item, 'NombreTrasvase').text = ''
        etree.SubElement(trasvase_item, 'RfcTrasvase').text = ''
        etree.SubElement(trasvase_item, 'PermisoTrasvase').text = ''
        etree.SubElement(trasvase_item, 'DescripcionTrasvase').text = ''
        etree.SubElement(trasvase_item, 'CfdiTrasvase').text = ''

        dictamen = etree.SubElement(complemento_distribuidor, 'DICTAMEN')
        etree.SubElement(dictamen, 'RfcDictamen').text = ''
        etree.SubElement(dictamen, 'LoteDictamen').text = ''
        etree.SubElement(dictamen, 'NumeroFolioDictamen').text = ''
        etree.SubElement(dictamen, 'FechaEmisionDictamen').text = ''
        etree.SubElement(dictamen, 'ResultadoDictamen').text = ''

        certificado = etree.SubElement(complemento_distribuidor, 'CERTIFICADO')
        etree.SubElement(certificado, 'RfcCertificado').text = ''
        etree.SubElement(certificado, 'NumeroFolioCertificado').text = ''
        etree.SubElement(certificado, 'FechaEmisionCertificado').text = ''
        etree.SubElement(certificado, 'ResultadoCertificado').text = ''

        nacional = etree.SubElement(complemento_distribuidor, 'NACIONAL')
        cliente_o_proveedor = etree.SubElement(nacional, 'ClienteOProveedor')
        etree.SubElement(cliente_o_proveedor, 'RfcClienteOProveedor').text = ''
        etree.SubElement(cliente_o_proveedor, 'NombreClienteOProveedor').text = ''
        etree.SubElement(cliente_o_proveedor, 'PermisoClienteOProveedor').text = ''
        cfdi = etree.SubElement(cliente_o_proveedor, 'CFDIs')
        cfdi_item = etree.SubElement(cfdi, 'CFDI')
        etree.SubElement(cfdi_item, 'TipoCFDI').text = ''
        etree.SubElement(cfdi_item, 'PrecioVentaOCompraOContrap').text = ''
        etree.SubElement(cfdi_item, 'FechaYHoraTransaccion').text = ''
        volumen_documentado = etree.SubElement(cfdi_item, 'VolumenDocumentado')
        etree.SubElement(volumen_documentado, 'ValorNumerico').text = ''
        etree.SubElement(volumen_documentado, 'UM').text = ''

        extranjero = etree.SubElement(complemento_distribuidor, 'EXTRANJERO')
        importacion_o_exportacion = etree.SubElement(extranjero, 'ImportacionOExportacion')
        etree.SubElement(importacion_o_exportacion, 'PermisoImportacionOExportacion').text = ''
        pedimentos = etree.SubElement(importacion_o_exportacion, 'PEDIMENTOS')
        pedimento = etree.SubElement(pedimentos, 'Pedimento')
        etree.SubElement(pedimento, 'PuntoDeInternacionOExtraccion').text = ''
        etree.SubElement(pedimento, 'PaisOrigenODestino').text = ''
        etree.SubElement(pedimento, 'MedioDeTransEntraOSaleAduana').text = ''
        etree.SubElement(pedimento, 'PedimentoAduanal').text = ''
        etree.SubElement(pedimento, 'Incoterms').text = ''
        etree.SubElement(pedimento, 'PrecioDeImportacionOExportacion').text = ''
        volumen_documentado_extranjero = etree.SubElement(pedimento, 'VolumenDocumentado')
        etree.SubElement(volumen_documentado_extranjero, 'ValorNumerico').text = ''
        etree.SubElement(volumen_documentado_extranjero, 'UM').text = ''
        # Aclaración
        etree.SubElement(complemento_distribuidor, 'ACLARACION').text = ''
        
        # Convertir a string
        xml_string = etree.tostring(complemento_distribuidor, pretty_print=True, xml_declaration=True, encoding='UTF-8')
        # Validar el XML contra el esquema
        try:
            schema.validate(etree.fromstring(xml_string))
            print("El XML es válido.")
        except xmlschema.exceptions.XMLSchemaValidationError as e:
            print(f"Error de validación: {e}")
        return xml_string

    """
