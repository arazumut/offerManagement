# Generated by Django 5.1.6 on 2025-03-06 23:14

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('musteri', '0002_profile'),
        ('teklifler', '0002_alter_teklif_durum'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TeklifAnalitik',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tarih', models.DateField(auto_now_add=True)),
                ('toplam_teklif', models.IntegerField(default=0)),
                ('onaylanan_teklif', models.IntegerField(default=0)),
                ('reddedilen_teklif', models.IntegerField(default=0)),
                ('ortalama_yanit_suresi', models.DurationField(null=True)),
            ],
        ),
        migrations.AlterModelOptions(
            name='musteri',
            options={'verbose_name': 'Müşteri', 'verbose_name_plural': 'Müşteriler'},
        ),
        migrations.AddField(
            model_name='musteri',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Bildirim',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tip', models.CharField(choices=[('ONAY', 'Onay'), ('RED', 'Red'), ('REVIZYON', 'Revizyon')], max_length=20)),
                ('mesaj', models.TextField()),
                ('okundu', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('musteri', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='musteri.musteri')),
                ('teklif', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teklifler.teklif')),
            ],
            options={
                'verbose_name': 'Bildirim',
                'verbose_name_plural': 'Bildirimler',
                'ordering': ['-created_at'],
            },
        ),
    ]
