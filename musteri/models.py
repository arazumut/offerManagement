from django.contrib.auth.models import User
from django.db import models

class Musteri(models.Model):
    ad_soyad = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefon = models.CharField(max_length=20)
    firma_adi = models.CharField(max_length=100, blank=True)
    adres = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.ad_soyad

class Urun(models.Model):
    ad = models.CharField(max_length=100)
    aciklama = models.TextField()
    fiyat = models.DecimalField(max_digits=10, decimal_places=2)
    kategori = models.CharField(max_length=50)
    
    def __str__(self):
        return self.ad

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_firma_sahibi = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username