# Binary-Power

💳 Paycell Kampüs Cüzdanı Simülasyonu
Codenight Case: QR Ödeme, Bölüş, Bütçe ve Cashback
Bu proje, bir Codenight Case etkinliği kapsamında, Paycell benzeri bir dijital cüzdan deneyimini simüle etmek için geliştirilmiştir. Proje, özellikle bir kampüs senaryosundaki günlük harcamaları yönetmeyi kolaylaştıran temel finansal akışlara odaklanmıştır.

✨ Temel Özellikler (MVP)
Bu mini-uygulama, 6-8 saatlik süre içinde geliştirilmesi gereken beş temel alan aşağıdaki gibidir:
Cüzdan Yönetimi: Kullanıcı kayıt/giriş (mock), bakiye görüntüleme, bakiye yükleme (top-up) ve arkadaşlara transfer (P2P).

QR Ödeme (Mock): İşletme (POS) tarafından üretilen QR kodu okutma, ödeme isteğini onaylama ve başarılı/başarısız durumlarını yönetme.

Hesap Bölüşme (Split): Ödeme sonrası harcamayı arkadaşlar arasında eşit veya ağırlıklı (weight) olarak bölme ve alacak/verecek takibi.

Bütçe/Limit Takibi: Kullanıcının aylık kategori bazında bütçe tanımlaması (kafe, market, ulaşım) ve eşik (%80, %100) geçildiğinde uyarı mekanizması.

Cashback: Basit kampanya kurallarına göre iade hesaplama ve cüzdana yansıtma ("Kafe kategorisinde %5 iade", "İlk QR ödeme 20 TL iade").

🛠️ Teknik Detaylar
mock API'ler ve sahte verilerle (CSV tohumları) sistem işler.
Bu aplikasyonda FastAPI, SQLLite3 teknolojileri kullanılmıştır
Sistemi test etmek amacıyla swagger teknolojisi kullanılmıştır.
