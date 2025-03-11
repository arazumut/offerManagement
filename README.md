# Teklif Yönetim Sistemi

Bu proje, firmaların müşterilerine teklif verme sürecini dijitalleştiren ve yöneten bir web uygulamasıdır. Sistem, müşterilerin teklif taleplerini oluşturmasına, firma sahiplerinin bu teklifleri yönetmesine ve tekliflerin durumlarını takip etmesine olanak sağlar.

## 🚀 Özellikler

### 👥 Kullanıcı Yönetimi
- **Kullanıcı Rolleri**: 
  - Firma Sahibi
  - Normal Kullanıcı
- **Kimlik Doğrulama**: Güvenli giriş ve kayıt sistemi
- **Yetkilendirme**: Role dayalı erişim kontrolü

### 📝 Teklif Yönetimi
- **Teklif Oluşturma**: Müşteriler için kolay teklif talep formu
- **Durum Takibi**: Tekliflerin durumlarını anlık takip
  - Beklemede
  - Onaylandı
  - Reddedildi
  - Revizyon
- **PDF Çıktısı**: Tekliflerin PDF formatında çıktısını alma
- **E-posta Bildirimleri**: Teklif durumu değişikliklerinde otomatik bildirimler
- **Teklif Detayları**: Tekliflerin detaylı bilgilerini görüntüleme

### 💼 Firma Sahibi Paneli
- **Teklif Listesi**: Tüm tekliflerin görüntülenmesi
- **Teklif İşlemleri**:
  - Onaylama
  - Reddetme
  - Revizyon İsteme
  - Düzenleme
- **Müşteri Yönetimi**: Müşteri bilgilerinin takibi
- **Teklif Analitiği**: Tekliflerin performansını analiz etme

### 🎨 Kullanıcı Arayüzü
- **Responsive Tasarım**: Mobil uyumlu arayüz
- **Modern UI**: Bootstrap 5 ile geliştirilmiş kullanıcı dostu arayüz
- **Bildirimler**: İşlem durumları için anlık bildirimler
- **Tema Desteği**: Karanlık ve aydınlık tema seçenekleri

### 📊 Dashboard
- **Performans Metrikleri**: Toplam teklif, onay oranı, ortalama yanıt süresi
- **Grafikler**: Aylık teklif istatistikleri, sektörel dağılım
- **En Aktif Müşteriler**: En çok teklif talebi oluşturan müşteriler
- **Gerçek Zamanlı Veriler**: Anlık veri güncellemeleri

### 📈 Raporlama
- **Excel Raporu**: Teklif raporlarını Excel formatında indirme
- **Detaylı Analitikler**: Teklif performansını izleme ve analiz etme

### 💬 Mesajlaşma Sistemi
- **Kullanıcılar Arası Mesajlaşma**: Firma sahipleri ve müşteriler arasında mesajlaşma
- **WebSocket Desteği**: Gerçek zamanlı mesajlaşma

## 🛠 Teknolojiler

- **Backend**: Django 4.2+
- **Frontend**: Bootstrap 5
- **API**: Django Rest Framework
- **Veritabanı**: SQLite/PostgreSQL
- **PDF İşleme**: WeasyPrint
- **Form İşleme**: Django Crispy Forms
- **İkonlar**: Font Awesome
- **Grafikler**: Chart.js
- **Veri İşleme**: Pandas

## 📋 Gereksinimler 

- Python 3.8+
- Django 4.2+
- PostgreSQL veya SQLite
- WeasyPrint
- Django Rest Framework
- Django Crispy Forms
- Font Awesome
- Pandas
- Chart.js

## 🚀 Kurulum

1. Projeyi klonlayın:

```bash
git clone https://github.com/arazumut/offerManagement.git

cd teklif_yonetim_sistemi


3. Gereksinimleri yükleyin:

bash
pip install -r requirements.txt



4. Veritabanı migrationlarını yapın:

bash
python manage.py migrate



5. Sunucuyu başlatın:

bash
python manage.py runserver


## 👥 Kullanıcı Rolleri ve İşlevler

### 📱 Müşteri
- Teklif talebi oluşturma
- Teklif durumunu görüntüleme
- PDF çıktısı alma

### 👔 Firma Sahibi
- Tüm teklifleri görüntüleme
- Teklif durumunu güncelleme
- Müşteri bilgilerini yönetme
- PDF oluşturma ve e-posta gönderme

## 🔒 Güvenlik

- CSRF koruması
- Kullanıcı kimlik doğrulama
- Role dayalı erişim kontrolü
- Güvenli parola yönetimi

## 📧 E-posta Ayarları

E-posta gönderimi için SMTP ayarlarını `settings.py` dosyasında yapılandırın:






