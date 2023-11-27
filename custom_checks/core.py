import fnmatch
import logging
import os
import re
import subprocess
import sys
import traceback
from functools import wraps

from custom_checks.parse_config import load_conf

PLATFORM = sys.platform
CONF = load_conf()

LOG = logging.getLogger(__name__)
LOG.setLevel(CONF.config.get('DEFAULT', 'log_level', fallback='INFO').upper())


def run_check_wrapper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            LOG.info('func {} - OK'.format(func.__name__))
            return func(*args, **kwargs)
        except Exception as error:
            LOG.error((
                f'There is an error with {func.__name__}'
                f'Error: {str(error)}'
                f'Full error: {traceback.format_exc()}'), exc_info=True)
            return 'There is an error with {}'.format(func.__name__)

    return wrapper


def is_check_enabled(check_name: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if CONF.config.getboolean('CHECK', check_name, fallback=False):
                return func(CONF, check_name, *args, **kwargs)

            LOG.warning(f'{check_name} is DISABLED or NOT FOUND in infra.conf')

        return wrapper

    return decorator


@run_check_wrapper
def check_package(package: str):
    check_result = f'unavailable platfrom: {PLATFORM}'
    LOG.warning(check_result)
    if PLATFORM == 'linux':
        cmd = f'dpkg -l | grep {package}'
        check_result = subprocess.getoutput(cmd)

    return True if check_result else False


@run_check_wrapper
def get_value_from_file(value, path):
    try:
        with open(path, 'r') as file:
            lines = file.readlines()

    except FileNotFoundError:
        return 'There is no file with this path: {}'.format(path)

    return ''.join([line for line in lines if value in line])


@run_check_wrapper
def file_to_dict(file_path, pattern=r'export (\w+)=(.*)'):
    def _parse_line(line):
        match = re.match(pattern, line)
        if match:
            key = match.group(1)
            value = match.group(2).strip('"')
            return key, value
        return None

    result_dict = {}

    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('export'):
                parsed_line = _parse_line(line)
                if parsed_line:
                    key, value = parsed_line
                    result_dict[key] = value

    return result_dict


@run_check_wrapper
def get_value_from_env(value, path):
    cmd = '. {} && env | grep {}'.format(path, value)
    output = subprocess.getoutput(cmd)
    if not output:
        return f'No {value} in {path}'
    return subprocess.getoutput(cmd)


def get_values_from_env(path, pattern=None):
    cmd = ["bash", "-c", f"diff <(env) <(source {path} && env)"]
    output = subprocess.run(cmd, capture_output=True, text=True)
    if output.returncode > 1:
        raise Exception(f"Error: {output.stderr}")

    result_dict = {}

    for line in output.stdout.split('\n'):
        if line.startswith('>'):
            k, v, *_ = line.replace('> ', '').split('=', 1)
            if pattern:
                pattern = re.compile(
                    pattern) if not isinstance(pattern, re.Pattern) else pattern
                if re.match(pattern, k):
                    result_dict[k] = v
                continue

            result_dict[k] = v
    return result_dict


def find_file_by_pattern(pattern, path):
    result = []
    for root, _, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    if result:
        return ''.join(result[0])

    return f'No file with name: {pattern}'


def save_to_file(check_name, content, path='endtest.txt'):
    init_part = f'<{check_name.upper()}>'.center(110, '-')
    print(init_part)
    if content:
        print(content)
        content = f'{init_part}\n{content}'
        with open(path, 'a') as file:
            file.write(content + '\n')
    else:
        print('unable to write result for %s' % check_name)
        LOG.warning('unable to write result for %s' % check_name)

@run_check_wrapper
def load_env(file_path='/root/admin-openrc'):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and line.startswith('export'):
                key, value = line.replace('export ', '').split('=')
                os.environ[key] = value
