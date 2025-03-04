# Author: K.Umut Araz
# Date: 05.03.2025  00.39

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from teklifler.views import TeklifViewSet, MusteriViewSet, UrunViewSet
from musteri.views import musteri_talep_formu, talep_basarili, anasayfa, register, firma_sahibi_paneli
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import TemplateView

router = DefaultRouter()
router.register(r'teklifler', TeklifViewSet)
router.register(r'musteriler', MusteriViewSet)
router.register(r'urunler', UrunViewSet)

urlpatterns = [
    path('', anasayfa, name='anasayfa'),  
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),  
    path('talep-formu/', musteri_talep_formu, name='musteri_talep_formu'),
    path('talep-basarili/', talep_basarili, name='talep_basarili'),
    path('register/', register, name='register'),
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='logout_success'), name='logout'),
    path('logout-success/', TemplateView.as_view(template_name='logout_success.html'), name='logout_success'),
    path('firma-sahibi-paneli/', firma_sahibi_paneli, name='firma_sahibi_paneli'),
]