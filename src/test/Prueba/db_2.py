# app/db_2.py
from flask import current_app
from flask_mysqldb import MySQL

def get_secondary_db():
    app = current_app._get_current_object()
    app.config.from_object('app.config.SecondaryConfig')
    return MySQL(app)

def query_secondary_db():
    db = get_secondary_db()
    cursor = db.connection.cursor()
    cursor.execute('SELECT * FROM usuarios_cv')  # Cambia 'another_table' por una tabla real
    results = cursor.fetchall()
    cursor.close()
    return results
