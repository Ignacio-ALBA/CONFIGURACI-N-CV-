from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from config import config

app = Flask(__name__)
app.config.from_object(config['development'])

# Inicializa SQLAlchemy
db = SQLAlchemy(app)

@app.route('/test')
def index():
    # Consultar en la base de datos principal
    query_main = text('SELECT * FROM tanques')
    try:
        with db.engine.connect() as connection:
            result_main = connection.execute(query_main)
            rows_main = result_main.fetchall()
    except Exception as e:
        rows_main = [f"Error in main DB: {e}"]

    # Consultar en la base de datos secundaria (db2)
    query_secondary = text('SELECT * FROM usuarios_cv')
    try:
        with db.get_engine(bind='db2').connect() as connection:
            result_secondary = connection.execute(query_secondary)
            rows_secondary = result_secondary.fetchall()
    except Exception as e:
        rows_secondary = [f"Error in secondary DB: {e}"]

    # Combina los resultados de ambas consultas
    result_str_main = '\n'.join(f'Main DB: {row}' for row in rows_main)
    result_str_secondary = '\n'.join(f'Secondary DB: {row}' for row in rows_secondary)
    
    return f'Results from Main DB:\n{result_str_main}\n\nResults from Secondary DB:\n{result_str_secondary}'

if __name__ == '__main__':
    app.run(debug=True)
