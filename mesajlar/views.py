from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Count, Max, F, OuterRef, Subquery
from .models import Sohbet, Mesaj
from django.db.models.functions import Coalesce

@login_required
def sohbet_listesi(request):

    sohbetler = Sohbet.objects.filter(katilimcilar=request.user)
    
    # Son mesaj alt sorgusu
    son_mesaj_subquery = Mesaj.objects.filter(
        sohbet=OuterRef('pk')
    ).order_by('-gonderilme_tarihi').values('icerik', 'gonderilme_tarihi', 'gonderen')[:1]
    
    # Okunmamış mesaj sayısı
    sohbetler = sohbetler.annotate(
        son_mesaj_icerik=Subquery(son_mesaj_subquery.values('icerik')),
        son_mesaj_tarihi=Subquery(son_mesaj_subquery.values('gonderilme_tarihi')),
        son_mesaj_gonderen=Subquery(son_mesaj_subquery.values('gonderen')),
        okunmamis_mesaj_sayisi=Count(
            'mesajlar', 
            filter=Q(mesajlar__okundu=False) & ~Q(mesajlar__gonderen=request.user)
        )
    ).order_by('-son_mesaj_tarihi')
    
    # Her sohbet için diğer katılımcıyı bul
    for sohbet in sohbetler:
        sohbet.diger_katilimci = sohbet.katilimcilar.exclude(id=request.user.id).first()
        
        # Son mesaj bilgisini ekle
        if hasattr(sohbet, 'son_mesaj_icerik') and sohbet.son_mesaj_icerik:
            sohbet.son_mesaj = {
                'icerik': sohbet.son_mesaj_icerik,
                'gonderilme_tarihi': sohbet.son_mesaj_tarihi,
                'gonderen_id': sohbet.son_mesaj_gonderen
            }
        else:
            sohbet.son_mesaj = None
    
    return render(request, 'mesajlar/sohbet_listesi.html', {
        'sohbetler': sohbetler,
    })

@login_required
def yeni_sohbet(request, alici_id):
    alici = get_object_or_404(User, id=alici_id)


    sohbetler = Sohbet.objects.filter(katilimcilar=request.user).filter(katilimcilar=alici)
    
    if sohbetler.exists():
    
        return redirect('mesajlar:sohbet_detay', sohbet_id=sohbetler.first().id)
    else:

        yeni_sohbet = Sohbet.objects.create()
        yeni_sohbet.katilimcilar.add(request.user, alici)
        return redirect('mesajlar:sohbet_detay', sohbet_id=yeni_sohbet.id)

@login_required
def sohbet_detay(request, sohbet_id):
    sohbet = get_object_or_404(Sohbet, id=sohbet_id, katilimcilar=request.user)
    mesajlar = sohbet.mesajlar.all()
    
    # Okunmamış mesajları okundu olarak işaretle
    mesajlar.filter(~Q(gonderen=request.user), okundu=False).update(okundu=True)
    
    # Diğer katılımcıyı bul
    diger_katilimci = sohbet.katilimcilar.exclude(id=request.user.id).first()
    
    return render(request, 'mesajlar/sohbet_detay.html', {
        'sohbet': sohbet,
        'mesajlar': mesajlar,
        'diger_katilimci': diger_katilimci,
    })

@login_required
def kullanici_listesi(request):
    
    if hasattr(request.user, 'profile') and request.user.profile.is_firma_sahibi:
        # Firma sahibi ise müşterileri göster
        kullanicilar = User.objects.filter(profile__is_firma_sahibi=False)
    else:
        # Müşteri ise firma sahiplerini göster
        kullanicilar = User.objects.filter(profile__is_firma_sahibi=True)
    
    return render(request, 'mesajlar/kullanici_listesi.html', {
        'kullanicilar': kullanicilar,
    })
