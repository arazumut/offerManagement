from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import MusteriTalepFormu, UserRegistrationForm
from teklifler.models import Teklif
from django.contrib.auth import login
from .models import Profile, Musteri, Bildirim
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg, Q, F
from django.db.models.functions import TruncMonth
import pandas as pd
from django.http import HttpResponse, JsonResponse
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
import logging
from datetime import timedelta

# Create your views here.

logger = logging.getLogger(__name__)

def anasayfa(request):
    if not request.user.is_authenticated:
        return render(request, 'anasayfa.html')
    
    try:
        # Kullanıcı girişi yapılmışsa, profilini kontrol etmemiz gerekiyor
        if hasattr(request.user, 'profile'):
            if request.user.profile.is_firma_sahibi:
                # Firma sahibi ise firma paneline yönlendirmemiz gerekiyor
                return redirect('firma_sahibi_paneli')
            else:
                # Müşteri ise müşteri paneline yönlendirmemiz gerekiyor
                return redirect('musteri_paneli')
        
        return render(request, 'anasayfa.html')
        
    except Exception as e:
        logger.error(f"Anasayfa hatası: {str(e)}")
        messages.error(request, 'Bir hata oluştu. Lütfen daha sonra tekrar deneyin.')
        return render(request, 'anasayfa.html')

def musteri_talep_formu(request):
    if request.method == 'POST':
        form = MusteriTalepFormu(request.POST)
        if form.is_valid():
            # Eğer kullanıcı giriş yapmışsa ve müşteri kaydı varsa, mevcut müşteriyi kullan auth hatası alırsam bu düzeltilecek unutma!
            if request.user.is_authenticated:
                musteri = request.user.musteri_set.first()
                if not musteri:
                    musteri = form.save(commit=False)
                    musteri.user = request.user
                    musteri.save()
            else:
                musteri = form.save()
            
            talep_detay = request.POST.get('talep_detay')
            
            
            Teklif.objects.create(
                musteri=musteri,
                notlar=talep_detay,
                toplam_tutar=0,
                durum='BEKLEMEDE'
            )
            
            messages.success(request, 'Teklif talebiniz başarıyla alınmıştır.')
            if request.user.is_authenticated:
                return redirect('musteri_paneli')
            return redirect('talep_basarili')
    else:
        initial_data = {}
        if request.user.is_authenticated:
            musteri = request.user.musteri_set.first()
            if musteri:
                initial_data = {
                    'ad_soyad': musteri.ad_soyad,
                    'email': musteri.email,
                    'telefon': musteri.telefon,
                    'firma_adi': musteri.firma_adi,
                    'adres': musteri.adres
                }
        form = MusteriTalepFormu(initial=initial_data)
    
    return render(request, 'musteri/talep_formu.html', {'form': form})

