
from bs4 import BeautifulSoup


import requests









parameter='deep'

url=f'https://scholar.google.com/scholar?hl=tr&as_sdt=0%2C5&q={parameter}&btnG='
response =requests.get(url)
html_content=response.text




soup=BeautifulSoup(html_content,'html.parser')



titles = soup.find_all(class_='gs_or_ggsm')
for title in titles:

    a=title.find('a')
    if a:
        span=a.find('span')
        print(span.text)


