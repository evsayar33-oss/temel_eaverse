# Güvenlik

API anahtarlarını, broker kimlik bilgilerini veya Telegram tokenlarını dosyalara, issue'lara ve loglara yazmayın. GitHub Actions Secrets kullanın.

Bir secret sızarsa hemen sağlayıcıdan iptal edin ve yenisini oluşturun. Bu repo canlı emir göndermez. Gerçek emir entegrasyonu eklenirse ayrı bir izinli workflow ve ayrı secret kümesi kullanılmalıdır.
