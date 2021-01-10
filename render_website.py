import json

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server


def rebuild():
    with open('./library/books_info.json', 'r', encoding='utf-8') as my_file:
        books_info = my_file.read()
    books_info = json.loads(books_info)

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    rendered_page = template.render(books_info=books_info)

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)


def main():
    rebuild()

    server = Server()
    server.watch('./template.html', rebuild)
    server.serve(root='.')


if __name__ == '__main__':
    main()
