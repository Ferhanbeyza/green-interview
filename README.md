# Yapay Zeka Destekli Mülakat Platformlarında Video İşleme ve Karbon İsrafı Optimizasyonu

Yeşil İşe Alım & Bilgisayarlı Görü optimizasyonu. Video mülakatlarda yüz ifadesi (duygu)
analizinin enerji israfını **GSF CodeCarbon** ile ölçer ve **dinamik kare atlatma
(Adaptive Frame Sampling)** + hafifletilmiş ön işleme ile azaltır.

## Problem

Mülakat videoları analiz edilirken derin sinir ağı saniyedeki tüm kareleri (30 fps), ham
çözünürlükte tek tek işler. Ardışık karelerin çoğu neredeyse aynıdır; her birinde modeli
yeniden çalıştırmak gereksiz CPU/GPU tüketimi ve karbon salınımıdır.

## Çözüm

| Aşama | Dosya | Çıktı |
|---|---|---|
| 1. Hedef kod | Açık kaynaklı [DeepFace](https://github.com/serengil/deepface) duygu analizi (`common.py`) | Çalışan yüz ifadesi analizi |
| 2. Baseline ölçümü | `baseline.py` — her kare, ham çözünürlük | `results/emissions_baseline.csv` |
| 3. Kod iyileştirme | `optimized.py` — dinamik kare atlatma + 480p ön işleme | Optimize Python kodu |
| 4. İkinci ölçüm | `optimized.py` + `compare.py` — aynı videolar | `results/emissions_optimized.csv`, tasarruf yüzdesi |
| 5. Sürdürülebilirlik raporu | `compare.py` | `results/summary.md`, `results/comparison.png` |
| Tarayıcıda ön eleme | `web/index.html` — OpenCV.js (WebAssembly) | Sunucuya gidecek kare / veri miktarı |

### Dinamik kare atlatma nasıl çalışır?

1. Her kare 160×90 gri bir kopyaya indirilir (çok ucuz bir işlem).
2. Bu kopya, en son **analiz edilen** karenin kopyasıyla karşılaştırılır (ortalama piksel farkı).
3. Fark eşiğin (`--threshold`, varsayılan 5.0) üzerindeyse kare "kritik"tir: 480p'ye küçültülür ve model çalıştırılır.
4. Değilse model çalıştırılmaz, önceki duygu sonucu o kare için aynen kullanılır.
5. Güvenlik için en geç `--max-gap` (varsayılan 1 sn) sürede bir kare mutlaka analiz edilir.

## Kurulum

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

`data/` klasörüne bir veya birkaç mülakat videosu (mp4, mov, avi, mkv, webm) koyun.
İlk çalıştırmada DeepFace model ağırlıklarını bir kez indirir.

## Çalıştırma

```bash
python baseline.py data/      # 1. ölçüm
python optimized.py data/     # 2. ölçüm (aynı videolar)
python compare.py             # kıyaslama + grafik
```

Tarayıcı demosu: `web/index.html` dosyasını tarayıcıda açıp bir video seçin.

## Sonuçlar

`python compare.py` çıktısı `results/summary.md` dosyasına yazılır.

## Araçlar

GSF CodeCarbon · OpenCV · DeepFace · OpenCV.js (WebAssembly)
