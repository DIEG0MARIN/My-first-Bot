import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from db import registrar_usuario, registrar_servicio

# Configuración del registro
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)

TOKEN = '8080603920:AAGTVZXZASnE-ulJFtUrPnlRULvdZgDGW9w'

# Manejar los mensajes
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    if 'estado' not in context.user_data:
        await update.message.reply_text("👋 ¡Hola! Soy TechFUCS, tu asistente técnico en la FUCS. ¿Cómo te llamas? 🤖")
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

            await update.message.reply_text(f"Hola, {nombre}. ¿De qué facultad o edificio te comunicas? 💻", reply_markup=reply_markup)
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
        await update.message.reply_text(f"Gracias por indicarlo. ¿En qué servicio necesitas ayuda en {area_otros}? 🤖💻", reply_markup=servicio_markup)
        context.user_data['estado'] = 'esperando_servicio'

    elif context.user_data['estado'] == 'esperando_detalle_otros':
        detalle_otros = text.strip()
        await update.message.reply_text(f"📋 Gracias por la información. Registramos tu solicitud: {detalle_otros}")

        # Mensaje directo al usuario indicando que un especialista se pondrá en contacto
        await update.message.reply_text(
            "🔧 ¡Estamos ajustando nuestras tuercas! Un especialista pronto se pondrá en contacto contigo. Por favor espera... 🤖💻"
        )

        nombre = context.user_data.get('nombre', 'Desconocido')
        area = context.user_data.get('area', 'No especificado')
        registrar_servicio(nombre, area, detalle_otros)

        context.user_data['estado'] = None

# Manejar botones
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if 'estado' in context.user_data and context.user_data['estado'] == 'esperando_area':
        if query.data == 'area_otros':
            await query.message.reply_text("Por favor, escribe el nombre de la dependencia o área a la que perteneces. 💻")
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
            await query.message.reply_text(f"¡Gracias por indicarlo! ¿En qué servicio necesitas ayuda en {area_seleccionada}? 🤖💻", reply_markup=servicio_markup)
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
            await query.message.reply_text(f"Gracias por seleccionarlo. TechFUCS está procesando tu solicitud de {categoria}. Cuéntanos más detalles. 🤖💬")
            context.user_data['estado'] = 'esperando_detalle_otros'

        elif servicio_seleccionado == 'reserva_auditorio':
            enlace_reserva = "https://ejemplo.com/reserva-auditorio"
            await query.message.reply_text(f"Para realizar tu reserva, por favor diligencia los datos en el siguiente enlace: [Reserva Auditorio JGC]({enlace_reserva})", parse_mode="Markdown")
            
# Configuración del bot
def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button))
    application.run_polling()

if __name__ == '__main__':
    main()
