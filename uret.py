import json, os, re, datetime
import requests
import anthropic
from video import video_yap

DILLER = {"tr": "Türkçe"}  # yalnızca Türkçe; diğerleri: "en": "English", "de": "Deutsch", "ru": "Русский"
BASLANGIC = datetime.date(2026, 10, 28)  # serinin ilk günü; kendinize göre değiştirin
client = anthropic.Anthropic()  # ANTHROPIC_API_KEY ortam değişkenini okur
SKILL = open("skills/kisa-video-senaristi/SKILL.md", encoding="utf-8").read()

# --- Adım 3: günün kavramı ve senaryo ---

def bugunun_kavrami():
    kavramlar = {k["id"]: k for k in json.load(open("data/kavramlar.json", encoding="utf-8"))}
    sira = json.load(open("data/sira.json"))
    gun_no = (datetime.date.today() - BASLANGIC).days
    return kavramlar[sira[gun_no % len(sira)]], gun_no + 1

def json_al(metin):
    return json.loads(re.sub(r"^```(json)?|```$", "", metin.strip(), flags=re.M))

def senaryo(kavram, dil):
    istem = (f"Kavram: {kavram['ad']}\n"
             f"Doğrulanmış tanım: {kavram['tanim']}\nHedef dil: {DILLER[dil]}")
    yanit = client.beta.messages.create(
        model="claude-opus-5-5",
        max_tokens=16000,
        output_config={"effort": "medium"},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",  # reddedilen istek sunucu tarafında başka modelle yeniden denenir
        system=SKILL,
        messages=[{"role": "user", "content": istem}],
    )
    if yanit.stop_reason == "refusal":
        raise RuntimeError(f"Claude senaryoyu reddetti: {kavram['ad']} / {dil}")
    return json_al(next(b.text for b in yanit.content if b.type == "text"))

# --- Adım 4–5: seslendirme, müzik ve 9:16 video: video.py ---

# --- Adım 6: Telegram ile onay ---

TG = f"https://api.telegram.org/bot{os.environ['TELEGRAM_TOKEN']}"
SOHBET = os.environ["TELEGRAM_CHAT_ID"]

def onaya_gonder(dosya, gun, dil, baslik):
    tuslar = {"inline_keyboard": [[
        {"text": "Onayla", "callback_data": f"ok|{gun}|{dil}"},
        {"text": "Reddet", "callback_data": f"no|{gun}|{dil}"}]]}
    with open(dosya, "rb") as f:
        requests.post(f"{TG}/sendVideo", files={"video": f}, data={
            "chat_id": SOHBET, "caption": f"{gun} · {dil.upper()} · {baslik}",
            "reply_markup": json.dumps(tuslar)}, timeout=120).raise_for_status()

def onceki_videolari_koru():
    """Pages her yayında baştan kurulur; onay bekleyen dünkü ve bugünkü videoları geri indirir."""
    pages = os.environ.get("PAGES_URL", "").rstrip("/")
    if not pages:
        return []
    sinir = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    try:
        klasorler = requests.get(f"{pages}/index.json", timeout=60).json()
    except Exception:  # liste yoksa en azından dünün ve bugünün günlük klasörleri
        klasorler = [sinir, datetime.date.today().isoformat()]
    korunan = []
    for ad in klasorler:
        if ad[:10] < sinir:
            continue
        r = requests.get(f"{pages}/{ad}/meta.json", timeout=60)
        if r.status_code != 200:
            continue
        os.makedirs(f"cikti/{ad}", exist_ok=True)
        with open(f"cikti/{ad}/meta.json", "wb") as f:
            f.write(r.content)
        for dil in r.json():
            with open(f"cikti/{ad}/{dil}.mp4", "wb") as f:
                f.write(requests.get(f"{pages}/{ad}/{dil}.mp4", timeout=120).content)
        korunan.append(ad)
    return korunan

if __name__ == "__main__":
    korunan = onceki_videolari_koru()
    kavram, gun_no = bugunun_kavrami()
    gun = datetime.date.today().isoformat()
    if os.environ.get("KAVRAM_ID"):  # elle istenen kavram: ayrı klasöre, günlük videoyu ezmeden
        kavram = next(k for k in json.load(open("data/kavramlar.json", encoding="utf-8"))
                      if k["id"] == int(os.environ["KAVRAM_ID"]))
        gun = f"{gun}-k{kavram['id']}"
    klasor = f"cikti/{gun}"
    os.makedirs(klasor, exist_ok=True)
    meta = {}
    for dil in DILLER:
        s = senaryo(kavram, dil)
        meta[dil] = s
        onaya_gonder(video_yap(s, dil, gun_no, klasor), gun, dil, s["baslik"])
    with open(f"{klasor}/meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False)
    for ad in os.listdir(klasor):  # yalnızca dil videoları ve meta.json kalır
        if "_" in ad or not (ad.endswith(".mp4") or ad == "meta.json"):
            os.remove(os.path.join(klasor, ad))
    with open("cikti/index.json", "w") as f:
        json.dump(sorted(set(korunan) | {gun}), f)
