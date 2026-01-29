from fpdf import FPDF
from datetime import datetime
import os
from config_carpet.config import GlobalConfig
import logging
import qrcode  # Asegúrate de tener instalado el paquete qrcode

class PDF(FPDF):
    def __init__(self, data_report, orientation='L', headerpage='Reporte Volumétrico Mensual', periodo='', SelloDigital='', include_qr=False):
        super().__init__(orientation=orientation)
        self.headerpage = headerpage
        self.data_report = data_report
        self.periodo = periodo
        self.include_qr = include_qr  # Variable para habilitar o deshabilitar el QR
        self.SelloDigital = SelloDigital  # Inicializar SelloDigital

        # Adjust margins to make the body smaller
        self.set_left_margin(10)
        self.set_right_margin(10)
        self.set_auto_page_break(auto=True, margin=40)

    def header(self):
        # Set title
        # Añadir imagen al encabezado
        image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..","static/img/didipsa_HD.png"))
        self.image(image_path, x=20, y=2, w=50, h=15)
        image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..","static/img/scaizen-logo.png"))
        self.image(image_path, x=self.w-70, y=5, w=50, h=10)
        #self.line(20, 20, self.w - 20, 20)
        self.set_font('Arial', 'B', 12)
        self.cell(0, 12, self.headerpage, 0, 1, 'C')
        
        x = self.get_x()
        y = self.get_y()

        # Calculate column widths
        page_width = self.w - 2 * self.l_margin  # Page width minus left and right margins
        col_width = page_width / 2  # Equal width for each column

        #Esto debe de ir al lado derecho de la hoja
        col_width = page_width - (11)
        self.set_font('Arial', 'B', 9)
        self.cell(col_width, 6, 'Versión del sistema ',0, 0, 'R')
        self.set_font('Arial', '', 9)
        self.cell(11, 6,'4.0.10', 0, 0, 'R')
        self.ln() 

        self.set_font('Arial', 'B', 9)
        self.cell(36, 6, 'RFC Contribuyente:', 0, 0, 'L')
        self.set_font('Arial', '', 9)
        RfcContribuyente = self.data_report.RfcContribuyente
        self.cell(len(RfcContribuyente)*2.5, 6, RfcContribuyente, 0, 0, 'L')

        #Esto debe de ir al lado derecho de la hoja
        RfcProveedor = self.data_report.RfcProveedor
        col_width = page_width - 36 - (len(RfcProveedor) + len(RfcContribuyente))*2.5
        self.set_font('Arial', 'B', 9)
        self.cell(col_width, 6, 'RFC Proveedor del Sistema Informático:', 0, 0, 'R')
        self.set_font('Arial', '', 9)
        self.cell(len(RfcProveedor)*2.5, 6, RfcProveedor, 0, 0, 'R')
        self.ln() 

        self.set_font('Arial', 'B', 9)
        self.cell(44, 6, 'FC Representante Legal:', 0, 0, 'L')
        self.set_font('Arial', '', 9)
        RfcRepresentanteLegal = self.data_report.RfcRepresentanteLegal
        self.cell(len(RfcRepresentanteLegal)*2.5, 6, RfcRepresentanteLegal, 0, 0, 'L')
        #Esto debe de ir al lado derecho de la hoja
        RfcProveedorEquipos = "POPR790201696"
        col_width = page_width - 44 - (len(RfcProveedorEquipos) + len(RfcRepresentanteLegal))*2.5
        self.set_font('Arial', 'B', 9)
        self.cell(col_width, 6, 'RFC Proveedor de Equipos:', 0, 0, 'R')
        self.set_font('Arial', '', 9)
        self.cell(len(RfcProveedorEquipos)*2.5, 6, RfcProveedorEquipos, 0, 0, 'R')
        self.ln() 

        self.set_font('Arial', 'B', 9)
        self.cell(34, 6, 'Clave Instalación:', 0, 0, 'L')
        self.set_font('Arial', '', 9)
        ClaveInstalacion = self.data_report.ClaveInstalacion
        self.cell(len(ClaveInstalacion)*2.5, 6, ClaveInstalacion, 0, 0, 'L')
        self.set_font('Arial', 'B', 9)
        self.cell(18, 6, 'Carácter:', 0, 0, 'L')
        self.set_font('Arial', '', 9)
        TipoCaracter = self.data_report.TipoCaracter
        self.cell(len(TipoCaracter)*2.5, 6, TipoCaracter, 0, 0, 'L')
        self.set_font('Arial', 'B', 9)
        self.cell(22, 6, 'Modalidad:', 0, 0, 'L')
        self.set_font('Arial', '', 9)
        ModalidadPermiso = self.data_report.ModalidadPermiso
        self.cell(len(ModalidadPermiso)*3, 6, ModalidadPermiso, 0, 0, 'L')
        self.set_font('Arial', 'B', 9)
        self.cell(38, 6, 'Número de Permiso:', 0, 0, 'L')
        self.set_font('Arial', '', 9)
        NumPermiso = self.data_report.NumPermiso
        self.cell(len(NumPermiso)*2.5, 6, NumPermiso, 0, 0, 'L')
        self.ln() 

        self.set_font('Arial', 'B', 9)
        self.cell(60, 6, 'Número de contrato o asignación:', 0, 0, 'L')
        self.set_font('Arial', '', 9)
        NumContratoOAsignacion = self.data_report.NumContratoOAsignacion if self.data_report.NumContratoOAsignacion else "S/N"
        self.cell(len(NumContratoOAsignacion)*2.5, 6, NumContratoOAsignacion, 0, 0, 'L')
        self.ln() 
        self.set_font('Arial', 'B', 9)
        self.cell(42, 6, 'Descripción Instalación: ', 0, 0, 'L')
        self.set_font('Arial', '', 9)
        descripcion = 'Comercializador Inova, Oficinas en Ciudad de México'
        self.cell(len(descripcion)*2.5, 6, descripcion, 0, 0, 'L')
        self.ln() 
        self.set_font('Arial', 'B', 9)
        self.cell(18, 6, 'Dirección: ', 0, 0, 'L')
        self.set_font('Arial', '', 9)
        direccion = 'HERA 85, COL. CREDITO CONSTRUCTOR ALCALDÍA BENITO JUAREZ C.P 03940, CIUDAD DE MÉXICO'
        self.cell(len(direccion)*2, 6, direccion, 0, 0, 'L')
        self.ln() 
        
        self.set_font('Arial', 'B', 9)
        self.cell(18, 6, 'Longitud: ', 0, 0, 'L')
        self.set_font('Arial', '', 9)
        GeolocalizacionLongitud = str(self.data_report.GeolocalizacionLongitud)
        self.cell(len(GeolocalizacionLongitud)*2.5, 6, GeolocalizacionLongitud, 0, 0, 'L')

        self.set_font('Arial', 'B', 9)
        self.cell(18, 6, 'Latitud: ', 0, 0, 'L')
        self.set_font('Arial', '', 9)
        GeolocalizacionLatitud = str(self.data_report.GeolocalizacionLatitud)
        self.cell(len(GeolocalizacionLatitud)*2.5, 6, GeolocalizacionLatitud, 0, 0, 'L')
        self.ln() 

        self.set_font('Arial', 'B', 9)
        self.cell(27, 6, 'Número Pozos: ', 0, 0, 'L')
        self.set_font('Arial', '', 9)
        NumeroPozos = str(self.data_report.NumeroPozos)
        self.cell(7, 6, NumeroPozos, 0, 0, 'L')

        self.set_font('Arial', 'B', 9)
        self.cell(29, 6, 'Número Tanque: ', 0, 0, 'L')
        self.set_font('Arial', '', 9)
        NumeroTanques = str(self.data_report.NumeroTanques)
        self.cell(7, 6, NumeroTanques, 0, 0, 'L')

        self.set_font('Arial', 'B', 9)
        self.cell(39, 6, 'Número Dispensarios: ', 0, 0, 'L')
        self.set_font('Arial', '', 9)
        NumeroDispensarios = str(self.data_report.NumeroDispensarios)
        self.cell(7, 6, NumeroDispensarios, 0, 0, 'L')

        self.set_font('Arial', 'B', 9)
        self.cell(64, 6, 'Número de Ductos Entrada y Salida:', 0, 0, 'L')
        self.set_font('Arial', '', 9)
        NumeroDuctosEntradaSalida = str(self.data_report.NumeroDuctosEntradaSalida)
        self.cell(7, 6, NumeroDuctosEntradaSalida, 0, 0, 'L')

        self.set_font('Arial', 'B', 9)
        self.cell(83, 6, 'Número de Ductos de Transporte y Distribución:', 0, 0, 'L')
        self.set_font('Arial', '', 9)
        NumeroDuctosTransporteDistribucion = str(self.data_report.NumeroDuctosTransporteDistribucion)
        self.cell(7, 6, NumeroDuctosTransporteDistribucion, 0, 0, 'L')
        self.ln() 

        self.set_font('Arial', 'B', 9)
        self.cell(36, 6, 'Periodo del reporte:', 0, 0, 'L')
        self.set_font('Arial', '', 9)
        periodo = self.periodo
        self.cell(len(periodo)*2.5, 6, periodo, 0, 0, 'L')

        #Esto debe de ir al lado derecho de la hoja
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        col_width = page_width - 36 - (36 + len(periodo)*2.5)
        self.set_font('Arial', 'B', 9)
        self.cell(col_width, 6, 'Fecha y Hora de generación del reporte', 0, 0, 'R')
        self.set_font('Arial', '', 9)
        self.cell(36, 6, date, 0, 0, 'R')
        self.ln() 
        self.ln() 
        
    def check_page_break(self, height_needed):
        # Calcula la altura disponible en la página
        if self.get_y() + height_needed > self.h - self.b_margin:
            self.add_page() 
            return True 
        else:  return False 
        
    def producto_text(self, data):
        config = GlobalConfig()
        # Remover el símbolo #
        producto_color = config.PRODUCTOS_COLOR_BY_NAME
        producto_name = config.PRODUCTOS_NAMES
        hex = producto_color[data.nombre_producto]
        hex = hex.lstrip('#')

        # Convertir las partes del color
        r = int(hex[0:2], 16)
        g = int(hex[2:4], 16)
        b = int(hex[4:6], 16)

        self.set_font('Arial', 'B', 11)
        self.set_text_color(r, g, b)  # Cambiar color del texto a azul
        #self.cell(0, 6, f"Producto {producto_name[data.nombre_producto].capitalize()}", 0, 0, 'L')
        self.cell(0, 6, f"Producto {producto_name[data.nombre_producto]}", 0, 0, 'L')
        self.ln() 

        self.set_text_color(0, 0, 0)
        self.set_font('Arial', 'B', 10)
        self.cell(34, 6, 'Clave de Producto:', 0, 0, 'L')
        self.set_font('Arial', '', 10)
        ClaveProducto = data.ClaveProducto
        self.cell(30, 6, ClaveProducto, 0, 0, 'L')
        self.set_font('Arial', 'B', 10)
        self.cell(40, 6, 'Sistema de medición:', 0, 0, 'L')
        self.set_font('Arial', '', 10)
        self.cell(45, 6, 'Veeder Root TLS450PLUS', 0, 0, 'L')
        self.set_font('Arial', 'B', 10)
        self.cell(40, 6, 'Clave de Subproducto:', 0, 0, 'L')
        self.set_font('Arial', '', 10)
        ClaveSubProducto = data.ClaveSubProducto
        self.cell(20, 6, ClaveSubProducto, 0, 0, 'L')

        self.set_font('Arial', 'B', 10)
        self.cell(31, 6, 'Marca Comercial:', 0, 0, 'L')
        self.set_font('Arial', '', 10)
        MarcaComercial = data.MarcaComercial
        self.cell(40, 6, MarcaComercial, 0, 0, 'L')
        self.ln() 
        if data.ClaveProducto == "PR07":
            self.set_font('Arial', 'B', 10)
            self.cell(61, 6, 'Gasolina con combustible No fósil:', 0, 0, 'L')
            self.set_font('Arial', '', 10)
            GasolinaConCombustibleNoFosil = str(data.GasolinaConCombustibleNoFosil) 
            self.cell(20, 6, GasolinaConCombustibleNoFosil, 0, 0, 'L')

            self.set_font('Arial', 'B', 10)
            self.cell(80, 6, 'Campos de combustible No fósil en Gasolina:', 0, 0, 'L')
            self.set_font('Arial', '', 10)
            ComposDeCombustibleNoFosilEnGasolina = str(data.ComposDeCombustibleNoFosilEnGasolina) if data.ComposDeCombustibleNoFosilEnGasolina else "N/A"
            self.cell(20, 6, ComposDeCombustibleNoFosilEnGasolina, 0, 0, 'L')

            self.set_font('Arial', 'B', 10)
            self.cell(54, 6, 'Campos Octanaje en Gasolina:', 0, 0, 'L')
            self.set_font('Arial', '', 10)
            ComposOctanajeGasolina = "10"
            self.cell(20, 6, ComposOctanajeGasolina, 0, 0, 'L')
            self.ln() 
        if data.ClaveProducto == "PR03":
            self.set_font('Arial', 'B', 10)
            self.cell(56, 6, 'Diésel con combustible No fósil:', 0, 0, 'L')
            self.set_font('Arial', '', 10)
            DieselConCombustibleNoFosil = str(data.DieselConCombustibleNoFosil)
            self.cell(20, 6, DieselConCombustibleNoFosil, 0, 0, 'L')

            self.set_font('Arial', 'B', 10)
            self.cell(74, 6, 'Campos de combustible No fósil en Diésel:', 0, 0, 'L')
            self.set_font('Arial', '', 10)
            ComposDeCombustibleNoFosilEnDiesel = str(data.ComposDeCombustibleNoFosilEnDiesel) if data.ComposDeCombustibleNoFosilEnDiesel else "N/A"
            self.cell(20, 6, ComposDeCombustibleNoFosilEnDiesel, 0, 0, 'L')
            self.ln() 

        self.set_font('Arial', 'B', 10)
        self.cell(20, 6, 'Marcaje:', 0, 0, 'L')
        self.set_font('Arial', '', 10)
        Marcaje = data.Marcaje if data.Marcaje else "No"
        self.cell(20, 6, Marcaje, 0, 0, 'L')
        self.set_font('Arial', 'B', 10)
        self.cell(60, 6, 'Concentración Sustancia Marcaje:', 0, 0, 'L')
        self.set_font('Arial', '', 10)
        ConcentracionSustanciasMarcaje = f"{data.ConcentracionSustanciasMarcaje} ppm " if data.ConcentracionSustanciasMarcaje else "N/A"    
        self.cell(20, 6, ConcentracionSustanciasMarcaje, 0, 0, 'L')
        self.ln() 
        self.ln()
   
    def tanque_text(self, data):
        self.check_page_break(100)
        self.set_font('Arial', 'B', 11)
        self.cell(0, 6, f"Tanque {data.ClaveIdentificacionTanque}", 0, 0, 'L')
        self.ln()#Salto de linea

        self.set_font('Arial', 'B', 10)
        self.cell(51, 6, 'Clave Identificación Tanque:', 0, 0, 'L')
        self.set_font('Arial', '', 10)
        ClaveIdentificacionTanque = data.ClaveIdentificacionTanque
        self.cell(len(ClaveIdentificacionTanque)*2.5, 6, ClaveIdentificacionTanque, 0, 0, 'L')
        self.ln()#Salto de linea   
        self.set_font('Arial', 'B', 10)
        self.cell(40, 6, 'Sistema de medición:', 0, 0, 'L')
        self.set_font('Arial', '', 10)
        self.cell(45, 6, 'Veeder Root TLS450PLUS', 0, 0, 'L')
        self.ln()
        self.set_font('Arial', 'B', 10)
        self.cell(69, 6, 'Localización y Descripción del Tanque:', 0, 0, 'L')
        self.set_font('Arial', '', 10)
        LocalizacionYODescripcionTanque = data.LocalizacionYODescripcionTanque
        self.cell(len(LocalizacionYODescripcionTanque)*2.5, 6, LocalizacionYODescripcionTanque, 0, 0, 'L')
        self.ln()#Salto de linea
        self.set_font('Arial', 'B', 10)
        self.cell(61, 6, 'Vigencia de Calibración del tanque:', 0, 0, 'L')
        self.set_font('Arial', '', 10)
        VigenciaCalibracionTanque = str(data.VigenciaCalibracionTanque)
        self.cell(len(VigenciaCalibracionTanque)*2.5, 6, VigenciaCalibracionTanque, 0, 0, 'L')
        self.ln()#Salto de linea
        self.set_font('Arial', 'B', 10)
        self.cell(49, 6, 'Capacidad Total de Tanque:', 0, 0, 'L')
        self.set_font('Arial', '', 10)
        CapacidadTotalTanque = str(data.CapacidadTotalTanque)
        self.cell(len(CapacidadTotalTanque)*2.5, 6, CapacidadTotalTanque, 0, 0, 'L')
        self.ln()#Salto de linea
        self.set_font('Arial', 'B', 10)
        self.cell(51, 6, 'Capacidad Operativa Tanque:', 0, 0, 'L')
        self.set_font('Arial', '', 10)
        CapacidadOperativaTanque = str(data.CapacidadOperativaTanque)
        self.cell(len(CapacidadOperativaTanque)*2.5, 6, CapacidadOperativaTanque, 0, 0, 'L')
        self.ln()#Salto de linea
        self.set_font('Arial', 'B', 10)
        self.cell(41, 6, 'Capacidad Útil Tanque:', 0, 0, 'L')
        self.set_font('Arial', '', 10)
        CapacidadUtilTanque = str(data.CapacidadOperativaTanque)
        self.cell(len(CapacidadUtilTanque)*2.5, 6, CapacidadUtilTanque, 0, 0, 'L')
        self.ln()#Salto de linea
        self.set_font('Arial', 'B', 10)
        self.cell(59, 6, 'Capacidad de Fondaje del Tanque:', 0, 0, 'L')
        self.set_font('Arial', '', 10)
        CapacidadFondajeTanque = str(data.CapacidadFondajeTanque)
        self.cell(len(CapacidadFondajeTanque)*2.5, 6, CapacidadFondajeTanque, 0, 0, 'L')
        self.ln()#Salto de linea
        self.set_font('Arial', 'B', 10)
        self.cell(48, 6, 'Volumen Mínimo Operativo:', 0, 0, 'L')
        self.set_font('Arial', '', 10)
        VolumenMinimoOperacion = str(data.VolumenMinimoOperacion)
        self.cell(len(VolumenMinimoOperacion)*2.5, 6, VolumenMinimoOperacion, 0, 0, 'L')
        self.ln()#Salto de linea





        self.ln()

    def section_title_table(self, title):
        # Set a section title
        self.set_font('Arial', 'B', 11)
        self.cell(0, 10, title, 0, 1, 'L')

    def section_title(self, title):
        # Set a section title
        self.set_font('Arial', 'B', 10)
        self.cell(0, 6, title, 0, 1, 'L')

    def section_body(self, data):
        # Data in section
        self.set_font('Arial', '', 10)
        for row in data:
            self.cell(0, 6, row, 0, 1)

    def create_table(self, headers, rows):
        # Headers - black background, white text
        self.set_fill_color(33, 37, 41)  # Blackish background
        self.set_text_color(255, 255, 255)  # White text
        self.set_font('Arial', 'B', 9)
        
        # Set headers
        for header in headers:
            self.cell(70, 6, header, 1, 0, 'C', 1)  # Create black background cells
        self.ln()

        # Rows - grey background
        self.set_fill_color(245, 245, 245)  # Light grey
        self.set_text_color(0, 0, 0)  # Black text
        self.set_font('Arial', '', 9)

        # Set rows with grey background
        for row in rows:
            if isinstance(row, list):
                for item in row:
                    self.cell(70, 6, str(item), 1, 0, 'C', 1)
                self.ln()
    
    def create_table_tank(self, sizes, headers, rows, colums_align={}):
        # Calcula el ancho total disponible de la página
        total_width = self.w - 2 * self.l_margin
        logging.debug(f'total_width: {total_width}')

        # Convierte cada porcentaje en `sizes` al tamaño real en puntos
        sizes_in_points = [(percent / 100) * total_width for percent in sizes]

        def set_headers():
            # Headers - black background, white text
            self.set_fill_color(33, 37, 41)  # Blackish background
            self.set_text_color(255, 255, 255)  # White text
            self.set_font('Arial', 'B', 9)
            
            maxh = 6
            for i, header in enumerate(headers):
                doble_header = len(header) * 4
                if doble_header > sizes_in_points[i]: 
                    maxh = max(6, 6 * int(doble_header / sizes_in_points[i]))
            
            for i, header in enumerate(headers):
                x_before = self.get_x()
                y_before = self.get_y()
                h = maxh if (len(header) * 2) <= sizes_in_points[i] else 6
                self.multi_cell(sizes_in_points[i], h, header, 1, 'C', 1)
                self.set_xy(x_before + sizes_in_points[i], y_before)
            self.ln()

        set_headers()

        # Rows - grey background
        self.set_fill_color(245, 245, 245)  # Light grey
        self.set_text_color(0, 0, 0)  # Black text
        self.set_font('Arial', '', 9)

        maxh = 6
        for row in rows:
            if isinstance(row, list):
                # Calculate max height for each cell in the row to ensure all cells stay on the same page
                columna_excluida = None
                for i, item in enumerate(row):
                    doble_header = len(str(item)) * 2
                    if doble_header > sizes_in_points[i]: 
                        maxh = max(6, 6 * int(doble_header / sizes_in_points[i]))
                        columna_excluida = i

                # Check if there is enough space for the row; if not, add a page break
                row_height = maxh
                if self.get_y() + row_height > self.page_break_trigger:
                    self.add_page()
                    set_headers()  # Re-add headers after a page break
                    self.set_fill_color(245, 245, 245)  # Light grey
                    self.set_text_color(0, 0, 0)  # Black text
                    self.set_font('Arial', '', 9)


                y_before = self.get_y()
                x_before = self.get_x()

                for i, item in enumerate(row):
                    align = colums_align.get(str(i + 1), 'C')
                    
                    h = 6 if columna_excluida == i else maxh
                    suma = maxh - 6 if i > 3 else 0

                    # Logging statements for debugging
                    #logging.debug(f'id: {row[0]}, columna {i}: h={h}, y={y_before}, data={item}')

                    # Create the cell with alignment and fill
                    self.multi_cell(sizes_in_points[i], h, str(item), 1, align, 1)
                    self.set_xy(x_before + sizes_in_points[i], y_before + suma)
                    x_before += sizes_in_points[i]

                self.ln()

        

    def table_headers(self, sizes, headers):
        total_width = self.w - 2 * self.l_margin
        # Convierte cada porcentaje en `sizes` al tamaño real en puntos
        sizes_in_points = [(percent / 100) * total_width for percent in sizes]
        
        # Headers - black background, white text
        self.set_fill_color(18, 43, 73)  # Blackish background
        self.set_text_color(255, 255, 255)  # White text
        self.set_font('Arial', 'B', 9)
        
        for i, header in enumerate(headers):
            x_before = self.get_x()  # Store current x position
            y_before = self.get_y()  # Store current y position
            self.multi_cell(sizes_in_points[i], 8, header, 1, 'C', 1)  # Create multi-line header cells
            self.set_xy(x_before + sizes_in_points[i], y_before)  # Move x to the right for next cell
        self.ln()


    def two_column_section(self, data):
        self.set_font('Arial', 'B', 10)

        # Calculate column widths
        page_width = self.w - 2 * self.l_margin  # Page width minus left and right margins
        col_width = page_width / 2  # Equal width for each column

        # Save the current position
        x = self.get_x()
        y = self.get_y()

        # Set column widths
        col1_x = x
        col2_x = x + col_width

        # First column (left-aligned)
        self.set_x(col1_x)
        self.multi_cell(col_width, 6, f"RFC Contribuyente: {data['RfcContribuyente']}\n"
                        f"RFC Representante Legal: {data['RfcRepresentanteLegal']}\n"
                        f"RFC Proveedor del Sistema Informático: {data['RfcProveedor']}\n"
                        f"Número de contrato o asignación: {data['NumContratoOAsignacion']}\n"
                        f"Perido del Reporte: ")
        self.set_xy(col2_x, y)

        # Second column (right-aligned)
        self.set_font('Arial', 'B', 10)
        self.multi_cell(col_width, 6, f"Clave Intalación: {data['ClaveInstalacion']}\n"
                                        f"Número de Permiso: {data['NumPermiso']}\n"
                                        f"Modalidad: {data['ModalidadPermiso']}\n"
                                        f"Carácter: {data['TipoCaracter']}\n"
                                        f'Fecha del Reporte: {datetime.now().strftime("%Y/%m/%d %H:%M:%S")}', align='R')
        self.ln()  # New line after the columns

    def footer(self):
        # Set position of the footer at 1.5 cm from the bottom
        self.set_y(-40)
        # Set font for the footer
        self.set_font('Arial', 'I', 6)

        #sello_digital = ("DBbMazqcf74QxTGeGd48BCOwce2Ft/H7YpLVia8e0TwnKO+nEJyJA4LKVc+YHwKX8CkBI/y4lEMdW3eou6hVEl6up0CUWAW7WuThqrI9+hhCZWgDhKKOrs2RO9uFAQTa6A0X/2dZpPWhxTAHBXEPVn9n7Mi1lK1hBK48l0pth1COXDRgGusmv+0S6SlDJ3mIYVtXtlY2flWkIq1xls73Kz7XfVy1f6sfjXigsYo19MoP6kAD65HtCayEQ2lXtQRrajeoe7TfNSpJ1frDpMLpwYno7iLXzy7Am59zuOKa+QCFNUJ6uNaH+nqKQiqHQj5zlCie4KcMi6bIiCV2lS51vg==")
        sello_digital = self.SelloDigital
        # try:
        #     # Generate QR code dynamically from sello_digital
        #     qr = qrcode.QRCode(box_size=2, border=1)
        #     qr.add_data(sello_digital.replace("\n", ""))  # Remove line breaks for QR generation
        #     qr.make(fit=True)
        #     qr_image = qr.make_image(fill='black', back_color='white')
            
        #     # Save QR code to a temporary file
        #     qr_temp_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static/temp_qr.png"))
        #     qr_image.save(qr_temp_path)

        #     # Add QR code to the PDF
        #     qr_x = 10
        #     qr_y = self.h - 40
        #     self.image(qr_temp_path, x=qr_x, y=qr_y, w=30, h=30)

        #     # Add the digital seal title
        #     self.set_xy(qr_x + 35, qr_y)  # Position text to the right of the QR
        #     self.set_font('Arial', 'B', 10)  # Bold font for the title
        #     self.cell(0, 4, "Sello Digital:", 0, 1, 'L')  # Title in bold

        #     # Add the digital seal content aligned with the title
        #     self.set_x(qr_x + 35)  # Align content with the title
        #     self.set_font('Arial', 'I', 10)  # Italic font for the content
        #     self.multi_cell(0, 4, sello_digital, 0, 'L')  # Content spans the rest of the width

        # except Exception as e:
        #     logging.error(f"Error al generar o colocar el QR: {e}")
        # finally:
        #     # Ensure the temporary file is deleted
        #     if os.path.exists(qr_temp_path):
        #         os.remove(qr_temp_path)

        # Add page number in the bottom-right corner
        self.set_y(-10)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'R')

