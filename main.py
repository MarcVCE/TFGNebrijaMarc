import os
import logging
import sys
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai
import signal
from message_handler import process_message, handle_specific_commands, generar_y_enviar_respuesta

# Configurar el registro
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno desde el archivo .env
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")

# Configurar tu API Key de Google
genai.configure(api_key=GOOGLE_API_KEY)

# Inicializar el modelo generativo
modelo = genai.GenerativeModel('gemini-pro')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    start_message = (
        "¡Bienvenido a Asistente Multifuncional 3000!\n"
        "Estoy aquí para ayudarte con tus necesidades, desde traducir texto hasta brindarte recetas deliciosas.\n\n"
        "Puedes controlarme enviando estos comandos:\n\n"
        "Comandos Generales:\n"
        "/start - Muestra este mensaje de inicio\n\n"
        "Comandos de Búsqueda:\n"
        "scrapear: <término de búsqueda> - Busca artículos científicos en PubMed\n"
        "Ejemplo: scrapear: inteligencia artificial\n\n"
        "scrapear_enlace: <enlace> - Realiza scraping de un enlace específico\n"
        "Ejemplo: scrapear_enlace: https://pubmed.ncbi.nlm.nih.gov/34127285/\n\n"
        "Para más información sobre cómo usar este bot, por favor visita la documentación de la API de Gemini: https://gemini.google.com/.\n"
        "Este bot funciona con la API de Gemini de Google. Por favor, evita hacer preguntas no éticas. ¡Gracias!"
    )
    await update.message.reply_text(start_message)

async def message_handler_main(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    texto_recibido, idioma = await process_message(update, context)
    using_any_handle_specific_commands = await handle_specific_commands(update, context, texto_recibido)
    if not using_any_handle_specific_commands:
       await generar_y_enviar_respuesta(update, context, texto_recibido, idioma, modelo)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    # Notificar al usuario del error
    if update and update.effective_message:
        await update.effective_message.reply_text("Ocurrió un error inesperado. Inténtalo de nuevo más tarde.")


def main() -> None:
    # Crear la aplicación
    application = Application.builder().token(token=TELEGRAM_API_TOKEN).build()

    # Registrar manejador para el comando /start
    application.add_handler(CommandHandler(command="start", callback=start))

    # Registrar manejador para recibir mensajes
    application.add_handler(MessageHandler(filters=filters.TEXT & ~filters.COMMAND, callback=message_handler_main))
    application.add_handler(MessageHandler(filters=filters.VOICE, callback=message_handler_main))

    # Registrar el manejador de errores
    application.add_error_handler(error_handler)

    def signal_handler(sig, frame):
        print("\n¡Deteniendo el bot!")
        sys.exit(0)

    # Registrar el manejador de señal para detener el bot
    signal.signal(signal.SIGINT, signal_handler)  # Mata proceso con CTRL+C
    signal.signal(signal.SIGTERM, signal_handler) # Comunica al proceso un apagado “amable” (cerrando 
                                                  # conexiones, ficheros y limpiando sus propios búferes)

    # Iniciar el bot
    print("El bot está en funcionamiento. Presiona Ctrl + C para detener el script.")
    application.run_polling()

if __name__ == '__main__':
    main()
