import yake
import docx
import re
from pdfminer.high_level import extract_text
import ezodf
import pymorphy2


def made_text(file_name):
    name_split = file_name.split('/')[-1]
    tip = name_split.split('.')[-1]
    if tip == 'txt':
        return f'{name_split} ' + open(file_name, encoding='utf-8').read()
    if tip in ['docx', 'docm']:
        doc = docx.Document(file_name)
        return f'{name_split} ' + ''.join([p.text for p in doc.paragraphs])
    if tip == 'pdf':
        return f'{name_split} ' + ' '.join(re.findall(r'\b\w+\b', extract_text(file_name)))
    if tip in ('odt', 'ods', 'odg', 'odp'):
        fl = ezodf.opendoc(file_name)
        print(str(fl))
        out = []
        for i in fl.body:
            out.extend(re.findall(r"\b\w+\b", i.plaintext().lower()))
        return f'{name_split} ' + ' '.join(out)


def made_keywords(text):
    try:
        nmbr = int(count_words(text) * 0.10)
        extractor_ru = yake.KeywordExtractor(
            lan="ru",
            n=4,
            dedupLim=0.6,
            top=nmbr
        )
        return list(x[0].lower() for x in sorted(tuple(extractor_ru.extract_keywords(text)), key=lambda y: y[1]))
    except Exception as er:
        return ['document']


def count_words(text):
    n = len(re.findall(r'\b\w+\b', text))
    return float(n)