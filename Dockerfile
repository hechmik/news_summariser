FROM python:3
RUN mkdir /news_summariser
ADD requirements.txt /news_summariser
RUN pip3 install -r /news_summariser/requirements.txt
RUN wget http://nlp.stanford.edu/data/glove.6B.zip
RUN unzip glove.6B.zip -d /news_summariser/glove.6B
RUN rm -rf glove.6B.zip
ADD src /news_summariser/src
RUN mkdir /news_summariser/output_summaries /news_summariser/articles_db
VOLUME /news_summariser/output_summaries /news_summariser/articles_db
WORKDIR "/news_summariser/src"
CMD [ "python3", "./main.py" ]
