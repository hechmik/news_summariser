import numpy as np
import nltk
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from scipy.spatial.distance import cosine
import networkx as nx

def load_word_embedding_model(fn):
    model = {}
    with open(fn, 'r') as f:
        for line in f:
            values = line.split()
            word = values[0]
            vector = np.asarray(values[1:], "float32")
            model[word] = vector
    return model

def tokenize_sentence(s):
    nltk.download('punkt')
    tokenizes_s = word_tokenize(s)
    return tokenizes_s

def load_stop_words():
    nltk.download('stopwords')
    stopws = stopwords.words("english")
    stopws = np.array(stopws[:-36]) # for excluding "negation" words
    return stopws

def preprocess_text(s, stopws):
    s = s.lower()
    s = re.sub('[^A-Za-z0-9 ]+', ' ', s)
    s = tokenize_sentence(s)
    s = [word for word in s if word not in stopws]
    return s

def vectorize_sentence(s, model, stopws, empty_vector_size=50):
    v = []
    for word in preprocess_text(s, stopws):
        try:
            v.append(model[word])
        except:
            v.append(np.zeros(empty_vector_size)) #word not in the model
    return np.mean(v, axis=0)

def compute_sentence_similarity(s1, s2, model, stopws):
    vector_1 = vectorize_sentence(s1, model, stopws)
    vector_2 = vectorize_sentence(s2, model, stopws)
    sim = cosine(vector_1, vector_2)
    return sim

def build_similarity_matrix(sentences, model, stopws):
    n_sent = len(sentences)
    matrix = np.zeros((n_sent, n_sent))
    for i in range(0, n_sent):
        for j in range(0, n_sent):
            if i == j:
                continue
            elif matrix[j,i] != 0:
                matrix[i,j] = matrix[j,i]
            else:
                matrix[i,j] = compute_sentence_similarity(sentences[i], sentences[j], model, stopws)
    return matrix

def find_top_n_sentences(matrix, n, sentences):
    graph = nx.from_numpy_array(matrix)
    scores = nx.pagerank(graph)
    #print(scores)
    ranked_sentences = sorted(((scores[i],s) for i,s in enumerate(sentences)), reverse=True)
    summary = []
    for i in range(0, n):
        summary.append(ranked_sentences[i][1])    
    return "\n".join(summary)

def create_summary(sentences, model_fn="../glove.6B/glove.6B.50d.txt", n=5):
    stopws = load_stop_words()
    model = load_word_embedding_model(model_fn)
    matrix = build_similarity_matrix(sentences, model, stopws)
    summary = find_top_n_sentences(matrix, n, sentences)
    return summary