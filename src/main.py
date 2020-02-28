import feed
import scraper
import json
import time

if __name__ == "__main__":

    with open("config/websites.json", "r") as f:
        website_infos = json.load(f)
    articles_infos = feed.get_feeds_articles(website_infos)
    articles = {}
    for feed in articles_infos:
        for title in feed.keys():
            print(title)
            source = feed[title]['source']
            main_div_class = website_infos[source]['main_class']
            article_url = feed[title]['url']
            print("source: {}, main_div: {}, url: {}".format(source, main_div_class, article_url))
            text = scraper.scrape_page(article_url, main_div_class)
            articles[title] = text
            time.sleep(2)
    print(articles)