import fnmatch
import logging
import os
import subprocess
import traceback
from functools import wraps

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='/var/log/infra_check.log',
    filemode='a',
    level=logging.INFO
)


def run_check_wrapper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            logging.info('func {} - OK'.format(func.__name__))
            return func(*args, **kwargs)
        except Exception as error:
            logging.error(('There is an error with {}'.format(func.__name__),
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
    if result != []:

        return ''.join(result[0])

    raise FileNotFoundError


def save_to_file(content='error: no content', path='endtest.txt'):
    print(content)
    with open(path, 'a') as file:
        file.write(content + '\n')
