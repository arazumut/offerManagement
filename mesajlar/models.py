from django.db import models
from django.contrib.auth.models import User

class Sohbet(models.Model):
    katilimcilar = models.ManyToManyField(User, related_name='sohbetler')
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True)
    son_guncelleme = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Sohbet {self.id}"

class Mesaj(models.Model):
    sohbet = models.ForeignKey(Sohbet, on_delete=models.CASCADE, related_name='mesajlar')
    gonderen = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gonderilen_mesajlar')
    icerik = models.TextField()
    gonderilme_tarihi = models.DateTimeField(auto_now_add=True)
    okundu = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['gonderilme_tarihi']
    
    def __str__(self):
        return f"{self.gonderen.username}: {self.icerik[:50]}"
