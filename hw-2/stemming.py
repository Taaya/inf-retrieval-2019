import psycopg2
from psycopg2.extras import DictCursor
from pymystem3 import Mystem
from nltk.stem.snowball import RussianStemmer
import uuid


class MyStemObject(object):
    def __init__(self, id, articles_id, term):
        self.id = id
        self.articles_id = articles_id
        self.term = term


class PorterObject(object):
    def __init__(self, id, articles_id, term):
        self.id = id
        self.articles_id = articles_id
        self.term = term

conn = psycopg2.connect(host="localhost", database="parsing", user="postgres", password="postgres")
cursor = conn.cursor(cursor_factory=DictCursor)
cursor.execute("SELECT id, content from articles")
records = cursor.fetchall()

ids = []
texts = []

for r in records:
    ids.append(r[0])
    texts.append(r[1].lower())


stop_words = open('stopwords-ru.txt').read().split('\n')


punctuation = [',', '.', '?', '!', '“', '”', '(', ')', ':', '«', '»', '\n', "'"]
processed_texts = []
for text in texts:
    processed_words = []
    words_from_this_text = text.split(' ')
    for w in words_from_this_text:
        for p in punctuation:
            w = w.replace(p, '')
        processed_words.append(w)
        if w in stop_words:
            processed_words.remove(w)

    text = ' '.join(processed_words)
    processed_texts.append(text)


mystem_texts = []
porter = RussianStemmer()
i = 0
j = 0
for text in processed_texts:
    mystem = Mystem()
    lemmas = mystem.lemmatize(text)

    for l in lemmas:
        if l == " ":
            lemmas.remove(l)

    for lem in lemmas:
        if lem != ' ':
            ms = MyStemObject(id=str(uuid.uuid4()), term=lem, articles_id=ids[i])
            cursor.execute("insert into words_mystem(id, articles_id, term) values('" + ms.id + "', '" + ms.articles_id +
                                       "', '" + ms.term + "');")

    i += 1
    porter_words = [porter.stem(l) for l in lemmas]

    for word in porter_words:
        port = PorterObject(id=str(uuid.uuid4()), term=word, articles_id=ids[j])
        cursor.execute("insert into words_porter(id, articles_id, term) values('" + port.id + "', '" + port.articles_id +
                   "', '" + port.term + "');")
    j += 1


conn.commit()
cursor.close()
conn.close()
