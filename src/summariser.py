import math
from typing import List

import numpy as np
import nltk
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from scipy.spatial.distance import cosine
from sklearn.feature_extraction.text import TfidfVectorizer
import networkx as nx
import logging


def load_word_embedding_model(fn="../glove.6B/glove.6B.50d.txt"):
    """
    Return the Word Embedding model at the given path
    :param fn: path where the model of interest is stored
    :return:
    """
    logging.info("load_word_embedding_model >>>")
    model = {}
    with open(fn, 'r') as f:
        for line in f:
            values = line.split()
            word = values[0]
            vector = np.asarray(values[1:], "float32")
            model[word] = vector
    logging.info("load_word_embedding_model <<<")
    return model


def download_dependencies():
    """
    Download resources needed for text preprocessing
    :return:
    """
    logging.info("download_dependencies >>>")
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')
    logging.info("download_dependencies <<<")


def split_text_into_sentences(text):
    """
    Given a list of paragraphs or a string of sentences, return a list with one sentence per element
    :param text:
    :return:
    """
    logging.debug("split_text_into_sentences >>>")
    if type(text) == str:
        split_text = nltk.sent_tokenize(text)
    elif isinstance(text, list):
        split_text = []
        for s in text:
            split_text = split_text + nltk.sent_tokenize(s)
    logging.debug("split_text_into_sentences <<<")
    return split_text


def filter_sentences_by_length(sentences, min_words_in_sentence):
    """
    Return sentences whose length is equal or greater than the required one
    :param sentences: list of sentences
    :param min_words_in_sentence: minimum number of words a sentence must have in order to be kept
    :return:
    """
    if min_words_in_sentence > 0:
        sentences = [s for s in sentences if len(s.split()) >= min_words_in_sentence]
    return sentences


def tokenize_sentence(s):
    """
    Given a sentence it returns its tokenised version
    :param s: String containing sentence(s)
    :return:
    """
    logging.debug("tokenize_sentence >>>")
    tokenized_s = word_tokenize(s)
    logging.debug("tokenize_sentence <<<")
    return tokenized_s


def load_stop_words():
    """
    Get the stop words list
    :return:
    """
    logging.info("load_stop_words >>>")
    stopws = stopwords.words("english")
    stopws = np.array(stopws[:-36])  # for excluding "negation" words
    logging.info("load_stop_words <<<")
    return stopws


def initialise_lemmatiser():
    """
    Get a WordNet Lemmatizer instance
    :return:
    """
    logging.debug("get_word_lemma >>>")
    wn_lemmatiser = WordNetLemmatizer()
    logging.debug("get_word_lemma <<<")
    return wn_lemmatiser


def get_word_lemma(lemmatiser, w: str):
    """
    Apply lemmatisation to the given word using WordNet as resource
    :param lemmatiser: Lemmatiser instance to use for transforming the input word
    :param w: word to transform
    :return:
    """
    logging.debug("get_word_lemma >>>")
    lemma = lemmatiser.lemmatize(w)
    logging.debug("get_word_lemma <<<")
    return lemma


def preprocess_text(s: str, stopws, lemmatiser):
    """
    Preprocess the given text by lowercasing, removing special chars, tokenizing and removing stop words
    :param s: text to preprocess
    :param stopws: list of stop words to remove
    :param lemmatiser lemmatiser instance to use for transforming words
    :return:
    """
    logging.debug("preprocess_text >>>")
    s = s.lower()
    # Remove tabs, trailing spaces etc.
    s = " ".join(s.split())
    s = tokenize_sentence(s)
    # Delete words that are not alpha numeric
    s = [word for word in s if word.isalpha()]
    # Remove stop words
    s = [word for word in s if word not in stopws]
    # Apply lemmatisation
    s = [get_word_lemma(lemmatiser, word) for word in s]
    s = " ".join(s)
    logging.debug("preprocess_text <<<")
    return s


def vectorize_sentence(sentence: str, model, empty_vector_size=50):
    """
    Given a text transform it in a list of vectors using Word Embeddings techniques
    :param sentence: string containing a sentence
    :param model: word embedding model
    :param empty_vector_size: size of the vector of zeros that will replace a word not found in the model
    :return:
    """
    logging.debug("vectorize_sentence >>>")
    v = []
    for word in sentence.split():
        try:
            v.append(model[word])
        except Exception:
            logging.warning("Word {} not found in WE model: replacing it with vector of 0s".format(word))
            v.append(np.zeros(empty_vector_size))  # word not in the model
    logging.debug("vectorize_sentence <<<")
    return np.mean(v, axis=0)


def compute_sentence_similarity(s1: str, s2: str, model):
    """
    Return the similarity of two sentences
    :param s1: first sentence
    :param s2: second sentence
    :param model: word embedding model to use for summarising text
    :return:
    """
    logging.debug("compute_sentence_similarity >>>")
    vector_1 = vectorize_sentence(s1, model)
    vector_2 = vectorize_sentence(s2, model)
    sim = cosine(vector_1, vector_2)
    logging.debug("compute_sentence_similarity <<<")
    return sim


