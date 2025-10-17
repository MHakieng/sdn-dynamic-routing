#!/usr/bin/env python3
"""
Karmaşık Topoloji - Gerçekçi Ağ Senaryosu
8 switch, 8 host içeren karmaşık test topolojisi
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController, OVSKernelSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink


class ComplexTopology(Topo):
    """
    Karmaşık 8-switch topolojisi - Gerçek ağ senaryosunu simüle eder
    
           h1---s1---s2---h2
                |\ /|
                | X |
                |/ \|
           h3---s3---s4---h4
                |\ /|
                | X |
                |/ \|
           h5---s5---s6---h5
                |\ /|
                | X |
                |/ \|
           h7---s7---s8---h8
    """
    
    def build(self):
        # Host'ları ekle
        hosts = []
        for i in range(1, 9):
            h = self.addHost(
                f'h{i}',
                ip=f'10.0.0.{i}/24',
                mac=f'00:00:00:00:00:0{i}'
            )
            hosts.append(h)
        
        # Switch'leri ekle
        switches = []
        for i in range(1, 9):
            s = self.addSwitch(
                f's{i}',
                dpid=f'000000000000000{i}'
            )
            switches.append(s)
        
        # Her host'u bir switch'e bağla
        for i in range(8):
            self.addLink(
                hosts[i],
                switches[i],
                bw=100,
                delay='2ms',
                loss=0
            )
        
        # Switch'ler arası bağlantılar - Farklı karakteristikler
        # Yatay bağlantılar (hızlı)
        self.addLink(switches[0], switches[1], bw=100, delay='5ms', loss=0)
        self.addLink(switches[2], switches[3], bw=100, delay='5ms', loss=0)
        self.addLink(switches[4], switches[5], bw=100, delay='5ms', loss=0)
        self.addLink(switches[6], switches[7], bw=100, delay='5ms', loss=0)
        
        # Dikey bağlantılar (orta hız)
        self.addLink(switches[0], switches[2], bw=50, delay='10ms', loss=0)
        self.addLink(switches[1], switches[3], bw=50, delay='10ms', loss=0)
        self.addLink(switches[2], switches[4], bw=50, delay='10ms', loss=0)
        self.addLink(switches[3], switches[5], bw=50, delay='10ms', loss=0)
        self.addLink(switches[4], switches[6], bw=50, delay='10ms', loss=0)
        self.addLink(switches[5], switches[7], bw=50, delay='10ms', loss=0)
        
        # Çapraz bağlantılar (alternatif yollar - daha yavaş)
        self.addLink(switches[0], switches[3], bw=30, delay='20ms', loss=1)
        self.addLink(switches[1], switches[2], bw=30, delay='20ms', loss=1)
        self.addLink(switches[2], switches[5], bw=30, delay='20ms', loss=1)
        self.addLink(switches[3], switches[4], bw=30, delay='20ms', loss=1)
        self.addLink(switches[4], switches[7], bw=30, delay='20ms', loss=1)
        self.addLink(switches[5], switches[6], bw=30, delay='20ms', loss=1)


def run_topology():
    """Topolojiyi başlat ve CLI aç"""
    setLogLevel('info')
    
    topo = ComplexTopology()
    
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
    CLI(net)
    
    info('*** Stopping network\n')
    net.stop()


if __name__ == '__main__':
    run_topology()
