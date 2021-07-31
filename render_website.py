import json
import os
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked, sliced


def rebuild():
    with open('description.json', 'r', encoding='utf8') as json_file:
        books_json = json_file.read()
    books = json.loads(books_json)
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')
    pages_dir = Path(Path.cwd() / 'pages')
    books_per_page = 10
    os.makedirs(pages_dir, exist_ok=True)
    render_pages(template, books, pages_dir, books_per_page)
    print("Site rebuilt")


def render_pages(template, books, pages_dir, books_per_page=10):
    for page, chunk in enumerate(list(sliced(books, books_per_page)), 1):
        rendered_page = template.render(
            books=list(chunked(chunk, 2)),
        )
        filename = os.path.join(pages_dir, f'index{page}.html')
        with open(filename, 'w', encoding="utf8") as file:
            file.write(rendered_page)


def main():
    rebuild()
    server = Server()
    server.watch('template.html', rebuild)
    server.serve(root='.')


if __name__ == '__main__':
    main()
