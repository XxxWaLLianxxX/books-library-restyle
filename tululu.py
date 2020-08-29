import requests
import os
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json

template_url = 'http://tululu.org'


def download_txt(url, filename, folder='books/'):
    filename = sanitize_filename(filename)
    folder = os.path.join(folder)
    response = requests.get(url)
    if response.encoding == 'utf-8':
        os.makedirs(folder, exist_ok=True)
        path = f"{folder}{filename}.txt"
        with open(path, "w", encoding='utf-8') as book:
            book.write(response.text)
        return path


def download_image(url, filename, folder='images/'):
    filename = sanitize_filename(filename)
    folder = os.path.join(folder)
    response = requests.get(url)
    os.makedirs(folder, exist_ok=True)
    path = f"{folder}{filename}"
    with open(path, "wb") as image:
        image.write(response.content)
    return path


books_info = []
for page_number in range(1, 2):
    page_url = f'http://tululu.org/l55/{page_number}/'
    response = requests.get(page_url, allow_redirects=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')

    if response.status_code != 302:
        book_card_selector = 'table.d_book'
        book_card = soup.select(book_card_selector)
        for a in book_card:
            book_id = a.select_one('a')['href']
            book_link = urljoin(page_url, book_id)
            response = requests.get(book_link, allow_redirects=False)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            book_selector = 'table.d_book a'
            book = soup.select(book_selector)
            for id in book:
                if 'txt' in id['href']:
                    url_txt = urljoin(template_url, id['href'])

            title_tag_selector = 'body div[id=content] h1'
            title_tag = soup.select_one(title_tag_selector)
            title_text = title_tag.text
            title_and_author = title_text.split('::')
            title = title_and_author[0].rstrip()
            author = title_and_author[-1].lstrip()

            book_image = soup.select_one('div.bookimage img')['src']
            book_image_link = urljoin(page_url, book_image)
            image_name = book_image_link.split('/')

            comments = []
            texts = soup.select('.texts')
            for comment in texts:
                if comment:
                    comments.append(comment.select_one('.black').text)

            genre_list = []
            genres_selector = 'body div[id=content] span.d_book a'
            genres = soup.select(genres_selector)
            for genre in genres:
                genre_list.append(genre.text)

            book_path = download_txt(url_txt, title)
            image_path = download_image(book_image_link, image_name[-1])

            book_info = {
                'title': title,
                'author': author,
                'img_src': image_path,
                'book_path': book_path,
                'comments': comments,
                'genres': genre_list,
            }
            books_info.append(book_info)

with open("books_info.json", "w") as json_file:
    json.dump(books_info, json_file, ensure_ascii=False)
