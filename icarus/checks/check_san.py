import requests

from icarus.checks.core import (is_check_enabled, run_check_wrapper,
                                save_to_file)


class NoSANSetupError(Exception):
    pass


@run_check_wrapper
def check_san(servers=None, conf=None):
    if not servers:
        servers = conf.config.get(
            'DEFAULT', 'san_servers', fallback='Please setup SAN servers for this check')
        if servers == 'Please setup SAN servers for this check':
            raise NoSANSetupError(servers)
        servers = servers.split(', ') if ',' in servers else servers.split()
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
        stdout += 'Problem servers: {}\n'.format(','.join(bad_servers))
    stdout += (
        'Available {} from {}: '
        '{}'.format(len(alive_servers), str(len(servers)), alive_servers)
    )
    return stdout


@is_check_enabled(check_name='check_san')
def main_check_san(conf, check_name, inp=None):
    servers = None
    if inp:
        inp = input('enter ip:\n')
        servers = [server for server in inp.split()]

    save_to_file(check_name, check_san(servers=servers, conf=conf))


if __name__ == '__main__':
    main_check_san(inp=False)
