import requests
import sys

from core import run_check_wrapper


@run_check_wrapper
def check_san(servers):
    stdout = ''
    alive_servers = []
    bad_servers = []
    for server in servers:
        try:
            http_response = requests.get(
                "http://{}/".format(server), verify=False, timeout=3)
            http_status = http_response.status_code
        except Exception:
            http_status = 500
        try:
            https_response = requests.get(
                "https://{}/".format(server), verify=False, timeout=3)
            https_status = https_response.status_code
        except Exception:
            https_status = 500
        if http_status == 200 or https_status == 200:
            alive_servers.append(server)
        else:
            bad_servers.append(server)
            stdout += "SAN is not available at {}\n".format(server)
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
    print(check_san(servers))


if __name__ == '__main__':
    main()
