import feed
import summariser
import scraper
import logging
import json
from datetime import datetime

if __name__ == "__main__":

    logging.root.handlers = []
    logging.basicConfig(format='%(asctime)s|%(name)s|%(levelname)s| %(message)s',
                        level=logging.WARN,
                        filename="news_summariser.log")

    # set up logging to console
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # set a format which is simpler for console use
    formatter = logging.Formatter(fmt='%(asctime)s|%(name)s|%(levelname)s| %(message)s',
                                  datefmt="%d-%m-%Y %H:%M:%S")
    console.setFormatter(formatter)
    logging.getLogger("").addHandler(console)
    logging.info('Application started')
    # Load configuration files
    with open("config/websites.json", "r") as f:
        website_infos = json.load(f)
    with open("config/settings.json", "r") as f:
        settings = json.load(f)

    already_read_articles_fn = settings['already_read_articles_fn']
    articles_infos = feed.get_feeds_articles(website_infos, already_read_articles_fn)
    summaries = {}
    # Download, if needed, necessary libraries for text processing
    summariser.download_dependencies()
    # Load Word Embedding model
    model = summariser.load_word_embedding_model()
    for title in articles_infos.keys():
        source = articles_infos[title]['source']
        main_div_class = website_infos[source]['main_class']
        article_url = articles_infos[title]['url']
        logging.debug("source: {}, url: {}".format(source, article_url))
        text = scraper.scrape_page(article_url, main_div_class)
        if len(text) > 0:
            summary = ""
            try:
                summary = summariser.create_summary(text,
                                                    model,
                                                    settings['reduction_factor'],
                                                    settings['summarise_paragraphs'])
            except Exception as e:
                logging.error("unable to create summary for {}".format(article_url))
                logging.error(e)

            if summary != "":
                summaries[title] = {}
                summaries[title]['summary'] = summary
                summaries[title]['url'] = article_url
    logging.info("Finished to summarise articles!")
    # Store summaries and update DB only if there are new summaries
    if summaries != {}:
        summary_fn = settings['summaries_fn'].format(str(datetime.now()))
        logging.info("Summaries stored")
        with open(summary_fn, 'w') as file:
            file.write(json.dumps(summaries))
        feed.update_parsed_articles(articles_infos, already_read_articles_fn)

        logging.info("Updated articles db")
