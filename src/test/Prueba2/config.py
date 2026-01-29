class Config:
    SECRET_KEY = 'B!1weNAt1T%kvhUI*S'

class DevelopmentConfig(Config):
    DEBUG = True
    
    # URI principal para una base de datos
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/scaizendb_2'
    
    # Configuración de bases de datos adicionales usando 'binds'
    SQLALCHEMY_BINDS = {
        'db2': 'mysql+pymysql://root:@localhost/scaizen_cv'
    }
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

config = {
    'development': DevelopmentConfig
}