def talep_basarili(request):
    return render(request, 'musteri/talep_basarili.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Kullanıcıyı oluştur
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            
            
            Profile.objects.create(
                user=new_user, 
                is_firma_sahibi=form.cleaned_data['is_firma_sahibi']
            )
            
            # Eğer firma sahibi değilse müşteri olarak kaydet olarak eklemek zorundayız unutma!
            if not form.cleaned_data['is_firma_sahibi']:
                Musteri.objects.create(
                    user=new_user,
                    ad_soyad=form.cleaned_data.get('ad_soyad', ''),
                    email=form.cleaned_data.get('email', ''),
                    telefon=form.cleaned_data.get('telefon', ''),
                    firma_adi=form.cleaned_data.get('firma_adi', ''),
                    adres=form.cleaned_data.get('adres', '')
                )
            
            login(request, new_user)
            return redirect('anasayfa')
    else:
        form = UserRegistrationForm()
    return render(request, 'musteri/register.html', {'form': form})

@login_required
def firma_sahibi_paneli(request):
    if not request.user.profile.is_firma_sahibi:
        messages.error(request, 'Bu sayfaya erişim yetkiniz bulunmuyor.')
        return redirect('anasayfa')
    
    teklifler = Teklif.objects.all().order_by('-created_at')
    return render(request, 'musteri/firma_sahibi_paneli.html', {'teklifler': teklifler})

@login_required
def dashboard(request):
    try:
        if not request.user.profile.is_firma_sahibi:
            messages.error(request, 'Bu sayfaya erişim yetkiniz bulunmuyor.')
            return redirect('anasayfa')

    
        aktif_musteriler = Musteri.objects.annotate(
            teklif_sayisi=Count('teklif')
        ).order_by('-teklif_sayisi')[:10]

    
        aylik_teklifler = Teklif.objects.annotate(
            ay=TruncMonth('created_at')
        ).values('ay').annotate(
            toplam=Count('id'),
            onaylanan=Count('id', filter=Q(durum='ONAYLANDI')),
            reddedilen=Count('id', filter=Q(durum='REDDEDILDI')),
            bekleyen=Count('id', filter=Q(durum='BEKLEMEDE'))
        ).order_by('ay')

        aylik_veriler = []
        for teklif in aylik_teklifler:
            if teklif['ay']:  # ay değeri None değilse
                ay_str = teklif['ay'].strftime('%B %Y')
                aylik_veriler.append({
                    'ay': ay_str,
                    'toplam': teklif['toplam'],
                    'onaylanan': teklif['onaylanan'],
                    'reddedilen': teklif['reddedilen'],
                    'bekleyen': teklif['bekleyen']
                })

        sektor_dagilimi = Musteri.objects.values('firma_adi').annotate(
            teklif_sayisi=Count('teklif')
        ).order_by('-teklif_sayisi')

        sektor_veriler = []
        for sektor in sektor_dagilimi:
            firma_adi = sektor['firma_adi'] if sektor['firma_adi'] else 'Diğer'
            sektor_veriler.append({
                'firma_adi': firma_adi,
                'teklif_sayisi': sektor['teklif_sayisi']
            })

        
        toplam_teklif = Teklif.objects.count()
        onaylanan_teklif = Teklif.objects.filter(durum='ONAYLANDI').count()
        
        try:
            onay_orani = (onaylanan_teklif / toplam_teklif * 100) if toplam_teklif > 0 else 0
        except ZeroDivisionError:
            onay_orani = 0

        tamamlanan_teklifler = Teklif.objects.filter(
            durum__in=['ONAYLANDI', 'REDDEDILDI']
        ).exclude(
            updated_at__isnull=True
        )

        toplam_sure = timedelta()
        tamamlanan_sayi = 0
        
        for teklif in tamamlanan_teklifler:
            if teklif.updated_at and teklif.created_at:
                sure = teklif.updated_at - teklif.created_at
                toplam_sure += sure
                tamamlanan_sayi += 1

        ortalama_sure = toplam_sure / tamamlanan_sayi if tamamlanan_sayi > 0 else timedelta()

        performans = {
            'toplam_teklif': toplam_teklif,
            'onaylanan_teklif': onaylanan_teklif,
            'reddedilen_teklif': Teklif.objects.filter(durum='REDDEDILDI').count(),
            'bekleyen_teklif': Teklif.objects.filter(durum='BEKLEMEDE').count(),
            'ortalama_yanit_suresi': ortalama_sure,
            'onay_orani': round(onay_orani, 2)
        }

        context = {
            'aktif_musteriler': aktif_musteriler,
            'aylik_veriler': json.dumps(aylik_veriler, cls=DjangoJSONEncoder),
            'sektor_veriler': json.dumps(sektor_veriler, cls=DjangoJSONEncoder),
            'performans': performans
        }

        return render(request, 'musteri/dashboard.html', context)

    except Exception as e:
        logger.error(f"Dashboard hatası: {str(e)}")
        messages.error(request, 'Dashboard yüklenirken bir hata oluştu. Lütfen daha sonra tekrar deneyin.')
        return redirect('firma_sahibi_paneli')

@login_required
def export_rapor(request):
    if not request.user.profile.is_firma_sahibi:
        return redirect('anasayfa')

    teklifler = Teklif.objects.all().values(
        'id', 'musteri__ad_soyad', 'toplam_tutar',
        'durum', 'created_at', 'updated_at'
    )

    df = pd.DataFrame(list(teklifler))
    
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="teklif_raporu.xlsx"'
    
    df.to_excel(response, index=False)
    return response

@login_required
@require_POST
def teklif_islem(request, teklif_id, islem_tipi):
    try:
        if not request.user.profile.is_firma_sahibi:
            return JsonResponse({
                'success': False,
                'error': 'Bu işlem için yetkiniz bulunmuyor.'
            }, status=403)
        
        teklif = get_object_or_404(Teklif, id=teklif_id)
        
        if teklif.durum in ['ONAYLANDI', 'REDDEDILDI']:
            return JsonResponse({
                'success': False,
                'error': 'Bu teklif için işlem yapılamaz.'
            }, status=400)
        
        aciklama = request.POST.get('aciklama', '').strip()
        if not aciklama:
            return JsonResponse({
                'success': False,
                'error': 'Açıklama alanı zorunludur.'
            }, status=400)

        if islem_tipi == 'onay':
            try:
                fiyat = float(request.POST.get('fiyat', 0))
                if fiyat <= 0:
                    return JsonResponse({
                        'success': False,
                        'error': 'Geçerli bir fiyat giriniz.'
                    }, status=400)
                
                teklif.toplam_tutar = fiyat
                teklif.durum = 'ONAYLANDI'
                mesaj = f"Teklifiniz {fiyat:,.2f} TL tutarında onaylanmıştır. Açıklama: {aciklama}"
                bildirim_tipi = 'ONAY'
                
            except (ValueError, TypeError):
                return JsonResponse({
                    'success': False,
                    'error': 'Geçersiz fiyat formatı.'
                }, status=400)
                
        elif islem_tipi == 'red':
            teklif.durum = 'REDDEDILDI'
            mesaj = f"Teklifiniz reddedilmiştir. Sebep: {aciklama}"
            bildirim_tipi = 'RED'
            
        elif islem_tipi == 'revizyon':
            teklif.durum = 'REVIZYON'
            mesaj = f"Teklifiniz için revizyon talep edildi. Detaylar: {aciklama}"
            bildirim_tipi = 'REVIZYON'
            
        else:
            return JsonResponse({
                'success': False,
                'error': 'Geçersiz işlem tipi.'
            }, status=400)
        
        teklif.save()
        
        Bildirim.objects.create(
            musteri=teklif.musteri,
            teklif=teklif,
            tip=bildirim_tipi,
            mesaj=mesaj
        )
        
        return JsonResponse({
            'success': True,
            'message': mesaj
        })
        
    except Teklif.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Teklif bulunamadı.'
        }, status=404)
        
    except Exception as e:
        logger.error(f"Teklif işlem hatası - Teklif ID: {teklif_id}, İşlem: {islem_tipi}, Hata: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'İşlem sırasında bir hata oluştu. Lütfen daha sonra tekrar deneyin.'
        }, status=500)

