import numpy as np
import nltk
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from scipy.spatial.distance import cosine
import networkx as nx


def load_word_embedding_model(fn="../glove.6B/glove.6B.50d.txt"):
    """
    Return the Word Embedding model at the given path
    :param fn: path where the model of interest is stored
    :return:
    """
    model = {}
    with open(fn, 'r') as f:
        for line in f:
            values = line.split()
            word = values[0]
            vector = np.asarray(values[1:], "float32")
            model[word] = vector
    return model


def download_dependencies():
    nltk.download('punkt')
    nltk.download('stopwords')


def tokenize_sentence(s):
    """
    Given a sentence it returns its tokenised version
    :param s: String containing sentence(s)
    :return:
    """
    tokenized_s = word_tokenize(s)
    return tokenized_s


def load_stop_words():
    """
    Get stop words list
    :return:
    """
    stopws = stopwords.words("english")
    stopws = np.array(stopws[:-36])  # for excluding "negation" words
    return stopws


def preprocess_text(s, stopws):
    """
    Preprocess the given text by applying lowercasing, removal of special chars, tokenization and stop words removal
    :param s: text to preprocess
    :param stopws: list of stop words to remove
    :return:
    """
    s = s.lower()
    s = re.sub('[^A-Za-z0-9 ]+', ' ', s)
    s = tokenize_sentence(s)
    s = [word for word in s if word not in stopws]
    return s


def vectorize_sentence(s, model, stopws, empty_vector_size=50):
    """
    Given a text transform it in a list of vectors using Word Embeddings techniques
    :param s:
    :param model:
    :param stopws:
    :param empty_vector_size:
    :return:
    """
    v = []
    for word in preprocess_text(s, stopws):
        try:
            v.append(model[word])
        except:
            v.append(np.zeros(empty_vector_size)) #word not in the model
    return np.mean(v, axis=0)


def compute_sentence_similarity(s1, s2, model, stopws):
    """
    Return the similarity of two sentences
    :param s1:
    :param s2:
    :param model:
    :param stopws:
    :return:
    """
    vector_1 = vectorize_sentence(s1, model, stopws)
    vector_2 = vectorize_sentence(s2, model, stopws)
    sim = cosine(vector_1, vector_2)
    return sim


def build_similarity_matrix(sentences, model, stopws):
    """
    Compute the similarity matrix related to all input sentences
    :param sentences:
    :param model:
    :param stopws:
    :return:
    """
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
    return matrix


def find_top_n_sentences(matrix, n, sentences, tol=0.001, max_iter=150):
    """
    Return the n most dissimilar sentences in the matrix
    :param matrix:
    :param n:
    :param sentences:
    :param tol:
    :param max_iter:
    :return:
    """
    graph = nx.from_numpy_array(matrix)
    scores = nx.pagerank(graph, max_iter=max_iter, tol=tol)
    ranked_sentences = sorted(((scores[i], s) for i, s in enumerate(sentences)), reverse=True)
    summary = []
    for i in range(0, n):
        summary.append(ranked_sentences[i][1])    
    return "".join(summary)


def split_text_into_sentences(text):
    """
    Given a list of paragraphs return a list with one sentence per element
    :param text:
    :return:
    """

    sentences = []
    for s in text:
        sentences = sentences + nltk.sent_tokenize(s)
    return sentences


def create_summary(text, model, n=4):
    """
    Summarize the given text using n sentences.
    :param text: List of paragraphs containing the article's text
    :param model: Word Embeddings model
    :param n: how much to reduce the article. The summary length will be: (number of sentences)/n
    :return:
    """
    sentences = split_text_into_sentences(text)
    desired_summary_length = int(len(sentences)/n)
    stopws = load_stop_words()
    matrix = build_similarity_matrix(sentences, model, stopws)
    summary = find_top_n_sentences(matrix, desired_summary_length, sentences)
    return summary
