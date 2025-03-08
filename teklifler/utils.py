import logging
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)

def send_teklif_email(teklif, subject=None, template_name='emails/teklif_bildirim.html'):
    """
    Teklif ile ilgili e-posta gönderme fonksiyonu
    """
    try:
        logger.info(f"E-posta gönderme işlemi başlatıldı - Teklif ID: {teklif.id}")
        
        # Alıcı e-posta kontrolü
        if not teklif.musteri.email:
            logger.error("Müşteri e-posta adresi bulunamadı")
            return False

        context = {
            'teklif': teklif,
            'musteri': teklif.musteri,
            'durum': teklif.get_durum_display(),
            'durum_mesaji': settings.TEKLIF_BILDIRIM_MESAJLARI.get(teklif.durum, ''),
            'site_url': 'http://localhost:8000'  
        }

        logger.debug(f"E-posta şablonu hazırlanıyor - Template: {template_name}")
        
        
        html_message = render_to_string(template_name, context)
        
        # Düz metin içeriği oluştur
        plain_message = strip_tags(html_message)
        
    
        if not subject:
            subject = f'Teklif #{teklif.id} - {teklif.get_durum_display()}'

        logger.info(f"E-posta gönderiliyor - Alıcı: {teklif.musteri.email}")
        
        # E-posta ayarlarını logla
        logger.debug(f"E-posta ayarları: HOST={settings.EMAIL_HOST}, PORT={settings.EMAIL_PORT}, TLS={settings.EMAIL_USE_TLS}")
        
        # E-postayı gönder
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[teklif.musteri.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info("E-posta başarıyla gönderildi")
        return True
        
    except Exception as e:
        logger.error(f"E-posta gönderme hatası: {str(e)}")
        return False 