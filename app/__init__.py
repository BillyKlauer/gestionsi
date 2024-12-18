from flask import Flask, render_template
import os
import logging

# Obtener la ruta absoluta al directorio actual del script
base_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(base_dir, 'templates')

app = Flask(__name__, template_folder=template_dir)
app.secret_key = 'Seguro2024'

from app import routes

# Manejador de errores global
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error_404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    logging.error(f"Error interno del servidor: {e}")
    return render_template('error_500.html'), 500