# Download base image
FROM python:3
# Create the folder where all code will be put
RUN mkdir /news_summariser
# Copy the requirements file
ADD requirements.txt /news_summariser
# Install needed libraries
RUN pip3 install -r /news_summariser/requirements.txt
# Download GloVe model
RUN wget http://nlp.stanford.edu/data/glove.6B.zip
# Unzip it
RUN unzip glove.6B.zip -d /news_summariser/glove.6B
# Remove the original file just for saving ~ 800 MB
RUN rm -rf glove.6B.zip
# Copy code in the appropriate directory
ADD src /news_summariser/src
# Create directories where summaries, logs and parsed articles will be saved
RUN mkdir /news_summariser/output_summaries /news_summariser/articles_db /news_summariser/log
# Create volumes for being able to access logs, summaries and DB from the outside and for not losing them
VOLUME /news_summariser/output_summaries /news_summariser/articles_db /news_summariser/log
# Change workdir
WORKDIR "/news_summariser/src"
# Let the music play :)
CMD [ "python3", "./main.py" ]
