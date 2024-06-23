import logging
import re
import google.generativeai as genai
import langid
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from myaudiototext import audio_a_texto
from mytexttoaudio import texto_a_audio
from scraping import handle_scrapear, handle_scrapear_enlace, handle_resumen

# Configurar el registro
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Diccionario de idiomas disponibles
idiomas_disponible = {
    "es": "es-ES",  # español
    "fr": "fr-FR",  # francés
    "it": "it-IT",  # italiano
    "pt": "pt-PT",  # portugués
    "de": "de-DE",  # alemán
    "en": "en-GB"   # inglés
}

# Función para formatear la respuesta
def formatear_respuesta(text):
    return re.sub(r"•", " *", text).replace("\n", "\n *")

async def process_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> tuple:
    idioma = "es-ES"  # Por defecto en español
    texto_recibido = ""

    if update.message.voice:
        voice_note_id = update.message.voice.file_id
        audio_file = await context.bot.get_file(voice_note_id)
        audio_path = "Audio.m4a"
        await audio_file.download_to_drive(audio_path)
        
        # Transcribir audio
        texto_recibido, idioma_detectado_nom = audio_a_texto(audio_path)
        if idioma_detectado_nom:
            idioma = idiomas_disponible.get(idioma_detectado_nom, "es-ES")

    else:
        texto_recibido = update.message.text
        # Detectar idioma del texto recibido
        language_info = langid.classify(texto_recibido)
        idioma_detectado_nom = language_info[0]
        if idioma_detectado_nom:
            idioma = idiomas_disponible.get(idioma_detectado_nom, "es-ES")
    
    context.user_data['texto_recibido'] = texto_recibido
    context.user_data['idioma'] = idioma
    return texto_recibido, idioma


async def handle_specific_commands(update: Update, context: ContextTypes.DEFAULT_TYPE, texto_recibido: str) -> bool:
    if texto_recibido.startswith('scrapear:'):
        await handle_scrapear(update, context)
        return True
    elif texto_recibido.startswith('resumen:'):
        await handle_resumen(update, context)
        return True
    elif texto_recibido.startswith('scrapear_enlace:'):
        await handle_scrapear_enlace(update, context)
        return True
    return False


async def preguntar_preferencia_respuesta(update: Update) -> None:
    keyboard = [
        [InlineKeyboardButton("Texto", callback_data='texto')],
        [InlineKeyboardButton("Audio", callback_data='audio')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("¿Cómo quieres recibir la respuesta?", reply_markup=reply_markup)


async def generar_y_enviar_respuesta(
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE, 
        texto_recibido: str, 
        idioma: str, 
        modelo: genai.GenerativeModel
    ) -> None:

    config = genai.GenerationConfig(max_output_tokens=512, temperature=0.1, top_p=1, top_k=32)
    respuesta = modelo.generate_content(contents=texto_recibido, generation_config=config)
    respuesta_text = respuesta.text

    preferencia = context.user_data.get('preferencia_respuesta', 'texto')

    if preferencia == 'audio':
        try:
            texto_a_audio(respuesta_text, idioma)
            await update.message.reply_voice(voice=open('respuesta.mp3', 'rb'))
        except Exception as e:
            logger.error("Error al convertir texto a audio:", exc_info=e)
            await update.message.reply_text("Error al convertir el texto a audio.")
    else:
        await update.message.reply_text(formatear_respuesta(respuesta_text))
