import logging
from functools import wraps
import subprocess


logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='checks.log',
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
                           'Full error: {}'.format(error)))
            return 'There is an error with {}'.format(func.__name__)

    return wrapper


@run_check_wrapper
def get_value_from_file(value, path):
    try:
        with open(path, 'r') as file:
            lines = file.readlines()

    except FileNotFoundError:
        return 'There is no file with this path: {}'.format(path)

    return '\n'.join([line for line in lines if value in line])


@run_check_wrapper
def get_value_from_env(value, path):
    cmd = 'source {} && env | grep {}'.format(path, value)
    check_value = run_check_wrapper(subprocess.getoutput)
    value = check_value(cmd)
    return value
