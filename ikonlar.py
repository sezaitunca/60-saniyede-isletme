"""Kodla çizilen, sticker görünümlü ikonlar (telifsiz)."""
import math
from PIL import Image, ImageDraw, ImageFilter, ImageFont

S = 400  # çizim tuvali
KONTUR = (27, 27, 47, 255)
K = 10  # kontur kalınlığı

def _tuval():
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)

def kahve():
    im, d = _tuval()
    for x in (130, 190, 250):  # dalgalı buhar
        d.line([(x + 12 * math.sin(y / 18), y) for y in range(40, 145, 5)],
               fill=(255, 255, 255, 235), width=12, joint="curve")
    d.ellipse([70, 310, 330, 360], fill="#E8E8F0", outline=KONTUR, width=K)
    d.ellipse([250, 200, 330, 290], outline=KONTUR, width=26)
    d.ellipse([250, 200, 330, 290], outline="#FF5A5F", width=12)
    d.rounded_rectangle([100, 170, 280, 330], 40, fill="#FF5A5F", outline=KONTUR, width=K)
    d.rectangle([110, 230, 270, 260], fill="white")
    d.ellipse([100, 150, 280, 195], fill="#6B3E26", outline=KONTUR, width=K)
    return im

def para():
    im, d = _tuval()
    for y in (300, 265, 230):
        d.ellipse([60, y, 220, y + 55], fill="#FFB300", outline=KONTUR, width=K)
    d.ellipse([150, 90, 350, 290], fill="#FFD54F", outline=KONTUR, width=K)
    d.ellipse([180, 120, 320, 260], outline="#FFB300", width=10)
    f = ImageFont.truetype("fonts/Montserrat.ttf", 110)
    f.set_variation_by_axes([900])
    d.text((250, 192), "₺" if f.getbbox("₺")[2] > 10 else "$", font=f, fill="#E65100", anchor="mm")
    return im

def _cubuklar(d, yukseklikler, renkler):
    for i, (h, r) in enumerate(zip(yukseklikler, renkler)):
        x = 70 + i * 70
        d.rounded_rectangle([x, 340 - h, x + 52, 340], 10, fill=r, outline=KONTUR, width=K)
    d.line([50, 345, 350, 345], fill=KONTUR, width=K)

def _ok(d, noktalar, renk):
    d.line(noktalar, fill=KONTUR, width=30, joint="curve")
    d.line(noktalar, fill=renk, width=16, joint="curve")
    (x1, y1), (x2, y2) = noktalar[-2], noktalar[-1]
    a = math.atan2(y2 - y1, x2 - x1)
    uc = [(x2 + 30 * math.cos(a), y2 + 30 * math.sin(a)),
          (x2 + 34 * math.cos(a + 2.3), y2 + 34 * math.sin(a + 2.3)),
          (x2 + 34 * math.cos(a - 2.3), y2 + 34 * math.sin(a - 2.3))]
    d.polygon(uc, fill=renk, outline=KONTUR, width=K)

def grafik_artis():
    im, d = _tuval()
    _cubuklar(d, [80, 130, 180, 240], ["#4FC3F7", "#29B6F6", "#66BB6A", "#43A047"])
    _ok(d, [(70, 230), (150, 180), (210, 200), (320, 70)], "#FF5252")
    return im

def grafik_dusus():
    im, d = _tuval()
    _cubuklar(d, [240, 180, 130, 70], ["#FFB74D", "#FF8A65", "#EF5350", "#E53935"])
    _ok(d, [(70, 60), (160, 130), (220, 110), (320, 230)], "#7E57C2")
    return im

def soru():
    im, d = _tuval()
    d.polygon([(110, 300), (90, 370), (180, 315)], fill="#7C4DFF", outline=KONTUR, width=K)
    d.ellipse([50, 40, 350, 330], fill="#7C4DFF", outline=KONTUR, width=K)
    f = ImageFont.truetype("fonts/Montserrat.ttf", 220)
    f.set_variation_by_axes([900])
    d.text((200, 185), "?", font=f, fill="white", anchor="mm", stroke_width=6, stroke_fill=KONTUR)
    return im

