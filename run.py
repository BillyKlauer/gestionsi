from app import app

if __name__ == '__main__':
    # Crear directorio de logs si no existe
    import os
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Ejecutar la aplicación
    app.run(debug=True, host='0.0.0.0', port=5000)