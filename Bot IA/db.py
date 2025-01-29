import mysql.connector
from datetime import datetime
import logging


def obtener_conexion():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # Sin contraseña
        port=3308,  # Puerto de tu MySQL según lo configurado
        database="bot_ia"  # Nombre correcto de tu base de datos
    )


# Registrar un usuario
def registrar_usuario(nombre):
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        query = "INSERT INTO usuarios (nombre) VALUES (%s)"
        cursor.execute(query, (nombre,))
        conexion.commit()
        logging.info("Usuario registrado correctamente.")
    except mysql.connector.Error as err:
        logging.error(f"Error al registrar usuario: {err}")
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()


# Registrar un usuario con Telegram ID
def registrar_usuario_con_telegram_id(nombre, telegram_id):
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor(dictionary=True)

        # Verificar si el usuario ya existe
        query_check = "SELECT * FROM usuarios WHERE nombre = %s"
        cursor.execute(query_check, (nombre,))
        usuario = cursor.fetchone()

        if usuario:
            cursor.fetchall()  # 🟢 Limpia cualquier resultado pendiente
            cursor.close()  # 🟢 Cierra el cursor antes de abrir otro
            cursor = conexion.cursor()  # 🟢 Reabre el cursor correctamente

            # Si el usuario ya existe, actualiza el telegram_id
            query_update = "UPDATE usuarios SET telegram_id = %s WHERE nombre = %s"
            cursor.execute(query_update, (telegram_id, nombre))
            logging.info(f"Usuario {nombre} actualizado con telegram_id {telegram_id}")
        else:
            cursor.close()  # 🟢 Asegura que el cursor anterior se cierre antes de la inserción
            cursor = conexion.cursor()

            # Si no existe, lo inserta
            query_insert = "INSERT INTO usuarios (nombre, telegram_id) VALUES (%s, %s)"
            cursor.execute(query_insert, (nombre, telegram_id))
            logging.info(f"Usuario {nombre} registrado con telegram_id {telegram_id}")

        conexion.commit()
    except mysql.connector.Error as err:
        logging.error(f"Error al registrar usuario con telegram_id: {err}")
    finally:
        if cursor:
            cursor.close()  # ✅ Cierra el cursor correctamente
        if conexion.is_connected():
            conexion.close()  # ✅ Cierra la conexión correctamente


# Registrar un servicio
def registrar_servicio(nombre_usuario, area, detalle):
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        fecha_solicitud = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        query = """
            INSERT INTO servicios (nombre_usuario, area, detalle, fecha_solicitud, estado)
            VALUES (%s, %s, %s, %s, 'pendiente')
        """
        cursor.execute(query, (nombre_usuario, area, detalle, fecha_solicitud))
        conexion.commit()
        return cursor.lastrowid  # Retorna el ID del servicio registrado
    except mysql.connector.Error as err:
        logging.error(f"Error al registrar servicio: {err}")
        return None
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()


# Verificar el estado de un caso
def verificar_estado_caso(servicio_id):
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        query = "SELECT estado FROM servicios WHERE id = %s"
        cursor.execute(query, (servicio_id,))
        servicio = cursor.fetchone()
        return servicio and servicio['estado'] == 'asignado'
    except mysql.connector.Error as err:
        logging.error(f"Error al verificar estado del caso: {err}")
        return True  # Asume que fue tomado en caso de error
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()


# Asignar un caso a un técnico
def asignar_caso_a_tecnico(servicio_id, tecnico_id):
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        query = """
            UPDATE servicios
            SET tecnico_id = %s, estado = 'asignado'
            WHERE id = %s AND estado = 'pendiente'
        """
        cursor.execute(query, (tecnico_id, servicio_id))
        conexion.commit()
        logging.info("Caso asignado correctamente al técnico.")
    except mysql.connector.Error as err:
        logging.error(f"Error al asignar caso al técnico: {err}")
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()


# Obtener el ID de Telegram del usuario asociado a un caso
def obtener_id_usuario_del_caso(servicio_id):
    conexion = obtener_conexion()
    try:
        cursor = conexion.cursor(dictionary=True)
        query = """
            SELECT usuarios.telegram_id
            FROM servicios
            INNER JOIN usuarios ON servicios.nombre_usuario = usuarios.nombre
            WHERE servicios.id = %s
        """
        cursor.execute(query, (servicio_id,))
        usuario = cursor.fetchone()
        
        # Limpieza de resultados pendientes
        cursor.fetchall()  # Esto asegura que no queden resultados no leídos
        
        return usuario['telegram_id'] if usuario else None
    except mysql.connector.Error as err:
        logging.error(f"Error al obtener el ID del usuario: {err}")
        return None
    finally:
        # Cierra el cursor y la conexión
        if cursor:
            cursor.close()
        if conexion.is_connected():
            conexion.close()


# Obtener técnicos disponibles
def obtener_tecnicos_disponibles():
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        query = "SELECT * FROM tecnicos WHERE disponible = TRUE"
        cursor.execute(query)
        return cursor.fetchall()
    except mysql.connector.Error as err:
        logging.error(f"Error al obtener técnicos disponibles: {err}")
        return []
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()


# Actualizar la disponibilidad de un técnico
def actualizar_estado_tecnico(tecnico_id, disponible):
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        query = "UPDATE tecnicos SET disponible = %s WHERE id = %s"
        cursor.execute(query, (disponible, tecnico_id))
        conexion.commit()
        logging.info("Estado de disponibilidad del técnico actualizado correctamente.")
    except mysql.connector.Error as err:
        logging.error(f"Error al actualizar estado del técnico: {err}")
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()


# Obtener un técnico por ID
def obtener_tecnico_por_id(tecnico_id):
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        query = "SELECT * FROM tecnicos WHERE id = %s"
        cursor.execute(query, (tecnico_id,))
        return cursor.fetchone()
    except mysql.connector.Error as err:
        logging.error(f"Error al obtener técnico por ID: {err}")
        return None
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()




