from transformers import BertTokenizer, EncoderDecoderModel
import json

def load_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = json.load(file)
    return content


def extract_title_abstract_and_link(article):
    title_text = article["title"]
    title = title_text.strip() if title_text else None
    link_text = article["link"]
    link = link_text.strip() if link_text else None
    abstract_text = article["abstract"]
    abstract = abstract_text.strip() if abstract_text else None
    return title, abstract, link


def generate_summary_from_abstract(text):
    # Cargar el modelo y el tokenizador
    modelo = EncoderDecoderModel.from_pretrained(
        pretrained_model_name_or_path="patrickvonplaten/bert2bert_cnn_daily_mail")
    tokenizador = BertTokenizer.from_pretrained(
        pretrained_model_name_or_path="bert-base-uncased")
    
    # Tokenizar el texto
    inputs = tokenizador([text], max_length=512, truncation=True, return_tensors="pt")
    
    # Generar el resumen
    resumen_ids = modelo.generate(inputs.input_ids, max_length=150, num_beams=4, early_stopping=True)
    resumen = tokenizador.decode(resumen_ids[0], skip_special_tokens=True)
    
    return resumen

def extract_information_json():
    # Cargar el contenido del archivo
    content = load_file('pubmed_articles.json')
    
    # Extraer títulos, resúmenes y enlaces de los artículos
    titles_abstracts_and_links = []
    for article in content:
        title, abstract, link = extract_title_abstract_and_link(article)
        if abstract and link:
            titles_abstracts_and_links.append((title, abstract, link))
    
    return titles_abstracts_and_links