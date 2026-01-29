
class Proveedores:
    def __init__(self,RFC)-> None:
        self.RFC = RFC

    

class Caracteres:
    def __init__(self,TipoCaracter,ModalidadPermiso,NumPermiso,
                  NumContratoOAsignacion,InstalacionAlmacenGasNatural)-> None:
        self.TipoCaracter = TipoCaracter
        self.ModalidadPermiso = ModalidadPermiso
        self.NumPermiso = NumPermiso
        self.NumContratoOAsignacion = NumContratoOAsignacion
        self.InstalacionAlmacenGasNatural = InstalacionAlmacenGasNatural

class Geolocalizacion:
    def __init__(self,GeolocalizacionLatitud,GeolocalizacionLongitud) -> None:
        self.GeolocalizacionLatitud = GeolocalizacionLatitud
        self.GeolocalizacionLongitud = GeolocalizacionLongitud
 



class Producto:#TH-01,TH-02,TH-03
    def __init__(self,ClaveProducto,ClaveSubProducto,Producto  ,MarcaComercial,Marcaje,ConcentracionSustanciaMarcaje,
                  Tanque) -> None:
        self.ClaveProducto = ClaveProducto
        
        self.ClaveSubProducto = ClaveSubProducto #Instancia de Subproducto
        self.Producto = Producto
        self.MarcaComercial = MarcaComercial
        self.Marcaje = Marcaje
        self.ConcentracionSustanciaMarcaje = ConcentracionSustanciaMarcaje

        self.Tanque=Tanque#Instancia de Tanque
       


class Gasolina:#PR07 Obligatorios
    def __init__(self,ComposOctanajeGasolina,
                    GasolinaConCombustibleNoFosil,
                    ComposDeCombustibleNoFosilEnGasolina  ) -> None:
                self.ComposOctanajeGasolina = ComposOctanajeGasolina
                self.GasolinaConCombustibleNoFosil = GasolinaConCombustibleNoFosil
                self.ComposDeCombustibleNoFosilEnGasolina = ComposDeCombustibleNoFosilEnGasolina

class Diesel:#PR03
    def __init__(self,DieselConCombustibleNoFosil,
                    ComposDeCombustibleNoFosilEnDiesel ) -> None:
            self.DieselConCombustibleNoFosil = DieselConCombustibleNoFosil
            self.ComposDeCombustibleNoFosilEnDiesel = ComposDeCombustibleNoFosilEnDiesel
    
    #class Turbosina(UserMixin):#PR11
    #    def __init__(self,TurbosinaConCombustibleNoFosil:str,
    #                 ComposDeCombustibleNoFosilEnTurbosina:int) -> None:
    #        self.TurbosinaConCombustibleNoFosil = TurbosinaConCombustibleNoFosil
    #        self.ComposDeCombustibleNoFosilEnTurbosina = ComposDeCombustibleNoFosilEnTurbosina

     
    """class GasLP(UserMixin):#
        def __init__(self,ComposDePropanoEnGasLP:float,
                     ComposDeButanoEnGasLP:float
                     ) -> None:
            self.ComposDePropanoEnGasLP = ComposDePropanoEnGasLP
            self.ComposDeButanoEnGasLP = ComposDeButanoEnGasLP

    class Petroleo(UserMixin):#PR07
        def __init__(self,DensidadDePetroleo:float,
                     ComposDeAzufreEnPetroleo:float) -> None:
            self.DensidadDePetroleo = DensidadDePetroleo
            self.ComposDeAzufreEnPetroleo = ComposDeAzufreEnPetroleo
    
    #Checar con Oney
    class GasNatural(UserMixin):#PR09
       #class ComposGasNaturalOCondensados(UserMixin):
        def __init__(self, 
                   ComposGasNaturalOCondensados:str,
                    FraccionMolar:float,
                     PoderCalorifico:int) -> None:
                self.ComposGasNaturalOCondensados = ComposGasNaturalOCondensados
                self.FraccionMolar = FraccionMolar
                self.PoderCalorifico = PoderCalorifico

    class Otros(UserMixin):#PRO20
        def __init__(self,Otros:str) -> None:
            self.Otros = Otros"""
       


