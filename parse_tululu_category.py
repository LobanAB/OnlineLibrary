import argparse
import json
import os
import sys
import urllib
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def download_txt(book_id: int, book_header, folder):
    """Функция для скачивания текстовых файлов.
    Args:
        book_id (str): id книги, которую хочется скачать.
        book_header (str): заголовок книги.
        folder (str): Папка, куда сохранять текст.
    """
    url = f'https://tululu.org/txt.php'
    payload = {'id': book_id}
    response = requests.get(url, params=payload)
    response.raise_for_status()
    check_for_redirect(response)
    book_header = f'{book_id}.{sanitize_filename(book_header)}'
    filename = os.path.join(folder, f'{book_header}.txt')
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(response.text)
    return filename


def download_image(image: str, folder, book_id) -> str:
    """Функция для скачивания текстовых файлов.
    Args:
        image (str): Cсылка на обложку книги, которую хочется скачать.
        folder (str): Папка, куда сохранять.
        book_id (int): id книги.
    """
    url = f'https://tululu.org{image}'
    response = requests.get(url)
    response.raise_for_status()
    image_name = f'{book_id}_' + os.path.split(urlparse(urllib.parse.unquote(image)).path)[-1]
    filename = os.path.join(folder, image_name)
    with open(filename, 'wb') as file:
        file.write(response.content)
    return filename


def parse_book_page(book_id: int) -> dict:
    url = f'https://tululu.org/b{book_id}/'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    header, author = map(str.strip, soup.select_one('h1').text.split('::'))
    book_description = {
        'header': header,
        'image': soup.select_one('.bookimage img')['src'],
        'comments': [comment.get_text() for comment in soup.select('#content .black')],
        'author': author,
        'genre': [genre.text for genre in soup.select_one('#content span.d_book').select('a')]
    }
    return book_description


def check_for_redirect(response: requests.models.Response) -> None:
    if response.history:
        raise requests.HTTPError


def parse_category_page(category_id=55, page_to_parse=1):
    url = f'https://tululu.org/l{category_id}/{page_to_parse}'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    books_id = [book.a.extract().get('href')[2:-1] for book in
                soup.select('#content .bookimage')]
    return books_id


def save_description_to_file(book_description, json_path):
    with open(json_path.joinpath('description.json'), 'w', encoding='utf8') as my_file:
        json.dump(book_description, my_file, ensure_ascii=False)


def get_category_last_page(category_id):
    url = f'https://tululu.org/l{category_id}/'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    end_page = int(soup.select('.npage')[-1].text)
    return end_page


def main() -> None:
    category_id = 55
    end_page = get_category_last_page(category_id) + 1
    parser = argparse.ArgumentParser(
        description='Программа скачивает книги с библиотеки tululu.org')
    parser.add_argument(
        '-s', '--start_page', help='id страницы с которой начать закачку', type=int, default=1)
    parser.add_argument(
        '-e', '--end_page', help='id страницы до которой скачать', type=int, default=end_page)
    parser.add_argument(
        '-df',
        '--dest_folder',
        help='путь к каталогу с результатами парсинга: картинкам, книгам, JSON.',
        type=str, default=''
    )
    parser.add_argument(
        '-si', '--skip_imgs', help='не скачивать картинки', action='store_true')
    parser.add_argument(
        '-st', '--skip_txt', help='не скачивать книги', action='store_true')
    parser.add_argument(
        '-jp', '--json_path', help='путь к *.json файлу с результатами', type=str, default='')
    args = parser.parse_args()
    Path(Path.cwd() / args.dest_folder / 'books').mkdir(parents=True, exist_ok=True)
    Path(Path.cwd() / args.dest_folder / 'images').mkdir(parents=True, exist_ok=True)
    if args.json_path != '':
        Path(Path.cwd() / args.dest_folder / args.json_path).mkdir(parents=True, exist_ok=True)
    books_ids = [parse_category_page(category_id, page) for page in range(args.start_page, args.end_page)]
    books_id = [id for ids in books_ids for id in ids]
    books_json = []
    for book_id in books_id:
        try:
            book_description = parse_book_page(book_id)
            if not args.skip_txt:
                book_description['local_txt'] = download_txt(book_id, book_description["header"],
                                                             Path.cwd() / args.dest_folder / 'books')
            if not args.skip_imgs:
                book_description['local_image'] = download_image(book_description['image'],
                                                                 Path.cwd() / args.dest_folder / 'images', book_id)
            books_json.append(book_description)
        except requests.exceptions.HTTPError:
            print(f'Книга - id_{book_id} отсутствует на сервере', file=sys.stderr)
    save_description_to_file(books_json, Path.cwd() / args.dest_folder / args.json_path)


if __name__ == '__main__':
    main()