def ampul():
    im, d = _tuval()
    for a in range(-150, -20, 32):  # ışınlar
        r = math.radians(a)
        d.line([200 + 150 * math.cos(r), 160 + 150 * math.sin(r),
                200 + 190 * math.cos(r), 160 + 190 * math.sin(r)], fill="#FFEB3B", width=14)
    d.rounded_rectangle([150, 250, 250, 330], 14, fill="#B0BEC5", outline=KONTUR, width=K)
    d.line([155, 280, 245, 280], fill=KONTUR, width=8)
    d.line([155, 305, 245, 305], fill=KONTUR, width=8)
    d.ellipse([90, 60, 310, 280], fill="#FFEE58", outline=KONTUR, width=K)
    d.arc([130, 100, 230, 200], 180, 260, fill="white", width=14)
    return im

def saat():
    im, d = _tuval()
    d.ellipse([50, 50, 350, 350], fill="#FF7043", outline=KONTUR, width=K)
    d.ellipse([85, 85, 315, 315], fill="white", outline=KONTUR, width=6)
    for i in range(12):
        a = math.radians(i * 30)
        d.line([200 + 95 * math.cos(a), 200 + 95 * math.sin(a),
                200 + 110 * math.cos(a), 200 + 110 * math.sin(a)], fill=KONTUR, width=8)
    d.line([200, 200, 200, 115], fill=KONTUR, width=14)
    d.line([200, 200, 265, 230], fill="#FF7043", width=12)
    d.ellipse([186, 186, 214, 214], fill=KONTUR)
    return im

def alisveris():
    im, d = _tuval()
    d.arc([140, 50, 260, 190], 180, 360, fill=KONTUR, width=22)
    d.polygon([(90, 130), (310, 130), (335, 350), (65, 350)], fill="#EC407A", outline=KONTUR, width=K)
    d.ellipse([130, 160, 150, 180], fill=KONTUR)
    d.ellipse([250, 160, 270, 180], fill=KONTUR)
    d.polygon([(90, 130), (310, 130), (313, 160), (87, 160)], fill="#F48FB1")
    return im

def kitap():
    im, d = _tuval()
    d.polygon([(40, 110), (200, 140), (200, 340), (40, 310)], fill="#1E88E5", outline=KONTUR, width=K)
    d.polygon([(360, 110), (200, 140), (200, 340), (360, 310)], fill="#1565C0", outline=KONTUR, width=K)
    d.polygon([(60, 95), (200, 125), (200, 320), (60, 290)], fill="white", outline=KONTUR, width=K)
    d.polygon([(340, 95), (200, 125), (200, 320), (340, 290)], fill="#F5F5F5", outline=KONTUR, width=K)
    for y in (160, 195, 230):
        d.line([85, y - 25, 175, y - 5], fill="#90A4AE", width=7)
        d.line([225, y - 5, 315, y - 25], fill="#90A4AE", width=7)
    return im

def hedef():
    im, d = _tuval()
    for r, c in ((160, "#E53935"), (120, "white"), (80, "#E53935"), (40, "white")):
        d.ellipse([200 - r, 210 - r, 200 + r, 210 + r], fill=c, outline=KONTUR, width=K)
    d.line([200, 210, 330, 80], fill=KONTUR, width=22)
    d.line([200, 210, 330, 80], fill="#FFCA28", width=10)
    d.polygon([(330, 80), (300, 60), (345, 40), (370, 50), (360, 95), (340, 110)], fill="#29B6F6", outline=KONTUR, width=8)
    return im

def terazi():
    im, d = _tuval()
    d.rounded_rectangle([120, 330, 280, 360], 10, fill="#FFB300", outline=KONTUR, width=K)
    d.rectangle([188, 90, 212, 335], fill="#FFB300", outline=KONTUR, width=8)
    d.line([60, 110, 340, 110], fill=KONTUR, width=22)
    d.line([60, 110, 340, 110], fill="#FFD54F", width=10)
    for x in (80, 320):
        d.line([x, 110, x - 45, 220], fill=KONTUR, width=6)
        d.line([x, 110, x + 45, 220], fill=KONTUR, width=6)
        d.chord([x - 65, 170, x + 65, 270], 0, 180, fill="#FFD54F", outline=KONTUR, width=K)
    d.ellipse([180, 70, 220, 110], fill="#FFB300", outline=KONTUR, width=8)
    return im

def fabrika():
    im, d = _tuval()
    for i, r in enumerate((24, 32, 40)):
        d.ellipse([270 + i * 18 - r, 80 - i * 30 - r, 270 + i * 18 + r, 80 - i * 30 + r], fill=(236, 239, 241, 230))
    d.rectangle([250, 90, 295, 200], fill="#8D6E63", outline=KONTUR, width=K)
    d.polygon([(50, 350), (50, 190), (130, 240), (130, 190), (210, 240), (210, 190), (350, 190), (350, 350)],
              fill="#26A69A", outline=KONTUR, width=K)
    for x in (80, 160, 240):
        d.rounded_rectangle([x, 270, x + 50, 320], 8, fill="#FFF59D", outline=KONTUR, width=7)
    return im

