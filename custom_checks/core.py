import fnmatch
import logging
import os
import subprocess
import traceback
from functools import wraps

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    # filename='/var/log/infra_check.log',
    filename='infra_check.log',
    filemode='w',
    level=logging.INFO
)


def run_check_wrapper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(__name__)
        try:
            logger.info('func {} - OK'.format(func.__name__))
            return func(*args, **kwargs)
        except Exception as error:
            logger.error(('There is an error with {}'.format(func.__name__),
                           'Error: {}'.format(error),
                           'Full error: {}'.format(traceback.format_exc())))
            return 'There is an error with {}'.format(func.__name__)

    return wrapper


@run_check_wrapper
def get_value_from_file(value, path):
    try:
        with open(path, 'r') as file:
            lines = file.readlines()

    except FileNotFoundError:
        return 'There is no file with this path: {}'.format(path)

    return ''.join([line for line in lines if value in line])


@run_check_wrapper
def get_value_from_env(value, path):
    cmd = '. {} && env | grep {}'.format(path, value)
    return subprocess.getoutput(cmd)


@run_check_wrapper
def find_file_by_pattern(pattern, path):
    result = []
    for root, _, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    if result:
        return ''.join(result[0])

    raise FileNotFoundError


def save_to_file(content='error: no content', path='endtest.txt'):
    print(content)
    with open(path, 'a') as file:
        file.write(content + '\n')


@run_check_wrapper
def load_env(file_path='/root/admin-openrc'):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and line.startswith('export'):
                key, value = line.replace('export ', '').split('=')
                os.environ[key] = value
