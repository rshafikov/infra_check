import json
import logging
import socket
import struct
import time
from socket import AF_INET, SOCK_DGRAM

from core import (CONF, get_values_from_env, is_check_enabled,
                  run_check_wrapper, save_to_file)

LOG = logging.getLogger(__name__)
LOG.setLevel(CONF.config.get('DEFAULT', 'log_level', fallback='INFO').upper())


def _get_ntp_time(host='pool.ntp.org'):
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


def _get_ntp_from_initrc(initrc_path, ntp_pattern=r'\w+_NTP[0-9]?'):
    return get_values_from_env(
            initrc_path,
            pattern=ntp_pattern)


@run_check_wrapper
def check_ntp(initrc, pattern):
    servers = _get_ntp_from_initrc(initrc, pattern)
    LOG.debug('%s parsed values: %s' % (initrc, servers))
    alive_servers = []
    time_list = {}
    bad_servers = []
    for server in servers.values():
        try:
            time_list.setdefault(server, _get_ntp_time(server))
            alive_servers.append(server)
        except Exception as error:
            bad_servers.append(server)
    return {
        'availability': f'Available {str(len(alive_servers))} from {str(len(servers))}',
        'available_servers': ', '.join(alive_servers),
        'problem_servers': ', '.join(bad_servers) if bad_servers else 'not found'
    }


@is_check_enabled(check_name='check_ntp')
def main_check_ntp(conf, check_name, *args, **kwargs):
    initrc_files = conf.initrc_list
    ntp_pattern = conf.get_regexp('ntp_pattern', r'\w+_NTP[0-9]?')
    result = {path: check_ntp(path, ntp_pattern) for path in initrc_files}
    save_to_file(check_name=check_name, content=json.dumps(result, indent=4))


if __name__ == '__main__':
    main_check_ntp()
