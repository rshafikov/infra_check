import socket
import struct
import sys
import time
from socket import AF_INET, SOCK_DGRAM

from core import run_check_wrapper


def get_ntp_time(host='pool.ntp.org'):
    port = 123
    buf = 1024
    address = (host, port)
    msg = '\x1b' + 47 * '\0'
    time_since_1970 = 2208988800
    socket.setdefaulttimeout(2)
    client = socket.socket(AF_INET, SOCK_DGRAM)
    client.sendto(msg.encode('utf-8'), address)
    msg, address = client.recvfrom(buf)
    t = struct.unpack('!12I', msg)[10]
    t -= time_since_1970
    return time.ctime(t).replace('  ', ' ')


@run_check_wrapper
def check_ntp(servers):
    alive_servers = []
    time_list = {}
    bad_servers = []
    stdout = ''
    for server in servers:
        try:
            time_list.setdefault(server, get_ntp_time(server))
            alive_servers.append(server)
        except Exception as error:
            stdout += 'NTP {} is NOT available: {}\n'.format(server, error)
            bad_servers.append(server)
    if bad_servers:
        stdout += 'Problem servers: {}\n'.format(', '.join(bad_servers))
    stdout += (
        'Available {} from {}: '
        '{}'.format(len(alive_servers), str(len(servers)), alive_servers)
    )
    return stdout


def main():
    read = sys.stdin.readline()
    servers = [server for server in read.split()]
    print(check_ntp(servers))


if __name__ == '__main__':
    main()
