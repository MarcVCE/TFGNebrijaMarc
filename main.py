import os
import logging
import sys
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import google.generativeai as genai
import re
import signal
from scraping import scrape_pubmed, scrape_article_link

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
modelo = genai.GenerativeModel('gemini-pro')

# Función para formatear la respuesta
def formatear_respuesta(text):
    return re.sub(r"•", " *", text).replace("\n", "\n *")

async def start(update: Update, context: CallbackContext) -> None:
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

async def message_handler(update: Update, context: CallbackContext) -> None:
    entrada = update.message.text

    if entrada.startswith('scrapear:'):
        query = entrada.split(':', 1)[1].strip()
        top_results = scrape_pubmed(query)
        if top_results:
            response = "Aquí están los primeros 5 resultados:\n\n"
            for idx, title, authors, link, summary in top_results:
                response += f"{idx}. {title}\n   Autores: {authors}\n   Enlace: {link}\n\n"
            context.user_data['results'] = top_results
            await update.message.reply_text(response)
            
            # Enviar el archivo .txt con todos los resultados
            await update.message.reply_document(document=open('pubmed_articles.txt', 'rb'))
        else:
            await update.message.reply_text('No se encontraron artículos para el término de búsqueda proporcionado.')
    
    elif entrada.startswith('resumen:'):
        try:
            parts = entrada.split(':', 2)
            article_number = int(parts[1].strip())
            format_type = parts[2].strip() if len(parts) > 2 else 'APA'
            if 'results' in context.user_data and 1 <= article_number <= len(context.user_data['results']):
                _, title, authors, link, summary = context.user_data['results'][article_number - 1]
                if format_type.lower() == 'apa':
                    citation = f"{authors} ({link}). {title}. PubMed."
                else:
                    citation = f"{title} por {authors}. Más detalles en {link}."
                await update.message.reply_text(f"Resumen del artículo {article_number}:\n\n{summary}\n\nCita en formato {format_type.upper()}:\n{citation}")
            else:
                await update.message.reply_text('Número de artículo inválido o no se ha realizado una búsqueda previa.')
        except ValueError:
            await update.message.reply_text('Por favor, proporciona un número de artículo válido.')

    elif entrada.startswith('scrapear_enlace:'):
        link = entrada.split(':', 1)[1].strip()
        title, authors, abstract = scrape_article_link(link)
        if title and authors and abstract:
            response = f"Título: {title}\nAutores: {', '.join(authors)}\nResumen: {abstract}"
            await update.message.reply_text(response)
        else:
            await update.message.reply_text('No se pudo obtener información del enlace proporcionado.')
    
    else:
        # Obtener respuesta del modelo generativo
        respuesta = modelo.generate_content(entrada)
        respuesta_text = respuesta.text
        await update.message.reply_text(formatear_respuesta(respuesta_text))

async def error_handler(update: Update, context: CallbackContext) -> None:
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    # Notificar al usuario del error
    if update.effective_message:
        await update.effective_message.reply_text("Ocurrió un error inesperado. Inténtalo de nuevo más tarde.")

def main() -> None:
    # Crear la aplicación
    application = Application.builder().token(token=TELEGRAM_API_TOKEN).build()

    # Registrar manejador para el comando /start
    application.add_handler(CommandHandler(command="start", callback=start))

    # Registrar manejador para recibir mensajes
    application.add_handler(MessageHandler(filters=filters.TEXT & ~filters.COMMAND, callback=message_handler))

    # Registrar el manejador de errores
    application.add_error_handler(error_handler)
    print("El bot está en funcionamiento. Presiona Ctrl + C para detener el script.")

    def signal_handler(sig, frame):
        print("\n¡Deteniendo el bot!")
        sys.exit(0)

    # Registrar el manejador de señal para detener el bot
    signal.signal(signal.SIGINT, signal_handler)  # Mata proceso con CTRL+C
    signal.signal(signal.SIGTERM, signal_handler) # Comunina al proceso un apagado “amable” (cerrando 
                                                  # conexiones, ficheros y limpiando sus propios búfer)

    # Iniciar el bot
    print("El bot está en funcionamiento. Presiona Ctrl + C para detener el script.")
    application.run_polling()

if __name__ == '__main__':
    main()
