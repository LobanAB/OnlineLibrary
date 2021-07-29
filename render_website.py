import json

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def rebuild():
    with open('description.json', 'r', encoding='utf8') as json_file:
        books_json = json_file.read()
    books = json.loads(books_json)
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')
    rendered_page = template.render(
        books=list(chunked(books, 2)),
    )
    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)
    print("Site rebuilt")


def main():
    rebuild()
    server = Server()
    server.watch('template.html', rebuild)
    server.serve(root='.')


if __name__ == '__main__':
    main()
