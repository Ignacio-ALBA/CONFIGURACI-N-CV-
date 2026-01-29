import json
from jsonschema import validate, Draft7Validator
#pip install -U 'jsonschema<4.0'

# Definir el esquema JSON
schema ={
  "$schema": "https://dev.sat.gob.mx/docs/esquema-sat-json.pdf",
  "$id": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Diario.schema.json",
  "$version": "0.3.0",
  "type": "object",
  "description": "Es el elemento madre del archivo JSON.",
  "properties": {
    "Version": {
      "type": "string",
      "pattern": "^[0-9]+\\.[0-9]+$",
      "description": "Requerido para todos los contribuyentes, debe expresar la versión del programa informático que genera el archivo JSON."
    },
    "RfcContribuyente": {
      "$ref": "#/definitions/RFC",
      "description": "Requerido para todos los contribuyentes, para expresar su RFC. Puede ser de persona moral o física."
    },
    "RfcRepresentanteLegal": {
      "$ref": "#/definitions/RfcPersonaFisica",
      "description": "Condicional para todos los contribuyentes que sean persona moral, para expresar el RFC de su representante legal. El RFC deberá contener 13 caracteres al tratarse de una persona física."
    },
    "RfcProveedor": {
      "$ref": "#/definitions/RfcPersonaMoral",
      "description": "Requerido para todos los contribuyentes, para expresar el RFC del proveedor del programa informático para llevar controles volumétricos autorizado por el SAT. El RFC deberá contener 12 caracteres al tratarse de una persona moral."
    },
    "RfcProveedores": {
      "type": "array",
      "minItems": 1,
      "description": "Opcional para expresar el RFC de los proveedores de equipos, sistemas, programas o cualquier otro componente de los controles volumétricos. El RFC deberá contener 12 ó 13 caracteres. Este campo deberá repetirse por cada proveedor con que se cuente.",
      "items": {
        "$ref": "#/definitions/RFC",
        "description": "Opcional para expresar el RFC de los proveedores de equipos, sistemas, programas o cualquier otro componente de los controles volumétricos. El RFC deberá contener 12 ó 13 caracteres. Este campo deberá repetirse por cada proveedor con que se cuente."
      }
    },
    "Caracter": {
      "enum": ["contratista", "asignatario", "permisionario", "usuario"],
      "description": "Requerido para expresar el carácter con el que actúa para efectos regulatorios."
    },
    "ModalidadPermiso": {
      "type": "string",
      "pattern": "^PER([1-9]|[1-4][0-9]|5[0-6])$",
      "description": "Condicional cuando en el elemento ``Caracter\"{} se haya seleccionado ``permisionario\"{}, para expresar el tipo de permiso conforme a lo señalado en la sección \\ref{Claves} ``\\nameref{Claves}\"{}, subsección \\ref{Claves:Permiso} ``\\nameref{Claves:Permiso}\"{}."
    },
    "NumPermiso": {
      "type": "string",
      "description": "Condicional cuando en el elemento ``Caracter\"{} se haya seleccionado ``permisionario\"{} para expresar el número de permiso otorgado por la Comisión Reguladora de Energía o la Secretaría de Energía siguiendo el patrón asociado al permiso, conforme a la sección \\ref{Claves} ``\\nameref{Claves}\"{}, subsección \\ref{Claves:Permiso} ``\\nameref{Claves:Permiso}\"{}."
    },
    "NumContratoOAsignacion": {
      "type": "string",
      "minLength": 14,
      "maxLength": 24,
      "description": "Condicional cuando en el elemento ``Caracter\"{} se haya seleccionado ``contratista\"{} o ``asignatario\"{} para expresar el número de asignación otorgada por la Secretaría de Energía o el número de contrato celebrado con la Comisión Nacional de Hidrocarburos, según corresponda."
    },
    "InstalacionAlmacenGasNatural": {
      "type": "string",
      "minLength": 16,
      "maxLength": 250,
      "description": "Condicional cuando en el elemento “Caracter” se haya seleccionado ``usuario\"{}, para identificar de forma descriptiva la instalación."
    },
    "ClaveInstalacion": {
      "type": "string",
      "description": "Requerido para expresar la clave de identificación de la instalación o proceso donde deban instalarse sistemas de medición, conforme a la sección \\ref{Claves} ``\\nameref{Claves}\"{}, subsección \\ref{Claves:Instalacion} ``\\nameref{Claves:Instalacion}\"{}."
    },
    "DescripcionInstalacion": {
      "type": "string",
      "minLength": 5,
      "maxLength": 250,
      "description": "Requerido para describir la instalación o proceso donde deban instalarse sistemas de medición."
    },
    "Geolocalizacion": {
      "type": "array",
      "minItems": 1,
      "description": "Opcional, para registrar la ubicación geográfica (Latitud y Longitud) de la instalación expresada en Grados decimales (DD), con los elementos GeolocalizacionLatitud y GeolocalizacionLongitud. Para el caso de áreas Contractuales o Asignaciones se deberán indicar las coordenadas de cada vértice.",
      "items": {
        "$ref": "#/definitions/Geoloc",
        "description": "Par de coordenadas de geolocalización."
      }
    },
    "NumeroPozos": {
      "type": "integer",
      "minimum": 0,
      "description": "Requerido para expresar el número de pozos con los que cuenta. En caso de no tener debe manifestar 0."
    },
    "NumeroTanques": {
      "type": "integer",
      "minimum": 0,
      "description": "Requerido para expresar el número de tanques con los que cuenta o, en su caso, módulos. En caso de no tener debe manifestar 0."
    },
    "NumeroDuctosEntradaSalida": {
      "type": "integer",
      "minimum": 0,
      "description": "Requerido para expresar el número de ductos de entrada y salida a medios de almacenamiento o de carga y descarga a medios de transporte o distribución con los que cuenta. En caso de no tener debe manifestar 0."
    },
    "NumeroDuctosTransporteDistribucion": {
      "type": "integer",
      "minimum": 0,
      "description": "Requerido para expresar el número de ductos de transporte o distribución con los que cuenta. En caso de no tener debe manifestar 0."
    },
    "NumeroDispensarios": {
      "type": "integer",
      "minimum": 0,
      "description": "Requerido para expresar el número de dispensarios con los que cuenta. En caso de no tener debe manifestar 0."
    },
    "FechaYHoraCorte": {
      "type": "string",
      "format": "date-time",
      "description": "Requerido para expresar la fecha y hora que corresponde a la información que se reporta, deberá expresarse la hora en UTC con la indicación del huso horario yyyy-mm-ddThh:mm:ss+-hh:mm, de acuerdo con la especificación ISO 8601."
    },
    "Producto": {
      "type": "array",
      "minItems": 1,
      "description": "Este campo es una lista de Productos.",
      "items": {
        "type": "object",
        "description": "Objeto para describir un Producto.",
        "properties": {
          "ClaveProducto": {
            "enum": [
              "PR03",
              "PR07",
              "PR08",
              "PR09",
              "PR10",
              "PR11",
              "PR12",
              "PR13",
              "PR14",
              "PR15",
              "PR16",
              "PR17",
              "PR18",
              "PR19"
            ],
            "description": "Requerido para expresar la clave del producto conforme a lo señalado en la sección \\ref{Claves} ``\\nameref{Claves}\"{}, subsección \\ref{Claves:Producto} ``\\nameref{Claves:Producto}\"{}."
          },
          "ClaveSubProducto": {
            "type": "string",
            "pattern": "^SP([1-9]|[1-3][0-9]|4[0-8])$",
            "description": "Condicional cuando hayan seleccionado los productos PR03, PR07, PR08, PR09, PR11, PR13, PR15, PR16, PR17, PR18 u PR19, para expresar la clave del subproducto conforme a lo señalado en la sección \\ref{Claves} ``\\nameref{Claves}\"{}, subsección \\ref{Claves:Subproducto} ``\\nameref{Claves:Subproducto}\"{}."
          },
          "ComposOctanajeGasolina": {
            "type": "integer",
            "minimum": 87,
            "maximum": 130,
            "description": "Condicional en caso de que haya seleccionado el producto PR07. Deberá tener un valor mínimo de 87 y un máximo de 130."
          },
          "GasolinaConCombustibleNoFosil": {
            "type": "string",
            "enum": ["Sí", "No"],
            "description": "Condicional en caso de que haya seleccionado el producto PR07 para expresar si el producto contiene combustible no fósil."
          },
          "ComposDeCombustibleNoFosilEnGasolina": {
            "type": "integer",
            "minimum": 1,
            "maximum": 99,
            "description": "Condicional en caso de que haya declarado ``Sí\"{} en el elemento ``GasolinaConCombustibleNoFosil\"{}, para expresar el porcentaje de combustible no fósil contenido en el producto. Deberá tener un valor mínimo de 1 a 99."
          },
          "DieselConCombustibleNoFosil": {
            "type": "string",
            "enum": ["Sí", "No"],
            "description": "Condicional en caso de que haya seleccionado el producto PR03 para expresar si el producto contiene combustible no fósil."
          },
          "ComposDeCombustibleNoFosilEnDiesel": {
            "type": "integer",
            "minimum": 1,
            "maximum": 99,
            "description": "Condicional en caso de que haya declarado ``Sí\"{} en el elemento ``DieselConCombustibleNoFosil\"{}, para expresar el porcentaje de combustible no fósil contenido en el producto. Deberá tener un valor mínimo de 1 a 99."
          },
          "TurbosinaConCombustibleNoFosil": {
            "type": "string",
            "enum": ["Sí", "No"],
            "description": "Condicional en caso de que haya seleccionado el producto PR11 para expresar si el producto contiene combustible no fósil."
          },
          "ComposDeCombustibleNoFosilEnTurbosina": {
            "type": "integer",
            "minimum": 1,
            "maximum": 99,
            "description": "Condicional en caso de que haya declarado ``Sí\"{} en el elemento ``TurbosinaConCombustibleNoFosil\"{}, para expresar el porcentaje de combustible no fósil contenido en el producto. Deberá tener un valor mínimo de 1 a 99."
          },
          "ComposDePropanoEnGasLP": {
            "type": "number",
            "minimum": 0.01,
            "maximum": 99.99,
            "fractionDigits": 2,
            "description": "Condicional en caso de que haya seleccionado el producto PR12, para expresar el porcentaje normalizado de propano en el gas licuado de petróleo, conforme a los resultados del dictamen emitido por el proveedor del servicio de emisión de dictámenes que determinen el tipo de hidrocarburo o petrolífero de que se trate. Deberá tener un valor mínimo de 0.01 a 99.99."
          },
          "ComposDeButanoEnGasLP": {
            "type": "number",
            "minimum": 0.01,
            "maximum": 99.99,
            "fractionDigits": 2,
            "description": "Condicional en caso de que haya seleccionado el producto PR12, para expresar el porcentaje normalizado de butano en el gas licuado de petróleo, conforme a los resultados del dictamen emitido por el proveedor del servicio de emisión de dictámenes que determinen el tipo de hidrocarburo o petrolífero de que se trate. Deberá tener un valor mínimo de 0.01 a 99.99."
          },
          "DensidadDePetroleo": {
            "type": "number",
            "minimum": 0.1,
            "maximum": 80,
            "fractionDigits": 1,
            "description": "Condicional tratándose de sujetos que hayan manifestado ser ``contratista\"{} o ``asignatario\"{} en el elemento ``Caracter\"{}, en caso de que haya seleccionado el producto PR08, para expresar la densidad del petróleo, expresada en °API. Deberá tener un valor mínimo de 0.1 a 80.0."
          },
          "ComposDeAzufreEnPetroleo": {
            "type": "number",
            "minimum": 0.1,
            "maximum": 10,
            "fractionDigits": 1,
            "description": "Condicional tratándose de sujetos que hayan manifestado ser ``contratista\"{} o ``asignatario\"{} en el elemento ``Caracter\"{} en caso de que haya seleccionado el producto PR08, para expresar el porcentaje de azufre en el petróleo. Deberá tener un valor mínimo de 0.1 a 10.0."
          },
          "Otros": {
            "type": "string",
            "minLength": 1,
            "maxLength": 30,
            "description": "Condicional cuando se haya seleccionado el producto PR15, y el subproducto SP20 para expresar componentes diferentes a los productos señalados en el catálogo."
          },
          "MarcaComercial": {
            "type": "string",
            "minLength": 2,
            "maxLength": 200,
            "description": "Opcional para expresar la marca comercial de los petrolíferos."
          },
          "Marcaje": {
            "type": "string",
            "minLength": 2,
            "maxLength": 40,
            "description": "Opcional para expresar la sustancia química empleada como marcador."
          },
          "ConcentracionSustanciaMarcaje": {
            "type": "number",
            "minLength": 1,
            "maxLength": 1000,
            "description": "Condicional para expresar la concentración de la sustancia cuando se haya manifestado marcaje. Se mide en ppm. Deberá tener un valor mínimo de 1 y máximo de 1000."
          },
          "GasNaturalOCondensados": {
            "type": "array",
            "minItems": 2,
            "maxItems": 10,
            "description": "Condicional, tratándose de sujetos que hayan manifestado ``contratista\"{} o ``asignatario\"{} en Carácter, en caso de que haya seleccionado los productos PR09 o PR10 para registrar la información detallada de la composición del gas natural o de los condensados. La suma de la fracción molar de todos los componentes debe ser igual a 1.",
            "items": {
              "type": "object",
              "description": "Objeto para describir los productos gas natural o condensados.",
              "properties": {
                "ComposGasNaturalOCondensados": {
                  "type": "string",
                  "pattern": "^GNC(0[1-9]|10)$",
                  "description": "Requerido en caso de que haya seleccionado los productos PR09 o PR10, para expresar cada componente en la mezcla, conforme a lo señalado en la sección \\ref{Claves} ``\\nameref{Claves}\"{}, subsección \\ref{Claves:GNC} ``\\nameref{Claves:GNC}\"{}. Únicamente para quienes se hayan ostentado con el carácter de contratista o asignatario. Este campo deberá repetirse cuantos componentes tenga el gas natural o el condensado."
                },
                "FraccionMolar": {
                  "type": "number",
                  "minimum": 0,
                  "maximum": 0.999,
                  "fractionDigits": 3,
                  "description": "Requerido para expresar la fracción molar por cada componente expresado en ``ComposGasNaturalOCondensados\"{}.  Deberá tener un valor mínimo de 0 a 0.999 por cada componente de la mezcla. La suma de la fracción molar de todos los componentes debe ser igual a 1."
                },
                "PoderCalorifico": {
                  "type": "number",
                  "minimum": 0.001,
                  "maximum": 150000,
                  "description": "Requerido para expresar el poder calorífico por cada componente expresado en ``ComposGasNaturalOCondensados\"{}, expresado en BTU/pie cúbico para el gas natural y MMBTU tratándose de condensados."
                }
              },
              "required": [
                "ComposGasNaturalOCondensados",
                "FraccionMolar",
                "PoderCalorifico"
              ],
              "additionalProperties": False
            }
          },
          "Tanque": {
            "type": "array",
            "description": "Esta sección se debe declarar por cada uno de los tanques en caso de que hayan manifestado número de tanques mayor que cero en ``NumeroTanques\"{}.",
            "items": {
              "type": "object",
              "description": "Objeto para describir un Tanque.",
              "properties": {
                "ClaveIdentificacionTanque": {
                  "type": "string",
                  "pattern": "^(TQS|CTQ|MUL|ATQ|SMR|BTQ|VEA|CAS|STQ)-(ACA|AUP|ALM|ACL|ASN|ACO|BSP|BDE|CMN|CO[MN]|DEN|DIS|EMA|ESN|EDS|ESA|EXO|EXP|EXT|GSH|LON|RPO|MNA|PTA|PDD|PGN|RCN|REF|RGN|SIS|SFO|SDA|TDA|TDD|TR[EA]|TDP|USP)-[0-9]{4}$",
                  "description": "Requerido para expresar la clave de identificación de cada tanque o en su caso módulo, controlado por el contribuyente, conforme a la sección \\ref{Claves} ``\\nameref{Claves}\"{}, subsección \\ref{Claves:Permiso} ``\\nameref{Claves:Permiso}\"{}, subsubsección \\ref{Claves:Tanque} ``\\nameref{Claves:Tanque}\"{}."
                },
                "Localizaciony/oDescripcionTanque": {
                  "type": "string",
                  "minLength": 2,
                  "maxLength": 250,
                  "description": "Requerido para expresar la localización y/o descripción de cada tanque o, en su caso, modulo (ejemplo: terminal de almacenamiento pajaritos, tanque de gasolina Premium o crudo para exportación Dos Bocas capacidad de 20,000 barriles)."
                },
                "VigenciaCalibracionTanque": {
                  "type": "string",
                  "format": "date",
                  "description": "Requerido para expresar la vigencia de calibración de cada tanque, deberá expresarse yyyy-mm-dd, de acuerdo con la especificación ISO 8601."
                },
                "CapacidadTotalTanque": {
                  "$ref": "#/definitions/Volumen",
                  "description": "Requerido para expresar la capacidad que, respetando en todo momento los parámetros de seguridad y fiabilidad de la propia instalación (márgenes operacionales) y desde un punto de vista técnico, puede proporcionar la instalación (capacidad máxima de diseño), utilizando todos los equipos de la misma (cantidad expresada en litros tratándose de petrolíferos, pie cúbico tratándose de gas natural para contratistas y asignatarios, metro cúbico tratándose de gas natural en los demás casos, barril tratándose de petróleo y condensados)."
                },
                "CapacidadOperativaTanque": {
                  "$ref": "#/definitions/Volumen",
                  "description": "Requerido para expresar la capacidad que es susceptible de ser extraída de cada tanque (cantidad expresada en litros tratándose de petrolíferos, pie cúbico tratándose de gas natural para contratistas y asignatarios, metro cúbico tratándose de gas natural en los demás casos, barril tratándose de petróleo y condensados)."
                },
                "CapacidadUtilTanque": {
                  "$ref": "#/definitions/Volumen",
                  "description": "Requerido para expresar la capacidad que resulta de la ``CapacidadTotalTanque\"{} menos ``VolumenMinimoOperacion\"{}. No obstante, es posible que esta capacidad útil pueda verse reducida por otras limitaciones dependiendo de su integración en el conjunto del sistema de cada tanque (cantidad expresada en litros tratándose de petrolíferos, pie cúbico tratándose de gas natural para contratistas y asignatarios, metro cúbico tratándose de gas natural en los demás casos, barril tratándose de petróleo y condensados)."
                },
                "CapacidadFondajeTanque": {
                  "$ref": "#/definitions/Volumen",
                  "description": "Condicional para expresar la capacidad mínima de líquido de fondo que el tanque debe tener para que la extracción de líquidos mediante bombeo sea técnicamente factible (cantidad expresada en litros tratándose de petrolíferos, barril tratándose de petróleo y condensados), tratándose de cada tanque que contenga líquido."
                },
                "CapacidadGasTalon": {
                  "$ref": "#/definitions/Volumen",
                  "description": "Condicional para aquellos que hayan señalado la clave de producto PR09 para expresar el nivel mínimo operativo de llenado de los tanques que puedan almacenar gases."
                },
                "VolumenMinimoOperacion": {
                  "$ref": "#/definitions/Volumen",
                  "description": "Requerido para expresar el volumen por debajo del cual no puede utilizarse la instalación al no estar garantizada la fiabilidad y la seguridad operativa de los equipos y del propio tanque por cada tanque (cantidad expresada en litros tratándose de petrolíferos, pie cúbico tratándose de gas natural para contratistas y asignatarios, metro cúbico tratándose de gas natural en los demás casos, barril tratándose de petróleo y condensados)."
                },
                "EstadoTanque": {
                  "enum": ["O", "F"],
                  "description": "Requerido para indicar el estado de cada tanque. Deberá manifestar O - en operación, o en su caso F - fuera de operación."
                },
                "Medidores": {
                  "type": "array",
                  "minItems": 1,
                  "description": "Arreglo de medidores que se encuentren en el Tanque.",
                  "items": {
                    "type": "object",
                    "description": "Objeto para describir un medidor.",
                    "properties": {
                      "SistemaMedicionTanque": {
                        "type": "string",
                        "pattern": "^(SME|SMD-(ETA|SDA))-(TQS|CTQ|MUL|ATQ|SMR|BTQ|VEA|CAS|STQ)-(ACA|AUP|ALM|ACL|ASN|ACO|BSP|BDE|CMN|CO[MN]|DEN|DIS|EMA|ESN|EDS|ESA|EXO|EXP|EXT|GSH|LON|RPO|MNA|PTA|PDD|PGN|RCN|REF|RGN|SIS|SFO|SDA|TDA|TDD|TR[EA]|TDP|USP)-[0-9]{4}$",
                        "description": "Requerido para expresar la clave de identificación del sistema de medición instalado en cada tanque, conforme a la sección \\ref{Claves} ``\\nameref{Claves}\"{}, subsección \\ref{Claves:Medicion} ``\\nameref{Claves:Medicion}\"{}. Este campo deberá poder repetirse por cada medidor instalado en el tanque."
                      },
                      "LocalizODescripSistMedicionTanque": {
                        "type": "string",
                        "minLength": 2,
                        "maxLength": 250,
                        "description": "Requerido para expresar la localización y/o describir el sistema de medición manifestado en SistemaMedicionTanque, instalado en cada tanque. Este campo deberá poder repetirse por cada medidor instalado en el tanque, manifestado en SistemaMedicionTanque."
                      },
                      "VigenciaCalibracionSistMedicionTanque": {
                        "type": "string",
                        "format": "date",
                        "description": "Requerido para expresar la vigencia de calibración del sistema de medición de cada tanque, deberá expresarse yyyy-mm-dd, de acuerdo con la especificación ISO 8601. Este campo deberá poder repetirse por cada medidor instalado en el tanque."
                      },
                      "IncertidumbreMedicionSistMedicionTanque": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1,
                        "fractionDigits": 3,
                        "description": "Requerido para expresar la incertidumbre de la medición. Por ejemplo, para una incertidumbre del 1\\% se deberá ingresar 0.010. Este campo deberá poder repetirse por cada medidor instalado en el tanque."
                      }
                    },
                    "required": [
                      "SistemaMedicionTanque",
                      "LocalizODescripSistMedicionTanque",
                      "VigenciaCalibracionSistMedicionTanque",
                      "IncertidumbreMedicionSistMedicionTanque"
                    ],
                    "additionalProperties": False
                  }
                },
                "Existencias": {
                  "type": "object",
                  "description": "Objeto para describir las existencias.",
                  "properties": {
                    "VolumenExistenciasAnterior": {
                      "type": "number",
                      "minimum": -100000000000.0,
                      "maximum": 100000000000.0,
                      "fractionDigits": 3,
                      "description": "Requerido para expresar las existencias del día anterior n-1 (cantidad expresada en litros tratándose de petrolíferos, pie cúbico tratándose de gas natural para contratistas y asignatarios, metro cúbico tratándose de gas natural en los demás casos, barril tratándose de petróleo y condensados)."
                    },
                    "VolumenAcumOpsRecepcion": {
                      "$ref": "#/definitions/Volumen",
                      "description": "Requerido para expresar el volumen total de las operaciones de recepción realizadas en las 24 horas anteriores (cantidad expresada en litros tratándose de petrolíferos, pie cúbico tratándose de gas natural para contratistas y asignatarios, metro cúbico tratándose de gas natural en los demás casos, barril tratándose de petróleo y condensados)."
                    },
                    "HoraRecepcionAcumulado": {
                      "type": "string",
                      "pattern": "^([01][0-9]|2[0-3])(:[0-5][0-9]){2}[-|+]([01][0-9]|2[0-3])(:[0-5][0-9])$",
                      "description": "Requerido para expresar la hora en que se realizó el registro de volumen acumulado, deberá expresarse la hora en UTC, de acuerdo con la especificación ISO 8601 con la indicación del huso horario hh:mm:ss+-hh:mm."
                    },
                    "VolumenAcumOpsEntrega": {
                      "$ref": "#/definitions/Volumen",
                      "description": "Requerido para expresar el volumen total de las operaciones de entrega realizadas en las 24 horas anteriores (cantidad expresada en litros tratándose de petrolíferos, barril tratándose de petróleo y condensados, y metro cúbico tratándose de gas natural)."
                    },
                    "HoraEntregaAcumulado": {
                      "type": "string",
                      "pattern": "^([01][0-9]|2[0-3])(:[0-5][0-9]){2}[-|+]([01][0-9]|2[0-3])(:[0-5][0-9])$",
                      "description": "Requerido para expresar la hora en que se realizó el registro de volumen acumulado, deberá expresarse la hora en UTC, de acuerdo con la especificación ISO 8601 con la indicación del huso horario hh:mm:ss+-hh:mm."
                    },
                    "VolumenExistencias": {
                      "type": "number",
                      "minimum": -100000000000.0,
                      "maximum": 100000000000.0,
                      "fractionDigits": 3,
                      "description": "Requerido para expresar el resultado de sumar el ``VolumenExistenciasAnterior\"{} y el ``VolumenAcumOpRecepcion\"{} menos el ``VolumenAcumOpEntrega\"{} realizadas en las 24 horas anteriores (cantidad expresada en litros tratándose de petrolíferos, pie cúbico tratándose de gas natural para contratistas y asignatarios, metro cúbico tratándose de gas natural en los demás casos, barril tratándose de petróleo y condensados)."
                    },
                    "FechaYHoraEstaMedicion": {
                      "type": "string",
                      "format": "date-time",
                      "description": "Requerido para expresar la fecha y hora de esta medición. Deberá ser a la misma hora de la medición del día anterior y expresarse la hora en UTC con la indicación del huso horario yyyy-mm-ddThh:mm:ss+-hh:mm, de acuerdo con la especificación ISO 8601."
                    },
                    "FechaYHoraMedicionAnterior": {
                      "type": "string",
                      "format": "date-time",
                      "description": "Requerido para expresar la fecha y hora de la medición anterior, deberá expresarse la hora en UTC con la indicación del huso horario yyyy-mm-ddThh:mm:ss+-hh:mm, de acuerdo con la especificación ISO 8601."
                    }
                  },
                  "required": [
                    "VolumenExistenciasAnterior",
                    "VolumenAcumOpsRecepcion",
                    "HoraRecepcionAcumulado",
                    "VolumenAcumOpsEntrega",
                    "HoraEntregaAcumulado",
                    "VolumenExistencias",
                    "FechaYHoraEstaMedicion",
                    "FechaYHoraMedicionAnterior"
                  ],
                  "additionalProperties": False
                },
                "Recepciones": {
                  "type": "object",
                  "description": "Objeto para describir las recepciones.",
                  "properties": {
                    "TotalRecepciones": {
                      "type": "integer",
                      "minimum": 0,
                      "maximum": 200,
                      "description": "Requerido para expresar el total de recepciones en la estación de proceso, en la refinería, en la terminal de almacenamiento o área de almacenamiento para usos propios, en la instalación fija para recibir gas natural, en los ductos de transporte y distribución, en los medios de transporte o distribución distintos a ductos o en la estación de servicio."
                    },
                    "SumaVolumenRecepcion": {
                      "$ref": "#/definitions/Volumen",
                      "description": "Requerido para expresar la suma del volumen recibido por compras o por prestaciones de servicio o recepciones provenientes de la misma instalación producto de las actividades del asignatario, contratista o permisionario (cantidad expresada en litros tratándose de petrolíferos, pie cúbico tratándose de gas natural para contratistas y asignatarios, metro cúbico tratándose de gas natural en los demás casos, barril tratándose de petróleo y condensados)."
                    },
                    "TotalDocumentos": {
                      "type": "integer",
                      "minimum": 0,
                      "maximum": 200,
                      "description": "Requerido para expresar el total de documentos (complementos) que amparen las recepciones."
                    },
                    "SumaCompras": {
                      "type": "number",
                      "minimum": -9999999999.999,
                      "maximum": 9999999999.999,
                      "fractionDigits": 3,
                      "description": "Opcional para expresar la suma de los importes totales de las transacciones de compra."
                    },
                    "Recepcion": {
                      "type": "array",
                      "minItems": 1,
                      "description": "Esta sección se debe declarar por cada una de las recepciones en caso de que hayan manifestado total de recepciones mayor que cero en Recepciones.",
                      "items": {
                        "type": "object",
                        "description": "Objeto para describir una recepción.",
                        "properties": {
                          "NumeroDeRegistro": {
                            "type": "number",
                            "minimum": 1,
                            "maximum": 2000,
                            "description": "Requerido para expresar el número de registro único y consecutivo de cada recepción, generado por el programa informático."
                          },
                          "VolumenInicialTanque": {
                            "$ref": "#/definitions/Volumen",
                            "description": "Requerido para expresar el volumen inicial antes de la recepción del producto por operación (cantidad expresada en litros tratándose de petrolíferos, pie cúbico tratándose de gas natural para contratistas y asignatarios, metro cúbico tratándose de gas natural en los demás casos, barril tratándose de petróleo y condensados)."
                          },
                          "VolumenFinalTanque": {
                            "type": "number",
                            "minimum": -100000000000.0,
                            "maximum": 100000000000.0,
                            "fractionDigits": 3,
                            "description": "Requerido para expresar el volumen final después de la recepción del producto por operación (cantidad expresada en litros tratándose de petrolíferos, pie cúbico tratándose de gas natural para contratistas y asignatarios, metro cúbico tratándose de gas natural en los demás casos, barril tratándose de petróleo y condensados)."
                          },
                          "VolumenRecepcion": {
                            "$ref": "#/definitions/Volumen",
                            "description": "Requerido para expresar el volumen final después de la recepción del producto por operación (cantidad expresada en litros tratándose de petrolíferos, pie cúbico tratándose de gas natural para contratistas y asignatarios, metro cúbico tratándose de gas natural en los demás casos, barril tratándose de petróleo y condensados)."
                          },
                          "Temperatura": {
                            "type": "number",
                            "minimum": -170,
                            "maximum": 100,
                            "fractionDigits": 3,
                            "description": "Requerido para expresar la temperatura del tanque a la que se realizó la cuantificación y/o totalización de la masa o volumen del hidrocarburo o petrolífero de que se trate, tomando en consideración las condiciones de referencia. La unidad de medida son grados Celsius."
                          },
                          "PresionAbsoluta": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 200.0,
                            "fractionDigits": 3,
                            "description": "Requerido para expresar la presión absoluta a la que se realizó la cuantificación y/o totalización de la masa o volumen del hidrocarburo o petrolífero de que se trate, tomando en consideración las condiciones de referencia. La unidad de medida es kPa."
                          },
                          "FechaYHoraInicioRecepcion": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Requerido para expresar la fecha y hora inicial de cada operación de recepción, deberá expresarse la hora en UTC con la indicación del huso horario yyyy-mm-ddThh:mm:ss+-hh:mm, de acuerdo con la especificación ISO 8601."
                          },
                          "FechaYHoraFinalRecepcion": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Requerido para expresar la fecha y hora final de cada operación de recepción, deberá expresarse la hora en UTC con la indicación del huso horario yyyy-mm-ddThh:mm:ss+-hh:mm, de acuerdo con la especificación ISO 8601."
                          },
                          "Complemento": {
                            "type": "object",
                            "descripcion": "Este elemento debe contener el complemento correspondiente a la actividad del obligado.",
                            "anyOf": [
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Almacenamiento.schema.json"
                              },
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Comercializacion.schema.json"
                              },
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-CDLR.schema.json"
                              },
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Disribucion.schema.json"
                              },
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Extraccion.json"
                              },
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Expendio.schema.json"
                              },
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Refinacion.schema.json"
                              },
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Transporte.schema.json"
                              }
                            ]
                          }
                        },
                        "required": [
                          "NumeroDeRegistro",
                          "VolumenInicialTanque",
                          "VolumenFinalTanque",
                          "VolumenRecepcion",
                          "Temperatura",
                          "PresionAbsoluta",
                          "FechaYHoraInicioRecepcion",
                          "FechaYHoraFinalRecepcion"
                        ],
                        "additionalProperties": False
                      }
                    }
                  },
                  "required": [
                    "TotalRecepciones",
                    "SumaVolumenRecepcion",
                    "TotalDocumentos"
                  ],
                  "additionalProperties": False,
                  "if": {
                    "properties": {
                      "TotalRecepciones": {
                        "type": "integer",
                        "minimum": 1
                      }
                    }
                  },
                  "then": {
                    "required": ["Recepcion"]
                  }
                },
                "Entregas": {
                  "type": "object",
                  "description": "Objeto para describir las entregas.",
                  "properties": {
                    "TotalEntregas": {
                      "type": "integer",
                      "minimum": 0,
                      "maximum": 100000000000,
                      "description": "Requerido para expresar el número total de registros de entrega por ventas, autoconsumo o por prestaciones de servicio."
                    },
                    "SumaVolumenEntregado": {
                      "$ref": "#/definitions/Volumen",
                      "description": "Requerido para expresar la suma del volumen entregado por ventas, autoconsumo o por prestaciones de servicio (cantidad expresada en litros tratándose de petrolíferos, pie cúbico tratándose de gas natural para contratistas y asignatarios, metro cúbico tratándose de gas natural en los demás casos, barril tratándose de petróleo y condensados)."
                    },
                    "TotalDocumentos": {
                      "type": "integer",
                      "minimum": 0,
                      "maximum": 200000000000,
                      "description": "Requerido para expresar el total de documentos (complementos) que amparen las entregas por ventas, autoconsumo o por prestaciones de servicio."
                    },
                    "SumaVentas": {
                      "type": "number",
                      "minimum": -9999999999.999,
                      "maximum": 9999999999.999,
                      "fractionDigits": 3,
                      "description": "Opcional para expresar la suma de los importes totales de las transacciones de venta."
                    },
                    "Entrega": {
                      "type": "array",
                      "minItems": 1,
                      "description": "Esta sección se debe declarar por cada una de las entregas en caso de que hayan manifestado total de entregas mayor que cero en Entregas.",
                      "items": {
                        "type": "object",
                        "description": "Objeto para describir una Entrega.",
                        "properties": {
                          "NumeroDeRegistro": {
                            "type": "number",
                            "minimum": 1,
                            "maximum": 200000000000,
                            "description": "Requerido para expresar el número de registro único y consecutivo de cada entrega por ventas, autoconsumo o por prestaciones de servicio, generado por el programa informático."
                          },
                          "VolumenInicialTanque": {
                            "$ref": "#/definitions/Volumen",
                            "description": "Requerido para expresar el volumen inicial antes de la recepción del producto por operación (cantidad expresada en litros tratándose de petrolíferos, pie cúbico tratándose de gas natural para contratistas y asignatarios, metro cúbico tratándose de gas natural en los demás casos, barril tratándose de petróleo y condensados)."
                          },
                          "VolumenFinalTanque": {
                            "type": "number",
                            "minimum": -100000000000.0,
                            "maximum": 100000000000.0,
                            "fractionDigits": 3,
                            "description": "Requerido para expresar el volumen final después de la entrega del producto por cada operación de venta, entrega, suministro o exportación (cantidad expresada en litros tratándose de petrolíferos, pie cúbico tratándose de gas natural para contratistas y asignatarios, metro cúbico tratándose de gas natural en los demás casos, barril tratándose de petróleo y condensados)."
                          },
                          "VolumenEntregado": {
                            "$ref": "#/definitions/Volumen",
                            "description": "Requerido para expresar el volumen entregado por cada operación de venta, entrega, suministro o exportación, a partir de la medición anterior (cantidad expresada en litros tratándose de petrolíferos, pie cúbico tratándose de gas natural para contratistas y asignatarios, metro cúbico tratándose de gas natural en los demás casos, barril tratándose de petróleo y condensados)."
                          },
                          "Temperatura": {
                            "type": "number",
                            "minimum": -170,
                            "maximum": 100,
                            "fractionDigits": 3,
                            "description": "Requerido para expresar la temperatura del tanque a la que se realizó la cuantificación y/o totalización de la masa o volumen del hidrocarburo o petrolífero de que se trate, tomando en consideración las condiciones de referencia. La unidad de medida es grados Celsius."
                          },
                          "PresionAbsoluta": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 200.0,
                            "fractionDigits": 3,
                            "description": "Requerido para expresar la presión absoluta a la que se realizó la cuantificación y/o totalización de la masa o volumen del hidrocarburo o petrolífero de que se trate, tomando en consideración las condiciones de referencia. La unidad de medida es kPa."
                          },
                          "FechaYHoraInicialEntrega": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Requerido para expresar la fecha y hora inicial de cada operación de entrega, deberá expresarse la hora en UTC con la indicación del huso horario yyyy-mm-ddThh:mm:ss+-hh:mm, de acuerdo con la especificación ISO 8601."
                          },
                          "FechaYHoraFinalEntrega": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Requerido para expresar la fecha y hora final de cada operación de entrega, deberá expresarse la hora en UTC con la indicación del huso horario yyyy-mm-ddThh:mm:ss+-hh:mm, de acuerdo con la especificación ISO 8601."
                          },
                          "Complemento": {
                            "description": "Este elemento debe contener el complemento correspondiente a la actividad del obligado.",
                            "anyOf": [
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Almacenamiento.schema.json"
                              },
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Comercializacion.schema.json"
                              },
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-CDLR.schema.json"
                              },
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Disribucion.schema.json"
                              },
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Extraccion.json"
                              },
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Expendio.schema.json"
                              },
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Refinacion.schema.json"
                              },
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Transporte.schema.json"
                              }
                            ]
                          }
                        },
                        "required": [
                          "NumeroDeRegistro",
                          "VolumenInicialTanque",
                          "VolumenFinalTanque",
                          "VolumenEntregado",
                          "Temperatura",
                          "PresionAbsoluta",
                          "FechaYHoraInicialEntrega",
                          "FechaYHoraFinalEntrega"
                        ],
                        "additionalProperties": False
                      }
                    }
                  },
                  "required": [
                    "TotalEntregas",
                    "SumaVolumenEntregado",
                    "TotalDocumentos"
                  ],
                  "additionalProperties": False,
                  "if": {
                    "properties": {
                      "TotalEntregas": {
                        "type": "integer",
                        "minimum": 1
                      }
                    }
                  },
                  "then": {
                    "required": ["Entrega"]
                  }
                }
              },
              "required": [
                "ClaveIdentificacionTanque",
                "Localizaciony/oDescripcionTanque",
                "VigenciaCalibracionTanque",
                "CapacidadTotalTanque",
                "CapacidadOperativaTanque",
                "CapacidadUtilTanque",
                "VolumenMinimoOperacion",
                "EstadoTanque",
                "Medidores",
                "Existencias",
                "Recepciones",
                "Entregas"
              ],
              "additionalProperties": False
            }
          },
          "Ducto": {
            "type": "array",
            "description": "Esta sección se debe declarar por cada uno de los ductos en caso de que hayan manifestado número de ductos mayor que cero en ``NumeroDuctosEntradaSalida\"{} y ``NumeroDuctosTransporteDistribucion\"{}.",
            "items": {
              "type": "object",
              "description": "Objeto para describir un ducto.",
              "properties": {
                "ClaveIdentificacionDucto": {
                  "type": "string",
                  "pattern": "^DUC-(TRA|DIS|CAR|DES|ETA|SDA)-[0-9]{4}$",
                  "description": "Requerido para expresar la clave de identificación de los ductos de recolección, y ductos de entrada y salida de las baterías de separación en el área contractual, ductos de entrada y salida de las plantas de compresión, descompresión, licuefacción y regasificación, ductos de entrada y salida de la refinería, ductos de transporte y distribución, ductos de entrada y salida a los medios de almacenamiento, conforme a la sección \\ref{Claves} ``\\nameref{Claves}\"{}, subsección \\ref{Claves:Instalacion} ``\\nameref{Claves:Instalacion}\"{}, subsubsección \\ref{Claves:Ducto} ``\\nameref{Claves:Ducto}\"{}.."
                },
                "DescripcionDucto": {
                  "type": "string",
                  "minLength": 2,
                  "maxLength": 250,
                  "description": "Requerido para expresar la localización y/o descripción de cada ducto (ejemplo: llegada a centro procesador de gas). Tratándose de ductos de distribución deberá describirse el sistema."
                },
                "DiametroDucto": {
                  "type": "number",
                  "minimum": 1.0,
                  "maximum": 200.0,
                  "fractionDigits": 3,
                  "description": "Requerido para expresar el diámetro nominal, en pulgadas. Deberá tener un valor mínimo de 1 a 200."
                },
                "Medidores": {
                  "type": "array",
                  "minItems": 1,
                  "items": {
                    "type": "object",
                    "description": "Objeto para describir un medidor.",
                    "properties": {
                      "SistemaMedicionDucto": {
                        "type": "string",
                        "pattern": "^(SMD-DUC-(TRA|DIS|CAR|DES|ETA|SDA))-[0-9]{4}$",
                        "description": "Requerido para expresar la clave de identificación de cada sistema de medición del ducto. Este campo deberá poder repetirse por cada medidor instalado en el ducto, conforme a la sección \\ref{Claves} ``\\nameref{Claves}\"{}, subsección \\ref{Claves:Medicion} ``\\nameref{Claves:Medicion}\"{}."
                      },
                      "LocalizODescripSistMedicionDucto": {
                        "type": "string",
                        "minLength": 2,
                        "maxLength": 250,
                        "description": "Requerido para expresar la localización y/o descripción del sistema de medición de cada ducto. Este campo deberá poder repetirse por cada medidor instalado en el ducto, manifestado en SistemaMedicionDucto."
                      },
                      "VigenciaCalibracionSistMedicionDucto": {
                        "type": "string",
                        "format": "date",
                        "description": "Requerido para expresar la vigencia de calibración del sistema de medición de cada ducto, deberá expresarse yyyy-mm-dd, de acuerdo con la especificación ISO 8601. Este campo deberá poder repetirse por cada medidor instalado en el ducto, manifestado en SistemaMedicionDucto."
                      },
                      "IncertidumbreMedicionSistMedicionDucto": {
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "fractionDigits": 3,
                        "description": "Requerido para expresar la incertidumbre de la medición. Por ejemplo, para una incertidumbre del 1\\% se deberá ingresar 0.010. Este campo deberá poder repetirse por cada medidor instalado en el ducto, manifestado en SistemaMedicionDucto."
                      }
                    },
                    "required": [
                      "SistemaMedicionDucto",
                      "LocalizODescripSistMedicionDucto",
                      "VigenciaCalibracionSistMedicionDucto",
                      "IncertidumbreMedicionSistMedicionDucto"
                    ],
                    "additionalProperties": False
                  }
                },
                "CapacidadGasTalon": {
                  "$ref": "#/definitions/Volumen",
                  "description": "Condicional para aquellos que hayan señalado la clave de producto PR09 para expresar el nivel mínimo operativo de las redes de transporte del sistema gasista. Esta cantidad corresponderá al nivel mínimo de llenado de los gasoductos de transporte, traducida en días de utilización."
                },
                "Recepciones": {
                  "type": "object",
                  "description": "Objeto para describir las Recepciones.",
                  "properties": {
                    "TotalRecepciones": {
                      "type": "integer",
                      "minimum": 0,
                      "maximum": 100,
                      "description": "Requerido para expresar el total de recepciones en el cabezal de pozo o ducto de recolección, la estación de proceso, en la refinería, en la terminal de almacenamiento o área de almacenamiento para usos propios, en la instalación fija para recibir gas natural, en los ductos de transporte y distribución, en los medios de transporte o distribución distintos a ductos o en la estación de servicio."
                    },
                    "SumaVolumenRecepcion": {
                      "$ref": "#/definitions/Volumen",
                      "description": "Requerido para expresar la suma del volumen recibido por compras o por prestaciones de servicio (cantidad expresada en litros tratándose de petrolíferos, pie cúbico tratándose de gas natural para contratistas y asignatarios, metro cúbico tratándose de gas natural en los demás casos, barril tratándose de petróleo y condensados)."
                    },
                    "TotalDocumentos": {
                      "type": "integer",
                      "minimum": 0,
                      "maximum": 200,
                      "description": "Requerido para expresar el total de documentos que amparen las recepciones."
                    },
                    "SumaCompras": {
                      "type": "number",
                      "minimum": -9999999999.999,
                      "maximum": 9999999999.999,
                      "fractionDigits": 3,
                      "description": "Opcional para expresar la suma de los importes totales de las transacciones de compra."
                    },
                    "Recepcion": {
                      "type": "array",
                      "minItems": 1,
                      "description": "Esta sección se debe declarar por cada una de las recepciones en caso de que hayan manifestado total de recepciones mayor que cero en Recepciones.",
                      "items": {
                        "type": "object",
                        "description": "Objeto para describir una Recepción.",
                        "properties": {
                          "NumeroDeRegistro": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 2000,
                            "description": "Requerido para expresar el número de registro único y consecutivo de cada recepción, generado por el programa informático."
                          },
                          "VolumenPuntoEntrada": {
                            "$ref": "#/definitions/Volumen",
                            "description": "Requerido para expresar el volumen a la entrada del ducto antes de la recepción del producto por cada operación, puede considerar el volumen de gas de empaque (cantidad expresada en litros tratándose de petrolíferos, pie cúbico tratándose de gas natural para contratistas y asignatarios, metro cúbico tratándose de gas natural en los demás casos, barril tratándose de petróleo y condensados)."
                          },
                          "VolumenRecepcion": {
                            "$ref": "#/definitions/Volumen",
                            "description": "Requerido para expresar la cantidad de producto recibido por operación de compra, recepción, recolección o importación (cantidad expresada en litros tratándose de petrolíferos, pie cúbico tratándose de gas natural para contratistas y asignatarios, metro cúbico tratándose de gas natural en los demás casos, barril tratándose de petróleo y condensados)."
                          },
                          "Temperatura": {
                            "type": "number",
                            "minimum": -170,
                            "maximum": 100,
                            "fractionDigits": 3,
                            "description": "Requerido para expresar la temperatura a la que se realizó la cuantificación y/o totalización de la masa o volumen del hidrocarburo o petrolífero de que se trate, tomando en consideración las condiciones de referencia. La unidad de medida es grados Celsius."
                          },
                          "PresionAbsoluta": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 200,
                            "fractionDigits": 3,
                            "description": "Requerido para expresar la presión absoluta a la que se realizó la cuantificación y/o totalización de la masa o volumen del hidrocarburo o petrolífero de que se trate, tomando en consideración las condiciones de referencia. La unidad de medida es kPa."
                          },
                          "FechaYHoraInicioRecepcion": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Requerido para expresar la fecha y hora inicial de cada operación de recepción en el día, deberá expresarse la hora en UTC con la indicación del huso horario yyyy-mm-ddThh:mm:ss+-hh:mm, de acuerdo con la especificación ISO 8601."
                          },
                          "FechaYHoraFinalRecepcion": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Requerido para expresar la fecha y hora final de cada operación de recepción, deberá expresarse la hora en UTC con la indicación del huso horario yyyy-mm-ddThh:mm:ss+-hh:mm, de acuerdo con la especificación ISO 8601."
                          },
                          "Complemento": {
                            "description": "Este elemento debe contener el complemento correspondiente a la actividad del obligado.",
                            "anyOf": [
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Almacenamiento.schema.json"
                              },
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Comercializacion.schema.json"
                              },
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-CDLR.schema.json"
                              },
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Disribucion.schema.json"
                              },
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Extraccion.json"
                              },
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Expendio.schema.json"
                              },
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Refinacion.schema.json"
                              },
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Transporte.schema.json"
                              }
                            ]
                          }
                        },
                        "required": [
                          "NumeroDeRegistro",
                          "VolumenPuntoEntrada",
                          "VolumenRecepcion",
                          "Temperatura",
                          "PresionAbsoluta",
                          "FechaYHoraInicioRecepcion",
                          "FechaYHoraFinalRecepcion"
                        ]
                      }
                    }
                  },
                  "required": [
                    "TotalRecepciones",
                    "SumaVolumenRecepcion",
                    "TotalDocumentos"
                  ],
                  "additionalProperties": False,
                  "if": {
                    "properties": {
                      "TotalRecepciones": {
                        "type": "integer",
                        "minimum": 1
                      }
                    }
                  },
                  "then": {
                    "required": ["Recepcion"]
                  }
                },
                "Entregas": {
                  "type": "object",
                  "description": "Objeto para describir las Entregas.",
                  "properties": {
                    "TotalEntregas": {
                      "type": "integer",
                      "minimum": 0,
                      "maximum": 100000,
                      "description": "Requerido para expresar el número total de registros de entrega por ventas, autoconsumo o por prestaciones de servicio para todos los ductos de entrada y salida a medios de almacenamiento, ductos de carga y descarga de medios de transporte."
                    },
                    "SumaVolumenEntregado": {
                      "$ref": "#/definitions/Volumen",
                      "description": "Requerido para expresar la suma del volumen entregado por ventas, autoconsumo o por prestaciones de servicio, tratándose de contribuyentes que hayan manifestado permiso de expendio al público, deberán señalar el volumen del totalizador (cantidad expresada en litros tratándose de petrolíferos, pie cúbico tratándose de gas natural para contratistas y asignatarios, metro cúbico tratándose de gas natural en los demás casos, barril tratándose de petróleo y condensados)."
                    },
                    "TotalDocumentos": {
                      "type": "integer",
                      "minimum": 0,
                      "maximum": 200,
                      "description": "Requerido para expresar el total de documentos que amparen las entregas por ventas, autoconsumo o por prestaciones de servicio."
                    },
                    "SumaVentas": {
                      "type": "number",
                      "minimum": -9999999999.999,
                      "maximum": 9999999999.999,
                      "fractionDigits": 3,
                      "description": "Opcional para expresar la suma de los importes totales de las transacciones de venta."
                    },
                    "Entrega": {
                      "type": "array",
                      "description": "Esta sección se debe declarar por cada una de las entregas en caso de que hayan manifestado total de entregas mayor que cero en Entregas.",
                      "items": {
                        "type": "object",
                        "description": "Objeto para describir una Entrega.",
                        "properties": {
                          "NumeroDeRegistro": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 2000,
                            "description": "Requerido para expresar el número de registro único y consecutivo de cada entrega por ventas, autoconsumo o por prestaciones de servicio, generado por el programa informático."
                          },
                          "VolumenPuntoSalida": {
                            "$ref": "#/definitions/Volumen",
                            "description": "Requerido para expresar el volumen a la salida del ducto antes de la entrega del producto por cada operación de venta, entrega, suministro o exportación, puede considerar el volumen de gas de empaque (cantidad expresada en litros tratándose de petrolíferos, pie cúbico tratándose de gas natural para contratistas y asignatarios, metro cúbico tratándose de gas natural en los demás casos, barril tratándose de petróleo y condensados)."
                          },
                          "VolumenEntregado": {
                            "$ref": "#/definitions/Volumen",
                            "description": "Requerido para expresar el volumen entregado por cada operación de venta, entrega, suministro o exportación(cantidad expresada en litros tratándose de petrolíferos, pie cúbico tratándose de gas natural para contratistas y asignatarios, metro cúbico tratándose de gas natural en los demás casos, barril tratándose de petróleo y condensados)."
                          },
                          "Temperatura": {
                            "type": "number",
                            "minimum": -170,
                            "maximum": 100,
                            "fractionDigits": 3,
                            "description": "Requerido para expresar la temperatura a la que se realizó la cuantificación y/o totalización de la masa o volumen del hidrocarburo o petrolífero de que se trate, tomando en consideración las condiciones de referencia. La unidad de medida es grados Celsius."
                          },
                          "PresionAbsoluta": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 200,
                            "fractionDigits": 3,
                            "description": "Requerido para expresar la presión absoluta a la que se realizó la cuantificación y/o totalización de la masa o volumen del hidrocarburo o petrolífero de que se trate tomando en consideración las condiciones de referencia. La unidad de medida es kPa."
                          },
                          "FechaYHoraInicialEntrega": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Requerido para expresar la fecha y hora inicial de cada operación de entrega en el día, deberá expresarse la hora en UTC con la indicación del huso horario yyyy-mm-ddThh:mm:ss+-hh:mm, de acuerdo con la especificación ISO 8601."
                          },
                          "FechaYHoraFinalEntrega": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Requerido para expresar la fecha y hora final de cada operación de entrega, deberá expresarse la hora en UTC con la indicación del huso horario yyyy-mm-ddThh:mm:ss+-hh:mm, de acuerdo con la especificación ISO 8601."
                          },
                          "Complemento": {
                            "descripcion": "Este elemento debe contener el complemento correspondiente a la actividad del obligado.",
                            "anyOf": [
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Almacenamiento.schema.json"
                              },
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Comercializacion.schema.json"
                              },
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-CDLR.schema.json"
                              },
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Disribucion.schema.json"
                              },
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Extraccion.json"
                              },
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Expendio.schema.json"
                              },
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Refinacion.schema.json"
                              },
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Transporte.schema.json"
                              }
                            ]
                          }
                        },
                        "required": [
                          "NumeroDeRegistro",
                          "VolumenPuntoSalida",
                          "VolumenEntregado",
                          "Temperatura",
                          "PresionAbsoluta",
                          "FechaYHoraInicialEntrega",
                          "FechaYHoraFinalEntrega"
                        ]
                      }
                    }
                  },
                  "required": [
                    "TotalEntregas",
                    "SumaVolumenEntregado",
                    "TotalDocumentos"
                  ],
                  "additionalProperties": False,
                  "if": {
                    "properties": {
                      "TotalEntregas": {
                        "type": "integer",
                        "minimum": 1
                      }
                    }
                  },
                  "then": {
                    "required": ["Entrega"]
                  }
                }
              },
              "required": [
                "ClaveIdentificacionDucto",
                "DescripcionDucto",
                "DiametroDucto",
                "Medidores",
                "Recepciones",
                "Entregas"
              ]
            }
          },
          "Pozo": {
            "type": "array",
            "description": "Esta sección se debe declarar por cada uno de los pozos en caso de que hayan manifestado número de pozos mayor que cero en ``NumeroPozos\"{}.",
            "items": {
              "type": "object",
              "description": "Objeto para describir un Pozo.",
              "properties": {
                "ClavePozo": {
                  "type": "string",
                  "pattern": "^POZ-[0-9A-Za-z]{1,40}-[0-9]{4}[A-Z]{3}$",
                  "description": "Requerido para expresar la clave de identificación de cada pozo registrado ante la CNH, conforme a la sección \\ref{Claves} ``\\nameref{Claves}\"{}, subsección \\ref{Claves:Instalacion} ``\\nameref{Claves:Instalacion}\"{}, subsubsección \\ref{Claves:Pozo} ``\\nameref{Claves:Pozo}\"{}."
                },
                "DescripcionPozo": {
                  "type": "string",
                  "minLength": 2,
                  "maxLength": 250,
                  "description": "Requerido para expresar la localización y/o descripción de cada cabezal de pozo conforme Planes de Exploración y Desarrollo para la Extracción de Hidrocarburos aprobados por la CNH."
                },
                "Medidores": {
                  "type": "array",
                  "minItems": 1,
                  "description": "Arreglo de medidores para los pozos.",
                  "items": {
                    "type": "object",
                    "description": "Objeto para describir un medidor.",
                    "properties": {
                      "SistemaMedicionPozo": {
                        "type": "string",
                        "pattern": "^SMD-POZ-[0-9A-Za-z]{1,40}-[0-9]{4}[A-Z]{3}$",
                        "description": "Requerido para expresar la clave de identificación del sistema de medición instalado en cada cabezal de pozo, conforme a la sección \\ref{Claves} ``\\nameref{Claves}\"{}, subsección \\ref{Claves:Medicion} ``\\nameref{Claves:Medicion}\"{}. Este campo deberá poder repetirse por cada medidor instalado en el pozo."
                      },
                      "LocalizODescripSistMedicionPozo": {
                        "type": "string",
                        "minLength": 2,
                        "maxLength": 250,
                        "description": "Requerido para expresar la localización y/o descripción del sistema de medición de cada cabezal de pozo. Este campo deberá poder repetirse por cada medidor instalado en el pozo, manifestado en SistemaMedicionPozo."
                      },
                      "VigenciaCalibracionSistMedicionPozo": {
                        "type": "string",
                        "format": "date",
                        "description": "Requerido para expresar la vigencia de calibración del sistema de medición de cada cabezal de pozo, deberá expresarse yyyy-mm-dd, de acuerdo con la especificación ISO 8601. Este campo deberá poder repetirse por cada medidor instalado en el pozo, manifestado en SistemaMedicionPozo."
                      },
                      "IncertidumbreMedicionSistMedicionPozo": {
                        "type": "number",
                        "minimum": 0.001,
                        "maximum": 1.0,
                        "fractionDigits": 3,
                        "description": "Requerido para expresar la incertidumbre de la medición. Por ejemplo, para una incertidumbre del 1\\% se deberá ingresar 0.010. Este campo deberá poder repetirse por cada medidor instalado en el pozo, manifestado en SistemaMedicionPozo."
                      }
                    },
                    "required": [
                      "SistemaMedicionPozo",
                      "LocalizODescripSistMedicionPozo",
                      "VigenciaCalibracionSistMedicionPozo",
                      "IncertidumbreMedicionSistMedicionPozo"
                    ],
                    "additionalProperties": False
                  }
                },
                "Recepciones": {
                  "type": "object",
                  "description": "Objeto para describir las recepciones.",
                  "properties": {
                    "TotalRecepciones": {
                      "type": "integer",
                      "minimum": 0,
                      "maximum": 1000,
                      "description": "Requerido para expresar el total de recepciones (por ejemplo reinyecciones) en el cabezal de pozo o ducto de recolección."
                    },
                    "SumaVolumenRecepcion": {
                      "$ref": "#/definitions/Volumen",
                      "description": "Requerido para expresar la suma del volumen reinyectado en el pozo (pie cúbico tratándose de gas natural, barril tratándose de petróleo y condensados)."
                    },
                    "TotalDocumentos": {
                      "type": "integer",
                      "minimum": 0,
                      "maximum": 100,
                      "description": "Requerido para expresar el total de documentos que amparen las recepciones."
                    },
                    "SumaCompras": {
                      "type": "number",
                      "minimum": -9999999999.999,
                      "maximum": 9999999999.999,
                      "fractionDigits": 3,
                      "description": "Opcional para expresar la suma de los importes totales de las transacciones de compra."
                    },
                    "Recepcion": {
                      "type": "array",
                      "minItems": 1,
                      "description": "Esta sección se debe declarar por cada una de las recepciones en caso de que hayan manifestado total de recepciones mayor que cero en Recepciones.",
                      "items": {
                        "type": "object",
                        "description": "Objeto para describir una recepción.",
                        "properties": {
                          "NumeroDeRegistro": {
                            "type": "number",
                            "minimum": 1,
                            "maximum": 2000,
                            "description": "Requerido para expresar el número de registro único y consecutivo de cada recepción, generado por el programa informático."
                          },
                          "VolumenRecepcion": {
                            "$ref": "#/definitions/Volumen",
                            "description": "Requerido para expresar la cantidad de producto inyectado (pie cúbico tratándose de gas natural, barril tratándose de petróleo y condensados)."
                          },
                          "Temperatura": {
                            "type": "number",
                            "minimum": -170,
                            "maximum": 100,
                            "fractionDigits": 3,
                            "description": "Requerido para expresar la temperatura a la que se realizó la cuantificación y/o totalización de la masa o volumen del hidrocarburo, tomando en consideración las condiciones de referencia. La unidad de medida es grados Celsius."
                          },
                          "PresionAbsoluta": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 200,
                            "fractionDigits": 3,
                            "description": "Requerido para expresar la presión absoluta a la que se realizó la cuantificación y/o totalización de la masa o volumen del hidrocarburo, tomando en consideración las condiciones de referencia. La unidad de medida es kPa."
                          },
                          "FechaYHoraInicioRecepcion": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Requerido para expresar la fecha y hora inicial de cada operación de recepción en el día, deberá expresarse la hora en UTC con la indicación del huso horario yyyy-mm-ddThh:mm:ss+-hh:mm, de acuerdo con la especificación ISO 8601."
                          },
                          "FechaYHoraFinalRecepcion": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Requerido para expresar la fecha y hora final de cada operación de recepción, deberá expresarse la hora en UTC con la indicación del huso horario yyyy-mm-ddThh:mm:ss+-hh:mm, de acuerdo con la especificación ISO 8601."
                          },
                          "Complemento": {
                            "description": "Este elemento debe contener el complemento correspondiente a la actividad del obligado.",
                            "anyOf": [
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Almacenamiento.schema.json"
                              },
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Comercializacion.schema.json"
                              },
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-CDLR.schema.json"
                              },
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Disribucion.schema.json"
                              },
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Extraccion.json"
                              },
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Expendio.schema.json"
                              },
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Refinacion.schema.json"
                              },
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Transporte.schema.json"
                              }
                            ]
                          }
                        },
                        "required": [
                          "NumeroDeRegistro",
                          "VolumenRecepcion",
                          "Temperatura",
                          "PresionAbsoluta",
                          "FechaYHoraInicioRecepcion",
                          "FechaYHoraFinalRecepcion"
                        ]
                      }
                    }
                  },
                  "required": [
                    "TotalRecepciones",
                    "SumaVolumenRecepcion",
                    "TotalDocumentos"
                  ],
                  "additionalProperties": False,
                  "if": {
                    "properties": {
                      "TotalRecepciones": { "type": "integer", "minimum": 1 }
                    }
                  },
                  "then": { "required": ["Recepcion"] }
                },
                "Entregas": {
                  "type": "object",
                  "description": "Objeto para describir las entregas.",
                  "properties": {
                    "TotalEntregas": {
                      "type": "integer",
                      "minimum": 0,
                      "maximum": 99,
                      "description": "Requerido para expresar el número total de registros de los hidrocarburos producidos."
                    },
                    "SumaVolumenEntregado": {
                      "$ref": "#/definitions/Volumen",
                      "description": "Requerido para expresar la suma del volumen producido de hidrocarburos (cantidad expresada en pie cúbico tratándose de gas natural, barril tratándose de petróleo y condensados)."
                    },
                    "TotalDocumentos": {
                      "type": "integer",
                      "minimum": 0,
                      "maximum": 200,
                      "description": "Requerido para expresar el total de documentos (complementos) que amparen las entregas por ventas, autoconsumo o por prestaciones de servicio."
                    },
                    "SumaVentas": {
                      "type": "number",
                      "minimum": -9999999999.999,
                      "maximum": 9999999999.999,
                      "fractionDigits": 3,
                      "description": "Opcional para expresar la suma de los importes totales de las transacciones de venta."
                    },
                    "Entrega": {
                      "type": "array",
                      "description": "Esta sección se debe declarar por cada una de las entregas en caso de que hayan manifestado total de entregas mayor que cero en Entregas.",
                      "items": {
                        "type": "object",
                        "description": "Objeto para describir una Entrega.",
                        "properties": {
                          "NumeroDeRegistro": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 2000,
                            "description": "Requerido para expresar el número de registro único y consecutivo de cada entrega por ventas, autoconsumo o por prestaciones de servicio, generado por el programa informático."
                          },
                          "VolumenEntregado": {
                            "$ref": "#/definitions/Volumen",
                            "description": "Requerido para expresar el volumen producido (cantidad expresada en pie cúbico tratándose de gas natural, barril tratándose de petróleo y condensados)."
                          },
                          "Temperatura": {
                            "type": "number",
                            "minimum": -170,
                            "maximum": 100,
                            "fractionDigits": 3,
                            "description": "Requerido para expresar la temperatura a la que se realizó la cuantificación y/o totalización de la masa o volumen del hidrocarburo, tomando en consideración las condiciones de referencia. La unidad de medida es grados Celsius."
                          },
                          "PresionAbsoluta": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 200,
                            "fractionDigits": 3,
                            "description": "Requerido para expresar la presión absoluta a la que se realizó la cuantificación y/o totalización de la masa o volumen del hidrocarburo, tomando en consideración las condiciones de referencia. La unidad de medida es kPa."
                          },
                          "FechaYHoraInicioEntrega": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Requerido para expresar la fecha y hora inicial de cada operación de entrega en el día o en su caso la hora a la que se toma la medición diaria, deberá expresarse la hora en UTC con la indicación del huso horario yyyy-mm-ddThh:mm:ss+-hh:mm de acuerdo con la especificación ISO 8601."
                          },
                          "FechaYHoraFinalEntrega": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Requerido para expresar la fecha y hora final de cada operación de entrega, deberá expresarse la hora en UTC con la indicación del huso horario yyyy-mm-ddThh:mm:ss+-hh:mm, de acuerdo con la especificación ISO 8601."
                          },
                          "Complemento": {
                            "description": "Este elemento debe contener el complemento correspondiente a la actividad del obligado.",
                            "anyOf": [
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Almacenamiento.schema.json"
                              },
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Comercializacion.schema.json"
                              },
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-CDLR.schema.json"
                              },
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Disribucion.schema.json"
                              },
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Extraccion.json"
                              },
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Expendio.schema.json"
                              },
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Refinacion.schema.json"
                              },
                              {
                                "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Transporte.schema.json"
                              }
                            ]
                          }
                        },
                        "required": [
                          "NumeroDeRegistro",
                          "VolumenEntregado",
                          "Temperatura",
                          "PresionAbsoluta",
                          "FechaYHoraInicioEntrega",
                          "FechaYHoraFinalEntrega"
                        ]
                      }
                    }
                  },
                  "required": [
                    "TotalEntregas",
                    "SumaVolumenEntregado",
                    "TotalDocumentos"
                  ],
                  "additionalProperties": False,
                  "if": {
                    "properties": {
                      "TotalEntregas": {
                        "type": "integer",
                        "minimum": 1
                      }
                    }
                  },
                  "then": {
                    "required": ["Entrega"]
                  }
                }
              },
              "required": ["ClavePozo", "DescripcionPozo"]
            }
          },
          "Dispensario": {
            "type": "array",
            "description": "Esta sección se debe declarar por cada uno de los dispensarios en caso de que hayan manifestado número de dispensarios mayor que cero en ``NumeroDispensarios\"{}.",
            "items": {
              "type": "object",
              "description": "Objeto para describir un Dispensario.",
              "properties": {
                "ClaveDispensario": {
                  "type": "string",
                  "pattern": "^DISP-[0-9]{4}$",
                  "description": "Requerido para expresar la clave de identificación de cada dispensario, controlado por el contribuyente, conforme a la sección \\ref{Claves} ``\\nameref{Claves}\"{}, subsección \\ref{Claves:Instalacion} ``\\nameref{Claves:Instalacion}\"{}, subsubsección \\ref{Claves:Dispensario} ``\\nameref{Claves:Dispensario}\"{}."
                },
                "Medidores": {
                  "type": "array",
                  "description": "Lista de medidores.",
                  "minItems": 1,
                  "items": {
                    "type": "object",
                    "description": "Objeto para describir los medidores.",
                    "properties": {
                      "SistemaMedicionDispensario": {
                        "type": "string",
                        "pattern": "^SMD-DISP-[0-9]{4}$",
                        "minLength": 8,
                        "maxLength": 30,
                        "description": "Requerido para expresar la clave de identificación del sistema de medición instalado en cada dispensario, es necesario manifestar los totalizadores (acumulado e instantáneo) conforme a la sección \\ref{Claves} ``\\nameref{Claves}\"{}, subsección \\ref{Claves:Medicion} ``\\nameref{Claves:Medicion}\"{}. Este campo deberá poder repetirse por cada medidor instalado en el dispensario."
                      },
                      "LocalizODescripSistMedicionDispensario": {
                        "type": "string",
                        "minLength": 2,
                        "maxLength": 250,
                        "description": "Requerido para expresar la localización y/o describir el sistema de medición instalado en cada dispensario. Este campo deberá poder repetirse por cada medidor instalado en el dispensario, incluidos los totalizadores (acumulado e instantáneo), manifestado en SistemaMedicionDispensario."
                      },
                      "VigenciaCalibracionSistMedicionDispensario": {
                        "type": "string",
                        "format": "date",
                        "description": "Requerido para expresar la vigencia de calibración de cada dispensario, deberá expresarse yyyy-mm-dd, de acuerdo con la especificación ISO 8601. Este campo deberá poder repetirse por cada medidor instalado en el dispensario, manifestado en SistemaMedicionDispensario."
                      },
                      "IncertidumbreMedicionSistMedicionDispensario": {
                        "type": "number",
                        "minimum": 0.001,
                        "maximum": 1,
                        "fractionDigits": 3,
                        "description": "Requerido para expresar la incertidumbre de la medición. Por ejemplo, para una incertidumbre del 1\\% se deberá ingresar 0.010. Este campo deberá poder repetirse por cada medidor instalado en el dispensario, manifestado en SistemaMedicionDispensario."
                      }
                    },
                    "required": [
                      "SistemaMedicionDispensario",
                      "LocalizODescripSistMedicionDispensario",
                      "VigenciaCalibracionSistMedicionDispensario",
                      "IncertidumbreMedicionSistMedicionDispensario"
                    ],
                    "additionalProperties": False
                  }
                },
                "Manguera": {
                  "type": "array",
                  "minItems": 1,
                  "description": "Esta sección se debe declarar por cada manguera de cada dispensario manifestado en el elemento anterior Dispensario.",
                  "items": {
                    "type": "object",
                    "description": "Objeto para describir una manguera.",
                    "properties": {
                      "IdentificadorManguera": {
                        "type": "string",
                        "pattern": "^DISP-[0-9]{4}-MGA-[0-9]{4}$",
                        "description": "Requerido para expresar el número identificador de la manguera, conforme a la sección \\ref{Claves} ``\\nameref{Claves}\"{}, subsección \\ref{Claves:Instalacion} ``\\nameref{Claves:Instalacion}\"{}, subsubsección \\ref{Claves:Manguera} ``\\nameref{Claves:Manguera}\"{}."
                      },
                      "Entregas": {
                        "type": "object",
                        "description": "Objeto para describir las Entregas.",
                        "properties": {
                          "TotalEntregas": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 100000000000,
                            "description": "Requerido para expresar el número total de registros de entrega por ventas o autoconsumo."
                          },
                          "SumaVolumenEntregado": {
                            "$ref": "#/definitions/Volumen",
                            "description": "Requerido para expresar la suma del volumen entregado por ventas y autoconsumo (cantidad expresada en litros tratándose de petrolíferos)."
                          },
                          "TotalDocumentos": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 200000000000,
                            "description": "Requerido para expresar el total de documentos (complementos) que amparen las entregas por ventas o autoconsumo."
                          },
                          "SumaVentas": {
                            "type": "number",
                            "minimum": -9999999999.999,
                            "maximum": 9999999999.999,
                            "fractionDigits": 3,
                            "description": "Opcional para expresar la suma de los importes totales de las transacciones de venta."
                          },
                          "Entrega": {
                            "type": "array",
                            "minItems": 1,
                            "description": "Esta sección se debe declarar por cada una de las entregas en caso de que hayan manifestado total de entregas mayor que cero en Entregas.",
                            "items": {
                              "type": "object",
                              "description": "Objeto para describir una Entrega.",
                              "properties": {
                                "NumeroDeRegistro": {
                                  "type": "integer",
                                  "minimum": 1,
                                  "maximum": 2000,
                                  "description": "Requerido para expresar el número de registro único y consecutivo de cada entrega por ventas o autoconsumo, generado por el programa informático."
                                },
                                "TipoDeRegistro": {
                                  "enum": ["D", "E", "J", "A", "N", "C"],
                                  "description": "Requerido para expresar el tipo de registro por transacción de venta. Deberán señalar ``D\"{} tratándose de ventas, ``E\"{} tratándose de entregas por prestaciones de servicio, ``J\"{} en el caso de jarreos realizados por la Procuraduría Federal del Consumidor, la CRE o la autoridad competente, UVAS o laboratorios móviles, ``A\"{} tratándose de auto-jarreos y ``N\"{} tratándose de producto en consignación, ``C\"{} tratándose de autoconsumo. Únicamente para quienes se hayan ostentado con el carácter de permisionario de expendio de petrolíferos."
                                },
                                "VolumenEntregadoTotalizadorAcum": {
                                  "$ref": "#/definitions/Volumen",
                                  "description": "Requerido para expresar el volumen entregado, que resulta de la suma de cada operación o despacho de combustible; se refiere al volumen del totalizador acumulado por día(cantidad expresada en litros tratándose de petrolíferos)."
                                },
                                "VolumenEntregadoTotalizadorInsta": {
                                  "$ref": "#/definitions/Volumen",
                                  "description": "Requerido para expresar el volumen entregado por cada operación o despacho de combustible; se refiere al volumen del totalizador instantáneo (cantidad expresada en litros tratándose de petrolíferos)."
                                },
                                "PrecioVentaTotalizadorInsta": {
                                  "type": "number",
                                  "minimum": 0.0,
                                  "maximum": 1000000,
                                  "fractionDigits": 3,
                                  "description": "Opcional para expresar el precio de venta en pesos por cada despacho de combustible, registrado en el totalizador instantáneo, tratándose de registros de venta."
                                },
                                "FechaYHoraEntrega": {
                                  "type": "string",
                                  "format": "date-time",
                                  "description": "Requerido para expresar la hora de cada operación de entrega o despacho de combustible en el día; tratándose de contribuyentes que hayan manifestado permiso de expendio al público, deberán señalar la hora del totalizador instantáneo, deberá expresarse la hora en UTC con la indicación del huso horario yyyy-mm-ddThh:mm:ss+-hh:mm, de acuerdo con la especificación ISO 8601."
                                },
                                "Complemento": {
                                  "descripcion": "Este elemento debe contener el complemento correspondiente a la actividad del obligado.",
                                  "anyOf": [
                                    {
                                      "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Almacenamiento.schema.json"
                                    },
                                    {
                                      "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Comercializacion.schema.json"
                                    },
                                    {
                                      "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-CDLR.schema.json"
                                    },
                                    {
                                      "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Disribucion.schema.json"
                                    },
                                    {
                                      "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Extraccion.json"
                                    },
                                    {
                                      "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Expendio.schema.json"
                                    },
                                    {
                                      "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Refinacion.schema.json"
                                    },
                                    {
                                      "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Transporte.schema.json"
                                    }
                                  ]
                                }
                              },
                              "required": [
                                "NumeroDeRegistro",
                                "TipoDeRegistro",
                                "VolumenEntregadoTotalizadorAcum",
                                "VolumenEntregadoTotalizadorInsta",
                                "FechaYHoraEntrega"
                              ],
                              "additionalProperties": False
                            }
                          }
                        },
                        "required": [
                          "TotalEntregas",
                          "SumaVolumenEntregado",
                          "TotalDocumentos"
                        ],
                        "additionalProperties": False,
                        "if": {
                          "properties": {
                            "TotalEntregas": {
                              "type": "integer",
                              "minimum": 1
                            }
                          }
                        },
                        "then": {
                          "required": ["Entrega"]
                        }
                      }
                    },
                    "required": ["IdentificadorManguera"],
                    "additionalProperties": False
                  }
                }
              },
              "required": ["ClaveDispensario", "Medidores", "Manguera"]
            }
          }
        },
        "required": ["ClaveProducto"],
        "additionalProperties": False,
        "allOf": [
          {
            "if": {
              "properties": {
                "ClaveProducto": {
                  "const": "PR09"
                }
              },
              "required": ["Ducto"]
            },
            "then": {
              "properties": {
                "Ducto": {
                  "type": "array",
                  "items": {
                    "type": "object",
                    "required": ["CapacidadGasTalon"]
                  }
                }
              }
            }
          },
          {
            "if": {
              "properties": {
                "ClaveProducto": {
                  "enum": [
                    "PR03",
                    "PR07",
                    "PR08",
                    "PR09",
                    "PR11",
                    "PR13",
                    "PR15",
                    "PR16",
                    "PR17",
                    "PR18",
                    "PR19"
                  ]
                }
              }
            },
            "then": {
              "required": ["ClaveSubProducto"]
            }
          },
          {
            "if": {
              "properties": {
                "ClaveProducto": {
                  "const": "PR03"
                }
              }
            },
            "then": {
              "properties": {
                "ClaveSubProducto": {
                  "enum": ["SP18", "SP19", "SP22", "SP23", "SP24", "SP25"]
                }
              },
              "required": ["DieselConCombustibleNoFosil"]
            }
          },
          {
            "if": {
              "properties": {
                "ClaveProducto": {
                  "const": "PR07"
                }
              }
            },
            "then": {
              "properties": {
                "ClaveSubProducto": {
                  "enum": ["SP16", "SP17"]
                }
              },
              "required": [
                "ComposOctanajeGasolina",
                "GasolinaConCombustibleNoFosil"
              ]
            }
          },
          {
            "if": {
              "properties": {
                "ClaveProducto": {
                  "const": "PR08"
                }
              }
            },
            "then": {
              "properties": {
                "ClaveSubProducto": {
                  "type": "string",
                  "pattern": "^SP([1-9]|1[0-5])$"
                }
              }
            }
          },
          {
            "if": {
              "properties": {
                "ClaveProducto": {
                  "const": "PR09"
                }
              }
            },
            "then": {
              "properties": {
                "ClaveSubProducto": {
                  "enum": [
                    "SP27",
                    "SP28",
                    "SP29",
                    "SP37",
                    "SP38",
                    "SP41",
                    "SP42",
                    "SP43",
                    "SP44",
                    "SP47"
                  ]
                }
              }
            }
          },
          {
            "if": {
              "properties": {
                "ClaveProducto": {
                  "const": "PR11"
                }
              }
            },
            "then": {
              "properties": {
                "ClaveSubProducto": {
                  "enum": ["SP34", "SP35"]
                }
              },
              "required": ["TurbosinaConCombustibleNoFosil"]
            }
          },
          {
            "if": {
              "properties": {
                "ClaveProducto": {
                  "const": "PR12"
                }
              }
            },
            "then": {
              "required": ["ComposDePropanoEnGasLP", "ComposDeButanoEnGasLP"]
            }
          },
          {
            "if": {
              "properties": {
                "ClaveProducto": {
                  "const": "PR13"
                }
              }
            },
            "then": {
              "properties": {
                "ClaveSubProducto": {
                  "enum": ["SP30", "SP31", "SP32", "SP33"]
                }
              }
            }
          },
          {
            "if": {
              "properties": {
                "ClaveProducto": {
                  "const": "PR15"
                }
              }
            },
            "then": {
              "properties": {
                "ClaveSubProducto": {
                  "enum": ["SP20", "SP21", "SP36", "SP39", "SP40"]
                }
              }
            }
          },
          {
            "if": {
              "properties": {
                "ClaveProducto": {
                  "const": "PR16"
                }
              }
            },
            "then": {
              "properties": {
                "ClaveSubProducto": {
                  "const": "SP48"
                }
              }
            }
          },
          {
            "if": {
              "properties": {
                "ClaveProducto": {
                  "const": "PR17"
                }
              }
            },
            "then": {
              "properties": {
                "ClaveSubProducto": {
                  "enum": ["SP45", "SP46"]
                }
              }
            }
          },
          {
            "if": {
              "properties": {
                "ClaveProducto": {
                  "const": "PR18"
                }
              }
            },
            "then": {
              "properties": {
                "ClaveSubProducto": {
                  "const": "SP26"
                }
              }
            }
          },
          {
            "if": {
              "properties": {
                "ClaveProducto": {
                  "const": "PR19"
                }
              }
            },
            "then": {
              "properties": {
                "ClaveSubProducto": {
                  "const": "SP42"
                }
              }
            }
          },
          {
            "if": {
              "properties": {
                "GasolinaConCombustibleNoFosil": {
                  "const": "Sí"
                }
              }
            },
            "then": {
              "additionalRequired": ["ComposDeCombustibleNoFosilEnGasolina"]
            }
          },
          {
            "if": {
              "properties": {
                "DieselConCombustibleNoFosil": {
                  "const": "Sí"
                }
              }
            },
            "then": {
              "additionalRequired": ["ComposDeCombustibleNoFosilEnDiesel"]
            }
          },
          {
            "if": {
              "properties": {
                "TurbosinaConCombustibleNoFosil": {
                  "const": "Sí"
                }
              }
            },
            "then": {
              "additionalRequired": ["ComposDeCombustibleNoFosilEnTurbosina"]
            }
          },
          {
            "if": {
              "properties": {
                "ClaveSubProducto": {
                  "const": "SP20"
                }
              }
            },
            "then": {
              "additionalRequired": ["Otros"]
            }
          },
          {
            "if": {
              "required": ["Marcaje"]
            },
            "then": {
              "additionalRequired": ["ConcentracionSustanciaMarcaje"]
            }
          }
        ]
      }
    },
    "Bitacora": {
      "type": "array",
      "description": "Esta sección se debe declarar con los datos de todos los eventos que se hayan, así como las alarmas que éstos hayan generado.",
      "items": {
        "type": "object",
        "description": "Objeto para describir un evento de la bitácora.",
        "properties": {
          "NumeroRegistro": {
            "type": "integer",
            "minimum": 0,
            "maximum": 1000,
            "description": "Requerido para expresar el número de registro, único y consecutivo del evento."
          },
          "FechaYHoraEvento": {
            "type": "string",
            "format": "date-time",
            "description": "Requerido para expresar la fecha y hora del evento, deberá expresarse la hora en UTC con la indicación del huso horario yyyy-mm-ddThh:mm:ss+-hh:mm, de acuerdo con la especificación ISO 8601."
          },
          "UsuarioResponsable": {
            "type": "string",
            "minLength": 1,
            "maxLength": 1000,
            "description": "Condicional tratándose de registros que no se generen automáticamente, para expresar el usuario responsable de registrar el evento."
          },
          "TipoEvento": {
            "type": "integer",
            "minimum": 1,
            "maximum": 21,
            "description": "Requerido para expresar el tipo de evento conforme a la siguiente clasificación: 1) administración del sistema, 2) eventos de la UCC, 3) eventos relacionados a los programas informáticos, 4) eventos de comunicación, 5) operaciones cotidianas, 6) verificaciones realizadas por la autoridad fiscal o por proveedores autorizados por el SAT, 7) exista una diferencia de más de 0.5\\% tratándose de Hidrocarburos y Petrolíferos líquidos o de 1\\% tratándose de Hidrocarburos y Petrolíferos gaseosos, en el volumen final del periodo, obtenido de sumar al volumen inicial en dicho periodo, las recepciones de producto y restar las entregas de producto, incluyendo las pérdidas por proceso, 8) el volumen de existencias registrado al corte del día, es igual al registrado en el corte del día anterior y existen registros de entradas o salidas en el corte del día, 9) el volumen de existencias registrado por cada tipo de Hidrocarburo o Petrolífero y sistema de medición es menor a cero, 10) el volumen de existencias registrado en el corte del día varía con respecto al corte del día anterior y no existen registros de entradas o salidas en el corte del día, 11) el volumen de salidas en un lapso de veinticuatro horas es mayor al volumen de entradas del mismo lapso más el volumen de existencias del corte del día anterior, 12) calibración no vigente, 13) intento de alteración de cualquier registro, 14) registros incompletos o duplicados, 15) problemas de comunicación, 16) falla del medio de almacenamiento, 17) falla en la red de comunicación, 18) falla de energía, 19) error en la transmisión de información, 20) rechazos de inicio de sesión, 21) paro de emergencia."
          },
          "DescripcionEvento": {
            "type": "string",
            "minLength": 2,
            "maxLength": 250,
            "description": "Requerido para expresar la descripción del evento de que se trate."
          },
          "IdentificacionComponenteAlarma": {
            "type": "string",
            "minLength": 2,
            "maxLength": 250,
            "description": "Condicional cuando se haya seleccionado 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21 en TipoEvento, para identificar el componente que originó la alarma (Canal de comunicación, dispensarios, sistemas de medición)."
          }
        },
        "required": [
          "NumeroRegistro",
          "FechaYHoraEvento",
          "TipoEvento",
          "DescripcionEvento"
        ],
        "additionalProperties": False,
        "allOf": [
          {
            "if": {
              "properties": {
                "TipoEvento": {
                  "type": "integer",
                  "minimum": 7,
                  "maximum": 21
                }
              }
            },
            "then": {
              "required": ["IdentificacionComponenteAlarma"]
            }
          }
        ]
      }
    }
  },
  "required": [
    "Version",
    "RfcContribuyente",
    "RfcProveedor",
    "Caracter",
    "Producto",
    "ClaveInstalacion",
    "DescripcionInstalacion",
    "NumeroPozos",
    "NumeroTanques",
    "NumeroDuctosEntradaSalida",
    "NumeroDuctosTransporteDistribucion",
    "NumeroDispensarios",
    "FechaYHoraCorte",
    "Bitacora"
  ],
  "allOf": [
    {
      "if": {
        "properties": {
          "RfcContribuyente": {
            "type": "string",
            "pattern": "^([A-ZÑ]|\\&){3}[0-9]{2}(0[1-9]|1[0-2])([12][0-9]|0[1-9]|3[01])[A-Z0-9]{3}$"
          }
        }
      },
      "then": {
        "required": ["RfcRepresentanteLegal"]
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "enum": ["contratista", "asignatario"]
          }
        }
      },
      "then": {
        "required": ["NumContratoOAsignacion"]
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "enum": ["contratista", "asignatario"]
          },
          "Producto": {
            "type": "array",
            "items": {
              "properties": {
                "ClaveProducto": {
                  "enum": ["PR09", "PR10"]
                }
              }
            }
          }
        }
      },
      "then": {
        "properties": {
          "Producto": {
            "type": "array",
            "items": {
              "required": ["GasNaturalOCondensados"]
            }
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "enum": ["usuario", "permisionario"]
          }
        }
      },
      "then": {
        "properties": {
          "ClaveInstalacion": {
            "type": "string",
            "pattern": "^(ACA|AUP|ALM|ACL|ASN|ACO|BSP|BDE|CMN|CO[MN]|DEN|DIS|EMA|ESN|EDS|ESA|EXO|EXP|EXT|GSH|LON|RPO|MNA|PTA|PDD|PGN|RCN|REF|RGN|SIS|SFO|SDA|TDA|TDD|TR[EA]|TDP|USP)-[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "enum": ["contratista", "asignatario"]
          }
        }
      },
      "then": {
        "properties": {
          "ClaveInstalacion": {
            "type": "string",
            "pattern": "^(ACL|ASN)-(TRE|MNA)-[a-zA-Z0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "enum": ["contratista", "asignatario"]
          },
          "Producto": {
            "type": "array",
            "items": {
              "properties": {
                "ClaveProducto": {
                  "const": "PR08"
                }
              }
            }
          }
        }
      },
      "then": {
        "properties": {
          "Producto": {
            "type": "array",
            "items": {
              "required": ["DensidadDePetroleo", "ComposDeAzufreEnPetroleo"]
            }
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "usuario"
          }
        }
      },
      "then": {
        "required": ["InstalacionAlmacenGasNatural"]
      }
    },
    {
      "if": {
        "properties": {
          "NumeroTanques": {
            "type": "integer",
            "minimum": 1
          }
        }
      },
      "then": {
        "properties": {
          "Producto": {
            "type": "array",
            "contains": [
              {
                "type": "object",
                "properties": {
                  "Tanque": {
                    "type": "array",
                    "minItems": 1
                  }
                },
                "required": ["Tanque"]
              }
            ]
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "NumeroPozos": {
            "type": "integer",
            "minimum": 1
          }
        }
      },
      "then": {
        "properties": {
          "Producto": {
            "type": "array",
            "contains": [
              {
                "type": "object",
                "properties": {
                  "Pozo": {
                    "type": "array",
                    "minItems": 1
                  }
                },
                "required": ["Pozo"]
              }
            ]
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "NumeroDuctosTransporteDistribucion": {
            "type": "integer",
            "minimum": 1
          }
        }
      },
      "then": {
        "properties": {
          "Producto": {
            "type": "array",
            "contains": [
              {
                "type": "object",
                "properties": {
                  "Ducto": {
                    "type": "array",
                    "minItems": 1
                  }
                },
                "required": ["Ducto"]
              }
            ]
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "NumeroDuctosEntradaSalida": {
            "type": "integer",
            "minimum": 1
          }
        }
      },
      "then": {
        "properties": {
          "Producto": {
            "type": "array",
            "contains": [
              {
                "type": "object",
                "properties": {
                  "Ducto": {
                    "type": "array",
                    "minItems": 1
                  }
                },
                "required": ["Ducto"]
              }
            ]
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "NumeroDispensarios": {
            "type": "integer",
            "minimum": 1
          }
        }
      },
      "then": {
        "properties": {
          "Producto": {
            "type": "array",
            "contains": [
              {
                "type": "object",
                "properties": {
                  "Dispensario": {
                    "type": "array",
                    "minItems": 1
                  }
                },
                "required": ["Dispensario"]
              }
            ]
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          }
        }
      },
      "then": {
        "required": ["ModalidadPermiso"]
      },
      "else": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "[0-9A-Z/\\-]{14,28}"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "enum": ["PER1", "PER6"]
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^H/[0-9]{1,5}/COM/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER2"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^PL/[0-9]{1,5}/EXP/ES/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER3"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^PL/[0-9]{1,5}/EXP/ES/MM/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER4"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^PL/[0-9]{1,5}/EXP/ESA/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER5"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^PL/[0-9]{1,5}/DIS/OM/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER7"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^PL/[0-9]{1,5}/TRA/OM/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER8"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^PL/[0-9]{1,5}/TRA/DUC/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER9"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^PL/[0-9]{1,5}/TRA/TM/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER10"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^PQ/[0-9]{1,5}/TRA/DUC/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER11"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^PL/[0-9]{1,5}/ALM/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER12"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^PQ/[0-9]{1,5}/ALM/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER13"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^PL/[0-9]{1,5}/ALM/AE/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER14"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^PL/[0-9]{1,5}/EXP/AE/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER15"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^G/[0-9]{1,5}/ALM/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER16"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^P/[0-9]{1,5}/ALM/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER17"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^G/[0-9]{1,5}/COM/GN/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER18"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^G/[0-9]{1,5}/COM/PETRO/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER19"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^G/[0-9]{1,5}/COM/CEE/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER20"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^G/[0-9]{1,5}/COMP/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER21"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^G/[0-9]{1,5}/DESC/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER22"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^G/[0-9]{1,5}/DIS/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER23"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^G/[0-9]{1,5}/DIS/OM/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER24"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^G/[0-9]{1,5}/EXP/ES/FE/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER25"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^G/[0-9]{1,5}/EXP/ES/MM/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER26"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^G/[0-9]{1,5}/GES/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER27"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^G/[0-9]{1,5}/LICUE/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER28"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^G/[0-9]{1,5}/REG/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER29"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^G/[0-9]{1,5}/TUP/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER30"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^G/[0-9]{1,5}/SAB/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER31"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^G/[0-9]{1,5}/TRA/OM/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER32"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^P/[0-9]{1,5}/TRA/TM/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER33"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^P/[0-9]{1,5}/TRA/OM/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER34"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^G/[0-9]{1,5}/TRA/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER35"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^GN/[0-9]{1,5}/P/TRA/DUC/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER36"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^GN/[0-9]{1,5}/TRA/DUC/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER37"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^P/[0-9]{1,5}/TRA/DUC/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER38"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^P/[0-9]{1,5}/P/TRA/DUC/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER39"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^LP/[0-9]{1,5}/DIST/AUT/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER40"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^LP/[0-9]{1,5}/DIST/PLA/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER41"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^LP/[0-9]{1,5}/DIST/DUC/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER42"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^G/[0-9]{1,5}/LPD/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER43"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^LP/[0-9]{1,5}/EXP/ES/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER44"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^LP/[0-9]{1,5}/EXP/AUT/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER45"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^LP/[0-9]{1,5}/COM/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER46"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^LP/[0-9]{1,5}/TRA/DUC/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER47"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^G/[0-9]{1,5}/LPT/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER48"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^LP/[0-9]{1,5}/TRA/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER49"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^LP/[0-9]{1,5}/ALM/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER50"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^G/[0-9]{1,5}/LPA/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER51"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^LP/[0-9]{1,5}/DIST/REP/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER52"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^PL/[0-9]{1,5}/EXP/ESA/MM/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER53"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^PL/[0-9]{1,5}/DIS/DUC/[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER54"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^SENER-REF-[0-9]{1,3}-[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER55"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^SENER-TP-[0-9]{1,3}-[0-9]{4}$"
          }
        }
      }
    },
    {
      "if": {
        "properties": {
          "Caracter": {
            "const": "permisionario"
          },
          "ModalidadPermiso": {
            "const": "PER56"
          }
        }
      },
      "then": {
        "properties": {
          "NumContratoOAsignacion": {
            "type": "string",
            "pattern": "^SENER-CPG-[0-9]{1,3}-[0-9]{4}$"
          }
        }
      }
    }
  ],
  "additionalProperties": False,
  "definitions": {
    "RFC": {
      "description": "El Registro Federal de Contribuyentes es la clave que se asigna a las personas físicas y morales que tengan obligación de presentar declaraciones periódicas de pago, informativas o por cuenta de terceros, o estén obligadas a expedir comprobantes fiscales por las actividades que realicen.\n La clave se conforma de 12 dígitos en el caso de personas morales, los primeros 3, corresponden a la denominación o razón social del contribuyente, los siguientes 6 corresponden a su fecha de constitución (aa/mm/dd) y los últimos 3 son los dígitos de la homoclave, la cual permite que el RFC sea único e irrepetible aun y cuando coincidan los primeros 9 dígitos anteriores.\n Para el caso de personas físicas, la clave se conforma de 13 dígitos, los primeros 4, corresponden al nombre del contribuyente (2 dígitos para apellido paterno, 1 para apellido materno y 1 para el nombre del contribuyente), los siguientes 6 corresponden a su fecha de nacimiento (aa/mm/dd) y los últimos 3 son los dígitos de la homoclave, la cual permite que el RFC sea único e irrepetible aun y cuando coincidan los primeros 9 dígitos anteriores.",
      "type": "string",
      "pattern": "^([A-ZÑ]|\\&){3,4}[0-9]{2}(0[1-9]|1[0-2])([12][0-9]|0[1-9]|3[01])[A-Z0-9]{3}$"
    },
    "RfcPersonaFisica": {
      "description": "RFC con longitud de 13 posiciones, correspondiente a una persona física.",
      "type": "string",
      "pattern": "^([A-ZÑ]|\\&){4}[0-9]{2}(0[1-9]|1[0-2])([12][0-9]|0[1-9]|3[01])[A-Z0-9]{3}$"
    },
    "RfcPersonaMoral": {
      "description": "RFC con longitud de 12 posiciones, correspondiente a una persona moral.",
      "type": "string",
      "pattern": "^([A-ZÑ]|\\&){3}[0-9]{2}(0[1-9]|1[0-2])([12][0-9]|0[1-9]|3[01])[A-Z0-9]{3}$"
    },
    "Geoloc": {
      "type": "object",
      "description": "Estructura que almacena pares de coordenadas.",
      "properties": {
        "GeolocalizacionLatitud": {
          "type": "number",
          "minimum": -90,
          "maximum": 90,
          "fractionDigits": 7,
          "description": "Requerido para expresar la ubicación geográfica de la instalación, expresada en Grados decimales (DD). Para el caso de áreas Contractuales o Asignaciones se deberán indicar las coordenadas de cada vértice. Este elemento se puede repetir por cada vértice del área o asignación."
        },
        "GeolocalizacionLongitud": {
          "type": "number",
          "minimum": -180,
          "maximum": 180,
          "fractionDigits": 7,
          "description": "Requerido para expresar la ubicación geográfica de la instalación expresada en Grados decimales (DD). Para el caso de áreas Contractuales o Asignaciones se deberán indicar las coordenadas de cada vértice. Este elemento se puede repetir por cada vértice del área o asignación."
        }
      },
      "required": ["GeolocalizacionLatitud", "GeolocalizacionLongitud"]
    },
    "Volumen": {
      "type": "object",
      "description": "Objeto para describir un volumen y su unidad de medida.",
      "properties": {
        "ValorNumerico": {
          "description": "Valor adimensional del volumen.",
          "type": "number",
          "minimum": 0,
          "maximum": 100000000000,
          "fractionDigits": 3
        },
        "UnidadDeMedida": {
          "description": "Unidad de medida asociada al valor numérico.",
          "$ref": "#/definitions/UM"
        }
      },
      "required": ["ValorNumerico", "UnidadDeMedida"],
      "additionalProperties": False
    },
    "UM": {
      "description": "Este tipo de variable sólo permite los valores indicados en la sección \\ref{Claves} ``\\nameref{Claves}\"{}, subsección \\ref{Claves:UnidadDeMedida} ``\\nameref{Claves:UnidadDeMedida}\"{}.",
      "type": "string",
      "pattern": "^UM0[1-4]$"
    }
  }
}


