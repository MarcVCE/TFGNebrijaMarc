import requests
import json
from os import getenv
import base64

def texto_a_audio(respuesta: str, idioma: str):
    # Tu API key de Google Cloud
    cloud_api = getenv("CLOUD_API")

    # URL de la API de Google Cloud Text-to-Speech (cloud.google.com/text-to-speech)
    url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={cloud_api}"

    # Datos para la solicitud
    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }

    data = {
        "input": {
            "text": respuesta
        },
        "voice": {
            "languageCode": idioma,
            "name": f"{idioma}-Standard-B"  # Cambia esto al tipo de voz que prefieras
        },
        "audioConfig": {
            "audioEncoding": "MP3"
        }
    }

    # Realiza la solicitud POST
    response = requests.post(url=url, headers=headers, data=json.dumps(data))

    # Verifica si la solicitud fue exitosa
    if response.status_code == 200:
        response_json = response.json()
        audio_content = response_json['audioContent']
        # Decodifica el contenido de audio
        audio_content_decoded = base64.b64decode(audio_content)

        # Guarda el audio en un archivo
        with open("respuesta.mp3", "wb") as audio_file:
            audio_file.write(audio_content_decoded)

        print("Conversión de texto a voz completada. Revisa el archivo respuesta.mp3.")
    else:
        print("Error en la solicitud:", response.text)