def insanlar():
    im, d = _tuval()
    for x, y, r, c in ((110, 170, 50, "#42A5F5"), (290, 170, 50, "#AB47BC"), (200, 140, 60, "#FF7043")):
        d.chord([x - r * 1.7, y + r * 1.0, x + r * 1.7, y + r * 4.2], 180, 360, fill=c, outline=KONTUR, width=K)
        d.ellipse([x - r, y - r, x + r, y + r], fill="#FFCC80", outline=KONTUR, width=K)
    return im

def roket():
    im, d = _tuval()
    d.polygon([(170, 300), (200, 390), (230, 300)], fill="#FF9800")
    d.polygon([(185, 300), (200, 360), (215, 300)], fill="#FFEB3B")
    d.polygon([(140, 230), (90, 310), (150, 300)], fill="#E53935", outline=KONTUR, width=K)
    d.polygon([(260, 230), (310, 310), (250, 300)], fill="#E53935", outline=KONTUR, width=K)
    d.rounded_rectangle([140, 90, 260, 310], 60, fill="#ECEFF1", outline=KONTUR, width=K)
    d.chord([140, 30, 260, 170], 180, 360, fill="#E53935", outline=KONTUR, width=K)
    d.ellipse([170, 150, 230, 210], fill="#29B6F6", outline=KONTUR, width=K)
    return im

def kamyon():
    im, d = _tuval()
    d.rounded_rectangle([30, 120, 250, 290], 14, fill="#FFA726", outline=KONTUR, width=K)
    d.polygon([(250, 170), (320, 170), (370, 230), (370, 290), (250, 290)], fill="#42A5F5", outline=KONTUR, width=K)
    d.polygon([(270, 185), (315, 185), (350, 228), (270, 228)], fill="#E1F5FE", outline=KONTUR, width=7)
    for x in (90, 300):
        d.ellipse([x - 38, 255, x + 38, 331], fill="#37474F", outline=KONTUR, width=K)
        d.ellipse([x - 14, 279, x + 14, 307], fill="#CFD8DC")
    return im

def kalp():
    im, d = _tuval()
    pts = []
    for i in range(80):
        t = 2 * math.pi * i / 80
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((200 + x * 10.5, 190 - y * 10.5))
    d.polygon(pts, fill="#FF1744", outline=KONTUR, width=K)
    d.arc([110, 110, 190, 190], 190, 260, fill="white", width=14)
    return im

def cuzdan():
    im, d = _tuval()
    d.ellipse([230, 50, 330, 150], fill="#FFD54F", outline=KONTUR, width=K)
    d.rounded_rectangle([40, 120, 360, 340], 30, fill="#8D6E63", outline=KONTUR, width=K)
    d.rounded_rectangle([230, 190, 370, 270], 20, fill="#A1887F", outline=KONTUR, width=K)
    d.ellipse([260, 215, 290, 245], fill="#FFD54F", outline=KONTUR, width=6)
    return im

IKONLAR = {f.__name__: f for f in (kahve, para, grafik_artis, grafik_dusus, soru, ampul, saat, alisveris,
                                   kitap, hedef, terazi, fabrika, insanlar, roket, kamyon, kalp, cuzdan)}

def sticker(ad):
    """İkonu beyaz kenarlı, gölgeli sticker olarak döndürür (S+80 kare)."""
    ikon = IKONLAR.get(ad, soru)()
    p = 40
    tam = Image.new("RGBA", (S + 2 * p, S + 2 * p), (0, 0, 0, 0))
    tam.paste(ikon, (p, p), ikon)
    alfa = tam.split()[3].point(lambda v: 255 if v > 20 else 0)
    kenar = alfa.filter(ImageFilter.MaxFilter(29))
    golge = Image.new("RGBA", tam.size, (0, 0, 0, 0))
    golge.putalpha(kenar.point(lambda v: v * 90 // 255))
    golge = golge.filter(ImageFilter.GaussianBlur(10))
    sonuc = Image.new("RGBA", tam.size, (0, 0, 0, 0))
    sonuc.alpha_composite(golge, (0, 14))
    beyaz = Image.new("RGBA", tam.size, (255, 255, 255, 0))
    beyaz.putalpha(kenar)
    sonuc.alpha_composite(beyaz)
    sonuc.alpha_composite(tam)
    return sonuc
