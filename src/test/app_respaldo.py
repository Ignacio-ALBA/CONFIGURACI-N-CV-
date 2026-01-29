from flask import Flask, render_template, request, redirect, url_for, flash

from flask_mysqldb import MySQL

from config import config
#proteccion para el login, tokken csrf_token
from flask_wtf.csrf import CSRFProtect 
#login manager
from flask_login import LoginManager, login_user, logout_user, login_required
#Models
from models.ModelUser import ModelUser

#Entities:
from models.entities.User import User

app = Flask(__name__)

csrf = CSRFProtect()
db = MySQL(app)

login_manager_app = LoginManager(app)

@login_manager_app.user_loader
def load_user(id):
     return ModelUser.get_by_id(db,id)


@app.route('/')
def index():#Al acceder me redirije a la ruta login
    return redirect(url_for('login'))

@app.route('/login', methods=['GET','POST'])  # Ajusta la regla de ruta aquí
def login():
    if request.method == 'POST':
           # print(request.form['username'])
           # print(request.form['password'])
            user = User(0, request.form['username'],None,None ,request.form['password'],None,None,None)
            logged_user=ModelUser.login(db, user)
            if logged_user != None:
                if logged_user.password_user:
                     login_user(logged_user)#lo almacena como usuario logeado
                     return redirect(url_for('scaizen'))
                else:
                    flash("Contraseña invalida...")
                    return render_template('auth/login.html') 
            else:
                flash("Usuario no encontrado...")
                return render_template('auth/login.html')

    else:   
            return render_template('auth/login.html')

#cerrar sesion
@app.route('/logout')
def logout():
     logout_user()
     return redirect(url_for('login'))

@app.route('/scaizen')
def scaizen():
    return render_template('scaizen.html')


@app.route('/permisos')
@login_required
def permisos(): #esta es una vista protegida solo para usuarios logeados
    return render_template('scaizen.html', title='Tablas', content=render_template('tables.html'))

@app.route('/protected')
@login_required
def protected(): #esta es una vista protegida solo para usuarios logeados
    return "<h1>Solo usuarios logeados</h1>"

def status_401(error):
     return redirect(url_for('login'))
def status_404(error):
     return "<h1>Página no encontrada</h1>"


if __name__ == '__main__':
    app.config.from_object(config['development'])
    csrf.init_app(app)
    app.register_error_handler(401,status_401)
    app.register_error_handler(404,status_404)
    app.run()
