from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import MusteriTalepFormu, UserRegistrationForm
from teklifler.models import Teklif
from django.contrib.auth import login
from .models import Profile, Musteri
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg, Q, F
from django.db.models.functions import TruncMonth
import pandas as pd
from django.http import HttpResponse
import json
from django.core.serializers.json import DjangoJSONEncoder

# Create your views here.

def anasayfa(request):
    return render(request, 'anasayfa.html')

def musteri_talep_formu(request):
    if request.method == 'POST':
        form = MusteriTalepFormu(request.POST)
        if form.is_valid():
            musteri = form.save()
            talep_detay = request.POST.get('talep_detay')
            
            
            Teklif.objects.create(
                musteri=musteri,
                notlar=talep_detay,
                toplam_tutar=0  
            )
            
            messages.success(request, 'Teklif talebiniz başarıyla alınmıştır.')
            return redirect('talep_basarili')
    else:
        form = MusteriTalepFormu()
    
    return render(request, 'musteri/talep_formu.html', {'form': form})

def talep_basarili(request):
    return render(request, 'musteri/talep_basarili.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            Profile.objects.create(user=new_user, is_firma_sahibi=form.cleaned_data['is_firma_sahibi'])
            login(request, new_user)
            return redirect('anasayfa')
    else:
        form = UserRegistrationForm()
    return render(request, 'musteri/register.html', {'form': form})

@login_required
def firma_sahibi_paneli(request):
    if not request.user.profile.is_firma_sahibi:
        return redirect('anasayfa')  

    teklifler = Teklif.objects.all()
    return render(request, 'musteri/firma_sahibi_paneli.html', {'teklifler': teklifler})

@login_required
def dashboard(request):
    if not request.user.profile.is_firma_sahibi:
        return redirect('anasayfa')

    # En aktif müşteriler
    aktif_musteriler = Musteri.objects.annotate(
        teklif_sayisi=Count('teklif')
    ).order_by('-teklif_sayisi')[:10]

    # Aylık teklif istatistikleri
    aylik_teklifler = Teklif.objects.annotate(
        ay=TruncMonth('created_at')
    ).values('ay').annotate(
        toplam=Count('id'),
        onaylanan=Count('id', filter=Q(durum='ONAYLANDI')),
        reddedilen=Count('id', filter=Q(durum='REDDEDILDI'))
    ).order_by('ay')

    # Grafik verilerini hazırla
    aylik_teklifler_labels = json.dumps(
        [teklif['ay'].strftime('%B %Y') for teklif in aylik_teklifler],
        cls=DjangoJSONEncoder
    )
    aylik_teklifler_data = json.dumps(
        [teklif['toplam'] for teklif in aylik_teklifler]
    )

    # Sektörel dağılım verilerini hazırla
    sektor_dagilimi = Musteri.objects.values('firma_adi').annotate(
        toplam=Count('id')
    ).order_by('-toplam')
    
    sektor_labels = json.dumps(
        [sektor['firma_adi'] or 'Diğer' for sektor in sektor_dagilimi]
    )
    sektor_data = json.dumps(
        [sektor['toplam'] for sektor in sektor_dagilimi]
    )

    # Performans metrikleri
    toplam_teklif = Teklif.objects.count()
    performans = {
        'toplam_teklif': toplam_teklif,
        'ortalama_yanit_suresi': Teklif.objects.filter(
            durum__in=['ONAYLANDI', 'REDDEDILDI']
        ).aggregate(
            avg_sure=Avg(F('updated_at') - F('created_at'))
        )['avg_sure'],
        'onay_orani': (Teklif.objects.filter(durum='ONAYLANDI').count() / toplam_teklif * 100) if toplam_teklif > 0 else 0
    }

    context = {
        'aylik_teklifler': aylik_teklifler,
        'aylik_teklifler_labels': aylik_teklifler_labels,
        'aylik_teklifler_data': aylik_teklifler_data,
        'aktif_musteriler': aktif_musteriler,
        'sektor_labels': sektor_labels,
        'sektor_data': sektor_data,
        'performans': performans
    }

    return render(request, 'musteri/dashboard.html', context)

@login_required
def export_rapor(request):
    if not request.user.profile.is_firma_sahibi:
        return redirect('anasayfa')

    # Excel raporu oluştur
    teklifler = Teklif.objects.all().values(
        'id', 'musteri__ad_soyad', 'toplam_tutar',
        'durum', 'created_at', 'updated_at'
    )

    df = pd.DataFrame(list(teklifler))
    
    # Excel dosyası oluştur
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="teklif_raporu.xlsx"'
    
    df.to_excel(response, index=False)
    return response
