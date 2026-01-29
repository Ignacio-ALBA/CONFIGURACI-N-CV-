
# -*- coding: utf-8 -*-

import json

# Crear datos dummy
data = {
    'Header': [{
        'RFC Contribuyente': 'PIN960315R16',
        'RFC Representante Legal': 'PEPC930514UN7',
        'RFC Proveedor Sistema Informático': 'ADT161011FC2',
        'RFC Proveedor de Equipos': 'POPR790201696',
        'Clave Instalación': 'ACL-TRE-0045',
        'Descripción Instalación': 'Terminal de almacenamiento de gasolina con octanaje menor a 91 octanos, con una capacidad de 200000 litros.',
        'Dirección': 'Carr. a Zacatecas 450, Sauzalito, 78116 San Luis Potosí, S.L.P',
        'Longitud': 22.20138,
        'Latitud': -101.02329,
        'Número Pozos': 0,
        'Número Ducto Entrada/Salida': 2,
        'Número Dispensarios': 0,
        'Fecha y Hora del Corte': '2024-01-18 13:32:08'
    }],
    'Productos': [
        {'Clave de Producto': 'PR03 (Diésel)', 'Diésel con combustible No fósil': 'Sí'},
        {'Clave de Subproducto': 'SP00', 'Compos de combustible No fósil en Diésel': '10%'},
        {'Gasolina con combustible No fósil': 'Sí', 'Marca Comercial': 'Blue-ultrapower 5000', 'Concentración Sustancia Marcaje': '100 ppm'},
        {'Compos de combustile No fósil en Gasolina': '10%', 'Marcaje': 'Nitrógeno'}
    ],
    'Tanques': [{
        'Clave Identificación Tanques': 'TQS-TDA.0001',
        'Localización y Descripción del Tanque': 'Tanque de almacenamiento ubicado en la terminal PINSA',
        'Vigencia de Calibración del Tanque': '2026-01-18',
        'Capacidad Total de Tanque': {'Valor numérico': 1000000, 'UM': 'UM02'},
        'Capacidad Operativa Tanque': {'Valor numérico': 900000, 'UM': 'UM02'},
        'Capacidad Útil Tanque': {'Valor numérico': 1000000, 'UM': 'UM02'},
        'Capacidad Fondaje Tanque': {'Valor numérico': 700, 'UM': 'UM02'},
        'Volumen Mínimo Operativo': {'Valor numérico': 20, 'UM': 'UM03'},
        'Estado del Tanque': 'O'
    }],
    'Medición Tanque': [{
        'Sistema de Medición Tanque': 'SME-TQS-TDA-0001',
        'Localización, Descripción del sistema de medición del Tanque': 'Medidor de nivel MEDIMEX30000.',
        'Vigencia de la Calibración del sistema de Medición del Tanque': '2025-06-20',
        'Incertidumbre de la Medición del Sistema de Medición del Tanque': 0.010,
        'Volumen de la Existencia Anterior': {
            'Volumen natural': {'Valor numérico': 65.338, 'UM': 'UM03'},
            'Volumen Neto': {'Valor numérico': 65.253, 'UM': 'UM03'},
            'Fecha y Hora': '2024-01-04 23:59:39'
        },
        'Volumen Acumulado o pos Recepción': {
            'Volumen natural': {'Valor numérico': 62.010, 'UM': 'UM03'},
            'Volumen Neto': {'Valor numérico': 61.958, 'UM': 'UM03'},
            'Fecha y Hora': '2024-01-05 23:59:39'
        },
        'Volumen Acumulado o pos Entrega': {
            'Volumen natural': {'Valor numérico': 60.751, 'UM': 'UM03'},
            'Volumen Neto': {'Valor numérico': 60.702, 'UM': 'UM03'},
            'Fecha y Hora': '2024-01-05 22:59:20'
        },
        'Volumen final de la Existencia': {
            'Volumen natural': {'Valor numérico': 61.986, 'UM': 'UM03'},
            'Volumen Neto': {'Valor numérico': 61.965, 'UM': 'UM03'},
            'Fecha y Hora': '2024-01-05 23:59:44'
        }
    }],
    'Recepciones': [{
        'Total de la Recepciones': 4,
        'Suma de volúmenes de la recepción': {
            'Suma de las compras': '$190,455.00',
            'Total de Documentos': 2
        }
    }],
    'Entrega': [{
        'Total de la Entregas': 3,
        'Suma de volúmenes de la Entrega': {
            'Suma de las compras': '$100,455.00'
        }
    }],

    
    'Volumenes':[{
        'Fecha y hora de la Lectura':'2024-01-05 00:00:22',
        'Vol. Natural(m3)':  65.336   ,
        'Vol. Neto (m3)':  65.251  ,
        'Temp':  21.22 ,
        'UM': "UM02",

        '#Registro': None ,
        'Vol. Natural(m3)': None ,
        'Vol. Neto (m3)': None ,
        'Temp': None ,
        'UM': None  ,
        'Presión absoluta': None ,


        '#Registro': None ,
        'Vol. Natural(m3)': None,
        'Vol. Neto (m3)': None ,
        'Temp': None ,
        'UM': None ,
        'Presión absoluta': None 
    },
    {
        'Fecha y hora de la Lectura':'2024-01-05 14:00:09',
        'Vol. Natural(m3)':  65.329  ,
        'Vol. Neto (m3)':  65.304  ,
        'Temp': 20.47  ,
        'UM': "UM02" ,

        '#Registro': None ,
        'Vol. Natural(m3)': None ,
        'Vol. Neto (m3)': None ,
        'Temp': None  ,
        'UM': None  ,
        'Presión absoluta': None ,


        '#Registro': None ,
        'Vol. Natural(m3)': None,
        'Vol. Neto (m3)': None ,
        'Temp': None ,
        'UM': None ,
        'Presión absoluta': None 
    },
    {
        'Fecha y hora de la Lectura': '2024-01-05 14:22:00',
        'Vol. Natural(m3)': None  ,
        'Vol. Neto (m3)': None  ,
        'Temp': None,
        'UM':None ,

        '#Registro': None ,
        'Vol. Natural(m3)': None ,
        'Vol. Neto (m3)': None ,
        'Temp': None  ,
        'UM': None  ,
        'Presión absoluta':None  ,


        '#Registro': ' 001 ' ,
        'Vol. Natural(m3)':  19.998 ,
        'Vol. Neto (m3)':  20.016   ,
        'Temp': 18.9  ,
        'UM': 'UM02'  ,
        'Presión absoluta':  101.325 
    },
    {
        'Fecha y hora de la Lectura':'2024-01-05 14:40:00',
        'Vol. Natural(m3)':45.331  ,
        'Vol. Neto (m3)': 45.288 ,
        'Temp': 20.47,
        'UM': 'UM02' ,

        '#Registro': None ,
        'Vol. Natural(m3)':None  ,
        'Vol. Neto (m3)':None  ,
        'Temp':None  ,
        'UM': None  ,
        'Presión absoluta': None ,


        '#Registro':None ,
        'Vol. Natural(m3)':None ,
        'Vol. Neto (m3)':None  ,
        'Temp': None ,
        'UM': None ,
        'Presión absoluta':None  
    },
    {
        'Fecha y hora de la Lectura': '2024-01-05 14:45:00',
        'Vol. Natural(m3)':45.331   ,
        'Vol. Neto (m3)':45.288 ,
        'Temp': 20.47,
        'UM': 'UM02',

        '#Registro': None ,
        'Vol. Natural(m3)': None ,
        'Vol. Neto (m3)':None  ,
        'Temp':None  ,
        'UM':  None ,
        'Presión absoluta': None,


        '#Registro': None ,
        'Vol. Natural(m3)':None ,
        'Vol. Neto (m3)': None ,
        'Temp':None  ,
        'UM':None  ,
        'Presión absoluta': None 
    },
    {
        'Fecha y hora de la Lectura': '2024-01-05 14:49:00',
        'Vol. Natural(m3)': None ,
        'Vol. Neto (m3)':None  ,
        'Temp': None,
        'UM':None ,

        '#Registro': None ,
        'Vol. Natural(m3)': None,
        'Vol. Neto (m3)': None ,
        'Temp': None ,
        'UM':  None ,
        'Presión absoluta': None ,


        '#Registro': '002'  ,
        'Vol. Natural(m3)': 0.698,
        'Vol. Neto (m3)': 0.697 ,
        'Temp': 22.1 ,
        'UM': 'UM02' ,
        'Presión absoluta': 101.325 
    },
    {
        'Fecha y hora de la Lectura':'2024-01-05  14:58:00',
        'Vol. Natural(m3)':44.633  ,
        'Vol. Neto (m3)':44.591  ,
        'Temp':21.22 ,
        'UM': 'UM02',

        '#Registro':  None,
        'Vol. Natural(m3)':None  ,
        'Vol. Neto (m3)': None ,
        'Temp': None ,
        'UM': None  ,
        'Presión absoluta': None ,


        '#Registro': None ,
        'Vol. Natural(m3)':None ,
        'Vol. Neto (m3)':None  ,
        'Temp': None ,
        'UM': None ,
        'Presión absoluta': None 
    },
    {
        'Fecha y hora de la Lectura': '2024-01-05 15:00:01 ',
        'Vol. Natural(m3)': 44.633 ,
        'Vol. Neto (m3)': 44.591 ,
        'Temp':20.69,
        'UM':'UM02' ,

        '#Registro': None ,
        'Vol. Natural(m3)': None ,
        'Vol. Neto (m3)': None ,
        'Temp':None  ,
        'UM':None   ,
        'Presión absoluta': None ,


        '#Registro': None ,
        'Vol. Natural(m3)':None ,
        'Vol. Neto (m3)':None  ,
        'Temp':None  ,
        'UM': None,
        'Presión absoluta': None 
    },
    {
        'Fecha y hora de la Lectura': '2024-01-05 15:35:00',
        'Vol. Natural(m3)': None ,
        'Vol. Neto (m3)':  None,
        'Temp': None,
        'UM': None ,

        '#Registro':'003'  ,
        'Vol. Natural(m3)': '40,082'  ,
        'Vol. Neto (m3)': '40,075' ,
        'Temp': 20.2 ,
        'UM':  'UM02' ,
        'Presión absoluta': 101.325 ,


        '#Registro': None ,
        'Vol. Natural(m3)':None ,
        'Vol. Neto (m3)': None ,
        'Temp':None  ,
        'UM': None ,
        'Presión absoluta': None 
    },
    {
        'Fecha y hora de la Lectura':'2024-01-05 15:51:00',
        'Vol. Natural(m3)':84.715  ,
        'Vol. Neto (m3)':84.666  ,
        'Temp':20.80 ,
        'UM': 'UM02' ,

        '#Registro': None ,
        'Vol. Natural(m3)':None  ,
        'Vol. Neto (m3)':None  ,
        'Temp':None  ,
        'UM': None  ,
        'Presión absoluta': None ,


        '#Registro': None ,
        'Vol. Natural(m3)':None ,
        'Vol. Neto (m3)': None ,
        'Temp': None ,
        'UM': None ,
        'Presión absoluta': None 
    },
    {
        'Fecha y hora de la Lectura':'2024-01-05 17:04:44',
        'Vol. Natural(m3)': 84.715 ,
        'Vol. Neto (m3)':84.666  ,
        'Temp':20.92 ,
        'UM': 'UM02' ,

        '#Registro': None ,
        'Vol. Natural(m3)': None ,
        'Vol. Neto (m3)':  None,
        'Temp': None  ,
        'UM':  None ,
        'Presión absoluta':None  ,


        '#Registro':None  ,
        'Vol. Natural(m3)':None ,
        'Vol. Neto (m3)':None  ,
        'Temp':None  ,
        'UM': None ,
        'Presión absoluta': None 
    },
    {
        'Fecha y hora de la Lectura': '2024-01-05 17:50:00',
        'Vol. Natural(m3)': None ,
        'Vol. Neto (m3)':None  ,
        'Temp':None ,
        'UM': None,

        '#Registro':None  ,
        'Vol. Natural(m3)': None ,
        'Vol. Neto (m3)':None  ,
        'Temp': None ,
        'UM': None  ,
        'Presión absoluta': None ,


        '#Registro': '004' ,
        'Vol. Natural(m3)':4.998 ,
        'Vol. Neto (m3)':4.996 ,
        'Temp':20.6  ,
        'UM': 'UM02' ,
        'Presión absoluta': 101.325 
    },
    {
        'Fecha y hora de la Lectura':'2024-01-05 17:59:28',
        'Vol. Natural(m3)':79.717  ,
        'Vol. Neto (m3)': 79.670 ,
        'Temp': 20.99,
        'UM': 'UM02',

        '#Registro': None ,
        'Vol. Natural(m3)': None ,
        'Vol. Neto (m3)':None  ,
        'Temp':None  ,
        'UM':  None ,
        'Presión absoluta':None  ,


        '#Registro': None ,
        'Vol. Natural(m3)':None ,
        'Vol. Neto (m3)': None ,
        'Temp':None  ,
        'UM': None ,
        'Presión absoluta': None 
    },
    {
        'Fecha y hora de la Lectura': '2024-01-05 18:00:11',
        'Vol. Natural(m3)': 79.717  ,
        'Vol. Neto (m3)':79.670  ,
        'Temp':21.00 ,
        'UM':'UM02' ,

        '#Registro': None ,
        'Vol. Natural(m3)': None ,
        'Vol. Neto (m3)':None  ,
        'Temp':  None,
        'UM': None  ,
        'Presión absoluta':None  ,


        '#Registro':None  ,
        'Vol. Natural(m3)':None,
        'Vol. Neto (m3)': None ,
        'Temp': None ,
        'UM':None  ,
        'Presión absoluta':None  
    },
    {
        'Fecha y hora de la Lectura': '2024-01-05 18:38:00',
        'Vol. Natural(m3)':None  ,
        'Vol. Neto (m3)': None ,
        'Temp':None ,
        'UM':None ,

        '#Registro': '005'  ,
        'Vol. Natural(m3)': 42.215 ,
        'Vol. Neto (m3)': 42.177 ,
        'Temp':21.1  ,
        'UM': 'UM02'  ,
        'Presión absoluta': 101.325 ,


        '#Registro': None ,
        'Vol. Natural(m3)':None ,
        'Vol. Neto (m3)': None ,
        'Temp': None  ,
        'UM': None  ,
        'Presión absoluta': None 
    },
     {
        'Fecha y hora de la Lectura': '2024-01-05 18:59:47' ,
        'Vol. Natural(m3)': 121.932  ,
        'Vol. Neto (m3)': 121.847  ,
        'Temp': 21.07 ,
        'UM':  'UM02' ,

        '#Registro': None  ,
        'Vol. Natural(m3)':None  ,
        'Vol. Neto (m3)': None  ,
        'Temp': None  ,
        'UM':  None  ,
        'Presión absoluta': None  ,


        '#Registro':None    ,
        'Vol. Natural(m3)': None ,
        'Vol. Neto (m3)': None ,
        'Temp':None  ,
        'UM': None ,
        'Presión absoluta': None 
    },
   
     {
        'Fecha y hora de la Lectura': '2024-01-05 20:00:46' ,
        'Vol. Natural(m3)': 121.932  ,
        'Vol. Neto (m3)': 121.847  ,
        'Temp': 21.18,
        'UM': 'UM02'  ,

        '#Registro': None  ,
        'Vol. Natural(m3)':None  ,
        'Vol. Neto (m3)':None   ,
        'Temp':None   ,
        'UM':  None  ,
        'Presión absoluta': None  ,


        '#Registro': None   ,
        'Vol. Natural(m3)':None  ,
        'Vol. Neto (m3)':None  ,
        'Temp': None ,
        'UM':  None,
        'Presión absoluta':None  
    },
     {
        'Fecha y hora de la Lectura': '2024-01-05 20:07:00' ,
        'Vol. Natural(m3)':None   ,
        'Vol. Neto (m3)':  None ,
        'Temp':None,
        'UM':  None ,

        '#Registro':  '006' ,
        'Vol. Natural(m3)': 49.970 ,
        'Vol. Neto (m3)': 49.912  ,
        'Temp':  21.4 ,
        'UM':  'UM02'  ,
        'Presión absoluta': 101.325  ,


        '#Registro': None   ,
        'Vol. Natural(m3)': None ,
        'Vol. Neto (m3)': None ,
        'Temp': None ,
        'UM': None ,
        'Presión absoluta':  None
    },
     {
        'Fecha y hora de la Lectura':'2024-01-05 20:20:00'  ,
        'Vol. Natural(m3)': 171.902  ,
        'Vol. Neto (m3)':171.759   ,
        'Temp':21.18,
        'UM':  'UM02' ,

        '#Registro': None   ,
        'Vol. Natural(m3)': None ,
        'Vol. Neto (m3)': None  ,
        'Temp': None  ,
        'UM': None   ,
        'Presión absoluta': None  ,


        '#Registro': None   ,
        'Vol. Natural(m3)':None  ,
        'Vol. Neto (m3)': None ,
        'Temp': None ,
        'UM':None  ,
        'Presión absoluta': None 
    },
     {
        'Fecha y hora de la Lectura': '2024-01-05 20:23:34' ,
        'Vol. Natural(m3)': 171.902  ,
        'Vol. Neto (m3)':171.759   ,
        'Temp': 21.18,
        'UM': 'UM02'  ,

        '#Registro':  None ,
        'Vol. Natural(m3)':None  ,
        'Vol. Neto (m3)': None  ,
        'Temp': None  ,
        'UM':  None  ,
        'Presión absoluta': None  ,


        '#Registro': None   ,
        'Vol. Natural(m3)': None ,
        'Vol. Neto (m3)': None ,
        'Temp': None ,
        'UM': None ,
        'Presión absoluta': None 
    },
     {
        'Fecha y hora de la Lectura': '2024-01-05  20:27:00' ,
        'Vol. Natural(m3)':  None ,
        'Vol. Neto (m3)': None  ,
        'Temp':None,
        'UM':  None ,

        '#Registro':  '007' ,
        'Vol. Natural(m3)': 9.977 ,
        'Vol. Neto (m3)': 9.963  ,
        'Temp': 21.7  ,
        'UM':  'UM02'  ,
        'Presión absoluta': 101.325  ,


        '#Registro': None   ,
        'Vol. Natural(m3)':None  ,
        'Vol. Neto (m3)': None ,
        'Temp':None  ,
        'UM': None ,
        'Presión absoluta': None 
    },
     {
        'Fecha y hora de la Lectura':'2024-01-05 20:59:00',
        'Vol. Natural(m3)':181.879   ,
        'Vol. Neto (m3)': 181.736  ,
        'Temp':22.20,
        'UM': 'UM02'  ,

        '#Registro':None   ,
        'Vol. Natural(m3)': None ,
        'Vol. Neto (m3)': None  ,
        'Temp':None  ,
        'UM': None   ,
        'Presión absoluta':None   ,


        '#Registro':  None  ,
        'Vol. Natural(m3)': None ,
        'Vol. Neto (m3)': None,
        'Temp':None  ,
        'UM': None ,
        'Presión absoluta': None 
    },
     {
        'Fecha y hora de la Lectura':'2024-01-05 23:59:44',
        'Vol. Natural(m3)': 181.879  ,
        'Vol. Neto (m3)': 181.736  ,
        'Temp': 20.40,
        'UM': 'UM02'  ,

        '#Registro':  None ,
        'Vol. Natural(m3)':None  ,
        'Vol. Neto (m3)': None  ,
        'Temp': None  ,
        'UM':None    ,
        'Presión absoluta':None   ,


        '#Registro': None   ,
        'Vol. Natural(m3)': None ,
        'Vol. Neto (m3)':None  ,
        'Temp': None ,
        'UM': None ,
        'Presión absoluta': None 
    }
    ],
    'Volumen Inicial':[{
        'Vol. Natural m3': 65.336,
        'Vol. Neto m3': 65.251,
        'UM': 'UM02' ,
        'Temp Promedio': 21.22
    }],
    'Recepción (descargas)':[{
       'Vol. Natural m3': 142.244 ,
        'Vol. Neto m3':142.127 ,
        'UM': 'UM02' ,
        'Temp Promedio': 21.7 

    }],
    'Entrega (cargas) ':[{
       'Vol. Natural m3': 25.694  ,
        'Vol. Neto m3':25.709 ,
        'UM': 'UM02' ,
        'Temp Promedio':20.6
    }],
    'Volumen Existencias ':[{
       'Vol. Natural m3': 201.886 ,
        'Vol. Neto m3':201.669 ,
        'UM': 'UM02' ,
        'Temp Promedio':'----'
    }],    
    'Volumen Final  ':[{
       'Vol. Natural m3': 181.879 ,
        'Vol. Neto m3':181.736 ,
        'UM': 'UM02' ,
        'Temp Promedio':20.40
    }],    
    'Diferencia ':[{
       'Vol. Natural m3': -20.007 ,
        'Vol. Neto m3':-19.933 ,
        'UM': 'UM02' ,
        'Temp Promedio':'----'
    }], 
    'Ductos': [{
        'Clave de Identificación del Ducto:': 'DUC-DES-004',
        'Descripción del Ducto': 'Ducto de descarga del autotanque de clave TQS-ATQ-1234 de distribución de petrolíferos.',
        'Sistema de Medición del Ducto':'SMD-DUC-DES-004' ,
        'Vigencia de la Calibración del Sistema de Medición del Ducto': '2018-06-30' ,
        'Incertidumbre de Medición del Sistema de Medición del Ducto': '0.9%',

        'Diámetro del Ducto': '3 pulgadas' ,
        'Descripción del sistema de Medición del Ducto': 'Medidor dinámico Marca DuctMex',


        'Total de Recepciones':2 ,
        'Suma del volumen de la Recepción':'70,000',
         'UM': 'UM04',
        'Total de Documentos':2
        }],
}

# Convertir a JSON
json_data = json.dumps(data, indent=2)
print(json_data)

# Nombre del archivo de texto
nombre_archivo = 'JSON.txt'

# Abrir el archivo en modo escritura
with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
    # Escribir el JSON en el archivo
    json.dump(data, archivo, ensure_ascii=False, indent=2)

print(f'Se ha guardado el JSON en {nombre_archivo}')