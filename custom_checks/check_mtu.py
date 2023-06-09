import json
import subprocess

from core import run_check_wrapper, save_to_file


@run_check_wrapper
def check_mtu(destination_server, max_size=1500, step=100):
    if isinstance(destination_server, list):
        destination_server = destination_server[0]

    max_size = int(max_size)
    step = int(step)
    save_to_file('DO NOT FORGET: THERE IS 28 BYTES HEADER IN MTU PACKAGE!')
    mtu_dict = {
        'DESTINATION': destination_server,
        'OK': [],
        'FAILED': []
    }

    for size in range(max_size, 0, -step):
        ping = subprocess.run(
            ['ping',
             '-c', '1',
             '-s', str(size - 28),
             '-M', 'do',
             '-W', '1',
             destination_server],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        output = ping.stdout.decode('utf-8')
        if 'icmp_seq=1' in output:
            mtu_dict['OK'].append(size)
        else:
            mtu_dict['FAILED'].append(size)
    if mtu_dict['OK'] == [] and mtu_dict['FAILED'] == []:
        raise Exception('ZERO PINGS! TRY TO CHECK DESTINATION SERVER')

    return json.dumps(mtu_dict, indent=4)


def main():
    input_list = input(
        'Write ip and MTU size coherently, example: 10.0.0.1 1500\n').split()
    print(check_mtu(
        destination_server=input_list[0],
        max_size=int(input_list[1]))
    )


if __name__ == '__main__':
    main()
