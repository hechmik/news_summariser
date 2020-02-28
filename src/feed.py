import feedparser

def get_website_article_link_title(feed_name, website):
    """
    Given a RSS Feed link return the current article with their titles and links
    Parameters
    ----------
    feed_name : str
        Feed RSS URL
    """
    feed = feedparser.parse(feed_name)
    articles_to_download = {}
    for i in range(0, len(feed.entries)):
        title = feed.entries[i].title
        url = feed.entries[i].link
        articles_to_download[title] = {}
        articles_to_download[title]['url'] = url
        articles_to_download[title]['source'] = website
    return articles_to_download

def get_feeds_articles(config):
    """
    Return the link and title of articles in the given RSS feeds
    Parameters
    ----------
    config : dict
        Dictionaries where websites infos such as feed URL are stored
    """
    articles_infos = []
    for website in config.keys():
        print(website)
        website_rss =config[website]['rss']
        print(website_rss)
        articles_infos.append(get_website_article_link_title(website_rss, website))
    return articles_infos
    