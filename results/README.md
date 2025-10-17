# Results Directory

Bu dizinde test sonuçları, grafikler ve analiz raporları saklanır.

## İçerik

Test scriptleri çalıştırıldığında bu dizinde şu dosyalar oluşturulacak:

### Test Sonuçları
- `*_YYYYMMDD_HHMMSS.json` - Ham test verileri (JSON formatında)
- `*_YYYYMMDD_HHMMSS_summary.csv` - Özet istatistikler (CSV formatında)

### Grafikler
- `latency_comparison.png` - Gecikme karşılaştırma grafiği
- `throughput_comparison.png` - Throughput analiz grafiği
- `packet_loss_comparison.png` - Paket kaybı karşılaştırması
- `convergence_comparison.png` - Convergence time grafiği
- `radar_comparison.png` - Genel performans radar grafiği

### Raporlar
- `analysis_report.txt` - Detaylı metin tabanlı analiz raporu

## Kullanım

```bash
# Test çalıştır
cd tests
python3 performance_test.py

# Sonuçları görselleştir
cd utils
python3 visualizer.py

# Sonuçları görüntüle
cd results
ls -lh
```

## Örnek Çıktı Yapısı

```
results/
├── shortest_path_20251017_143052.json
├── shortest_path_20251017_143052_summary.csv
├── load_balancing_20251017_144218.json
├── load_balancing_20251017_144218_summary.csv
├── qos_based_20251017_145334.json
├── qos_based_20251017_145334_summary.csv
├── latency_comparison.png
├── throughput_comparison.png
├── packet_loss_comparison.png
├── convergence_comparison.png
├── radar_comparison.png
└── analysis_report.txt
```

## Not

`.gitignore` dosyasında sonuç dosyaları (*.json, *.csv, *.png) ignore edilmiştir.
Sadece bu README dosyası git'e commit edilir.
