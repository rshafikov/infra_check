from check_ntp import check_ntp
from check_dns import check_dns
# from check_dhcp import check_dhcp
from check_ldap import check_ldap
from check_context_without_comments import search_cyrillic
from check_san import check_san
from check_mtu import check_mtu
from check_macs import check_macs


with open("/root/endpars", "r") as file:
    lines = [line for line in file]
    print('<NTP>'.center(65, '-'))
    ntp_servers = [line.split()[1] for line in lines if line.startswith('NTP')]
    ntp_output = check_ntp(ntp_servers)
    print(ntp_output)
    print('<DNS>'.center(65, '-'))
    dns_servers = [line.split()[1] for line in lines if line.startswith('DNS')]
    dns_output = check_dns(dns_servers)
    print(dns_output)
    print('<DHCP>'.center(65, '-'))
    if 'OK  Package nmap is installed.\n' in lines:
        dhcp_servers = [line.split()[2] for line in lines if line.startswith(
            'Local DNS')]
        # dhcp_output = check_dhcp(dhcp_servers)
        # print(dhcp_output)
    else:
        print(
            'Failed to check DHCP-servers.\n'
            'Please install nmap package at first!\n'
            'Try this command: apt-get install nmap'
            )
    print('<LDAP-servers>'.center(65, '-'))
    if 'OK  Package ldap-utils is installed.\n' in lines:
        print('<IPA>'.center(65, '-'))
        ldap_ipa = [line.split()[2:] for line in lines if line.startswith(
            'Keystone FreeIpa')]
        try:
            print(check_ldap(
                password=ldap_ipa[2][0],
                servers=ldap_ipa[0],
                container=ldap_ipa[1][0],
                base=ldap_ipa[3][0],
                filter=ldap_ipa[4][0]
                ))
        except Exception as error:
            print(
                'There is an error with IPA LDAP-parameters: {}'.format(error)
                )
        print('<MSAD>'.center(65, '-'))
        ldap_msad = [line.split()[2:] for line in lines if line.startswith(
            'Keystone AD')]
        try:
            print(check_ldap(
                password=ldap_msad[2][0],
                servers=ldap_msad[0],
                container=' '.join(ldap_msad[1]),
                base=ldap_msad[3][0],
                filter=' '.join(ldap_msad[4]))
            )
        except Exception as error:
            print(
                'There is an error with MSAD LDAP-parameters: {}'.format(error)
                )
    else:
        print(
            'Failed to check LDAP-servers.\n'
            'Please install ldap-utils package at first!\n'
            'Try this command: apt-get install ldap-utils'
            )
    print('<Cyrillic check>'.center(65, '-'))
    search_cyrillic('/var/www/html/')
    print('<SAN>'.center(65, '-'))
    san_servers = [line.split()[1] for line in lines if line.startswith('SAN')]
    print(check_san(san_servers))
    print('<MTU>'.center(65, '-'))
    mtu = [line.split()[1] for line in lines if line.startswith('MTU')]
    print(check_mtu(destination_server=dns_servers[0], max_size=int(mtu[0])))
    print("<MAC's>".center(65, '-'))
    print(check_macs(directory='/etc/dhcp/dhcpd.conf'))
    print("<END OF TEST>".center(65, '-'))
