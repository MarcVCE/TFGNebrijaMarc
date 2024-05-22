import requests
from bs4 import BeautifulSoup

def scrape_pubmed(query, max_results=5):
    url = f"https://pubmed.ncbi.nlm.nih.gov/?term={query}"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = soup.find_all('article', class_='full-docsum')

        results = []
        for idx, article in enumerate(articles, 1):
            title = article.find('a', class_='docsum-title').get_text(strip=True)

            summary = (article.find('div', class_='full-view-snippet').get_text(strip=True) 
                       if article.find('div', 'full-view-snippet') else 'No summary available')
            
            authors = (article.find('span', class_='docsum-authors full-authors').get_text(strip=True) 
                       if article.find('span', 'docsum-authors full-authors') else 'No authors listed')
            
            link = "https://pubmed.ncbi.nlm.nih.gov" + article.find('a', class_='docsum-title')['href']
            results.append((idx, title, authors, link, summary))

        # Obtener los primeros 5 resultados para el chat
        top_results = results[:max_results]

        # Guardar todos los resultados en un archivo .txt
        with open('pubmed_articles.txt', 'w', encoding='utf-8') as file:
            for idx, title, authors, link, summary in results:
                file.write(f"{idx}. {title}\n   Autores: {authors}\n   Enlace: {link}\n   Resumen: {summary}\n\n")

        return top_results
    else:
        print('Error al acceder a PubMed')
        return []

def scrape_article_link(link):
    response = requests.get(link)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.find('h1', class_='heading-title').get_text(strip=True)
        authors = [author.get_text(strip=True) for author in soup.find_all('a', class_='full-name')]
        abstract = soup.find('div', class_='abstract-content selected').get_text(strip=True) if soup.find('div', class_='abstract-content selected') else 'No abstract available'
        return title, authors, abstract
    else:
        print('Error al acceder al enlace proporcionado')
        return None, None, None
