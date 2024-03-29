import logging
import os
import re
from configparser import ConfigParser
from pathlib import Path

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(filename='/tmp/infra_check.log', mode='a')],
    level=logging.INFO
)

LOG = logging.getLogger(__name__)

CONF_PATH = os.path.join(os.path.expanduser("~"), ".infra.conf'")


DEFAULT_CONF = {
    'DEFAULT': {
        'mtu_dest': 'ya.ru google.com',
        'mtu_size_step': '1600 200',
        'san_servers': 'ya.ru 127.0.0.1',
        'log_level': 'INFO',
        'cyrillic_search_dir': '/var/www/html/',
        'dhcpd_path': '/etc/dhcp/dhcpd.conf',
        'repo_pattern': 'REPO[0-9]?',
        'ntp_pattern': '\w+_NTP[0-9]?',
        'dns_pattern': '\w+_DNS[0-9]?',
    },
    'CHECK': {
        'check_repo': True,
        'check_cyrillic': True,
        'check_macs': True,
        'check_san': True,
        'check_ntp': True,
        'check_dns': True,
        'check_mtu': True,
        'check_ldap': True,
        'check_ocfs2': False,
        'check_dhcp': False
    }
}


class ConfigurationException(Exception):
    pass


class FileNotFound(Exception):
    pass


class Config:
    def __init__(self, path: str = CONF_PATH, default_dict: dict = {}):
        self.path = Path(self._check_path(path))
        self.config = ConfigParser()
        self.config.read(self.path, 'utf-8')
        self.sections = self.config.sections()
        self.params = {}
        self.initrc_list = self._get_initrc_list()

    def get_section(self, sec: str) -> dict:
        if self.is_section(sec):
            return {
                k: v for k, v in self.config[sec].items()}
        else:
            raise ConfigurationException("Can't get a section: %s" % sec)

    def is_section(self, sec_name):
        return sec_name in self.config

    def read(self):
        for sec in self.config.sections():
            try:
                self.params.update({sec: self.get_section(sec)})
            except ConfigurationException as err:
                LOG.warning('There is no section with name: %s' % sec)

    def pprint(self):
        import json
        print(json.dumps(self.params, indent=4))

    @staticmethod
    def _check_path(path: str) -> str:
        path_obj = Path(path.replace("'", ""))
        if path_obj.is_file():
            return path_obj.as_posix()
        if path.endswith('dir') and path_obj.is_dir():
            return path_obj.as_posix()
        LOG.warning('Error while checking path: %s' % path)
        raise FileNotFound('wrong path: %s' % path)

    def _get_initrc_list(self):
        try:
            return [v.replace("'", "").replace('"', '') for k, v in self.get_section(
                'INITRC').items() if k.startswith('initrc')]
        except ConfigurationException as err:
            return None

    def get_regexp(self, regexp_name, default):
        pattern = self.config.get('CHECK', regexp_name, raw=True, fallback=default)
        return re.compile(pattern)


def load_conf(config_path=CONF_PATH, default_dict={}):
    c = Config(config_path, default_dict)
    c.read()
    return c


config = load_conf()
LOG.setLevel(config.config.get(
    'DEFAULT', 'log_level', fallback='INFO').upper())
