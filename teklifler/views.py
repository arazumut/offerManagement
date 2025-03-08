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
from .utils import send_teklif_email

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
        
    
        try:
            self.email_gonder(request, pk=pk)
        except Exception as e:
            
            pass
            
        return Response(TeklifSerializer(teklif).data)
    # mail entegresyon denemesi.

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
        try:
            teklif = self.get_object()
            subject = f'Teklif #{teklif.id} - Durum Güncellemesi'
            
            
            html_message = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #2c3e50;">Teklif Durumu Güncellendi</h2>
                        <p>Sayın {teklif.musteri.ad_soyad},</p>
                        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                            <p><strong>Teklif No:</strong> #{teklif.id}</p>
                            <p><strong>Durum:</strong> {teklif.get_durum_display()}</p>
                            <p><strong>Toplam Tutar:</strong> {teklif.toplam_tutar} TL</p>
                            <p><strong>Son Güncelleme:</strong> {teklif.updated_at.strftime('%d.%m.%Y %H:%M')}</p>
                        </div>
                        {f'<p><strong>Notlar:</strong> {teklif.notlar}</p>' if teklif.notlar else ''}
                        <hr style="border: 1px solid #eee; margin: 20px 0;">
                        <p style="color: #666; font-size: 12px;">
                            Bu e-posta otomatik olarak gönderilmiştir. Lütfen yanıtlamayınız.
                        </p>
                    </div>
                </body>
            </html>
            """
            
            
            plain_message = f"""
            Teklif Durumu Güncellendi
            
            Sayın {teklif.musteri.ad_soyad},
            
            Teklif No: #{teklif.id}
            Durum: {teklif.get_durum_display()}
            Toplam Tutar: {teklif.toplam_tutar} TL
            Son Güncelleme: {teklif.updated_at.strftime('%d.%m.%Y %H:%M')}
            
            {f'Notlar: {teklif.notlar}' if teklif.notlar else ''}
            
            Bu e-posta otomatik olarak gönderilmiştir. Lütfen yanıtlamayınız.
            """

            send_mail(
                subject=subject,
                message=plain_message,
                html_message=html_message,
                from_email=None,  # settings.py'deki DEFAULT_FROM_EMAIL kullanılacak
                recipient_list=[teklif.musteri.email],
                fail_silently=False,
            )
            
            return Response({'status': 'E-posta başarıyla gönderildi'})
            
        except Exception as e:
            return Response(
                {'error': f'E-posta gönderilirken bir hata oluştu: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )