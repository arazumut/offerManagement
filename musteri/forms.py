from django import forms
from django.contrib.auth.models import User
from .models import Musteri, Profile
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox

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
        
        if Musteri.objects.filter(email=email).exists():
            raise forms.ValidationError('Bu e-posta adresi zaten kullanılıyor.')
        
        return email

class UserRegistrationForm(forms.ModelForm):
    username = forms.CharField(label='Kullanıcı Adı')
    password = forms.CharField(label='Şifre', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Şifre (Tekrar)', widget=forms.PasswordInput)
    is_firma_sahibi = forms.BooleanField(label='Firma Sahibiyim', required=False)
    
    
    ad_soyad = forms.CharField(label='Ad Soyad', required=False)
    email = forms.EmailField(label='E-posta', required=False)
    telefon = forms.CharField(label='Telefon', required=False)
    firma_adi = forms.CharField(label='Firma Adı', required=False)
    adres = forms.CharField(label='Adres', widget=forms.Textarea(attrs={'rows': 3}), required=False)

    class Meta:
        model = User
        fields = ('username',)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Bu kullanıcı adı zaten kullanılıyor.')
        return username

    def clean_password2(self):
        cd = self.cleaned_data
        if cd.get('password') != cd.get('password2'):
            raise forms.ValidationError('Şifreler eşleşmiyor.')
        return cd['password2']

    def clean(self):
        cleaned_data = super().clean()
        is_firma_sahibi = cleaned_data.get('is_firma_sahibi')
        
        if not is_firma_sahibi:
            required_fields = {
                'ad_soyad': 'Ad Soyad',
                'email': 'E-posta',
                'telefon': 'Telefon',
                'firma_adi': 'Firma Adı',
                'adres': 'Adres'
            }
            
            for field, label in required_fields.items():
                value = cleaned_data.get(field)
                if not value or (isinstance(value, str) and not value.strip()):
                    self.add_error(field, f'{label} alanı müşteri kaydı için zorunludur.')
        
        return cleaned_data 
    





class LoginForm(forms.Form):
    username = forms.CharField(label='Kullanıcı Adı')
    password = forms.CharField(label='Şifre', widget=forms.PasswordInput)
    captcha = ReCaptchaField(
        widget=ReCaptchaV2Checkbox(
            api_params={
                'sitekey': '6LfSB_AqAAAAAMSG9Aby5buydYGN777cx4c6tSzV',
            },
            attrs={
                'data-theme': 'light',
                'data-size': 'normal',
            }
        )
    )