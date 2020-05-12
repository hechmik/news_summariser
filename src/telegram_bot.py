import time
import schedule
import requests
import json
from os import listdir
from os.path import isfile, join
from telegram.utils import helpers
import database_io
import logging


def telegram_bot_sendtext(bot_chat_id: str, bot_token: str, bot_message: str):
    """
    Send the given message to the Telegram Bot
    :param bot_chat_id: Telegram chat ID
    :param bot_token: Token of the given bot
    :param bot_message: Message that will be sent
    :return:
    """
    logging.debug("telegram_bot_sendtext >>>")
    payload = {
        'chat_id': bot_chat_id,
        'text': helpers.escape_markdown(bot_message, "2"),
        'parse_mode': 'MarkdownV2'
    }
    response = requests.post("https://api.telegram.org/bot{token}/sendMessage".format(token=bot_token),
                             data=payload).json()
    if not response['ok']:
        logging.error("Unable to send the following message to the bot: {message}".format(message=bot_message))
        logging.error(response)
    logging.debug("telegram_bot_sendtext <<<")


def get_summaries_fn_list(summaries_dir: str, db_dir: str):
    """
    Obtain the filenames of summaries that haven't been sent in previous iterations
    :return:
    """
    logging.info("get_summaries_fn_list >>>")
    fn_articles = [{"fn": join(summaries_dir, fn_article)} for fn_article in listdir(summaries_dir) if
                   isfile(join(summaries_dir, fn_article)) and fn_article.endswith(".json")]

    messages_previously_sent = database_io.retrieve_items_from_db(db_dir, "messages")
    summaries_to_send = database_io.get_delta(messages_previously_sent, fn_articles)
    logging.info("get_summaries_fn_list <<<")
    return summaries_to_send


def send_summaries(settings: dict):
    """
    Retrieve summaries and send them to Telegram Bot if they weren't already sent
    :param settings: Dictionary where various configurations are stored
    :return:
    """
    logging.info("send_summaries >>>")
    bot_token = settings['telegram_token']
    bot_chat_id = settings['telegram_chat_id']
    db_dir = settings['db_telegram_path']
    summaries_dir = settings['summaries_dir']
    fn_summaries = get_summaries_fn_list(summaries_dir, db_dir)
    try:

        if not fn_summaries:
            telegram_bot_sendtext(bot_chat_id, bot_token, "No summaries to send!")
        for item in fn_summaries:
            fn = item['fn']
            with open(fn) as f:
                current_summaries = json.load(f)
            for summary in current_summaries:
                message = """**{}**\n{}\nSummary:\n{}""".format(
                    summary['title'],
                    summary['url'],
                    summary['summary'])
                telegram_bot_sendtext(bot_chat_id, bot_token, message)
                time.sleep(1)
        database_io.update_items_in_db(fn_summaries, db_dir, "messages")
    except Exception as ex:
        logging.error(ex)
    logging.info("send_summaries <<<")
