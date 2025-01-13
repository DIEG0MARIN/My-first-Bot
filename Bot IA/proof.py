# import pytest
# from telegram import Update
# from telegram.ext import CallbackContext
# from bot import handle_message, button  # Asegúrate de importar tus funciones del bot

# @pytest.mark.asyncio
# async def test_handle_message():
#     # Simula un mensaje de texto de un usuario
#     update = Update.de_json({
#         "update_id": 10000,  # ID del update
#         "message": {
#             "message_id": 1,  # ID del mensaje
#             "text": "Hola",
#             "chat": {"id": 12345, "type": "private"},  # Tipo de chat
#             "from": {"id": 67890, "is_bot": False, "first_name": "UsuarioPrueba"},
#             "date": 1633022842  # Marca de tiempo Unix
#         }
#     }, bot=None)
#     context = CallbackContext(dispatcher=None)
#     await handle_message(update, context)
#     # Verifica que el estado inicial sea correcto
#     assert context.user_data.get('estado') == 'esperando_nombre'

# @pytest.mark.asyncio
# async def test_button():
#     # Simula un evento de botón
#     update = Update.de_json({
#         "update_id": 10001,  # ID del update
#         "callback_query": {
#             "id": "unique-id",  # ID único para la consulta
#             "chat_instance": "chat-instance-id",  # ID único del chat
#             "data": "reserva_util_si",
#             "message": {
#                 "message_id": 2,  # ID del mensaje
#                 "chat": {"id": 12345, "type": "private"},  # Tipo de chat
#                 "date": 1633022842  # Marca de tiempo Unix
#             },
#             "from": {"id": 67890, "is_bot": False, "first_name": "UsuarioPrueba"},
#         }
#     }, bot=None)
#     context = CallbackContext(dispatcher=None)
#     await button(update, context)
#     # Verifica que el estado se haya reiniciado
#     assert context.user_data.get('estado') is None


# from db import obtener_tecnico_disponible

# tecnico = obtener_tecnico_disponible()
# if tecnico:
#     print("Técnico disponible encontrado:", tecnico)
# else:
#     print("No hay técnicos disponibles.")


import asyncio
from db import obtener_tecnicos_disponibles
from telegram import Bot

TOKEN = '8080603920:AAGTVZXZASnE-ulJFtUrPnlRULvdZgDGW9w'

async def prueba_comunicacion_tecnicos():
    bot = Bot(token=TOKEN)

    # Obtén los técnicos disponibles
    tecnicos = obtener_tecnicos_disponibles()
    if not tecnicos:
        print("No hay técnicos disponibles.")
        return

    # Envía un mensaje a cada técnico disponible
    for tecnico in tecnicos:
        try:
            await bot.send_message(
                chat_id=tecnico['telegram_id'],
                text="🔔 Prueba de comunicación: Este es un mensaje de prueba del bot. Por favor, responde si lo recibes."
            )
            print(f"Mensaje enviado al técnico: {tecnico['nombre']} ({tecnico['telegram_id']})")
        except Exception as e:
            print(f"Error al enviar mensaje al técnico {tecnico['nombre']}: {e}")

# Ejecutar la prueba
if __name__ == '__main__':
    asyncio.run(prueba_comunicacion_tecnicos())
