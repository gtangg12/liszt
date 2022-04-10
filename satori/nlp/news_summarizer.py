import json
import datetime
import numpy as np
import networkx
from sklearn.cluster import KMeans
from .news_utils import *


def frequency_matrix(sentences):
    """ Returns frequency matrix, defined as m(i, j) -> (sentence, word frequency) """
    words = {w for s in sentences for w in s}
    index = {w : i for i, w in enumerate(words)}

    m, n = len(sentences), len(words)
    matrix = np.zeros((m, n))
    for i, s in enumerate(sentences):
        for w in s:
            matrix[i, index[w]] += 1
    return matrix


def cosine_matrix(matrix):
    """ Calculates the cosine similarity matrix from frequency matrix """
    norm = np.linalg.norm(matrix, axis = 1)
    tmp = np.expand_dims(norm, 1)
    normalized_matrix = matrix / np.expand_dims(norm, 1)
    return normalized_matrix @ normalized_matrix.T


def text_rank(sentences, max_num=4):
    """ Extractive summary of sentences via text rank algorithm """
    divisor = 4
    round = divisor // 2
    min_num = 1

    # run pagerank
    matrix = cosine_matrix(frequency_matrix(sentences))
    graph = networkx.from_numpy_array(matrix)
    scores = networkx.pagerank(graph)

    # extract top sentences for summary and arrange in chronological order
    n = len(sentences)
    ranked_sentences = sorted(((scores[i], i) for i in range(n)), reverse=True)
    num = min(max((n + round) // divisor, min_num), max_num)
    top = sorted(ranked_sentences[:num], key = lambda x: x[1])

    # generate summary
    summary = [sentences[top[i][1]] for i in range(num)]
    summary = [summary[i] for i in range(num)]

    # get first sentence if not already present
    topic = [sentences[0]] if 0 not in list(zip(*top))[1] else []
    return topic + summary


def cluster(articles):
    """ Return list of lists of similiar news, clustered via k-means using topic
        embeddings. """
    topic_embeddings = np.array([a.topic_embedding for a in articles])
    nc = len(articles) // 3
    kmeans = KMeans(n_clusters=nc, random_state=0).fit(topic_embeddings)
    clusters = [[] for i in range(nc)]
    for i, a in enumerate(articles):
        clusters[kmeans.labels_[i]].append(a)
    return clusters


def summarize_article_group(articles):
    sentences = []
    for a in articles:
        sentences.extend(a.summary_sentences)
        sentences.append('[SEP]')
    while len(sentences) > 16:
        sentences = text_rank(sentences, len(sentences) / 2)
    text = ' '.join(sentences)
    summary = huggingface_summarizer(text, min_length=128, max_length=1024)
    return summary[0]['summary_text'].strip()


def generate_report_text(articles):
    report_text = []
    clusters = cluster(articles)
    for c in clusters:
        image = None
        for a in c:
            if not len(a['images']):
                image = a['images'][0]
                break
        report_text.append(
            {'text': summarize_article_group(c),
            'image': image})
        #report_text += '\n\n'
    return report_text
