# app/main.py
from flask import Flask
from config import DevelopmentConfig
from db_1 import query_main_db
from db_2 import query_secondary_db

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

@app.route('/')
def index():
    results = query_main_db()
    return str(results)

@app.route('/secondary')
def secondary():
    results = query_secondary_db()
    return str(results)

if __name__ == '__main__':
    app.run()
