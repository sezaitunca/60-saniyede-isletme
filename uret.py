import json, os, re, datetime, subprocess, wave
import requests
import anthropic
from piper import PiperVoice
from PIL import Image, ImageDraw, ImageFont

DILLER = {"tr": "Türkçe", "en": "English", "de": "Deutsch", "ru": "Русский"}
BASLANGIC = datetime.date(2026, 11, 2)  # serinin ilk günü; kendinize göre değiştirin
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

# --- Adım 4–5: seslendirme ve 9:16 video ---

SESLER = {"tr": "tr_TR-dfki-medium", "en": "en_US-lessac-medium",
          "de": "de_DE-thorsten-medium", "ru": "ru_RU-irina-medium"}  # Piper sesleri
W, H = 1080, 1920
# Yerelde denerken FONT ortam değişkeniyle başka bir yazı tipi verilebilir
FONT = os.environ.get("FONT", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
SERI = {"tr": "60 Saniyede İşletme", "en": "Business in 60 Seconds",
        "de": "Business in 60 Sekunden", "ru": "Бизнес за 60 секунд"}

def seslendir(metin, dil, dosya):
    ses = PiperVoice.load(f"sesler/{SESLER[dil]}.onnx")
    with wave.open(dosya, "wb") as w:
        ses.synthesize_wav(metin, w)

def sar(d, metin, font, en=W - 160):  # satırları piksel genişliğine göre böler
    satirlar = []
    for kelime in metin.split():
        if satirlar and d.textlength(f"{satirlar[-1]} {kelime}", font=font) <= en:
            satirlar[-1] += f" {kelime}"
        else:
            satirlar.append(kelime)
    return satirlar

def kare(seri, baslik, cumle, i, n, dosya):
    img = Image.new("RGB", (W, H), (18, 24, 38))
    d = ImageDraw.Draw(img)
    kucuk, orta, buyuk = (ImageFont.truetype(FONT, s) for s in (44, 64, 76))
    d.text((80, 160), seri, font=kucuk, fill=(255, 196, 0))
    y = 240
    for satir in sar(d, baslik, orta):
        d.text((80, y), satir, font=orta, fill="white"); y += 80
    y = 780
    for satir in sar(d, cumle, buyuk):
        d.text((80, y), satir, font=buyuk, fill="white"); y += 100
    d.rectangle([80, 1720, 80 + (W - 160) * (i + 1) // n, 1736], fill=(255, 196, 0))
    img.save(dosya)

def video_yap(s, dil, gun_no, klasor):
    seri = f"{SERI[dil]} · {gun_no}"
    parcalar = []
    for i, cumle in enumerate(s["cumleler"]):
        png, wav, mp4 = (f"{klasor}/{dil}_{i}.{u}" for u in ("png", "wav", "mp4"))
        kare(seri, s["baslik"], cumle, i, len(s["cumleler"]), png)
        seslendir(cumle, dil, wav)
        subprocess.run(["ffmpeg", "-y", "-loop", "1", "-i", png, "-i", wav,
                        "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p",
                        "-r", "30", "-c:a", "aac", "-ar", "44100", "-b:a", "128k",
                        "-shortest", mp4], check=True)
        parcalar.append(mp4)
    liste = f"{klasor}/{dil}_liste.txt"
    with open(liste, "w") as f:
        f.writelines(f"file '{os.path.basename(p)}'\n" for p in parcalar)
    cikti = f"{klasor}/{dil}.mp4"
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", liste,
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                    "-movflags", "+faststart", cikti], check=True)
    return cikti

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

if __name__ == "__main__":
    kavram, gun_no = bugunun_kavrami()
    gun = datetime.date.today().isoformat()
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
