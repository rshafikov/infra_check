import subprocess
import time

from check_context_without_comments import search_cyrillic
from check_dns import check_dns
from check_ldap import check_ldap
from check_macs import check_macs
from check_mtu import check_mtu
from check_ntp import check_ntp
from check_ocfs2 import check_ocfs2, print_config
from check_san import check_san
from core import find_file_by_pattern, logging, run_check_wrapper, save_to_file

INITRC_DIR = '/var/www/html/'


@run_check_wrapper
def parse_data():
    logging.info('<START TEST>'.center(69, '-'))
    cmd = '/bin/bash /root/check_pack.sh'
    check_packages = run_check_wrapper(subprocess.getoutput)
    packages = check_packages(cmd)
    time.sleep(1)
    try:
        with open('/root/endpars', 'r') as file:
            lines = [line for line in file]
    except Exception:
        logging.info('endparse taken from local dir')
        save_to_file('Trying to parse data locally')
        with open('endpars', 'r') as file:
            lines = [line for line in file]
    ntp_servers = [line.split()[1] for line in lines if line.startswith('NTP')]
    dns_servers = {
        'dns': [line.split()[1] for line in lines if line.startswith('DNS')]}
    ldap_ipa = [line.split()[2:] for line in lines if line.startswith(
            'Keystone FreeIpa')]
    dhcp_servers = [line.split()[2] for line in lines if line.startswith(
        'Local DNS')]
    ldap_msad = [line.split()[2:] for line in lines if line.startswith(
        'Keystone AD')]
    san_servers = [line.split()[1] for line in lines if line.startswith('SAN')]
    mtu = {'mtu': line.split()[1] for line in lines if line.startswith('MTU')}

    return (
        lines,
        packages,
        ntp_servers,
        dns_servers,
        ldap_ipa,
        dhcp_servers,
        ldap_msad,
        san_servers,
        mtu
        )


(lines, packages, ntp_servers, dns_servers, ldap_ipa,
 dhcp_servers, ldap_msad, san_servers, mtu) = parse_data()

save_to_file('<NTP>'.center(69, '-'))
ntp_output = check_ntp(ntp_servers)
save_to_file(ntp_output)

save_to_file('<DNS>'.center(69, '-'))
dns_output = check_dns(dns_servers.get('dns', []))
save_to_file(dns_output)

save_to_file('<DHCP>'.center(69, '-'))
if 'Package isc-dhcp-client is installed' in packages:
    cmd = ['/bin/bash', '/root/custom_checks/run_dhcp.sh']
    dhcp_check = run_check_wrapper(subprocess.run)
    dhcp_check(cmd)
    time.sleep(1)

else:
    save_to_file(
        'Failed to check DHCP-servers.\n'
        'Please install dhclient utility at first!\n'
        'Try this command: apt-get install isc-dhcp-client'
        )

save_to_file('<LDAP-servers>'.center(69, '-'))
if 'Package ldap-utils is installed' in packages:
    save_to_file('<IPA>'.center(69, '-'))
    try:
        password = ldap_ipa[2][0]
        servers = ldap_ipa[0]
        container = ldap_ipa[1][0]
        base = ldap_ipa[3][0]
        filter = ldap_ipa[4][0]
        save_to_file(check_ldap(password, servers, container, base, filter))
    except Exception as error:
        save_to_file(
            'There is an error with IPA LDAP-parameters: {}'.format(error))

    save_to_file('<MSAD>'.center(69, '-'))
    try:
        password = ldap_msad[2][0]
        servers = ldap_msad[0]
        container = ' '.join(ldap_msad[1])
        base = ldap_msad[3][0]
        filter = ' '.join(ldap_msad[4])
        save_to_file(check_ldap(password, servers, container, base, filter))
    except Exception as error:
        save_to_file(
            'There is an error with MSAD LDAP-parameters: {}'.format(error))

else:
    logging.info('func {} - NOT HAS BEEN LAUNCHED'.format(check_ldap.__name__))
    save_to_file(
        'Failed to check LDAP-servers.\n'
        'Please install ldapsearch utility at first!\n'
        'Try this command: apt-get install ldap-utils'
        )

save_to_file('<Cyrillic check>'.center(69, '-'))
save_to_file(search_cyrillic(INITRC_DIR))

save_to_file('<SAN>'.center(69, '-'))
save_to_file(check_san(san_servers))

save_to_file('<MTU>'.center(69, '-'))
save_to_file(
    check_mtu(destination_server=dns_servers.get('dns', 'localhost'),
              max_size=mtu.get('mtu', 1500)))

save_to_file("<MAC's>".center(69, '-'))
save_to_file(check_macs(directory='/etc/dhcp/dhcpd.conf'))

save_to_file("<OCFS2_CONF>".center(69, '-'))
INITRC_, INITRC_2, BIND9 = (
    find_file_by_pattern('INITRC_', INITRC_DIR),
    find_file_by_pattern('INITRC_2', INITRC_DIR),
    find_file_by_pattern('install_bind9', INITRC_DIR)
)
ocfs_config_1 = check_ocfs2(INITRC_, BIND9)
save_to_file(print_config(INITRC_, ocfs_config_1))
ocfs_config_2 = check_ocfs2(INITRC_2, BIND9)
save_to_file(print_config(INITRC_2, ocfs_config_2))

save_to_file('<END OF TEST>'.center(69, '-'))
