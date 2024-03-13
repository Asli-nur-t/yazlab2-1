from django.shortcuts import render
from bs4 import BeautifulSoup

from .models import PDFData
import requests
from django.conf import settings
# Create your views here.
import os

import re
import PyPDF2




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










import re

def pdf_verilerini_kaydet(pdf_dosyasi, url, name):
    with open(pdf_dosyasi, 'rb') as file:
        pdf_okuyucu = PyPDF2.PdfReader(file)
        
        # Her bir sayfada dolaş
        for sayfa_numarasi in range(len(pdf_okuyucu.pages)):
            if pdf_okuyucu.pages[sayfa_numarasi].isEncrypted:
                continue
            
            sayfa = pdf_okuyucu.pages[sayfa_numarasi]
            metin = sayfa.extract_text()
            
            
            # Yayın Tarihi
            date_pattern = re.compile(r'Yayın Tarihi: (\d{2}/\d{2}/\d{4})')
            match = date_pattern.search(metin)
            if match:
                publication_date = match.group(1)
            
            # Yayın Adı
            publish_name_pattern = re.compile(r'Yayın Adı: (.+)')
            match = publish_name_pattern.search(metin)
            if match:
                publish_name = match.group(1)
            
            # Yazar Adları
            authors_pattern = re.compile(r'Yazarlar: (.+)')
            match = authors_pattern.search(metin)
            if match:
                authors_name = match.group(1)
            
            # Yayın Türü
            publish_type_pattern = re.compile(r'Yayın Türü: (.+)')
            match = publish_type_pattern.search(metin)
            if match:
                publish_type = match.group(1)
            
            
            # Yayın Türü
            publication_type_pattern = re.compile(r'Yayın Türü: (.+)')
            match = publication_type_pattern.search(metin)
            if match:
                publication_type = match.group(1)
                print("yayın türü bulundu")
            
            # Yayımcı Adı
            publisher_name_pattern = re.compile(r'Yayımcı Adı: (.+)')
            match = publisher_name_pattern.search(metin)
            if match:
                publisher_name = match.group(1)
                print("yayıncı adı bulundu")
            
            # Anahtar Kelimeler
            key_words_pattern = re.compile(r'Anahtar Kelimeler: (.+)')
            match = key_words_pattern.search(metin)
            if match:
                key_words = match.group(1)
            
            # Özet
            summary_pattern = re.compile(r'Özet: (.+)')
            match = summary_pattern.search(metin)
            if match:
                summary = match.group(1)
            
            # Referans
            reference_pattern = re.compile(r'Referans: (.+)')
            match = reference_pattern.search(metin)
            if match:
                reference = match.group(1)
            
            # Atıf Sayısı
            citations_pattern = re.compile(r'Atıf Sayısı: (\d+)')
            match = citations_pattern.search(metin)
            if match:
                number_of_citations = int(match.group(1))
            
            # DOI Numarası
            doi_pattern = re.compile(r'DOI Numarası: (.+)')
            match = doi_pattern.search(metin)
            if match:
                doi_number = match.group(1)
            
            # PDF'den ayıklanan metinden gerekli verileri bul
            document_name = name  # PDF'den alınan belge adı
            document_url = url  # PDF dosyasının URL'si (opsiyonel)
            publish_id = ''  # Yayın ID'si
            publish_name = publish_name_pattern  # Yayın adı
            authors_name = authors_pattern  # Yazar adları
            publish_type = publish_type_pattern  # Yayın türü
            publication_type = publication_type_pattern  # Yayın türü
            publication_date = date_pattern  # Yayın tarihi
            publisher_name = publisher_name_pattern  # Yayımcı adı
            key_words = key_words_pattern  # Anahtar kelimeler
            summary = summary_pattern  # Özet
            reference = reference_pattern  # Referans
            number_of_citations = citations_pattern # Atıf sayısı
            doi_number = doi_pattern  # DOI numarası
            
            
            # Yukarıdaki verileri ayıkla ve PDFData modeline uygun şekilde kaydet
            pdf_verisi = PDFData.objects.create(
                document_name=document_name,
                document_url=document_url,
                publish_id=publish_id,
                publish_name=publish_name,
                authors_name=authors_name,
                publish_type=publish_type,
                publication_type=publication_type,
                publication_date=publication_date,
                publisher_name=publisher_name,
                key_words=key_words,
                summary=summary,
                reference=reference,
                number_of_citations=number_of_citations,
                doi_number=doi_number
            )
            pdf_verisi.save()
            
            print('Metin:')
            print(metin)




























# def pdf_verilerini_kaydet(pdf_dosyasi,url,name):
    
#         with open(pdf_dosyasi, 'rb') as file:
#             pdf_okuyucu = PyPDF2.PdfReader(file)
            
#             # Her bir sayfada dolaş
#             for sayfa_numarasi in range(len(pdf_okuyucu.pages)):
#                 if pdf_okuyucu.pages[sayfa_numarasi].isEncrypted:
#                     break  # Şifreli sayfa ile karşılaşıldığında döngüyü sonlandır
#                 sayfa = pdf_okuyucu.pages[sayfa_numarasi]
#                 metin = sayfa.extract_text()
#                 # PDF'den ayıklanan metinden gerekli verileri bul
#                 document_name = name  # PDF'den alınan belge adı
#                 document_url = url  # PDF dosyasının URL'si (opsiyonel)
#                 publish_id = ''     # Yayın ID'si
#                 publish_name = ''   # Yayın adı
#                 authors_name = ''   # Yazar adları
#                 publish_type = ''   # Yayın türü
#                 publication_type = ''  # Yayın türü
#                 publication_date = ''  # Yayın tarihi
#                 publisher_name = ''    # Yayımcı adı
#                 key_words = ''         # Anahtar kelimeler
#                 summary = ''           # Özet
#                 reference = ''         # Referans
#                 number_of_citations = 0  # Atıf sayısı
#                 doi_number = 0         # DOI numarası
                
#                 # Yukarıdaki verileri ayıkla ve PDFData modeline uygun şekilde kaydet
#                 pdf_verisi = PDFData.objects.create(
#                     document_name=document_name,
#                     document_url=document_url,
#                     publish_id=publish_id,
#                     publish_name=publish_name,
#                     authors_name=authors_name,
#                     publish_type=publish_type,
#                     publication_type=publication_type,
#                     publication_date=publication_date,
#                     publisher_name=publisher_name,
#                     key_words=key_words,
#                     summary=summary,
#                     reference=reference,
#                     number_of_citations=number_of_citations,
#                     doi_number=doi_number
#                 )
#                 pdf_verisi.save()
#                 print('metin')
#                 print(metin)
