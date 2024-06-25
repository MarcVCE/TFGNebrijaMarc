import os
import logging
import sys
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (Application, CommandHandler, MessageHandler, 
                          filters, ContextTypes, CallbackQueryHandler)
import google.generativeai as genai
import signal
from message_handler import (process_message, handle_specific_commands, 
                             generate_and_send_answer, ask_answer_preference)

# Configurar el registro
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno desde el archivo .env
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")

# Configurar tu API Key de Google
genai.configure(api_key=GOOGLE_API_KEY)

# Inicializar el modelo generativo
model = genai.GenerativeModel(model_name='gemini-pro')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    start_message = (
        "Welcome to Multifunctional Assistant 3000!\n"
        "I am here to help you with your needs, from translating text to providing delicious recipes.\n\n"
        "You can control me by sending these commands:\n\n"
        "General Commands:\n"
        "/start - Show this start message\n\n"
        "Search Commands:\n"
        "scrape: <search term> - Search for scientific articles on PubMed\n"
        "Example: scrape: artificial intelligence\n\n"
        "scrape_link: <link> - Scrape a specific link\n"
        "Example: scrape_link: https://pubmed.ncbi.nlm.nih.gov/34127285/\n\n"
        "For more information on how to use this bot, please visit the Gemini API documentation: https://gemini.google.com/.\n"
        "This bot works with the Google Gemini API. Please avoid asking unethical questions. Thank you!"
    )
    await update.message.reply_text(start_message)


async def message_handler_main(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    received_text, language = await process_message(update=update, context=context)
    using_any_handle_specific_commands = await handle_specific_commands(update=update, 
                                                                        context=context, 
                                                                        received_text=received_text)
    if not using_any_handle_specific_commands:
       await ask_answer_preference(update=update)



async def post_selected_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    preference = query.data
    context.user_data['answer_preference'] = preference
    await generate_and_send_answer(update=query, 
                                   context=context, 
                                   received_text=context.user_data['received_text'], 
                                   language=context.user_data['language'], 
                                   model=model)



async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    # Notificar al usuario del error
    if update and update.effective_message:
        await update.effective_message.reply_text("An unexpected error occurred. Please try again later.")



def main() -> None:
    # Crear la aplicación
    application = Application.builder().token(token=TELEGRAM_API_TOKEN).build()

    # Registrar manejador para el comando /start
    application.add_handler(CommandHandler(command="start", callback=start))

    # Registrar manejador para recibir mensajes
    application.add_handler(MessageHandler(filters=filters.TEXT & ~filters.COMMAND, callback=message_handler_main))
    application.add_handler(MessageHandler(filters=filters.VOICE, callback=message_handler_main))

    # Registrar el CallbackQueryHandler para los botones inline
    application.add_handler(CallbackQueryHandler(callback=post_selected_button))

    # Registrar el manejador de errores
    application.add_error_handler(error_handler)

    def signal_handler(sig, frame):
        print("\nStopping the bot!")
        sys.exit(0)

    # Registrar el manejador de señal para detener el bot
    signal.signal(signal.SIGINT, signal_handler)  # Mata proceso con CTRL+C
    signal.signal(signal.SIGTERM, signal_handler) # Comunica al proceso un apagado “amable” (cerrando conexiones, ficheros y limpiando sus propios búferes)

    # Iniciar el bot
    print("The bot is running. Press Ctrl + C to stop the script.")
    application.run_polling()



if __name__ == '__main__':
    main()
