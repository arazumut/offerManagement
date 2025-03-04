# Generated by Django 5.1.6 on 2025-03-04 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Musteri',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ad_soyad', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('telefon', models.CharField(max_length=20)),
                ('firma_adi', models.CharField(blank=True, max_length=100)),
                ('adres', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Urun',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ad', models.CharField(max_length=100)),
                ('aciklama', models.TextField()),
                ('fiyat', models.DecimalField(decimal_places=2, max_digits=10)),
                ('kategori', models.CharField(max_length=50)),
            ],
        ),
    ]
