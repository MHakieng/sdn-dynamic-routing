#!/usr/bin/env python3
"""
Visualizer - Test sonuçlarını görselleştirir ve analiz eder
"""

import json
import os
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # GUI olmadan çalışma
import numpy as np
from datetime import datetime
import pandas as pd


class ResultVisualizer:
    def __init__(self, results_dir='../results'):
        self.results_dir = results_dir
        self.results = {}
    
    def load_results(self, result_files=None):
        """JSON sonuç dosyalarını yükle"""
        if result_files is None:
            # Results dizinindeki tüm JSON dosyalarını yükle
            result_files = [
                os.path.join(self.results_dir, f) 
                for f in os.listdir(self.results_dir) 
                if f.endswith('.json')
            ]
        
        print(f"Loading {len(result_files)} result files...")
        
        for file_path in result_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    controller_name = data['controller']
                    
                    if controller_name not in self.results:
                        self.results[controller_name] = []
                    
                    self.results[controller_name].append(data)
                    print(f"  Loaded: {os.path.basename(file_path)}")
            except Exception as e:
                print(f"  Error loading {file_path}: {e}")
        
        print(f"\nLoaded results for {len(self.results)} controllers")
    
    def extract_metrics(self):
        """Her controller için metrikleri çıkar"""
        metrics = {}
        
        for controller, result_list in self.results.items():
            metrics[controller] = {
                'latency': [],
                'throughput': [],
                'packet_loss': [],
                'convergence_time': []
            }
            
            for result in result_list:
                # Ping metrikleri
                if 'ping' in result.get('tests', {}):
                    for ping in result['tests']['ping']:
                        metrics[controller]['latency'].append(ping['avg_rtt'])
                        metrics[controller]['packet_loss'].append(ping['packet_loss'])
                
                # Throughput metrikleri
                if 'throughput' in result.get('tests', {}):
                    for tp in result['tests']['throughput']:
                        metrics[controller]['throughput'].append(tp['throughput'])
                
                # Convergence metrikleri
                if 'convergence' in result.get('tests', {}):
                    for conv in result['tests']['convergence']:
                        metrics[controller]['convergence_time'].append(conv['convergence_time'])
        
        return metrics
    
    def plot_latency_comparison(self, metrics, output_file='latency_comparison.png'):
        """Gecikme karşılaştırma grafiği"""
        plt.figure(figsize=(12, 6))
        
        controllers = list(metrics.keys())
        latencies = [metrics[c]['latency'] for c in controllers]
        
        # Box plot
        plt.subplot(1, 2, 1)
        bp = plt.boxplot(latencies, labels=controllers, patch_artist=True)
        
        # Renklendirme
        colors = ['lightblue', 'lightgreen', 'lightcoral']
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
        
        plt.ylabel('Latency (ms)')
        plt.title('Latency Comparison (Box Plot)')
        plt.grid(axis='y', alpha=0.3)
        
        # Bar chart (ortalama)
        plt.subplot(1, 2, 2)
        avg_latencies = [np.mean(lat) if lat else 0 for lat in latencies]
        std_latencies = [np.std(lat) if lat else 0 for lat in latencies]
        
        x_pos = np.arange(len(controllers))
        bars = plt.bar(x_pos, avg_latencies, yerr=std_latencies, 
                      capsize=5, color=colors, alpha=0.7)
        
        plt.xlabel('Controller')
        plt.ylabel('Average Latency (ms)')
        plt.title('Average Latency with Std Dev')
        plt.xticks(x_pos, controllers)
        plt.grid(axis='y', alpha=0.3)
        
        # Değerleri bar üzerine yaz
        for i, (bar, val) in enumerate(zip(bars, avg_latencies)):
            plt.text(bar.get_x() + bar.get_width()/2, val + std_latencies[i],
                    f'{val:.1f}ms', ha='center', va='bottom')
        
        plt.tight_layout()
        output_path = os.path.join(self.results_dir, output_file)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_path}")
        plt.close()
    
    def plot_throughput_comparison(self, metrics, output_file='throughput_comparison.png'):
        """Throughput karşılaştırma grafiği"""
        plt.figure(figsize=(12, 6))
        
        controllers = list(metrics.keys())
        throughputs = [metrics[c]['throughput'] for c in controllers]
        
        # Violin plot
        plt.subplot(1, 2, 1)
        parts = plt.violinplot(throughputs, positions=range(len(controllers)), 
                              showmeans=True, showmedians=True)
        
        plt.ylabel('Throughput (Mbps)')
        plt.title('Throughput Distribution (Violin Plot)')
        plt.xticks(range(len(controllers)), controllers)
        plt.grid(axis='y', alpha=0.3)
        
        # Bar chart
        plt.subplot(1, 2, 2)
        avg_throughputs = [np.mean(tp) if tp else 0 for tp in throughputs]
        max_throughputs = [np.max(tp) if tp else 0 for tp in throughputs]
        
        x_pos = np.arange(len(controllers))
        width = 0.35
        
        colors = ['#2E86AB', '#A23B72']
        bars1 = plt.bar(x_pos - width/2, avg_throughputs, width, 
                       label='Average', color=colors[0], alpha=0.7)
        bars2 = plt.bar(x_pos + width/2, max_throughputs, width,
                       label='Maximum', color=colors[1], alpha=0.7)
        
        plt.xlabel('Controller')
        plt.ylabel('Throughput (Mbps)')
        plt.title('Average vs Maximum Throughput')
        plt.xticks(x_pos, controllers)
        plt.legend()
        plt.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        output_path = os.path.join(self.results_dir, output_file)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_path}")
        plt.close()
    
    def plot_packet_loss(self, metrics, output_file='packet_loss_comparison.png'):
        """Paket kaybı karşılaştırması"""
        plt.figure(figsize=(10, 6))
        
        controllers = list(metrics.keys())
        packet_losses = [metrics[c]['packet_loss'] for c in controllers]
        
        avg_losses = [np.mean(pl) if pl else 0 for pl in packet_losses]
        
        colors = ['#06A77D', '#F77F00', '#D62828']
        bars = plt.bar(controllers, avg_losses, color=colors, alpha=0.7)
        
        plt.ylabel('Packet Loss (%)')
        plt.title('Average Packet Loss Comparison')
        plt.grid(axis='y', alpha=0.3)
        
        # Değerleri bar üzerine yaz
        for bar, val in zip(bars, avg_losses):
            plt.text(bar.get_x() + bar.get_width()/2, val,
                    f'{val:.2f}%', ha='center', va='bottom')
        
        # Referans çizgisi (kabul edilebilir maksimum)
        plt.axhline(y=1.0, color='r', linestyle='--', label='Threshold (1%)', alpha=0.5)
        plt.legend()
        
        plt.tight_layout()
        output_path = os.path.join(self.results_dir, output_file)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_path}")
        plt.close()
    
    def plot_convergence_time(self, metrics, output_file='convergence_comparison.png'):
        """Convergence time karşılaştırması"""
        plt.figure(figsize=(10, 6))
        
        controllers = list(metrics.keys())
        conv_times = [metrics[c]['convergence_time'] for c in controllers]
        
        avg_conv = [np.mean(ct) * 1000 if ct else 0 for ct in conv_times]  # ms'ye çevir
        
        colors = ['#4ECDC4', '#FF6B6B', '#FFE66D']
        bars = plt.bar(controllers, avg_conv, color=colors, alpha=0.7)
        
        plt.ylabel('Convergence Time (ms)')
        plt.title('Average Convergence Time (Link Failure Recovery)')
        plt.grid(axis='y', alpha=0.3)
        
        # Değerleri bar üzerine yaz
        for bar, val in zip(bars, avg_conv):
            plt.text(bar.get_x() + bar.get_width()/2, val,
                    f'{val:.0f}ms', ha='center', va='bottom')
        
        plt.tight_layout()
        output_path = os.path.join(self.results_dir, output_file)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_path}")
        plt.close()
    
    def plot_radar_chart(self, metrics, output_file='radar_comparison.png'):
        """Radar chart ile genel karşılaştırma"""
        plt.figure(figsize=(10, 10))
        
        controllers = list(metrics.keys())
        
        # Metrikleri normalize et (0-100 arası)
        categories = ['Low Latency', 'High Throughput', 'Low Packet Loss', 
                     'Fast Convergence', 'Stability']
        
        scores = {}
        for controller in controllers:
            # Latency (düşük iyi): 0-50ms arası, ters skala
            avg_lat = np.mean(metrics[controller]['latency']) if metrics[controller]['latency'] else 25
            lat_score = max(0, 100 - (avg_lat / 50 * 100))
            
            # Throughput (yüksek iyi): 0-100 Mbps arası
            avg_tp = np.mean(metrics[controller]['throughput']) if metrics[controller]['throughput'] else 50
            tp_score = min(100, (avg_tp / 100) * 100)
            
            # Packet Loss (düşük iyi): 0-5% arası, ters skala
            avg_loss = np.mean(metrics[controller]['packet_loss']) if metrics[controller]['packet_loss'] else 1
            loss_score = max(0, 100 - (avg_loss / 5 * 100))
            
            # Convergence (hızlı iyi): 0-5s arası, ters skala
            avg_conv = np.mean(metrics[controller]['convergence_time']) if metrics[controller]['convergence_time'] else 1.5
            conv_score = max(0, 100 - (avg_conv / 5 * 100))
            
            # Stability (varyasyon düşük iyi)
            lat_std = np.std(metrics[controller]['latency']) if len(metrics[controller]['latency']) > 1 else 5
            stability_score = max(0, 100 - (lat_std / 20 * 100))
            
            scores[controller] = [lat_score, tp_score, loss_score, conv_score, stability_score]
        
        # Radar chart çiz
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]  # Döngüyü kapat
        
        ax = plt.subplot(111, polar=True)
        
        colors = ['#FF6B6B', '#4ECDC4', '#FFE66D']
        
        for i, (controller, score_list) in enumerate(scores.items()):
            score_list += score_list[:1]  # Döngüyü kapat
            ax.plot(angles, score_list, 'o-', linewidth=2, 
                   label=controller, color=colors[i])
            ax.fill(angles, score_list, alpha=0.15, color=colors[i])
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(['20', '40', '60', '80', '100'])
        ax.grid(True)
        
        plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        plt.title('Controller Performance Radar Chart\n(Higher is Better)', 
                 size=14, pad=20)
        
        plt.tight_layout()
        output_path = os.path.join(self.results_dir, output_file)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_path}")
        plt.close()
    
    def generate_summary_report(self, metrics, output_file='analysis_report.txt'):
        """Özet rapor oluştur"""
        output_path = os.path.join(self.results_dir, output_file)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("SDN CONTROLLER PERFORMANCE ANALYSIS REPORT\n")
            f.write("="*70 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for controller in metrics.keys():
                f.write(f"\n{'='*70}\n")
                f.write(f"CONTROLLER: {controller.upper()}\n")
                f.write(f"{'='*70}\n\n")
                
                # Latency analizi
                if metrics[controller]['latency']:
                    lats = metrics[controller]['latency']
                    f.write(f"LATENCY METRICS:\n")
                    f.write(f"  Average: {np.mean(lats):.2f} ms\n")
                    f.write(f"  Minimum: {np.min(lats):.2f} ms\n")
                    f.write(f"  Maximum: {np.max(lats):.2f} ms\n")
                    f.write(f"  Std Dev: {np.std(lats):.2f} ms\n")
                    f.write(f"  Median:  {np.median(lats):.2f} ms\n\n")
                
                # Throughput analizi
                if metrics[controller]['throughput']:
                    tps = metrics[controller]['throughput']
                    f.write(f"THROUGHPUT METRICS:\n")
                    f.write(f"  Average: {np.mean(tps):.2f} Mbps\n")
                    f.write(f"  Minimum: {np.min(tps):.2f} Mbps\n")
                    f.write(f"  Maximum: {np.max(tps):.2f} Mbps\n")
                    f.write(f"  Std Dev: {np.std(tps):.2f} Mbps\n\n")
                
                # Packet loss analizi
                if metrics[controller]['packet_loss']:
                    losses = metrics[controller]['packet_loss']
                    f.write(f"PACKET LOSS METRICS:\n")
                    f.write(f"  Average: {np.mean(losses):.3f} %\n")
                    f.write(f"  Maximum: {np.max(losses):.3f} %\n\n")
                
                # Convergence analizi
                if metrics[controller]['convergence_time']:
                    convs = metrics[controller]['convergence_time']
                    f.write(f"CONVERGENCE METRICS:\n")
                    f.write(f"  Average: {np.mean(convs)*1000:.2f} ms\n")
                    f.write(f"  Minimum: {np.min(convs)*1000:.2f} ms\n")
                    f.write(f"  Maximum: {np.max(convs)*1000:.2f} ms\n\n")
            
            # Karşılaştırma özeti
            f.write(f"\n{'='*70}\n")
            f.write("COMPARISON SUMMARY\n")
            f.write(f"{'='*70}\n\n")
            
            # En iyi performans gösteren
            best_latency = min(metrics.keys(), 
                             key=lambda x: np.mean(metrics[x]['latency']) if metrics[x]['latency'] else float('inf'))
            best_throughput = max(metrics.keys(),
                                key=lambda x: np.mean(metrics[x]['throughput']) if metrics[x]['throughput'] else 0)
            best_convergence = min(metrics.keys(),
                                 key=lambda x: np.mean(metrics[x]['convergence_time']) if metrics[x]['convergence_time'] else float('inf'))
            
            f.write(f"Best Latency Performance:     {best_latency}\n")
            f.write(f"Best Throughput Performance:  {best_throughput}\n")
            f.write(f"Best Convergence Performance: {best_convergence}\n\n")
            
            f.write("\nRECOMMENDATIONS:\n")
            f.write("-" * 70 + "\n")
            f.write(f"• For latency-sensitive applications: Use {best_latency}\n")
            f.write(f"• For bandwidth-intensive applications: Use {best_throughput}\n")
            f.write(f"• For dynamic networks (frequent topology changes): Use {best_convergence}\n")
        
        print(f"Saved: {output_path}")
    
    def generate_all_visualizations(self):
        """Tüm görselleştirmeleri oluştur"""
        print("\n" + "="*60)
        print("GENERATING VISUALIZATIONS")
        print("="*60 + "\n")
        
        metrics = self.extract_metrics()
        
        if not any(metrics.values()):
            print("No metrics found in results!")
            return
        
        print("Creating charts...")
        self.plot_latency_comparison(metrics)
        self.plot_throughput_comparison(metrics)
        self.plot_packet_loss(metrics)
        self.plot_convergence_time(metrics)
        self.plot_radar_chart(metrics)
        
        print("\nGenerating text report...")
        self.generate_summary_report(metrics)
        
        print("\n" + "="*60)
        print("VISUALIZATION COMPLETE!")
        print("="*60)
        print(f"\nAll files saved in: {self.results_dir}/")


def main():
    """Ana fonksiyon"""
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║   SDN PERFORMANCE VISUALIZER & ANALYZER               ║
    ║                                                        ║
    ║   This tool generates:                                ║
    ║   • Latency comparison charts                         ║
    ║   • Throughput analysis                               ║
    ║   • Packet loss graphs                                ║
    ║   • Convergence time comparison                       ║
    ║   • Radar chart (overall performance)                 ║
    ║   • Detailed text report                              ║
    ╚════════════════════════════════════════════════════════╝
    """)
    
    visualizer = ResultVisualizer()
    
    # Sonuçları yükle
    visualizer.load_results()
    
    if not visualizer.results:
        print("\nNo result files found in results/ directory!")
        print("Please run performance_test.py first to generate test results.")
        return
    
    # Görselleştirmeleri oluştur
    visualizer.generate_all_visualizations()
    
    print("\n✓ Analysis complete! Check the results/ directory for charts and reports.")


if __name__ == '__main__':
    main()
