from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from itertools import zip_longest

from reportlab.platypus import Table, TableStyle
import datetime

def crear_tabla(c, x_position, y_position):
        data = [
            ['Volumen Inicial del Tanque','','','','',
             'Volumen Recepción / Descargas (Recibido)','','','','','','Volumen Entrega / Cargas (Salidas)','','','','',''],
            ['Fecha y hora \nde la Lectura', 'Vol.\nNatural(m3)', 'Vol.\nNeto(m3)','Temp','UM','#Registro','Vol.\nNatural(m3)','Vol.\nNeto(m3)','Temp','UM','Presión \nAbsoluta','#Registro','Vol.\nNatural(m3)','Vol.\nNeto(m3)','Temp','UM','Presión \nAbsoluta'],
            
 
        ]
        nuevos_datos = [
            ["2024-01-05 00:00:22", "65.336", "65.251", "21.22", "UM02", "", "", "", "", "", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""],

            # Agrega más filas si es necesario
        ]

        # Añadir los nuevos datos a la tabla existente
        data.extend(nuevos_datos)
        
        total  = [
              ["", "", "", "", "", "", "", "", "", "", "", "", "Vol.\nNatural(m3)", "Vol.\nNeto(m3)", "UM", "Temp \nPromedio", ""],
              ["", "", "", "", "", "", "", "", "", "", "","Volumen Inicial",  "", "", "", "", ""],
              ["", "", "", "", "", "", "", "", "", "", "","Recepción \n(descargas)","", "", "", "", ""],
              ["", "", "", "", "", "", "", "", "", "", "","Entrega (cargas)", "","", "", "", ""],
              ["", "", "", "", "", "", "", "", "", "", "","Volumen Existencias", "","", "", "---", ""],
              ["", "", "", "", "", "", "", "", "", "", "","Volumen Final","", "", "", "", ""],
              ["", "", "", "", "", "", "", "", "", "", "","Diferencia", "","", "", "---", ""]
 
        ]
        data.extend(total)
 
        table = Table(data)
 
        style = TableStyle([
                ('BACKGROUND', (0, 1), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white ),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                # Configuración de fondo y combinaciones de celdas
                ('BACKGROUND', (0, 0), (4, 0), (255/255, 222/255, 227/255)),# Pink
                ('SPAN', (0, 0), (4, 0)),
                ('BACKGROUND', (5, 0), (10, 0), (133/255, 255/255, 133/255)),#green
                ('SPAN', (5, 0), (10, 0)),
                ('BACKGROUND', (11, 0), (16, 0), (155/255, 155/255, 252/255)),#blue
                ('SPAN', (11, 0), (16, 0)),
            ])
        table.setStyle(style)
            
            # Configurar anchos de columna
        col_widths = [80, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40]
        table._argW = col_widths
            
            # Obtener ancho y altura de la página
        width, height = letter

            # Dibujar la tabla en la posición dada
        table.wrapOn(c, width, height)
        table.drawOn(c, x_position, y_position)

