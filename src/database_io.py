from typing import List
from tinydb import TinyDB, Query
import logging


def get_already_summarised_articles(filename: str):
    """
    Query the DB for obtaining articles summarised in the past
    :param filename: path where TinyDB is stored
    :return:
    """
    logging.info("load_already_read_articles >>>")
    try:
        db = TinyDB(filename)
        q = Query()
        articles_already_read = db.search(q.title.exists())
    except Exception as ex:
        logging.error(ex)
        articles_already_read = {}
    if db:
        db.close()
    logging.info("load_already_read_articles <<<")
    return articles_already_read


def get_new_articles(old_articles, current_articles):
    """
    Find, among current articles, the ones that weren't summarised in previous iterations
    :param old_articles: articles already summarised
    :param current_articles: articles that were just obtained from RSS feed(s)
    :return:
    """
    logging.info("get_new_articles >>>")
    if not old_articles:
        return current_articles
    articles_not_yet_summarised = [article for article in current_articles if article not in old_articles]
    logging.info("get_new_articles <<<")
    return articles_not_yet_summarised


def update_parsed_articles(summarised_articles: List[dict], articles_db_fn: str):
    """
    Add the summarised articles in the JSON "DB" file
    :param summarised_articles: articles that were summarised during the last execution
    :param articles_db_fn: filename where the JSON "DB" is stored
    :return:
    """
    logging.info("update_parsed_articles >>>")
    db = TinyDB(articles_db_fn)
    q = Query()
    for article in summarised_articles:
        db.upsert(article, q.url == article['url'])
    db.close()
    logging.info("update_parsed_articles <<<")