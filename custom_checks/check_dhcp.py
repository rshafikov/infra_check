import json
import time

from scapy.all import IP, UDP, Ether, sniff

from core import run_check_wrapper, save_to_file


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
        return {
            "iface": '{}'.format(iface),
            "message_type": dhcp_info,
            "source": ip_src,
            "destination": ip_dst,
            "cur_time": time.strftime('%I:%M:%S'),
            "ether_src": '{}'.format(ether_src),
            "ether_dst": '{}'.format(ether_dst),
            "preview": 'source ({}:{}) -> dest ({}:{})'.format(
                ip_src, udp_sport, ip_dst, udp_dport)
        }

    except Exception as e:
        return e


@run_check_wrapper
def listen_dhcp_msg():
    stdout = ''
    filter_expr = "port 67 or port 68"
    stdout += ('sniff_start_time: ' + time.strftime("%I:%M:%S") + '\n')
    result = sniff(filter=filter_expr, timeout=20)
    output = [packet_handler(packet) for packet in result]
    dhcp_servers = [
        p['source'] for p in output if p['message_type'] == 'DHCP Ack']
    stdout += ('\n'.join([json.dumps(p, indent=4) for p in output]) + '\n')
    stdout += ('{}\n'.format(result)[1:-1])
    stdout += (
        '\nAvailable {} DHCP: {}'.format(
            len(set(dhcp_servers)), set(dhcp_servers)))
    stdout += '\nsniff_end_time: ' + time.strftime("%I:%M:%S")
    return stdout


if __name__ == '__main__':
    save_to_file(listen_dhcp_msg())