def add_header(c, width, height):
     # Añade un encabezado horizontal
    c.setLineWidth(1)
    c.setStrokeColor(colors.black)
    # c.line(20, height - 20, width - 20, height - 20)  # Dibuja una línea horizontal en la parte superior de la página

    image_path = 'logo.png'
    # Ajusta la posición (x, y) y el tamaño (width, height) de la imagen según sea necesario
    c.drawImage(image_path, x=50, y=height - 50, width=200, height=30)  
    print("Hola")
    header_text = "Versión del sistema 4.0.20"
    c.setFont("Helvetica-Bold", 7)
    c.drawString(660, height - 45, header_text)

    #Izquierda
    c.drawString(50, height - 65, "RFC Contribuyente:")
    c.drawString(50, height - 75, "RFC Representante Legal:")
    
    c.drawString(50, height - 90, "Clave Instalación:")
    c.drawString(50, height - 100, "Número de contrato o asignación:")
    
    c.drawString(250, height - 90, "Carácter:")
    c.drawString(350, height - 90, "Modalidad:")
    c.drawString(480, height - 90, "Número de Permiso:")

    c.drawString(50, height - 120, "Descripción Instalación:")
    c.drawString(50, height - 130, "Dirección:")
    c.drawString(520, height - 130, "Longitud:")
    c.drawString(650, height - 130, "Latitud:")

    c.drawString(50, height - 150, "Número de Pozos:")
    c.drawString(150, height - 150, "Número de Tanques:")
    c.drawString(250, height - 150, "Número Ducto Entrada/Salida:")
    c.drawString(400, height - 150, "Número Dispensarios:")
    c.drawString(500, height - 150, "Fecha y Hora del Corte:")

    #Derecha
    c.drawString(560, height - 65, "RFC Proveedor del Sistema Informático:")
    c.drawString(595, height - 75, "RFC Proveedor de Equipos:")

    c.setFont("Helvetica", 7)
    c.drawString(120, height - 65, " ")
    c.drawString(140, height - 75, " ")

    c.drawString(115, height - 90, " ")
    c.drawString(170, height - 100, " ")

    c.drawString(135, height - 120, "Terminal de almacenamiento de gasolina con octanaje menor a 91 octanos, con una capacidad de 660,000 litros.")
    c.drawString(90, height - 130, " Ignacio Mariscal 1, Zona Sin Asignación de Nombre de Col 1, San Pablo Xochimehuacan, 72014 Heroica Puebla de Zaragoza, Pue. ")
    
    
    c.drawString(560, height - 130, "19.106049048776473")
    c.drawString(680, height - 130, "-98.20741210135")

    c.drawString(285, height - 90, " ")
    c.drawString(390, height - 90, " ")
    c.drawString(555, height - 90, " ")

    c.drawString(695, height - 65, "ADT161011FC2")
    c.drawString(690, height - 75, "COHA8406117B0")

    #Añadir datos desde la BD
    c.drawString(130, height - 150, "0")
    c.drawString(230, height - 150, "9")
    c.drawString(360, height - 150, "0")
    c.drawString(480, height - 150, "0")
    now = datetime.datetime.now()
    current_datetime = now.strftime("%Y-%m-%d %H:%M")


    c.drawString(590, height - 150, current_datetime)




def create_pdf(data_list, filename="mi_documento.pdf"):
    # Configura el tamaño de la página a orientación horizontal
    page_size = landscape(letter)
    c = canvas.Canvas(filename, pagesize=page_size)

    # Obtén el ancho y la altura de la página
    width, height = page_size

    # Añade el encabezado en la primera página
    add_header(c, width, height)
    print(width)
    # Calcula las posiciones horizontales para cada columna
    x_position_1 = 70  # Posición horizontal de la primera columna
    x_position_2 = width / 2  # Posición horizontal de la segunda columna
    x_position_3 = width / 3  # Posición horizontal de la segunda columna
 
    # Inicializa la posición vertical
    y_position = height - 170
  
    # Itera sobre ambas listas de datos simultáneamente usando `zip`
    for data, data_2,data_3  in zip_longest(
        data_list, data_list_2,data_list_3,    fillvalue=''):
        # Verifica si la posición vertical es baja y se necesita una nueva página
        if y_position < 30:
            c.showPage()  # Finaliza la página actual y comienza una nueva
            add_header(c, width, height)  # Añade un nuevo encabezado en la nueva página si tienes esta función
            y_position = height - 170  # Restablece la posición vertical para los datos
           
           
        # Añade datos a sus columnas correspondientes
        #Pagina 1
        c.setFont("Helvetica-Bold", 7)
        c.drawString(x_position_1, y_position, data)
        c.drawString(x_position_2, y_position-20, data_2)
        c.drawString(x_position_3+300, y_position-20, data_3)

        # Ajusta la posición vertical hacia abajo para el siguiente par de datos
        y_position -= 20
    c.showPage()  # Finaliza la página actual y comienza una nueva
    add_header(c, width, height)  # Añade un nuevo encabezado en la nueva página si tienes esta función
    y_position = height - 170  # Restablece la posición vertical para los datos
    crear_tabla(c, x_position_1-20, y_position-250)

    x_position_1_1 = 70  # Posición horizontal de la primera columna
    x_position_2_2 = width / 2  # Posición horizontal de la segunda columna
    x_position_3_3 = width / 3  # Posición horizontal de la segunda columna
    x_position_4_4 = width / 4  # Posición horizontal de la segunda columna
    x_position_5_5 = width / 5  # Posición horizontal de la segunda columna

    y_position_2 = height - 170

    c.showPage()  # Finaliza la página actual y comienza una nueva
    add_header(c, width, height)  # Añade un nuevo encabezado en la nueva página si tienes 
    for data,data_2,data_3,data_4,data_5  in zip_longest(
        data_ductos,data_ductos_2,data_ductos_3,data_ductos_4,data_ductos_5,    fillvalue=''):
        # Verifica si la posición vertical es baja y se necesita una nueva página
        if y_position < 30:
            c.showPage()  # Finaliza la página actual y comienza una nueva
            add_header(c, width, height)  # Añade un nuevo encabezado en la nueva página si tienes esta función
            y_position = height - 170  # Restablece la posición vert
        c.drawString(x_position_1_1, y_position_2, data)
        c.drawString(x_position_2_2, y_position_2-20, data_2)
        c.drawString(x_position_3_3-50, y_position_2-160, data_3)
        c.drawString(x_position_4_4+200, y_position_2-160, data_4)
        c.drawString(x_position_5_5+350, y_position_2-160, data_5)

        y_position_2 -= 20

    # Cierra el documento PDF
    c.save()

