import requests
from bs4 import BeautifulSoup
import logging


def scrape_page(link, article_class):
    """
    Return the entire article in the given link
    :param link: Article URL
    :param article_class: CSS Class of the dive that contains all the article paragraphs.
    :return:
    """
    logging.info("scrape_page >>>")
    page = requests.get(link) 
    soup = BeautifulSoup(page.content, 'html.parser')
    article_content = soup.body.find(class_=article_class)
    article = []
    try:
        for paragraph in article_content.find_all('p'):
            sentence = paragraph.get_text()
            if sentence != "":
                article.append(paragraph.get_text())
    except AttributeError:
        logging.error("Can't find article text for {}".format(link))
    except Exception as e:
        logging.error("Error while parsing article {}".format(link))
        logging.error(e)
    return article
