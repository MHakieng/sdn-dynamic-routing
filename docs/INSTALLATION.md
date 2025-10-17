# SDN Projesi Kurulum Kılavuzu

## 🔧 Sistem Gereksinimleri

### Donanım
- **RAM**: Minimum 4GB (8GB önerilir)
- **Disk**: 10GB boş alan
- **CPU**: 2+ çekirdek

### Yazılım
- **İşletim Sistemi**: Ubuntu 20.04+ / Debian 10+ (WSL2 de kullanılabilir)
- **Python**: 3.7+
- **Git**: En son sürüm

## 📦 Windows'ta Kurulum (WSL2 Kullanarak)

### Adım 1: WSL2 Kurulumu

1. PowerShell'i yönetici olarak açın:
```powershell
wsl --install -d Ubuntu-22.04
```

2. Kurulum tamamlandıktan sonra Ubuntu'yu başlatın ve kullanıcı oluşturun.

3. Ubuntu terminal'inde güncellemeleri yapın:
```bash
sudo apt update && sudo apt upgrade -y
```

### Adım 2: Mininet Kurulumu

```bash
# Gerekli paketleri kur
sudo apt-get install -y git

# Mininet'i klonla ve kur
cd ~
git clone https://github.com/mininet/mininet
cd mininet
git checkout 2.3.0
sudo PYTHON=python3 ./util/install.sh -a

# Kurulumu test et
sudo mn --test pingall
```

### Adım 3: Ryu Controller Kurulumu

```bash
# pip'i güncelle
sudo apt-get install -y python3-pip

# Ryu ve bağımlılıkları kur
pip3 install ryu eventlet
pip3 install networkx matplotlib pandas seaborn numpy
```

### Adım 4: Proje Dosyalarını Kopyala

WSL2'de Windows dosyalarına erişim:
```bash
cd /mnt/c/Users/Hakit/Desktop/PROJE\ DENEMELERİ/sdn

# Veya projeyi WSL home'a kopyala
cp -r /mnt/c/Users/Hakit/Desktop/PROJE\ DENEMELERİ/sdn ~/sdn-project
cd ~/sdn-project
```

### Adım 5: Python Bağımlılıklarını Kur

```bash
pip3 install -r requirements.txt
```

## 🐧 Linux'ta Doğrudan Kurulum

```bash
# Sistem güncellemeleri
sudo apt update && sudo apt upgrade -y

# Mininet kurulumu
sudo apt-get install mininet

# Python ve bağımlılıklar
sudo apt-get install python3-pip python3-dev
pip3 install ryu networkx matplotlib pandas seaborn numpy colorlog

# Proje dizinine git
cd sdn
pip3 install -r requirements.txt
```

## ✅ Kurulum Testi

### Test 1: Mininet
```bash
sudo mn --test pingall
```
Beklenen çıktı: `Results: 0% dropped`

### Test 2: Ryu
```bash
ryu-manager --version
```
Beklenen çıktı: Ryu sürüm numarası

### Test 3: Python Modülleri
```bash
python3 -c "import ryu; import networkx; import matplotlib; print('✓ All modules OK')"
```

## 🚀 İlk Çalıştırma

### Terminal 1: Controller'ı Başlat
```bash
cd ~/sdn-project/controllers
ryu-manager shortest_path_controller.py
```

### Terminal 2: Mininet'i Başlat
```bash
cd ~/sdn-project/topologies
sudo python3 simple_topology.py
```

### Terminal 3: Test Çalıştır (İsteğe bağlı)
```bash
cd ~/sdn-project/tests
python3 performance_test.py
```

## 🔍 Sorun Giderme

### Sorun 1: "sudo: mn: command not found"
**Çözüm:**
```bash
sudo apt-get install mininet
# Veya Mininet'i source'tan kur (yukarıdaki adımlar)
```

### Sorun 2: "ModuleNotFoundError: No module named 'ryu'"
**Çözüm:**
```bash
pip3 install ryu --user
# PATH'e ekle
export PATH=$PATH:~/.local/bin
```

### Sorun 3: "Permission denied" hataları
**Çözüm:**
```bash
# Mininet root gerektiriyor
sudo python3 script.py

# Veya sudo'ya Python path'i ekle
sudo env PATH=$PATH python3 script.py
```

### Sorun 4: Controller bağlanamıyor
**Çözüm:**
```bash
# Port 6653'ün açık olduğunu kontrol et
sudo netstat -tulpn | grep 6653

# Eski controller'ları kapat
sudo pkill -f ryu-manager

# Firewall kontrolü
sudo ufw allow 6653
```

### Sorun 5: WSL2'de grafik görüntüleme
**Çözüm:**
```bash
# X Server kur (Windows'ta VcXsrv veya Xming)
# WSL'de DISPLAY değişkenini ayarla
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0

# Veya matplotlib backend'ini değiştir (kod içinde)
matplotlib.use('Agg')  # GUI gerektirmez
```

## 📝 Faydalı Komutlar

### Mininet Komutları
```bash
# Basit topoloji
sudo mn --topo single,3

# Custom controller
sudo mn --controller=remote,ip=127.0.0.1,port=6653

# Topolojiyi temizle
sudo mn -c
```

### Ryu Komutları
```bash
# Controller'ı verbose modda çalıştır
ryu-manager --verbose controller.py

# Birden fazla app çalıştır
ryu-manager app1.py app2.py

# REST API ile çalıştır
ryu-manager --observe-links controller.py
```

### Mininet CLI Komutları
```
mininet> help              # Komutları listele
mininet> nodes             # Node'ları göster
mininet> net               # Topolojiyi göster
mininet> links             # Link'leri göster
mininet> dump              # Node bilgileri
mininet> h1 ping h2        # Host'lar arası ping
mininet> pingall           # Tüm hostlar arası ping
mininet> iperf h1 h2       # Bant genişliği testi
mininet> link s1 s2 down   # Link'i devre dışı bırak
mininet> link s1 s2 up     # Link'i aktifleştir
mininet> quit              # Çıkış
```

## 🎯 Sonraki Adımlar

1. ✅ Kurulumu tamamladınız
2. 📖 [USAGE.md](USAGE.md) dosyasını okuyun
3. 🧪 Test senaryolarını çalıştırın
4. 📊 Sonuçları analiz edin
5. 📄 Rapor hazırlayın

## 📚 Ek Kaynaklar

- [Mininet Walkthrough](http://mininet.org/walkthrough/)
- [Ryu Documentation](https://ryu.readthedocs.io/)
- [OpenFlow Tutorial](https://github.com/mininet/openflow-tutorial)
- [SDN Fundamentals](https://www.coursera.org/learn/sdn)

## 🆘 Destek

Sorun yaşarsanız:
1. Bu dosyadaki sorun giderme bölümünü kontrol edin
2. Log dosyalarını inceleyin (`logs/` dizini)
3. GitHub Issues'da benzer sorunları arayın
