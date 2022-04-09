from .news_utils import *
from .news_summarizer import *


class Article:
    def __init__(self, source, url, text):
        self.source = source
        self.url = url
        self.text = text

        # pipeline
        self.sentences = text_to_sentences(text)
        self.summary_sentences = text_rank(self.sentences)
        self.topic_embedding = self.get_topic_embedding()

    def get_topic_embedding(self):
        return text_embedding(self.sentences[0])

        sum = np.zeros(TEXT_EMBEDDING_DIM)
        for sentence in self.sentences:
            sum += text_embedding(sentence)
        return sum / len(self.sentences)


def load_articles(path):
    articles = []
    with open(path, 'r') as fin:
        data = json.load(fin)
    for entry in data:
        articles.append(Article(entry['source'], entry['url'], entry['text']))
<<<<<<< HEAD
    return articles
=======
    return articles


if __name__ == '__main__':
    date_str = datetime.datetime.now().strftime('%Y-%m-%d')
    articles = load_articles(f'data/{date_str}/news.json')
    print(generate_report_text(articles))
>>>>>>> 3c8e637 (basic framework)
