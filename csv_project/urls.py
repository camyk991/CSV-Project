from django.contrib import admin
from django.urls import path, include
from csv_app.views import index

urlpatterns = [
    path('', index, name='index'),
]
