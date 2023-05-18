def check_macs(directory='dhcpd.conf'):
    macs = []
    with open(directory, encoding='utf-8') as file:
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


def main():
    print(check_macs(input('Write dhcpd.conf path:\n')))


if __name__ == '__main__':
    main()
