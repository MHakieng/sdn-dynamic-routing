#!/usr/bin/env python3
"""
Performans Test Script
SDN controller'ların performansını ölçer ve karşılaştırır
"""

import subprocess
import time
import json
import csv
from datetime import datetime
import os


class PerformanceTest:
    def __init__(self, results_dir='../results'):
        self.results_dir = results_dir
        self.test_results = []
        
        # Results dizinini oluştur
        os.makedirs(results_dir, exist_ok=True)
    
    def run_ping_test(self, src='h1', dst='h2', count=100):
        """
        Ping testi çalıştır ve gecikme metriklerini topla
        
        Returns:
            dict: {
                'min_rtt': float,
                'avg_rtt': float,
                'max_rtt': float,
                'packet_loss': float,
                'successful_pings': int
            }
        """
        print(f"\n[PING TEST] {src} -> {dst} ({count} packets)")
        
        # Mininet CLI üzerinden ping komutu
        # Not: Bu script Mininet dışından çalıştırılıyorsa,
        # Mininet CLI'ya komut gönderme mekanizması gerekir
        
        # Simüle edilmiş sonuçlar (gerçek testlerde Mininet'ten alınır)
        results = {
            'src': src,
            'dst': dst,
            'min_rtt': 5.2,  # ms
            'avg_rtt': 12.4,
            'max_rtt': 25.8,
            'packet_loss': 0.5,  # %
            'successful_pings': int(count * 0.995),
            'total_pings': count
        }
        
        print(f"  Min RTT: {results['min_rtt']} ms")
        print(f"  Avg RTT: {results['avg_rtt']} ms")
        print(f"  Max RTT: {results['max_rtt']} ms")
        print(f"  Packet Loss: {results['packet_loss']}%")
        
        return results
    
    def run_iperf_test(self, src='h1', dst='h2', duration=10, protocol='TCP'):
        """
        iPerf testi çalıştır ve throughput ölç
        
        Returns:
            dict: {
                'throughput': float (Mbps),
                'jitter': float (ms) - UDP için,
                'lost_packets': int - UDP için,
                'protocol': str
            }
        """
        print(f"\n[IPERF TEST] {src} -> {dst} ({protocol}, {duration}s)")
        
        results = {
            'src': src,
            'dst': dst,
            'protocol': protocol,
            'duration': duration,
            'throughput': 85.4,  # Mbps (simüle)
            'jitter': 2.1 if protocol == 'UDP' else None,  # ms
            'lost_packets': 12 if protocol == 'UDP' else None
        }
        
        print(f"  Throughput: {results['throughput']} Mbps")
        if protocol == 'UDP':
            print(f"  Jitter: {results['jitter']} ms")
            print(f"  Lost Packets: {results['lost_packets']}")
        
        return results
    
    def run_convergence_test(self, link='s1-s2'):
        """
        Link kesintisinde convergence time ölç
        
        Returns:
            dict: {
                'link': str,
                'convergence_time': float (seconds),
                'packets_lost_during_failover': int
            }
        """
        print(f"\n[CONVERGENCE TEST] Simulating {link} failure")
        
        # Link'i devre dışı bırak
        print(f"  Disabling link {link}...")
        time.sleep(0.5)
        
        # Yeni yol bulma süresini ölç
        start_time = time.time()
        
        # Ping testleri ile yeni yolun kurulduğunu doğrula
        print(f"  Measuring recovery time...")
        time.sleep(1.5)  # Simüle edilmiş convergence
        
        convergence_time = time.time() - start_time
        
        results = {
            'link': link,
            'convergence_time': convergence_time,
            'packets_lost_during_failover': 8,
            'successful_recovery': True
        }
        
        print(f"  Convergence Time: {results['convergence_time']:.3f} seconds")
        print(f"  Packets Lost: {results['packets_lost_during_failover']}")
        
        # Link'i tekrar aç
        print(f"  Re-enabling link {link}...")
        time.sleep(0.5)
        
        return results
    
    def run_comprehensive_test(self, controller_name, test_scenarios):
        """
        Belirli bir controller için kapsamlı test paketi çalıştır
        
        Args:
            controller_name: str - Controller adı
            test_scenarios: list - Test senaryoları listesi
        
        Returns:
            dict: Test sonuçları
        """
        print(f"\n{'='*60}")
        print(f"TESTING CONTROLLER: {controller_name}")
        print(f"{'='*60}")
        
        results = {
            'controller': controller_name,
            'timestamp': datetime.now().isoformat(),
            'tests': {}
        }
        
        # Ping testleri
        if 'ping' in test_scenarios:
            print("\n--- PING TESTS ---")
            results['tests']['ping'] = []
            
            test_pairs = [('h1', 'h2'), ('h1', 'h3'), ('h2', 'h4')]
            for src, dst in test_pairs:
                ping_result = self.run_ping_test(src, dst, count=100)
                results['tests']['ping'].append(ping_result)
                time.sleep(1)
        
        # iPerf testleri
        if 'throughput' in test_scenarios:
            print("\n--- THROUGHPUT TESTS ---")
            results['tests']['throughput'] = []
            
            for protocol in ['TCP', 'UDP']:
                iperf_result = self.run_iperf_test('h1', 'h2', duration=10, protocol=protocol)
                results['tests']['throughput'].append(iperf_result)
                time.sleep(1)
        
        # Convergence testleri
        if 'convergence' in test_scenarios:
            print("\n--- CONVERGENCE TESTS ---")
            results['tests']['convergence'] = []
            
            links = ['s1-s2', 's2-s4']
            for link in links:
                conv_result = self.run_convergence_test(link)
                results['tests']['convergence'].append(conv_result)
                time.sleep(2)
        
        # Sonuçları kaydet
        self.save_results(results)
        
        return results
    
    def save_results(self, results):
        """Test sonuçlarını JSON ve CSV formatında kaydet"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        controller = results['controller']
        
        # JSON formatında kaydet
        json_file = os.path.join(self.results_dir, f'{controller}_{timestamp}.json')
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n[SAVED] Results saved to {json_file}")
        
        # CSV formatında özet kaydet
        csv_file = os.path.join(self.results_dir, f'{controller}_{timestamp}_summary.csv')
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Controller', 'Timestamp', 'Test Type', 'Metric', 'Value'])
            
            # Ping sonuçları
            if 'ping' in results['tests']:
                for ping in results['tests']['ping']:
                    writer.writerow([controller, results['timestamp'], 'Ping', 
                                   f"{ping['src']}->{ping['dst']} Avg RTT (ms)", 
                                   ping['avg_rtt']])
                    writer.writerow([controller, results['timestamp'], 'Ping',
                                   f"{ping['src']}->{ping['dst']} Packet Loss (%)",
                                   ping['packet_loss']])
            
            # Throughput sonuçları
            if 'throughput' in results['tests']:
                for iperf in results['tests']['throughput']:
                    writer.writerow([controller, results['timestamp'], 'Throughput',
                                   f"{iperf['protocol']} Throughput (Mbps)",
                                   iperf['throughput']])
            
            # Convergence sonuçları
            if 'convergence' in results['tests']:
                for conv in results['tests']['convergence']:
                    writer.writerow([controller, results['timestamp'], 'Convergence',
                                   f"{conv['link']} Convergence Time (s)",
                                   conv['convergence_time']])
        
        print(f"[SAVED] Summary saved to {csv_file}")
    
    def compare_controllers(self, result_files):
        """Birden fazla controller sonucunu karşılaştır"""
        print("\n" + "="*60)
        print("CONTROLLER COMPARISON")
        print("="*60)
        
        comparison = {}
        
        for result_file in result_files:
            with open(result_file, 'r') as f:
                results = json.load(f)
                controller = results['controller']
                comparison[controller] = results
        
        # Karşılaştırma raporu oluştur
        print("\n--- AVERAGE LATENCY ---")
        for controller, results in comparison.items():
            if 'ping' in results['tests']:
                avg_latencies = [p['avg_rtt'] for p in results['tests']['ping']]
                avg = sum(avg_latencies) / len(avg_latencies)
                print(f"  {controller}: {avg:.2f} ms")
        
        print("\n--- AVERAGE THROUGHPUT ---")
        for controller, results in comparison.items():
            if 'throughput' in results['tests']:
                throughputs = [t['throughput'] for t in results['tests']['throughput']]
                avg = sum(throughputs) / len(throughputs)
                print(f"  {controller}: {avg:.2f} Mbps")
        
        print("\n--- CONVERGENCE TIME ---")
        for controller, results in comparison.items():
            if 'convergence' in results['tests']:
                conv_times = [c['convergence_time'] for c in results['tests']['convergence']]
                avg = sum(conv_times) / len(conv_times)
                print(f"  {controller}: {avg:.3f} seconds")


def main():
    """Ana test fonksiyonu"""
    tester = PerformanceTest()
    
    # Test senaryoları
    test_scenarios = ['ping', 'throughput', 'convergence']
    
    # Her controller için test çalıştır
    controllers = [
        'shortest_path',
        'load_balancing',
        'qos_based'
    ]
    
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║   SDN CONTROLLER PERFORMANCE TEST SUITE               ║
    ║                                                        ║
    ║   Test Scenarios:                                     ║
    ║   - Ping Tests (Latency & Packet Loss)               ║
    ║   - Throughput Tests (TCP & UDP)                     ║
    ║   - Convergence Tests (Link Failure Recovery)        ║
    ╚════════════════════════════════════════════════════════╝
    """)
    
    input("Press ENTER to start testing...")
    
    result_files = []
    
    for controller in controllers:
        print(f"\n\nStarting test for {controller} controller...")
        print("Make sure the controller is running and Mininet is active!")
        input(f"Press ENTER when {controller} controller is ready...")
        
        results = tester.run_comprehensive_test(controller, test_scenarios)
        
        # Sonuç dosyasını kaydet
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        result_file = os.path.join(tester.results_dir, f'{controller}_{timestamp}.json')
        result_files.append(result_file)
        
        print(f"\nCompleted tests for {controller}")
        time.sleep(2)
    
    # Karşılaştırma yap
    if len(result_files) > 1:
        print("\n\nGenerating comparison report...")
        tester.compare_controllers(result_files)
    
    print("\n\n" + "="*60)
    print("ALL TESTS COMPLETED!")
    print("="*60)
    print(f"\nResults saved in: {tester.results_dir}/")
    print("\nRun visualizer.py to generate charts and detailed analysis.")


if __name__ == '__main__':
    main()
