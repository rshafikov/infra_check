import logging
import subprocess
import time

from check_ntp import check_ntp
from check_dns import check_dns
# from check_dhcp import check_dhcp
from check_ldap import check_ldap
from check_context_without_comments import search_cyrillic
from check_san import check_san
from check_mtu import check_mtu
from check_macs import check_macs


logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='checks.log',
    filemode='a',
    level=logging.INFO
)


def run_check_wrapper(func):
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            logging.info('func {} - OK'.format(func.__name__))
            return result
        except Exception as e:
            logging.error(('There is an error with {}'.format(func.__name__),
                           'Full error: \n{}'.format(e)))
            return 'There is an error with {}'.format(func.__name__)

    return wrapper


@run_check_wrapper
def parse_data():
    try:
        with open("/root/endpars.txt", "r") as file:
            lines = [line for line in file]
    except Exception:
        logging.info('endparse taken from local dir')
        print('Trying to parse data locally')
        with open("endpars", "r") as file:
            lines = [line for line in file]
    ntp_servers = [line.split()[1] for line in lines if line.startswith('NTP')]
    dns_servers = [line.split()[1] for line in lines if line.startswith('DNS')]
    ldap_ipa = [line.split()[2:] for line in lines if line.startswith(
            'Keystone FreeIpa')]
    dhcp_servers = [line.split()[2] for line in lines if line.startswith(
        'Local DNS')]
    ldap_msad = [line.split()[2:] for line in lines if line.startswith(
        'Keystone AD')]
    san_servers = [line.split()[1] for line in lines if line.startswith('SAN')]
    mtu = [line.split()[1] for line in lines if line.startswith('MTU')]

    return (
        lines,
        ntp_servers,
        dns_servers,
        ldap_ipa,
        dhcp_servers,
        ldap_msad,
        san_servers,
        mtu
        )


lines, ntp_servers, dns_servers, ldap_ipa, dhcp_servers, ldap_msad, san_servers, mtu = parse_data()

print('<NTP>'.center(65, '-'))
check_ntp = run_check_wrapper(check_ntp)
ntp_output = check_ntp(ntp_servers)
print(ntp_output)

print('<DNS>'.center(65, '-'))
check_dns = run_check_wrapper(check_dns)
dns_output = check_dns(dns_servers)
print(dns_output)

print('<DHCP>'.center(65, '-'))
if 'OK' in lines:
    cmd = ['source', 'run_dhcp.sh']
    subprocess.run(cmd)
    time.sleep(1)

else:
    print(
        'Failed to check DHCP-servers.\n'
        'Please install dhclient package at first!\n'
        'Try this command: apt-get install nmap'
        )

print('<LDAP-servers>'.center(65, '-'))
if 'OK  Package ldap-utils is installed.\n' in lines:
    print('<IPA>'.center(65, '-'))
    check_ldap = run_check_wrapper(check_ldap)
    try:
        password = ldap_ipa[2][0]
        servers = ldap_ipa[0]
        container = ldap_ipa[1][0]
        base = ldap_ipa[3][0]
        filter = ldap_ipa[4][0]
        print(check_ldap(password, servers, container, base, filter))
    except Exception as error:
        print('There is an error with IPA LDAP-parameters: {}'.format(error))

    print('<MSAD>'.center(65, '-'))
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
    print(
        'Failed to check LDAP-servers.\n'
        'Please install ldap-utils package at first!\n'
        'Try this command: apt-get install ldap-utils'
        )

print('<Cyrillic check>'.center(65, '-'))
search_cyrillic = run_check_wrapper(search_cyrillic)
search_cyrillic('/var/www/html/')

print('<SAN>'.center(65, '-'))
check_san = run_check_wrapper(check_san)
print(check_san(san_servers))

print('<MTU>'.center(65, '-'))
check_mtu = run_check_wrapper(check_mtu)
print(check_mtu(destination_server=dns_servers[0], max_size=int(mtu[0])))

print("<MAC's>".center(65, '-'))
check_macs = run_check_wrapper(check_macs)
print(check_macs(directory='/etc/dhcp/dhcpd.conf'))

print("<END OF TEST>".center(65, '-'))
