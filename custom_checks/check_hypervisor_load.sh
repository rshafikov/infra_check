#!/bin/bash
. /root/admin-openrc
virt-top --script -n 5 -d 1 --csv /tmp/virt-output.csv
sleep 0.5
if [ ! -e /tmp/check_hypervisor_load.py ]; then
cat > /tmp/check_hypervisor_load.py << EOF
import csv
import subprocess
import socket
import logging
from functools import wraps
import traceback

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='/var/log/infra_check.log',
    filemode='a',
    level=logging.INFO
)


def run_check_wrapper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            logging.info('func {} - OK'.format(func.__name__))
            return func(*args, **kwargs)
        except Exception as error:
            logging.error(('There is an error with {}'.format(func.__name__),
                           'Error: {}'.format(error),
                           'Full error: {}'.format(traceback.format_exc())))
            return 'There is an error with {}'.format(func.__name__)

    return wrapper


@run_check_wrapper
def get_nova_server_list() -> list:
    hostname = socket.gethostname()
    cmd = [
        'nova', 'list',
        '--all-tenants',
        '--host', hostname,
        '--fields', 'instance_name,name'
    ]
    output = subprocess.check_output(cmd).decode('utf-8').split('\n')[3:-1]
    raw_server_list = [
        [item.strip() for item in line.split('|')[1:-1]]
        for line in output]
    return raw_server_list


@run_check_wrapper
def get_and_update_last_screen(
        csv_file_path: str = '/tmp/virt-output.csv') -> dict:
    with open(csv_file_path, 'r') as file:
        screens = [
            upd for upd in csv.DictReader(file, restkey='Hosted')]
    screen = screens[-1]
    vm_count = int(screen.get('Running'))
    hostname = screen.get('Hostname')
    screen_filled = {
        'hostname': hostname,
        '_running': vm_count,
        '_hosted': screen.get('Hosted'),
        'server_list': [
            {
                'hostname': hostname,
                '_domain_name': screen.get('Domain name'),
                '_domain_id': screen.get('Domain ID'),
                'block_read': screen.get('Block RDRQ'),
                'block_write': screen.get('Block WRRQ'),
                'cpu_%': format(
                    float(screen.get('%CPU').replace(',', '.')), '.3f'),
                'ram_%': screen.get('%Mem')
            }]
        }

    if screen_filled['_hosted'] and vm_count > 1:
        hosted = screen_filled.get('_hosted')
        for num in range(0, vm_count-1):
            screen_filled['server_list'].append(
                {
                    'hostname': hostname,
                    '_domain_name': hosted[num*10+1],
                    '_domain_id': hosted[num*10],
                    'block_read': hosted[num*10+6],
                    'block_write': hosted[num*10+7],
                    'cpu_%': format(
                        float(hosted[num*10+3].replace(',', '.')), '.3f'),
                    'ram_%': hosted[num*10+5]
                }
            )
    return screen_filled


@run_check_wrapper
def main():
    nova_server_list = get_nova_server_list()
    screen = get_and_update_last_screen()
    for server in screen['server_list']:
        s_domain_name = server['_domain_name']
        try:
            nova_pair = next(
                s for s in nova_server_list if s[1] == s_domain_name)
        except Exception:
            nova_pair = [
                server.get('_domain_id'), '', server.get('_domain_name')]
        server.update({
            'ID': nova_pair[0],
            'name': nova_pair[2]
        })
        print(
            server['hostname'], server['ID'],
            server['name'], server['block_read'],
            server['block_write'], server['cpu_%'],
            server['ram_%'])


if __name__ == '__main__':
    main()

EOF
fi
sleep 0.5
python3 /tmp/check_hypervisor_load.py > /tmp/hypervisor_load.txt
