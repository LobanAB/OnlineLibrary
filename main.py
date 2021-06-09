import requests
from pathlib import Path
from bs4 import BeautifulSoup
import os
from pathvalidate import sanitize_filename

def get_book(book_id):
    url = f"https://tululu.org/txt.php?id={book_id}"
    print(url)
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    filename = download_txt(book_id, get_book_header(book_id))
    with open(filename, 'wb') as file:
        file.write(response.content)


def download_txt(book_id, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        book_id (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    # TODO: Здесь ваша реализация
    return os.path.join(folder, (str(book_id) + '.' + sanitize_filename(filename) + '.txt'))


def get_book_header(book_id):
    url = f'https://tululu.org/b{book_id}/'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    # print(soup.find(class_='bookimage').find('img')['src'])
    # print(soup.find_all(class_='d_book')[2].find('td').text)
    # print('Заголовок:', soup.find('h1').text.split('::')[0].strip())
    # print('Автор:', soup.find('h1').text.split('::')[1].strip())
    book_header = soup.find('h1').text.split('::')[0].strip()
    return book_header

def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def main():
    Path("books").mkdir(parents=True, exist_ok=True)
    for book_id in range(1, 11):
        try:
            get_book(book_id)
        except requests.exceptions.HTTPError:
            pass


if __name__ == '__main__':
    main()
