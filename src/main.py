"""
Main class for running the summariser. Assuming you have correctly installed the needed libraries
and correctly setup the various config JSON files just type
python3 main.py for executing the summarisation operations!
"""
import logging
import json
import schedule
import feed
import summariser
import scraper
import database_io
import telegram_bot
import transformers_summaries
from flask import Flask, render_template, request

global MODEL


def summarise_new_articles():
    """
    Start the summarisation process according the config files
    :return:
    """
    logging.info("summarise_new_articles >>>")
    # Get the list of articles summarised in the past
    db_path = settings['db_path']
    old_articles = database_io.retrieve_items_from_db(db_path, "articles")
    articles_infos = feed.get_feeds_articles(website_infos, old_articles)
    summaries = []

    for article in articles_infos:
        source = article['source']
        main_div_class = website_infos[source]['main_class']
        article_url = article['url']
        logging.debug("source: {source}, url: {url}".format(source=source, url=article_url))
        text = scraper.scrape_page(article_url,
                                   main_div_class,
                                   website_infos[source]['number_of_first_paragraphs_to_ignore'],
                                   website_infos[source]['number_of_last_paragraphs_to_ignore'])

        if text:
            try:
                article_summary = summariser.create_summary(text, MODEL, settings)
                current_article_summary = {
                    "title": article['title'],
                    "summary": article_summary,
                    "url": article_url,
                    "sent": False}
                if current_article_summary:
                    summaries.append(current_article_summary)
            except Exception as ex:
                logging.error("Unable to summarise %s", article_url)
                logging.error(ex)
    logging.info("Finished to summarise articles!")
    # Update DB only if there are new summaries
    if summaries:
        database_io.insert_items_in_db(summaries, db_path, "articles")
        logging.info("Articles db updated!")
    if settings['send_summaries_via_telegram']:
        telegram_bot.send_summaries(settings)
    logging.info("summarise_new_articles <<<")


def activate_endpoint(settings):
    # start flask
    app = Flask(__name__)

    # Homepage
    @app.route('/')
    def home():
        return render_template('homepage.html')

    # Summarisation endpoint
    @app.route('/', methods=['POST'])
    def get_data():
        raw_text = request.form['rawtext']
        split_text = summariser.split_text_into_sentences(raw_text)
        return render_template("homepage.html",
                               summary=str(summariser.create_summary(split_text, MODEL, settings)))

    return app


def load_model(settings):
    global MODEL
    algorithm = settings['algorithm']
    if algorithm == "pagerank":
        import word_mover_distance.model as model
        we = model.WordEmbedding(model_fn=settings['word_embedding_fn'])
        empty_strategy = None
        if 'empty_strategy' in settings.keys():
            empty_strategy = settings['empty_strategy']
        MODEL = {"distance_metric": settings['distance_metric'],
                 "model_object": we,
                 "empty_strategy": empty_strategy}
    elif algorithm == "t5" or algorithm == "bart":
        MODEL = transformers_summaries.load_transformer_model()
    else:
        MODEL = None


def run_backend():
    app = activate_endpoint(settings)
    app.run(host="0.0.0.0")


if __name__ == "__main__":
    # Load configuration files
    with open("config/websites.json", "r") as f:
        website_infos = json.load(f)
    with open("config/settings.json", "r") as f:
        settings = json.load(f)
    logging.root.handlers = []
    logging.basicConfig(format='%(asctime)s|%(name)s|%(levelname)s| %(message)s',
                        level=logging.WARN,
                        filename=settings['log_fn'])

    # set up logging to console
    console = logging.StreamHandler()
    console.setLevel(logging.WARN)
    # set a format which is simpler for console use
    formatter = logging.Formatter(fmt='%(asctime)s|%(name)s|%(levelname)s| %(message)s',
                                  datefmt="%d-%m-%Y %H:%M:%S")
    console.setFormatter(formatter)
    logging.getLogger("").addHandler(console)
    # Download, if needed, necessary libraries for text processing
    summariser.download_dependencies()
    # Load Word Embedding model
    load_model(settings)
    logging.info('Application started')
    if settings['activate_endpoint']:
        import multiprocessing
        # Multiprocessing is needed in order to launch the Rest API and executing the remaining code.
        # The reason why is that app.run, by default in Flask, doesn't allow the execution of further instructions
        p = multiprocessing.Process(target=run_backend)
        p.start()

    # Execute the whole operation at launch
    summarise_new_articles()
    if settings['always_on_execution_mode']:
        # Schedule the run of the summarisation task
        schedule.every(settings['scheduling_minutes']).minutes.do(summarise_new_articles)
        while True:
            schedule.run_pending()
