import socket
import sys

from core import run_check_wrapper


@run_check_wrapper
def check_dns(servers: str):
    alive_servers = []
    bad_servers = []
    stdout = ''
    for server in servers:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            s.connect((server, 53))
            s.close()
            alive_servers.append(server)
        except socket.error as error:
            stdout += 'DNS {} is NOT available: {}\n'.format(server, error)
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
    print(check_dns(servers))


if __name__ == '__main__':
    main()
