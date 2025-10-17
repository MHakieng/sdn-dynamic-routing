#!/usr/bin/env python3
"""
Load Balancing Controller
Yük dengeleme tabanlı dinamik yönlendirme yapan SDN controller
Trafik yükünü dengeleyerek optimal yol seçer
"""

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ether_types
from ryu.topology import event
from ryu.topology.api import get_switch, get_link
import networkx as nx
import time
from collections import defaultdict


class LoadBalancingController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    
    def __init__(self, *args, **kwargs):
        super(LoadBalancingController, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.topology_api_app = self
        self.net = nx.DiGraph()
        self.datapath_list = {}
        
        # Yük takibi için
        self.link_load = defaultdict(int)  # (src_dpid, dst_dpid) -> load
        self.link_capacity = {}  # (src_dpid, dst_dpid) -> capacity
        
        # Performans metrikleri
        self.packet_count = 0
        self.flow_install_count = 0
        self.path_calculations = 0
        self.load_balanced_paths = 0
        self.start_time = time.time()
        
        self.logger.info("Load Balancing Controller initialized")
    
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
        """Topoloji bilgisini güncelle"""
        switch_list = get_switch(self.topology_api_app, None)
        switches = [switch.dp.id for switch in switch_list]
        self.net.add_nodes_from(switches)
        
        links_list = get_link(self.topology_api_app, None)
        
        # Link'leri ekle ve kapasitelerini ayarla
        for link in links_list:
            src_dpid = link.src.dpid
            dst_dpid = link.dst.dpid
            port = link.src.port_no
            
            # Link ekle (ağırlık = mevcut yük)
            self.net.add_edge(src_dpid, dst_dpid, port=port, weight=0)
            
            # Varsayılan kapasite (Mbps cinsinden)
            self.link_capacity[(src_dpid, dst_dpid)] = 100
        
        self.logger.info(f"Topology updated: {len(switches)} switches, {len(links_list)} links")
    
    def update_link_weight(self, src, dst, load):
        """Link ağırlığını yüke göre güncelle"""
        if self.net.has_edge(src, dst):
            capacity = self.link_capacity.get((src, dst), 100)
            # Yük oranına göre ağırlık (0-1 arası normalize)
            utilization = min(load / capacity, 1.0)
            # Yüksek yük = yüksek ağırlık (maliyet)
            weight = 1 + (utilization * 10)  # 1-11 arası değer
            self.net[src][dst]['weight'] = weight
            self.link_load[(src, dst)] = load
    
    def get_least_loaded_path(self, src, dst):
        """En az yüklü yolu hesapla (ağırlıklı shortest path)"""
        try:
            self.path_calculations += 1
            
            # Tüm olası yolları bul
            all_paths = list(nx.all_simple_paths(self.net, src, dst, cutoff=5))
            
            if not all_paths:
                return None
            
            # Her yolun toplam yükünü hesapla
            path_loads = []
            for path in all_paths:
                total_load = 0
                for i in range(len(path) - 1):
                    load = self.link_load.get((path[i], path[i+1]), 0)
                    total_load += load
                path_loads.append((path, total_load))
            
            # En az yüklü yolu seç
            best_path = min(path_loads, key=lambda x: x[1])
            
            if best_path[1] < min(path_loads, key=lambda x: x[1])[1] * 1.5:
                self.load_balanced_paths += 1
            
            return best_path[0]
        except:
            # Hata durumunda basit shortest path
            try:
                return nx.shortest_path(self.net, src, dst)
            except:
                return None
    
    def install_path(self, path, src_mac, dst_mac, in_port, out_port):
        """Hesaplanan yol üzerindeki tüm switch'lere flow rule yükle"""
        if len(path) < 2:
            return
        
        # Yol üzerindeki linklerin yükünü artır
        for i in range(len(path) - 1):
            self.link_load[(path[i], path[i+1])] += 1
            self.update_link_weight(path[i], path[i+1], self.link_load[(path[i], path[i+1])])
        
        # İlk switch için
        datapath = self.datapath_list[path[0]]
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        match = parser.OFPMatch(in_port=in_port, eth_dst=dst_mac)
        actions = [parser.OFPActionOutput(self.net[path[0]][path[1]]['port'])]
        self.add_flow(datapath, 1, match, actions, idle_timeout=10, hard_timeout=30)
        
        # Ara switch'ler için
        for i in range(1, len(path) - 1):
            datapath = self.datapath_list[path[i]]
            match = parser.OFPMatch(eth_dst=dst_mac)
            actions = [parser.OFPActionOutput(self.net[path[i]][path[i+1]]['port'])]
            self.add_flow(datapath, 1, match, actions, idle_timeout=10, hard_timeout=30)
        
        # Son switch için
        datapath = self.datapath_list[path[-1]]
        match = parser.OFPMatch(eth_dst=dst_mac)
        actions = [parser.OFPActionOutput(out_port)]
        self.add_flow(datapath, 1, match, actions, idle_timeout=10, hard_timeout=30)
        
        self.logger.info(f"Load-balanced path installed: {' -> '.join(map(str, path))}")
    
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
                # En az yüklü yolu hesapla
                path = self.get_least_loaded_path(dpid, dst_dpid)
                
                if path:
                    self.install_path(path, src, dst, in_port, dst_port)
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
            'path_calculations': self.path_calculations,
            'load_balanced_paths': self.load_balanced_paths,
            'packets_per_second': self.packet_count / elapsed_time if elapsed_time > 0 else 0,
            'elapsed_time': elapsed_time,
            'average_link_load': sum(self.link_load.values()) / len(self.link_load) if self.link_load else 0
        }
