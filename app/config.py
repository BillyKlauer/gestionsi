import os
from dotenv import load_dotenv
import logging
from ldap3 import Server, Connection, ALL
import cx_Oracle

load_dotenv()
#print("Variables de entorno:")
#print(f"AD_SERVER: {os.getenv('AD_SERVER')}")
#print(f"AD_DOMAIN: {os.getenv('AD_DOMAIN')}")
#print(f"ORACLE_TNSNAMES: {os.getenv('ORACLE_TNSNAMES')}")

class Config:
    # Configuración de Directorio Activo
    AD_SERVER = os.getenv('AD_SERVER')
    AD_DOMAIN = os.getenv('AD_DOMAIN')

    # Configuración de base de datos Oracle
    ORACLE_TNSNAMES = os.getenv('ORACLE_TNSNAMES')
    
    @staticmethod
    def authenticate_ad(username, password):
        """
        Autenticar usuario contra Directorio Activo
        """
        
        try:
            # Debug: Imprimir valores de configuración
            #print(f"AD_SERVER (type {type(Config.AD_SERVER)}): {Config.AD_SERVER}")
            #print(f"AD_DOMAIN (type {type(Config.AD_DOMAIN)}): {Config.AD_DOMAIN}")

             # Validar que los parámetros no sean None o estén vacíos
            if not username or not password:
                logging.error("Username o password están vacíos")
                return False

            # Verificar que las configuraciones de AD estén definidas
            if not Config.AD_SERVER or not Config.AD_DOMAIN:
                logging.error(f"Configuraciones de AD no definidas SERVER: {Config.AD_SERVER}, DOMAIN: {Config.AD_DOMAIN}")
                return False

            
            server = Server(Config.AD_SERVER, get_info=ALL)
            conn = Connection(server, 
                              user=f'{Config.AD_DOMAIN}\\{username}', 
                              password=password, 
                              auto_bind=True)
            
            return conn.bind()
        except Exception as e:
            logging.error(f"Error de autenticación AD: {type(e)} - {e}")
            
            return False

    @staticmethod
    def get_user_data(username):
        """
        Obtener datos de usuario desde base de datos Oracle
        """

        connection = None
        cursor = None

        try:
            # Establecer conexión usando cadena TNS
            dsn = cx_Oracle.makedsn('INFO7364.cmac-arequipa.com.pe', '1523', service_name=Config.ORACLE_TNSNAMES)
            connection = cx_Oracle.connect(user='usr_alter_ebs', password='usr_alter_ebs_desa', dsn=dsn)
            
            cursor = connection.cursor()
            cursor.execute("select full_name, cargo_empl, unid_empl from ca_alt_vs_datos_empl where usuario_empl = :username", 
                           username=username + 'pru')
            
            user_data = cursor.fetchone()

            if user_data is None:
                logging.warning(f"No se encontraron datos para el usuario: {username}")
                #print(f"No se encontraron datos para el usuario: {username}")
                return None
            
            logging.info(f"Datos de usuario obtenidos: {user_data}")
            return user_data
                    
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            logging.error(f"Error de base de datos Oracle: {error.code}, {error.message}")
            #print(f"Error de base de datos Oracle: {error.code}, {error.message}")
            return None
        except Exception as e:
            logging.error(f"Error obteniendo datos de usuario: {e}")
            #print(f"Error obteniendo datos de usuario: {e}")
            return None
        finally:
        # Asegurar cierre de cursor y conexión
            if cursor:
                cursor.close()
            if connection:
                connection.close()
        
    @staticmethod
    def validate_password_strength(password):
        """
        Validar complejidad de contraseña
        """
        if len(password) < 8:
            return False
        
        has_uppercase = any(c.isupper() for c in password)
        has_lowercase = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)
        
        return has_uppercase and has_lowercase and has_digit and has_special

    @staticmethod
    def check_login_attempts(username):
        """
        Limitar intentos de login
        """
        # Implementar lógica de bloqueo tras X intentos fallidos
        pass