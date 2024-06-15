import whisper

def audio_a_texto(audio_path):
    model = whisper.load_model("small")
    result = model.transcribe(audio_path)
    idioma = result["language"]
    texto = result["text"]
    return texto, idioma
