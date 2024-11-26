import mysql.connector
from mysql.connector import Error

# Función para conectar a la base de datos
def crear_conexion():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='bot_ia',
            user='root',
            password='',
            port=3308  # Cambia según tu configuración
        )
        return connection
    except Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

# Función para insertar el nombre en la base de datos
def insertar_usuario(nombre):
    connection = crear_conexion()
    if connection is None:
        return
    cursor = connection.cursor()
    query = "INSERT INTO usuarios_chat (nombre) VALUES (%s)"
    cursor.execute(query, (nombre,))
    connection.commit()
    cursor.close()
    connection.close()

# Función para insertar el servicio seleccionado en la base de datos
def insertar_servicio(nombre, area, servicio):
    connection = crear_conexion()
    if connection is None:
        return
    cursor = connection.cursor()
    query = "INSERT INTO servicios (nombre, area, servicio) VALUES (%s, %s, %s)"
    cursor.execute(query, (nombre, area, servicio))
    connection.commit()
    cursor.close()
    connection.close()
