
from django.shortcuts import render
from bs4 import BeautifulSoup
import requests
from urllib.parse import quote


def homepage(request):
    if request.method == 'POST':
        arama = request.POST.get('arama')
        url = f'https://scholar.google.com/scholar?hl=tr&as_sdt=0%2C5&q={arama}&btnG='
        
        response = requests.get(url)
        html_content = response.text

        soup = BeautifulSoup(html_content, 'html.parser')

        titles = soup.find_all(class_='gs_or_ggsm')
        results = []

    for title in titles[:10]:
        a = title.find('a')
        if a:
            pdf_link = a.get('href')
            if pdf_link and pdf_link.endswith('.pdf'):
                results.append(pdf_link)
                print(pdf_link)



        return render(request, 'index.html', {'results': results})

    return render(request, 'index.html')
