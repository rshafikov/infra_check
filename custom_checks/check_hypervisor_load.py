import csv
import json
import logging
import multiprocessing
import os
import socket
import subprocess
import traceback
from functools import wraps

from keystoneauth1 import loading, session
from keystoneclient import client
from novaclient import client as nova_client

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
def load_env(file_path='/root/admin-openrc'):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and line.startswith('export'):
                key, value = line.replace('export ', '').split('=')
                os.environ[key] = value


@run_check_wrapper
def get_nova_server_list_cli():
    hostname = socket.gethostname()
    cmd = [
        'nova', 'list',
        '--all-tenants',
        '--host', hostname,
        '--fields', 'instance_name,name'
    ]
    output = subprocess.check_output(cmd).decode('utf-8').split('\n')[3:-1]
    return [[i.strip() for i in line.split('|')[1:-1]] for line in output]


@run_check_wrapper
def nova_servers_api():
    load_env()
    loader = loading.get_plugin_loader('password')
    auth = loader.load_from_options(
        auth_url=os.getenv('OS_AUTH_URL'),
        username=os.getenv('OS_USERNAME'),
        password=os.getenv('OS_PASSWORD'),
        project_name=os.getenv('OS_PROJECT_NAME'),
        user_domain_name=os.getenv('OS_USER_DOMAIN_NAME'),
        project_domain_name=os.getenv('OS_PROJECT_DOMAIN_NAME')
    )

    sess_keystone = session.Session(auth=auth)
    keystone = client.Client(session=sess_keystone)
    projects = keystone.projects.list()

    sess_nova = session.Session(auth=auth)
    nova = nova_client.Client(version='2.47', session=sess_nova)
    servers = nova.servers.list(
        search_opts={
            'all_tenants': 1,
            'host': socket.gethostname()})
    vms = {
        vm._info.get(
            "OS-EXT-SRV-ATTR:instance_name"): vm._info for vm in servers}
    for vm in vms:
        vm_project_id = vms[vm].get('tenant_id')
        vm_project_name = next(
            p.name for p in projects if p.id == vm_project_id)
        vms[vm].update({'project_name': vm_project_name})
    return vms


@run_check_wrapper
def get_and_update_last_screen(
        csv_file_path: str = '/tmp/virt-output.csv') -> dict:
    with open(csv_file_path, 'r') as file:
        screens = [
            upd for upd in csv.DictReader(file, restkey='Hosted')]
    screen = screens[-2]
    vm_count = int(screen.get('Running', '0'))
    hostname = screen.get('Hostname')
    screen_filled = {
        'hostname': hostname,
        '_running': vm_count,
        '_hosted': screen.get('Hosted'),
        'server_list': [
            {
                'hypervisor_hostname': hostname,
                '_host_cpus': multiprocessing.cpu_count(),
                '_domain_name': screen.get('Domain name'),
                '_domain_id': screen.get('Domain ID'),
                'block_read': screen.get('Block RDBY'),
                'block_write': screen.get('Block WRBY'),
                'cpu_%': format(
                    float(screen.get('%CPU').replace(',', '.')), '.3f'),
                'ram_%': screen.get('%Mem'),
                'net_received': screen.get('Net RXBY'),
                'net_sent': screen.get('Net TXBY')
            }]
        }

    if screen_filled['_hosted'] and vm_count > 1:
        hosted = screen_filled.get('_hosted')
        for num in range(0, vm_count-1):
            screen_filled['server_list'].append(
                {
                    'hypervisor_hostname': hostname,
                    '_host_cpus': multiprocessing.cpu_count(),
                    '_domain_name': hosted[num*10+1],
                    '_domain_id': hosted[num*10],
                    'block_read': hosted[num*10+6],
                    'block_write': hosted[num*10+7],
                    'cpu_%': format(
                        float(hosted[num*10+3].replace(',', '.')), '.3f'),
                    'ram_%': hosted[num*10+5],
                    'net_received': hosted[num*10+8],
                    'net_sent': hosted[num*10+9]
                }
            )
    return screen_filled


@run_check_wrapper
def nova_vm_list() -> list:
    nova_servers = nova_servers_api()
    screen = get_and_update_last_screen()
    for server in screen['server_list']:
        s_domain_name = server['_domain_name']
        nova_pair = nova_servers.get(s_domain_name)
        if not nova_pair:
            server.update({
                'ID': server.get('_domain_id'),
                'name': server.get('_domain_name')
            })
        else:
            server.update({
                'name': nova_pair.get('name'),
                'user_id': nova_pair.get('user_id'),
                'nova_compute_host': nova_pair.get('OS-EXT-SRV-ATTR:host'),
                'project_name': nova_pair.get('project_name'),
                'project_id': nova_pair.get('tenant_id'),
                'flavor_name': nova_pair.get('flavor').get('original_name'),
                'ID': nova_pair.get('id'),
                'availability_zone': nova_pair.get(
                    'OS-EXT-AZ:availability_zone'),
                'created': nova_pair.get('created'),
                'vm_state': nova_pair.get('OS-EXT-STS:vm_state'),
                'power_state': nova_pair.get('OS-EXT-STS:power_state'),
                'image_id': (
                    nova_pair['image']['id'] if nova_pair['image'] else ''),
                'ip_addr': nova_pair.get('addresses'),
            })
    return screen['server_list']


def main():
    vms = nova_vm_list()
    for vm in vms:
        if isinstance(vm, dict):
            logging.info('{}'.format(json.dumps(vm, indent=4)))
        else:
            logging.error('vm object:\n{}'.format(vm))
        try:
            ips = ''.join(
                ['{} {}'.format(
                    vm['ip_addr'][ifc][0]['addr'],
                    vm['ip_addr'][ifc][0]['OS-EXT-IPS-MAC:mac_addr'])
                    for ifc in vm['ip_addr']])
            print(
                vm['hypervisor_hostname'], vm['ID'],
                vm['name'], vm['block_read'],
                vm['block_write'], vm['cpu_%'],
                vm['ram_%'], vm['net_received'],
                vm['net_sent'], vm['flavor_name'],
                vm['user_id'], vm['project_id'],
                vm['project_name'], vm['availability_zone'],
                vm['vm_state'], vm['power_state'],
                vm['created'], ips
            )
        except KeyError:
            logging.info('{} not in OpenStack'.format(vm['name']))
            print(
                vm['hypervisor_hostname'], vm['ID'],
                vm['name'], vm['block_read'],
                vm['block_write'], vm['cpu_%'],
                vm['ram_%'], vm['net_received'],
                vm['net_sent']
            )
        except Exception as error:
            logging.error(('Error: {}'.format(error),
                           'Full error: {}'.format(traceback.format_exc())))


if __name__ == '__main__':
    main()
