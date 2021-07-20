import requests
import json
from pathlib import Path
from bs4 import BeautifulSoup
import os
from pathvalidate import sanitize_filename
import argparse
import sys


def download_txt(book_id: int, skip_txt, folder) -> dict:
    """Функция для скачивания текстовых файлов.
    Args:
        book_id (str): id книги, которую хочется скачать.
        skip_txt (bool): пропустить закачку текста книги.
        folder (str): Папка, куда сохранять.
    """
    url = f'https://tululu.org/txt.php'
    payload = {'id': book_id}
    response = requests.get(url, params=payload)
    response.raise_for_status()
    check_for_redirect(response)
    book_description = parse_book_page(book_id)
    if not skip_txt:
        filename = os.path.join(folder, f'{book_id}.{sanitize_filename(book_description["header"])}.txt')
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(response.text)
    return book_description


def download_image(image: str, folder) -> None:
    """Функция для скачивания текстовых файлов.
    Args:
        image (str): Cсылка на обложку книги, которую хочется скачать.
        folder (str): Папка, куда сохранять.
    """
    url = f'https://tululu.org{image}'
    response = requests.get(url)
    response.raise_for_status()
    image_name = image.split('/')[-1]
    filename = os.path.join(folder, image_name)
    with open(filename, 'wb') as file:
        file.write(response.content)


def parse_book_page(book_id: int) -> dict:
    url = f'https://tululu.org/b{book_id}/'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    comments = [comment.get_text() for comment in soup.select('#content .black')]
    book_description = {
        'header': soup.select_one('h1').text.split('::')[0].strip(),
        'image': soup.select_one('.bookimage img')['src'],
        'comments': comments,
        'author': soup.select_one('h1').text.split('::')[1].strip(),
        'genre': soup.select_one('#content span.d_book')
            .text.split(':')[1].strip().strip('.').split(', ')
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
    with open(json_path.joinpath('description.json'), 'a', encoding='utf8') as my_file:
        json.dump(book_description, my_file, ensure_ascii=False)


def category_last_page(category_id):
    url = f'https://tululu.org/l{category_id}/'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    end_page = int(soup.select('.npage')[-1].text)
    return end_page


def main() -> None:
    category_id = 55
    end_page = category_last_page(category_id) + 1
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
    for book_id in books_id:
        try:
            book_description = download_txt(book_id, args.skip_txt, Path.cwd() / args.dest_folder / 'books')
            save_description_to_file(book_description, Path.cwd() / args.dest_folder / args.json_path)
            if not args.skip_imgs:
                download_image(book_description['image'], Path.cwd() / args.dest_folder / 'images')
        except requests.exceptions.HTTPError:
            print(f'Книга - id_{book_id} отсутствует на сервере', file=sys.stderr)


if __name__ == '__main__':
    main()
