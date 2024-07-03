import logging
import google.generativeai as genai
import langid
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from myaudiototext import audio_to_text
from mytexttoaudio import text_to_audio
from summarylinks import extract_information_json, generate_summary_from_abstract

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

async def process_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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


async def ask_answer_preference(update: Update) -> None:
    keyboard = [
        [InlineKeyboardButton("Text", callback_data='text')],
        [InlineKeyboardButton("Audio", callback_data='audio')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    question_text = "How would you like to receive the answer?"
    await update.message.reply_text(text=question_text, reply_markup=reply_markup)


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
            error_text = "Error converting text to audio:"
            logger.error(msg=error_text, exc_info=e)
            await update.message.reply_text(text=error_text)
    else:
        await update.message.reply_text(text=answer_text)


async def send_summaries_telegram(update: Update, 
                                  context: ContextTypes.DEFAULT_TYPE):
    waiting_message = '_🤖⏳ Our Artificial Intelligence model is working on your task_'
    my_waiting_message = await update.message.reply_text(text=waiting_message, parse_mode="Markdown")
    titles_abstracts_and_links = extract_information_json()
    response_summaries = ""
    for i, (title, abstract, link) in enumerate(titles_abstracts_and_links, start=1):
        summary_from_abstract : str = generate_summary_from_abstract(text=abstract, max_chars_answer=256)
        response_summaries += f"{i}. *{title}*\n{summary_from_abstract.capitalize()}\n\n"
    
    await update.message.reply_text(text=response_summaries, parse_mode="Markdown")
    await update.message.delete(api_kwargs={"message_id":my_waiting_message.message_id})