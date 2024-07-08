# Puedes añadir todos los que encuentres de
# https://stackoverflow.com/questions/39142778/how-to-determine-the-language-of-a-piece-of-text
# o cualquier otro fuente.

# Y añadir a modo comparativo más texto en diferentes idiomas o algo de ruido en plan 
# "Sesi e un test en fransé." , "Esto e une testo en espanyol" o viceversa, 
# teniendo en cuenta que todo esto también supondrá un verdadero reto a los detectores de idioma

from langdetect import detect_langs
from guess_language import guess_language
import chardet
from langid.langid import LanguageIdentifier, model
import matplotlib.pyplot as plt

# Texto de ejemplo para detección de idioma
texts = [
    "This is an English text.",
    "Este es un texto en español.",
    "Ceci est un texte en français.",
    "Dies ist ein deutscher Text.",
    "これは日本語のテキストです。"
]

def detect_with_langid(text):
    identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)
    language, probability = identifier.classify(text)
    return language, probability

def detect_with_langdetect(text):
    try:
        detections = detect_langs(text)
        detections_probabilities = [(str(detection.lang), detection.prob) for detection in detections]
        return detections_probabilities
    except:
        return None

def detect_with_guess_language(text):
    language = guess_language(text)
    return language, None  # guess_language does not provide a probability

def detect_with_chardet(text : str):
    detection = chardet.detect(text.encode())
    return detection['encoding'], detection['confidence']

results = {
    "Text": ["English", "Spanish", "French", "German", "Japanese"],
    "Langid": [],
    "Langdetect": [],
    "GuessLanguage": [],
    "Chardet": []
}

for text in texts:
    print(f"Text: {text}")
    
    # Detect language with langid
    language_langid, probability_langid = detect_with_langid(text)
    results["Langid"].append((language_langid, probability_langid))
    print(f"Langid: {language_langid} with probability {probability_langid}")
    
    # Detect language with langdetect
    detections_langdetect = detect_with_langdetect(text)
    if detections_langdetect:
        results["Langdetect"].append(detections_langdetect[0])  # Suponiendo que tomamos el más probable
        for language, probability in detections_langdetect:
            print(f"Langdetect: {language} with probability {probability}")
    else:
        print("Langdetect: Detection failed.")
    
    # Detect language with guess_language
    lang_guess_language, _ = detect_with_guess_language(text)
    results["GuessLanguage"].append(lang_guess_language)
    print(f"GuessLanguage: {lang_guess_language}")
    
    # Detect language with chardet
    encoding_chardet, confidence_chardet = detect_with_chardet(text)
    results["Chardet"].append((encoding_chardet, confidence_chardet))
    print(f"Chardet: {encoding_chardet} with confidence {confidence_chardet}")

# Preparar datos para el gráfico
texts_labels = results["Text"]
langid_probabilities = [probability for _, probability in results["Langid"]]
langdetect_probabilities = [probability for _, probability in results["Langdetect"]]
chardet_probabilities = [confidence for _, confidence in results["Chardet"]]

# Crear el gráfico comparativo
x = range(len(texts_labels))

plt.figure(figsize=(14, 7))

plt.plot(x, langid_probabilities, label='Langid', marker='o')
plt.plot(x, langdetect_probabilities, label='Langdetect', marker='s')
plt.plot(x, chardet_probabilities, label='Chardet', marker='^')

plt.xlabel('Text')
plt.ylabel('Probability/Confidence')
plt.title('Comparative Language Detection Probabilities by Text')
plt.xticks(x, texts_labels, rotation=45)
plt.legend()
plt.tight_layout()
plt.grid(True)
plt.show()