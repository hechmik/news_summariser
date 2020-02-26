import feedparser
import json

def get_website_article_link_title(feed_name):
    """
    Given a RSS Feed link return the current article with their titles and links
    Parameters
    ----------
    feed_name : str
        Feed RSS URL
    """
    feed = feedparser.parse(feed_name)
    articles_to_download = {}
    for i in range(1, len(feed.entries)):
        key = feed.entries[i].title
        value = feed.entries[i].link
        articles_to_download[key] = value
    return articles_to_download

def get_feeds_articles(fn="config/rss_feed.json"):
    """
    Return the link and title of articles in the given RSS feeds
    Parameters
    ----------
    fn : str
        Filename where RSS Feeds are stored in a JSON array format. Default: "config/rss_feed.json"
    """
    with open(fn, "r") as f:
        feeds = json.load(f)
    articles_infos = []
    for site in feeds:
        articles_infos.append(get_website_article_link_title(site))
    return articles_infos
    

