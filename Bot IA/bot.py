import logging
import mysql.connector
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CallbackQueryHandler, CommandHandler
from db import registrar_usuario, registrar_servicio, actualizar_estado_tecnico, obtener_tecnicos_disponibles, obtener_conexion,obtener_id_usuario_del_caso,asignar_caso_a_tecnico,verificar_estado_caso
from db import registrar_usuario_con_telegram_id
import random


# Configuración del registro
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)

TOKEN = '8080603920:AAGTVZXZASnE-ulJFtUrPnlRULvdZgDGW9w'

# Manejar los mensajes
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    # Capturar el `telegram_id` del usuario
    telegram_id = update.message.from_user.id
    nombre_usuario = update.message.from_user.full_name
    
    
    # Logging para verificar el registro del usuario
    logging.info(f"Registrando usuario {nombre_usuario} con telegram_id {telegram_id}")

    
    
    # Registrar al usuario en la base de datos si no existe
    registrar_usuario_con_telegram_id(nombre_usuario, telegram_id)
    
    
    text = update.message.text

    if 'estado' not in context.user_data:
        await update.message.reply_text("👋 ¡Hola! Soy Gauss Σ, su asistente técnico de la FUCS. ¿Podría indicarme su nombre para continuar? 🤖")
        context.user_data['estado'] = 'esperando_nombre'

    elif context.user_data['estado'] == 'esperando_nombre':
        nombre = text.strip()
        if all(x.isalpha() or x.isspace() for x in nombre):
            context.user_data['nombre'] = nombre
            registrar_usuario(nombre)

            keyboard = [
                [InlineKeyboardButton("Ciencias Básicas", callback_data='ciencias_basicas')],
                [InlineKeyboardButton("Edificio SAPD", callback_data='edificio_sapd')],
                [InlineKeyboardButton("Bienestar", callback_data='bienestar')],
                [InlineKeyboardButton("Ciencias del Movimiento", callback_data='ciencias_movimiento')],
                [InlineKeyboardButton("Otros", callback_data='area_otros')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                f"Hola, {nombre}. ¿De que edificio te comunicas? 💻", 
                reply_markup=reply_markup
            )
            context.user_data['estado'] = 'esperando_area'
        else:
            await update.message.reply_text("Por favor, ingresa un nombre válido (solo letras y espacios).")

    elif context.user_data['estado'] == 'esperando_area_otros':
        area_otros = text.strip()
        context.user_data['area'] = area_otros
        servicio_keyboard = [
            [InlineKeyboardButton("Audiovisual", callback_data='servicio_audiovisual')],
            [InlineKeyboardButton("Red", callback_data='servicio_red')],
            [InlineKeyboardButton("Soporte Equipo", callback_data='servicio_equipo')],
            [InlineKeyboardButton("Reserva Auditorio JGC", callback_data='reserva_auditorio')],
            [InlineKeyboardButton("Otros", callback_data='servicio_otros')],
            [InlineKeyboardButton("Regresar", callback_data='regresar_area')],
        ]
        servicio_markup = InlineKeyboardMarkup(servicio_keyboard)
        await update.message.reply_text(
            f"Gracias por indicarlo. ¿En qué servicio necesitas ayuda en {area_otros}? 🤖💻", 
            reply_markup=servicio_markup
        )
        context.user_data['estado'] = 'esperando_servicio'

    elif context.user_data['estado'] == 'esperando_detalle_otros':
        detalle_otros = text.strip()
        await update.message.reply_text(f"📋 Gracias por la información. Registramos tu solicitud: {detalle_otros}")


     # Registrar el servicio y obtener su ID
        nombre = context.user_data.get('nombre', 'Desconocido')
        area = context.user_data.get('area', 'No especificado')
        detalle_otros = text.strip()
        servicio_id = registrar_servicio(nombre, area, detalle_otros)  # Esto ahora devuelve el ID del servicio registrado


    # Logging para confirmar el registro del servicio
        logging.info(f"Servicio registrado con ID: {servicio_id} para el usuario {nombre}")



     # Guardar el ID del servicio en el contexto
        context.user_data['servicio_id'] = servicio_id




        # Mensaje directo al usuario indicando que un especialista se pondrá en contacto
        await update.message.reply_text(
            "🔧 ¡Estamos ajustando nuestras tuercas! Un especialista pronto se pondrá en contacto contigo. Por favor espera... 🤖💻"
        )

        # Verifica que el servicio se haya registrado correctamente
        if not servicio_id:
            await update.message.reply_text("⚠️ Hubo un problema al registrar el servicio. Por favor, intenta nuevamente.")
            return
        
        
        

        # Notificar a los técnicos disponibles
        # Notificar a los técnicos disponibles
tecnicos_disponibles = obtener_tecnicos_disponibles()

if tecnicos_disponibles:
    tecnico_seleccionado = random.choice(tecnicos_disponibles)  # ✅ Técnico aleatorio
    

async def asignar_tecnico_automaticamente(context, servicio_id, nombre, area, detalle_otros):
    """
    Asigna automáticamente un técnico aleatorio y notifica al usuario y al técnico.
    """
    tecnicos_disponibles = obtener_tecnicos_disponibles()

    if tecnicos_disponibles:
        tecnico_seleccionado = random.choice(tecnicos_disponibles)  # ✅ Selecciona técnico aleatorio
        
        # Asigna el caso en la base de datos
        asignar_caso_a_tecnico(servicio_id, tecnico_seleccionado['id'])

        # Obtener ID de usuario para notificación
        usuario_id = obtener_id_usuario_del_caso(servicio_id)
        
        if usuario_id:
            await context.bot.send_message(
                chat_id=usuario_id,
                text=f"🔧 Tu caso ha sido asignado al técnico {tecnico_seleccionado['nombre']}. Pronto se pondrán en contacto contigo."
            )
        
        # Notificar al técnico asignado
        await context.bot.send_message(
            chat_id=tecnico_seleccionado['telegram_id'],
            text=f"✅ Se te ha asignado un nuevo caso:\n"
            f"👤 Usuario: {nombre}\n"
            f"🏢 Área: {area}\n"
            f"📋 Detalles: {detalle_otros}\n"
            f"Por favor, contacta al usuario para atender su solicitud."
        )
    else:
        logging.warning("No hay técnicos disponibles en este momento.")










# Manejar botones
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if 'estado' in context.user_data and context.user_data['estado'] == 'esperando_area':
        if query.data == 'area_otros':
            await query.message.reply_text(
                "Por favor, escribe el nombre de la dependencia o área a la que perteneces. 💻"
            )
            context.user_data['estado'] = 'esperando_area_otros'
        else:
            area_seleccionada = query.data
            context.user_data['area'] = area_seleccionada

            servicio_keyboard = [
                [InlineKeyboardButton("Audiovisual", callback_data='servicio_audiovisual')],
                [InlineKeyboardButton("Red", callback_data='servicio_red')],
                [InlineKeyboardButton("Soporte Equipo", callback_data='servicio_equipo')],
                [InlineKeyboardButton("Reserva Auditorio JGC", callback_data='reserva_auditorio')],
                [InlineKeyboardButton("Otros", callback_data='servicio_otros')],
                [InlineKeyboardButton("Regresar", callback_data='regresar_area')],
            ]
            servicio_markup = InlineKeyboardMarkup(servicio_keyboard)
            await query.message.reply_text(
                f"¡Gracias por indicarlo! ¿En qué servicio necesitas ayuda en {area_seleccionada}? 🤖💻", 
                reply_markup=servicio_markup
            )
            context.user_data['estado'] = 'esperando_servicio'

    elif 'estado' in context.user_data and context.user_data['estado'] == 'esperando_servicio':
        servicio_seleccionado = query.data

        if servicio_seleccionado == 'regresar_area':
            keyboard = [
                [InlineKeyboardButton("Ciencias Básicas", callback_data='ciencias_basicas')],
                [InlineKeyboardButton("Edificio SAPD", callback_data='edificio_sapd')],
                [InlineKeyboardButton("Bienestar", callback_data='bienestar')],
                [InlineKeyboardButton("Ciencias del Movimiento", callback_data='ciencias_movimiento')],
                [InlineKeyboardButton("Otros", callback_data='area_otros')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text("Regresando a la selección de áreas. 🤖", reply_markup=reply_markup)
            context.user_data['estado'] = 'esperando_area'

        elif servicio_seleccionado in ['servicio_audiovisual', 'servicio_red', 'servicio_equipo', 'servicio_otros']:
            mensaje_categoria = {
                'servicio_audiovisual': "Audiovisual",
                'servicio_red': "Red",
                'servicio_equipo': "Soporte Equipo",
                'servicio_otros': "Otros"
            }
            categoria = mensaje_categoria[servicio_seleccionado]
            await query.message.reply_text(
                f"Gracias por seleccionarlo. TechFUCS está procesando tu solicitud de {categoria}. Cuéntanos más detalles. 🤖💬"
            )
            context.user_data['estado'] = 'esperando_detalle_otros'

        elif servicio_seleccionado == 'reserva_auditorio':
            enlace_reserva = "https://ejemplo.com/reserva-auditorio"
            await query.message.reply_text(
                f"Para realizar tu reserva, por favor diligencia los datos en el siguiente enlace: [Reserva Auditorio JGC]({enlace_reserva})",
                parse_mode="Markdown"
            )

            # Teclado con opciones para evaluar la utilidad
            evaluacion_keyboard = [
                [InlineKeyboardButton("😊 Sí", callback_data='reserva_util_si')],
                [InlineKeyboardButton("🙁 No", callback_data='reserva_util_no')],
            ]
            evaluacion_markup = InlineKeyboardMarkup(evaluacion_keyboard)
            await query.message.reply_text(
                "¿Te ha sido útil esta información? 😊", reply_markup=evaluacion_markup
            )
            context.user_data['estado'] = 'esperando_reserva_respuesta'

    elif 'estado' in context.user_data and context.user_data['estado'] == 'esperando_reserva_respuesta':
        if query.data == 'reserva_util_si':
            # Teclado con opciones de calificación
            estrellas_keyboard = [
                [InlineKeyboardButton("⭐", callback_data='1_estrella'), InlineKeyboardButton("⭐⭐", callback_data='2_estrellas')],
                [InlineKeyboardButton("⭐⭐⭐", callback_data='3_estrellas'), InlineKeyboardButton("⭐⭐⭐⭐", callback_data='4_estrellas')],
                [InlineKeyboardButton("⭐⭐⭐⭐⭐", callback_data='5_estrellas')],
            ]
            estrellas_markup = InlineKeyboardMarkup(estrellas_keyboard)
            await query.message.reply_text(
                "¡Gracias! Para nosotros es un placer ayudarte. Por favor califica nuestro servicio: 😊",
                reply_markup=estrellas_markup
            )

        elif query.data in ['1_estrella', '2_estrellas', '3_estrellas', '4_estrellas', '5_estrellas']:
            # Mensaje de agradecimiento y reinicio del estado
            await query.message.reply_text(
                "😊 ¡Gracias por tu calificación! Si necesitas algo más, no dudes en escribirme en cualquier momento. ¡Hasta pronto! 🤖"
            )
            context.user_data.clear()  # Reinicia el estado del usuario

        elif query.data == 'reserva_util_no':
            await query.message.reply_text(
                "🤖💻 En un momento, uno de nuestros especialistas se pondrá en contacto contigo. Por favor espera... ⚙️😊"
            )
            context.user_data.clear()  # Reinicia el estado del usuario

async def actualizar_disponibilidad(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        args = context.args
        if len(args) != 1 or args[0].lower() not in ['true', 'false']:
            await update.message.reply_text("Uso incorrecto. Usa: /estado_disponibilidad true o /estado_disponibilidad false")
            return

        disponible = args[0].lower() == 'true'
        actualizar_estado_tecnico(update.message.from_user.id, disponible)

        estado = "disponible" if disponible else "no disponible"
        await update.message.reply_text(f"Tu estado de disponibilidad ha sido actualizado a: {estado}.")
    except Exception as e:
        logging.error(f"Error actualizando disponibilidad: {e}")
        await update.message.reply_text("Ocurrió un error al intentar actualizar tu disponibilidad.")


######################################################################################

async def manejar_botones_prueba(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    logging.info(f"Callback de prueba recibido: {query.data}")
    if query.data == "aceptar_prueba":
        await query.edit_message_text("✅ Has aceptado la prueba.")
    elif query.data == "rechazar_prueba":
        await query.edit_message_text("❌ Has rechazado la prueba.")

    
    
    
async def prueba_botones(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Aceptar", callback_data="aceptar_prueba")],
        [InlineKeyboardButton("Rechazar", callback_data="rechazar_prueba")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    logging.info("Mostrando botones de prueba.")
    await update.message.reply_text("Presiona un botón:", reply_markup=reply_markup)






#################################


     
async def verificar_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id  # Obtiene el ID del usuario
    await update.message.reply_text(f"Tu ID de Telegram es: {user_id}")


# Configuración del bot
def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()

    # Handler para mensajes de texto
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Handlers para comandos
    application.add_handler(CommandHandler("estado_disponibilidad", actualizar_disponibilidad))
    application.add_handler(CommandHandler("verificar_id", verificar_id))
    application.add_handler(CommandHandler("prueba_botones", prueba_botones))

    # Handler genérico para otros botones (si fuera necesario)
    application.add_handler(CallbackQueryHandler(button))






   



    application.run_polling()

if __name__ == '__main__':
    main()