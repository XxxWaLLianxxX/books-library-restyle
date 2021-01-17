import json

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def on_reload():
    with open('./library/books_info.json', 'r', encoding='utf-8') as my_file:
        books_info = my_file.read()
    books_info = json.loads(books_info)
    chunked_books_info = list(chunked(books_info, 2))

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    rendered_page = template.render(
        chunked_books_info=chunked_books_info,
    )

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)


def main():
    on_reload()

    server = Server()
    server.watch('./template.html', on_reload)
    server.serve(root='.')


if __name__ == '__main__':
    main()
