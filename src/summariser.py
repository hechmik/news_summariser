"""
In this file all functions needed for creating summaries are present, from loading pretrained
models to executing the core summarisation task.
"""
import math
from typing import List
import logging
import numpy as np
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from scipy.spatial.distance import cosine
from sklearn.feature_extraction.text import TfidfVectorizer
import networkx as nx
from transformers_summaries import generate_transformers_summary


def download_dependencies():
    """
    Download resources needed for text preprocessing
    :return:
    """
    logging.debug("download_dependencies >>>")
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')
    logging.debug("download_dependencies <<<")


def split_text_into_sentences(text):
    """
    Given a list of paragraphs or a string of sentences, return a list with one sentence per element
    :param text:
    :return:
    """
    logging.debug("split_text_into_sentences >>>")
    if isinstance(text, str):
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
    logging.debug("filter_sentences_by_length >>>")
    if min_words_in_sentence > 0:
        sentences = [s for s in sentences if len(s.split()) >= min_words_in_sentence]
    logging.debug("filter_sentences_by_length <<<")
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
    logging.debug("load_stop_words >>>")
    stopws = np.array(stopwords.words("english"))
    logging.debug("load_stop_words <<<")
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
    Preprocess the given text by:
    - Lowercasing
    - Removing special chars
    - Apply tokenizetion
    - Removing stop words
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
    logging.debug("preprocess_text <<<")
    return s


def vectorize_sentence(sentence: List[str], model, empty_strategy):
    """
    Given a text transform it in a list of vectors using Word Embeddings techniques
    :param sentence: string containing a sentence
    :param model: word embedding model
    :param empty_strategy: which strategy to use for handling missing values (default = use a vector of zeros)
    :return:
    """
    logging.debug("vectorize_sentence >>>")
    sentence_embeddings = []
    vector_size = len(model['the'])
    for word in sentence:
        try:
            sentence_embeddings.append(model[word])
        except KeyError:
            logging.warning("Word %s not found in WE model", word)
            if empty_strategy == "fill":
                sentence_embeddings.append(np.zeros(vector_size))
        except Exception as ex:
            logging.error(ex)
    if sentence_embeddings:
        sentence_vector = np.average(sentence_embeddings, axis=0)
    else:
        # Return default value if no word is in the embedding
        sentence_vector = np.zeros(vector_size)
    return sentence_vector


def compute_sentence_similarity(s1: List[str], s2: List[str], model_infos: dict):
    """
    Return the similarity of two sentences
    :param s1: first sentence
    :param s2: second sentence
    :param model_infos: dict where word embedding model and distance metric to use are specified
    :return:
    """
    logging.debug("compute_sentence_similarity >>>")
    distance_metric = model_infos['distance_metric']
    model_obj = model_infos['model_object']
    if distance_metric == "cosine":
        empty_strategy = model_infos['empty_strategy']
        vector_1 = vectorize_sentence(s1, model_obj.model, empty_strategy)
        vector_2 = vectorize_sentence(s2, model_obj.model, empty_strategy)
        score = cosine(vector_1, vector_2)
    elif distance_metric == "wmd":
        score = model_obj.wmdistance(s1, s2)
    else:
        raise NameError("Invalid distance metric: it should be cosine or wmd")
    logging.debug("compute_sentence_similarity <<<")
    return score


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
            if i != j:
                matrix[i, j] = matrix[j, i] = compute_sentence_similarity(sentences[i],
                                                                          sentences[j],
                                                                          model)
    logging.info("build_similarity_matrix <<<")
    return matrix


def pagerank_summarisation(matrix,
                           n_sentences: int,
                           original_article: List[str],
                           tol=0.05,
                           max_iter=150):
    """
    Return the n most dissimilar sentences in the matrix. The comparison is done using PageRank.
    :param matrix: sentences similarity matrix
    :param n_sentences: number of sentences to pick
    :param original_article: original phrases
    :param tol: tolerance parameter for PageRank convergence
    :param max_iter: maximum number of iteration for PageRank convergence
    :return:
    """
    logging.info("find_top_n_sentences >>>")
    graph = nx.from_numpy_array(matrix)
    scores = nx.pagerank(graph, max_iter=max_iter, tol=tol)
    summary = get_sentences_by_scores(n_sentences, scores, original_article, True)
    text = " ".join(summary)
    logging.info("find_top_n_sentences <<<")
    return text


