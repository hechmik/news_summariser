import numpy as np
import nltk
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from scipy.spatial.distance import cosine
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
    logging.info("download_dependencies <<<")


def tokenize_sentence(s):
    """
    Given a sentence it returns its tokenised version
    :param s: String containing sentence(s)
    :return:
    """
    logging.info("tokenize_sentence >>>")
    tokenized_s = word_tokenize(s)
    logging.info("tokenize_sentence <<<")
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


def preprocess_text(s, stopws):
    """
    Preprocess the given text by applying lowercasing, removal of special chars, tokenization and stop words removal
    :param s: text to preprocess
    :param stopws: list of stop words to remove
    :return:
    """
    logging.info("preprocess_text >>>")
    s = s.lower()
    s = re.sub('[^A-Za-z0-9 ]+', ' ', s)
    s = tokenize_sentence(s)
    s = [word for word in s if word not in stopws]
    logging.info("preprocess_text <<<")
    return s


def vectorize_sentence(s, model, stopws, empty_vector_size=50):
    """
    Given a text transform it in a list of vectors using Word Embeddings techniques
    :param s: string containing sentence
    :param model: word embedding model
    :param stopws: stop word list
    :param empty_vector_size: size of the vector of zeros that will replace a word not found in the model
    :return:
    """
    logging.info("vectorize_sentence >>>")
    v = []
    for word in preprocess_text(s, stopws):
        try:
            v.append(model[word])
        except Exception as e:
            logging.warn("Word {} not found in word embedding model: will replace it with zero vector".format(word))
            v.append(np.zeros(empty_vector_size)) #word not in the model
    logging.info("vectorize_sentence <<<")
    return np.mean(v, axis=0)


def compute_sentence_similarity(s1, s2, model, stopws):
    """
    Return the similarity of two sentences
    :param s1: first sentence
    :param s2: second sentence
    :param model: word embedding model to use for summarising text
    :param stopws: stopwords list to remove
    :return:
    """
    logging.info("compute_sentence_similarity >>>")
    vector_1 = vectorize_sentence(s1, model, stopws)
    vector_2 = vectorize_sentence(s2, model, stopws)
    sim = cosine(vector_1, vector_2)
    logging.info("compute_sentence_similarity <<<")
    return sim


def build_similarity_matrix(sentences, model, stopws):
    """
    Compute the similarity matrix related to all input sentences
    :param sentences: list of sentences to compare
    :param model: word embedding model
    :param stopws: stopwords list to not consider
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
                matrix[i, j] = compute_sentence_similarity(sentences[i], sentences[j], model, stopws)
    logging.info("build_similarity_matrix <<<")
    return matrix


def find_top_n_sentences(matrix, n, sentences, tol=0.001, max_iter=150):
    """
    Return the n most dissimilar sentences in the matrix. The comparison is done using PageRank.
    :param matrix: sentences similarity matrix
    :param n: number of sentences to pick
    :param sentences: original article
    :param tol: tolerance parameter for PageRank convergence
    :param max_iter: maximum number of iteration for PageRank convergence
    :return:
    """
    logging.info("find_top_n_sentences >>>")
    graph = nx.from_numpy_array(matrix)
    scores = nx.pagerank(graph, max_iter=max_iter, tol=tol)
    ranked_sentences = sorted(((scores[i], s) for i, s in enumerate(sentences)), reverse=True)
    summary = []
    for i in range(0, n):
        summary.append(ranked_sentences[i][1])
    text = "".join(summary)
    logging.info("find_top_n_sentences <<<")
    return text


def split_text_into_sentences(text):
    """
    Given a list of paragraphs return a list with one sentence per element
    :param text:
    :return:
    """
    logging.info("split_text_into_sentences >>>")
    sentences = []
    for s in text:
        sentences = sentences + nltk.sent_tokenize(s)
    logging.info("split_text_into_sentences <<<")
    return sentences


def create_summary(text, model, n, use_paragraphs):
    """
    Summarize the given text using n sentences.
    :param text: List of paragraphs containing the article's text
    :param model: Word Embeddings model
    :param n: how much to reduce the article. The summary length will be: (number of text units)/n
    :param use_paragraphs: if True the most meaning paragraphs will be chosen. Otherwise top n sentences will be picked
    :return:
    """
    logging.info("load_stop_words >>>")
    if use_paragraphs:
        sentences = text
    else:
        sentences = split_text_into_sentences(text)
    desired_summary_length = int(len(sentences) / n) + 1
    stopws = load_stop_words()
    matrix = build_similarity_matrix(sentences, model, stopws)
    summary = find_top_n_sentences(matrix, desired_summary_length, sentences)
    logging.info("load_stop_words <<<")
    return summary
