import requests
from bs4 import BeautifulSoup
import os
from pathvalidate import sanitize_filename


url = 'https://tululu.org/b9/'
response = requests.get(url)
response.raise_for_status()
#print(response.text)
soup = BeautifulSoup(response.text, 'lxml')
#print(soup.prettify())
#print(soup.find('h1').text)
print(soup.find(class_='bookimage').find('img')['src'])
print(soup.find_all(class_='d_book')[2].find('td').text)
print('Заголовок:', soup.find('h1').text.split('::')[0].strip())
print('Автор:', soup.find('h1').text.split('::')[1].strip())

def download_txt(url, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    # TODO: Здесь ваша реализация
    return os.path.join(folder, (sanitize_filename(filename) + '.txt'))

# Примеры использования
url = 'http://tululu.org/txt.php?id=1'

filepath = download_txt(url, 'Алиби')
print(filepath)  # Выведется books/Алиби.txt

filepath = download_txt(url, 'Али/би', folder='books/')
print(filepath)  # Выведется books/Алиби.txt

filepath = download_txt(url, 'Али\\би', folder='txt/')
print(filepath)  # Выведется txt/Алиби.txt
