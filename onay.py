import json, os, requests
from yayinla import youtube_yukle, instagram_yayinla

TG = f"https://api.telegram.org/bot{os.environ['TELEGRAM_TOKEN']}"
SOHBET = os.environ["TELEGRAM_CHAT_ID"]
PAGES = os.environ["PAGES_URL"].rstrip("/")
INSTAGRAM_DILLERI = {"tr", "en"}
# Bilgileri girilmemiş platform atlanır; yalnızca bağlı olanlara yayın yapılır
YOUTUBE_BAGLI = bool(os.environ.get("YT_REFRESH_TOKEN"))
INSTAGRAM_BAGLI = bool(os.environ.get("IG_TOKEN") and os.environ.get("IG_USER_ID"))

def mesaj(metin):
    requests.post(f"{TG}/sendMessage", data={"chat_id": SOHBET, "text": metin}, timeout=60)

def dene(ad, is_):
    """Bir platformdaki hata diğerlerini durdurmasın; sonucu Telegram'a bildir."""
    try:
        mesaj(f"{ad}: {is_()}")
    except Exception as e:
        mesaj(f"{ad}: yayınlanamadı ({e})")

if not (YOUTUBE_BAGLI or INSTAGRAM_BAGLI):
    print("Bağlı yayın hesabı yok; onaylar hesap bağlanana kadar bekletiliyor.")
    raise SystemExit(0)

guncellemeler = requests.get(f"{TG}/getUpdates", timeout=60,
    params={"allowed_updates": json.dumps(["callback_query"])}).json()["result"]
for u in guncellemeler:
    cq = u.get("callback_query")
    if not cq or str(cq["from"]["id"]) != SOHBET:
        continue
    karar, gun, dil = cq["data"].split("|")
    requests.post(f"{TG}/answerCallbackQuery", data={"callback_query_id": cq["id"], "text": "Alındı"})
    if karar != "ok":
        mesaj(f"{gun} {dil.upper()} reddedildi.")
        continue
    s = requests.get(f"{PAGES}/{gun}/meta.json", timeout=60).json()[dil]
    url = f"{PAGES}/{gun}/{dil}.mp4"
    if YOUTUBE_BAGLI:
        dosya = f"/tmp/{gun}_{dil}.mp4"
        with open(dosya, "wb") as f:
            f.write(requests.get(url, timeout=120).content)
        dene("YouTube", lambda: f"https://youtube.com/shorts/{youtube_yukle(dosya, s, dil)}")
    if INSTAGRAM_BAGLI and dil in INSTAGRAM_DILLERI:
        dene("Instagram Reels", lambda: instagram_yayinla(url, s, "REELS") or "yayınlandı")
        dene("Instagram Story", lambda: instagram_yayinla(url, s, "STORIES") or "yayınlandı")
# Hatalar Telegram'a bildirildiği için onaylar her durumda işlenmiş sayılır (çift yükleme olmaz)
if guncellemeler:
    requests.get(f"{TG}/getUpdates", params={"offset": guncellemeler[-1]["update_id"] + 1}, timeout=60)
