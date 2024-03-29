from django.shortcuts import render
from bs4 import BeautifulSoup
from datetime import datetime
from .models import PDFData
import requests
from django.conf import settings
# Create your views here.
import os

import re
import PyPDF2
from pymongo import MongoClient
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
import locale


def temizle(string):
    # Boşlukları ve noktalama işaretlerini kaldır
    temiz_veri = re.sub(r'\s+', '', string)  # Boşlukları kaldır
    
    temiz_veri = re.sub(r'[^\w\s]', '', temiz_veri)  # Noktalama işaretlerini kaldır
    return temiz_veri
def detail(request,id):
    pdf_detail=PDFData.objects.get(id=id)

    return render(request,'detail.html',{'data':pdf_detail})
def homepage(request):
    if request.method == 'GET':
        order = request.GET.get('order', None)
        order_q = request.GET.get('order_q', None)
        datas = None

        if order == 'old_to_new':
            datas = PDFData.objects.order_by('publication_date')
        elif order == 'new_to_old':
            datas = PDFData.objects.order_by('-publication_date')
        else:
            datas = PDFData.objects.all()

        if order_q == 'old_to_new_q':
            datas = datas.order_by('number_of_citations')
        elif order_q == 'new_to_old_q':
            datas = datas.order_by('-number_of_citations')
          # Varsayılan sıralama

        return render(request, 'index.html', {'datas': datas})
    if request.method=='POST':

        if 'arama' in request.POST:
            arama=request.POST.get('arama')
            arama=arama.strip()
            arama=arama.replace(" ", "+")
            obj = PDFData.objects.all() # Örnek bir object_id alma yöntemi
            
            # Nesneyi veritabanından sil
            obj.delete()
            parameter='deep'

            url=f'https://scholar.google.com/scholar?hl=tr&as_sdt=0%2C5&q={arama}&btnG='
            url=f'https://dergipark.org.tr/tr/search?q={arama}&section=articles'


            response =requests.get(url)
            html_content=response.text




            soup=BeautifulSoup(html_content,'html.parser')



            # titles = soup.find_all(class_='gs_or_ggsm')
            titles=soup.find_all(class_='card article-card dp-card-outline')
            # results=[]2
            results = []
            for title in titles:
                publish_type=title.find(class_="badge badge-secondary")
                
                
                if publish_type:
                    publish_type=publish_type.text
                    print(publish_type)


                content=title.find(class_='card-title')
                baslikLink=content.find('a')

                baslik=baslikLink.text.strip()
            
                articleUrl=baslikLink['href']

                responseArticle =requests.get(articleUrl)
                html_contentArticle=responseArticle.text




                soupArticle=BeautifulSoup(html_contentArticle,'html.parser')
                pdf_link=soupArticle.find(class_='kt-nav__link')
                # pdf_link=pdf_link.find('a')
                authors=soupArticle.find(class_='record_properties table')
                authors=authors.find_all('tr')
                yazarlar_listesi=[]
                tarih=''
                for author in authors:
                    th=author.find('th')
                    if th.text=='Yazarlar':
                        yazarlar=author.find('td')
                        yazarlar=yazarlar.find_all('p')
                        for yazar in yazarlar:
                            yazar=yazar.find('span')
                            # yazarlar_listesi.append(yazar.text.strip())
                    
                    if th.text=='Yayımlanma Tarihi':
                        tarih=author.find('td')
                        tarih=tarih.text
                authors=soupArticle.find(class_='article-authors')
                if authors:
                    authors=authors.find_all('a')
                    for author in authors:
                        yazarlar_listesi.append(author.text.strip())

                keywords=soupArticle.find(class_='article-keywords data-section')
                anahtarlar=[]
                if keywords:
                    keywords=keywords.find('p')
                    keywords=keywords.find_all('a')
                    
                    for keyword in keywords:
                        anahtar=keyword.text
                        anahtarlar.append(anahtar)

                references=soupArticle.find(class_='table table-striped m-table cite-table')
                
                references=references.find_all('td')
                if references:
                    reference=references[1].text


                referans=soupArticle.find(class_='article-citations data-section')
                referans_list=[]
                referans_sayisi=0
                if referans:
                
            
                    referans=referans.find_all('li')
                    for ref in referans:
                        referans_list.append(ref.text.strip())
                    referans_sayisi=len(referans)

                





                document_name=baslik
                document_url='https://dergipark.org.tr'+pdf_link.get('href')

                temizVeri = temizle(document_url)+'.pdf'
                filename = os.path.join(settings.MEDIA_ROOT, 'pdf', os.path.basename(temizVeri))
                with open(filename, 'wb') as f:
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
                
                    response = requests.get(document_url, headers=headers)
                    f.write(response.content)
                    print(f"{filename} indirildi.")

                
                summary=soupArticle.find(class_='article-abstract data-section')
                if summary:

                    summary=summary.find('p')
                    summary=summary.text

                veri=pdf_link.get('href')

                publisher_name=soupArticle.find_all('fw-500')
                
                publisher_name=publisher_name[-1:0]
                
                if publisher_name:
                    publisher_name=publisher_name.text

                # locale.setlocale(locale.LC_TIME, 'tr_TR.UTF-8')
                tr_to_en_months = {
                'Ocak': 'January',
                'Şubat': 'February',
                'Mart': 'March',
                'Nisan': 'April',
                'Mayıs': 'May',
                'Haziran': 'June',
                'Temmuz': 'July',
                'Ağustos': 'August',
                'Eylül': 'September',
                'Ekim': 'October',
                'Kasım': 'November',
                'Aralık': 'December'
            }

                tarih_formati = "%d %B %Y"

