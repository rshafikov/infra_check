import json
import random
import string

from core import (find_file_by_pattern, get_value_from_env,
                  get_value_from_file, run_check_wrapper, save_to_file,
                  subprocess)


@run_check_wrapper
def generate_fake_region():
    digits = string.hexdigits[:-6]
    return ''.join(random.choice(digits) for _ in range(32)).upper()


@run_check_wrapper
def get_list_of_hostnames(
        initrc, ocfs_config, cluster_type='hypervisor'):
    cmd = (
        '''
            . {}
            i=1
            {};
            do
                if [ $i -gt "9" ];then
                    numi=$i
                else
                    numi="0$i"
                fi
            echo {}
            let i=$i+1
            done
        '''.format(
            initrc,
            ocfs_config['$hosti'][cluster_type],
            ocfs_config['NODE_FULL_PATTERN'])
    )
    return subprocess.run(
        ['bash', '-c', cmd], capture_output=True, text=True).stdout


# @run_check_wrapper
def parse_dns_record_pattern(
        bind9_path, cluster_type='hypervisor'):
    hostname_patterns = get_value_from_file(
        'update add', bind9_path).split('\n')[:-1]
    pattern_dict = {'full_pattern_list': [
        p for p in hostname_patterns if '$REVERSE_IP' not in p]
    }
    pattern_dict.update({
       'hypervisor': (pattern_dict.get('full_pattern_list')[0]),
       'controller': (pattern_dict.get('full_pattern_list')[1]),
       'dbmaster': (pattern_dict.get('full_pattern_list')[2])
    })
    n_full_pattern = pattern_dict.get(cluster_type)
    n_name_pattern = next(
        n for n in n_full_pattern.split() if '$CLOUD_ZONE' in n)
    n_ip_pattern = next(
        n for n in n_full_pattern.split() if '$NET.$hosti' in n)
    return n_full_pattern, n_name_pattern, n_ip_pattern


# @run_check_wrapper
def print_config(initrc, ocfs_config):
    stdout = 'OCFS2_CLUSTER by {}\n\n'.format(initrc)
    list_of_hosts = ocfs_config['$OCFS2_IPS']
    cluster_name = ocfs_config['$OCFS2_CLUSTER_NAME']
    stdout += (
        'heartbeat:\n'
        '        pseudo_region = {}\n'
        '        cluster = {}\n\n'
    ).format(generate_fake_region(), cluster_name)
    list_of_hostnames = ocfs_config.get('NODE_HOSTNAME_LIST')
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
        ).format(node_ip.split('.')[-1], name, node_ip, cluster_name)
    stdout += (
        """
cluster:
        node_count = {}
        heartbeat_mode = global
        name = {}
        """.format(len(list_of_hosts), cluster_name)
    )
    return stdout


# @run_check_wrapper
def check_ocfs2(initrc, bind9_path, cluster_type='hypervisor'):
    ocfs_config = {}
    ocfs2_cluster_name_up = get_value_from_env(
        'OCFS2_CLUSTER_NAME', initrc).split('=')
    print(ocfs2_cluster_name_up)
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
     node_ip_pattern) = parse_dns_record_pattern(bind9_path, cluster_type)
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
        '$hosti': {
            'hypervisor': hosti_range[0],
            'controller': hosti_range[1],
            'dbmaster': hosti_range[2]
        }
    })
    list_of_hostnames = get_list_of_hostnames(
        initrc, ocfs_config, cluster_type).split('\n')
    ocfs_config.update(
        {'NODE_HOSTNAME_LIST': [h for h in list_of_hostnames]})
    return ocfs_config


# @run_check_wrapper
def check_cluster(initrc_, bind9, cluster_type='hypervisor'):
    ocfs_config = check_ocfs2(initrc_, bind9, cluster_type)
    save_to_file(print_config(initrc_, ocfs_config))


def main():
    check_cluster(
        '/Users/rshafikov/Desktop/_work/modulo/cobbler/custom_checks/1.7/install_ocfs2',
        '/Users/rshafikov/Desktop/_work/modulo/cobbler/custom_checks/1.7/install_bind9',
    )
    # path = input('Enter path of the directory with initrc_ files:\n')
    # initrc_ = find_file_by_pattern('initrc_', path)
    # initrc_2 = find_file_by_pattern('initrc_2', path)
    # initrc_ctrl = find_file_by_pattern('initrc_.controller.ocfs2', path)
    # bind9 = find_file_by_pattern('install_bind9', path)
    # if initrc_ != f'No file with name: initrc_':
    #     check_cluster(initrc_, bind9)
    # if initrc_2 != f'No file with name: initrc_2':
    #     check_cluster(initrc_2, bind9)
    # if initrc_ctrl != f'No file with name: initrc_.controller.ocfs2':
    #     check_cluster(initrc_ctrl, bind9, 'controller')
    #
    # ocfs_config_ctrl = check_ocfs2(initrc_ctrl, bind9, 'controller')
    # print(json.dumps(ocfs_config_ctrl, indent=4))
    # print(print_config(initrc_ctrl, ocfs_config_ctrl))


if __name__ == '__main__':
    main()
