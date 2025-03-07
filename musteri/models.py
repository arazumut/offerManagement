from django.contrib.auth.models import User
from django.db import models
from django.db.models import Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta


class Musteri(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    ad_soyad = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefon = models.CharField(max_length=20)
    firma_adi = models.CharField(max_length=100, blank=True)
    adres = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.ad_soyad

    class Meta:
        verbose_name = 'Müşteri'
        verbose_name_plural = 'Müşteriler'

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

class TeklifAnalitik(models.Model):
    tarih = models.DateField(auto_now_add=True)
    toplam_teklif = models.IntegerField(default=0)
    onaylanan_teklif = models.IntegerField(default=0)
    reddedilen_teklif = models.IntegerField(default=0)
    ortalama_yanit_suresi = models.DurationField(null=True)
    
    @classmethod
    def hesapla_gunluk_analitik(cls):
        bugun = timezone.now().date()
        teklifler = Teklif.objects.filter(created_at__date=bugun)
        
        return cls.objects.create(
            toplam_teklif=teklifler.count(),
            onaylanan_teklif=teklifler.filter(durum='ONAYLANDI').count(),
            reddedilen_teklif=teklifler.filter(durum='REDDEDILDI').count(),
            ortalama_yanit_suresi=teklifler.exclude(
                durum='BEKLEMEDE'
            ).aggregate(Avg('updated_at' - 'created_at'))['avg']
        )

class Bildirim(models.Model):
    BILDIRIM_TIPLERI = [
        ('ONAY', 'Onay'),
        ('RED', 'Red'),
        ('REVIZYON', 'Revizyon'),
    ]

    musteri = models.ForeignKey('Musteri', on_delete=models.CASCADE)
    teklif = models.ForeignKey('teklifler.Teklif', on_delete=models.CASCADE)
    tip = models.CharField(max_length=20, choices=BILDIRIM_TIPLERI)
    mesaj = models.TextField()
    okundu = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Bildirim'
        verbose_name_plural = 'Bildirimler'

    def __str__(self):
        return f"{self.get_tip_display()} - {self.musteri.ad_soyad}"