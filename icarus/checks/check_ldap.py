import logging
import subprocess

from icarus.checks.core import (CONF, check_package, is_check_enabled,
                                run_check_wrapper, save_to_file)
from icarus.checks.parse_config import load_conf

LOG = logging.getLogger(__name__)
LOG.setLevel(CONF.config.get('DEFAULT', 'log_level', fallback='INFO').upper())


SHELL_PARAMS = {
    'CMD': 'ldapsearch -l 5 -w "{}" -H "{}" -D "{}" -b "{}" "{}"',
    'ok_codes': {
        0: 'OK',
    },
    'err_codes': {
        49: 'invalid credentials',
        255: "can't contact ldap server",
        32: "invalid parameters in request",
        -1: "unknown error",
    },
}


class LDAPParseResponseError(Exception):
    pass


@run_check_wrapper
def check_ldap(password, servers, container, base, ldap_filter):
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
        ldap_filter=ldap_ipa[4][0])
    )
    """
    out = 'Error'
    servers = servers.split() if ',' not in servers else servers.split(',')
    for server in servers:
        if server.startswith('ldap://127.0'):
            LOG.info('localhost has been discovered via LDAP-check')

        try:
            ldapsearch_args = SHELL_PARAMS['CMD'].format(
                password.replace('"', '').replace("'", ""),
                server.replace('"', '').replace("'", ""),
                container.replace('"', '').replace("'", ""),
                base.replace('"', '').replace("'", ""),
                ldap_filter.replace('"', '').replace("'", "")
            )

            LOG.debug('CMD: %s' % ldapsearch_args)
            req = subprocess.run(
                ldapsearch_args,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            LOG.debug('stdout:\n%s' % req.stdout)
            LOG.debug(
                'stderr:\n%s' % req.stderr if req.stderr else 'no stderr')
            res_code = req.returncode
            _, out = req.stdout.split(
                '# search result') if req.stdout else ('', req.stderr)
            if res_code in SHELL_PARAMS['ok_codes']:
                return f"{SHELL_PARAMS['ok_codes'][res_code]}\n{out}"
            elif res_code in SHELL_PARAMS['err_codes']:
                return f"{SHELL_PARAMS['err_codes'][res_code]}\n{out}"

            raise LDAPParseResponseError

        except LDAPParseResponseError:
            return f'unknown error: {out}'
        except Exception as error:
            LOG.info('error while checking LDAP server: %s' % error)
            return 'There is an error with LDAP {}: {}'.format(
                server, error)


@is_check_enabled(check_name='check_ldap')
def main_check_ldap(main_conf, check_name, *args, **kwargs):
    # ldap_ipa = [
    #     ['ldap://127.0.2.2,', 'ldap://10.114.10.11'],
    #     ['uid=msk_virazh_admin,cn=users,cn=accounts,dc=crp,dc=rzd'],
    #     ['Zz1234567890'],
    #     ['cn=users,cn=accounts,dc=crp,dc=rzd'],
    #     ['memberOf=cn=msk-virazh-user-pug,cn=groups,cn=accounts,dc=crp,dc=rzd']
    # ]
    required_pckg = 'ldapearch'
    stdout = f'install package: "{required_pckg}" to continue this test'
    if check_package(required_pckg):
        stdout = ''
        for keystone_conf in ('keystone_conf_ipa', 'keystone_conf_msad'):
            try:
                ipa_conf = load_conf(
                    config_path=main_conf.get_section(
                        'KEYSTONE')[keystone_conf])
            except KeyError as err:
                LOG.warning('parameter %s in infra.conf not found' % err)
                continue

            stdout += (
                """
                \rLDAP: {keystone_conf}\nCONF PATH: {path}\nRESULT: {ldap}
                """.format(
                    keystone_conf=keystone_conf,
                    path=ipa_conf.path,
                    ldap=check_ldap(
                        password=ipa_conf.config.get('ldap', 'password'),
                        servers=ipa_conf.config.get('ldap', 'url'),
                        container=ipa_conf.config.get('ldap', 'user'),
                        base=ipa_conf.config.get('ldap', 'user_tree_dn'),
                        ldap_filter=ipa_conf.config.get('ldap', 'user_filter')
                    )
                )
            )

    save_to_file(check_name=check_name, content=stdout)


if __name__ == '__main__':
    main_check_ldap()
