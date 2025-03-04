from django.db import models
from django.contrib.auth.models import User
from musteri.models import Musteri, Urun

# Author: K.Umut Araz
# Date: 05.03.2025  00.39

class Teklif(models.Model):
    DURUM_CHOICES = [
        ('BEKLEMEDE', 'Beklemede'),
        ('ONAYLANDI', 'Onaylandı'),
        ('REDDEDILDI', 'Reddedildi'),
        ('REVIZYON', 'Revizyon Bekliyor'),
    ]
    
    musteri = models.ForeignKey(Musteri, on_delete=models.CASCADE)
    urunler = models.ManyToManyField(Urun, through='TeklifUrunu')
    toplam_tutar = models.DecimalField(max_digits=10, decimal_places=2)
    durum = models.CharField(max_length=20, choices=DURUM_CHOICES, default='BEKLEMEDE')
    notlar = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

class TeklifUrunu(models.Model):
    teklif = models.ForeignKey(Teklif, on_delete=models.CASCADE)
    urun = models.ForeignKey(Urun, on_delete=models.CASCADE)
    miktar = models.PositiveIntegerField(default=1)
    birim_fiyat = models.DecimalField(max_digits=10, decimal_places=2)