def build_similarity_matrix(sentences: List[str], model):
    """
    Compute the similarity matrix related to all input sentences
    :param sentences: list of sentences to compare
    :param model: word embedding model
    :return:
    """
    logging.info("build_similarity_matrix >>>")
    n_sent = len(sentences)
    matrix = np.zeros((n_sent, n_sent))
    for i in range(0, n_sent):
        for j in range(0, n_sent):
            if i == j:
                continue
            elif matrix[j, i] != 0:
                matrix[i, j] = matrix[j, i]
            else:
                matrix[i, j] = compute_sentence_similarity(sentences[i], sentences[j], model)
    logging.info("build_similarity_matrix <<<")
    return matrix


def pagerank_summarisation(matrix, n: int, original_article: List[str], tol=0.01, max_iter=150):
    """
    Return the n most dissimilar sentences in the matrix. The comparison is done using PageRank.
    :param matrix: sentences similarity matrix
    :param n: number of sentences to pick
    :param original_article: original phrases
    :param tol: tolerance parameter for PageRank convergence
    :param max_iter: maximum number of iteration for PageRank convergence
    :return:
    """
    logging.info("find_top_n_sentences >>>")
    graph = nx.from_numpy_array(matrix)
    scores = nx.pagerank(graph, max_iter=max_iter, tol=tol)
    summary = get_sentences_by_scores(n, scores, original_article, True)
    text = " ".join(summary)
    logging.info("find_top_n_sentences <<<")
    return text


def get_sentences_by_scores(n: int, scores, sentences: List[str], maximise_score: bool):
    """
    Return the sentences which maximise/minimise the given scores preserving their original order
    :param n: number of sentences to include in the output list
    :param scores: scores associated with the given sentences
    :param sentences: List of sentences to evaluate
    :param maximise_score: whether to choose sentence that maximise or minimise the given scores
    :return:
    """
    logging.debug("get_sentences_by_scores >>>")
    # Create a dictionary for storing sentences and their position in the given text
    sentences_with_index = {}
    for i in range(0, len(sentences)):
        sentences_with_index[sentences[i]] = i
    # Order sentences by their score
    ranked_sentences = sorted(((scores[i], s) for i, s in enumerate(sentences)), reverse=maximise_score)

    # Keep only most meaningful sentences
    ranked_sentences = ranked_sentences[0:n]
    # Get the indexes of these meaningful sentences
    summary_sentences_index = []
    for i in range(0, n):
        current_sentence = ranked_sentences[i][1]
        current_sentence_index = sentences_with_index[current_sentence]
        summary_sentences_index.append(current_sentence_index)
    #  Sort indexes in ascending order: in this way we will maintain article coherence
    summary_sentences_index.sort()
    summary = [sentences[i] for i in summary_sentences_index]
    return summary


def tf_idf_summarisation(preprocessed_sentences: List[str], original_article: List[str], n: int):
    """
    Create a summary according to tf-idf values in the given text
    :param preprocessed_sentences: previously pre-processed sentences
    :param original_article: sentences to evaluate for summarisation in their original form
    :param n: number of sentences to include for each summary
    :return:
    """
    logging.info("tf_idf_summarisation >>>")
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(preprocessed_sentences)
    number_of_sentences = tfidf_matrix.shape[0]
    scores = []
    for index in range(0, number_of_sentences):
        tf_idf_score_curr_sent = tfidf_matrix[index].toarray()
        # remove zero scores
        tf_idf_score_curr_sent = tf_idf_score_curr_sent[tf_idf_score_curr_sent > 0]
        # Compute the average tf-idf value in the given sentence
        curr_sent_avg_score = np.mean(tf_idf_score_curr_sent)
        scores.append(curr_sent_avg_score)
    summary = get_sentences_by_scores(n, scores, original_article, True)
    summary = " ".join(summary)
    logging.info("tf_idf_summarisation <<<")
    return summary


def create_summary(text: List[str], model, n: int, min_words_in_sentence: int, algorithm: str):
    """
    Summarize the given text using n sentences.
    :param text: List of paragraphs containing the article's text
    :param model: Word Embeddings model
    :param n: how much to reduce the article. The summary length will be: (number of text units)/n
    :param min_words_in_sentence: minimum number of words a sentence must have in order to be kept
    :param algorithm: Which approach to use for computing the summary
    :return:
    """
    logging.info("load_stop_words >>>")
    sentences = split_text_into_sentences(text)
    sentences = filter_sentences_by_length(sentences, min_words_in_sentence)
    desired_summary_length = math.ceil(len(sentences) / n)
    stopws = load_stop_words()
    lemmatiser = initialise_lemmatiser()
    preprocessed_sentences = [preprocess_text(s, stopws, lemmatiser) for s in sentences]
    if algorithm == "pagerank":
        matrix = build_similarity_matrix(preprocessed_sentences, model)
        summary = pagerank_summarisation(matrix, desired_summary_length, sentences)
    elif algorithm == "tf_idf":
        summary = tf_idf_summarisation(preprocessed_sentences, sentences, desired_summary_length)
    else:
        logging.error("Invalid algorithm. Expected pagerank or tf_idf, got {}".format(algorithm))
        summary = ""
    logging.info("load_stop_words <<<")
    return summary
