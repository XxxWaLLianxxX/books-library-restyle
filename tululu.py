import requests
import os
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup
from urllib.parse import urljoin

template_url = 'http://tululu.org/'


def download_txt(url, filename, folder='books/'):
    filename = sanitize_filename(filename)
    folder = os.path.join(folder)
    response = requests.get(url)
    if response.encoding == 'utf-8':
        os.makedirs(folder, exist_ok=True)
        with open(f"{folder}{filename}.txt", "w") as book:
            book.write(response.text)


def download_image(url, filename, folder='images/'):
    filename = sanitize_filename(filename)
    folder = os.path.join(folder)
    response = requests.get(url)
    os.makedirs(folder, exist_ok=True)
    with open(f"{folder}{filename}", "wb") as image:
        image.write(response.content)


for id in range(1, 11):
    book_url = f'{template_url}b{id}/'
    url_txt = f'{template_url}txt.php?id={id}'
    response = requests.get(book_url, allow_redirects=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')

    if response.status_code != 302:
        book_image = soup.find(class_='bookimage').find('img')['src']
        book_image_link = urljoin(template_url, book_image)
        image_name = book_image_link.split('/')

        title_tag = soup.find('div', id='content').h1
        title_text = title_tag.text
        book_and_author = title_text.split('::')
        book = book_and_author[0].rstrip()

        comments = []
        texts = soup.find_all(class_='texts')
        for comment in texts:
            comments.append(comment.find(class_='black').text)

        genre_list = []
        d_book = soup.find('div', id='content').find('span', class_='d_book')
        genres = d_book.find_all('a')
        for genre in genres:
            genre_list.append(genre.text)

        download_txt(url_txt, book)
        download_image(book_image_link, image_name[-1])
