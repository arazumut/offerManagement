# Author: K.Umut Araz
# Date: 05.03.2025  00.39

from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Teklif, TeklifUrunu
from musteri.models import Musteri, Urun
from .serializers import (
    TeklifSerializer, MusteriSerializer, 
    UrunSerializer, TeklifUrunuSerializer
)
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from django.core.mail import send_mail
from rest_framework.permissions import IsAuthenticated

# Create your views here.

class MusteriViewSet(viewsets.ModelViewSet):
    queryset = Musteri.objects.all()
    serializer_class = MusteriSerializer

class UrunViewSet(viewsets.ModelViewSet):
    queryset = Urun.objects.all()
    serializer_class = UrunSerializer

class TeklifViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Teklif.objects.all()
    serializer_class = TeklifSerializer

    def perform_create(self, serializer):
        teklif = serializer.save(created_by=self.request.user)
        urunler_data = self.request.data.get('urunler', [])
        
        for urun_data in urunler_data:
            TeklifUrunu.objects.create(
                teklif=teklif,
                urun_id=urun_data['urun'],
                miktar=urun_data['miktar'],
                birim_fiyat=urun_data['birim_fiyat']
            )

    @action(detail=True, methods=['post'])
    def durum_guncelle(self, request, pk=None):
        teklif = self.get_object()
        yeni_durum = request.data.get('durum')
        
        if yeni_durum not in dict(Teklif.DURUM_CHOICES):
            return Response(
                {'error': 'Geçersiz durum'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        teklif.durum = yeni_durum
        teklif.save()
        return Response(TeklifSerializer(teklif).data)

    @action(detail=True, methods=['post'])
    def revizyon_iste(self, request, pk=None):
        teklif = self.get_object()
        teklif.durum = 'REVIZYON'
        teklif.save()
        return Response({'status': 'Teklif revizyona gönderildi'})

    @action(detail=True, methods=['post'])
    def onayla(self, request, pk=None):
        teklif = self.get_object()
        teklif.durum = 'ONAYLANDI'
        teklif.save()
        return Response({'status': 'Teklif onaylandı'})

    @action(detail=True, methods=['post'])
    def reddet(self, request, pk=None):
        teklif = self.get_object()
        teklif.durum = 'REDDEDILDI'
        teklif.save()
        return Response({'status': 'Teklif reddedildi'})

    @action(detail=True, methods=['get'])
    def pdf_olustur(self, request, pk=None):
        teklif = self.get_object()
        html_string = render_to_string('teklif_pdf.html', {'teklif': teklif})
        html = HTML(string=html_string)
        pdf = html.write_pdf()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'filename=teklif_{teklif.id}.pdf'
        return response

    @action(detail=True, methods=['post'])
    def email_gonder(self, request, pk=None):
        teklif = self.get_object()
        subject = f'Teklif #{teklif.id}'
        message = f'Teklif detayları: {teklif.toplam_tutar} TL\nDurum: {teklif.durum}\nNotlar: {teklif.notlar}'
        recipient_list = [teklif.musteri.email]

        send_mail(
            subject,
            message,
            'from@example.com',  
            recipient_list
        )
        return Response({'status': 'E-posta gönderildi'})