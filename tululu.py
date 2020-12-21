import json
import os
import sys
import logging
import re

import argparse
import requests

from bs4 import BeautifulSoup
from datetime import datetime
from pathvalidate import sanitize_filename, sanitize_filepath
from urllib.parse import urljoin

TEMPLATE_URL = 'https://tululu.org'


def download_txt(url, filename, folder):
    unique_key = str(datetime.now().timestamp()).replace('.', '')
    filename = sanitize_filename(filename)
    folder = sanitize_filepath(os.path.join(folder, 'books/'))
    response = requests.get(url, allow_redirects=False, verify=False)
    response.raise_for_status()
    os.makedirs(folder, exist_ok=True)
    file_path = "{folder}/{filename}{unique_key}.txt".format(folder=folder, filename=filename, unique_key=unique_key)
    with open(file_path, "w", encoding='utf-8') as book:
        book.write(response.text)
    return file_path


def download_image(url, filename, folder):
    unique_key = str(datetime.now().timestamp()).replace('.', '')
    filename = sanitize_filename(filename)
    folder = sanitize_filepath(os.path.join(folder, 'images/'))
    response = requests.get(url, allow_redirects=False, verify=False)
    response.raise_for_status()
    os.makedirs(folder, exist_ok=True)
    file_path = "{folder}/{unique_key}{filename}".format(folder=folder, unique_key=unique_key, filename=filename)
    with open(file_path, "wb") as image:
        image.write(response.content)
    return file_path


def pull_title_and_author(book_soup):
    title_tag_selector = 'body div[id=content] h1'
    title_tag = book_soup.select_one(title_tag_selector)
    title_text = title_tag.text
    title_and_author = title_text.split('::')
    title = title_and_author[0].rstrip()
    author = title_and_author[-1].lstrip()
    return title, author


def pull_book_image(book_soup, page_url):
    book_image = book_soup.select_one('div.bookimage img')['src']
    book_image_link = urljoin(page_url, book_image)
    image_name = book_image_link.split('/')
    return book_image_link, image_name


def get_cmd_args():
    parser = argparse.ArgumentParser(description="Программа скачивает книги с tululu.org")
    parser.add_argument(
        "-sp",
        "--start_page",
        help="Номер первой скачиваемой страницы",
        type=int,
        default=1,
    )
    parser.add_argument(
        "-ep",
        "--end_page",
        help="Номер последней скачиваемой страницы",
        type=int,
        default=1,
    )
    parser.add_argument(
        "-si",
        "--skip_imgs",
        help="Не скачивать картинки",
        action="store_true",
    )
    parser.add_argument(
        "-st",
        "--skip_txt",
        help="Не скачивать книги",
        action="store_true",
    )
    parser.add_argument(
        "-df",
        "--dest_folder",
        help="Путь к каталогу с результатами парсинга",
        default="library/",
    )
    parser.add_argument(
        "-jp",
        "--json_path",
        help="Указать свой путь к *.json файлу с результатами",
    )
    args = parser.parse_args()
    return args


args = get_cmd_args()
dest_folder = args.dest_folder
json_path = args.json_path


def main():
    requests.packages.urllib3.disable_warnings()

    if args.dest_folder:
        os.makedirs(dest_folder, exist_ok=True)
    if args.json_path:
        os.makedirs(json_path, exist_ok=True)

    books_info = []
    template_downloading_book_url = 'https://tululu.org/txt.php?id={book_id}'

    start_page = args.start_page
    end_page = args.end_page
    for page_number in range(start_page, end_page + 1):
        page_url = f'https://tululu.org/l55/{page_number}/'
        try:
            response = requests.get(page_url, allow_redirects=False, verify=False)
        except requests.exceptions.ConnectionError:
            logging.error('Неправильная ссылка')

        if response.status_code != 200:
            logging.warning('Страница {} не найдена'.format(page_url))
            continue

        page_soup = BeautifulSoup(response.text, 'lxml')
        book_card_selector = 'table.d_book'
        book_cards = page_soup.select(book_card_selector)
        for book_card in book_cards:
            book_href = book_card.select_one('a')['href']
            book_abs_link = urljoin(page_url, book_href)
            response = requests.get(book_abs_link, allow_redirects=False, verify=False)
            if response.status_code != 200:
                logging.warning('Страница {} не найдена'.format(page_url))
                continue
            book_soup = BeautifulSoup(response.text, 'lxml')
            downloading_book_url = template_downloading_book_url.format(book_id=re.search(r'\d+', book_href).group(0))

            title, author = pull_title_and_author(book_soup)

            book_image_link, image_name = pull_book_image(book_soup, page_url)

            texts = book_soup.select('.texts')
            comments = [comment.select_one('.black').text for comment in texts if comment]

            genres_selector = 'body div[id=content] span.d_book a'
            genres = book_soup.select(genres_selector)
            genre_list = [genre.text for genre in genres]

            book_path = ''
            if not args.skip_txt:
                try:
                    book_path = download_txt(downloading_book_url, title, dest_folder)
                except requests.exceptions.HTTPError:
                    logging.error('Не удалось скачать книгу')

            image_path = ''
            if not args.skip_imgs:
                try:
                    image_path = download_image(book_image_link, image_name[-1], dest_folder)
                except requests.exceptions.HTTPError:
                    logging.error('Не удалось скачать обложку книги')

            book_info = {
                'title': title,
                'author': author,
                'img_src': image_path,
                'book_path': book_path,
                'comments': comments,
                'genres': genre_list,
            }
            books_info.append(book_info)

    if args.json_path:
        json_file_path = sanitize_filepath(os.path.join(json_path, 'books_info.json'))
    else:
        json_file_path = sanitize_filepath(os.path.join(dest_folder, 'books_info.json'))

    with open(json_file_path, "w", encoding='utf-8') as json_file:
        json.dump(books_info, json_file, ensure_ascii=False)


if __name__ == '__main__':
    main()
