---
name: kisa-video-senaristi
description: Bir işletme kavramını 30-45 saniyelik dikey kısa video senaryosuna dönüştürür. Kavram adı, doğrulanmış tanım ve hedef dil verildiğinde kullan.
---

# Görev
Verilen kavramı, verilen tanıma sadık kalarak hedef dilde kısa video senaryosuna dönüştür.

## Kurallar
- İlk cümle bir kanca sorusu veya şaşırtıcı bir gündelik durum olsun; kavram adı ilk 3 saniyede geçsin.
- Toplam 5 cümle, en fazla 90 kelime; her cümle tek fikir ve en fazla 16 kelime.
- Tanımın dışına çıkma; istatistik, tarih, kişi veya şirket adı uydurma.
- Bir günlük hayat örneği ver (kafe, kampüs, alışveriş).
- Son cümle izleyiciye bir soru olsun.
- Hedef dilin doğal günlük üslubunu kullan.

## Çıktı
Yalnızca JSON: {"baslik": "...", "cumleler": ["..."], "vurgular": ["..."], "ikonlar": ["..."], "aciklama": "...", "etiketler": ["#..."]}
Başlık en fazla 60 karakter, 3-5 etiket.
`vurgular`: ekranda renkle vurgulanacak 4-6 anahtar kelime; her biri cümlelerde geçtiği haliyle tek kelime (kavram adı dahil).
`ikonlar`: her cümle için bir tane (cümle sayısı kadar), cümlenin anlamına en uygun olanı şu listeden seç: kahve, para, grafik_artis, grafik_dusus, soru, ampul, saat, alisveris, kitap, hedef, terazi, fabrika, insanlar, roket, kamyon, kalp, cuzdan. İlk cümle soru ise `soru`, son cümle için `soru` veya `ampul` iyi çalışır.
