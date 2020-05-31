"""
This module contains useful functions for sending the summaries to a given Telegram Bot.
"""
import time
import json
from os import listdir
from os.path import isfile, join
import logging
import requests
from telegram.utils import helpers
import database_io


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
        'text': bot_message,
        'parse_mode': 'MarkdownV2'
    }
    response = requests.post(
        "https://api.telegram.org/bot{token}/sendMessage".format(token=bot_token),
        data=payload).json()
    if not response['ok']:
        logging.error(
            "Unable to send the following message: {message}".format(message=bot_message))
        logging.error(response)
    logging.debug("telegram_bot_sendtext <<<")


def get_summaries_fn_list(summaries_dir: str, db_dir: str):
    """
    Obtain the filenames of summaries that haven't been sent in previous iterations
    :return:
    """
    logging.info("get_summaries_fn_list >>>")
    fn_articles = [{"fn": join(summaries_dir, fn_article)}
                   for fn_article in listdir(summaries_dir)
                   if isfile(join(summaries_dir, fn_article)) and fn_article.endswith(".json")]

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
    # Extract infos for sending messages to bot
    bot_token = settings['telegram_token']
    bot_chat_id = settings['telegram_chat_id']
    db_dir = settings['db_telegram_path']
    summaries_dir = settings['summaries_dir']
    # Get summaries that haven't been sent
    fn_summaries = get_summaries_fn_list(summaries_dir, db_dir)
    # List where summaries that were successfully sent will be sent
    summaries_successfully_sent = []
    # If there aren't new summaries just send a default message
    if not fn_summaries:
        telegram_bot_sendtext(bot_chat_id,
                              bot_token,
                              helpers.escape_markdown("No summaries to send!", "2"))
    else:
        for item in fn_summaries:
            try:
                fn = item['fn']
                # Load summaries
                with open(fn) as f:
                    current_summaries = json.load(f)
                for article in current_summaries:
                    send_current_summary_as_message(article, bot_chat_id, bot_token)

                summaries_successfully_sent.append(item)
            except Exception as ex:
                logging.error(ex)
    database_io.update_items_in_db(summaries_successfully_sent, db_dir, "messages")
    logging.info("send_summaries <<<")


def send_current_summary_as_message(article: dict, bot_chat_id: str, bot_token: str):
    """
    Send the current summary to the given telegram bot
    :param article: Summary to send via Telegram
    :param bot_chat_id: Target chat ID
    :param bot_token: Bot Token
    :return:
    """
    # Build message
    title = helpers.escape_markdown(article['title'], "2")
    url = helpers.escape_markdown(article['url'], "2")
    summary = helpers.escape_markdown(article['summary'], "2")
    message = """*{title}*\n{url}\nSummary:\n{summary}""".format(
        title=title,
        url=url,
        summary=summary)
    message_len = len(message)
    chat_max_len = 4096
    # Telegram limits messages to 4096 char: if its longer it is best to split it
    if message_len < chat_max_len:
        # Send it to the bot
        telegram_bot_sendtext(bot_chat_id, bot_token, message)
        time.sleep(1)
    else:
        splits = round(message_len / chat_max_len + 1)
        for i in range(splits):
            end_index = chat_max_len * (i + 1)
            if end_index > chat_max_len:
                end_index = chat_max_len
            telegram_bot_sendtext(bot_chat_id, bot_token, message[i * 4096:end_index])
            time.sleep(1)
