import logging

from core import is_check_enabled, run_check_wrapper, save_to_file


@run_check_wrapper
def check_macs(conf):
    default_value = '/etc/dhcp/dhpcd.conf'
    dhcpd_path = conf.config.get(
        'CHECK', 'dhcpd_path', fallback=default_value)
    macs = []
    with open(dhcpd_path, encoding='utf-8') as file:
        content = file.readlines()
        macs = [line.strip().split()[2][:-1] for line in content if line.strip(
        ).startswith('hardware')]
        macs_set = set(macs)
        if len(macs) == len(macs_set):
            return "There is no same MAC's"
        else:
            empty_list = []
            doubled_macs = []
            for mac in macs:
                if mac not in empty_list:
                    empty_list.append(mac)
                else:
                    doubled_macs.append(mac)
        return "There is {} MAC's have copy: {}".format(
            len(doubled_macs), ' '.join(doubled_macs))


@is_check_enabled(check_name='check_macs')
def main_check_macs(conf, check_name, *args, **kwargs):
    save_to_file(check_name=check_name, content=check_macs(conf))


if __name__ == '__main__':
    main_check_macs()
