import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ContextTypes
import json
from typing import List


def scrape_article_with_article_number(url_article_number : str):
    url_article = f"https://pubmed.ncbi.nlm.nih.gov{url_article_number}"
    response_article = requests.get(url_article)
    if response_article.status_code == 200:
        soup = BeautifulSoup(response_article.content, 'html.parser')
        abstract_raw = soup.find(id="eng-abstract")
        abstract = abstract_raw.get_text(strip=True) if abstract_raw else None
    else:
        abstract = None    # None también lo interpreta como False, por eso se puede hacer if abstract:

    return abstract


def scrape_pubmed_pageinfo_to_txt(query, 
                                  max_results=5):
    url = f"https://pubmed.ncbi.nlm.nih.gov/?term={query}"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        articles : List[BeautifulSoup] = soup.find_all('article', class_='full-docsum')

        results = []
        for idx, article in enumerate(articles, 1):
            title = article.find('a', class_='docsum-title').get_text(strip=True)
            url_article_number = article.find('a', class_='docsum-title').get('href')
            abstract = scrape_article_with_article_number(url_article_number=url_article_number)

            if abstract:  # None también lo interpreta como False, por eso se puede hacer if abstract:
                repetead_article = False
                for saved_article in results:
                    if saved_article['abstract'] == abstract:
                       repetead_article = True
                
                if not repetead_article: 
                    authors = (article.find('span', class_='docsum-authors full-authors').get_text(strip=True) 
                               if article.find('span', 'docsum-authors full-authors') else 'No authors listed')
    
                    link = "https://pubmed.ncbi.nlm.nih.gov" + article.find('a', class_='docsum-title').get('href')
                    json_information = {
                            "idx":idx, 
                            "title":title, 
                            "authors":authors, 
                            "link":link, 
                            "abstract":abstract
                        }
                    results.append(json_information)

        # Obtener los primeros 5 resultados para el chat
        top_results = results[:max_results]

        # Guardar todos los resultados en un archivo .json
        with open(file='pubmed_articles.json', mode='w', encoding='utf-8') as file:
            json.dump(
                        obj=top_results, 
                        fp=file, 
                        indent=4,
                        ensure_ascii=False
                     )

        return top_results
    else:
        print('Error accessing PubMed')
        return []
    


async def handle_scraping_answer_telegram(update: Update, 
                                          context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args) # Coge los valores y los une ejemplo [[inteligencia],[artificial]]
    top_results = scrape_pubmed_pageinfo_to_txt(query)
    if top_results:
        response = "Here are the top 5 results:\n\n"
        for jsoninfo in top_results:
            response += (f"*{jsoninfo['idx']}. {jsoninfo['title']}*\n"   
                         + f"*Authors*: {jsoninfo['authors']}\n*Link*: {jsoninfo['link']}\n\n")
        context.user_data['results'] = top_results
        await update.message.reply_text(text=response, parse_mode="Markdown")
        
        # Enviar el archivo .json con todos los resultados
        await update.message.reply_document(document=open('pubmed_articles.json', 'rb'))
    else:
        await update.message.reply_text('No articles found for the provided search term.')



# Still not add abstract in main.py start message prompt and handle_specific_commands from message_handler.py
async def handle_abstract_answer_telegram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        parts = update.message.text.split(':', 2)
        article_number = int(parts[1].strip())
        format_type = parts[2].strip() if len(parts) > 2 else 'APA'
        if 'results' in context.user_data and 1 <= article_number <= len(context.user_data['results']):
            _, title, authors, link, abstract = context.user_data['results'][article_number - 1]
            if format_type.lower() == 'apa':
                citation = f"{authors} ({link}). {title}. PubMed."
            else:
                citation = f"{title} by {authors}. More details at {link}."
                my_text = (f"Abstract of article {article_number}:\n\n{abstract}\n\n" +
                        f" Citation in {format_type.upper()} format:\n{citation}")
            await update.message.reply_text(text=my_text)
        else:
            error_text = 'Invalid article number or no previous search performed.'
            await update.message.reply_text(text=error_text)
    except ValueError:
        alert_text = 'Please provide a valid article number.'
        await update.message.reply_text(text=alert_text)



def scrape_article_link(link):
    response = requests.get(link)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.find('h1', class_='heading-title').get_text(strip=True)
        authors_soup : List[BeautifulSoup] = soup.find_all('a', class_='full-name')
        authors = [author.get_text(strip=True) for author in authors_soup]
        abstract = (soup.find(id='eng-abstract').get_text(strip=True) 
                    if soup.find(id='eng-abstract') else 'No abstract available')
        return title, authors, abstract
    else:
        print('Error accessing the provided link')
        return None, None, None
    


async def handle_scraping_link_answer_telegram(update: Update, 
                                               context: ContextTypes.DEFAULT_TYPE):
    link = context.args[0]  # Coge el primer valor del context.args = la url pasada
    title, authors, abstract = scrape_article_link(link=link)
    if title and authors and abstract:
        response = f"Title: {title}\nAuthors: {', '.join(authors)}\nAbstract: {abstract}"
        await update.message.reply_text(response)
    else:
        error_text = 'Could not retrieve information from the provided link.'
        await update.message.reply_text(text=error_text)
