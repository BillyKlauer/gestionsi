from flask import render_template, request, redirect, session, flash
import bleach
from app import app
from app.config import Config
import logging
from datetime import datetime
import os

# Configuración de logging
LOG_FILE = os.path.join(os.path.dirname(__file__), '..', 'logs', 'historial.log')
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, 
                    format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

@app.route('/', methods=['GET', 'POST'])
def login():
    try:
        # Impresión de depuración
        template_path = os.path.join(app.template_folder, 'login.html')
        #print(f"Intentando renderizar: {template_path}")
        #print(f"Archivo existe: {os.path.exists(template_path)}")

        # Inicializar user_data como None
        user_data = None

        if request.method == 'POST':
            
            username = bleach.clean(request.form['username'])
            password = request.form['password']

            if not username or not password:
                flash('Credenciales requeridas', 'error')
                return render_template('login.html')
        
            if not Config.validate_password_strength(password):
                flash('Contraseña no cumple requisitos de seguridad', 'error')
                return render_template('login.html')
            
            # Log de intento de acceso
            logging.info(f"Intento de acceso - Usuario: {username}")
                        
            # Autenticación contra Directorio Activo
            if Config.authenticate_ad(username, password):
                # Obtener datos de usuario desde Oracle
                user_data = Config.get_user_data(username)

                #print(f"Datos de usuario en login: {user_data}")
                
            if user_data:
                session['username'] = username
                session['user_data'] = user_data #dict(zip(['full_name', 'cargo_empl', 'unid_empl'], user_data)) if user_data else {}
                
                return redirect('/dashboard')
            else:
                flash('No se encontraron datos de usuario', 'error')
                logging.warning(f"Datos de usuario no encontrados para: {username}")
        else:
            flash('Credenciales inválidas', 'error')
    
        return render_template('login.html')

    except Exception as e:
        logging.error(f"Error en login: {e}")
        flash('Error en el proceso de login', 'error')
        return render_template('login.html'), 500

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/')
    
    user_data = session.get('user_data', None)

    #print(f"Datos de usuario en dashboard: {user_data}")

     # Verificar si user_data existe
    if user_data is None:
        flash('Información de usuario no disponible', 'error')
        return redirect('/')
    
    return render_template('dashboard.html', user_data=user_data)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error_404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    logging.error(f"Error interno del servidor: {e}")
    return render_template('error_500.html'), 500