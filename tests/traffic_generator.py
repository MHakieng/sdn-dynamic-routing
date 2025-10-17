#!/usr/bin/env python3
"""
Traffic Generator - Gerçekçi ağ trafiği oluşturur
"""

import random
import time
from datetime import datetime


class TrafficGenerator:
    def __init__(self, hosts):
        """
        Args:
            hosts: list - Host listesi ['h1', 'h2', 'h3', 'h4']
        """
        self.hosts = hosts
        self.traffic_patterns = []
    
    def generate_uniform_traffic(self, duration=60, packets_per_second=10):
        """
        Düzgün dağılımlı trafik oluştur
        
        Args:
            duration: int - Test süresi (saniye)
            packets_per_second: int - Saniyedeki paket sayısı
        """
        print(f"\n[UNIFORM TRAFFIC] Generating {packets_per_second} pps for {duration}s")
        
        start_time = time.time()
        packet_count = 0
        
        while time.time() - start_time < duration:
            # Rastgele kaynak ve hedef seç
            src = random.choice(self.hosts)
            dst = random.choice([h for h in self.hosts if h != src])
            
            # Ping gönder (simüle)
            print(f"  [{packet_count}] {src} -> {dst}", end='\r')
            
            packet_count += 1
            time.sleep(1.0 / packets_per_second)
        
        print(f"\n  Generated {packet_count} packets")
        return packet_count
    
    def generate_burst_traffic(self, num_bursts=5, burst_size=100, interval=10):
        """
        Patlamalı (burst) trafik oluştur
        
        Args:
            num_bursts: int - Burst sayısı
            burst_size: int - Her burst'teki paket sayısı
            interval: int - Burst'ler arası süre (saniye)
        """
        print(f"\n[BURST TRAFFIC] {num_bursts} bursts of {burst_size} packets")
        
        total_packets = 0
        
        for burst_num in range(num_bursts):
            print(f"\n  Burst {burst_num + 1}/{num_bursts}")
            
            for i in range(burst_size):
                src = random.choice(self.hosts)
                dst = random.choice([h for h in self.hosts if h != src])
                
                print(f"    [{i+1}/{burst_size}] {src} -> {dst}", end='\r')
                total_packets += 1
                time.sleep(0.01)  # Çok hızlı gönderim
            
            print(f"\n  Burst {burst_num + 1} completed. Waiting {interval}s...")
            if burst_num < num_bursts - 1:
                time.sleep(interval)
        
        print(f"\n  Total packets: {total_packets}")
        return total_packets
    
    def generate_elephant_mouse_traffic(self, duration=60, elephant_ratio=0.2):
        """
        Elephant-Mouse trafik paterni
        Elephant flows: Büyük, uzun süreli akışlar
        Mouse flows: Küçük, kısa süreli akışlar
        
        Args:
            duration: int - Test süresi (saniye)
            elephant_ratio: float - Elephant flow oranı (0-1)
        """
        print(f"\n[ELEPHANT-MOUSE TRAFFIC] Duration: {duration}s, Elephant ratio: {elephant_ratio}")
        
        start_time = time.time()
        elephant_count = 0
        mouse_count = 0
        
        # Elephant flow'ları başlat (iPerf benzeri)
        num_elephants = int(len(self.hosts) * elephant_ratio)
        print(f"\n  Starting {num_elephants} elephant flows...")
        
        for i in range(num_elephants):
            src = self.hosts[i % len(self.hosts)]
            dst = self.hosts[(i + 1) % len(self.hosts)]
            print(f"    Elephant Flow {i+1}: {src} -> {dst}")
            elephant_count += 1
        
        # Mouse flow'ları oluştur
        print(f"\n  Generating mouse flows...")
        while time.time() - start_time < duration:
            src = random.choice(self.hosts)
            dst = random.choice([h for h in self.hosts if h != src])
            
            # Küçük paket burst'ü (1-10 paket)
            burst_size = random.randint(1, 10)
            print(f"    Mouse Flow: {src} -> {dst} ({burst_size} packets)", end='\r')
            mouse_count += burst_size
            
            time.sleep(random.uniform(0.1, 0.5))
        
        print(f"\n\n  Elephant flows: {elephant_count}")
        print(f"  Mouse flows: {mouse_count} packets")
        
        return elephant_count, mouse_count
    
    def generate_ddos_simulation(self, target='h1', duration=30, attack_rate=100):
        """
        DDoS saldırısı simülasyonu (test amaçlı)
        
        Args:
            target: str - Hedef host
            duration: int - Saldırı süresi (saniye)
            attack_rate: int - Saniyedeki paket sayısı
        """
        print(f"\n[DDoS SIMULATION] Target: {target}, Rate: {attack_rate} pps")
        print("  WARNING: This is for testing purposes only!")
        
        start_time = time.time()
        packet_count = 0
        
        attackers = [h for h in self.hosts if h != target]
        
        while time.time() - start_time < duration:
            attacker = random.choice(attackers)
            print(f"  [{packet_count}] {attacker} -> {target} (Attack)", end='\r')
            
            packet_count += 1
            time.sleep(1.0 / attack_rate)
        
        print(f"\n  Total attack packets: {packet_count}")
        return packet_count
    
    def run_scenario(self, scenario_name):
        """
        Önceden tanımlanmış senaryoları çalıştır
        
        Args:
            scenario_name: str - 'light', 'medium', 'heavy', 'mixed'
        """
        print(f"\n{'='*60}")
        print(f"RUNNING SCENARIO: {scenario_name.upper()}")
        print(f"{'='*60}")
        
        if scenario_name == 'light':
            # Hafif yük
            self.generate_uniform_traffic(duration=30, packets_per_second=5)
        
        elif scenario_name == 'medium':
            # Orta yük
            self.generate_uniform_traffic(duration=60, packets_per_second=20)
        
        elif scenario_name == 'heavy':
            # Ağır yük
            self.generate_uniform_traffic(duration=60, packets_per_second=50)
        
        elif scenario_name == 'mixed':
            # Karışık yük
            print("\n  Phase 1: Uniform traffic (30s)")
            self.generate_uniform_traffic(duration=30, packets_per_second=10)
            
            print("\n  Phase 2: Burst traffic")
            self.generate_burst_traffic(num_bursts=3, burst_size=50, interval=5)
            
            print("\n  Phase 3: Elephant-Mouse traffic (30s)")
            self.generate_elephant_mouse_traffic(duration=30, elephant_ratio=0.3)
        
        else:
            print(f"  Unknown scenario: {scenario_name}")