@login_required
def bildirimler(request):
    try:
        musteri = request.user.musteri_set.first()
        if not musteri:
            return redirect('anasayfa')
        
        bildirimler = Bildirim.objects.filter(musteri=musteri, okundu=False)
        return render(request, 'musteri/bildirimler.html', {
            'bildirimler': bildirimler
        })
    except Exception as e:
        logger.error(f"Hata: {str(e)}")
        return JsonResponse({'error': 'Bir hata oluştu'}, status=500)

@login_required
def musteri_paneli(request):
    try:
        musteri = request.user.musteri_set.first()
        if not musteri:
            messages.error(request, 'Müşteri hesabı bulunamadı.')
            return redirect('anasayfa')
        
        teklifler = Teklif.objects.filter(musteri=musteri)
        
        teklifler_data = {
            'all': teklifler.order_by('-created_at'),
            'count': teklifler.count(),
            'onaylanan': teklifler.filter(durum='ONAYLANDI').count(),
            'reddedilen': teklifler.filter(durum='REDDEDILDI').count(),
            'bekleyen': teklifler.filter(durum='BEKLEMEDE').count()
        }
        
        bildirimler = Bildirim.objects.filter(musteri=musteri, okundu=False)
        
        return render(request, 'musteri/musteri_paneli.html', {
            'musteri': musteri,
            'teklifler': teklifler_data,
            'bildirimler': bildirimler,
            'bildirim_sayisi': bildirimler.count()
        })
    except Exception as e:
        logger.error(f"Müşteri paneli hatası: {str(e)}")
        messages.error(request, 'Bir hata oluştu. Lütfen daha sonra tekrar deneyin.')
        return redirect('anasayfa')

@login_required
def teklif_detay(request, teklif_id):
    try:
        musteri = request.user.musteri_set.first()
        if not musteri:
            return JsonResponse({'error': 'Yetkisiz erişim'}, status=403)
        
        teklif = get_object_or_404(Teklif, id=teklif_id, musteri=musteri)
        bildirimler = Bildirim.objects.filter(teklif=teklif).order_by('-created_at')
        
        return JsonResponse({
            'id': teklif.id,
            'durum': teklif.get_durum_display(),
            'created_at': teklif.created_at.strftime('%d.%m.%Y %H:%M'),
            'updated_at': teklif.updated_at.strftime('%d.%m.%Y %H:%M'),
            'toplam_tutar': float(teklif.toplam_tutar) if teklif.toplam_tutar else 0,
            'notlar': teklif.notlar,
            'bildirimler': [{
                'tip': bildirim.get_tip_display(),
                'mesaj': bildirim.mesaj,
                'tarih': bildirim.created_at.strftime('%d.%m.%Y %H:%M')
            } for bildirim in bildirimler]
        })
    except Exception as e:
        logger.error(f"Teklif detay hatası - Teklif ID: {teklif_id}, Hata: {str(e)}")
        return JsonResponse({'error': 'Teklif detayı alınamadı'}, status=500)
