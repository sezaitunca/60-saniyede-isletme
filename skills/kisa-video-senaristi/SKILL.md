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
Yalnızca JSON: {"baslik": "...", "cumleler": ["..."], "vurgular": ["..."], "aciklama": "...", "etiketler": ["#..."]}
Başlık en fazla 60 karakter, 3-5 etiket.
`vurgular`: ekranda renkle vurgulanacak 4-6 anahtar kelime; her biri cümlelerde geçtiği haliyle tek kelime (kavram adı dahil).
