import requests
from bs4 import BeautifulSoup


url = 'https://www.franksonnenbergonline.com/blog/are-you-grateful/'
response = requests.get(url)
response.raise_for_status()
print(response.text)
soup = BeautifulSoup(response.text, 'lxml')
print(soup.prettify())
