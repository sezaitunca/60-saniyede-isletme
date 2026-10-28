# Colab'da çalıştırın: kavramlar.json dosyasını yükleyin, sonra bu hücreyi çalıştırın.
# Üretilen sira.json dosyasını indirip data/ altına koyun.
!pip install -U sentence-transformers

import json, torch
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("google/embeddinggemma-2",
                            model_kwargs={"torch_dtype": torch.float32})
kavramlar = json.load(open("kavramlar.json", encoding="utf-8"))
emb = model.encode([f"{k['ad']}. {k['tanim']}" for k in kavramlar],
                   prompt_name="Document")
benzerlik = model.similarity(emb, emb)

kalan = list(range(len(kavramlar)))
sira = [kalan.pop(0)]
while kalan:
    son7 = sira[-7:]
    secilen = min(kalan, key=lambda j: max(benzerlik[i][j].item() for i in son7))
    sira.append(secilen)
    kalan.remove(secilen)

json.dump([kavramlar[i]["id"] for i in sira], open("sira.json", "w"))
