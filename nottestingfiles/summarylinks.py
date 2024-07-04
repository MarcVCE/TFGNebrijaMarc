import math
from transformers import BertTokenizer, EncoderDecoderModel
import json

def load_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = json.load(file)
    return content


def extract_title_abstract_and_link(article : str):
    title_text = article["title"]
    title = title_text.strip() if title_text else None
    link_text = article["link"]
    link = link_text.strip() if link_text else None
    abstract_text = article["abstract"]
    abstract = abstract_text.strip() if abstract_text else None
    return title, abstract, link


def calculate_avg_token_length(text, tokenizer : BertTokenizer):
    total_value_tokens = 0
    total_tokens = 0
    tokens = tokenizer.tokenize(text=text) # Con el tokenizador
    total_value_tokens = sum(len(token) for token in tokens) # Ejemplo tokens = [9, 24, 31 , etc] = yo que sé,
                                                             # suma de valores 250
    total_tokens = len(tokens)  # Ejemplo: Hay 45 tokens en esa lista de tokens 
    
    avg_token_length = total_value_tokens / total_tokens if total_tokens > 0 else 0  # Media de tamaño de tokens = 5,555
    return avg_token_length


def generate_summary_from_abstract(text, max_chars_answer):
    # Cargar el modelo y el tokenizador
    model_name = "patrickvonplaten/bert2bert_cnn_daily_mail"
    model : EncoderDecoderModel = EncoderDecoderModel.from_pretrained(
        pretrained_model_name_or_path=model_name) # fine tuned from bert model
    tokenizer : BertTokenizer = BertTokenizer.from_pretrained(
        pretrained_model_name_or_path="bert-base-uncased")


    # Tokenizar el texto, in bert tokenizers, it's truly either 256 or 512 per tokenizer model
    max_tokens_allowed_to_tokenize_per_text_input = 512
    inputs = tokenizer(text=text, max_length=max_tokens_allowed_to_tokenize_per_text_input, 
                       truncation=True, return_tensors="pt") # Lo haces de esta forma y no con .tokenize porque es la única forma que
                                                             # acepta otros parámetros que no son simplemente el texto, pero la forma
                                                             # correcta si fuese sólo texto es con .tokenize, como en el otro uso que
                                                             # se le da en el fichero.

    avg_token_length = calculate_avg_token_length(text=text, tokenizer=tokenizer)

    # Aproximar el número de tokens para el límite de caracteres deseado
    established_max_output_tokens = math.ceil(max_chars_answer / avg_token_length)
    
    # Generar el resumen
    summaries_ids = model.generate(inputs=inputs["input_ids"], max_length=established_max_output_tokens, 
                                   num_beams=4, early_stopping=True)
    summary = tokenizer.decode(token_ids=summaries_ids[0], skip_special_tokens=True)

     
    # Verificar que el resumen no exceda el límite de caracteres y ajustar si es necesario
    if len(summary) > max_chars_answer or summary[-1] != ".":
        # Recortar el resumen al límite de caracteres especificado
        trunc_summary = summary[:max_chars_answer]
        # Buscar el último delimitador de oración antes del límite de caracteres
        last_period = trunc_summary.rfind('.')
        last_exclamation = trunc_summary.rfind('!')
        last_question = trunc_summary.rfind('?')
        
        # Encontrar el último delimitador que aparece en el texto truncado
        last_delimiter = max(last_period, last_exclamation, last_question)
        
        # Si no se encuentra ningún delimitador, recortar en el último espacio
        if last_delimiter == -1:
            summary = trunc_summary[:trunc_summary.rfind(' ')]
        else:
            summary = trunc_summary[:last_delimiter + 1]

    
    return summary

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