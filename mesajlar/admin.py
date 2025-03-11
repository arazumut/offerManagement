from django.contrib import admin
from .models import Sohbet, Mesaj

@admin.register(Sohbet)
class SohbetAdmin(admin.ModelAdmin):
    list_display = ('id', 'olusturulma_tarihi', 'son_guncelleme')
    filter_horizontal = ('katilimcilar',)

@admin.register(Mesaj)
class MesajAdmin(admin.ModelAdmin):
    list_display = ('id', 'sohbet', 'gonderen', 'gonderilme_tarihi', 'okundu')
    list_filter = ('okundu', 'gonderilme_tarihi')
    search_fields = ('icerik', 'gonderen__username')
