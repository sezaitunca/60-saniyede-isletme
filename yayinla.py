import os, time, requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def youtube_yukle(dosya, s, dil):
    creds = Credentials(None, refresh_token=os.environ["YT_REFRESH_TOKEN"],
                        token_uri="https://oauth2.googleapis.com/token",
                        client_id=os.environ["YT_CLIENT_ID"],
                        client_secret=os.environ["YT_CLIENT_SECRET"],
                        scopes=["https://www.googleapis.com/auth/youtube.upload"])
    yt = build("youtube", "v3", credentials=creds)
    govde = {
        "snippet": {"title": s["baslik"],
                    "description": s["aciklama"] + "\n\n" + " ".join(s["etiketler"]),
                    "categoryId": "27",  # Eğitim
                    "defaultLanguage": dil, "defaultAudioLanguage": dil},
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False,
                   "containsSyntheticMedia": True},
    }
    istek = yt.videos().insert(part="snippet,status", body=govde,
        media_body=MediaFileUpload(dosya, mimetype="video/mp4", resumable=True))
    return istek.execute()["id"]

IG = "https://graph.instagram.com"

def instagram_yayinla(video_url, s, tur="REELS"):
    """tur: "REELS" (akışta da paylaşılır) veya "STORIES" (24 saatlik hikâye)."""
    tok, kim = os.environ["IG_TOKEN"], os.environ["IG_USER_ID"]
    veri = {"media_type": tur, "video_url": video_url, "access_token": tok}
    if tur == "REELS":
        veri.update(share_to_feed="true",
                    caption=s["aciklama"] + "\n\n" + " ".join(s["etiketler"]))
    kap = requests.post(f"{IG}/{kim}/media", timeout=60, data=veri).json()
    if "id" not in kap:
        raise RuntimeError(f"Instagram {tur} kabı oluşturulamadı: {kap}")
    for _ in range(5):  # dakikada bir, en fazla 5 dakika kontrol
        time.sleep(60)
        durum = requests.get(f"{IG}/{kap['id']}", timeout=60,
                             params={"fields": "status_code", "access_token": tok}).json()
        if durum.get("status_code") == "FINISHED":
            break
    requests.post(f"{IG}/{kim}/media_publish", timeout=60,
                  data={"creation_id": kap["id"], "access_token": tok}).raise_for_status()