class Tanque:
    def __init__(self,ClaveIdentificacionTanque,
                 LocalizacionYODescripcionTanque,
                 VigenciaCalibracionTanque,
                 CapacidadTotalTanque,
                 CapacidadOperativaTanque,
                 CapacidadUtilTanque,
                 CapacidadFondajeTanque,
                 CapacidadGasTalon,                 
                 VolumenMinimoOperacion,
                 EstadoTanque,
                 MedicionTanque,
                 Existencia,
                 Recepciones,
                 Entregas) -> None:
                 
        self.ClaveIdentificacionTanque = ClaveIdentificacionTanque
        self.LocalizacionYODescripcionTanque= LocalizacionYODescripcionTanque
        self.VigenciaCalibracionTanque = VigenciaCalibracionTanque
        
        self.CapacidadTotalTanque = CapacidadTotalTanque  #Instancia de Capacidad
        self.CapacidadOperativaTanque = CapacidadOperativaTanque #Instancia de Capacidad
        self.CapacidadUtilTanque = CapacidadUtilTanque #Instancia de Capacidad
        self.CapacidadFondajeTanque = CapacidadFondajeTanque #Instancia de Capacidad
        self.CapacidadGasTalon = CapacidadGasTalon #Instancia de Capacidad
        self.VolumenMinimoOperacion = VolumenMinimoOperacion #Instancia de Capacidad
        
        self.EstadoTanque = EstadoTanque

        self.MedicionTanque = MedicionTanque  #Instancia de MedicionTanque ---->>>>> Debe ser un arreglo
        self.Existencias = Existencia#Instancia de Existencia
        self.Recepciones = Recepciones #Instancia de RECEPCIONES 
        self.Entregas = Entregas #Instancia  de Entregas

class Capacidad:
    def __init__(self,ValorNumerico,UM) -> None:
                self.ValorNumerico = ValorNumerico
                self.UM = UM

class MedicionTanques:
    def __init__(self,SistemaMedicionTanque ,
                     LocalizODescripSistMedicionTanque,
                     VigenciaCalibracionSistMedicionTanque,
                     IncertidumbreMedicionSistMedicionTanque) -> None:
            self.SistemaMedicionTanque = SistemaMedicionTanque
            self.LocalizODescripSistMedicionTanque = LocalizODescripSistMedicionTanque
            self.VigenciaCalibracionSistMedicionTanque = VigenciaCalibracionSistMedicionTanque
            self.IncertidumbreMedicionSistMedicionTanque = IncertidumbreMedicionSistMedicionTanque
    
class Existencia:
    def __init__(self,VolumenExistenciasAnterior,
                     VolumenAcumOpsRecepcion,
                     HoraRecepcionAcumulado,
                     VolumenAcumOpsEntrega,
                     HoraEntregaAcumulado,
                     VolumenExistencias,
                     FechaYHoraEstaMedicion,
                     FechaYHoraMedicionAnterior) -> None:
            
            self.VolumenExistenciasAnterior = VolumenExistenciasAnterior# instancia de Existencias_Volumenes
            self.VolumenAcumOpsRecepcion = VolumenAcumOpsRecepcion# instancia de Existencias_Volumenes

            self.HoraRecepcionAcumulado = HoraRecepcionAcumulado

            self.VolumenAcumOpsEntrega = VolumenAcumOpsEntrega# instancia de Existencias_Volumenes

            self.HoraEntregaAcumulado = HoraEntregaAcumulado

            self.VolumenExistencias = VolumenExistencias# instancia de Existencias_Volumenes

            self.FechaYHoraEstaMedicion = FechaYHoraEstaMedicion
            self.FechaYHoraMedicionAnterior = FechaYHoraMedicionAnterior


class Existencias_Volumenes:
    def __init__(self,ValorNumerico,UM) -> None:
                self.ValorNumerico = ValorNumerico
                self.UM = UM


class Recepciones:
    def __init__(self,TotalRecepciones,
                     SumaVolumenRecepcion,
                     TotalDocumentos,
                     SumaCompras,
                     Recepcion) -> None:
            self.TotalRecepciones = TotalRecepciones
            self.SumaVolumenRecepcion = SumaVolumenRecepcion
            self.TotalDocumentos = TotalDocumentos
            self.SumaCompras =SumaCompras
            self.Recepcion = Recepcion #instancia de Recepcion_HIJO --->>Debe ser un arreglo de tipo RECEPCION
    
class Recepcion:#Descarga
        def __init__(self,NumeroDeRegistro,
                     TipoDeRegistro,
                     VolumenInicialTanque,
                     VolumenFinalTanque,
                     VolumenRecepcion,
                     Temperatura,
                     PresionAbsoluta,
                     FechaYHoraInicioRecepcion,
                     FechaYHoraFinalRecepcion,
                     Complemento):
            self.NumeroDeRegistro = NumeroDeRegistro
            self.TipoDeRegistro = TipoDeRegistro

            self.VolumenInicialTanque  = VolumenInicialTanque#Instancia de Recepcion_Volumen
            self.VolumenFinalTanque = VolumenFinalTanque#Instancia de Recepcion_Volumen
            self.VolumenRecepcion = VolumenRecepcion#Instancia de Recepcion_Volumen

            self.Temperatura = Temperatura
            self.PresionAbsoluta = PresionAbsoluta
            self.FechaYHoraInicioRecepcion = FechaYHoraInicioRecepcion
            self.FechaYHoraFinalRecepcion = FechaYHoraFinalRecepcion 

            self.Complemento = Complemento#Opcional

