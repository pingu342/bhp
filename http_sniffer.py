# -*- coding: utf-8 -*-

from scapy import route
from scapy.all import *

# パケット処理用コールバック関数
def packet_callback(packet):
    if packet[TCP].payload:
        http_packet = str(packet[TCP].payload)
        if "get" in http_packet.lower():
            print "[*] Server: %s" % packet[IP].dst
            print "[*] %s" % packet[TCP].payload

# スニッファーを起動
sniff(filter="tcp port 80", prn=packet_callback, store=0)

