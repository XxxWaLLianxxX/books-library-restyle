import json
import os

import argparse
import requests

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename, sanitize_filepath
from urllib.parse import urljoin

TEMPLATE_URL = 'https://tululu.org'


def download_txt(url, filename, folder):
    filename = sanitize_filename(filename)
    folder = sanitize_filepath(os.path.join(folder, 'books/'))
    response = requests.get(url, allow_redirects=False, verify=False)
    response.raise_for_status()
    os.makedirs(folder, exist_ok=True)
    file_path = f"{folder}/{filename}.txt"
    with open(file_path, "w", encoding='utf-8') as book:
        book.write(response.text)
    return file_path


def download_image(url, filename, folder):
    filename = sanitize_filename(filename)
    folder = sanitize_filepath(os.path.join(folder, 'images/'))
    response = requests.get(url, allow_redirects=False, verify=False)
    response.raise_for_status()
    os.makedirs(folder, exist_ok=True)
    file_path = f"{folder}/{filename}"
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
start_page = args.start_page
end_page = args.end_page
dest_folder = args.dest_folder
json_path = args.json_path

os.makedirs(dest_folder, exist_ok=True)

if args.json_path:
    os.makedirs(json_path, exist_ok=True)


def main():
    books_info = []
    for page_number in range(start_page, end_page + 1):
        page_url = f'https://tululu.org/l55/{page_number}/'
        response = requests.get(page_url, allow_redirects=False, verify=False)
        response.raise_for_status()
        page_soup = BeautifulSoup(response.text, 'lxml')

        book_card_selector = 'table.d_book'
        book_cards = page_soup.select(book_card_selector)
        for book_card in book_cards:
            book_id = book_card.select_one('a')['href']
            book_link = urljoin(page_url, book_id)
            response = requests.get(book_link, allow_redirects=False, verify=False)
            response.raise_for_status()
            book_soup = BeautifulSoup(response.text, 'lxml')
            book_selector = 'table.d_book a'
            book = book_soup.select(book_selector)
            for id in book:
                if 'txt' in id['href']:
                    url_txt = urljoin(TEMPLATE_URL, id['href'])

            title, author = pull_title_and_author(book_soup)

            book_image_link, image_name = pull_book_image(book_soup, page_url)

            comments = []
            texts = book_soup.select('.texts')
            for comment in texts:
                if comment:
                    comments.append(comment.select_one('.black').text)

            genre_list = []
            genres_selector = 'body div[id=content] span.d_book a'
            genres = book_soup.select(genres_selector)
            for genre in genres:
                genre_list.append(genre.text)

            if args.skip_txt:
                book_path = ''
            else:
                try:
                    book_path = download_txt(url_txt, title, dest_folder)
                except requests.exceptions.HTTPError:
                    print(response.status_code)

            if args.skip_imgs:
                image_path = ''
            else:
                try:
                    image_path = download_image(book_image_link, image_name[-1], dest_folder)
                except requests.exceptions.HTTPError:
                    print(response.status_code)

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

    with open(json_file_path, "w") as json_file:
        json.dump(books_info, json_file, ensure_ascii=False)


if __name__ == '__main__':
    main()
