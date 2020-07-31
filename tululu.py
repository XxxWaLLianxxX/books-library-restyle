import requests
import os
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup


def download_txt(url, filename, folder='books/'):
    filename = sanitize_filename(filename)
    folder = os.path.join(folder)
    response = requests.get(url)
    if response.encoding == 'utf-8':
        with open(f"{folder}{filename}.txt", "w") as book:
            book.write(response.text)


folder = 'books/'
os.makedirs(folder, exist_ok=True)
template_url = 'http://tululu.org/'

for id in range(1, 11):
    book_url = f'{template_url}b{id}/'
    url = f'http://tululu.org/txt.php?id={id}'
    response = requests.get(book_url, allow_redirects=False)
    response.raise_for_status()
    if response.status_code != 302:
        soup = BeautifulSoup(response.text, 'lxml')
        title_tag = soup.find('div', id='content').h1
        title_text = title_tag.text
        book_and_author = title_text.split('::')
        book = book_and_author[0].rstrip()
        download_txt(url, book)
