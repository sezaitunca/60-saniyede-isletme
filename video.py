"""Dikey video: renkli hareketli arka plan, kelime kelime altyazı, sentezlenmiş müzik."""
import math, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from piper import PiperVoice, SynthesisConfig

W, H, FPS, SR = 1080, 1920, 30, 44100
FONT = "fonts/Montserrat.ttf"
SESLER = {"tr": "tr_TR-dfki-medium", "en": "en_US-lessac-medium",
          "de": "de_DE-thorsten-medium", "ru": "ru_RU-irina-medium"}  # Piper sesleri
SERI = {"tr": "60 Saniyede İşletme", "en": "Business in 60 Seconds",
        "de": "Business in 60 Sekunden", "ru": "Бизнес за 60 секунд"}
YORUM = {"tr": "Cevabını yorumlara yaz", "en": "Drop your answer below",
         "de": "Schreib's in die Kommentare", "ru": "Пиши ответ в комментариях"}
TAKIP = {"tr": ("Takip et", "Her gün yeni bir kavram"), "en": ("Follow", "A new concept every day"),
         "de": ("Folgen", "Jeden Tag ein neues Konzept"), "ru": ("Подпишись", "Каждый день новое понятие")}

# (gradyan üst, gradyan alt, ışık 1, ışık 2, vurgu)
PALETLER = [
    ("#2B0A5E", "#C0136F", "#FF6B35", "#00D1FF", "#FFD23F"),
    ("#031B4E", "#0E8F9C", "#FF3D7F", "#7CFF6B", "#FFE14D"),
    ("#3A0CA3", "#F72585", "#4CC9F0", "#FFBE0B", "#FFBE0B"),
    ("#1A1A2E", "#E94560", "#0F9BFF", "#FFC93C", "#FFC93C"),
    ("#0B3D2E", "#11998E", "#F15BB5", "#FEE440", "#FEE440"),
    ("#7F1D1D", "#F97316", "#FACC15", "#38BDF8", "#FDE047"),
]

LEAD, ARA, OUTRO = 0.6, 0.35, 2.2  # saniye: giriş, cümle arası, kapanış

def renk(h, a=255):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) + (a,)

def font(boyut, agirlik):
    f = ImageFont.truetype(FONT, boyut)
    f.set_variation_by_axes([agirlik])
    return f

# --- Ses ---

def seslendir(cumleler, dil):
    """Her cümleyi seslendirir; 44.1 kHz float dizileri döndürür."""
    ses = PiperVoice.load(f"sesler/{SESLER[dil]}.onnx")
    ayar = SynthesisConfig(length_scale=0.92)  # biraz daha enerjik tempo
    parcalar = []
    for c in cumleler:
        parca = [ch.audio_float_array for ch in ses.synthesize(c, syn_config=ayar)]
        x = np.concatenate(parca)
        kaynak = ses.config.sample_rate
        t = np.arange(int(len(x) * SR / kaynak)) * kaynak / SR
        parcalar.append(np.interp(t, np.arange(len(x)), x).astype(np.float32))
    return parcalar

def _nota(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)

def _ekle(iz, ornek, bas):
    i = int(bas * SR)
    if i >= len(iz):
        return
    son = min(len(iz), i + len(ornek))
    iz[i:son] += ornek[:son - i]

