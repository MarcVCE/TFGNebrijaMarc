import whisper

def audio_to_text(audio_path):
    model = whisper.load_model("small")
    result = model.transcribe(audio_path)
    language = result["language"]
    text = result["text"]
    return text, language
