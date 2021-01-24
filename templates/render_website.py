import json
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def on_reload():
    with open('../library/books_info.json', 'r', encoding='utf-8') as file:
        books_info = file.read()
    books_info = json.loads(books_info)

    chunked_books_info = list(chunked(books_info, 2))
    books_pages = list(chunked(chunked_books_info, 5))

    os.makedirs('pages', exist_ok=True)

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    for page_number, books_page in enumerate(books_pages, 1):
        rendered_page = template.render(
            books_page=books_page,
        )
        with open(f'pages/index{page_number}.html', 'w', encoding='utf8') as file:
            file.write(rendered_page)


def main():
    on_reload()

    server = Server()
    server.watch('./template.html', on_reload)
    server.serve(root='.')


if __name__ == '__main__':
    main()