def main():
    """Ana fonksiyon - Kullanım örnekleri"""
    
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║   SDN TRAFFIC GENERATOR                               ║
    ║                                                        ║
    ║   Available Traffic Patterns:                         ║
    ║   1. Uniform Traffic                                  ║
    ║   2. Burst Traffic                                    ║
    ║   3. Elephant-Mouse Traffic                           ║
    ║   4. DDoS Simulation                                  ║
    ║                                                        ║
    ║   Scenarios:                                          ║
    ║   - light: Low traffic load                           ║
    ║   - medium: Medium traffic load                       ║
    ║   - heavy: High traffic load                          ║
    ║   - mixed: Combination of patterns                    ║
    ╚════════════════════════════════════════════════════════╝
    """)
    
    # Host listesi (topolojiye göre ayarla)
    hosts = ['h1', 'h2', 'h3', 'h4']
    
    generator = TrafficGenerator(hosts)
    
    print("\nSelect traffic scenario:")
    print("1. Light")
    print("2. Medium")
    print("3. Heavy")
    print("4. Mixed")
    print("5. Custom")
    
    choice = input("\nEnter choice (1-5): ").strip()
    
    scenario_map = {
        '1': 'light',
        '2': 'medium',
        '3': 'heavy',
        '4': 'mixed'
    }
    
    if choice in scenario_map:
        generator.run_scenario(scenario_map[choice])
    
    elif choice == '5':
        print("\nCustom traffic generation:")
        print("1. Uniform")
        print("2. Burst")
        print("3. Elephant-Mouse")
        print("4. DDoS Simulation")
        
        pattern = input("Select pattern (1-4): ").strip()
        
        if pattern == '1':
            duration = int(input("Duration (seconds): "))
            rate = int(input("Packets per second: "))
            generator.generate_uniform_traffic(duration, rate)
        
        elif pattern == '2':
            bursts = int(input("Number of bursts: "))
            size = int(input("Burst size (packets): "))
            interval = int(input("Interval between bursts (seconds): "))
            generator.generate_burst_traffic(bursts, size, interval)
        
        elif pattern == '3':
            duration = int(input("Duration (seconds): "))
            ratio = float(input("Elephant flow ratio (0-1): "))
            generator.generate_elephant_mouse_traffic(duration, ratio)
        
        elif pattern == '4':
            target = input("Target host (e.g., h1): ")
            duration = int(input("Duration (seconds): "))
            rate = int(input("Attack rate (pps): "))
            generator.generate_ddos_simulation(target, duration, rate)
    
    else:
        print("Invalid choice!")
    
    print("\n\nTraffic generation completed!")
    print("Check controller logs and performance metrics.")


if __name__ == '__main__':
    main()
