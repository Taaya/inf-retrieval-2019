import psycopg2
from bs4 import BeautifulSoup
import requests
import uuid
print(str(uuid.uuid4()))

urls = ['https://habr.com/ru/sandbox/page2', 'https://habr.com/ru/sandbox/page3']
titles = []
texts = []
tags = []
hrefs = []
objects = []

for url in urls:
    response = requests.get(url, timeout=5)
    content = BeautifulSoup(response.content, "html.parser")
    articles = content.find_all(class_='post__title_link')
    for article in articles:
        titles.append(article.get_text())
        hrefs.append('https://habr.com/ru/sandbox' + article.get('href'))

for h in hrefs:
    response = requests.get(h, timeout=5)
    content = BeautifulSoup(response.content, "html.parser")
    text = content.find(class_='post__text post__text-html js-mediator-article')
    texts.append(text.get_text())
    pure_tags = content.find(class_='inline-list__item-link hub-link ')
    for pt in pure_tags:
        tags.append(pt.get_text()+';')


class Article(object):

    def __init__(self, id, title, keywords, content, url, student_id):
        self.id = id
        self.title = title
        self.keywords = keywords
        self.content = content
        self.url = url
        self.student_id = student_id


conn = psycopg2.connect(host="localhost",database="parsing", user="postgres", password="postgres")
cursor = conn.cursor()
my_id = str(uuid.uuid4())
for i in range(30):
    article_id = str(uuid.uuid4())
    article = Article(article_id, titles[i], tags[i], texts[i], hrefs[i], my_id)
    objects.append(article)


for o in objects:
    cursor.execute("INSERT INTO articles(id, title, keywords, content, url, student_id) values " +
                   o.id + ", " + o.title + ", " + o.keywords + ", " + o.content +
                   ", " + o.url + ", " + o.student_id + ");")