# Datos a ingresar en el JSON
datos = {
    "Version": "1.0", #String
    "RfcContribuyente": "PED840921K12", #String 
    "RfcRepresentanteLegal":"PEDS840921K12", #String
    "RfcProveedor": "PED840921K12",#String
    "Caracter": "contratista",#string  "contratista", "asignatario", "permisionario", "usuario"
    "ModalidadPermiso": "", #string
    "NumPermiso":"",#string
     "NumContratoOAsignacion": "",#String
    "InstalacionAlmacenGasNatural": " ",#string
    "ClaveInstalacion": " ",#string
    "DescripcionInstalacion": " ",#string
    "Geolocalizacion": [#array
        {
            "GeolocalizacionLatitud": 19.432608,
            "GeolocalizacionLongitud": -99.133333
        }
    ],
    "NumeroPozos": 1, #Int
    "NumeroTanques":1,#Int
    "NumeroDuctosEntradaSalida":1,#Int
    "NumeroDuctosTransporteDistribucion":2,#int
    "NumeroDispensarios":2,#int
    "FechaYHoraCorte": " ", #string format date-time  yyyy-mm-ddThh:mm:ss+-hh:mm
    "Producto": [ #array
        {
            "ClaveProducto": " ",#string solo PR03,PR07,etc
            "ClaveSubProducto": " ",#string
            "ComposOctanajeGasolina": " ",#int
            "GasolinaConCombustibleNoFosil": " ",#string ["Sí", "No"] PR07
            "ComposDeCombustibleNoFosilEnGasolina": " ",#int 
            "DieselConCombustibleNoFosil": " ",#String  ["Sí", "No"] PR03
            "ComposDeCombustibleNoFosilEnDiesel": "",#int
            "TurbosinaConCombustibleNoFosil": " ",#string  ["Sí", "No"] PR11
            "ComposDeCombustibleNoFosilEnTurbosina":" ",#int 
            "ComposDePropanoEnGasLP":" ",#double number PR12
            "ComposDeButanoEnGasLP": " ",#double number PR12
            "DensidadDePetroleo": " ",#double PR08
            "ComposDeAzufreEnPetroleo": " ",#double PR08
            "Otros": " ",#string PR15 SP20
            "MarcaComercial": " ",#string
            "Marcaje":" ",#string
            "ConcentracionSustanciaMarcaje":" ",#double
            "GasNaturalOCondensados": [#array PR09 o PR10 
                {
                    "ComposGasNaturalOCondensados":" ",#string
                    "FraccionMolar": " ",#double
                    "PoderCalorifico": " "#double
                }
            ],
            "Tanque": [#Array
                {
                        "ClaveIdentificacionTanque": "TQS-ACA-2020 ",#string
                        "Localizaciony/oDescripcionTanque":" ",#string
                        "VigenciaCalibracionTanque":" ",#string yyyy-mm-dd
                        "CapacidadTotalTanque":" ",#
                        "CapacidadOperativaTanque":" ",#
                        "CapacidadUtilTanque": " ",#
                        "CapacidadFondajeTanque":" ",# 
                        "CapacidadGasTalon":" ",
                        "VolumenMinimoOperacion": " ",
                        "EstadoTanque": " ",#booleano  ["O", "F"]
                        "Medidores": [
                            {
                                "SistemaMedicionTanque":"",#string
                                "LocalizODescripSistMedicionTanque":" ",#string
                                "VigenciaCalibracionSistMedicionTanque": " ",#string
                                "IncertidumbreMedicionSistMedicionTanque":" ",#double
                            }
                        ],
                        "Existencias":[
                            {
                            "VolumenExistenciasAnterior": " ",#number
                            "VolumenAcumOpsRecepcion":" ",#
                            "HoraRecepcionAcumulado": " ",#string
                            "VolumenAcumOpsEntrega": " ",#
                            "HoraEntregaAcumulado":" ",#string  
                            "VolumenExistencias":" ",#double
                            "FechaYHoraEstaMedicion":" ",
                            #string yyyy-mm-ddThh:mm:ss+-hh:mm
                            "FechaYHoraMedicionAnterior": " "#string
                            }
                        ],
                        "Recepciones": [
                            {
                                "TotalRecepciones": " ",#int
                                "SumaVolumenRecepcion":" ",
                                "TotalDocumentos": " ",#int
                                "SumaCompras": " ",#double
                                "Recepcion":[
                                    {
                                    "NumeroDeRegistro": " ",#double
                                    "VolumenInicialTanque":" ",#   
                                    "VolumenFinalTanque":" ",#
                                    "VolumenRecepcion": " ",#
                                    "Temperatura": " ",#double
                                    "PresionAbsoluta":" ",#double
                                    "FechaYHoraInicioRecepcion":" ",#string
                                    "FechaYHoraFinalRecepcion": " ",#string
                                    "Complemento": {
                                        "Almacenamiento": {
                                            "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Refinacion.schema.json"
                                            }

                                        }

                                    }
                                ],
                            }
                        ],
                        "Entregas":[
                            {
                             "TotalEntregas":" ",#int   
                             "SumaVolumenEntregado": " ",#
                             "TotalDocumentos":" ",#int
                             "SumaVentas":" ",#double
                            "Entrega":[
                                {
                                    "NumeroDeRegistro":" ",#number
                                    "VolumenInicialTanque":" ",#
                                    "VolumenFinalTanque": " ",#int
                                    "VolumenEntregado": " ",#
                                    "Temperatura":" ",#double
                                    "PresionAbsoluta":" ",#double
                                    "FechaYHoraInicialEntrega":" ",#string
                                    "FechaYHoraFinalEntrega":" ",#string
                                    "Complemento": {
                                        "Almacenamiento": {
                                            "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Refinacion.schema.json"
                                        }

                                    }
                                }
                            ]
                            
                            
                            
                          }
                        ],
                }
            ],
            "Ducto": [
                {
                    "ClaveIdentificacionDucto": " ",#string
                    "DescripcionDucto":" ",#string
                    "DiametroDucto":" ",#double
                    "Medidores":[
                        {
                            "SistemaMedicionDucto": "SMD-DUC-TRA-1234",
                            "LocalizODescripSistMedicionDucto": " ",#string
                            "VigenciaCalibracionSistMedicionDucto": "2024-06-18",#string date
                            "IncertidumbreMedicionSistMedicionDucto": 0.010#double
                        }
                    ],
                    "CapacidadGasTalon":" ",#
                    "Recepciones": [
                        {
                            "TotalRecepciones":" ",#int
                            "SumaVolumenRecepcion": " ",
                            "TotalDocumentos":" ",#int
                            "SumaCompras": " ",#double
                            "Recepcion":[
                                {
                                    "NumeroDeRegistro":" ",#int
                                    "VolumenPuntoEntrada":" ",
                                    "VolumenRecepcion": " ",
                                    "Temperatura":" ",#double
                                    "PresionAbsoluta":" ",#double
                                    "FechaYHoraInicioRecepcion":" ",#string
                                    "FechaYHoraFinalRecepcion":" ",#string
                                    "Complemento": {
                                        "Almacenamiento": {
                                            "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Refinacion.schema.json"
                                        }

                                    }
                                }
                            ],

                        }
                    ], 
                }
            ],
            "Pozo":[
                {
                   "ClavePozo":"",#string 
                   "DescripcionPozo":"",#String
                    "Medidores": [{
                        "SistemaMedicionPozo": " ",#string
                        "LocalizODescripSistMedicionPozo": " ",#string
                        "VigenciaCalibracionSistMedicionPozo": " ",#string
                        "IncertidumbreMedicionSistMedicionPozo":" ",#double
                    }],
                    "Recepciones":[{
                        "TotalRecepciones":" ",#int
                        "SumaVolumenRecepcion": " ",#
                        "TotalDocumentos": " ",#int
                        "SumaCompras": " ",#int
                        "Recepcion":[{
                            "NumeroDeRegistro":" ",#int
                            "VolumenRecepcion": " ",#
                            "Temperatura":" ",#double
                            "PresionAbsoluta":" ",#double
                            "FechaYHoraInicioRecepcion": " ",#string
                            "FechaYHoraFinalRecepcion":" ",
                            #string
                            "Complemento": {
                                        "Almacenamiento": {
                                            "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Refinacion.schema.json"
                                        }

                            }
                        }],
                        
                    }],
                     "Entregas":[{
                        "TotalEntregas": " ",#int
                         "SumaVolumenEntregado": "",
                         "TotalDocumentos":" ",#int
                          "SumaVentas": " ",#double
                           "Entrega":[{
                                "NumeroDeRegistro":"",#int
                                "VolumenEntregado":" ",#
                                "Temperatura": " ",#
                                "PresionAbsoluta": " ",#
                                "FechaYHoraInicioEntrega":" ",#
                                "FechaYHoraFinalEntrega":" ",#
                                "Complemento": {
                                        "Almacenamiento": {
                                            "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Refinacion.schema.json"
                                        }
                                    }
                           }],
                     }],
                }
            ],
            "Dispensario":[{
                    "ClaveDispensario": " ",#string
                    "Medidores":[{
                            "SistemaMedicionDispensario":" ",#string
                            "LocalizODescripSistMedicionDispensario":" ",#string
                            "VigenciaCalibracionSistMedicionDispensario":"",#string
                            "IncertidumbreMedicionSistMedicionDispensario":"",#double
                    }],
                    "Manguera":[{
                        "IdentificadorManguera":" ",#string
                        "Entregas":[{
                           "TotalEntregas":" ",#integer
                           "SumaVolumenEntregado":" ",
                           "TotalDocumentos":" ",#int
                           "SumaVentas":" ",#double 
                           "Entrega":[{
                                "NumeroDeRegistro":" ",#int
                                "TipoDeRegistro":" ",#enum["D", "E", "J", "A", "N", "C"]
                                "VolumenEntregadoTotalizadorAcum":"",#
                                "VolumenEntregadoTotalizadorInsta":" ",#
                                "PrecioVentaTotalizadorInsta":" ",#double
                                "FechaYHoraEntrega":" ",#string
                                "Complemento": {
                                        "Almacenamiento": {
                                            "$ref": "https://repositorio.cloudb.sat.gob.mx/Covol/json/Comp-Refinacion.schema.json"
                                        }
                                    }
                             }],
                        }],
                    }],
            }],
        }
    ],
    "Bitacora":[{
            "NumeroRegistro":" ",#int
             "FechaYHoraEvento": " ",#string
             "UsuarioResponsable": " ",#string
              "TipoEvento": " ",#int
               "DescripcionEvento":" ",#string
               "IdentificacionComponenteAlarma": " ",#string
    }]  

    # Añade más propiedades aquí según sea necesario
}

# Validar los datos contra el esquema
try:
    validate(instance=datos, schema=schema, cls=Draft7Validator)
    print("Los datos son válidos según el esquema.")
    
    # Guardar los datos en un archivo JSON
    with open('datos.json', 'w') as file:
        json.dump(datos, file, indent=4)
        print("Los datos han sido guardados correctamente en datos.json.")

except Exception as e:
    print(f"Los datos no son válidos según el esquema: {e}")
