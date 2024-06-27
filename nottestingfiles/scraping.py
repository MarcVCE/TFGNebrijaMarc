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


def scrape_pubmed_pageinfo_to_json(query, 
                                  max_results=5):
    results = []
    page = 1
    index_article = 1
    while len(results) < 5:
        
        url = f"https://pubmed.ncbi.nlm.nih.gov/?term={query}&page={page}"
        response = requests.get(url)
        if response.status_code == 200:
            page += 1
            soup = BeautifulSoup(response.content, 'html.parser')
            articles : List[BeautifulSoup] = soup.find_all('article', class_='full-docsum')

            for _, article in enumerate(articles, 1):
                title = article.find('a', class_='docsum-title').get_text(strip=True)
                url_article_number = article.find('a', class_='docsum-title').get('href')
                abstract = scrape_article_with_article_number(url_article_number=url_article_number)
                year_raw = article.find('span', class_="short-journal-citation").get_text(strip=True)
                year = year_raw.split(" ")[-1].replace("." , "")
                url_article_number_for_json = url_article_number.split("/")[1]
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
                                "idx":index_article, 
                                "title":title, 
                                "year":year,
                                "article_code":url_article_number_for_json,
                                "authors":authors, 
                                "link":link, 
                                "abstract":abstract
                            }
                        
                        index_article += 1
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
        else:
            print('Error accessing PubMed')
            return []
    
    return top_results


async def handle_scraping_answer_telegram(update: Update, 
                                          context: ContextTypes.DEFAULT_TYPE):
    
    waiting_message = '_🤖⏳ Our Artificial Intelligence model is working on your task_'
    my_waiting_message = await update.message.reply_text(text=waiting_message, parse_mode="Markdown")
    query = " ".join(context.args) # Coge los valores y los une ejemplo [[inteligencia],[artificial]]
    top_results = scrape_pubmed_pageinfo_to_json(query)
    if top_results:
        response = "Here are the top 5 results:\n\n"
        for jsoninfo in top_results:
            response += (f"*{jsoninfo['idx']}. {jsoninfo['title']}*\n"   
                         + f"*Authors*: {jsoninfo['authors']}\n*Link*: {jsoninfo['link']}\n\n")
        context.user_data['results'] = top_results
        await update.message.reply_text(text=response, parse_mode="Markdown")
        # Enviar el archivo .json con todos los resultados
        await update.message.reply_document(document=open('pubmed_articles.json', 'rb'))
        # Borra mensaje de espera
        await update.message.delete(api_kwargs={"message_id":my_waiting_message.message_id})
    else:
        not_found_message = 'No articles found for the provided search term.'
        await update.message.reply_text(text=not_found_message)
        await update.message.delete(api_kwargs={"message_id":my_waiting_message.message_id})



async def handle_articles_apa_answer_telegram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        waiting_message = '_🤖⏳ Our Artificial Intelligence model is working on your task_'
        my_waiting_message = await update.message.reply_text(text=waiting_message, parse_mode="Markdown")
        my_text = ""
        for article in context.user_data['results']:
            authors = article['authors']
            year = article['year']
            title = article['title']
            article_code_number = article['article_code']
            format_type = "apa"
            citation = f"{authors} ({year}). {title} PubMed."
            my_text += (f"*Article {article_code_number}* \n" +
                        f"*Citation in {format_type.upper()} format*:\n{citation}\n\n")
        await update.message.reply_text(text=my_text, parse_mode="Markdown")
        await update.message.delete(api_kwargs={"message_id":my_waiting_message.message_id})
    except:
        error_text = 'There was a problem in the answer generation'
        await update.message.reply_text(text=error_text)
        await update.message.delete(api_kwargs={"message_id":my_waiting_message.message_id})



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
    
    waiting_message = '_🤖⏳ Our Artificial Intelligence model is working on your task_'
    my_waiting_message = await update.message.reply_text(text=waiting_message, parse_mode="Markdown")
    link = context.args[0]  # Coge el primer valor del context.args = la url pasada
    title, authors, abstract = scrape_article_link(link=link)
    if title and authors and abstract:
        response = f"*Title:* {title}\n*Authors:* {', '.join(authors)}\n*Abstract:* {abstract}"
        await update.message.reply_text(text=response, parse_mode="Markdown")
        await update.message.delete(api_kwargs={"message_id":my_waiting_message.message_id})
    else:
        error_text = 'Could not retrieve information from the provided link.'
        await update.message.reply_text(text=error_text)
        await update.message.delete(api_kwargs={"message_id":my_waiting_message.message_id})
