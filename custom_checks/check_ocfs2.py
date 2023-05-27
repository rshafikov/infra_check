import json
import random
import string

from core import (get_value_from_env, get_value_from_file, run_check_wrapper,
                  subprocess)

INITRC_ = ('/Users/rshafikov/Desktop/_work/modulo'
           '/cobbler/html/stable/astra/1.6/initrc_')

INITRC_2 = ('/Users/rshafikov/Desktop/_work/modulo'
            '/cobbler/html/stable/astra/1.6/initrc_2')

BIND9 = ('/Users/rshafikov/Desktop/_work/modulo'
         '/cobbler/html/stable/astra/1.6/install_bind9')


@run_check_wrapper
def generate_fake_region():
    digits = string.hexdigits[:-6]
    return ''.join(random.choice(digits) for _ in range(32)).upper()


@run_check_wrapper
def get_list_of_hostnames(initrc, ocfs_config, hosti_id=0):
    cmd = (
        """
            source {}
            i=1
            {}
            do
                if [ $i -gt "9" ];then
                    numi=$i
                else
                    numi="0$i"
                fi
            echo {}
            let i=$i+1
            done
        """.format(
            initrc,
            ocfs_config['$hosti'][hosti_id],
            ocfs_config['NODE_FULL_PATTERN'])
    )
    return subprocess.getoutput(cmd)


@run_check_wrapper
def parse_dns_record_pattern(bind9_path):
    exclude_list = ('$REVERSE_IP', 'dbmaster', 'controller')
    hostname_pattern = get_value_from_file(
        'update add', bind9_path).split('\n')[:-1]
    exclude_list = ('$REVERSE_IP', 'dbmaster', 'controller')
    node_full_pattern = ''.join(
        [p for p in hostname_pattern if all(e not in p for e in exclude_list)])
    node_name_pattern = ''.join(
        n for n in node_full_pattern.split() if '$CLOUD_ZONE' in n)
    node_ip_pattern = ''.join(
        n for n in node_full_pattern.split() if '$NET.$hosti' in n)
    return node_full_pattern, node_name_pattern, node_ip_pattern


@run_check_wrapper
def print_config(initrc, ocfs_config):
    stdout = ''
    list_of_hosts = ocfs_config['$OCFS2_IPS']
    cluster_name = ocfs_config['$OCFS2_CLUSTER_NAME']
    stdout += (
        'heartbeat:\n'
        '       pseudo_region = {}\n'
        '       cluster = {}\n\n'
    ).format(generate_fake_region(), cluster_name)
    list_of_hostnames = get_list_of_hostnames(
        initrc, ocfs_config).split('\n')
    for node_number, node_ip, in enumerate(list_of_hosts, start=1):
        name = ''.join(
            h.split()[2] for h in list_of_hostnames if node_ip in h)
        stdout += (
            'node:\n'
            '        number = {}\n'
            '        name = {}\n'
            '        ip_address = {}\n'
            '        ip_port = 7777\n'
            '        cluster = {}\n\n'
        ).format(node_number, name, node_ip, cluster_name)
    stdout += (
        """
cluster:
        node_count = {}
        heartbeat_mode = global
        name = {}

        """.format(len(list_of_hosts), cluster_name)
    )
    return stdout


@run_check_wrapper
def check_ocfs2(initrc, bind9_path):
    ocfs_config = {}
    ocfs2_cluster_name_up = get_value_from_env(
        'OCFS2_CLUSTER_NAME', initrc).split('=')[1]
    ocfs2_ips_up = get_value_from_env(
        'OCFS2_IPS', initrc).split('=')[1].split()
    ocfs_number_of_nodes_list = [subprocess.getoutput(
        "echo {} | ".format(ip)+" awk -F'.' '{ print $4 }'")
        for ip in ocfs2_ips_up]
    cloud_zone_up = get_value_from_env('$CLOUD_ZONE', initrc).split('\n')
    cloud_zone_up = ''.join(
        s for s in cloud_zone_up if 'CLOUD_ZONE' in s).split('=')[1]
    net_up = get_value_from_env('$NET', initrc).split('\n')
    net_up = ''.join(
        s for s in net_up if 'NET' in s).split('=')[1]
    (node_full_pattern,
     node_name_pattern,
     node_ip_pattern) = parse_dns_record_pattern(BIND9)
    hosti_range = get_value_from_file(
        'for hosti', bind9_path).split('\n')
    ocfs_config.update({
        '$OCFS2_CLUSTER_NAME': ocfs2_cluster_name_up,
        '$OCFS2_IPS': ocfs2_ips_up,
        '$OCFS2_NODE_NUMBERS': ocfs_number_of_nodes_list,
        '$CLOUD_ZONE': cloud_zone_up,
        '$NET': net_up,
        'NODE_FULL_PATTERN': node_full_pattern,
        'NODE_NAME_PATTERN': node_name_pattern,
        'NODE_IP_PATTERN': node_ip_pattern,
        '$hosti': hosti_range})
    list_of_hostnames = get_list_of_hostnames(
        initrc, ocfs_config).split('\n')
    ocfs_config.update(
        {'NODE_HOSTNAME_LIST': [h for h in list_of_hostnames]})
    return ocfs_config


def main():
    ocfs_config_1 = check_ocfs2(INITRC_, BIND9)
    print(json.dumps(ocfs_config_1, indent=4))
    print(print_config(INITRC_, ocfs_config_1))

    ocfs_config_2 = check_ocfs2(INITRC_2, BIND9)
    print(json.dumps(ocfs_config_2, indent=4))
    print(print_config(INITRC_2, ocfs_config_2))


if __name__ == '__main__':
    main()
