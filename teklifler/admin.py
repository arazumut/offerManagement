# Author: K.Umut Araz
# Date: 05.03.2025  00.39

from django.contrib import admin
from .models import Teklif, TeklifUrunu

class TeklifUrunuInline(admin.TabularInline):
    model = TeklifUrunu
    extra = 1

@admin.register(Teklif)
class TeklifAdmin(admin.ModelAdmin):
    list_display = ('id', 'musteri', 'toplam_tutar', 'durum', 'created_at')
    list_filter = ('durum', 'created_at')
    inlines = [TeklifUrunuInline]