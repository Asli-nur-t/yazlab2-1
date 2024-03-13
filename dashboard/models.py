from django.db import models

# Create your models here.



class PDFData(models.Model):
    id=models.AutoField(primary_key=True)
    document_name=models.CharField(max_length=600)
    document_url=models.CharField(max_length=600)
    document_pdf=models.FileField(upload_to="pdf/")
    publish_id=models.CharField(max_length=600)
    publish_name=models.CharField(max_length=600)
    authors_name=models.CharField(max_length=600)
    publish_type=models.CharField(max_length=600)
    publication_type=models.CharField(max_length=600)
    publication_date=models.CharField(max_length=600)
    publisher_name=models.CharField(max_length=600)
    key_words=models.CharField(max_length=600)
    summary=models.CharField(max_length=600)
    reference=models.CharField(max_length=600)
    number_of_citations=models.DecimalField(max_digits=10,decimal_places=0)
    doi_number=models.DecimalField(max_digits=10,decimal_places=0)
    
    
    
    





