from rest_framework import serializers
from .models import Teklif, TeklifUrunu
from musteri.models import Musteri, Urun

# Author: K.Umut Araz
# Date: 05.03.2025  00.39

class MusteriSerializer(serializers.ModelSerializer):
    class Meta:
        model = Musteri
        fields = '__all__'

class UrunSerializer(serializers.ModelSerializer):
    class Meta:
        model = Urun
        fields = '__all__'

class TeklifUrunuSerializer(serializers.ModelSerializer):
    urun_adi = serializers.CharField(source='urun.ad', read_only=True)
    
    class Meta:
        model = TeklifUrunu
        fields = ['id', 'urun', 'urun_adi', 'miktar', 'birim_fiyat']

class TeklifSerializer(serializers.ModelSerializer):
    urunler = TeklifUrunuSerializer(source='teklifurunu_set', many=True)
    musteri_bilgisi = MusteriSerializer(source='musteri', read_only=True)

    class Meta:
        model = Teklif
        fields = ['id', 'musteri', 'musteri_bilgisi', 'urunler', 'toplam_tutar', 
                 'durum', 'notlar', 'created_at', 'updated_at'] 