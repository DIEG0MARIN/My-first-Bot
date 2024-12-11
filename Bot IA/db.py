import mysql.connector
from datetime import datetime

def obtener_conexion():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # Sin contraseña
        port=3308,  # Puerto de tu MySQL según lo configurado
        database="bot_ia"  # Nombre correcto de tu base de datos
    )

def registrar_usuario(nombre):
    conexion = None  # Inicializamos la variable
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        query = "INSERT INTO usuarios (nombre) VALUES (%s)"
        cursor.execute(query, (nombre,))
        conexion.commit()
        print("Usuario registrado correctamente")
    except mysql.connector.Error as err:
        print(f"Error al registrar usuario: {err}")
    finally:
        if conexion and conexion.is_connected():
            conexion.close()

def registrar_servicio(nombre_usuario, area, detalle):
    conexion = None  # Inicializamos la variable
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        # Obtenemos la fecha actual
        fecha_solicitud = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        query = """
            INSERT INTO servicios (nombre_usuario, area, detalle, fecha_solicitud)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (nombre_usuario, area, detalle, fecha_solicitud))
        conexion.commit()
        print("Servicio registrado correctamente")
    except mysql.connector.Error as err:
        print(f"Error al registrar servicio: {err}")
    finally:
        if conexion and conexion.is_connected():
            conexion.close()
