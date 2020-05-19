from typing import List
from tinydb import TinyDB, Query
import logging


def retrieve_items_from_db(filename: str, items_to_retrieve: str):
    """
    Query the DB for obtaining the specified items
    :param filename: path where TinyDB is stored
    :param items_to_retrieve: whether to retrieve articles summarised in the past or summaries already sent via telegram
    :return:
    """
    logging.info("retrieve_items_from_db >>>")
    try:
        db = TinyDB(filename)
        q = Query()
        if items_to_retrieve == "articles":
            query_result = db.search(q.title.exists())
        elif items_to_retrieve == "messages":
            query_result = db.search(q.fn.exists())
        db.close()
    except Exception as ex:
        logging.error(ex)
        query_result = {}
    logging.info("retrieve_items_from_db <<<")
    return query_result


def get_delta(old_items, current_items):
    """
    Find, among current items, the ones that aren't in old items
    :param old_items: items associated with previous iterations (e.g. articles already summarised, old summaries already sent via Telegram)
    :param current_items: items associated with the current iteration (e.g. articles just obtained from RSS feed(s), summaries in the target directory)
    :return:
    """
    logging.info("get_delta >>>")
    if not old_items:
        return current_items
    delta = [item for item in current_items if item not in old_items]
    logging.info("get_delta <<<")
    return delta


def update_items_in_db(items: List[dict], articles_db_fn: str, items_to_store:str):
    """
    Add the given items in the JSON "DB" file
    :param items: items used in the last execution that should be added to the given db
    :param articles_db_fn: filename where the JSON "DB" is stored
    :param items_to_store: whether to update articles or messages db
    :return:
    """
    logging.info("update_items_in_db >>>")
    db = TinyDB(articles_db_fn)
    q = Query()
    for item in items:
        if items_to_store == "articles":
            db.upsert(item, q.url == item['url'])
        elif items_to_store == "messages":
            db.upsert(item, q.fn == item['fn'])
    db.close()
    logging.info("update_items_in_db <<<")
