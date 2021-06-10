import requests
from pathlib import Path
from bs4 import BeautifulSoup
import os
from pathvalidate import sanitize_filename
import argparse

def get_book(book_id):
    download_txt(book_id)


def download_txt(book_id, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        book_id (str): Cсылка на текст, который хочется скачать.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    # TODO: Здесь ваша реализация
    url = f"https://tululu.org/txt.php?id={book_id}"
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    book_page = parse_book_page(book_id)
    filename = os.path.join(folder, (str(book_id) + '.' + sanitize_filename(book_page['header']) + '.txt'))
    #with open(filename, 'wb') as file:
    #   file.write(response.content)
    download_image(book_page['image'])


def download_image(image, folder='images/'):
    """Функция для скачивания текстовых файлов.
    Args:
        image (str): Cсылка на текст, который хочется скачать.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    url = f'https://tululu.org{image}'
    response = requests.get(url)
    response.raise_for_status()
    image_name = image.split('/')[-1]
    filename = os.path.join(folder, image_name)
    with open(filename, 'wb') as file:
        file.write(response.content)


def parse_book_page(book_id):
    url = f'https://tululu.org/b{book_id}/'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    print('Заголовок:', soup.find('h1').text.split('::')[0].strip())
    #print(soup.find(class_='bookimage').find('img')['src'])
    #print(urllib.parse.urljoin('https://tululu.org', soup.find(class_='bookimage').find('img')['src']))
    #image = urllib.parse.urljoin('https://tululu.org', soup.find(class_='bookimage').find('img')['src'])
    # print(soup.find_all(class_='d_book')[2].find('td').text)
    # print('Заголовок:', soup.find('h1').text.split('::')[0].strip())
    comments = []
    for comment in soup.find(id='content').find_all(class_='black'):
        comments.append(comment.get_text())
    print()
    book_header = dict(header=soup.find('h1').text.split('::')[0].strip(),
                       image=soup.find(class_='bookimage').find('img')['src'],
                       comments=comments,
                       author=soup.find('h1').text.split('::')[1].strip(),
                       genre=soup.find(id='content').find('span', class_='d_book').text.split(':')[1].strip().strip('.').split(', '))
    return book_header


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def main():
    parser = argparse.ArgumentParser(description='Программа скачивает книги '
                                                 'с библиотеки tululu.org ')
    parser.add_argument('start_id', help='id книги с которой начать закачку ')
    parser.add_argument('end_id', help='id книги конечный ')
    args = parser.parse_args()
    Path("books").mkdir(parents=True, exist_ok=True)
    Path("images").mkdir(parents=True, exist_ok=True)
    for book_id in range(int(args.start_id), (int(args.end_id) + 1)):
        try:
            get_book(book_id)
        except requests.exceptions.HTTPError:
            pass


if __name__ == '__main__':
    main()
