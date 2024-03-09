from django.shortcuts import render
from bs4 import BeautifulSoup

from .models import PDFData
import requests
from django.conf import settings
# Create your views here.
import os

import re

def temizle(string):
    # Boşlukları ve noktalama işaretlerini kaldır
    temiz_veri = re.sub(r'\s+', '', string)  # Boşlukları kaldır
    temiz_veri = re.sub(r'[^\w\s]', '', temiz_veri)  # Noktalama işaretlerini kaldır
    return temiz_veri

def homepage(request):

    if request.method=='POST':
        arama=request.POST.get('arama')

        parameter='deep'

        url=f'https://scholar.google.com/scholar?hl=tr&as_sdt=0%2C5&q={arama}&btnG='
        response =requests.get(url)
        html_content=response.text




        soup=BeautifulSoup(html_content,'html.parser')



        # titles = soup.find_all(class_='gs_or_ggsm')
        titles=soup.find_all(class_='gs_r gs_or gs_scl')
        # results=[]
        results = []
        for title in titles:
            
            baslik=title.find(class_='gs_rt')
            print(baslik.text)
            at=title.find(class_='gs_or_ggsm')
            
            if at:
                a=at.find('a')
                if a:

                    span=a.find('span')
                    print(span.text)

                

                # results.append(a.get('href'))
                    # results.append(baslik.text)

                   

# 'document_url' ve 'document_url' adında attribute'ları ekleyerek dictionary'e ekleme yapma
                    veri={}
                    veri['document_url'] = a.get('href')
                    veri['document_name'] = baslik.text
                    results.append(veri)
                # filename = os.path.basename(a.get('href'))


                    temizVeri=temizle(a.get('href'))
                #dosya_yolu = "/path/to/your/directory/"
                    filename = os.path.join(settings.MEDIA_ROOT, 'pdf', os.path.basename(temizVeri))
                    # filename = os.path.join(settings.MEDIA_ROOT, 'pdf', os.path.basename(a.get('href')))
    # İndirme işlemi
                    # if os.path.exists(filename):
#     with open(filename, 'wb') as f:
#         # Dosya işlemleri burada yapılır
# else:
#     # Dosya var olmadığında yapılacak işlemler
#     print(f"{filename} adlı dosya mevcut değil.")
                    


                    with open(filename, 'wb') as f:
                        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
                        response = requests.get(a.get('href'), headers=headers)
                    # response = requests.get()
                        f.write(response.content)
                    print(f"{filename} indirildi.")
                    # document_name=.text
                    document_name=baslik.text
                    document_url=a.get('href')
                    document_file=filename
                    pdf_data = PDFData(document_name=document_name, document_url=document_url, document_pdf=document_file)
                    pdf_data.save()


# for title in titles:
#     print(title.text)
        datas=PDFData.objects.all()
        return render(request,'index.html',{'results':results,'datas':datas})

    return render(request,'index.html')

