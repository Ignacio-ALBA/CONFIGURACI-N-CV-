import os
from reportlab.lib.pagesizes import  letter,landscape
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import utils
from reportlab.lib.units import inch
from PIL import Image, ImageOps
from reportlab.lib import colors


def process_image(image_path):
    # Abrir la imagen con PIL
    image = Image.open(image_path)

    # Convertir la imagen a modo RGBA (si no está en ese modo)
    image = image.convert("RGBA")

    # Crear una imagen completamente blanca con el mismo tamaño
    white_background = Image.new("RGBA", image.size, (255, 255, 255, 255))

    # Combinar las dos imágenes
    result = Image.alpha_composite(white_background, image)

    # Convertir la imagen resultante a modo RGB
    result = result.convert("RGB")

    return result



def export_to_pdf(data, image1_path, image2_path):
    try:
        # Crear un archivo PDF
        pdf_filename = "output.pdf"
        c = canvas.Canvas(pdf_filename, pagesize=landscape(letter))
        def draw_header():

                    # Establecer la fuente y el tamaño del texto para el encabezado
                    c.setFont("Helvetica-Bold", 14)

                                # Procesar las imágenes
                    processed_image1 = process_image(image1_path)
                    processed_image2 = process_image(image2_path)

                    # Añadir las imágenes procesadas al PDF #width=ancho  height=alto
                    c.drawInlineImage(processed_image1, 50, 480, width=130, height=80)
                    c.drawInlineImage(processed_image2, 200, 500, width=100, height=50)


                    # Agregar el encabezado al PDF
                 #   header_text = "Encabezado del Documento"
                  ## header_position = (A4[0] - header_width) / 2  # Centrar el encabezado
                    #c.drawString(header_position, 800, header_text)

            
                    # Restaurar la fuente y el tamaño del texto
                    c.setFont("Helvetica-Bold", 9)

                   
                    
                   # Agregar texto estático al PDF alineado a la izquierda
                    version_text = "Versión del sistema 4.0.10"
                    version_position = 600  # Alinear a la izquierda
                    # Ajusta la posición vertical según sea necesario
                    version_vertical_position = 500

                    c.drawString(version_position, version_vertical_position, version_text)
                    c.setFont("Helvetica", 9)
                    # Agregar datos al PDF en dos columnas
                    column1_x = 50
                    column1_y = 165
                    
                    column2_x = 490
                    column2_y = 380
                    
                    
                    # Establecer la fuente en negrita solo para los nombres
                    c.setFont("Helvetica-Bold", 9)

                    # Datos en la primera columna H
                    c.drawString(column1_x, 480, "RFC Contribuyente:")
                    c.drawString(column1_x, 470, "RFC Representante Legal:")
                    c.drawString(column1_x, 460, "Clave Instalación:")
                    c.drawString(column1_x, 420, "Dirección:")
                    c.drawString(column1_x, 410, "Número Pozos:")

                    # Datos en la segunda columna V 
                    c.drawString(column2_x, 480, "RFC Proveedor Sistema Informático:")
                    c.drawString(column2_x, 470, "RFC Proveedor Equipos:")
                    c.drawString(column2_x, 460, "Descipción Instalación:")

                    c.drawString(370, 420, "Longitud:")
                    c.drawString(480, 420, "Latitud:")



                    c.drawString(150, 410, "Número Tanque:")
                    c.drawString(270, 410, "Número Ducto Entrada/Salida:")
                    c.drawString(450, 410, "Número Dispensarios:")
                    c.drawString(580, 410, "Fecha y Hora del Corte:")

                    # Restaurar la fuente a la normal 
                    c.setFont("Helvetica", 9)
                    c.drawString(415, 420, "22.20138")
                    c.drawString(520, 420, "-101.02329")



                    # Datos H
                    c.drawString(650, 480, "ADT161011FC2")
                    c.drawString(600, 470, "POPR790201696")
                    c.drawString(130, 460, "ACL-TRE-0045")
                    c.drawString(95, 420, "Carr. a Zacatecas 450, Sauzalito, 78116 San Luis Potosí, S.L.P.")
                    c.drawString(120, 410, "0")
                    c.drawString(225, 410, "9")
                    c.drawString(405, 410, "2")
                    c.drawString(550, 410, "0")
                    c.drawString(690, 410, "2024-01-18 13:32:08")

                    #Datos V
                    contribuyente="PIN960315R16"
                    c.drawString(140, 480, contribuyente)
                    c.drawString(column1_y, 470, "PEPC930514UN7")

                    long_text = "Terminal de almacenamiento de gasolina con octanaje menor a 91 octanos, con una capacidad de 200000 litros."
                    # Longitud máxima para cada línea
                    max_line_length = 42
                    # Dividir el texto en líneas más cortas
                    lines = [long_text[i:i+max_line_length] for i in range(0, len(long_text), max_line_length)]
                    # Agregar líneas al PDF
                    for i, line in enumerate(lines):
                        c.drawString(590, 460 - i * 12, line)
        def draw_page():
            draw_header()


        #Pagina 1
        draw_page()
        
        # Agregar una sección con un título
        section_title = "Producto"
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, 350, section_title)
        c.setFont("Helvetica", 9)
        
        c.setFont("Helvetica-Bold", 9)
        c.drawString(50, 340, "Clave de Producto:")
        c.drawString(350, 340, "Clave de Subproducto:")

        c.drawString(50, 320, "Diésel con combustible No fósil:")
        c.drawString(350, 320, "Compos de combustible No fósil en Diésel:")

        c.setFont("Helvetica", 9)
        c.drawString(135, 340, "PR03 (Diésel)")
        c.drawString(450, 340, "SP00")

        c.drawString(190, 320, "Sí")
        c.drawString(535, 320, "10%")
 
        c.setFont("Helvetica-Bold", 9)
        c.drawString(50, 280, "Clave de Producto:")
        c.drawString(50, 270, "Compos Octanaje Gasolina:")
        c.drawString(50, 260, "Gasolina con combustible No fósil:")
        c.setFont("Helvetica", 9)
        c.drawString(140, 280, "PR07 (Gasolina)")
        c.drawString(175, 270, "92")



        c.setFont("Helvetica-Bold", 9)
        c.drawString(50, 250, "Marca Comercial:")
        c.drawString(50, 240, "Concentración Sustancia Marcaje:")
        c.drawString(350, 280, "Clave del Subproducto:")

        c.drawString(350, 250, "Compos de combustible No fósil en Gasolina:")
        c.drawString(350, 240, "Marcaje:")
        c.setFont("Helvetica", 9)


        c.drawString(205, 260, "Sí")
        c.drawString(130, 250, "Blue-ultrapower 5000")
        c.drawString(200, 240, "100 ppm")
        
        c.drawString(455, 280, "SP17")
        c.drawString(550, 250, "10%")
        c.drawString(390, 240, "Nitrógeno")

        #seccion 2
        section_title = "Tanques"
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, 190, section_title)
        c.setFont("Helvetica", 9)
        
        c.setFont("Helvetica-Bold", 9)
        c.drawString(50, 170, "Clave Identificación Tanques:")
        c.drawString(50, 160, "Localización y Descripción del Tanque:")
        c.drawString(50, 150, "Vigencia de Calibración del Tanque:")
        c.drawString(50, 140, "Capacidad Total de Tanque")
        c.drawString(50, 130, "Capacidad Operativa Tanque")
        c.drawString(50, 120, "Capacidad Útil Tanque")
        c.drawString(50, 110, "Capacidad Fondaje Tanque")
        c.drawString(50, 100, "Volumen Mínimo Operativo")
        c.drawString(50, 90, "Estado del Tanque:")
      

        c.drawString(350, 140,"Valor numérico:")
        c.drawString(350, 130,"Valor numérico:")
        c.drawString(350, 120,"Valor numérico:")
        c.drawString(350, 110, "Valor numérico:")
        c.drawString(350, 100, "Valor numérico:")
        
        c.drawString(600, 140, "UM:")
        c.drawString(600, 130, "UM:")
        c.drawString(600, 120, "UM:")
        c.drawString(600, 110, "UM:")
        c.drawString(600, 100, "UM:")
        c.setFont("Helvetica", 9)


        c.drawString(180, 170, "TQS-TDA.0001")
        c.drawString(220, 160, "Tanque de almacenamiento ubicado en la terminal PINSA")
        c.drawString(210, 150, "2026-01-18")
         
        c.drawString(420, 140, "1000000")
        c.drawString(420, 130, "900000")
        c.drawString(420, 120, "1000000")
        c.drawString(420, 110, "700")
        c.drawString(420, 100, "20")
        c.drawString(135, 90, "0")

        c.drawString(620, 140, "UM02")
        c.drawString(620, 130, "UM02")
        c.drawString(620, 120, "UM02")
        c.drawString(620, 110, "UM02")
        c.drawString(620, 100, "UM03")       
        #Seccion 3 
        section_title = "Medición Tanque"
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, 70, section_title)
        c.setFont("Helvetica", 9)

        c.setFont("Helvetica-Bold", 9)
        c.drawString(50, 60, "Sistema de Medición Tanque:")
        c.drawString(50, 50, "Vigencia de la Calibración del SIstema de Medición del Tanque:")
        c.drawString(50, 40, "Incertodumbre de la Medición del Sistema de Medición del Tanque:")
    
        c.drawString(350, 60,"Localización,Descripción del Sistema de medición del Tanque:")
        c.setFont("Helvetica", 9)

        c.drawString(180, 60, "SME-TQS-TDA-0001")
        c.drawString(325, 50, "2025-06-20")
        c.drawString(340, 40, "0.10")
        c.drawString(620, 60, "Medidor de nivel MEDIMEX30000.")

        #Pagina 2
        c.showPage()
        # Asociar la función draw_page con el evento drawPage
        c.drawPage = lambda x: draw_page()
        draw_page()
        section_title = "Volúmen de la Existencia Anterior"
        c.setFont("Helvetica-Bold", 9)
        c.drawString(50, 380, section_title)
        c.setFont("Helvetica", 9)
        
        c.setFont("Helvetica-Bold", 9)
        c.drawString(50, 370, "Volúmen natural:")
        c.drawString(350, 370,"Volúmen Neto:")
        c.drawString(600, 370, "Fecha y Hora:")
        c.setFont("Helvetica", 9)
        c.drawString(130, 370, "62.010 UM03")
        c.drawString(420, 370, "61.958 UM03")
        c.drawString(670, 370, "2024-01-05 16:59:39")


        section_title = "Volumen Acumulado o pos Entrega"
        c.setFont("Helvetica-Bold", 9)
        c.drawString(50, 350, section_title)
        c.setFont("Helvetica", 9)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(50, 340, "Volúmen natural:")
        c.drawString(350, 340,"Volúmen Neto:")
        c.drawString(600, 340, "Fecha y Hora:")
        c.setFont("Helvetica", 9)
        c.drawString(130, 340, "60.751 UM03")
        c.drawString(420, 340, "60.702 UM03 ")
        c.drawString(670, 340, "2024-01-05 18:40:20")



        section_title = "Volumen final de la Existencia"
        c.setFont("Helvetica-Bold", 9)
        c.drawString(50, 310, section_title)
        c.setFont("Helvetica", 9)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(50, 300, "Volúmen natural:")
        c.drawString(350, 300,"Volúmen Neto:")
        c.drawString(600, 300, "Fecha y Hora:")
        c.setFont("Helvetica", 9)
        c.drawString(130, 300, "61.986 UM03")
        c.drawString(420, 300, "61.965 UM03")
        c.drawString(670, 300, "2024-01-05 23:59:44")



        section_title = "Recepciones"
        c.setFont("Helvetica-Bold", 9)
        c.drawString(50, 270, section_title)
        c.setFont("Helvetica", 9)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(50, 260, "Total de la Recepciones:")
        c.drawString(50, 250,"Suma de volúmenes de la recepción:")
        c.drawString(50, 240, "Suma de las comprar:")
        c.drawString(50, 230, "Total de Documentos:")
        c.setFont("Helvetica", 9)
        c.drawString(160, 260, "4")
        c.drawString(150, 240, "$190,455.00")
        c.drawString(150, 230, "2")


        section_title = "Entregas"
        c.setFont("Helvetica-Bold", 9)
        c.drawString(400, 270, section_title)
        c.setFont("Helvetica", 9)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(400, 260, "Total de la Recepciones:")
        c.drawString(400, 250,"Suma de volúmenes de la entrega:")
        c.drawString(400, 240, "Suma de las comprar:")
        c.drawString(400, 230, "Total de Documentos:")
        c.setFont("Helvetica", 9)
        c.drawString(510, 260, "3")
        c.drawString(500, 240, "$100,455.00")
        c.drawString(500, 230, "3")



        # Agregar una sección con un título
       


        #Pagina 3
        c.showPage()
        # Asociar la función draw_page con el evento drawPage
        c.drawPage = lambda x: draw_page()
        draw_page()

                
                
                        
            # Datos para la tabla
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


            # Agrega más filas si es necesario
        ]
        data.extend(total)



        # Crear la tabla
        table = Table(data)
 
       
        # Agregar la tabla al PDF

        # Configurar estilos de la tabla
    
        # Establecer estilo de la tabla
        style = TableStyle([('BACKGROUND', (0, 1), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTSIZE', (0, 1), (-1, -1), 7),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('BACKGROUND', (0,0),(4,0), colors.pink),
                    ('SPAN',(0,0),(4,0)),
                    ('BACKGROUND', (5,0),(10,0), colors.green),
                    ('SPAN',(5,0),(10,0)),
                    ('BACKGROUND', (11,0),(16,0), colors.blue),
                    ('SPAN',(11,0),(16,0)),


                    ])
 
        # Aplicar los estilos a la tabla
        table.setStyle(style)
            
        # Obtener el ancho de la página
        width, height = letter

        # Obtener el ancho de cada columna
        #col_widths = [width / len(data[0]) for _ in data[0]]
        col_widths = [80, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40]  # Ancho de cada columna en puntos

        # Configurar el tamaño de las columnas
        table._argW = col_widths



        table.wrapOn(c, width, height)  # Ajusta las coordenadas según sea necesario
        table.drawOn(c, 50,height- 650)  # Ajusta las coordenadas según sea necesario




        #Pagina 4
        c.showPage()
        # Asociar la función draw_page con el evento drawPage
        c.drawPage = lambda x: draw_page()
        draw_page()

                
      
        c.setFont("Helvetica-Bold", 9)
        c.drawString(50, 350, "Clave de Identificación del Ducto:")
        c.drawString(50, 340, "Descripción del Ducto:")
        c.drawString(50, 330, "Sistema de Medición del Ducto:")
        c.drawString(50, 320, "Vigencia de la Calibración del Sistema de Medición del Ducto: ")
        c.drawString(50, 310, "Incertidumbre de Medición del Sistema de Medición del Ducto:")
        
        c.drawString(350, 350,"Diámetro del Ducto:")
        c.drawString(350, 330,"Descripción del sistema de Medición del Ducto:")

        c.drawString(50, 280, "Total de Recepciones:" )
        c.drawString(200, 280,"Suma del volumen de la Recepción: ")
        c.drawString(400, 280,"UM:")
        c.drawString(450, 280,"Total de Documentos:")
        c.setFont("Helvetica", 9)



        c.drawString(120, 130, "130000 del id")
        c.drawString(70, 110, "UM03")

        c.drawString(200, 350, "DUC-DES-004")
        c.drawString(150, 340, "Ducto de descarga del autotanque de clave TQS-ATQ-1234 de distribución de petrolíferos.")
        c.drawString(190, 330, "SMD-DUC-DES-004")
        c.drawString(320, 320, "2018-06-30")
        c.drawString(320, 310, "0.9%")
        
        c.drawString(440, 350," 3 pulgadas")
        c.drawString(560, 330,"Medidor dinámico Marca DuctMex ")


        c.drawString(150, 280, "2" )
        c.drawString(360, 280,"70,000")
        c.drawString(420, 280,"UM04")
        c.drawString(550, 280,"2")

        # Guardar el PDF
        c.save()
        print(f"El archivo PDF se ha guardado en: {os.path.abspath(pdf_filename)}")

    except Exception as e:
        print(f"Error: {e}")
# Rutas de las imágenes
image1_path = "src/static/img/logo_pinsa_.png"
image2_path = "src/static/img/scaizen-logo.png"

# Ejemplo de uso
data = ["Dato 1", "Dato 2", "Dato 3"]
export_to_pdf(data, image1_path, image2_path)