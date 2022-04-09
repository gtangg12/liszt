import re
import json
import numpy as np
import spacy
from sentence_transformers import SentenceTransformer
from transformers import pipeline


TEXT_EMBEDDING_DIM = 512

spacy_basic = spacy.load('en_core_web_md')
sentence_embedding_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
huggingface_summarizer = pipeline("summarization")


def text_to_sentences(text):
    doc = spacy_basic(text, disable=['ner', 'tagger', 'attribute_ruler', 'lemmatizer'])
    sentences = []
    in_long_quote = False # long_quotes are bad for summary
    for span in doc.sents:
        text = span.text
        if text.count('"') == 1:
            in_long_quote = not in_long_quote
        if in_long_quote or text[0] == text[-1] == '"':
            continue
        sentences.append(text)
    return sentences


def text_embedding(text):
    """ Returns unit embedding vector """
    return sentence_embedding_model.encode([text])[0]


def embedding_similiarity(embedding1, embedding2):
    return np.dot(embedding1, embedding2)


def contains_heading(soup, headings):
    tag_set = set([tag.name for tag in soup.find_all()])
    return any([h in tag_set for h in headings])


def concat_body_soups(body_soups):
    return ' '.join(list(map(lambda x: x.get_text(), body_soups)))


def remove_source_tag(text, source_tag):
    return re.sub(source_tag, '', text)


FILTER_REGEX = [
    (r'\([A-Za-z]*\)|\(|\)', r''),                  # parentheses
    (r'[^\u0000-\u007F]', r''),                     # unicode > ascii 127
    (r'\.\.\.', r''),                               # ...
    (r'(?<!\w)([A-Z])\.', r'\1'),                   # abbreviations
    (r'(?<!\w)([a-z])\.', r'\1'),
    (r'([A-Z][a-z]|[A-Z][a-z][a-z])\.', r'\1'),
    (r'[?!]', r'.'),                                # punctuation
    (r'\'s', r''),                                  # apostrophe
    (r's\'', r's'),
    (r'(\w)-(\w)', r'\1 \2'),                       # hyphens
    (r'(  +)', r' '),                               # extra spaces
    (r' . ', r' '),
    (r'\n', r' '),
]


def filter_text(text):
    for pattern, replace in FILTER_REGEX:
        text = re.sub(pattern, replace, text)
    return text.strip()
