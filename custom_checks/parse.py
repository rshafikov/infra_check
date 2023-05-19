import subprocess
import time

from check_ntp import check_ntp
from check_dns import check_dns
from check_ldap import check_ldap
from check_context_without_comments import search_cyrillic
from check_san import check_san
from check_mtu import check_mtu
from check_macs import check_macs
from core import logging, run_check_wrapper


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
        print('Trying to parse data locally')
        with open('endpars', 'r') as file:
            lines = [line for line in file]
    ntp_servers = [line.split()[1] for line in lines if line.startswith('NTP')]
    dns_servers = {
        'dns': line.split()[1] for line in lines if line.startswith('DNS')}
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

print('<NTP>'.center(69, '-'))
ntp_output = check_ntp(ntp_servers)
print(ntp_output)

print('<DNS>'.center(69, '-'))
dns_output = check_dns(dns_servers.get('dns', []))
print(dns_output)

print('<DHCP>'.center(69, '-'))
if 'Package isc-dhcp-client is installed' in packages:
    cmd = ['/bin/bash', '/root/custom_checks/run_dhcp.sh']
    dhcp_check = run_check_wrapper(subprocess.run)
    dhcp_check(cmd)
    time.sleep(1)

else:
    print(
        'Failed to check DHCP-servers.\n'
        'Please install dhclient utility at first!\n'
        'Try this command: apt-get install isc-dhcp-client'
        )

print('<LDAP-servers>'.center(69, '-'))
if 'Package ldap-utils is installed' in packages:
    print('<IPA>'.center(69, '-'))
    try:
        password = ldap_ipa[2][0]
        servers = ldap_ipa[0]
        container = ldap_ipa[1][0]
        base = ldap_ipa[3][0]
        filter = ldap_ipa[4][0]
        print(check_ldap(password, servers, container, base, filter))
    except Exception as error:
        print('There is an error with IPA LDAP-parameters: {}'.format(error))

    print('<MSAD>'.center(69, '-'))
    try:
        password = ldap_msad[2][0]
        servers = ldap_msad[0]
        container = ' '.join(ldap_msad[1])
        base = ldap_msad[3][0]
        filter = ' '.join(ldap_msad[4])
        print(check_ldap(password, servers, container, base, filter))
    except Exception as error:
        print('There is an error with MSAD LDAP-parameters: {}'.format(error))

else:
    logging.info('func {} - NOT HAS BEEN LAUNCHED'.format(check_ldap.__name__))
    print(
        'Failed to check LDAP-servers.\n'
        'Please install ldapsearch utility at first!\n'
        'Try this command: apt-get install ldap-utils'
        )

print('<Cyrillic check>'.center(69, '-'))
print(search_cyrillic('/var/www/html/'))

print('<SAN>'.center(69, '-'))
print(check_san(san_servers))

print('<MTU>'.center(69, '-'))
print(check_mtu(destination_server=dns_servers.get('dns', ['localhost'])[0],
                max_size=mtu.get('mtu', 1500)))

print("<MAC's>".center(69, '-'))
print(check_macs(directory='/etc/dhcp/dhcpd.conf'))

print('<END OF TEST>'.center(69, '-'))
