import json
import logging
import subprocess

from icarus.checks.core import (CONF, PLATFORM, is_check_enabled,
                                run_check_wrapper, save_to_file)

LOG = logging.getLogger(__name__)
LOG.setLevel(CONF.config.get('DEFAULT', 'log_level', fallback='INFO').upper())


PLAT_DEPS = {
    'linux': {
        'cmd': 'ping -c 1 -s {size} -M dont -W 1 {dest_server}',
        'err_codes': {
            1: 'wrong size',
            2: 'check destination server'
        },
        'ok_codes': {
            0: 'OK'
        }
    },
    'darwin': {
        'cmd': 'ping -c 1 -s {size} -D -W 1 {dest_server}',
        'err_codes': {
            2: 'wrong size',
            68: 'check destination server'
        },
        'ok_codes': {
            0: 'OK'
        }
    }
}


@run_check_wrapper
def check_mtu(dest_server, max_size=9000, step=100):
    max_size = int(max_size)
    step = int(step)
    mtu_dict = {
        'DESTINATION': dest_server,
        'OK': [],
        'FAILED': []
    }

    for size in range(max_size, 0, -step):
        cmd = PLAT_DEPS[PLATFORM].get('cmd').format(
            size=str(size - 28), dest_server=dest_server)
        ping_args = {
            'stdout': subprocess.PIPE,
            'stderr': subprocess.PIPE,
            'text': True
        }

        ping = subprocess.run(cmd.split(), **ping_args)
        LOG.debug(
            "cmd: {cmd} c:{code} err: {err} OUT: {out}".format(
                cmd=cmd,
                code=str(ping.returncode),
                err=str(ping.stderr),
                out=str(ping.stdout)),
        )

        if ping.returncode in PLAT_DEPS[PLATFORM]['ok_codes'].keys():
            mtu_dict['OK'].append(
                f"{size}, "
                f"{PLAT_DEPS[PLATFORM]['ok_codes'].get(ping.returncode, 'no such code')}")
        else:
            LOG.debug(
                'one more ping to d:{dest} with s:{size}'.format(
                    dest=dest_server, size=str(size)))
            ping = subprocess.run(cmd.split(), **ping_args)
            LOG.debug(
                "cmd: {cmd} c:{code} err: {err} OUT: {out}".format(
                    cmd=cmd,
                    code=str(ping.returncode),
                    err=str(ping.stderr),
                    out=str(ping.stdout)),
            )
            mtu_dict['FAILED'].append(
                f"{size}, "
                f"{PLAT_DEPS[PLATFORM]['err_codes'].get(ping.returncode, 'no such code')}")
    if mtu_dict['OK'] == [] and mtu_dict['FAILED'] == []:
        raise Exception('ZERO PINGS! TRY TO CHECK DESTINATION SERVER')

    return mtu_dict


def _chose_packet_size(output):
    pass


@is_check_enabled(check_name='check_mtu')
def main_check_ping(conf, check_name, *args, **kwargs):
    dest = conf.config.get('CHECK', 'mtu_dest', fallback='localhost').split()
    size, step = conf.config.get('CHECK', 'mtu_size_step', fallback='9000 100').split()
    result = [check_mtu(d, size, step) for d in dest]
    save_to_file(check_name=check_name, content=json.dumps(result, indent=4))


if __name__ == '__main__':
    main_check_ping()
