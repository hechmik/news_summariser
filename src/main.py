import feed
import summariser
import scraper
import database_io
import logging
import json
import schedule
from datetime import datetime


def store_summaries():
    summary_fn = settings['summaries_fn'].format(str(datetime.now()))
    with open(summary_fn, 'w') as file:
        file.write(json.dumps(summaries))
    logging.info("Summaries stored")


def summarise_current_article():
    summary = ""
    try:
        summary = summariser.create_summary(text,
                                            model,
                                            n=settings['reduction_factor'],
                                            min_words_in_sentence=settings['min_words_in_sentence'],
                                            algorithm=settings['algorithm'])
    except Exception as e:
        logging.error("Unable to create summary for {}".format(article_url))
        logging.error(e)
    if summary != "":
        current_article_summary_info = {"title": article['title'],
                                        "summary": summary,
                                        "url": article_url}
        summaries.append(current_article_summary_info)


def summarise_new_articles():
    global summaries, model, article, article_url, text
    # Get the list of articles summarised in the past
    old_articles = database_io.retrieve_items_from_db(db_path, "articles")
    articles_infos = feed.get_feeds_articles(website_infos, old_articles)
    summaries = []

    for article in articles_infos:
        source = article['source']
        main_div_class = website_infos[source]['main_class']
        article_url = article['url']
        logging.debug("source: {}, url: {}".format(source, article_url))
        text = scraper.scrape_page(article_url,
                                   main_div_class,
                                   website_infos[source]['number_of_first_paragraphs_to_ignore'],
                                   website_infos[source]['number_of_last_paragraphs_to_ignore'])

        if text:
            summarise_current_article()
    logging.info("Finished to summarise articles!")
    # Store summaries and update DB only if there are new summaries
    if summaries:
        store_summaries()

        database_io.update_items_in_db(articles_infos, db_path, "articles")
        logging.info("Articles db updated!")


if __name__ == "__main__":
    logging.root.handlers = []
    logging.basicConfig(format='%(asctime)s|%(name)s|%(levelname)s| %(message)s',
                        level=logging.INFO,
                        filename="/news_summariser/log/news_summariser.log")

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

    db_path = settings['db_path']
    schedule.every(settings['scheduling_minutes']).minutes.do(summarise_new_articles)
    # Download, if needed, necessary libraries for text processing
    summariser.download_dependencies()
    # Load Word Embedding model
    model = summariser.load_word_embedding_model()
    while True:
        schedule.run_pending()