def get_sentences_by_scores(n_sentences: int, scores, sentences: List[str], maximise_score: bool):
    """
    Return the sentences which maximise/minimise the given scores preserving their original order
    :param n_sentences: number of sentences to include in the output list
    :param scores: scores associated with the given sentences
    :param sentences: List of sentences to evaluate
    :param maximise_score: whether to choose sentence that maximise or minimise the given scores
    :return:
    """
    logging.info("get_sentences_by_scores >>>")
    # Create a dictionary for storing sentences and their position in the given text
    sentences_with_index = {}
    for i, sentence in enumerate(sentences):
        sentences_with_index[sentence] = i
    # Order sentences by their score
    ranked_sentences = sorted(((scores[i], s) for i, s in enumerate(sentences)),
                              reverse=maximise_score)
    # Keep only most meaningful sentences
    ranked_sentences = ranked_sentences[0:n_sentences]
    # Get the indexes of these meaningful sentences
    summary_sentences_index = []
    for ranked_sentence in ranked_sentences:
        current_sentence = ranked_sentence[1]
        current_sentence_index = sentences_with_index[current_sentence]
        summary_sentences_index.append(current_sentence_index)
    # Sort indexes in ascending order: in this way we will maintain article coherence
    summary_sentences_index.sort()
    summary = [sentences[i] for i in summary_sentences_index]
    logging.info("get_sentences_by_scores <<<")
    return summary


def tf_idf_summarisation(preprocessed_sentences: List[str],
                         original_article: List[str],
                         n_sentences: int):
    """
    Create a summary according to tf-idf values in the given text
    :param preprocessed_sentences: previously pre-processed sentences
    :param original_article: sentences to evaluate for summarisation in their original form
    :param n_sentences: number of sentences to include for each summary
    :return:
    """
    logging.info("tf_idf_summarisation >>>")
    vectorizer = TfidfVectorizer()
    preprocessed_sentences = ["".join(s) for s in preprocessed_sentences]
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
    summary = get_sentences_by_scores(n_sentences, scores, original_article, True)
    # Transform the summary back into a string
    summary = " ".join(summary)
    logging.info("tf_idf_summarisation <<<")
    return summary


def create_summary(text: List[str],
                   model: dict,
                   reduction_factor: int,
                   min_words_in_sentence: int,
                   algorithm: str):
    """
    Summarize the given text using n sentences.
    :param text: List of paragraphs containing the article's text
    :param model: Word Embeddings model
    :param reduction_factor: how much to reduce the article's length.
    The final summary will have N of sentences = n of sentences/reduction_factor
    :param min_words_in_sentence: minimum number of words a sentence must have in order to be kept
    :param algorithm: Which approach to use for computing the summary
    :return:
    """
    logging.info("create_summary >>>")
    sentences = split_text_into_sentences(text)
    desired_summary_length = math.ceil(len(sentences) / reduction_factor)
    sentences = filter_sentences_by_length(sentences, min_words_in_sentence)
    if desired_summary_length >= len(sentences):
        logging.warning("Reduction factor too high, returning whole article without short sentences")
        summary = " ".join(sentences)
    else:
        stopws = load_stop_words()
        lemmatiser = initialise_lemmatiser()
        preprocessed_sentences = [preprocess_text(s, stopws, lemmatiser) for s in sentences]
        if algorithm == "pagerank":
            matrix = build_similarity_matrix(preprocessed_sentences, model)
            summary = pagerank_summarisation(matrix, desired_summary_length, sentences)
        elif algorithm == "tf_idf":
            summary = tf_idf_summarisation(preprocessed_sentences, sentences, desired_summary_length)
        elif algorithm == "bart" or algorithm == "t5":
            summary = generate_transformers_summary(sentences, model)
        else:
            logging.error("Invalid algorithm. Expected pagerank or tf_idf, got %algorithm", algorithm)
            summary = ""
    logging.info("create_summary <<<")
    return summary
