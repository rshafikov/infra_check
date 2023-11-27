from check_ldap import main_check_ldap
from check_repo import main_check_repo
from check_context_without_comments import main_check_cyrillic
from check_macs import main_check_macs
from check_san import main_check_san
from check_ntp import main_check_ntp
from check_dns import main_check_dns
from check_mtu import main_check_ping


class CheckRunner:
    @staticmethod
    def _check_repo():
        main_check_repo()

    @staticmethod
    def _check_cyrrilic():
        main_check_cyrillic()

    @staticmethod
    def _check_macs():
        main_check_macs()

    @staticmethod
    def _check_san():
        main_check_san()

    @staticmethod
    def _check_ntp():
        main_check_ntp()

    @staticmethod
    def _check_dns():
        main_check_dns()

    @staticmethod
    def _check_mtu():
        main_check_ping()

    @staticmethod
    def _check_ldap():
        main_check_ldap()

    def run(self):
        self._check_repo()
        self._check_cyrrilic()
        self._check_macs()
        self._check_san()
        self._check_dns()
        self._check_ntp()
        self._check_mtu()
        self._check_ldap()


if __name__ == '__main__':
    runner = CheckRunner()
    runner.run()
