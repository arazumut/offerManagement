# Generated by Django 5.1.6 on 2025-03-14 14:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Sohbet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('olusturulma_tarihi', models.DateTimeField(auto_now_add=True)),
                ('son_guncelleme', models.DateTimeField(auto_now=True)),
                ('katilimcilar', models.ManyToManyField(related_name='sohbetler', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Mesaj',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('icerik', models.TextField()),
                ('gonderilme_tarihi', models.DateTimeField(auto_now_add=True)),
                ('okundu', models.BooleanField(default=False)),
                ('gonderen', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gonderilen_mesajlar', to=settings.AUTH_USER_MODEL)),
                ('sohbet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mesajlar', to='mesajlar.sohbet')),
            ],
            options={
                'ordering': ['gonderilme_tarihi'],
            },
        ),
    ]
