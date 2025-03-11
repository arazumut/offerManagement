from django.urls import path
from . import views

app_name = 'mesajlar'

urlpatterns = [
    path('', views.sohbet_listesi, name='sohbet_listesi'),
    path('sohbet/yeni/<int:alici_id>/', views.yeni_sohbet, name='yeni_sohbet'),
    path('sohbet/<int:sohbet_id>/', views.sohbet_detay, name='sohbet_detay'),
    path('kullanicilar/', views.kullanici_listesi, name='kullanici_listesi'),
]
