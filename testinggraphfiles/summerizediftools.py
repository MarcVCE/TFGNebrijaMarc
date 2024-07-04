import json
from nltk import download, tokenize
from transformers import BertTokenizer, EncoderDecoderModel, pipeline
from difflib import SequenceMatcher
import matplotlib.pyplot as plt

# Descargar recursos necesarios de NLTK
download('punkt')

# Función para cargar el archivo JSON
def load_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = json.load(file)
    return content

# Función para extraer título, abstract y enlace
def extract_title_abstract_and_link(article : str):
    title_text = article["title"]
    title = title_text.strip() if title_text else None
    link_text = article["link"]
    link = link_text.strip() if link_text else None
    abstract_text = article["abstract"]
    abstract = abstract_text.strip() if abstract_text else None
    return title, abstract, link

# Función para calcular la frecuencia de las palabras
def calculate_word_frequencies(text : str):
    words = tokenize.word_tokenize(text.lower())
    frequency_word_table = {}
    for word in words:
        if word.isalnum():  # Considerar solo palabras alfanuméricas
            if word in frequency_word_table:
                frequency_word_table[word] = frequency_word_table[word] + 1
            else:
                frequency_word_table[word] = 1

    return frequency_word_table

# Función para puntuar las oraciones
def score_sentences(sentences : list[str], frequency_word_table):
    sentence_scores = {}
    for i, sentence in enumerate(sentences):
        words = tokenize.word_tokenize(sentence.lower())
        sentence_score = 0
        for word in words:
            if word in frequency_word_table:
                sentence_score = sentence_score + frequency_word_table[word]

        # Añadir importancia de la posición (las primeras oraciones tienen más peso)
        bonus_value_per_start_sentence = (1 / (i + 1))
        sentence_scores[sentence] = sentence_score * bonus_value_per_start_sentence

    
    return sentence_scores

# Función para generar resumen basado en frecuencia de palabras
def generate_summary_nltk(text, max_chars):
    sentences = tokenize.sent_tokenize(text)
    if not sentences:
        return ""
    
    frequency_word_table = calculate_word_frequencies(text)
    sentence_scores = score_sentences(sentences, frequency_word_table)
    
    # Ordenar las oraciones por puntuación
    ranked_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)
    
    summary = ""
    for sentence in ranked_sentences:
        if len(sentence) <= max_chars:
            summary = summary + ' ' + sentence
        else:
            summary = summary + ' ' + sentence
            summary = summary[1:max_chars + 1]
            break
    
    return summary

# Función para generar resumen con BERT    (Transformadores ahora mismo es el state-of-art de NLP)
def generate_summary_transformers_bert(text, max_chars):
    model_name = "patrickvonplaten/bert2bert_cnn_daily_mail"
    model : EncoderDecoderModel = EncoderDecoderModel.from_pretrained(model_name)
    tokenizer : BertTokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

    inputs = tokenizer(text=text, return_tensors="pt", truncation=True, max_length=512)
    summary_ids = model.generate(inputs=inputs["input_ids"], num_beams=4, early_stopping=True)
    summary = tokenizer.decode(token_ids=summary_ids[0], skip_special_tokens=True)

    summary = summary[:max_chars]
    return summary



# Función para generar resumen con Facebook BART
def generate_summary_transformers_facebook(text, max_chars):
    summarizer = pipeline(task="summarization", model="facebook/bart-large-cnn")
    # do_sample=False desactiva el muestreo aleatorio. Se usa la 
    # estrategia de beam search para generar el resumen más probable. (como el num_beans = 4)
    summary = summarizer(text, max_length=1024, do_sample=False)
    summary_text = summary[0]['summary_text']
    
    summary_text = summary_text[:max_chars]
    return summary_text

# Función para ajustar el tamaño del resumen a un número exacto de caracteres
def adjust_summary_length(summary, max_chars):
    return summary[:max_chars]

# Función para calcular similitud entre textos
def calculate_similarity(text1, text2):
    return SequenceMatcher(None, text1, text2).ratio()

# Función principal
if __name__ == "__main__":
    # Cargar el contenido del archivo
    content = load_file('pubmed_articlestest.json')
    
    # Extraer títulos, resúmenes y enlaces de los artículos
    titles_summaries_and_links = []
    for article in content:
        title, summary, link = extract_title_abstract_and_link(article)
        if summary and link:
            titles_summaries_and_links.append((title, summary, link))
    
    # Generar resúmenes y calcular originalidad
    originalities = []
    for i, (title, summary, link) in enumerate(titles_summaries_and_links, start=1):
        print(f"Generando resúmenes para el artículo {i}: {title}")
        nltk_summary = generate_summary_nltk(text=summary, max_chars=200)
        bert_summary = generate_summary_transformers_bert(text=summary, max_chars=200)
        facebook_summary = generate_summary_transformers_facebook(text=summary, max_chars=200)
        
        # Ajustar los resúmenes a 200 caracteres exactos
        nltk_summary = adjust_summary_length(nltk_summary, 200)
        bert_summary = adjust_summary_length(bert_summary, 200)
        facebook_summary = adjust_summary_length(facebook_summary, 200)
        
        if len(nltk_summary) != 200:
            print(f"Problema al generar resumen con NLTK para el artículo {i}")
        if len(bert_summary) != 200:
            print(f"Problema al generar resumen con BERT para el artículo {i}")
        if len(facebook_summary) != 200:
            print(f"Problema al generar resumen con Facebook para el artículo {i}")
        
        original_nltk = 1 - calculate_similarity(summary, nltk_summary)
        original_bert = 1 - calculate_similarity(summary, bert_summary)
        original_facebook = 1 - calculate_similarity(summary, facebook_summary)
        
        originalities.append({
            "title": f"Resumen {i}",
            "link": link,
            "original_nltk": original_nltk,
            "original_bert": original_bert,
            "original_facebook": original_facebook
        })
        
        print(f"{i}. '{title}'\n")
        print(f"Resumen NLTK (200 chars):\n{nltk_summary}\n")
        print(f"Resumen BERT (200 chars):\n{bert_summary}\n")
        print(f"Resumen Facebook (200 chars):\n{facebook_summary}\n")
        print("Enlace:", link)
        print("\n" + "-"*80 + "\n")

    # Crear gráficos de originalidad
    titles = [item['title'] for item in originalities]
    original_nltk = [item['original_nltk'] for item in originalities]
    original_bert = [item['original_bert'] for item in originalities]
    original_facebook = [item['original_facebook'] for item in originalities]

    x = range(len(titles))
    
    plt.figure(figsize=(14, 7))
    
    plt.plot(x, original_nltk, label='NLTK', marker='o', linestyle='--')
    plt.plot(x, original_bert, label='BERT', marker='s')
    plt.plot(x, original_facebook, label='Facebook', marker='^')
    
    plt.xlabel('Resumen')
    plt.ylabel('Originalidad (1 - Similarity)')
    plt.title('Comparación de Originalidad Entre Métodos de Resumen')
    plt.xticks(x, titles, rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.show()
