# Automatic News Summariser
*If you think this repository is useful for solving your problem please leave a Star!* :)

As always feel free to make pull requests or open an issue if you think something is wrong and/or can be improved.
## Introduction

The goal of this project is to help me staying updated with the latest news about topics I care while saving some precious time. Also, I think that in this way I will be able to drastically reduce the number of bookmarks in my browser, therefore it is a win-win situation.

At the moment I am focusing in creating an extractive summariser and only the *n* most meaningful phrases in a given article will be returned to the user: even though the summaries may not appear as fluent as the original sources, this choice greatly reduces the problem complexity.

## High-level pipeline:
In order to achieve my starting goal the following operations are done:

1. Most recent articles are obtained by subscribing to the websites of interest' RSS feeds
2. Each article is scraped in order to obtain the full text. This is done because in the majority of cases a RSS feed contain only the first couple of sentences, redirecting the user to the original website for all the remaining infos
3. An extractive summary is created for each article
4. Summaries are sent back to the user. The first step will be to just store them on disk but I would like to experiment different output methods such as Telegram messages and/or emails.

## How to run the news summariser
The preferred way to run this project is via Docker. The reason why is that in this way you will keep your environment clean and it is safe to assume that everything will work. In order to do this, assuming you have Docker installed on your machines you will need to execute the following instructions:
### 1. (Optional): Review the various configurations
In the [src/config](src/config) directory you will find two files:
- [settings.json](src/config/settings.json): In this file you can choose:
    - the "reduction factor" of the output summaries: with a ```reduction_factor``` of 3 an article having N paragraphs/sentences will be summarised using N/3 paragraphs/sentences
    - the minimum number of words a sentence must have in order to be included in the summary (```min_words_in_sentence```). The default value is 0, meaning that all sentences can be included in the summary
    - path to the TinyDB instance where already summarised articles are stored (```db_path```)
    - path where summaries are stored (```summaries_fn```)
    - which algorithm to use for summarising articles (```algorithm```): at the moment you can choose between:
        - ```pagerank```: sentences in a given article are compared to each other in terms of their cosine similarity.Once the similarity matrix is built, PageRank is used for finding the most diverse sentences
        - ```tf_idf```: in this case a tf-idf matrix is built for each article. Sentences with the highest tf-idf average value are included in the summary
- [websites.json](src/config/websites.json). Here you can specify one key for each website you intend to summarise, whose keys are:
    - ```rss```: the URL of the given RSS feed
    - ```main_class```: the HTML *div class* that contains the article(s)
    - ```number_of_first_paragraphs_to_ignore``` . In websites like Politico the first paragraphs have not relevant information (e.g. datime, author(s) name(s)).
        If you specify a given number *n*, the first n paragraph would be ignored.
    - ```number_of_last_paragraphs_to_ignore```. In websites like Wired UK the last paragraphs have not relevant information (e.g. social media links, related articles).
        If you specify a given number *n*, the last n paragraph would be ignored.    
### 2. Build & launch the project

In order to run and stop the project we use [Docker Compose](https://docs.docker.com/compose/); this will also build the Docker containers on first run and will re-use them on later executions. Run `docker-compose up` in the root folder to launch the project.

Useful commands:
- `docker-compose up -d`: starts the project, the `-d` flag run containers in the background
- `docker-compose down`: stops the containers
- `docker-compose build`: re-build containers without starting (possible to use the `--no-cache` flag)

## Next steps

In the next weeks I will work on the following points in order to improve the news summariser:
- [X] Use a proper DB for storing parsed articles: at the moment I am using a JSON file as a temporary solution
- [X] Pick the most diverse (and meaningful) sentences in an alternative/simpler way (currently PageRank is used)
- [ ] Use other similarity functions
- [ ] Send output summaries via Telegram and/or email
- [ ] Improve logging and add basic ELK pipeline for monitoring application status
- [ ] Find a way for getting articles' text without having to specify the div class

## Sources

The course "Text Mining and Search" of my M.Sc. in Data Science at University of Milan-Bicocca, along with other courses and my working experience surely helped me in creating all these software components. I would also like to cite relevant articles from which I took inspiration to build some of the software components:
- [Text Similarities : Estimate the degree of similarity between two texts](https://medium.com/@adriensieg/text-similarities-da019229c894)
- [Text summarization in Python](https://towardsdatascience.com/text-summarization-in-python-3f5a25418606?gi=1d335d30c03d)
