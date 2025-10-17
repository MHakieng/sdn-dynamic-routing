# SDN Projesi Kullanım Kılavuzu

## 📚 İçindekiler

1. [Hızlı Başlangıç](#hızlı-başlangıç)
2. [Controller'lar](#controllers)
3. [Topolojiler](#topolojiler)
4. [Test Senaryoları](#test-senaryoları)
5. [Sonuç Analizi](#sonuç-analizi)
6. [İleri Seviye Kullanım](#ileri-seviye-kullanım)

## 🚀 Hızlı Başlangıç

### Temel Test Akışı

```bash
# 1. Controller'ı başlat (Terminal 1)
cd controllers
ryu-manager shortest_path_controller.py

# 2. Topolojiyi başlat (Terminal 2)
cd topologies
sudo python3 simple_topology.py

# 3. Mininet CLI'da testler
mininet> pingall
mininet> h1 ping -c 10 h2
mininet> iperf h1 h2
```

## 🎮 Controllers

### 1. Shortest Path Controller

**Ne yapar:** Dijkstra algoritması ile en kısa yolu hesaplar.

**Kullanım:**
```bash
ryu-manager controllers/shortest_path_controller.py
```

**Avantajları:**
- ✅ Hızlı yol hesaplama
- ✅ Basit ve anlaşılır
- ✅ Düşük gecikme

**Dezavantajları:**
- ❌ Yük dengeleme yok
- ❌ QoS desteği yok

**En uygun senaryolar:**
- Basit topolojiler
- Düşük gecikme gerektiren uygulamalar
- Stable ağlar (az değişiklik)

### 2. Load Balancing Controller

**Ne yapar:** Trafik yükünü dengeleyerek yol seçer.

**Kullanım:**
```bash
ryu-manager controllers/load_balancing_controller.py
```

**Avantajları:**
- ✅ Yük dengeli trafik dağıtımı
- ✅ Congestio önleme
- ✅ Daha iyi kaynak kullanımı

**Dezavantajları:**
- ❌ Daha yüksek hesaplama maliyeti
- ❌ Bazen daha uzun yollar

**En uygun senaryolar:**
- Yoğun trafik
- Çoklu path olan topolojiler
- Bant genişliği kritik uygulamalar

### 3. QoS-Based Controller

**Ne yapar:** Gecikme, bant genişliği ve paket kaybına göre yol seçer.

**Kullanım:**
```bash
ryu-manager controllers/qos_controller.py
```

**Avantajları:**
- ✅ Uygulama gereksinimlerine göre optimizasyon
- ✅ Çoklu metrik desteği
- ✅ Önceliklendirme

**Dezavantajları:**
- ❌ En karmaşık
- ❌ Daha fazla overhead

**En uygun senaryolar:**
- Heterojen trafik (VoIP, video, data)
- SLA gereksinimleri
- Kalite odaklı uygulamalar

## 🗺️ Topolojiler

### Simple Topology (4 switch, 4 host)

```
h1---s1---s2---h2
      |\ /|
      | X |
      |/ \|
h3---s3---s4---h4
```

**Kullanım:**
```bash
sudo python3 topologies/simple_topology.py
```

**Özellikler:**
- Küçük ve test için ideal
- Çoklu path seçenekleri
- Link karakteristikleri farklı

### Complex Topology (8 switch, 8 host)

```
h1---s1---s2---h2
      |\ /|
      | X |
      |/ \|
h3---s3---s4---h4
      |\ /|
      | X |
      |/ \|
h5---s5---s6---h6
      |\ /|
      | X |
      |/ \|
h7---s7---s8---h8
```

**Kullanım:**
```bash
sudo python3 topologies/complex_topology.py
```

**Özellikler:**
- Gerçekçi ağ simülasyonu
- Çok sayıda alternatif yol
- Scalability testi

## 🧪 Test Senaryoları

### Manuel Testler (Mininet CLI)

#### 1. Temel Bağlantı Testi
```
mininet> pingall
```

#### 2. Gecikme Ölçümü
```
mininet> h1 ping -c 100 h2
```

#### 3. Throughput Testi
```
mininet> iperf h1 h2
mininet> iperf -u -b 50M h1 h2  # UDP, 50Mbps
```

#### 4. Link Kesinti Simülasyonu
```
mininet> link s1 s2 down
mininet> h1 ping h2
mininet> link s1 s2 up
```

#### 5. Paralel İletişim
```
mininet> h1 ping h2 &
mininet> h3 ping h4 &
```

### Otomatik Testler

#### Performance Test
```bash
cd tests
python3 performance_test.py
```

**Ne yapar:**
- Ping testleri (latency, packet loss)
- iPerf testleri (throughput)
- Convergence testleri (recovery time)
- Tüm controller'lar için karşılaştırma

**Çıktılar:**
- `results/*.json` - Ham veri
- `results/*_summary.csv` - Özet tablo

#### Traffic Generator
```bash
cd tests
python3 traffic_generator.py
```

**Senaryolar:**
1. **Light**: Düşük yük (5 pps, 30s)
2. **Medium**: Orta yük (20 pps, 60s)
3. **Heavy**: Yüksek yük (50 pps, 60s)
4. **Mixed**: Karışık pattern'ler

**Custom trafik:**
```python
from traffic_generator import TrafficGenerator

gen = TrafficGenerator(['h1', 'h2', 'h3', 'h4'])
gen.generate_uniform_traffic(duration=60, packets_per_second=20)
```

## 📊 Sonuç Analizi

### Visualizer Kullanımı

```bash
cd utils
python3 visualizer.py
```

**Oluşturulan çıktılar:**

1. **latency_comparison.png**
   - Box plot: Gecikme dağılımı
   - Bar chart: Ortalama gecikme

2. **throughput_comparison.png**
   - Violin plot: Throughput dağılımı
   - Bar chart: Ortalama vs maksimum

3. **packet_loss_comparison.png**
   - Bar chart: Paket kaybı oranları

4. **convergence_comparison.png**
   - Bar chart: Recovery süreleri

5. **radar_comparison.png**
   - Radar chart: Genel performans

6. **analysis_report.txt**
   - Detaylı metriker
   - İstatistiksel analiz
   - Öneriler

### Sonuçları Yorumlama

#### Latency (Gecikme)
- **İyi**: < 20ms
- **Orta**: 20-50ms
- **Kötü**: > 50ms

#### Throughput (İş Çıkarma)
- **İyi**: > 80% link capacity
- **Orta**: 50-80%
- **Kötü**: < 50%

#### Packet Loss (Paket Kaybı)
- **İyi**: < 0.5%
- **Orta**: 0.5-1%
- **Kötü**: > 1%

#### Convergence Time
- **İyi**: < 1 second
- **Orta**: 1-3 seconds
- **Kötü**: > 3 seconds

## 🔬 İleri Seviye Kullanım

### Custom Controller Geliştirme

```python
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3

class MyController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    
    def __init__(self, *args, **kwargs):
        super(MyController, self).__init__(*args, **kwargs)
        # Initialization
    
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        # Switch connection handler
        pass
    
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        # Packet-in handler
        pass
```

### Custom Topoloji Oluşturma

```python
from mininet.topo import Topo

class MyTopo(Topo):
    def build(self):
        # Add hosts
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        
        # Add switches
        s1 = self.addSwitch('s1')
        
        # Add links
        self.addLink(h1, s1, bw=100, delay='5ms')
        self.addLink(s1, h2, bw=100, delay='5ms')
```

### Log Analizi

```bash
# Controller logları
tail -f logs/controller.log

# Mininet logları
sudo mn -c --verbosity debug

# Flow tablosu
sudo ovs-ofctl dump-flows s1
```

### Gerçek Zamanlı İzleme

```bash
# Trafik izleme
sudo tcpdump -i s1-eth1 -w capture.pcap

# Wireshark ile analiz
wireshark capture.pcap

# Flow istatistikleri
watch -n 1 'sudo ovs-ofctl dump-flows s1'
```

## 🎯 Pratik Örnekler

### Örnek 1: Shortest Path vs Load Balancing

```bash
# Terminal 1: Shortest Path Controller
ryu-manager controllers/shortest_path_controller.py

# Terminal 2: Mininet
sudo python3 topologies/simple_topology.py

# Terminal 3: Yoğun trafik oluştur
cd tests
python3 traffic_generator.py
# Seçim: 3 (Heavy)

# Ctrl+C ile durdur ve Load Balancing ile tekrarla
```

### Örnek 2: Link Kesintisi Simülasyonu

```bash
# Controller ve topolojiyi başlat
# Mininet CLI'da:

mininet> h1 ping h2 &
mininet> link s1 s2 down
# Convergence time'ı not et
mininet> link s1 s2 up
```

### Örnek 3: QoS Testleri

```bash
# QoS Controller ile başlat
ryu-manager controllers/qos_controller.py

# Farklı trafik tipleri
# VoIP simulation (UDP, düşük gecikme)
mininet> h1 iperf -u -b 10M h2

# Video streaming (TCP, yüksek throughput)
mininet> h3 iperf -t 30 h4
```

## 📈 Rapor Hazırlama

### 1. Veri Toplama
```bash
# Her controller için test çalıştır
python3 tests/performance_test.py
```

### 2. Analiz
```bash
# Görselleştirme oluştur
python3 utils/visualizer.py
```

### 3. Rapor Yapısı

```
1. GİRİŞ
   - Proje tanımı
   - Amaç ve hedefler

2. YÖNTEM
   - Kullanılan teknolojiler
   - Topoloji tasarımı
   - Controller algoritmaları

3. TESTLER VE SONUÇLAR
   - Test senaryoları
   - Ölçüm metrikleri
   - Grafikler ve tablolar

4. ANALİZ
   - Karşılaştırma
   - Güçlü/zayıf yönler
   - Trade-off'lar

5. SONUÇ VE ÖNERİLER
   - Bulgular
   - Gelecek çalışmalar
```

## 🆘 SSS

**S: Mininet "command not found" hatası?**
C: `sudo apt-get install mininet` veya source'tan kurulum yapın.

**S: Controller bağlanamıyor?**
C: Port 6653'ün açık olduğunu ve başka controller çalışmadığını kontrol edin.

**S: Grafikler oluşturulmuyor?**
C: matplotlib backend'ini 'Agg' olarak ayarlayın (GUI gerektirmez).

**S: Performans düşük?**
C: WSL2 kaynaklarını artırın veya native Linux kullanın.

**S: Test sonuçları gerçekçi değil?**
C: Bu simülasyon ortamıdır. Gerçek değerler donanıma bağlıdır.

## 📚 Ek Kaynaklar

- [OpenFlow Specification](https://opennetworking.org/software-defined-standards/specifications/)
- [Ryu Book](https://osrg.github.io/ryu-book/en/html/)
- [Mininet Documentation](http://mininet.org/documentation/)
- [SDN Tutorial](https://github.com/mininet/openflow-tutorial/wiki)
