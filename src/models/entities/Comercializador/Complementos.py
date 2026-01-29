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


class Comp_Comercializador():

    @classmethod
    def load_json_structure(cls,file_path):
        """Lee la estructura JSON desde un archivo con codificación UTF-8."""
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    @classmethod
    def Comp_Comercializacion_schema_json(cls,id_complemento,tipo,tipo_operacion,operacion,recepcion_entrega):
        try:
            complemendo_com = os.path.abspath(os.path.join(os.path.dirname(__file__),"..", "..", "..","static/schemes/comercializador/complemento/Comp-Comercializacion.schema.json"))
            estructura = cls.load_json_structure(complemendo_com)
            DailyReportFuntionsInstance = DailyReportFuntions(1)
            print("Complemento_comercializador")

            complementos_date = DailyReportFuntionsInstance.GetComplementDailyReportAll(id_complemento,tipo,tipo_operacion,operacion,recepcion_entrega)
            if complementos_date:
                    for complementos in complementos_date:

                        TerminalAlmyDist_reporte = {}
                        TermianlAlmyDist = complementos['TERMINALALMYTRANS_TERMINALALMYDIST']
                        TerminalAlmyDist = {
                            "Almacenamiento":{
                                "TerminalAlmYDist": TermianlAlmyDist['Almacenamiento'].TerminalAlm ,
                                "PermisoAlmYDist":TermianlAlmyDist['Almacenamiento'].PermisoAlmacenamiento ,
                                "TarifaDeAlmacenamiento":TermianlAlmyDist['Almacenamiento'].TarifaDeAlmacenamiento,
                                "CargoPorCapacidadAlmac":TermianlAlmyDist['Almacenamiento'].CargoPorCapacidadAlmac ,
                                "CargoPorUsoAlmac": TermianlAlmyDist['Almacenamiento'].CargoPorUsoAlmac ,
                                "CargoVolumetricoAlmac": TermianlAlmyDist['Almacenamiento'].CargoVolumetricoAlmac 
                            },
                            "Transporte":{
                                "PermisoTransporte":TermianlAlmyDist['Transporte'].PermisoTransporte,
                                "ClaveDeVehiculo": TermianlAlmyDist['Transporte'].ClaveDeVehiculo,
                                "TarifaDeTransporte":TermianlAlmyDist['Transporte'].TarifaDeTransporte ,
                                "CargoPorCapacidadTrans":  TermianlAlmyDist['Transporte'].CargoPorCapacidadTrans ,
                                "CargoPorUsoTrans": TermianlAlmyDist['Transporte'].CargoPorUsoTrans,
                                "CargoVolumetricoTrans": TermianlAlmyDist['Transporte'].CargoVolumetricoTrans,
                                        "TarifaDeSuministro": TermianlAlmyDist['Transporte'].TarfiaDeSuministro
                            }
                        }
                        TerminalAlmyDist_reporte = TerminalAlmyDist

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
                        logging.debug("complementos['NACIONAL']")
                        logging.debug(complementos['NACIONAL'])
                        for nacional in complementos['NACIONAL']:
                            logging.debug(nacional)
                            logging.debug(nacional['cfdis'])
                            logging.debug(nacional['NACIONAL'])
                            if nacional['cfdis'] != None and nacional['NACIONAL'] != None:
                                if  nacional['NACIONAL'] != None:
                                    Nacional_item={
                                        "RfcClienteOProveedor":str(nacional['NACIONAL'].RFC),
                                        "NombreClienteOProveedor":str(nacional['NACIONAL'].Nombre_comercial),
                                        #Camnbio de PermisoClienteOProveedor a PermisoClienteOProveedor
                                        **({ "PermisoClienteOProveedor": str(nacional['NACIONAL'].PermisoClienteOProveedor) } if nacional['NACIONAL'].PermisoClienteOProveedor is not None and nacional['NACIONAL'].PermisoClienteOProveedor != '' else {}),
                                        "CFDIs":[{
                                            "Cfdi":cfdi.CFDI,
                                            "TipoCfdi":cfdi.TipoCFDI,
                                            "PrecioVentaOCompraOContrap":cfdi.PrecioVentaOCompraOContrap,
                                            "FechaYHoraTransaccion":str(cfdi.FechaYHoraTransaccion.astimezone().isoformat()),
                                            "VolumenDocumentado":{
                                                "ValorNumerico": cfdi.VolumenDocumentado ,
                                                "UnidadDeMedida":str(cfdi.VolumenDocumentado_UM)
                                            }
                                        }for cfdi in nacional['cfdis'] if cfdi != None]
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
                    Comp_Comercializacion = {
                                "TipoComplemento": 'Comercializacion',
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
                        validate(instance=Comp_Comercializacion, schema=estructura)
                        logging.debug("exito al validar")
                        return Comp_Comercializacion  # Retorna el complemento válido
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
    def Diario_Comp_Comercializacion_XML(cls):
        schema_file = "src/static/schemes/comercializador/complemento/diario/Comercializacion.xsd"
        schema = xmlschema.XMLSchema(schema_file)

        # Crear el elemento raíz
        complemento_comercializacion = etree.Element(
            '{https://repositorio.cloudb.sat.gob.mx/Covol/xml/Diarios}Complemento_Comercializacion'
        )

        # Agregar TERMINALALMYDIST
        terminal_alm_y_dist = etree.SubElement(complemento_comercializacion, 'TERMINALALMYDIST')

        # Almacenamiento
        almacenamiento = etree.SubElement(terminal_alm_y_dist, 'Almacenamiento')
        etree.SubElement(almacenamiento, 'TerminalAlmYDist').text = ''
        etree.SubElement(almacenamiento, 'PermisoAlmYDist').text = ''
        etree.SubElement(almacenamiento, 'TarifaDeAlmacenamiento').text = ''
        etree.SubElement(almacenamiento, 'CargoPorCapacidadAlmac').text = ''
        etree.SubElement(almacenamiento, 'CargoPorUsoAlmac').text = ''
        etree.SubElement(almacenamiento, 'CargoVolumetricoAlmac').text = ''

        # Transporte
        transporte = etree.SubElement(terminal_alm_y_dist, 'Transporte')
        etree.SubElement(transporte, 'PermisoTransporte').text = ''
        etree.SubElement(transporte, 'ClaveDeVehiculo').text = ''
        etree.SubElement(transporte, 'TarifaDeTransporte').text = ''
        etree.SubElement(transporte, 'CargoPorCapacidadTrans').text = ''
        etree.SubElement(transporte, 'CargoPorUsoTrans').text = ''
        etree.SubElement(transporte, 'CargoVolumetricoTrans').text = ''

        # Trasvase
        trasvase = etree.SubElement(complemento_comercializacion, 'TRASVASE')
        trasvase_item = etree.SubElement(trasvase, 'TrasvaseItem')
        etree.SubElement(trasvase_item, 'NombreTrasvase').text = ''
        etree.SubElement(trasvase_item, 'RfcTrasvase').text = ''
        etree.SubElement(trasvase_item, 'PermisoTrasvase').text = ''
        etree.SubElement(trasvase_item, 'DescripcionTrasvase').text = ''
        etree.SubElement(trasvase_item, 'CfdiTrasvase').text = ''

        # Dictamen
        dictamen = etree.SubElement(complemento_comercializacion, 'DICTAMEN')
        etree.SubElement(dictamen, 'RfcDictamen').text = ''
        etree.SubElement(dictamen, 'LoteDictamen').text = ''
        etree.SubElement(dictamen, 'NumeroFolioDictamen').text = ''
        etree.SubElement(dictamen, 'FechaEmisionDictamen').text = ''
        etree.SubElement(dictamen, 'ResultadoDictamen').text = ''

        # Certificado
        certificado = etree.SubElement(complemento_comercializacion, 'CERTIFICADO')
        etree.SubElement(certificado, 'RfcCertificado').text = ''
        etree.SubElement(certificado, 'NumeroFolioCertificado').text = ''
        etree.SubElement(certificado, 'FechaEmisionCertificado').text = ''
        etree.SubElement(certificado, 'ResultadoCertificado').text = ''

        # Nacional
        nacional = etree.SubElement(complemento_comercializacion, 'NACIONAL')
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

        # Extranjero
        extranjero = etree.SubElement(complemento_comercializacion, 'EXTRANJERO')
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
        etree.SubElement(complemento_comercializacion, 'ACLARACION').text = ''
        # Convertir a string
        xml_string = etree.tostring(complemento_comercializacion, pretty_print=True, xml_declaration=True, encoding='UTF-8')
        # Validar el XML contra el esquema
        try:
            schema.validate(etree.fromstring(xml_string))
            print("El XML es válido.")
        except xmlschema.exceptions.XMLSchemaValidationError as e:
            print(f"Error de validación: {e}")
        return xml_string
        
    @classmethod
    def Mensual_Comp_Comercializacion_XML(cls):
        schema_file = "src/static/schemes/comercializador/complemento/mensual/Comercializacion.xsd"
        schema = xmlschema.XMLSchema(schema_file)

        # Crear el elemento raíz con el namespace correcto
        complemento_comercializacion = etree.Element(
            '{https://repositorio.cloudb.sat.gob.mx/Covol/xml/Mensuales}Complemento_Comercializacion'
        )

        terminal_alm_y_dist = etree.SubElement(complemento_comercializacion, 'TERMINALALMYDIST')

        # Almacenamiento
        almacenamiento = etree.SubElement(terminal_alm_y_dist, 'Almacenamiento')
        etree.SubElement(almacenamiento, 'TerminalAlmYDist').text = ''
        etree.SubElement(almacenamiento, 'PermisoAlmYDist').text = ''
        etree.SubElement(almacenamiento, 'TarifaDeAlmacenamiento').text = ''
        etree.SubElement(almacenamiento, 'CargoPorCapacidadAlmac').text = ''
        etree.SubElement(almacenamiento, 'CargoPorUsoAlmac').text = ''
        etree.SubElement(almacenamiento, 'CargoVolumetricoAlmac').text = ''

        # Transporte
        transporte = etree.SubElement(terminal_alm_y_dist, 'Transporte')
        etree.SubElement(transporte, 'PermisoTransporte').text = ''
        etree.SubElement(transporte, 'ClaveDeVehiculo').text = ''
        etree.SubElement(transporte, 'TarifaDeTransporte').text = ''
        etree.SubElement(transporte, 'CargoPorCapacidadTrans').text = ''
        etree.SubElement(transporte, 'CargoPorUsoTrans').text = ''
        etree.SubElement(transporte, 'CargoVolumetricoTrans').text = ''

        # Trasvase
        trasvase = etree.SubElement(complemento_comercializacion, 'TRASVASE')
        trasvase_item = etree.SubElement(trasvase, 'TrasvaseItem')
        etree.SubElement(trasvase_item, 'NombreTrasvase').text = ''
        etree.SubElement(trasvase_item, 'RfcTrasvase').text = ''
        etree.SubElement(trasvase_item, 'PermisoTrasvase').text = ''
        etree.SubElement(trasvase_item, 'DescripcionTrasvase').text = ''
        etree.SubElement(trasvase_item, 'CfdiTrasvase').text = ''

        # Dictamen
        dictamen = etree.SubElement(complemento_comercializacion, 'DICTAMEN')
        etree.SubElement(dictamen, 'RfcDictamen').text = ''
        etree.SubElement(dictamen, 'LoteDictamen').text = ''
        etree.SubElement(dictamen, 'NumeroFolioDictamen').text = ''
        etree.SubElement(dictamen, 'FechaEmisionDictamen').text = ''
        etree.SubElement(dictamen, 'ResultadoDictamen').text = ''


        # Certificado
        certificado = etree.SubElement(complemento_comercializacion, 'CERTIFICADO')
        etree.SubElement(certificado, 'RfcCertificado').text = ''
        etree.SubElement(certificado, 'NumeroFolioCertificado').text = ''
        etree.SubElement(certificado, 'FechaEmisionCertificado').text = ''
        etree.SubElement(certificado, 'ResultadoCertificado').text = ''


        # Nacional
        nacional = etree.SubElement(complemento_comercializacion, 'NACIONAL')
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

        # Extranjero
        extranjero = etree.SubElement(complemento_comercializacion, 'EXTRANJERO')
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
        etree.SubElement(complemento_comercializacion, 'ACLARACION').text = ''
        # Convertir a string
        xml_string = etree.tostring(complemento_comercializacion, pretty_print=True, xml_declaration=True, encoding='UTF-8')
        # Validar el XML contra el esquema
        try:
            schema.validate(etree.fromstring(xml_string))
            print("El XML es válido.")
        except xmlschema.exceptions.XMLSchemaValidationError as e:
            print(f"Error de validación: {e}")
        return xml_string

        """