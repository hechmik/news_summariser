# Automatic News Summariser
*If you think this repository is useful for solving your problem please leave a Star!* :)

As always feel free to make pull requests or open an issue if you think something is wrong and/or can be improved.
## Introduction

The goal of this project is to help me staying updated with the latest news about topics I care while saving some precious time. Also, I think that in this way I will be able to drastically reduce the number of bookmarks in my browser, therefore it is a win-win situation.

At the moment I am focusing in creating an extractive summariser and only the most meaningful phrases in a given article will be returned to the user: even though the summaries may not appear as fluent as the original sources, this choice greatly reduces the problem complexity.

## High-level pipeline:
In order to achieve my starting goal this project is structured as follows:

1. Most recent articles are obtained by subscribing to the websites of interest' RSS feeds
2. Each article is scraped in order to obtain the full text. This is necessary because in the majority of cases a RSS feed contain only the first couple of sentences, redirecting the user to the original website for all the remaining infos
3. An extractive summary is created for each article
4. Summaries are stored on disk as JSON files
5. (Optional): Summaries are sent to a Telegram Bot, so that you can read the news using the popular app
6. (Optional): Steps 1-5 are repeated every X minutes

## How to run the news summariser
The preferred way to run this project is via Docker. The reason why is that in this way you will keep your environment clean and it is safe to assume that everything will work. In order to do this, assuming you have Docker installed on your machines you will need to execute the following instructions:
### 1. (Optional) Create a Telegram Bot and get you chat ID
If you want to receive the summaries on Telegram you will need to create a bot. In order to do this:
1. Open the Telegram app and look for **@BotFather**
2. Type ```/start``` in order to start the conversation with this bot
3. Now let's type ```/newbot``` for creating your own bot
4. Choose an appropriate name and type it
5. Done! You will now get a message with your token for accessing via the HTTP API your bot. Keep this token safe, you will need it later on
6. Now access your bot, typing the name specified at step 4 and type /start
7. For retrieving your Chat ID please follow the first answer in [this StackOverflow thread](https://stackoverflow.com/questions/32423837/telegram-bot-how-to-get-a-group-chat-id)
 
### 2. Review the various configurations
In the [src/config](src/config) directory you will find two files: [settings.json](src/config/settings.json), associated with the project settings, and [websites.json](src/config/websites.json), where all the RSS feeds are specified.
#### 2.1 Settings.json 
In [settings.json](src/config/settings.json) the following parameters are specified:
- where application logs are stored (```log_fn```)
- path to the TinyDB instance where already summarised articles are stored (```db_path```)
- path to the TinyDB instance where already sent summaries are stored (```db_telegram_path```)
- folder where summaries are stored(```summaries_dir```)
- complete filename used for storing summaries(```summaries_fn```)
- the minimum number of words a sentence must have in order to be included in the summary (```min_words_in_sentence```). 
- the "reduction factor" of the output summaries: with a ```reduction_factor``` of 3 an article having N paragraphs/sentences will be summarised using N/3 paragraphs/sentences
- which algorithm to use for summarising articles (```algorithm```): at the moment you can choose between:
    - ```pagerank```: sentences in a given article are compared to each other in terms of their cosine similarity.Once the similarity matrix is built, PageRank is used for finding the most diverse sentences
    - ```tf_idf```: in this case a tf-idf matrix is built for each article. Sentences with the highest tf-idf average value are included in the summary
- whether to send the summaries via telegram or not (```send_summaries_via_telegram```), expressed as boolean
- the chat id of your chat with the bot (```telegram_chat_id```)
- the token associated with your bot (```telegram_token```)
- whether to execute the entire project every X minutes or not (```always_on_execution_mode```) expressed as boolean
- how frequent (in minutes) the entire project is run (```scheduling_minutes```)

#### 2.2 Websites.json
In [websites.json](src/config/websites.json) you can specify one key for each website you intend to summarise, whose keys are:
    - ```rss```: the URL of the given RSS feed
    - ```main_class```: the HTML *div class* that contains the article(s)
    - ```number_of_first_paragraphs_to_ignore``` . In websites like Politico the first paragraphs have not relevant information (e.g. datime, author(s) name(s)).
        If you specify a given number *n*, the first n paragraph would be ignored.
    - ```number_of_last_paragraphs_to_ignore```. In websites like Wired UK the last paragraphs have not relevant information (e.g. social media links, related articles).
        If you specify a given number *n*, the last n paragraph would be ignored.

I have uploaded an example of configuration with some of the websites I usually read.
### 3. Build & launch the project

In order to run and stop the project we use [Docker Compose](https://docs.docker.com/compose/).
The first step you will need to do is to build the desired Docker image: in order to do that just launch the `docker-compose build` command.
When the project is successfully build the following commands will be useful:

- `docker-compose up -d`: starts the project, the `-d` flag run containers in the background (detached mode)
- `docker-compose down`: stops the container(s)

## Next steps

In the next weeks I will work on the following points in order to improve the news summariser:
- [X] Use a proper DB for storing parsed articles: at the moment I am using a JSON file as a temporary solution
- [X] Pick the most diverse (and meaningful) sentences in an alternative/simpler way (currently PageRank is used)
- [X] Send output summaries via Telegram and/or email
- [ ] Use other similarity functions
- [ ] Improve logging and add basic ELK pipeline for monitoring application status
- [ ] Find a way for getting articles' text without having to specify the div class

## Sources

The course "Text Mining and Search" of my M.Sc. in Data Science at University of Milan-Bicocca, along with other courses and my working experience surely helped me in creating all these software components. I would also like to cite relevant articles from which I took inspiration to build some of the software components:
- [Text Similarities : Estimate the degree of similarity between two texts](https://medium.com/@adriensieg/text-similarities-da019229c894)
- [Text summarization in Python](https://towardsdatascience.com/text-summarization-in-python-3f5a25418606?gi=1d335d30c03d)
