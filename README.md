# Automatic News Summariser
## Introduction

The goal of this project is to help me staying updated with the latest news about topics I care while saving me some precious time. Also, I think that in this way I will be able to drastically reduce the number of bookmarks in my browser, therefore it is a win-win situation.

At the moment I am focusing in creating an extractive summariser and only the *n* most meaningful phrases in a given article will be returned to the user: even though the summaries may not appear as fluent as the original sources, this choice greatly reduces the problem complexity.

## High-level pipeline:
In order to achieve my original goal the following operations are done:

1. Most recent articles are obtained by subscribing to the websites of interest'RSS feeds
2. Each article is scraped in order to obtain the full text. This is done because in the majority of cases a RSS feed contain only the first of couple of the sentences, redirecting the user to the original website for all the infos
3. An extractive summary is created for each article
4. The summaries are sent back to the user. The first step will be to just store them on disk but I would like to experiment different output methods such as Telegram messages and/or emails.

## Sources

The course "Text Mining and Search" of my M.Sc. in Data Science at University of Milan-Bicocca, along with other courses and my working experience surely helped me in creating all these software components. I would also like to cite relevant articles from which I took inspiration to build some of the components:
- [Text Similarities : Estimate the degree of similarity between two texts](https://medium.com/@adriensieg/text-similarities-da019229c894)
- [Text summarization in Python](https://towardsdatascience.com/text-summarization-in-python-3f5a25418606?gi=1d335d30c03d)
