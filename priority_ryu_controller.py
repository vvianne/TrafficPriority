from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv4, tcp
from ryu.lib.packet import ether_types

class PriorityApp(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(PriorityApp, self).__init__(*args, **kwargs)
        self.mac_to_port = {}

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        # Install a default flow entry to send all unknown packets to the controller
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)
        self.logger.info("Default flow installed on datapath %s", datapath.id)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        
        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            return

        dst = eth.dst
        src = eth.src
        dpid = datapath.id

        self.mac_to_port.setdefault(dpid, {})

        # Learn MAC address to avoid flooding in the future
        self.mac_to_port[dpid][src] = in_port

        # Check if destination MAC is known
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        # Install flow rule to avoid sending the same packet-in to controller
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
            self.add_flow(datapath, 1, match, actions, msg.buffer_id)

        # Check for TCP traffic to apply priority rules
        if eth.ethertype == ether_types.ETH_TYPE_IP:
            ip_header = pkt.get_protocol(ipv4.ipv4)
            if ip_header.proto == 6:  # TCP
                tcp_header = pkt.get_protocol(tcp.tcp)
                
                # Check for Video traffic (port 5001)
                if tcp_header.dst_port == 5001:
                    match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP,
                                            ip_proto=6,
                                            tcp_dst=5001)
                    actions = [parser.OFPActionOutput(out_port)]
                    self.add_flow(datapath, 20, match, actions)
                    self.logger.info("Video Traffic detected! Priority set to 20")
                    
                # Check for File Transfer traffic (port 5002)
                elif tcp_header.dst_port == 5002:
                    match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP,
                                            ip_proto=6,
                                            tcp_dst=5002)
                    actions = [parser.OFPActionOutput(out_port)]
                    self.add_flow(datapath, 10, match, actions)
                    self.logger.info("File Transfer Traffic detected! Priority set to 10")
        
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)
