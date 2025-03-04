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

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password', widget=forms.PasswordInput)
    is_firma_sahibi = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2'] 