import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ContextTypes

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
        abstract = soup.find('div', class_='abstract-content selected').get_text(strip=True) if soup.find('div', 'abstract-content selected') else 'No abstract available'
        return title, authors, abstract
    else:
        print('Error al acceder al enlace proporcionado')
        return None, None, None




async def handle_scrapear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.split(':', 1)[1].strip()
    top_results = scrape_pubmed(query)
    if top_results:
        response = "Aquí están los primeros 5 resultados:\n\n"
        for idx, title, authors, link, summary in top_results:
            response += f"{idx}. {title}\n   Autores: {authors}\n   Enlace: {link}\n\n"
        context.user_data['results'] = top_results
        await update.message.reply_text(response)
        
        # Enviar el archivo .txt con todos los resultados
        await update.message.reply_document(document=open('pubmed_articles.txt', 'rb'))
    else:
        await update.message.reply_text('No se encontraron artículos para el término de búsqueda proporcionado.')




async def handle_resumen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        parts = update.message.text.split(':', 2)
        article_number = int(parts[1].strip())
        format_type = parts[2].strip() if len(parts) > 2 else 'APA'
        if 'results' in context.user_data and 1 <= article_number <= len(context.user_data['results']):
            _, title, authors, link, summary = context.user_data['results'][article_number - 1]
            if format_type.lower() == 'apa':
                citation = f"{authors} ({link}). {title}. PubMed."
            else:
                citation = f"{title} por {authors}. Más detalles en {link}."
            await update.message.reply_text(f"Resumen del artículo {article_number}:\n\n{summary}\n\nCita en formato {format_type.upper()}:\n{citation}")
        else:
            await update.message.reply_text('Número de artículo inválido o no se ha realizado una búsqueda previa.')
    except ValueError:
        await update.message.reply_text('Por favor, proporciona un número de artículo válido.')




async def handle_scrapear_enlace(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = update.message.text.split(':', 1)[1].strip()
    title, authors, abstract = scrape_article_link(link)
    if title and authors and abstract:
        response = f"Título: {title}\nAutores: {', '.join(authors)}\nResumen: {abstract}"
        await update.message.reply_text(response)
    else:
        await update.message.reply_text('No se pudo obtener información del enlace proporcionado.')