# String'i datetime objesine çevir
                if(tarih!="" or tarih!=None):
                    tarihDate= turkish_date_to_datetime(tarih)
                else:
                    tarihDate=None
                document_pdf=filename
                publish_id=veri[-5:0]
                publish_name=publisher_name
                authors_name=yazarlar_listesi
                publish_type=publish_type
                publication_type=""
                publication_date=tarihDate
                publisher_name=""
                key_words=anahtarlar
                summary=summary
                reference=reference
                number_of_citations=int(referans_sayisi)
                doi_number=0

                print(document_url)

                pdf_data= PDFData(
                    document_name=document_name,
                    document_url=document_url,
                    document_pdf=document_pdf,
                    publish_name=publish_name,
                    authors_name=authors_name,
                    publish_type=publish_type,
                    publication_date=publication_date,
                    publisher_name=publisher_name,
                    key_words=key_words,
                    summary=summary,
                    reference=reference,
                    number_of_citations=number_of_citations,
                    doi_number=doi_number
                ) 
                pdf_data.save()

            datas=PDFData.objects.all()
            return render(request,'index.html',{'datas':datas})

        elif 'submit_btn' in request.POST and request.POST['submit_btn'] == 'filter_submit':
            yazarlar=request.POST.getlist('yazarlar[]')
            yayin=request.POST.getlist('yayin[]')
            keywords=request.POST.getlist('keywords[]')

           
            queryset = datas=PDFData.objects.all()
            if yazarlar:
                queryset = queryset.filter(authors_name__in=yazarlar)
            if yayin:
                queryset = queryset.filter(publish_type__in=yayin)
            if keywords:
                queryset = queryset.filter(key_words__in=keywords)

            return render(request,'index.html',{'datas':queryset})    

        
    datas=PDFData.objects.all()
    return render(request,'index.html',{'datas':datas})

def turkish_date_to_datetime(turkish_date):
    tr_to_en_months = {
                'Ocak': 'January',
                'Şubat': 'February',
                'Mart': 'March',
                'Nisan': 'April',
                'Mayıs': 'May',
                'Haziran': 'June',
                'Temmuz': 'July',
                'Ağustos': 'August',
                'Eylül': 'September',
                'Ekim': 'October',
                'Kasım': 'November',
                'Aralık': 'December'
            }
    # Ay isimlerini İngilizceye çevirme
    for tr_month, en_month in tr_to_en_months.items():
        turkish_date = turkish_date.replace(tr_month, en_month)
    
    # Türkçe tarih stringini datetime objesine dönüştürme
    return datetime.strptime(turkish_date, '%d %B %Y')

def filter_documents(authors=[], publish_types=[], key_words=[]):
    # Elasticsearch bağlantısını oluştur
    client = Elasticsearch(hosts=["http://localhost:9200"])


    s = Search(using=client, index="pdf_index")

    # if AuthorizationException:
    #     author_query = Q('terms', authors_name=authors)
    #     s = s.query(author_query)

    if publish_types:
        publish_type_query = Q('terms', publish_type=publish_types)
        s = s.query(publish_type_query)
    if authors:
        publish_type_query = Q('terms',authors_name=authors)
        s = s.query(publish_type_query)
    if key_words:
        key_words_query = Q('terms', key_words=key_words)
        s = s.query(key_words_query)

    response = s.execute()
    return response

def pdf_verilerini_kaydet(pdf_dosyasi, url, name):
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

            # Yukarıdaki verileri ayıkla ve PDFData modeline uygun şekilde kaydet
            pdf_verisi = PDFData(
                document_name=name,
                document_url=url,
                publish_name=publish_name,
                authors_name=authors_name,
                publish_type=publish_type,
                publication_date=publication_date,
                publisher_name=publisher_name,
                key_words=key_words,
                summary=summary,
                reference=reference,
                number_of_citations=number_of_citations,
                doi_number=doi_number
            )
            pdf_verisi.save_base
            pdf_verisi.save()
