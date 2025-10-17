# 🐧 Ubuntu VirtualBox Kurulum Kılavuzu

## 📋 Sistem Gereksinimleri

### VirtualBox VM Ayarları
- **İşletim Sistemi**: Ubuntu 22.04 LTS
- **RAM**: 4 GB (minimum 2 GB)
- **CPU**: 2 çekirdek
- **Disk**: 25 GB
- **Ağ**: NAT veya Bridged

## 🚀 Adım Adım Kurulum

### 1. Ubuntu'yu Güncelleyin

```bash
sudo apt update
sudo apt upgrade -y
```

### 2. Gerekli Paketleri Kurun

```bash
# Build essentials
sudo apt install -y build-essential git wget curl vim

# Python ve pip
sudo apt install -y python3 python3-pip python3-dev

# Network araçları
sudo apt install -y net-tools iperf iperf3 tcpdump wireshark
```

### 3. Mininet Kurulumu

#### Yöntem 1: APT ile (Hızlı)
```bash
sudo apt install -y mininet
```

#### Yöntem 2: Source'tan (Önerilen - En güncel)
```bash
cd ~
git clone https://github.com/mininet/mininet
cd mininet
git checkout 2.3.0

# Tüm bileşenleri kur (-a: all)
sudo PYTHON=python3 ./util/install.sh -a

# Kurulumu test et
sudo mn --test pingall
```

**Beklenen çıktı:**
```
*** Results: 0% dropped (2/2 received)
```

### 4. Ryu Controller Kurulumu

```bash
# pip'i güncelle
pip3 install --upgrade pip

# Ryu ve bağımlılıkları
pip3 install ryu eventlet

# Ek kütüphaneler
pip3 install networkx matplotlib pandas seaborn numpy
```

### 5. Projeyi İndirin

#### GitHub'dan klonlama
```bash
cd ~
git clone https://github.com/MHakieng/sdn-dynamic-routing.git
cd sdn-dynamic-routing
```

#### Veya Windows'tan paylaşılan klasörden kopyalama
```bash
# VirtualBox'ta Shared Folder ayarlayın
# Devices > Shared Folders > Add folder
# Windows path: C:\Users\Hakit\Desktop\PROJE DENEMELERİ\sdn
# Mount point: /home/yourusername/sdn-project

# Kopyalama
cp -r /media/sf_sdn ~/sdn-project
cd ~/sdn-project
```

### 6. Python Bağımlılıklarını Kurun

```bash
cd ~/sdn-dynamic-routing  # veya ~/sdn-project
pip3 install -r requirements.txt
```

### 7. Test Edin

```bash
# Mininet testi
sudo mn --test pingall

# Ryu testi
ryu-manager --version

# Python modül testi
python3 -c "import ryu; import networkx; import matplotlib; print('✓ All OK!')"
```

## 🎯 İlk Çalıştırma

### Terminal 1: Controller Başlat
```bash
cd ~/sdn-dynamic-routing/controllers
ryu-manager shortest_path_controller.py
```

**Beklenen çıktı:**
```
loading app shortest_path_controller.py
instantiating app shortest_path_controller.py
...
Shortest Path Controller initialized
```

### Terminal 2: Mininet Başlat
```bash
cd ~/sdn-dynamic-routing/topologies
sudo python3 simple_topology.py
```

**Beklenen çıktı:**
```
*** Creating network
*** Adding controller
*** Adding hosts
*** Adding switches
...
mininet>
```

### Terminal 3: Mininet CLI'da Testler

```bash
mininet> pingall
mininet> h1 ping -c 10 h2
mininet> iperf h1 h2
mininet> quit
```

## 🔧 Yaygın Sorunlar ve Çözümler

### Sorun 1: "sudo: mn: command not found"

**Çözüm:**
```bash
# Mininet tekrar kur
sudo apt-get install mininet

# Veya PATH'i kontrol et
which mn
```

### Sorun 2: "Controller bağlanamıyor"

**Çözüm:**
```bash
# Eski Mininet instance'ları temizle
sudo mn -c

# Controller'ı durdur
pkill -f ryu-manager

# Port'u kontrol et
sudo netstat -tulpn | grep 6653

# Tekrar dene
```

### Sorun 3: "ImportError: No module named ryu"

**Çözüm:**
```bash
# pip3 ile kur
pip3 install ryu --user

# PATH'e ekle
echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc
source ~/.bashrc
```

### Sorun 4: "Permission denied" hataları

**Çözüm:**
```bash
# Mininet root gerektirir
sudo python3 script.py

# Kullanıcıyı netdev grubuna ekle (opsiyonel)
sudo usermod -aG netdev $USER
# Logout/login gerektirir
```

### Sorun 5: Grafik görüntüleme sorunu

**Çözüm:**
```bash
# matplotlib backend'ini Agg'e ayarla (GUI gerektirmez)
# visualizer.py dosyasında zaten ayarlı

# Veya X11 forwarding aktif et (SSH kullanıyorsanız)
export DISPLAY=:0
```

### Sorun 6: OVS (Open vSwitch) hatası

**Çözüm:**
```bash
# OVS'yi kur
sudo apt-get install openvswitch-switch

# Servisi başlat
sudo service openvswitch-switch start

# Durumunu kontrol et
sudo ovs-vsctl show
```

## 📦 VirtualBox İpuçları

### Guest Additions Kurulumu (Önerilen)

```bash
# Daha iyi performans ve ekran çözünürlüğü için
sudo apt install virtualbox-guest-utils virtualbox-guest-x11
sudo reboot
```

### Shared Clipboard Aktif Etme

1. VM kapalıyken
2. VirtualBox > Settings > General > Advanced
3. Shared Clipboard: Bidirectional
4. Drag'n'Drop: Bidirectional

