import feedparser
import json
import logging


def store_articles(data, filename):
    """
    Store articles as json file
    :param data: articles to memorize
    :param filename: file where articles will be stored
    :return:
    """
    logging.info("store_articles >>>")
    with open(filename, 'w') as f:
        f.write(json.dumps(data))
    logging.info("store_articles <<<")


def load_already_read_articles(filename):
    logging.info("load_already_read_articles >>>")
    try:
        with open(filename, 'r') as f:
            articles_already_read = json.load(f)
    except Exception as ex:
        logging.error(ex)
        articles_already_read = []
    logging.info("load_already_read_articles <<<")
    return articles_already_read


def get_new_articles(old_articles, new_articles):
    logging.info("get_new_articles >>>")
    articles_not_yet_summarised = [x for x in new_articles if x not in old_articles]
    logging.info("get_new_articles <<<")
    return articles_not_yet_summarised


def get_website_article_link_title(feed_name, website):
    """
    Given a RSS Feed link return the current article with their titles and links
    :param feed_name: Website name
    :param website:
    :return:
    """
    logging.info("get_website_article_link_title >>>")
    feed = feedparser.parse(feed_name)
    articles_to_download = {}
    for i in range(0, len(feed.entries)):
        title = feed.entries[i].title
        url = feed.entries[i].link
        articles_to_download[title] = {}
        articles_to_download[title]['url'] = url
        articles_to_download[title]['source'] = website
    logging.info("get_website_article_link_title <<<")
    return articles_to_download


def get_feeds_articles(news_dict, old_articles_fn):
    """
    Return the link and title of articles in the given RSS feeds that have not yet been summarised
    :param news_dict: Dictionaries where websites infos such as feed URL are stored
    :param old_articles_fn: Path where already read articles are stored
    :return:
    """
    logging.info("get_feeds_articles >>>")
    articles_infos = []
    for website in news_dict.keys():
        website_rss = news_dict[website]['rss']
        articles_infos.append(get_website_article_link_title(website_rss, website))
    old_articles = load_already_read_articles(old_articles_fn)
    articles_to_summarise = get_new_articles(old_articles, articles_infos)
    logging.info("get_feeds_articles <<<")
    return articles_to_summarise


def update_parsed_articles(summarised_articles, parsed_articles_fn):
    """
    Add the summarised articles in the JSON "DB" file
    :param summarised_articles: articles that were summarised during the last execution
    :param parsed_articles_fn: filename where the JSON "DB" is stored
    :return:
    """
    logging.info("update_parsed_articles >>>")
    old_articles = load_already_read_articles(parsed_articles_fn)
    parsed_articles = old_articles + [x for x in summarised_articles if x not in old_articles]
    store_articles(parsed_articles, parsed_articles_fn)
    logging.info("update_parsed_articles <<<")
