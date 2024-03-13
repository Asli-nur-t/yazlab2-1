from django.contrib import admin
from django.urls import path
from .views import homepage,detail

urlpatterns = [
   path('',homepage,name='inbox'),
   path('detail/<int:id>/',detail, name='detail'),
    ]