from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import MusteriTalepFormu, UserRegistrationForm
from teklifler.models import Teklif
from django.contrib.auth import login
from .models import Profile
from django.contrib.auth.decorators import login_required

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
