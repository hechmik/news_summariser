# Download base image
FROM continuumio/miniconda3
# Create the folder where all code, dependencies and models will be put
RUN mkdir /news_summariser
# Download GloVe model
RUN wget http://nlp.stanford.edu/data/glove.6B.zip
# Install unzip
RUN apt-get -y --no-install-recommends install unzip
# Unzip it
RUN unzip glove.6B.zip -d /news_summariser/glove.6B
# Remove the original file just for saving ~ 800 MB
RUN rm -rf glove.6B.zip
# Copy environment
ADD environment.yml /news_summariser
# Add conda-forge among available channels
RUN conda config --append channels conda-forge
# Create environment
RUN conda env create -f /news_summariser/environment.yml
# Copy code in the appropriate directory
ADD src /news_summariser/src
# Create directories where summaries, logs and parsed articles will be saved
RUN mkdir /news_summariser/output_summaries /news_summariser/articles_db /news_summariser/log
# Create volumes for being able to access logs, summaries and DB from the outside and for not losing them
VOLUME /news_summariser/output_summaries /news_summariser/db /news_summariser/log
# Change workdir
WORKDIR "/news_summariser/src"
# Let the music play :)
ENTRYPOINT ["conda", "run", "-n", "summariser"]