def muzik(sure, tohum):
    """Telifsiz, kodla sentezlenen hareketli bir lo-fi pop altlığı."""
    rng = np.random.default_rng(tohum)
    bpm = 104
    vurus = 60 / bpm
    kok = 57 + [0, 2, 5, 7, -2, 3][tohum % 6]
    akorlar = [[0, 4, 7], [7, 11, 14], [9, 12, 16], [5, 9, 12]]  # I–V–vi–IV
    n = int(sure * SR) + SR
    iz = np.zeros(n, np.float32)
    t_vurus = np.arange(int(vurus * SR)) / SR

    kick = np.sin(2 * np.pi * np.cumsum(45 + 90 * np.exp(-t_vurus * 30)) / SR) * np.exp(-t_vurus * 9)
    gurultu = rng.uniform(-1, 1, int(0.2 * SR)).astype(np.float32)
    clap = np.diff(gurultu, prepend=0) * np.exp(-np.arange(len(gurultu)) / SR * 22)
    hat = np.diff(gurultu[: int(0.05 * SR)], prepend=0) * np.exp(-np.arange(int(0.05 * SR)) / SR * 80)

    vurus_sayisi = int(sure / vurus) + 1
    for b in range(vurus_sayisi):
        t0 = b * vurus
        _ekle(iz, 0.55 * kick, t0)
        if b % 2 == 1:
            _ekle(iz, 0.22 * clap, t0)
        _ekle(iz, 0.07 * hat, t0 + vurus / 2)
        if b % 4 == 0:  # her ölçü: pad + bas
            akor = akorlar[(b // 4) % 4]
            olcu = np.arange(int(4 * vurus * SR)) / SR
            zarf = np.minimum(1, olcu / 0.08) * np.exp(-olcu * 0.5)
            pad = np.zeros_like(olcu)
            for aralik in akor:
                f = _nota(kok + aralik)
                for h in range(1, 6):  # yumuşak testere dalgası
                    pad += np.sin(2 * np.pi * f * h * olcu * (1 + 0.002 * h)) / (h * 1.6)
            _ekle(iz, (0.05 * pad * zarf).astype(np.float32), t0)
            fb = _nota(kok + akor[0] - 24)
            bas = (np.sin(2 * np.pi * fb * olcu) + 0.3 * np.sin(4 * np.pi * fb * olcu)) * np.exp(-olcu * 1.2)
            _ekle(iz, (0.3 * bas).astype(np.float32), t0)
            _ekle(iz, (0.3 * bas[: int(2 * vurus * SR)]).astype(np.float32), t0 + 2 * vurus)
        akor = akorlar[(b // 4) % 4]
        for k in range(2):  # sekizlik arpej
            f = _nota(kok + 12 + akor[(b * 2 + k) % 3])
            tt = np.arange(int(vurus / 2 * SR)) / SR
            pluck = (np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(4 * np.pi * f * tt)) * np.exp(-tt * 10)
            _ekle(iz, (0.07 * pluck).astype(np.float32), t0 + k * vurus / 2)
    return iz[: int(sure * SR)]

def whoosh(rng):
    n = int(0.45 * SR)
    t = np.linspace(0, 1, n)
    g = np.diff(rng.uniform(-1, 1, n + 1)).astype(np.float32)
    return g * np.sin(np.pi * t) ** 2 * 0.12

def karisim(sesler, tohum):
    """Ses + müzik + geçiş efektleri; cümle ve kelime zamanlamalarını da döndürür."""
    rng = np.random.default_rng(tohum + 1)
    zamanlar, t = [], LEAD
    for s in sesler:
        zamanlar.append((t, t + len(s) / SR))
        t += len(s) / SR + ARA
    sure = t - ARA + OUTRO
    n = int(sure * SR)
    konusma = np.zeros(n, np.float32)
    for s, (bas, _) in zip(sesler, zamanlar):
        _ekle(konusma, s, bas)
    efekt = np.zeros(n, np.float32)
    for bas, _ in zamanlar:
        _ekle(efekt, whoosh(rng), max(0, bas - 0.3))

    # konuşma varken müziği kıs (ducking)
    aktif = np.zeros(n, np.float32)
    for bas, son in zamanlar:
        aktif[int(bas * SR):int(son * SR)] = 1
    pencere = int(0.15 * SR)
    aktif = np.convolve(aktif, np.ones(pencere) / pencere, mode="same")
    kazanc = 0.75 - 0.5 * aktif
    m = muzik(sure, tohum)
    m = m / (np.abs(m).max() + 1e-9)
    fade = np.ones(n, np.float32)
    fade[: int(0.3 * SR)] = np.linspace(0, 1, int(0.3 * SR))
    fade[-int(1.2 * SR):] = np.linspace(1, 0, int(1.2 * SR))
    mix = konusma * 1.0 + m * kazanc * 0.32 * fade + efekt
    mix = np.tanh(mix * 1.1) * 0.95
    return mix, zamanlar, sure

def wav_yaz(x, dosya):
    veri = (np.clip(x, -1, 1) * 32767).astype("<i2")
    stereo = np.repeat(veri[:, None], 2, axis=1)
    with wave.open(dosya, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(stereo.tobytes())

# --- Görüntü ---

def arka_plan_hazirla(palet):
    w, h = W // 2, H // 2
    y = np.linspace(0, 1, h)[:, None, None]
    ust, alt = np.array(renk(palet[0])[:3]), np.array(renk(palet[1])[:3])
    grad = (ust * (1 - y) + alt * y).repeat(w, axis=1).astype(np.uint8)
    taban = Image.fromarray(grad).convert("RGBA")
    isiklar = []
    for i, r in enumerate((260, 210, 170)):
        pay = 200  # bulanıklık kenarda kesilmesin
        im = Image.new("RGBA", (r * 2 + 2 * pay, r * 2 + 2 * pay), (0, 0, 0, 0))
        ImageDraw.Draw(im).ellipse([pay, pay, pay + 2 * r, pay + 2 * r],
                                   fill=renk(palet[2 + i % 2], 150 if i < 2 else 90))
        isiklar.append(im.filter(ImageFilter.GaussianBlur(60)))
    return taban, isiklar

def arka_plan(taban, isiklar, t):
    im = taban.copy()
    w, h = taban.size
    yollar = [(0.25, 0.30, 0.31, 0.23), (0.75, 0.70, 0.23, 0.37), (0.5, 0.5, 0.41, 0.19)]
    for isik, (cx, cy, fx, fy) in zip(isiklar, yollar):
        x = int(w * (cx + 0.28 * math.sin(t * fx * 2))) - isik.width // 2
        y = int(h * (cy + 0.18 * math.cos(t * fy * 2))) - isik.height // 2
        im.paste(isik, (x, y), isik)
    return im.resize((W, H), Image.BILINEAR)

def satirlara_bol(kelimeler, f, en):
    satirlar, x = [[]], 0
    bosluk = f.getlength(" ")
    for k in kelimeler:
        g = f.getlength(k)
        if satirlar[-1] and x + g > en:
            satirlar.append([]); x = 0
        satirlar[-1].append(k)
        x += g + bosluk
    return satirlar

def cumle_duzeni(cumle):
    """Kelimelerin ekrandaki konumlarını hesaplar."""
    kelimeler = cumle.split()
    for boyut in (96, 86, 76, 68, 60, 52):
        f = font(boyut, 900)
        satirlar = satirlara_bol(kelimeler, f, W - 180)
        if len(satirlar) <= 5 and max(f.getlength(k) for k in kelimeler) <= W - 180:
            break
    satir_h = int(boyut * 1.32)
    y0 = 1010 - len(satirlar) * satir_h // 2
    konum, bosluk = [], f.getlength(" ")
    for i, satir in enumerate(satirlar):
        genislik = sum(f.getlength(k) for k in satir) + bosluk * (len(satir) - 1)
        x = (W - genislik) / 2
        for k in satir:
            konum.append((k, int(x), y0 + i * satir_h))
            x += f.getlength(k) + bosluk
    return f, konum

def kelime_zamanlari(ses, bas, kelimeler):
    """Kelimeleri sesin konuşulan kısmına uzunluklarına göre dağıtır."""
    aktif = np.where(np.abs(ses) > 0.02)[0]
    s0, s1 = (aktif[0], aktif[-1]) if len(aktif) else (0, len(ses))
    agirlik = np.array([len(k) + 2 for k in kelimeler], float)
    sinir = np.concatenate([[0], np.cumsum(agirlik) / agirlik.sum()])
    return [bas + (s0 + (s1 - s0) * sinir[i]) / SR for i in range(len(kelimeler))]

def vurgu_mu(kelime, vurgular):
    """Kelime, vurgulardan biriyle aynı köke sahipse (ilk 5 harf) True."""
    sade = kelime.strip(".,!?:;«»\"'—-").lower()
    for v in (v.lower() for v in vurgular):
        if sade == v or (min(len(sade), len(v)) >= 4 and sade[:5] == v[:5]):
            return True
    return False

def sabit_katman(seri, baslik, palet):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f = font(40, 700)
    g = f.getlength(seri)
    d.rounded_rectangle([70, 120, 70 + g + 90, 186], 33, fill=(0, 0, 0, 90))
    d.ellipse([92, 141, 116, 165], fill=renk(palet[4]))
    d.text((132, 153), seri, font=f, fill="white", anchor="lm")
    fb = font(66, 850)
    y = 240
    for satir in satirlara_bol(baslik.split(), fb, W - 160):
        metin = " ".join(satir)
        d.text((80, y + 5), metin, font=fb, fill=(0, 0, 0, 80))
        d.text((80, y), metin, font=fb, fill="white")
        y += 84
    return im

def kare_ciz(t, palet, zamanlar, duzenler, kz, vurgular, dil, sure):
    d_im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(d_im)
    n = len(zamanlar)
    vurgu = renk(palet[4])
    # üstte hikâye tarzı ilerleme çubukları
    seg = (W - 140 - (n - 1) * 12) / n
    for i, (bas, son) in enumerate(zamanlar):
        x0 = 70 + i * (seg + 12)
        d.rounded_rectangle([x0, 60, x0 + seg, 70], 5, fill=(255, 255, 255, 70))
        oran = min(1, max(0, (t - bas) / (son - bas + ARA)))
        if oran > 0:
            d.rounded_rectangle([x0, 60, x0 + seg * oran, 70], 5, fill=(255, 255, 255, 255))

    # şu anki cümle
    # yeni cümlenin ilk kelimesi gelene kadar önceki cümle ekranda kalır
    aktif = max([i for i, z in enumerate(kz) if t >= z[0]] or [0])
    if t < sure - OUTRO + 0.1:
        f, konum = duzenler[aktif]
        zaman = kz[aktif]
        for j, (k, x, y) in enumerate(konum):
            dt = t - zaman[j]
            if dt < 0:
                continue
            p = min(1, dt / 0.14)
            yy = y + int(28 * (1 - p) ** 2)
            bitis = zaman[j + 1] if j + 1 < len(zaman) else zamanlar[aktif][1]
            if t < bitis:  # şu an söylenen kelime
                g = f.getlength(k)
                d.rounded_rectangle([x - 16, yy - 8, x + g + 16, yy + f.size * 1.18], 22, fill=vurgu)
                d.text((x, yy), k, font=f, fill=(20, 20, 30, 255))
            else:
                a = int(255 * p)
                d.text((x + 4, yy + 7), k, font=f, fill=(0, 0, 0, int(90 * p)))
                d.text((x, yy), k, font=f, fill=vurgu[:3] + (a,) if vurgu_mu(k, vurgular) else (255, 255, 255, a))
        if aktif == n - 1 and t > zamanlar[-1][0] + 0.5:  # kapanış sorusu: yorum çağrısı
            fy = font(46, 700)
            metin = YORUM[dil]
            g = fy.getlength(metin)
            y = 1560 + int(8 * math.sin(t * 6))
            d.rounded_rectangle([(W - g) / 2 - 40, y, (W + g) / 2 + 40, y + 90], 45, fill=(255, 255, 255, 235))
            d.text((W / 2, y + 45), metin, font=fy, fill=renk(palet[0]), anchor="mm")
            d.polygon([(W / 2 - 22, y + 112), (W / 2 + 22, y + 112), (W / 2, y + 140)], fill=(255, 255, 255, 235))
    else:  # kapanış ekranı
        p = min(1, (t - (sure - OUTRO)) / 0.3)
        b1, b2 = TAKIP[dil]
        f1, f2 = font(120, 900), font(52, 600)
        y = 900 + int(60 * (1 - p) ** 2)
        g = f1.getlength(b1)
        d.rounded_rectangle([(W - g) / 2 - 60, y - 95, (W + g) / 2 + 60, y + 95], 95, fill=vurgu[:3] + (int(255 * p),))
        d.text((W / 2, y), b1, font=f1, fill=(20, 20, 30, int(255 * p)), anchor="mm")
        d.text((W / 2, y + 170), b2, font=f2, fill=(255, 255, 255, int(255 * p)), anchor="mm")
    return d_im

def video_yap(s, dil, gun_no, klasor):
    palet = PALETLER[gun_no % len(PALETLER)]
    sesler = seslendir(s["cumleler"], dil)
    mix, zamanlar, sure = karisim(sesler, gun_no)
    wav = f"{klasor}/{dil}_mix.wav"
    wav_yaz(mix, wav)
    duzenler = [cumle_duzeni(c) for c in s["cumleler"]]
    kz = [kelime_zamanlari(ses, bas, [k for k, _, _ in konum])
          for ses, (bas, _), (_, konum) in zip(sesler, zamanlar, duzenler)]
    vurgular = s.get("vurgular", [])
    sabit = sabit_katman(f"{SERI[dil]} · {gun_no}", s["baslik"], palet)
    taban, isiklar = arka_plan_hazirla(palet)
    cikti = f"{klasor}/{dil}.mp4"
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav,
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
         "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "160k", "-ar", str(SR), "-shortest",
         "-movflags", "+faststart", cikti], stdin=subprocess.PIPE)
    for i in range(int(sure * FPS)):
        t = i / FPS
        kare = arka_plan(taban, isiklar, t)
        giris = min(1, t / 0.4)  # başlık girişte aşağıdan kayar
        kare.alpha_composite(sabit, (0, int(40 * (1 - giris) ** 2)))
        kare.alpha_composite(kare_ciz(t, palet, zamanlar, duzenler, kz, vurgular, dil, sure))
        ff.stdin.write(kare.convert("RGB").tobytes())
    ff.stdin.close()
    if ff.wait() != 0:
        raise RuntimeError(f"ffmpeg hata verdi: {dil}")
    return cikti
