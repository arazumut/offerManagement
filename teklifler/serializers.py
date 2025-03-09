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
        fields = ['id', 'urun', 'urun_adi', 'miktar', 'birim_fiyat', 'indirim_orani', 'vergi_orani', 'toplam_fiyat']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        birim_fiyat = instance.birim_fiyat
        miktar = instance.miktar
        indirim_orani = instance.indirim_orani if hasattr(instance, 'indirim_orani') else 0
        vergi_orani = instance.vergi_orani if hasattr(instance, 'vergi_orani') else 0
        

        indirimli_fiyat = birim_fiyat * (1 - indirim_orani/100)
        
        vergili_fiyat = indirimli_fiyat * (1 + vergi_orani/100)
        
        toplam_fiyat = vergili_fiyat * miktar
        
        representation['toplam_fiyat'] = round(toplam_fiyat, 2)
        return representation

class TeklifSerializer(serializers.ModelSerializer):
    urunler = TeklifUrunuSerializer(source='teklifurunu_set', many=True)
    musteri_bilgisi = MusteriSerializer(source='musteri', read_only=True)
    durum_aciklamasi = serializers.CharField(source='get_durum_display', read_only=True)

    class Meta:
        model = Teklif
        fields = ['id', 'musteri', 'musteri_bilgisi', 'urunler', 'toplam_tutar', 
                 'durum', 'durum_aciklamasi', 'notlar', 'created_at', 'updated_at']

    def create(self, validated_data):
        urunler_data = validated_data.pop('teklifurunu_set')
        teklif = Teklif.objects.create(**validated_data)
        
        for urun_data in urunler_data:
            TeklifUrunu.objects.create(teklif=teklif, **urun_data)
            
        return teklif
    
    def update(self, instance, validated_data):
        urunler_data = validated_data.pop('teklifurunu_set', [])
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
                        
        instance.teklifurunu_set.all().delete()
        for urun_data in urunler_data:
            TeklifUrunu.objects.create(teklif=instance, **urun_data)
            
        return instance 