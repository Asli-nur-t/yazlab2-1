from django.shortcuts import render
from bs4 import BeautifulSoup

from .models import PDFData
import requests
from django.conf import settings
# Create your views here.
import os

import re
import PyPDF2
from pymongo import MongoClient



def temizle(string):
    # Boşlukları ve noktalama işaretlerini kaldır
    temiz_veri = re.sub(r'\s+', '', string)  # Boşlukları kaldır
    
    temiz_veri = re.sub(r'[^\w\s]', '', temiz_veri)  # Noktalama işaretlerini kaldır
    return temiz_veri
def detail(request,id):
    pdf_detail=PDFData.objects.get(id=id)

    return render(request,'detail.html',{'data':pdf_detail})
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
        # results=[]2
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
                    if filename.lower().endswith('pdf'):
                        # document_name=.text
                        document_name=baslik.text
                        document_url=a.get('href')
                        document_file=filename
                        document_nameid=temizVeri
                        # pdf_data = PDFData(document_name=document_name, document_url=document_url, document_pdf=document_file,document_nameid=document_nameid)
                        # pdf_data.save()
                        # Dosya bir PDF mi diye kontrol et
                    
                        pdf_verilerini_kaydet(document_file,document_url,document_name)
                    else: print("PDF değil.")
                    
                    



# for title in titles:
#     print(title.text)
        datas=PDFData.objects.all()
        return render(request,'index.html',{'results':results,'datas':datas})
    datas=PDFData.objects.all()
    return render(request,'index.html',{'datas':datas})


def pdf_verilerini_kaydet(pdf_dosyasi, url, name):
    client = MongoClient('mongodb://localhost:27017/')  # MongoDB bağlantısı
    db = client['webscraping']  # Veritabanı adı
    collection = db['pdfdata']  # Koleksiyon adı

    with open(pdf_dosyasi, 'rb') as file:
        try:
            pdf_okuyucu = PyPDF2.PdfFileReader(file)
        except Exception as e:
            print(f"PDF dosyası okunurken bir hata oluştu: {e}")
            return

        for sayfa_numarasi in range(len(pdf_okuyucu.pages)):
            sayfa = pdf_okuyucu.pages[sayfa_numarasi]
            metin = sayfa.extract_text()

            # Yayın Tarihi
            date_pattern = re.compile(r'Yayın Tarihi: (\d{2}/\d{2}/\d{4})')
            match_date = date_pattern.search(metin)
            publication_date = match_date.group(1) if match_date else None

            # Yayın Adı
            publish_name_pattern = re.compile(r'Yayın Adı: (.+)')
            match_publish_name = publish_name_pattern.search(metin)
            publish_name = match_publish_name.group(1) if match_publish_name else ''

            # Yazar Adları
            authors_pattern = re.compile(r'Yazarlar: (.+)')
            match_authors = authors_pattern.search(metin)
            authors_name = match_authors.group(1) if match_authors else ''

            # Yayın Türü
            publish_type_pattern = re.compile(r'Yayın Türü: (.+)')
            match_publish_type = publish_type_pattern.search(metin)
            publish_type = match_publish_type.group(1) if match_publish_type else ''

            # Yayımcı Adı
            publisher_name_pattern = re.compile(r'Yayımcı Adı: (.+)')
            match_publisher_name = publisher_name_pattern.search(metin)
            publisher_name = match_publisher_name.group(1) if match_publisher_name else ''

            # Anahtar Kelimeler
            key_words_pattern = re.compile(r'Anahtar Kelimeler: (.+)')
            match_key_words = key_words_pattern.search(metin)
            key_words = match_key_words.group(1) if match_key_words else ''

            # Özet
            summary_pattern = re.compile(r'Özet: (.+)')
            match_summary = summary_pattern.search(metin)
            summary = match_summary.group(1) if match_summary else ''

            # Referans
            reference_pattern = re.compile(r'Referans: (.+)')
            match_reference = reference_pattern.search(metin)
            reference = match_reference.group(1) if match_reference else ''

            # Atıf Sayısı
            citations_pattern = re.compile(r'Atıf Sayısı: (\d+)')
            match_citations = citations_pattern.search(metin)
            number_of_citations = int(match_citations.group(1)) if match_citations else ''

            # DOI Numarası
            doi_pattern = re.compile(r'DOI Numarası: (.+)')
            match_doi = doi_pattern.search(metin)
            doi_number = match_doi.group(1) if match_doi else ''

            # Yukarıdaki verileri ayıkla ve MongoDB'ye kaydet
            pdf_verisi = {
                'document_name': name,
                'document_url': url,
                'publish_name': publish_name,
                'authors_name': authors_name,
                'publish_type': publish_type,
                'publication_date': publication_date,
                'publisher_name': publisher_name,
                'key_words': key_words,
                'summary': summary,
                'reference': reference,
                'number_of_citations': number_of_citations,
                'doi_number': doi_number
            }
            collection.insert_one(pdf_verisi)
