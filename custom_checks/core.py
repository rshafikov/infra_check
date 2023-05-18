import logging
from functools import wraps


logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='/root/checks.log',
    filemode='a',
    level=logging.INFO
)


def run_check_wrapper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            logging.info('func {} - OK'.format(func.__name__))
            return result
        except Exception as error:
            logging.error(('There is an error with {}'.format(func.__name__),
                           'Full error: \n{}'.format(error)))
            return 'There is an error with {}'.format(func.__name__)

    return wrapper
