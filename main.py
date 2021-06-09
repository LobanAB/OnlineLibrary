import requests
from pathlib import Path


def get_book(book_id):
    url = f"https://tululu.org/txt.php?id={book_id}"
    print(url)
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    filename = f'books/id{book_id}.txt'
    with open(filename, 'wb') as file:
        file.write(response.content)


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
