from scapy.all import sniff, Ether, IP, UDP
import time
import json


def packet_handler(packet):
    try:
        ether_src = packet[Ether].src
        ether_dst = packet[Ether].dst
        ip_src = packet[IP].src
        ip_dst = packet[IP].dst
        udp_sport = packet[UDP].sport
        udp_dport = packet[UDP].dport
        dhcp_info = packet.summary().split('/')[-1].strip()
        iface = packet.sniffed_on
        dict_represent = {
            "iface": '{}'.format(iface),
            "message_type": dhcp_info,
            "direction": 'source ({}:{}) -> dest ({}:{})'.format(
                ip_src, udp_sport, ip_dst, udp_dport),
            "cur_time": time.strftime('%I:%M:%S'),
            "ether_src": '{}'.format(ether_src),
            "ether_dst": '{}'.format(ether_dst)
        }
        return json.dumps(dict_represent, indent=4)

    except Exception as e:
        return e


def listen_dhcp_msg():
    filter_expr = "port 67 or port 68"
    print('start_time: ' + time.strftime("%I:%M:%S"))
    result = sniff(filter=filter_expr, prn=packet_handler, timeout=20)
    print('{}'.format(result)[1:-1])
    print('end_time: ' + time.strftime("%I:%M:%S"))


if __name__ == '__main__':
    listen_dhcp_msg()
