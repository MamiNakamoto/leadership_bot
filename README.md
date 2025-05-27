# Leadership Bot

Telegram grubu için haftalık liderlik tablosu botu. Adminler kullanıcılara puan ekleyip çıkarabilir.

## Özellikler

- 📊 Haftalık liderlik tablosu
- ➕ Puan ekleme/silme (admin)
- 🔄 Tabloyu sıfırlama (admin)
- 👥 Admin ekleme
- 💾 Otomatik veritabanı yedekleme

## Komutlar

- `/siralama` - Liderlik tablosunu gösterir
- `/puanekle @kullanici` - Kullanıcıya puan ekler (admin)
- `/puansil @kullanici` - Kullanıcıdan puan siler (admin)
- `/sifirla` - Liderlik tablosunu sıfırlar (admin)
- `/adminekle @kullanici` - Yeni admin ekler (admin)

## Kurulum

1. Gereksinimleri yükleyin:
```bash
pip install -r requirements.txt
```

2. Bot token ve kanal ID'lerini `bot.py` dosyasında güncelleyin:
```python
BOT_TOKEN = "YOUR_BOT_TOKEN"
YED_KANAL_ID = -100****  # Yedekleme kanalı ID
MEXC_GROUP_ID = -10******
  # Ana grup ID
```

3. Botu çalıştırın:
```bash
python bot.py
```