### Ağ Ayarları

**NAT (Varsayılan)**
- Internet erişimi var
- Dışarıdan erişim yok
- Port forwarding eklenebilir

**Bridged Adapter (Önerilen)**
- Kendi IP'si var
- Windows'tan direkt erişilebilir
- Daha gerçekçi test

### Performans İyileştirme

```bash
# VM'i kapatın, sonra:
# VirtualBox > Settings > System > Processor
# - CPU sayısını artırın (2-4)
# - "Enable PAE/NX" aktif edin

# VirtualBox > Settings > Display
# - Video Memory: 128 MB
# - Enable 3D Acceleration
```

## 🎓 Test Senaryosu Örneği

### Senaryo: 3 Controller Karşılaştırması

```bash
# 1. Shortest Path Test
cd ~/sdn-dynamic-routing
ryu-manager controllers/shortest_path_controller.py &
sudo python3 topologies/simple_topology.py
# Testleri çalıştır (mininet CLI'da)
sudo mn -c

# 2. Load Balancing Test
ryu-manager controllers/load_balancing_controller.py &
sudo python3 topologies/simple_topology.py
# Testleri çalıştır
sudo mn -c

# 3. QoS Test
ryu-manager controllers/qos_controller.py &
sudo python3 topologies/simple_topology.py
# Testleri çalıştır
sudo mn -c

# 4. Otomatik test çalıştır
cd tests
python3 performance_test.py

# 5. Sonuçları görselleştir
cd ../utils
python3 visualizer.py

# 6. Sonuçları gör
cd ../results
ls -lh
```

## 📊 Performans Testleri

### Ping Testi
```bash
mininet> h1 ping -c 100 h2
```

### Throughput Testi
```bash
mininet> iperf h1 h2
mininet> iperf -u -b 50M h1 h2  # UDP, 50Mbps
```

### Link Kesinti Testi
```bash
mininet> h1 ping h2 &
mininet> link s1 s2 down
# Convergence time'ı gözlemle
mininet> link s1 s2 up
```

### Paralel Trafik
```bash
mininet> xterm h1 h2 h3 h4
# Her terminal'de farklı testler çalıştır
```

## 🔍 Debug ve Monitoring

### Wireshark ile Paket Yakalama
```bash
# Wireshark'ı root olarak başlat
sudo wireshark

# Interface seç: s1-eth1, s1-eth2, vb.
```

### OpenFlow Flow Tablosunu Görüntüleme
```bash
# Tüm switch'ler için
sudo ovs-ofctl dump-flows s1
sudo ovs-ofctl dump-flows s2
sudo ovs-ofctl dump-flows s3
sudo ovs-ofctl dump-flows s4
```

### Controller Loglarını İzleme
```bash
# Gerçek zamanlı log izleme
tail -f ~/sdn-dynamic-routing/logs/controller.log

# Hata arama
grep "ERROR" ~/sdn-dynamic-routing/logs/*.log
```

### Network Interface Monitoring
```bash
# Trafik göster
sudo iftop -i s1-eth1

# Paket sayısı
sudo tcpdump -i s1-eth1 -c 100
```

## 📝 Hızlı Komutlar

### Temizlik
```bash
# Mininet temizle
sudo mn -c

# Controller durdur
pkill -f ryu-manager

# Python cache temizle
find . -type d -name __pycache__ -exec rm -rf {} +
```

### Hızlı Başlat (Tek Script)
```bash
cd ~/sdn-dynamic-routing
chmod +x start.sh
./start.sh
```

### Snapshot Alın!
Kurulum tamamlandıktan sonra VirtualBox'ta snapshot alın:
- VM > Machine > Take Snapshot
- İsim: "SDN Setup Complete"
- Bir sorun olursa bu noktaya dönebilirsiniz

## ✅ Kurulum Kontrol Listesi

- [ ] Ubuntu 22.04 LTS kuruldu
- [ ] Sistem güncellemeleri yapıldı
- [ ] Mininet kuruldu ve test edildi
- [ ] Ryu Controller kuruldu
- [ ] Python kütüphaneleri kuruldu
- [ ] Proje GitHub'dan klonlandı
- [ ] İlk test başarılı (pingall)
- [ ] Controller çalışıyor
- [ ] Grafikler oluşturuluyor
- [ ] Guest Additions kuruldu (opsiyonel)
- [ ] Snapshot alındı

## 🎉 Başarılı Kurulum Göstergeleri

```bash
# 1. Mininet çalışıyor
$ sudo mn --test pingall
*** Results: 0% dropped

# 2. Ryu kurulu
$ ryu-manager --version
ryu-manager 4.34

# 3. Python modülleri tamam
$ python3 -c "import ryu; import mininet; print('OK')"
OK

# 4. Controller çalışıyor
$ ryu-manager controllers/shortest_path_controller.py
Shortest Path Controller initialized
```

## 📚 Ek Kaynaklar

- [Mininet Walkthrough](http://mininet.org/walkthrough/)
- [Ryu Book](https://osrg.github.io/ryu-book/en/html/)
- [OpenFlow Tutorial](https://github.com/mininet/openflow-tutorial/wiki)
- [VirtualBox Manual](https://www.virtualbox.org/manual/)

## 🆘 Yardım

Sorun yaşarsanız:
1. Bu dokümandaki "Yaygın Sorunlar" bölümüne bakın
2. Log dosyalarını kontrol edin
3. `sudo mn -c` ile temizlik yapın
4. Snapshot'a geri dönün

---

**Hazırlayan**: GitHub Copilot
**Son Güncelleme**: Ekim 2025
**Versiyon**: 1.0
