import feedparser
import logging
import database_io


def get_website_article_link_title(feed_name, website, articles_infos):
    """
    Given a RSS Feed link return the current article with their titles and links
    :param feed_name: RSS Feed URL
    :param website: name of the website
    :param articles_infos: list where parsed articles will be stored
    :return:
    """
    logging.info("get_website_article_link_title >>>")
    feed = feedparser.parse(feed_name)
    for i in range(0, len(feed.entries)):
        title = feed.entries[i].title
        url = feed.entries[i].link
        current_article = {'title': title, 'url': url, 'source': website}
        articles_infos.append(current_article)
    logging.info("get_website_article_link_title <<<")
    return articles_infos


def get_feeds_articles(news_dict, old_articles: list):
    """
    Return the link and title of articles in the given RSS feeds that have not yet been summarised
    :param news_dict: Dictionaries where websites infos such as feed URL are stored
    :param old_articles: List of already read articles
    :return:
    """
    logging.info("get_feeds_articles >>>")
    articles_infos = []
    for website in news_dict.keys():
        website_rss = news_dict[website]['rss']
        articles_infos = get_website_article_link_title(website_rss, website, articles_infos)
    articles_to_summarise = database_io.get_new_articles(old_articles, articles_infos)
    logging.info("get_feeds_articles <<<")
    return articles_to_summarise