# Lista de datos para agregar al PDF
    
data_list = [
    "Producto",
    "Clave de Producto:",
    "Diésel con combustible No fósil:",

    "Gasolina con combustible No fósil:",
    "Marca Comercial:",
    "Concentración Sustancia Marcaje:"
    "",
    "Tanques",
    "Clave Identificación Tanques:",
    "Localización y Descripción del Tanques:",
    "Vigencia de Calibración del tanque:",
    "Capacidad Total de Tanque",
    "Capacidad Operativa Tanque",
    "Capacidad Útil Tanque",
    "Capacidad Fondaje Tanque",
    "Volumen Mínimo Operativo",
    "Estado del Tanque: O ",
    "",
    "Medición Tanque:",
    "Sistema de Medición Tanque:",
    "Vigencia de la Calibración del sistema de Medición del Tanque:",
    "Incertidumbre de la Medición del Sistema de Medición del Tanque:",
    "",
    "Volumen de la Existencia Anterior",
    "Volumen natural:",
    "",
    "Volumen Acumulado o pos Recepción",
    "Volumen natural:",
    "",
    "Volumen Acumulado o pos Entrega",
    "Volumen natural:",
    "",
    "Volumen final de la Existencia",
    "Volumen natural:",
    "",
    "Recepciones",
    "Total de la Recepciones:",
    "Suma de volúmenes de la recepción",
    "Suma de las comprar:",
    "Total de Documentos:"
]

data_list_2 = [
    "Clave de Subproducto:",
    "Compos de combustible No fósil en Diésel:",
    "Compos de combustible No fósil en Gasolina:",
    "Marcaje:"
    "",
    "",
    "",
    "",
    "",
    "",
    "Valor numérico:",
    "Valor numérico:",
    "Valor numérico:",
    "Valor numérico:",
    "Valor numérico:",
    "",
    "",
    "",
    "Localización, Descripción del sistema de medición del Tanque:",
    "",
    "",
    "",
    "",
    "Volumen Neto:",
    "",
    "",
    "Volumen Neto:",
    "",
    "",
    "Volumen Neto:",
    "",
    "",
    "Volumen Neto:",
    "",
    "Entregas",
    "Total de la Entregas:",
    "Suma de volúmenes de la entrega",
    "Suma de las ventas:",
    "Total de Documentos(Facturas):"

]
data_list_3 = [
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "UM:",
    "UM:",
    "UM:",
    "UM:",
    "UM:",
     "",
    "",
    "",
    "",
    "",
    "",
    "",
    "",
    "Fecha y Hora:",
    "",
    "Fecha y Hora:",
    "",
    "Fecha y Hora:",
    "",
    "Fecha y Hora:",
    "",
    "Fecha y Hora:"

]

data_ductos = [
    "Ductos",
    "Clave de Identificación del Ducto:",
    "Descripción del Ducto:",
    "Sistema de Medición del Ducto:",
    "Vigencia de la Calibración del Sistema de Medición del Ducto:",
    "Incertidumbre de Medición del Sistema de Medición del Ducto:",
    "",
    "",
    "Total de Recepciones:"
]
data_ductos_2 = [
    "Diámetro del Ducto:",
    "Descripción del sistema de Medición del Ducto:",
]
data_ductos_3 = [
     "Suma del volumen de la Recepción:",
]
data_ductos_4 = [
     "UM:",
]
data_ductos_5 = [
     "Total de Documentos:",
]

# Llama a la función para crear el PDF
create_pdf(data_list, "mi_documento.pdf")
