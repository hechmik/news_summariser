import feedparser
import json


def write_json(data, filename='articles.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


def load_json(filename='articles.json'):

    try:
        with open(filename, 'r') as f:
            articles_already_read = json.load(f)
    except Exception as ex:
        print(ex)
        articles_already_read = []
    return articles_already_read


def get_new_articles(old_articles, new_articles):
    articles_not_yet_summarised = [x for x in new_articles if x not in old_articles]
    return articles_not_yet_summarised


def get_website_article_link_title(feed_name, website):
    """
    Given a RSS Feed link return the current article with their titles and links
    :param feed_name: Website name
    :param website:
    :return:
    """
    """
    
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
    Return the link and title of articles in the given RSS feeds who have not yet been summarised
    :param config: Dictionaries where websites infos such as feed URL are stored"
    :return:
    """

    articles_infos = []
    for website in config.keys():
        print(website)
        website_rss = config[website]['rss']
        print(website_rss)
        articles_infos.append(get_website_article_link_title(website_rss, website))
    old_articles = load_json()
    articles_to_summarise = get_new_articles(old_articles, articles_infos)
    return articles_to_summarise


def update_parsed_articles(summarised_articles):
    """
    Add the summarised articles in the JSON "DB" file
    :param summarised_articles: articles that were summarised during the last execution
    :return:
    """
    old_articles = load_json()
    parsed_articles = old_articles + [x for x in summarised_articles if x not in old_articles]
    write_json(parsed_articles)
