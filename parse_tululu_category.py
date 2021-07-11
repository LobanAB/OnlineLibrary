import requests
import json
from pathlib import Path
from bs4 import BeautifulSoup
import os
from pathvalidate import sanitize_filename
import argparse
import sys


def download_txt(book_id: int, folder='books/') -> dict:
    """Функция для скачивания текстовых файлов.
    Args:
        book_id (str): id книги, которую хочется скачать.
        folder (str): Папка, куда сохранять.
    """
    url = f"https://tululu.org/txt.php"
    payload = {"id": book_id}
    response = requests.get(url, params=payload)
    response.raise_for_status()
    check_for_redirect(response)
    book_description = parse_book_page(book_id)
    filename = os.path.join(folder, f"{book_id}.{sanitize_filename(book_description['header'])}.txt")
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(response.text)
    return book_description


def download_image(image: str, folder='images/') -> None:
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
    books_id_list = [book.a.extract().get('href')[2:-1] for book in
                     soup.select('#content .bookimage')]
    return books_id_list


def save_description_to_file(book_description):
    with open("description.json", "a", encoding='utf8') as my_file:
        json.dump(book_description, my_file, ensure_ascii=False)


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Программа скачивает книги с библиотеки tululu.org ')
    parser.add_argument(
        '-s', '--start_page', help='id книги с которой начать закачку ', type=int)
    parser.add_argument(
        '-e', '--end_page', help='id книги конечный ', type=int, default=702)
    args = parser.parse_args()
    Path("books").mkdir(parents=True, exist_ok=True)
    Path("images").mkdir(parents=True, exist_ok=True)
    category_id = 55
    books_id_lists = [parse_category_page(category_id, page) for page in range(args.start_page, args.end_page)]
    books_id_list = [item for sublist in books_id_lists for item in sublist]
    for book_id in books_id_list:
        try:
            book_description = download_txt(book_id)
            save_description_to_file(book_description)
            download_image(book_description['image'])
        except requests.exceptions.HTTPError:
            print(f"Книга - id_{book_id} отсутствует на сервере", file=sys.stderr)


if __name__ == '__main__':
    main()
