#!/usr/bin/env python3
"""
Metrics Collector - SDN performans metriklerini toplar
"""

import time
import json
import os
from datetime import datetime
from collections import defaultdict


class MetricsCollector:
    def __init__(self, controller_name, output_dir='../results'):
        """
        Args:
            controller_name: str - Controller adı
            output_dir: str - Metriklerin kaydedileceği dizin
        """
        self.controller_name = controller_name
        self.output_dir = output_dir
        self.start_time = time.time()
        
        # Metrikler
        self.metrics = {
            'controller': controller_name,
            'start_time': datetime.now().isoformat(),
            'packets': {
                'total': 0,
                'per_second': []
            },
            'flows': {
                'total': 0,
                'active': 0,
                'per_second': []
            },
            'links': {
                'total': 0,
                'active': 0,
                'utilization': defaultdict(float)
            },
            'switches': {
                'connected': 0
            },
            'events': []
        }
        
        os.makedirs(output_dir, exist_ok=True)
    
    def record_packet(self):
        """Paket işlendiğinde kaydet"""
        self.metrics['packets']['total'] += 1
    
    def record_flow(self):
        """Flow kurulduğunda kaydet"""
        self.metrics['flows']['total'] += 1
        self.metrics['flows']['active'] += 1
    
    def record_flow_removal(self):
        """Flow silindiğinde kaydet"""
        if self.metrics['flows']['active'] > 0:
            self.metrics['flows']['active'] -= 1
    
    def record_switch_connection(self):
        """Switch bağlandığında kaydet"""
        self.metrics['switches']['connected'] += 1
        self.record_event('switch_connected', f"Switch connected. Total: {self.metrics['switches']['connected']}")
    
    def record_link_discovery(self, src_dpid, dst_dpid):
        """Link keşfedildiğinde kaydet"""
        self.metrics['links']['total'] += 1
        self.metrics['links']['active'] += 1
        link_id = f"{src_dpid}-{dst_dpid}"
        self.metrics['links']['utilization'][link_id] = 0.0
        self.record_event('link_discovered', f"Link discovered: {link_id}")
    
    def update_link_utilization(self, src_dpid, dst_dpid, utilization):
        """Link kullanımını güncelle"""
        link_id = f"{src_dpid}-{dst_dpid}"
        self.metrics['links']['utilization'][link_id] = utilization
    
    def record_event(self, event_type, description):
        """Olay kaydet"""
        self.metrics['events'].append({
            'timestamp': datetime.now().isoformat(),
            'type': event_type,
            'description': description
        })
    
    def calculate_rates(self):
        """Saniye başına oranları hesapla"""
        elapsed = time.time() - self.start_time
        
        if elapsed > 0:
            pps = self.metrics['packets']['total'] / elapsed
            fps = self.metrics['flows']['total'] / elapsed
            
            self.metrics['packets']['per_second'].append(pps)
            self.metrics['flows']['per_second'].append(fps)
            
            return {
                'packets_per_second': pps,
                'flows_per_second': fps
            }
        
        return {'packets_per_second': 0, 'flows_per_second': 0}
    
    def get_summary(self):
        """Özet istatistikleri döndür"""
        elapsed = time.time() - self.start_time
        rates = self.calculate_rates()
        
        return {
            'controller': self.controller_name,
            'uptime': elapsed,
            'packets_processed': self.metrics['packets']['total'],
            'packets_per_second': rates['packets_per_second'],
            'flows_installed': self.metrics['flows']['total'],
            'flows_active': self.metrics['flows']['active'],
            'switches_connected': self.metrics['switches']['connected'],
            'links_discovered': self.metrics['links']['total']
        }
    
    def save_metrics(self):
        """Metrikleri dosyaya kaydet"""
        self.metrics['end_time'] = datetime.now().isoformat()
        self.metrics['duration'] = time.time() - self.start_time
        
        # Link utilization dict'i liste'ye çevir (JSON serialization için)
        self.metrics['links']['utilization'] = dict(self.metrics['links']['utilization'])
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.controller_name}_metrics_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        
        print(f"Metrics saved to: {filepath}")
        return filepath
    
    def print_summary(self):
        """Özet istatistikleri yazdır"""
        summary = self.get_summary()
        
        print("\n" + "="*60)
        print(f"METRICS SUMMARY - {self.controller_name}")
        print("="*60)
        print(f"Uptime:              {summary['uptime']:.2f} seconds")
        print(f"Packets Processed:   {summary['packets_processed']}")
        print(f"Packets/sec:         {summary['packets_per_second']:.2f}")
        print(f"Flows Installed:     {summary['flows_installed']}")
        print(f"Active Flows:        {summary['flows_active']}")
        print(f"Switches Connected:  {summary['switches_connected']}")
        print(f"Links Discovered:    {summary['links_discovered']}")
        print("="*60 + "\n")


# Test için
if __name__ == '__main__':
    collector = MetricsCollector('TestController')
    
    # Simüle edilmiş metrikler
    for i in range(100):
        collector.record_packet()
        if i % 10 == 0:
            collector.record_flow()
    
    collector.record_switch_connection()
    collector.record_switch_connection()
    collector.record_link_discovery(1, 2)
    collector.record_link_discovery(2, 3)
    collector.update_link_utilization(1, 2, 45.5)
    
    time.sleep(1)
    
    collector.print_summary()
    collector.save_metrics()
