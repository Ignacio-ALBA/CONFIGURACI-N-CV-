class Config:
    SECRET_KEY = 'B!1weNAt1T%kvhUI*S'
""""
class DevelopmentConfig(Config):
    DEBUG = True
    
    # URI principal para una base de datos

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://scaizenx:Sx2020@scaizen_web/scaizendb'
    
    # Configuración de bases de datos adicionales usando 'binds'
    SQLALCHEMY_BINDS = {
        'db2': 'mysql+pymysql://scaizenx:Sx2020@scaizen_web/scaizen_cv'
    }
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
"""

class DevelopmentConfig(Config):
    DEBUG = True
    
    # URI principal para una base de datos
    #SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:mi_contraseña@localhost/scaizendb'
    IP_SERVER = 'scaizen.com'
    #SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://scaizenx:Sx2020;@{IP_SERVER}/scaizendb'
    

    USER = None
    IP_SERVER = None
    value = 0
    if value == 0:
            USER = 'scaizenx:Sx2020'
            IP_SERVER = '172.18.0.2'
    elif value == 1:
            USER = 'root:'
            IP_SERVER = 'localhost'   
    
    
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{USER}@{IP_SERVER}/scaizendb'

    # Configuración de bases de datos adicionales usando 'binds'
    SQLALCHEMY_BINDS = {
        #'db2': f'mysql+pymysql://scaizenx:Sx2020;@{IP_SERVER}/scaizen_cv'
        'db2': f'mysql+pymysql://{USER}@{IP_SERVER}/scaizen_cv'

    }
    #PDF, JSON, XML 
    SQLALCHEMY_TRACK_MODIFICATIONS = False

config = {
    'development': DevelopmentConfig
}