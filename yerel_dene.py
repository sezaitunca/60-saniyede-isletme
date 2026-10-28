"""Yerelde deneme videosu üretir; Telegram'a göndermez, yayınlamaz.

Kullanım:  .venv/bin/python yerel_dene.py [kavram_numarası]
Numara verilmezse günün kavramı kullanılır. Video deneme/tr.mp4 olarak kaydedilir ve açılır.
"""
import json, os, subprocess, sys

for satir in open(".env", encoding="utf-8"):  # anahtarları .env dosyasından oku
    if "=" in satir and not satir.startswith("#"):
        ad, deger = satir.strip().split("=", 1)
        os.environ.setdefault(ad, deger)
os.environ["PATH"] = os.path.dirname(sys.executable) + os.pathsep + os.environ["PATH"]  # .venv içindeki ffmpeg

import uret

kavram, gun_no = uret.bugunun_kavrami()
if len(sys.argv) > 1:
    kavram = next(k for k in json.load(open("data/kavramlar.json", encoding="utf-8"))
                  if k["id"] == int(sys.argv[1]))
sabit = f"data/senaryolar/{kavram['id']}.json"
s = json.load(open(sabit, encoding="utf-8")) if os.path.exists(sabit) else uret.senaryo(kavram, "tr")
print(json.dumps(s, ensure_ascii=False, indent=1))
os.makedirs("deneme", exist_ok=True)
with open("deneme/senaryo.json", "w", encoding="utf-8") as f:
    json.dump(s, f, ensure_ascii=False, indent=1)
video = uret.video_yap(s, "tr", gun_no, "deneme")
print("Video hazır:", video)
subprocess.run(["open", video])
