import glob
import os
import sys

import numpy as np

os.environ['PATH'] += os.pathsep + os.path.join(os.getcwd(), 'Tesseract-OCR')
extensions = [
    '.xlsx', '.docx', '.pptx',
    '.pdf', '.txt', '.md', '.htm', 'html',
    '.jpg', '.jpeg', '.png', '.gif'
]

import warnings
import torch, textract, pdfplumber
from cleantext import clean
from razdel import sentenize
from sklearn.neighbors import NearestNeighbors
from sentence_transformers import SentenceTransformer

warnings.filterwarnings('ignore')

embedder = SentenceTransformer('/distillUSE')


def processor(path, embedder):
    try:
        if path.lower().endswith('.pdf'):
            with pdfplumber.open(path) as pdf:
                if len(pdf.pages):
                    text = ' '.join([
                        page.extract_text() or '' for page in pdf.pages if page
                    ])
        elif path.lower().endswith('.md') or path.lower().endswith('.txt'):
            with open(path, 'r', encoding='UTF-8') as fd:
                text = fd.read()
        else:
            text = textract.process(path, language='rus+eng').decode('UTF-8')
        if path.lower()[-4:] in ['.jpg', 'jpeg', '.gif', '.png']:
            text = clean(
                text,
                fix_unicode=False, lang='ru', to_ascii=False, lower=False,
                no_line_breaks=True
            )
        else:
            text = clean(
                text,
                lang='ru', to_ascii=False, lower=False, no_line_breaks=True
            )
        sentences = list(map(lambda substring: substring.text, sentenize(text)))
    except Exception as exception:
        return None
    if not len(sentences):
        return None
    return {
        'filepath': [path] * len(sentences),
        'sentences': sentences,
        'vectors': [vector.astype(float).tolist() for vector in embedder.encode(
            sentences
        )]
    }


def indexer(files, embedder):
    for file in files:
        processed = processor(file, embedder)
        if processed is not None:
            yield processed


def counter(path):
    if not os.path.exists(path):
        return None
    for file in glob.iglob(path + '/**', recursive=True):
        extension = os.path.splitext(file)[1].lower()
        if extension in extensions:
            yield file


def search(engine, text, sentences, files):
    indices = engine.kneighbors(
        embedder.encode([text])[0].astype(float).reshape(1, -1),
        return_distance=True
    )

    distance = indices[0][0][0]
    position = indices[1][0][0]

    print(
        'Релевантность "%.3f' % (1 - distance / 2),
        'Фраза: "%s", файл "%s"' % (sentences[position], files[position])
    )


print('Поиск файлов "%s"' % sys.argv[1])
paths = list(counter(sys.argv[1]))

print('Индексация "%s"' % sys.argv[1])
db = list(indexer(paths, embedder))

sentences, files, vectors = [], [], []
for item in db:
    sentences += item['sentences']
    files += item['filepath']
    vectors += item['vectors']

engine = NearestNeighbors(n_neighbors=1, metric='cosine').fit(
    np.array(vectors).reshape(len(vectors), -1)
)

query = input('Что искать: ')
while query:
    search(engine, query, sentences, files)
    query = input('Что искать: ')
