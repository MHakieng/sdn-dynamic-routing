# 🚀 Hızlı Başlangıç Kılavuzu

## ⚡ 5 Dakikada Başla

### 1️⃣ Kurulum (Sadece İlk Kez)

```bash
# WSL2/Ubuntu'da
cd ~/sdn-project

# Bağımlılıkları kur
pip3 install -r requirements.txt

# Mininet'i test et
sudo mn --test pingall
```

### 2️⃣ İlk Test (3 adım)

#### Terminal 1: Controller Başlat
```bash
cd controllers
ryu-manager shortest_path_controller.py
```

#### Terminal 2: Ağ Oluştur
```bash
cd topologies
sudo python3 simple_topology.py
```

#### Terminal 3: Mininet CLI
```
mininet> pingall
mininet> h1 ping -c 10 h2
mininet> iperf h1 h2
```

### 3️⃣ Otomatik Başlatma (Tek Komut)

```bash
chmod +x start.sh
./start.sh
```

## 📊 Hızlı Test ve Sonuç

### Test Çalıştır
```bash
cd tests
python3 performance_test.py
```

### Sonuçları Görselleştir
```bash
cd utils
python3 visualizer.py
```

### Sonuçları Gör
```bash
cd results
ls -lh
# PNG dosyalarını aç ve grafiklerini incele
```

## 🎯 Temel Komutlar Cheat Sheet

### Mininet CLI
```
pingall          # Tüm hostlar arası ping
h1 ping h2       # İki host arası ping
iperf h1 h2      # Throughput testi
link s1 s2 down  # Link'i kapat
link s1 s2 up    # Link'i aç
net              # Topolojiyi göster
quit             # Çıkış
```

### Controller Komutları
```bash
# Shortest Path
ryu-manager controllers/shortest_path_controller.py

# Load Balancing
ryu-manager controllers/load_balancing_controller.py

# QoS-Based
ryu-manager controllers/qos_controller.py
```

### Temizlik
```bash
# Mininet temizle
sudo mn -c

# Controller'ı durdur
pkill -f ryu-manager
```

## 🔧 Sorun mu Yaşıyorsun?

### "Command not found: mn"
```bash
sudo apt-get install mininet
```

### "Controller bağlanamıyor"
```bash
sudo mn -c
pkill -f ryu-manager
# Tekrar dene
```

### "Permission denied"
```bash
# Mininet root gerektirir
sudo python3 script.py
```

## 📚 Daha Fazla Bilgi

- **Detaylı Kurulum**: `docs/INSTALLATION.md`
- **Tam Kullanım Kılavuzu**: `docs/USAGE.md`
- **Proje Raporu**: `docs/PROJECT_REPORT.md`

## 🎓 Demo Senaryosu

### Senaryo: 3 Controller'ı Karşılaştır

1. **Shortest Path Test** (5 dk)
   ```bash
   ryu-manager controllers/shortest_path_controller.py
   # Yeni terminal
   sudo python3 topologies/simple_topology.py
   # Mininet CLI'da testler
   ```

2. **Load Balancing Test** (5 dk)
   ```bash
   # Öncekini kapat (Ctrl+C)
   ryu-manager controllers/load_balancing_controller.py
   # Aynı testleri tekrarla
   ```

3. **QoS Test** (5 dk)
   ```bash
   # Öncekini kapat (Ctrl+C)
   ryu-manager controllers/qos_controller.py
   # Aynı testleri tekrarla
   ```

4. **Sonuçları Karşılaştır**
   ```bash
   cd utils
   python3 visualizer.py
   # results/ dizinindeki grafikleri incele
   ```

## ✅ Başarı Kriterleri

- ✅ Mininet başarıyla çalışıyor
- ✅ Controller bağlanıyor
- ✅ Pingall %100 başarılı
- ✅ iPerf throughput ölçümleri alınıyor
- ✅ Grafikler oluşturuluyor

## 🎉 Tebrikler!

Artık SDN projeni çalıştırabiliyorsun!

**Sonraki Adımlar**:
1. Farklı topolojileri dene
2. Custom controller geliştir
3. Advanced testler çalıştır
4. Raporu tamamla