class Recepcion_Volumen:
        def __init__(self,ValorNumerico,UM) -> None:
                self.ValorNumerico = ValorNumerico
                self.UM = UM

class Recepcion_Volumen_Hijo:
        def __init__(self,ValorNumerico,UM) -> None:
                self.ValorNumerico = ValorNumerico
                self.UM = UM


class Entregas:
        def __init__(self,TotalEntregas,
                     SumaVolumenEntregado,
                     TotalDocumentos,
                     SumaVentas,
                     Entrega) -> None:
            self.TotalEntregas = TotalEntregas
            
            self.SumaVolumenEntregado = SumaVolumenEntregado #Instancia de Entregas_Volumen

            self.TotalDocumentos = TotalDocumentos
            self.SumaVentas = SumaVentas

            self.Entrega = Entrega #Instancia de Entrega_Hijo -->>Debe ser un arreglo

class Entregas_Volumen:
        def __init__(self,ValorNumerico,UM) -> None:
                self.ValorNumerico = ValorNumerico
                self.UM = UM

class Entrega:#Cargas
        def __init__(self,NumeroDeRegistro,
                    TipoDeRegistro,
                     VolumenInicialTanque,
                     VolumenFinalTanque,
                      VolumenEntregado,
                     Temperatura,
                      PresionAbsoluta,
                      FechaYHoraInicialEntrega,
                      FechaYHoraFinalEntrega,
                      Complemento ) -> None:
            self.NumeroDeRegistro = NumeroDeRegistro
            self.TipoDeRegistro = TipoDeRegistro

            self.VolumenInicialTanque = VolumenInicialTanque#Instancia de Entrega_Volumen
            self.VolumenFinalTanque = VolumenFinalTanque #Instancia de Entrega_Volumen
            self.VolumenEntregado = VolumenEntregado#Instancia de Entrega_Volumen

            self.Temperatura = Temperatura
            self.PresionAbsoluta = PresionAbsoluta
            self.FechaYHoraInicialEntrega = FechaYHoraInicialEntrega
            self.FechaYHoraFinalEntrega = FechaYHoraFinalEntrega
            self.Complemento = Complemento#Opcional

class Entrega_Volumen:
        def __init__(self,ValorNumerico,UM) -> None:
                self.ValorNumerico = ValorNumerico
                self.UM = UM


class Bitacora:
        def __init__(self,NumeroRegistro,
                    FechaYHoraEvento,
                     UsuarioResponsable,
                      TipoEvento,
                       DescripcionEvento,
                       IdentificacionComponenteAlarma) -> None:
            self.NumeroRegistro = NumeroRegistro
            self.FechaYHoraEvento =FechaYHoraEvento
            self.UsuarioResponsable = UsuarioResponsable
            self.TipoEvento =TipoEvento
            self.DescripcionEvento = DescripcionEvento
            self.IdentificacionComponenteAlarma =IdentificacionComponenteAlarma #Opcional


class ControlesVolumetricos:
    def __init__(self,Version,RfcContribuyente,RfcRepresnetanteLegal,RfcProveedor,RfcProveedores,Caracter,
                ClaveInstalacion,DescripcionInstalacion,
                Geolocalizacion,NumeroPozos,NumeroTanques,NumeroDuctosEntradaSalida,NumeroDuctosTransporteDistribucion,NumeroDispensarios,
               FechaYHoraCorte,Producto,Bitacora)-> None:
        self.Version = Version
        self.RfcContribuyente = RfcContribuyente
        self.RfcRepresnetanteLegal = RfcRepresnetanteLegal
        self.RfcProveedor = RfcProveedor #Se refiere al provedor de CV(software)

        self.RfcProveedores = Proveedores(RfcProveedores) #Instancia de Proveedores ,arreglo opcional
        
        self.Caracter = Caracter#Instancia de Caracter
        self.ClaveInstalacion = ClaveInstalacion
        self.DescripcionInstalacion = DescripcionInstalacion

        self.Geolocalizacion= Geolocalizacion #Instancia de Geolocalizacion 

        self.NumeroPozos = NumeroPozos
        self.NumeroTanques = NumeroTanques
        self.NumeroDuctosEntradaSalida = NumeroDuctosEntradaSalida
        self.NumeroDuctosTransporteDistribucion = NumeroDuctosTransporteDistribucion
        self.NumeroDispensarios = NumeroDispensarios
        self.FechaYHoraCorte = FechaYHoraCorte

    
        self.Producto = Producto #Clase complementaria de Producto


        self.Bitacora = Bitacora #Clase complementaria de Bitacora
        


        
    #def __str__(self):#Devuelve una representación en cadena de un objeto que es legible y útil para los humanos.
        

    #def __repr__(self):Devuelve una representación en cadena de un objeto que es útil para la depuración y puede ser usado para recrear el objeto (si es posible).
