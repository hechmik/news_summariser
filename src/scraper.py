import requests
from bs4 import BeautifulSoup

def scrape_page(link, article_class):
    """
    Return the entire article in the given link
    Parameters
    ----------
    link : str
        Article URL

    article_class: str
        CSS Class of the dive that contains all the article paragraphs.
    """
    page = requests.get(link) 
    soup = BeautifulSoup(page.content, 'html.parser')
    article_content= soup.body.find(class_=article_class)
    article = []
    try:

        for paragraph in article_content.find_all('p'):
            sentence = paragraph.get_text()
            if sentence != "":
                article.append(paragraph.get_text())
    except AttributeError:
        print("Can't find article text")
    except:
        print("Strange behaviour")
    return article
    