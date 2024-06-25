import logging
import re
import google.generativeai as genai
import langid
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from myaudiototext import audio_to_text
from mytexttoaudio import text_to_audio
from scraping import handle_scrapear, handle_scrapear_enlace, handle_resumen

# Configurar el registro
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Diccionario de idiomas disponibles
available_languages = {
    "es": "es-ES",  # español
    "fr": "fr-FR",  # francés
    "it": "it-IT",  # italiano
    "pt": "pt-PT",  # portugués
    "de": "de-DE",  # alemán
    "en": "en-GB"   # inglés
}

# Función para formatear la respuesta
def format_answer(text):
    return re.sub(r"•", " *", text).replace("\n", "\n *")

async def process_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> tuple:
    language = "es-ES"  # Por defecto en español
    received_text = ""

    if update.message.voice:
        voice_note_id = update.message.voice.file_id
        audio_file = await context.bot.get_file(file_id=voice_note_id)
        audio_path = "Audio.m4a"
        await audio_file.download_to_drive(custom_path=audio_path)
        
        # Transcribir audio
        received_text, detected_language_nom = audio_to_text(audio_path=audio_path)
        if detected_language_nom:
            language = available_languages.get(detected_language_nom, "es-ES")

    else:
        received_text = update.message.text
        # Detectar idioma del texto recibido
        language_info = langid.classify(received_text)
        detected_language_nom = language_info[0]
        if detected_language_nom:
            language = available_languages.get(detected_language_nom, "es-ES")
    
    context.user_data['received_text'] = received_text
    context.user_data['language'] = language
    return received_text, language


async def handle_specific_commands(update: Update, context: ContextTypes.DEFAULT_TYPE, received_text: str) -> bool:
    if received_text.startswith('scrape:'):
        await handle_scrapear(update, context)
        return True
    elif received_text.startswith('summary:'):
        await handle_resumen(update, context)
        return True
    elif received_text.startswith('scrape_link:'):
        await handle_scrapear_enlace(update, context)
        return True
    return False


async def ask_answer_preference(update: Update) -> None:
    keyboard = [
        [InlineKeyboardButton("Text", callback_data='text')],
        [InlineKeyboardButton("Audio", callback_data='audio')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("How would you like to receive the answer?", reply_markup=reply_markup)


async def generate_and_send_answer(
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE, 
        received_text: str, 
        language: str, 
        model: genai.GenerativeModel
    ) -> None:

    config = genai.GenerationConfig(max_output_tokens=512, temperature=0.1, top_p=1, top_k=32)
    answer = model.generate_content(contents=received_text, generation_config=config)
    answer_text = answer.text

    preference = context.user_data.get('answer_preference', 'text')

    if preference == 'audio':
        try:
            text_to_audio(answer=answer_text, language=language)
            await update.message.reply_voice(voice=open(file='respuesta.mp3', mode='rb'))
        except Exception as e:
            logger.error("Error converting text to audio:", exc_info=e)
            await update.message.reply_text("Error converting text to audio:")
    else:
        await update.message.reply_text(format_answer(text=answer_text))
