from django.contrib import admin
from .models import Musteri, Urun

@admin.register(Musteri)
class MusteriAdmin(admin.ModelAdmin):
    list_display = ('ad_soyad', 'email', 'telefon', 'firma_adi')
    search_fields = ('ad_soyad', 'email', 'firma_adi')

@admin.register(Urun)
class UrunAdmin(admin.ModelAdmin):
    list_display = ('ad', 'kategori', 'fiyat')
    list_filter = ('kategori',)
    search_fields = ('ad', 'aciklama')