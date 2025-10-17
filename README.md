# SDN Tabanlı Dinamik Yönlendirme Sistemi

## Proje Özeti
Bu proje, Software-Defined Networking (SDN) mimarisinde farklı dinamik yönlendirme algoritmalarını geliştirip performans karşılaştırması yapmayı amaçlamaktadır.

## Özellikler
- **Shortest Path Routing**: Dijkstra algoritması tabanlı en kısa yol yönlendirmesi
- **Load Balancing Routing**: Yük dengeleme tabanlı dinamik yönlendirme
- **QoS-Based Routing**: Gecikme ve bant genişliği bazlı kalite odaklı yönlendirme

## Kullanılan Teknolojiler
- **Mininet**: Sanal ağ simülasyonu
- **Ryu Controller**: SDN kontrol düzlemi
- **Python**: Algoritma geliştirme ve analiz
- **Matplotlib**: Veri görselleştirme
- **iPerf**: Performans testi

## Kurulum

### Gereksinimler
```bash
# Linux sistemlerde (Ubuntu/Debian):
sudo apt-get update
sudo apt-get install mininet python3-pip
pip3 install ryu matplotlib pandas networkx
```

### Windows Üzerinde (WSL2 veya VM Gerekli)
Bu proje Mininet gerektirdiğinden Linux ortamında çalışır. Windows kullanıcıları:
1. WSL2 (Windows Subsystem for Linux) kurabilir
2. VirtualBox/VMware ile Ubuntu VM kullanabilir

## Proje Yapısı
```
sdn/
├── controllers/          # SDN controller implementasyonları
│   ├── shortest_path_controller.py
│   ├── load_balancing_controller.py
│   └── qos_controller.py
├── topologies/          # Mininet topoloji tanımları
│   ├── simple_topology.py
│   ├── complex_topology.py
│   └── mesh_topology.py
├── tests/               # Test scriptleri
│   ├── performance_test.py
│   └── traffic_generator.py
├── utils/               # Yardımcı araçlar
│   ├── logger.py
│   ├── metrics_collector.py
│   └── visualizer.py
├── results/             # Test sonuçları ve grafikler
└── docs/                # Dokümantasyon ve raporlar
```

## Kullanım

### 1. Topoloji Oluşturma
```bash
sudo python3 topologies/simple_topology.py
```

### 2. Controller Başlatma
```bash
# Terminal 1 - Controller'ı başlat
ryu-manager controllers/shortest_path_controller.py

# Terminal 2 - Mininet'i başlat
sudo python3 topologies/simple_topology.py
```

### 3. Performans Testleri
```bash
# Mininet CLI'da
mininet> h1 ping -c 10 h2
mininet> iperf h1 h2
```

### 4. Analiz ve Raporlama
```bash
python3 tests/performance_test.py
python3 utils/visualizer.py
```

## Test Senaryoları

### Senaryo 1: Temel Bağlantı Testi
- Ping testleri ile gecikme ölçümü
- Paket kaybı analizi

### Senaryo 2: Throughput Testi
- iPerf ile bant genişliği ölçümü
- Farklı yük seviyelerinde performans

### Senaryo 3: Link Hatası Simülasyonu
- Link kesintilerinde yeniden yönlendirme
- Convergence time ölçümü

## Performans Metrikleri
- **Latency (Gecikme)**: ms cinsinden ortalama ve maksimum gecikme
- **Throughput (İş Çıkarma)**: Mbps cinsinden bant genişliği kullanımı
- **Packet Loss (Paket Kaybı)**: Yüzde olarak paket kayıp oranı
- **Convergence Time**: Topoloji değişikliklerinde adaptasyon süresi

## Sonuçlar
Test sonuçları ve grafikler `results/` klasöründe bulunur.

## Katkıda Bulunma
Bu bir akademik proje olup, eğitim amaçlıdır.

## Lisans
MIT License

## İletişim
Proje Sahibi: [İsim]
Tarih: Ekim 2025
