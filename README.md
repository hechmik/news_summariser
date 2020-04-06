# Automatic News Summariser
## Introduction

The goal of this project is to help me staying updated with the latest news about topics I care while saving some precious time. Also, I think that in this way I will be able to drastically reduce the number of bookmarks in my browser, therefore it is a win-win situation.

At the moment I am focusing in creating an extractive summariser and only the *n* most meaningful phrases in a given article will be returned to the user: even though the summaries may not appear as fluent as the original sources, this choice greatly reduces the problem complexity.

## High-level pipeline:
In order to achieve my original goal the following operations are done:

1. Most recent articles are obtained by subscribing to the websites of interest' RSS feeds
2. Each article is scraped in order to obtain the full text. This is done because in the majority of cases a RSS feed contain only the first of couple of the sentences, redirecting the user to the original website for all the infos
3. An extractive summary is created for each article
4. The summaries are sent back to the user. The first step will be to just store them on disk but I would like to experiment different output methods such as Telegram messages and/or emails.

## How to run the news summariser
The preferred way to run this project is via Docker. The reason why is that in this way you will keep your environment clean and it is safe to assume that everything will work. In order to do this, assuming you have Docker installed on your machines you will need to execute the following instructions:
#### 1. (Optional): Review the various configurations
In the [src/config](src/config) directory you will find two files:
- [settings.json](src/config/settings.json): In this file you can choose:
    - the "reduction factor" of the output summaries: with a ```reduction_factor``` of 3 an article having N paragraphs/sentences will be summarised using N/3 paragraphs/sentences
    - whether to summarise at "paragraph level" or "sentence level": I suggest to keep ```summarise_paragraphs``` set to True for more coherent summaries.
    - path where articles already summarised are stored (```already_read_articles_fn```)
    - path where summaries are stored (```summaries_fn```)
- [websites.json](src/config/websites.json): Here you can specify the RSS feed URL(S) of your interests, along with the HTML div class that contain the articles. Both infos are mandatory.
### 2. Build the docker image
In order to do that you simply have to run the following instructions:
```bash
docker build -t news_summariser .
```
Please keep in mind that ~ 2 GBs of data will be downloaded: in particular the docker image *python:3* will be downloaded, along with the GloVe pretrained models.

### 3. Launch the project

Once the image has been created we can run a Docker container that will execute the project. For doing that just execute the following instruction:
```bash
docker run -v /Users/kappa/repositories/news_summariser/output_summaries:/news_summariser/output_summaries -v /Users/kappa/repositories/news_summariser/articles_db:/news_summariser/articles_db news_summariser
```
Remember to change the volumes paths in order to reflect your current file system (the part before the ```:``` symbol) and eventual modification to the src/config/settings.json file (the part after the ```:```)
Also thanks to the use of Docker volumes next executions will only summarise new articles and you will be to view all summaries by accessing your ```output_summaries/``` directory.

## Next steps

In the next weeks I will work on the following points in order to improve the news summariser:
1. Use a proper DB for storing parsed articles: at the moment I am using a JSON file as a temporary solution
2. Pick the most diverse (and meaningful) sentences in an alternative/simpler way: I am building, for each article, a graph and using PageRank for identifying most meaningful nodes. The procedure is quite heavy and in certain scenarios it doesn't converge to a solution
3. Try other methods for picking the best sentences/paragraphs: at the moment I am assuming that most meaningful sentences have concepts that are infrequent in other parts.
4. Send output summaries via Telegram and/or email
4. Improve logging and add basic ELK pipeline for monitoring application status
5. Find a way for getting articles' text without having to specify the div class

## Sources

The course "Text Mining and Search" of my M.Sc. in Data Science at University of Milan-Bicocca, along with other courses and my working experience surely helped me in creating all these software components. I would also like to cite relevant articles from which I took inspiration to build some of the components:
- [Text Similarities : Estimate the degree of similarity between two texts](https://medium.com/@adriensieg/text-similarities-da019229c894)
- [Text summarization in Python](https://towardsdatascience.com/text-summarization-in-python-3f5a25418606?gi=1d335d30c03d)
