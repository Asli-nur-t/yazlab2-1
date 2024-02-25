
from bs4 import BeautifulSoup


import requests

url='https://www.cnnturk.com/'
response =requests.get(url)

html_content=response.text




soup=BeautifulSoup(html_content,'html.parser')


titles=soup.find('h1')

for title in titles:
    print(title.text)
