# Generated by Django 5.1.6 on 2025-03-07 23:39

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('musteri', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Teklif',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('toplam_tutar', models.DecimalField(decimal_places=2, max_digits=10)),
                ('durum', models.CharField(choices=[('BEKLEMEDE', 'Beklemede'), ('ONAYLANDI', 'Onaylandı'), ('REDDEDILDI', 'Reddedildi'), ('REVIZYON', 'Revizyon')], default='BEKLEMEDE', max_length=20)),
                ('notlar', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('musteri', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='musteri.musteri')),
            ],
        ),
        migrations.CreateModel(
            name='TeklifUrunu',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('miktar', models.PositiveIntegerField(default=1)),
                ('birim_fiyat', models.DecimalField(decimal_places=2, max_digits=10)),
                ('teklif', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teklifler.teklif')),
                ('urun', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='musteri.urun')),
            ],
        ),
        migrations.AddField(
            model_name='teklif',
            name='urunler',
            field=models.ManyToManyField(through='teklifler.TeklifUrunu', to='musteri.urun'),
        ),
    ]
