from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar
from cryptography.fernet import Fernet
from flask import redirect
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(filename)s - line %(lineno)d : %(message)s'
)


class GlobalConfig:
    def __init__(self):
        self.PERMISOS_VALIDOS = {
                                "Distribuidor": {
                                    "label": "Distribuidor",
                                    "sub_permisos": {
                                        "DCompras": {
                                            "label": "Compras",
                                            "sub_permisos": {
                                                "DComprasAlta": {
                                                    "label": "Alta",
                                                    "sub_permisos": {}
                                                },
                                                "DComprasConsultar": {
                                                    "label": "Consultar",
                                                    "sub_permisos": {}
                                                },
                                                "DComprasSubirFacturaXML": {
                                                    "label": "Subir Factura XML",
                                                    "sub_permisos": {}
                                                }
                                            }
                                        },
                                        "DVentas": {
                                            "label": "Ventas",
                                            "sub_permisos": {
                                                "DVentasConsultar": {
                                                    "label": "Consultar",
                                                    "sub_permisos": {}
                                                },
                                                "DVentasSubirFacturaXML": {
                                                    "label": "Subir Factura XML",
                                                    "sub_permisos": {}
                                                }
                                            }
                                        },
                                        "DReportes": {
                                            "label": "Reportes",
                                            "sub_permisos": {
                                                "DReportediario": {
                                                    "label": "Reporte diario",
                                                    "sub_permisos": {
                                                        "DReportediarioVer": {
                                                            "label": "Ver",
                                                            "sub_permisos": {}
                                                        },
                                                        "DReportediarioGenerar": {
                                                            "label": "Generar",
                                                            "sub_permisos": {}
                                                        },
                                                        "DReportediarioPDF": {
                                                            "label": "PDF",
                                                            "sub_permisos": {}
                                                        },
                                                        "DReportediarioJSON": {
                                                            "label": "JSON",
                                                            "sub_permisos": {}
                                                        },
                                                        "DReportediarioXML": {
                                                            "label": "XML",
                                                            "sub_permisos": {}
                                                        }
                                                    }
                                                },
                                                "DReportemensual": {
                                                    "label": "Reporte mensual",
                                                    "sub_permisos": {
                                                        "DReportemensualVer": {
                                                            "label": "Ver",
                                                            "sub_permisos": {}
                                                        },
                                                        "DReportemensualGenerar": {
                                                            "label": "Generar",
                                                            "sub_permisos": {}
                                                        },
                                                        "DReportemensualPDF": {
                                                            "label": "PDF",
                                                            "sub_permisos": {}
                                                        },
                                                        "DReportemensualJSON": {
                                                            "label": "JSON",
                                                            "sub_permisos": {}
                                                        },
                                                        "DReportemensualXML": {
                                                            "label": "XML",
                                                            "sub_permisos": {}
                                                        }
                                                    }
                                                },
                                                "DReportedealarmas": {
                                                    "label": "Reporte de alarmas",
                                                    "sub_permisos": {
                                                        "DReportedealarmasVer": {
                                                            "label": "Ver",
                                                            "sub_permisos": {}
                                                        },
                                                        "DReportedealarmasPDF": {
                                                            "label": "PDF",
                                                            "sub_permisos": {}
                                                        }
                                                    }
                                                },
                                                "DReportedeeventos": {
                                                    "label": "Reporte de eventos",
                                                    "sub_permisos": {
                                                        "DReportedeeventosVer": {
                                                            "label": "Ver",
                                                            "sub_permisos": {}
                                                        },
                                                        "DReportedeeventosPDF": {
                                                            "label": "PDF",
                                                            "sub_permisos": {}
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                },
                                "Comercializador": {
                                    "label": "Comercializador",
                                    "sub_permisos": {
                                        "CCompras": {
                                            "label": "Compras",
                                            "sub_permisos": {
                                                "CComprasAlta": {
                                                    "label": "Alta",
                                                    "sub_permisos": {}
                                                },
                                                "CComprasConsultar": {
                                                    "label": "Consultar",
                                                    "sub_permisos": {}
                                                }
                                            }
                                        },
                                        "CVentas": {
                                            "label": "Ventas",
                                            "sub_permisos": {
                                                "CVentasConsultar": {
                                                    "label": "Consultar",
                                                    "sub_permisos": {}
                                                },
                                                "CVentasSubirFacturaXML": {
                                                    "label": "Subir Factura XML",
                                                    "sub_permisos": {}
                                                }
                                            }
                                        },
                                        "CReportes": {
                                            "label": "Reportes",
                                            "sub_permisos": {
                                                "CReportediario": {
                                                    "label": "Reporte diario",
                                                    "sub_permisos": {
                                                        "CReportediarioVer": {
                                                            "label": "Ver",
                                                            "sub_permisos": {}
                                                        },
                                                        "CReportediarioGenerar": {
                                                            "label": "Generar",
                                                            "sub_permisos": {}
                                                        },
                                                        "CReportediarioPDF": {
                                                            "label": "PDF",
                                                            "sub_permisos": {}
                                                        },
                                                        "CReportediarioJSON": {
                                                            "label": "JSON",
                                                            "sub_permisos": {}
                                                        },
                                                        "CReportediarioXML": {
                                                            "label": "XML",
                                                            "sub_permisos": {}
                                                        }
                                                    }
                                                },
                                                "CReportemensual": {
                                                    "label": "Reporte mensual",
                                                    "sub_permisos": {
                                                        "CReportemensualVer": {
                                                            "label": "Ver",
                                                            "sub_permisos": {}
                                                        },
                                                        "CReportemensualGenerar": {
                                                            "label": "Generar",
                                                            "sub_permisos": {}
                                                        },
                                                        "CReportemensualPDF": {
                                                            "label": "PDF",
                                                            "sub_permisos": {}
                                                        },
                                                        "CReportemensualJSON": {
                                                            "label": "JSON",
                                                            "sub_permisos": {}
                                                        },
                                                        "CReportemensualXML": {
                                                            "label": "XML",
                                                            "sub_permisos": {}
                                                        }
                                                    }
                                                },
                                                "CReportedeeventos": {
                                                    "label": "Reporte de alarmas",
                                                    "sub_permisos": {
                                                        "CReportedeeventosVer": {
                                                            "label": "Ver",
                                                            "sub_permisos": {}
                                                        },
                                                        "CReportedeeventosPDF": {
                                                            "label": "PDF",
                                                            "sub_permisos": {}
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                },
                                "Catalogo": {
                                    "label": "Catálogo",
                                    "sub_permisos": {
                                        "Cliente": {
                                            "label": "Cliente",
                                            "sub_permisos": {
                                                "ClienteAlta": {
                                                    "label": "Alta",
                                                    "sub_permisos": {}
                                                },
                                                "ClienteEditar": {
                                                    "label": "Editar",
                                                    "sub_permisos": {}
                                                },
                                                "ClienteConsultar": {
                                                    "label": "Consultar",
                                                    "sub_permisos": {}
                                                },
                                                "ClienteEliminar": {
                                                    "label": "Eliminar",
                                                    "sub_permisos": {}
                                                }
                                            }
                                        },
                                        "Proveedor": {
                                            "label": "Proveedor",
                                            "sub_permisos": {
                                                "ProveedorAlta": {
                                                    "label": "Alta",
                                                    "sub_permisos": {}
                                                },
                                                "ProveedorEditar": {
                                                    "label": "Editar",
                                                    "sub_permisos": {}
                                                },
                                                "ProveedorConsultar": {
                                                    "label": "Consultar",
                                                    "sub_permisos": {}
                                                },
                                                "ProveedorEliminar": {
                                                    "label": "Eliminar",
                                                    "sub_permisos": {}
                                                }
                                            }
                                        },
                                        "Estacióndeservicio": {
                                            "label": "Estación de servicio",
                                            "sub_permisos": {
                                                "EstacióndeservicioAlta": {
                                                    "label": "Alta",
                                                    "sub_permisos": {}
                                                },
                                                "EstacióndeservicioEditar": {
                                                    "label": "Editar",
                                                    "sub_permisos": {}
                                                },
                                                "EstacióndeservicioConsultar": {
                                                    "label": "Consultar",
                                                    "sub_permisos": {}
                                                },
                                                "EstacióndeservicioEliminar": {
                                                    "label": "Eliminar",
                                                    "sub_permisos": {}
                                                }
                                            }
                                        },
                                        "Roles": {
                                            "label": "Roles",
                                            "sub_permisos": {
                                                "RolesAlta": {
                                                    "label": "Alta",
                                                    "sub_permisos": {}
                                                },
                                                "RolesEditar": {
                                                    "label": "Editar",
                                                    "sub_permisos": {}
                                                },
                                                "RolesEditarPermisos": {
                                                    "label": "Editar Permisos",
                                                    "sub_permisos": {}
                                                },
                                                "RolesConsultar": {
                                                    "label": "Consultar",
                                                    "sub_permisos": {}
                                                },
                                                "RolesEliminar": {
                                                    "label": "Eliminar",
                                                    "sub_permisos": {}
                                                }
                                            }
                                        },
                                        "Usuarios": {
                                            "label": "Usuarios",
                                            "sub_permisos": {
                                                "UsuariosAlta": {
                                                    "label": "Alta",
                                                    "sub_permisos": {}
                                                },
                                                "UsuariosEditar": {
                                                    "label": "Editar",
                                                    "sub_permisos": {}
                                                },
                                                "UsuariosConsultar": {
                                                    "label": "Consultar",
                                                    "sub_permisos": {}
                                                },
                                                "UsuariosEliminar": {
                                                    "label": "Eliminar",
                                                    "sub_permisos": {}
                                                }
                                            }
                                        }
                                    }
                                },
                                "Configuración": {
                                    "label": "Configuración",
                                    "sub_permisos": {}
                                }
                            }

        
        self.PRODUCTOS_COLOR_BY_NAME = {
            'magna':'#00923f',
            'premium':'#da251c',
            'diesel':'#292929',
            'regular':'#00923f'
            }
        
        self.PRODUCTOS_NAMES = {
            'magna': 'PX MAGNA',
            'premium': 'PX PREMIUM',
            'diesel': 'PX DIESEL',
            'regular': 'PX MAGNA'
        }

        self.CLAVES_PRODUCTOS ={
            '15101514': 'regular',
            '15101515': 'premium',
            '5101505': 'diesel',
            '15101505': 'diesel'

        }

        self.CLAVES_SERVICIOS ={
            '80141629': 'Servicio_asociado',
            '78101807': 'Servicios de transporte de carga de petróleo o químicos por carretera'
        }
            

        #self.IP_SERVER = '192.168.68.79'
        self.USER = None
        self.IP_SERVER = None
        value = 0
        if value == 0:
            self.USER = 'scaizenx:Sx2020;'
            self.IP_SERVER = '172.18.0.2'
        elif value == 1:
            self.USER = 'root:'
            self.IP_SERVER = 'localhost'            
 
        self.DATABASE_URL_SCAIZENDB = f'mysql+pymysql://{self.USER}@{self.IP_SERVER}/scaizendb'
        self.DATABASE_URL_SCAIZEN_CV = f'mysql+pymysql://{self.USER}@{self.IP_SERVER}/scaizen_cv'
        self.clave = self.generar_clave()

    def FILTER_JSON(self, json1, json2):
        result = {}
    
        for key in json1:
            # Siempre incluir la clave "label" si está presente en json1
            if key == "label":
                result[key] = json1[key]
            # Verificamos si la clave está en json2
            elif key in json2:
                # Si el valor es un diccionario, aplicamos la función recursivamente
                if isinstance(json1[key], dict) and isinstance(json2[key], dict):
                    result[key] = self.FILTER_JSON(json1[key], json2[key])
                else:
                    result[key] = json1[key]
                    
        return result
    
    def CONTAR_NUMERO_PERMISOS(self, perms_permitidos):
        total_permisos = 0
        stack = [perms_permitidos]  # Inicia con el diccionario completo de permisos

        while stack:
            current = stack.pop()  # Toma el último grupo de permisos
            # Sumar los permisos del nivel actual
            total_permisos += len(current)
            # Añade los sub_permisos a la pila para seguir contando
            for key in current:
                stack.append(current[key].get('sub_permisos', {}))  # Agrega los sub_permisos

        return total_permisos


    def CHECK_USER_PERM(self, permiso_id, permisos):
        """
        Verifica si el permiso_id está presente en la estructura anidada de permisos.

        :param permiso_id: ID del permiso que se busca.
        :param permisos: Estructura anidada de permisos del usuario.
        :return: True si se encuentra el permiso, False en caso contrario.
        """
        # Iterar sobre cada permiso en el nivel actual
        for key, permiso in permisos.items():
            # Verificar si el ID del permiso coincide con el permiso buscado
            if key == permiso_id:
                return True
            
            # Si existen sub_permisos, realizar la verificación de manera recursiva
            if 'sub_permisos' in permiso:
                if self.CHECK_USER_PERM(permiso_id, permiso['sub_permisos']):
                    return True
        
        return False  # Permiso no encontrado
    
    
    def FORMATEAR_PERMISOS(self, ids):
        """
        Genera una estructura de permisos anidada a partir de una lista de IDs.

        :param ids: Lista de IDs de permisos.
        :return: Estructura anidada de permisos.
        """
        permisos = {}

        for id in ids:
            partes = id.split('/')
            current_level = permisos

            for parte in partes:
                # Verifica si el nivel actual ya existe
                if parte not in current_level:
                    # Crea un nuevo nodo si no existe
                    current_level[parte] = {
                        #'label': parte,
                        'sub_permisos': {}
                    }
                # Mueve al siguiente nivel
                current_level = current_level[parte]['sub_permisos']

        return permisos
    
    def LIST_PERMISOS(self, data):
        ids = []
        for permiso in data:
            ids.append(permiso["Id"])
            if permiso["sub_permisos"]:
                ids.extend(self.LIST_PERMISOS(permiso["sub_permisos"]))
        return ids

    def GET_DATABASE_URL_SCAIZENDB(self):
        return self.DATABASE_URL_SCAIZENDB
    
    def GET_DATABASE_URL_SCAIZEN_CV(self):
        return self.DATABASE_URL_SCAIZEN_CV
    
    def GET_MESUAL_DATE_END(self, month = None, year = None):
        if month == None and year == None:
            today = datetime.now()
            date = today.replace(day=self.GET_MENSUAL_CV_DAY())
            date = date.strftime("%Y-%m-%d %H:%M:%S")
            return date
        elif month != None and year != None:
            ultimo_dia_mes= calendar.monthrange(int(year), int(month))[1]
            fecha_fin = datetime(int(year), int(month), ultimo_dia_mes, 23, 59, 59)
            fecha_fin = fecha_fin.strftime('%Y-%m-%d %H:%M:%S')
            return fecha_fin
        else:
            return None
        
    
    def GET_MESUAL_DATE_START(self):
        today = datetime.now()
        end_date = today.replace(day=self.GET_MENSUAL_CV_DAY())
        date_start = end_date - relativedelta(months=1)
        date_start = date_start.strftime("%Y-%m-%d %H:%M:%S")
        return date_start
    
    def GET_DIARIO_DATE_START(self):
        now = datetime.now()
        date_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return date_start.strftime("%Y-%m-%d %H:%M:%S")
    
    def GET_DIARIO_DATE_END(self):
        now = datetime.now()
        date_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        return date_end.strftime("%Y-%m-%d %H:%M:%S")
    

    def GET_DIARIO_DATE_START_(self,date):
        date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        return date_start.strftime("%Y-%m-%d %H:%M:%S")
    
    def GET_DIARIO_DATE_END_(self,date):
        date_end = date.replace(hour=23, minute=59, second=59, microsecond=999999)
        return date_end.strftime("%Y-%m-%d %H:%M:%S")
    





    def GET_DIARIO_DATE_END_BEFORE(self,date=None):
        if date is None:
            now = datetime.now()
        else: now = date
        date_end = now - relativedelta(days=1)
        date_end = date_end.replace(hour=23, minute=59, second=59, microsecond=999999)
        return date_end.strftime("%Y-%m-%d")
    
    def GET_PRODUCTOS_COLOR_BY_NAME(self,name):
        return self.PRODUCTOS_COLOR_BY_NAME[name]
    
    def GET_PRODUCTOS_PRODUCT_NAME(self,name):
        return self.PRODUCTOS_NAMES[name]
    

    # Generar una clave (esto debe hacerse una vez y la clave debe ser guardada)
    def generar_clave(self):
        return Fernet.generate_key()

    # Crear un objeto Fernet usando la clave
    def crear_fernet(self, clave):
        return Fernet(clave)

    # Encriptar y convertir a hexadecimal
    def encriptar_a_hex(self, clave, data):
        fernet = self.crear_fernet(clave)
        # Encriptar el ID y obtener el resultado en bytes
        encriptado = fernet.encrypt(str(data).encode())
        # Convertir a hexadecimal
        encriptado_hex = encriptado.hex()
        return encriptado_hex

    # Desencriptar desde hexadecimal
    def desencriptar_desde_hex(self,clave, encriptado_hex):
        fernet = self.crear_fernet(clave)
        # Convertir de hexadecimal a bytes
        encriptado_bytes = bytes.fromhex(encriptado_hex)
        # Desencriptar el ID
        desencriptado_bytes = fernet.decrypt(encriptado_bytes)
        return int(desencriptado_bytes.decode())  # Convertir de nuevo a int

class VerificarPermisosUsuario:
    def __init__(self, permiso_id, permisos):
        self.permiso_id = permiso_id
        self.permisos = permisos

    def __check_user_perms__(self, permiso_id, permisos):
        """
        Verifica si el permiso_id está presente en la estructura anidada de permisos.

        :param permiso_id: ID del permiso que se busca.
        :param permisos: Estructura anidada de permisos del usuario.
        :return: True si se encuentra el permiso, False en caso contrario.
        """
        # Iterar sobre cada permiso en el nivel actual
        for key, permiso in permisos.items():
            if key == permiso_id:
                return True
            # Verifica en sub_permisos de forma recursiva
            if 'sub_permisos' in permiso:
                if self.__check_user_perms__(permiso_id, permiso['sub_permisos']):
                    return True
        return False  # Permiso no encontrado
    
    def __enter__(self):
        if not self.__check_user_perms__(self.permiso_id, self.permisos):
            return False
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # No es necesario hacer nada especial al salir del contexto
        pass
    
# Ejemplo de uso
config = GlobalConfig()
#clave_hex_hash = config.clave  # Ahora esta clave se puede usar en otras operaciones
clave_hex_hash = b'8qrBoxP9kb5ApD96bUpHrTHK6LRmzljHaWb4oL_1H34='




