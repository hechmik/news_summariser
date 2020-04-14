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
    try:
        logging.info(link)
        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        headers = {'User-Agent': user_agent}
        article = []
        # If the link is a podcast don't bother downloading it
        if link.endswith(".mp3"):
            return article
        page = requests.get(link, timeout=3, headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        article_content = soup.body.find(class_=article_class)
        article = []
        for paragraph in article_content.find_all('p'):
            sentence = paragraph.get_text()
            if sentence != "":
                article.append(paragraph.get_text())
    except AttributeError as ae:
        logging.error("Can't find article text for {}".format(link))
        logging.error(ae)
    except Exception as e:
        logging.error("Error while parsing article {}".format(link))
        logging.error(e)
    return article
