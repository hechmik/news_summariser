import requests
from bs4 import BeautifulSoup
import logging
import re


def is_article_a_multimedia_page(link: str):
    """
    Check if the given link is a multimedia one or not. This is done by simply looking at the final extension
    :param link: URL address
    :return:
    """

    if link.endswith(".html"):
        return False
    elif re.match("(http(s)?:\/\/.+\/.+)(\.[a-z0-9]+)", link):
        return True
    else:
        return False


def scrape_page(link: str, article_class: str, first_paragraph_index: int, last_paragraph_index: int):
    """
    Return the entire article in the given link
    :param link: Article URL
    :param article_class: CSS Class of the dive that contains all the article paragraphs
    :param first_paragraph_index: how many paragraphs should be skipped, starting from the beginning of the article
    :param last_paragraph_index: how many paragraphs should be skipped, starting from the end of the article
    :return:
    """
    logging.info("scrape_page >>>")
    try:
        logging.info(link)
        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                     'Chrome/35.0.1916.47 Safari/537.36 '
        headers = {'User-Agent': user_agent}
        article = []
        if is_article_a_multimedia_page(link):
            return article
        page = requests.get(link, timeout=3, headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        article_content = soup.find("div", class_=article_class)
        article = []
        paragraphs = article_content.find_all('p')
        # Remove, if needed, some of the first and last paragraph(s)
        if first_paragraph_index > 0:
            paragraphs = paragraphs[first_paragraph_index:]
        if last_paragraph_index > 0:
            paragraphs = paragraphs[:-last_paragraph_index]

        for paragraph in paragraphs:
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
