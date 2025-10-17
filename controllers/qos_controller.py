#!/usr/bin/env python3
"""
QoS-Based Controller
Gecikme ve bant genişliği bazlı kalite odaklı yönlendirme yapan SDN controller
"""

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ether_types, ipv4
from ryu.topology import event
from ryu.topology.api import get_switch, get_link
import networkx as nx
import time
from collections import defaultdict


class QoSController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    
    def __init__(self, *args, **kwargs):
        super(QoSController, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.topology_api_app = self
        self.net = nx.DiGraph()
        self.datapath_list = {}
        
        # QoS metrikleri
        self.link_delay = {}  # (src_dpid, dst_dpid) -> delay (ms)
        self.link_bandwidth = {}  # (src_dpid, dst_dpid) -> bandwidth (Mbps)
        self.link_loss = {}  # (src_dpid, dst_dpid) -> packet loss (%)
        
        # Performans metrikleri
        self.packet_count = 0
        self.flow_install_count = 0
        self.qos_violations = 0
        self.high_priority_flows = 0
        self.start_time = time.time()
        
        self.logger.info("QoS-Based Controller initialized")
    
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        """Switch bağlandığında tablo temizleme ve table-miss kuralı ekle"""
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        self.datapath_list[datapath.id] = datapath
        
        # Table-miss flow entry yükle
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                        ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)
        
        self.logger.info(f"Switch {datapath.id} connected")
    
    def add_flow(self, datapath, priority, match, actions, buffer_id=None, idle_timeout=0, hard_timeout=0):
        """Flow entry ekle"""
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst,
                                    idle_timeout=idle_timeout,
                                    hard_timeout=hard_timeout)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst,
                                    idle_timeout=idle_timeout,
                                    hard_timeout=hard_timeout)
        datapath.send_msg(mod)
        self.flow_install_count += 1
    
    @set_ev_cls(event.EventSwitchEnter)
    def get_topology_data(self, ev):
        """Topoloji bilgisini güncelle ve link QoS özelliklerini ayarla"""
        switch_list = get_switch(self.topology_api_app, None)
        switches = [switch.dp.id for switch in switch_list]
        self.net.add_nodes_from(switches)
        
        links_list = get_link(self.topology_api_app, None)
        
        # Link'leri ekle ve QoS metriklerini ayarla
        for link in links_list:
            src_dpid = link.src.dpid
            dst_dpid = link.dst.dpid
            port = link.src.port_no
            
            # Varsayılan QoS değerleri (gerçek senaryoda ölçüm yapılır)
            # Bu değerler topoloji tanımından da alınabilir
            delay = 10  # ms (varsayılan)
            bandwidth = 100  # Mbps (varsayılan)
            loss = 0.1  # % (varsayılan)
            
            # Link ekle
            self.net.add_edge(src_dpid, dst_dpid, port=port, 
                            delay=delay, bandwidth=bandwidth, loss=loss)
            
            # QoS metriklerini sakla
            self.link_delay[(src_dpid, dst_dpid)] = delay
            self.link_bandwidth[(src_dpid, dst_dpid)] = bandwidth
            self.link_loss[(src_dpid, dst_dpid)] = loss
        
        self.logger.info(f"Topology updated: {len(switches)} switches, {len(links_list)} links")
    
    def calculate_path_qos(self, path):
        """Bir yolun QoS metriklerini hesapla"""
        total_delay = 0
        min_bandwidth = float('inf')
        total_loss = 0
        
        for i in range(len(path) - 1):
            src, dst = path[i], path[i+1]
            total_delay += self.link_delay.get((src, dst), 10)
            min_bandwidth = min(min_bandwidth, self.link_bandwidth.get((src, dst), 100))
            total_loss += self.link_loss.get((src, dst), 0.1)
        
        return {
            'delay': total_delay,
            'bandwidth': min_bandwidth,
            'loss': total_loss
        }
    
    def get_qos_path(self, src, dst, qos_requirement='balanced'):
        """
        QoS gereksinimlerine göre yol hesapla
        qos_requirement: 'low_latency', 'high_bandwidth', 'balanced'
        """
        try:
            # Tüm olası yolları bul (maksimum 5 hop)
            all_paths = list(nx.all_simple_paths(self.net, src, dst, cutoff=5))
            
            if not all_paths:
                return None
            
            # Her yolun QoS metriklerini hesapla
            path_qos = []
            for path in all_paths:
                qos = self.calculate_path_qos(path)
                path_qos.append((path, qos))
            
            # QoS gereksinimlerine göre en iyi yolu seç
            if qos_requirement == 'low_latency':
                # En düşük gecikme
                best_path = min(path_qos, key=lambda x: x[1]['delay'])
                self.logger.info(f"Selected low-latency path with {best_path[1]['delay']}ms delay")
            
            elif qos_requirement == 'high_bandwidth':
                # En yüksek bant genişliği
                best_path = max(path_qos, key=lambda x: x[1]['bandwidth'])
                self.logger.info(f"Selected high-bandwidth path with {best_path[1]['bandwidth']}Mbps")
            
            else:  # balanced
                # Dengeli: düşük gecikme + yüksek bant genişliği + düşük kayıp
                # Normalize edilmiş skorlama
                scores = []
                for path, qos in path_qos:
                    # Her metriği normalize et (0-1 arası)
                    delay_score = 1 / (1 + qos['delay'] / 100)  # Düşük gecikme = yüksek skor
                    bandwidth_score = qos['bandwidth'] / 100  # Yüksek BW = yüksek skor
                    loss_score = 1 / (1 + qos['loss'])  # Düşük kayıp = yüksek skor
                    
                    # Toplam skor (eşit ağırlık)
                    total_score = (delay_score + bandwidth_score + loss_score) / 3
                    scores.append((path, qos, total_score))
                
                best_path = max(scores, key=lambda x: x[2])
                self.logger.info(f"Selected balanced path with score {best_path[2]:.2f}")
                best_path = (best_path[0], best_path[1])
            
            # QoS gereksinimleri karşılanıyor mu kontrol et
            if best_path[1]['delay'] > 100:  # 100ms üzeri
                self.qos_violations += 1
                self.logger.warning(f"QoS violation: High delay {best_path[1]['delay']}ms")
            
            return best_path[0]
        
        except Exception as e:
            self.logger.error(f"Error calculating QoS path: {e}")
            # Hata durumunda basit shortest path
            try:
                return nx.shortest_path(self.net, src, dst)
            except:
                return None
    
    def determine_flow_priority(self, pkt):
        """Paket tipine göre öncelik belirle"""
        # IP paketi kontrolü
        ip_pkt = pkt.get_protocol(ipv4.ipv4)
        if ip_pkt:
            # DSCP (DiffServ) veya port bazlı önceliklendirme
            # Gerçek uygulamada daha detaylı kontrol yapılır
            if ip_pkt.proto == 6:  # TCP
                # Yüksek öncelikli (örn: SSH, HTTP)
                return 'high_bandwidth'
            elif ip_pkt.proto == 17:  # UDP
                # Düşük gecikme (örn: VoIP, gaming)
                return 'low_latency'
        
        return 'balanced'
    
    def install_path(self, path, src_mac, dst_mac, in_port, out_port, priority=1):
        """Hesaplanan yol üzerindeki tüm switch'lere flow rule yükle"""
        if len(path) < 2:
            return
        
        # İlk switch için
        datapath = self.datapath_list[path[0]]
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        match = parser.OFPMatch(in_port=in_port, eth_dst=dst_mac)
        actions = [parser.OFPActionOutput(self.net[path[0]][path[1]]['port'])]
        self.add_flow(datapath, priority, match, actions, idle_timeout=15, hard_timeout=45)
        
        # Ara switch'ler için
        for i in range(1, len(path) - 1):
            datapath = self.datapath_list[path[i]]
            match = parser.OFPMatch(eth_dst=dst_mac)
            actions = [parser.OFPActionOutput(self.net[path[i]][path[i+1]]['port'])]
            self.add_flow(datapath, priority, match, actions, idle_timeout=15, hard_timeout=45)
        
        # Son switch için
        datapath = self.datapath_list[path[-1]]
        match = parser.OFPMatch(eth_dst=dst_mac)
        actions = [parser.OFPActionOutput(out_port)]
        self.add_flow(datapath, priority, match, actions, idle_timeout=15, hard_timeout=45)
        
        self.logger.info(f"QoS path installed: {' -> '.join(map(str, path))}")
    
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        """Packet-In mesajlarını işle"""
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']
        
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        
        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            return
        
        dst = eth.dst
        src = eth.src
        dpid = datapath.id
        
        self.packet_count += 1
        
        # MAC öğrenme
        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][src] = in_port
        
        # Flow önceliğini belirle
        flow_priority_type = self.determine_flow_priority(pkt)
        flow_priority = 2 if flow_priority_type in ['low_latency', 'high_bandwidth'] else 1
        
        if flow_priority > 1:
            self.high_priority_flows += 1
        
        # Hedef MAC biliniyorsa ve topoloji varsa yönlendirme yap
        if dst in [mac for switch in self.mac_to_port.values() for mac in switch]:
            dst_dpid = None
            dst_port = None
            for switch_id, mac_table in self.mac_to_port.items():
                if dst in mac_table:
                    dst_dpid = switch_id
                    dst_port = mac_table[dst]
                    break
            
            if dst_dpid and dpid in self.net and dst_dpid in self.net:
                # QoS bazlı yol hesapla
                path = self.get_qos_path(dpid, dst_dpid, flow_priority_type)
                
                if path:
                    self.install_path(path, src, dst, in_port, dst_port, flow_priority)
                    out_port = self.net[dpid][path[1]]['port'] if len(path) > 1 else dst_port
                else:
                    out_port = ofproto.OFPP_FLOOD
            else:
                out_port = ofproto.OFPP_FLOOD
        else:
            out_port = ofproto.OFPP_FLOOD
        
        # Paketi gönder
        actions = [parser.OFPActionOutput(out_port)]
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data
        
        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)
    
    def get_statistics(self):
        """Performans istatistiklerini döndür"""
        elapsed_time = time.time() - self.start_time
        return {
            'packets_processed': self.packet_count,
            'flows_installed': self.flow_install_count,
            'qos_violations': self.qos_violations,
            'high_priority_flows': self.high_priority_flows,
            'packets_per_second': self.packet_count / elapsed_time if elapsed_time > 0 else 0,
            'elapsed_time': elapsed_time
        }
