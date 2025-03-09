# Author: K.Umut Araz
# Date: 05.03.2025  00.39

from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import path
from .models import Teklif, TeklifUrunu

class TeklifUrunuInline(admin.TabularInline):
    model = TeklifUrunu
    extra = 1

@admin.register(Teklif)
class TeklifAdmin(admin.ModelAdmin):
    list_display = ['id', 'musteri', 'toplam_tutar', 'durum', 'created_at', 'updated_at']
    list_filter = ['durum', 'created_at']
    search_fields = ['musteri__username']
    inlines = [TeklifUrunuInline]