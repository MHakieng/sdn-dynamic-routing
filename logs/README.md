# Logs Directory

Bu dizinde controller ve sistem logları saklanır.

## İçerik

- Controller logları
- Test logları
- System event logları

## Log Dosyası Formatı

```
YYYYMMDD_HHMMSS_<component>.log
```

### Örnek
```
logs/
├── 20251017_143052_controller.log
├── 20251017_143052_test.log
└── SDN_20251017_150123.log
```

## Log Seviyeleri

- **DEBUG**: Detaylı debugging bilgileri
- **INFO**: Genel bilgilendirme mesajları
- **WARNING**: Uyarı mesajları
- **ERROR**: Hata mesajları
- **CRITICAL**: Kritik sistem hataları

## Kullanım

```bash
# Logları görüntüle
tail -f logs/controller.log

# Son 100 satırı göster
tail -n 100 logs/controller.log

# Hataları filtrele
grep "ERROR" logs/*.log

# Log temizliği
rm logs/*.log
```

## Not

Log dosyaları `.gitignore`'da ignore edilmiştir.
