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

# Nueva función para registrar técnicos
def registrar_tecnico(nombre, telegram_id):
    conexion = None  # Inicializamos la variable
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        query = "INSERT INTO tecnicos (nombre, telegram_id, disponible) VALUES (%s, %s, TRUE)"
        cursor.execute(query, (nombre, telegram_id))
        conexion.commit()
        print("Técnico registrado correctamente.")
    except mysql.connector.Error as err:
        print(f"Error al registrar técnico: {err}")
    finally:
        if conexion and conexion.is_connected():
            conexion.close()

# Función para actualizar el estado de disponibilidad de un técnico
def actualizar_estado_tecnico(telegram_id, disponible):
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor()
        query = "UPDATE tecnicos SET disponible = %s WHERE telegram_id = %s"
        cursor.execute(query, (1 if disponible else 0, telegram_id))  # Convertimos booleano a 1 o 0
        conexion.commit()
        print("Estado de disponibilidad actualizado correctamente.")
    except mysql.connector.Error as err:
        print(f"Error al actualizar estado de disponibilidad: {err}")
    finally:
        if conexion.is_connected():
            conexion.close()


# Función para obtener técnicos disponibles
def obtener_tecnico_disponible():
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor(dictionary=True)
        query = "SELECT * FROM tecnicos WHERE disponible = 1 LIMIT 1"
        cursor.execute(query)
        tecnico = cursor.fetchone()  # Devuelve el primer técnico disponible
        return tecnico
    except mysql.connector.Error as err:
        print(f"Error al obtener técnico disponible: {err}")
        return None
    finally:
        if conexion.is_connected():
            conexion.close()



def obtener_tecnicos_disponibles():
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor(dictionary=True)
        query = "SELECT * FROM tecnicos WHERE disponible = 1"  # Selecciona todos los técnicos disponibles
        cursor.execute(query)
        tecnicos = cursor.fetchall()  # Recupera todos los técnicos disponibles
        return tecnicos
    except mysql.connector.Error as err:
        print(f"Error al obtener técnicos disponibles: {err}")
        return []
    finally:
        if conexion.is_connected():
            conexion.close()




# if __name__ == "__main__":
#     # Prueba para registrar un técnico
#     nombre_tecnico = "Diego Marín"
#     telegram_id = 5217793518  # ID ficticio
#     registrar_tecnico(nombre_tecnico, telegram_id)
    
    
