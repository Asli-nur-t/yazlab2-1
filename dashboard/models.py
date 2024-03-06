from django.db import models

# Create your models here.



class PDFData(models.Model):
    id=models.AutoField(primary_key=True)
    document_name=models.CharField(max_length=600)
    document_url=models.CharField(max_length=600)
    document_pdf=models.FileField(upload_to="pdf/")
    






