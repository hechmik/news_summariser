import feed
import summariser
import scraper
import json
import time

if __name__ == "__main__":

    with open("config/websites.json", "r") as f:
        website_infos = json.load(f)
    articles_infos = feed.get_feeds_articles(website_infos)
    summaries = {}
    # Download, if needed, necessary libraries for text processing
    summariser.download_dependencies()
    # Load Word Embedding model
    model = summariser.load_word_embedding_model()
    for feed in articles_infos:
        for title in feed.keys():
            print(title)
            source = feed[title]['source']
            main_div_class = website_infos[source]['main_class']
            article_url = feed[title]['url']
            print("source: {}, url: {}".format(source, article_url))
            text = scraper.scrape_page(article_url, main_div_class)
            if len(text) > 0:
                summary = ""
                try:
                    summary = summariser.create_summary(text)
                except Exception as e:
                    print("unable to create summary for {}".format(article_url))
                    print(e)

                if summary != "":
                    summaries[title] = {}
                    summaries[title]['summary'] = summariser.create_summary(text, model)
                    summaries[title]['url'] = article_url
    print("Finished to summarise articles!")
    with open('output_summaries.json', 'w') as file:
        file.write(json.dumps(summaries))
