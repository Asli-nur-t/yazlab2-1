from django.shortcuts import render
from bs4 import BeautifulSoup


import requests

# Create your views here.



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
                results.append(title.text)


# for title in titles:
#     print(title.text)

        return render(request,'index.html',{'results':results})

    return render(request,'index.html')
