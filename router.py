import scapy.all as scapy

def sniffing(interface: str):
    scapy.sniff(iface=interface,store=False,prn=process_packet)
    # scapy.sniff(filter='port 8000',store=False,prn=process_packet)
    
def process_packet(packet: scapy.packet.Packet):
    # if(packet.haslayer(scapy.Raw)):
    #     print(packet["Raw"].load)
    print(packet)
    
# sniffing('Wi-Fi')
sniffing('lo')