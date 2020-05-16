import feed
import summariser
import scraper
import database_io
import logging
import json
import schedule
from datetime import datetime
import telegram_bot


def store_summaries(summaries):
    summary_fn = settings['summaries_fn'].format(str(datetime.now()))
    with open(summary_fn, 'w') as file:
        file.write(json.dumps(summaries))
    logging.info("Summaries stored")


def summarise_current_article(text, article_url, article):
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
        return current_article_summary_info


def summarise_new_articles():
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
            summary = summarise_current_article(text, article_url, article)
            if summary:
                summaries.append(summary)
    logging.info("Finished to summarise articles!")
    # Store summaries and update DB only if there are new summaries
    if summaries:
        store_summaries(summaries)

        database_io.update_items_in_db(articles_infos, db_path, "articles")
        logging.info("Articles db updated!")
    if settings['send_summaries_via_telegram']:
        telegram_bot.send_summaries(settings)


if __name__ == "__main__":
    # Load configuration files
    with open("config/websites.json", "r") as f:
        website_infos = json.load(f)
    with open("config/settings.json", "r") as f:
        settings = json.load(f)
    logging.root.handlers = []
    logging.basicConfig(format='%(asctime)s|%(name)s|%(levelname)s| %(message)s',
                        level=logging.INFO,
                        filename=settings['log_fn'])

    # set up logging to console
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # set a format which is simpler for console use
    formatter = logging.Formatter(fmt='%(asctime)s|%(name)s|%(levelname)s| %(message)s',
                                  datefmt="%d-%m-%Y %H:%M:%S")
    console.setFormatter(formatter)
    logging.getLogger("").addHandler(console)

    logging.info('Application started')
    # Download, if needed, necessary libraries for text processing
    summariser.download_dependencies()
    # Load Word Embedding model
    model = summariser.load_word_embedding_model()
    db_path = settings['db_path']
    # Execute the whole operation at launch
    summarise_new_articles()
    if settings['always_on_execution_mode']:
        # Schedule the run of the summarisation task
        schedule.every(settings['scheduling_minutes']).minutes.do(summarise_new_articles)
        while True:
            schedule.run_pending()
