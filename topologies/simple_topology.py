#!/usr/bin/env python3
"""
Basit Topoloji - SDN Yönlendirme Test Ortamı
4 switch, 4 host içeren temel test topolojisi
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController, OVSKernelSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink


class SimpleTopology(Topo):
    """
    Basit 4-switch topolojisi:
    
    h1 --- s1 --- s2 --- h2
            |  \ /  |
            |   X   |
            |  / \  |
    h3 --- s3 --- s4 --- h4
    """
    
    def build(self):
        # Host'ları ekle
        h1 = self.addHost('h1', ip='10.0.0.1/24', mac='00:00:00:00:00:01')
        h2 = self.addHost('h2', ip='10.0.0.2/24', mac='00:00:00:00:00:02')
        h3 = self.addHost('h3', ip='10.0.0.3/24', mac='00:00:00:00:00:03')
        h4 = self.addHost('h4', ip='10.0.0.4/24', mac='00:00:00:00:00:04')
        
        # Switch'leri ekle
        s1 = self.addSwitch('s1', dpid='0000000000000001')
        s2 = self.addSwitch('s2', dpid='0000000000000002')
        s3 = self.addSwitch('s3', dpid='0000000000000003')
        s4 = self.addSwitch('s4', dpid='0000000000000004')
        
        # Host-Switch bağlantıları
        self.addLink(h1, s1, bw=100, delay='5ms')
        self.addLink(h2, s2, bw=100, delay='5ms')
        self.addLink(h3, s3, bw=100, delay='5ms')
        self.addLink(h4, s4, bw=100, delay='5ms')
        
        # Switch-Switch bağlantıları (mesh benzeri yapı)
        self.addLink(s1, s2, bw=50, delay='10ms')  # Yüksek bant genişliği
        self.addLink(s1, s3, bw=30, delay='15ms')  # Orta bant genişliği
        self.addLink(s1, s4, bw=20, delay='20ms')  # Düşük bant genişliği
        self.addLink(s2, s4, bw=40, delay='12ms')
        self.addLink(s3, s4, bw=35, delay='18ms')
        self.addLink(s2, s3, bw=25, delay='25ms')  # Uzun gecikme


def run_topology():
    """Topolojiyi başlat ve CLI aç"""
    setLogLevel('info')
    
    topo = SimpleTopology()
    
    # Mininet ağını oluştur
    net = Mininet(
        topo=topo,
        controller=lambda name: RemoteController(
            name, ip='127.0.0.1', port=6653
        ),
        switch=OVSKernelSwitch,
        link=TCLink,
        autoSetMacs=True,
        autoStaticArp=True
    )
    
    info('*** Starting network\n')
    net.start()
    
    info('*** Testing connectivity\n')
    net.pingAll()
    
    info('*** Running CLI\n')
    info('*** Kullanılabilir komutlar:\n')
    info('    pingall - Tüm hostlar arasında ping testi\n')
    info('    iperf h1 h2 - h1 ve h2 arasında bant genişliği testi\n')
    info('    h1 ping -c 10 h2 - 10 ping paketi gönder\n')
    info('    link s1 s2 down - Link\'i devre dışı bırak\n')
    info('    link s1 s2 up - Link\'i tekrar aç\n')
    
    CLI(net)
    
    info('*** Stopping network\n')
    net.stop()


if __name__ == '__main__':
    run_topology()
