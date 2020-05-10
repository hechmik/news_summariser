import time
import schedule
import requests
import json

from os import listdir
from os.path import isfile, join


def telegram_bot_sendtext(bot_message):
    telegram_endpoint = 'https://api.telegram.org/bot{}/sendMessage?chat_id={}&parse_mode=Markdown&text={}'.format(
        bot_token,
        bot_chat_id,
        bot_message
    )
    response = requests.get(telegram_endpoint).json()
    if not response['ok']:
        print("something bad happened")
    else:
        print("It looks good")


def get_articles_list():
    dir = settings['summaries_dir']
    fn_articles = [join(dir, f) for f in listdir(dir) if isfile(join(dir, f)) and f.endswith(".json")]
    return fn_articles


def send_summaries():
    print("Sending summaries")
    fn_articles = get_articles_list()
    for fn in fn_articles:
        with open(fn) as f:
            current_articles = json.load(f)
        for article in current_articles:
            message_template = """*{}*\n{}\nSummary: {}""".format(
                article['title'],
                article['url'],
                article['summary'])
            telegram_bot_sendtext(message_template)
            time.sleep(1)


if __name__ == "__main__":

    schedule.every(10).seconds.do(send_summaries)
    with open("config/settings.json") as f:
        settings = json.load(f)
    bot_token = settings['telegram_token']
    bot_chat_id = settings['telegram_chat_id']
    while True:
        schedule.run_pending()
        time.sleep(1)
