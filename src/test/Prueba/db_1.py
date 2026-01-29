# app/db_1.py
from flask import current_app
from flask_mysqldb import MySQL

def get_main_db():
    app = current_app._get_current_object()
    app.config.from_object('config.DevelopmentConfig')
    return MySQL(app)

def query_main_db():
    db = get_main_db()
    cursor = db.connection.cursor()
    cursor.execute('SELECT * FROM usuarios_cv')  # Cambia 'some_table' por una tabla real
    results = cursor.fetchall()
    cursor.close()
    return results
