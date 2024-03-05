from django.shortcuts import render
from bs4 import BeautifulSoup


import requests

# Create your views here.
import os


def homepage(request):

    if request.method=='POST':
        arama=request.POST.get('arama')

        parameter='deep'

        url=f'https://scholar.google.com/scholar?hl=tr&as_sdt=0%2C5&q={arama}&btnG='
        response =requests.get(url)
        html_content=response.text




        soup=BeautifulSoup(html_content,'html.parser')



        titles = soup.find_all(class_='gs_or_ggsm')
        results=[]
        for title in titles:

            a=title.find('a')
            if a:
                span=a.find('span')
                print(span.text)
                results.append(a.get('href'))
                filename = os.path.basename(a.get('href'))
    # İndirme işlemi
                with open(filename, 'wb') as f:
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
                    response = requests.get(a.get('href'), headers=headers)
                    # response = requests.get()
                    f.write(response.content)
                print(f"{filename} indirildi.")


# for title in titles:
#     print(title.text)

        return render(request,'index.html',{'results':results})

    return render(request,'index.html')


