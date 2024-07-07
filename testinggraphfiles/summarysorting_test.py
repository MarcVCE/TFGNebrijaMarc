import pytest
from summerizediftools import (calculate_word_frequencies, score_sentences, load_file, 
                               extract_title_abstract_and_link, sort_sentences_by_score)
from nltk.tokenize import sent_tokenize

def test_sort_sentences_by_score_from_file():
    # Cargar el contenido del archivo
    content = load_file('pubmed_articlestest.json')
    
    # Extraer el primer artículo con resumen y enlace
    if not content:
        pytest.fail("No se encontraron artículos en el archivo JSON.")
    
    title, summary, link = extract_title_abstract_and_link(content[0])
    if not summary:
        pytest.fail("El primer artículo no tiene resumen.")

    
    sentences = sent_tokenize(summary.lower())
    frequency_word_table = calculate_word_frequencies(summary)
    sentence_scores = score_sentences(sentences, frequency_word_table)
    sorted_sentences = sort_sentences_by_score(sentence_scores)

    # sentence_scores['eight publications addressed symptom clusters.'] = 5

    # Verificar que las oraciones están ordenadas de mayor a menor puntuación
    for i in range(len(sorted_sentences) - 1):
        true_condition = sentence_scores[sorted_sentences[i]] >= sentence_scores[sorted_sentences[i + 1]]
        assert_message = (
            f"Sentence '{sorted_sentences[i]}' with score {sentence_scores[sorted_sentences[i]]} " +
            f"should be greater than or equal to '{sorted_sentences[i + 1]}' " +
            f"with score {sentence_scores[sorted_sentences[i + 1]]}"
        )

        assert true_condition, assert_message 


if __name__ == "__main__":
    pytest.main()
