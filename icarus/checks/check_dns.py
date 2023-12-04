import json
import logging
import socket

from icarus.checks.core import (CONF, get_values_from_env, is_check_enabled,
                                run_check_wrapper, save_to_file)

LOG = logging.getLogger(__name__)
LOG.setLevel(CONF.config.get('DEFAULT', 'log_level', fallback='INFO').upper())

DNS_CONN_ERR = {
    'ok': 'ok',
    61: 'connection refused',
    8: 'could not resolve',
}


@run_check_wrapper
def check_dns(initrc, pattern):
    servers = _get_dns_from_initrc(initrc, pattern)
    LOG.debug('%s parsed values: %s' % (initrc, servers))
    alive = {}
    for server in servers.values():
        if len(server.split()) > 1:
            alive.update({s: _check_dns(s) for s in server.split()})
            continue
        alive.update({server: _check_dns(server)})

    return alive


def _check_dns(server: str) -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((server, 53))
        s.close()
        return DNS_CONN_ERR['ok']

    except socket.error as error:
        LOG.debug('DNS {} is NOT available: {}\n'.format(server, error))
        return DNS_CONN_ERR.get(error.errno, 'failed')


def _get_dns_from_initrc(initrc_path, ntp_pattern=r'\w+_DNS[0-9]?'):
    return get_values_from_env(
        initrc_path,
        pattern=ntp_pattern
    )


@is_check_enabled(check_name='check_dns')
def main_check_dns(conf, check_name, *args, **kwargs):
    initrc_files = conf.initrc_list
    ntp_pattern = conf.get_regexp('ntp_pattern', r'\w+_DNS[0-9]?')
    result = {path: check_dns(path, ntp_pattern) for path in initrc_files}
    save_to_file(check_name=check_name, content=json.dumps(result, indent=4))


if __name__ == '__main__':
    main_check_dns()
