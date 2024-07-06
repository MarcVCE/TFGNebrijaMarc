import pytest
from summerizediftools import (generate_summary_nltk, generate_summary_transformers_bert, load_file,
                               generate_summary_transformers_facebook, extract_title_abstract_and_link)

def test_summary_length():
    # Cargar el contenido del archivo
    content = load_file('pubmed_articlestest.json')
    
    if not content:
        pytest.fail("No se encontraron artículos en el archivo JSON.")
    
    for i, article in enumerate(content):
        title, summary, link = extract_title_abstract_and_link(article)
      
        # Generar resumen con NLTK y verificar la longitud
        nltk_summary = generate_summary_nltk(text=summary, max_chars=200)
        true_condition_nltk_summary = len(nltk_summary) == 200
        assert_message_nltk_summary = f"Artículo {i}: NLTK summary length is {len(nltk_summary)}, expected 200"
        assert true_condition_nltk_summary, assert_message_nltk_summary
        
        # Generar resumen con BERT y verificar la longitud
        bert_summary = generate_summary_transformers_bert(text=summary, max_chars=200)
        true_condition_bert_summary = len(bert_summary) == 200
        assert_message_bert_summary = f"Artículo {i}: BERT summary length is {len(bert_summary)}, expected 200"
        assert true_condition_bert_summary, assert_message_bert_summary
        
        # Generar resumen con Facebook BART y verificar la longitud
        facebook_summary = generate_summary_transformers_facebook(text=summary, max_chars=200)
        true_condition_facebook_summary = len(facebook_summary) == 200
        assert_message_facebook_summary = f"Artículo {i}: Facebook summary length is {len(facebook_summary)}, expected 200"
        assert true_condition_facebook_summary, assert_message_facebook_summary

if __name__ == "__main__":
    pytest.main()