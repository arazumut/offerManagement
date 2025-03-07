from django import forms
from django.contrib.auth.models import User
from .models import Musteri, Profile

class MusteriTalepFormu(forms.ModelForm):
    class Meta:
        model = Musteri
        fields = ['ad_soyad', 'email', 'telefon', 'firma_adi', 'adres']
        widgets = {
            'adres': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        if self.instance and self.instance.pk:
            return self.instance.email
        
        request = getattr(self, 'request', None)
        if request and request.user.is_authenticated:
            musteri = request.user.musteri_set.first()
            if musteri:
                return musteri.email
        
        return email

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Şifre', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Şifre (Tekrar)', widget=forms.PasswordInput)
    is_firma_sahibi = forms.BooleanField(label='Firma Sahibiyim', required=False)
    
    
    ad_soyad = forms.CharField(label='Ad Soyad', required=False)
    email = forms.EmailField(label='E-posta', required=False)
    telefon = forms.CharField(label='Telefon', required=False)
    firma_adi = forms.CharField(label='Firma Adı', required=False)
    adres = forms.CharField(label='Adres', widget=forms.Textarea, required=False)

    class Meta:
        model = User
        fields = ('username',)

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Şifreler eşleşmiyor.')
        return cd['password2']

    def clean(self):
        cleaned_data = super().clean()
        is_firma_sahibi = cleaned_data.get('is_firma_sahibi')
        
        # Eğer firma sahibi değilse müşteri bilgileri zorunlu tutcaksın yine auth hatası alırsan burayı düzelt.
        if not is_firma_sahibi:
            fields = ['ad_soyad', 'email', 'telefon', 'firma_adi', 'adres']
            for field in fields:
                if not cleaned_data.get(field):
                    self.add_error(field, 'Bu alan müşteri kaydı için zorunludur.')
        
        return cleaned_data 