# 60 Saniyede İşletme

Her sabah bir işletme kavramını Türkçe, İngilizce, Almanca ve Rusça 30–45 saniyelik dikey videoya dönüştürür, Telegram'dan onaya sunar ve onaylananları YouTube Shorts ile Instagram Reels'e yükler.

## Kurulum

1. Bu klasörü **public** bir GitHub reposuna gönderin; Settings > Pages > Source: **GitHub Actions**.
2. `araclar/token_al.py` ile YouTube yenileme belirtecini alın (OAuth onay ekranı **In production** olmalı).
3. Settings > Secrets and variables > Actions altına şunları ekleyin:
   `GEMINI_API_KEY`, `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID`, `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`, `IG_USER_ID`, `IG_TOKEN`, `PAGES_URL`.
4. `data/kavramlar.json` içindeki tanımları gözden geçirip genişletin; ardından `araclar/colab_sirala.py` ile Colab'da `data/sira.json` üretin.
5. `uret.py` içindeki `BASLANGIC` tarihini serinin ilk gününe ayarlayın.
6. Actions > "Günlük video üret" > Run workflow ile ilk denemeyi yapın.

## Dosyalar

| Dosya | Görev |
| --- | --- |
| `uret.py` | Günün kavramı, Gemini senaryo + TTS, Pillow kareleri, FFmpeg videosu, Telegram'a onaya gönderme |
| `onay.py` | Telegram tuşlarını okur, onaylananları yayınlar |
| `yayinla.py` | YouTube ve Instagram yükleme |
| `skills/kisa-video-senaristi/SKILL.md` | Senaryo kuralları (Agent Skill) |
| `.github/workflows/` | Günlük üretim (07:00 TR) ve 15 dakikalık onay işleri |

Instagram tokenı 60 günde dolar; ayda bir yenileyin:

```bash
curl "https://graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token&access_token=$IG_TOKEN"
```
