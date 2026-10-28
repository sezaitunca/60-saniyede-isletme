import json, os, requests
from yayinla import youtube_yukle, instagram_yayinla

TG = f"https://api.telegram.org/bot{os.environ['TELEGRAM_TOKEN']}"
SOHBET = os.environ["TELEGRAM_CHAT_ID"]
PAGES = os.environ["PAGES_URL"].rstrip("/")
INSTAGRAM_DILLERI = {"tr", "en"}

def mesaj(metin):
    requests.post(f"{TG}/sendMessage", data={"chat_id": SOHBET, "text": metin}, timeout=60)

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
    dosya = f"/tmp/{gun}_{dil}.mp4"
    with open(dosya, "wb") as f:
        f.write(requests.get(url, timeout=120).content)
    yt = youtube_yukle(dosya, s, dil)
    mesaj(f"YouTube: https://youtube.com/shorts/{yt}")
    if dil in INSTAGRAM_DILLERI:
        instagram_yayinla(url, s)
        mesaj(f"Instagram: {dil.upper()} Reels yayınlandı.")
if guncellemeler:
    requests.get(f"{TG}/getUpdates", params={"offset": guncellemeler[-1]["update_id"] + 1}, timeout=60)
