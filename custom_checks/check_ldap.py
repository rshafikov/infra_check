import subprocess

from core import run_check_wrapper


@run_check_wrapper
def check_ldap(password, servers, container, base, filter):
    """
    input args:
    ldap_ipa = [
        ['ldap://10.114.10.10,', 'ldap://10.114.10.11'],
        ['uid=pvrr_virazh_admin,cn=users,cn=accounts,dc=crp,dc=rzd'],
        ['Zz1234567890'],
        ['cn=users,cn=accounts,dc=crp,dc=rzd'],
        ['memberOf=cn=pvrr-virazh-user-pug,cn=groups,cn=accounts,dc=crp,dc=rzd']
    ]
    example:
    print(check_ldap(
        password=ldap_ipa[2][0],
        servers=ldap_ipa[0],
        container=ldap_ipa[1][0],
        base=ldap_ipa[3][0],
        filter=ldap_ipa[4][0])
    )
    """

    ldapsearch_command = 'ldapsearch '
    servers = [s if s[-1] != ',' else s[:-1] for s in servers]
    alive_servers = []
    bad_servers = []
    stdout = ''
    for server in servers:
        if server.startswith('ldap://127.0'):
            stdout += 'localhost has been discovered\n'
            continue
        try:
            ldapsearch_args = '-l 5 -w {} -H {} -D "{}" -b "{}" "({})"'.format(
                password,
                server,
                container,
                base,
                filter
            )
            result = subprocess.getoutput(
                ldapsearch_command + ldapsearch_args).split()
            if 'numEntries:' in result:
                num_entries = [result[i + 1] for i in range(
                    len(result)) if result[i] == 'numEntries:']
                if int(num_entries[0]) > 1:
                    alive_servers.append(server)
                    continue
            stdout += 'LDAP {} is NOT available\n'.format(server)
            stdout += (
                'You can check availability '
                'of this server manually:\n{}\n'.format(
                    ldapsearch_command + ldapsearch_args
                )
            )
            bad_servers.append(server)
        except Exception as error:
            stdout += 'There is an error with LDAP {}: {}\n'.format(
                server, error)
    if bad_servers:
        stdout += 'Problem servers: {}\n'.format(', '.join(bad_servers))
    stdout += (
        'Available {} from {}: '
        '{}'.format(len(alive_servers), str(len(servers)), alive_servers)
    )
    return stdout


def main():
    ldap_ipa = [
        ['ldap://127.0.2.2,', 'ldap://10.114.10.11'],
        ['uid=msk_virazh_admin,cn=users,cn=accounts,dc=crp,dc=rzd'],
        ['Zz1234567890'],
        ['cn=users,cn=accounts,dc=crp,dc=rzd'],
        ['memberOf=cn=msk-virazh-user-pug,cn=groups,cn=accounts,dc=crp,dc=rzd']
    ]
    print('THIS JUST AN EXAMPLE!')
    print(check_ldap(
        password=ldap_ipa[2][0],
        servers=ldap_ipa[0],
        container=ldap_ipa[1][0],
        base=ldap_ipa[3][0],
        filter=ldap_ipa[4][0])
    )


if __name__ == '__main__':
    main()
