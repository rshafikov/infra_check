import glob
import os

from icarus.checks.core import (is_check_enabled, run_check_wrapper,
                                save_to_file)


@run_check_wrapper
def search_cyrillic(conf):
    cobbler_directory = conf.config.get(
        'CHECK', 'cyrillic_search_dir', fallback='/var/www/html/')
    stdout = f'SEARCH_PATH: {cobbler_directory}\n'
    if not os.path.exists(cobbler_directory):
        raise FileNotFoundError(
            "file path {} doesn't exist".format(cobbler_directory))
    errors_with_files = 0
    files = glob.glob(cobbler_directory + '/**/*', recursive=True)
    for filename in files:
        if filename.endswith((
            '.gz',
            '.zip',
            '.bz2',
            '.deb',
            '.db',
            '.rpm',
            '.qcow2',
            '.img',
            '.xz',
            '.cz',
            'linux',
            'vmlinuz',
            'pxe',
            '.udeb')
        ):
            continue
        if os.path.isfile(filename):
            try:
                with open(filename, encoding='utf-8') as file:
                    content = file.readlines()
                    for line_number, line in enumerate(content, start=1):
                        for char_n, char in enumerate(line, start=0):
                            if char == '#':
                                break
                            if '\u0400' <= char <= '\u04FF':
                                cyrillic_word = ''
                                while (
                                    '\u0400' <= line[char_n] <= '\u04FF') or (
                                        line[char_n] == ' '):
                                    cyrillic_word += line[char_n]
                                    char_n += 1
                                stdout += (
                                    "Cyrrilic: "
                                    "'{}' in line {}:{} "
                                    "of file '{}'\n".format(
                                        cyrillic_word,
                                        line_number,
                                        char_n,
                                        filename
                                    )
                                )
                                break
            except Exception as error:
                errors_with_files += 1
                stdout = ('There is an error {} in file {}'.format(
                    error, filename))

    return stdout


@is_check_enabled(check_name='check_cyrillic')
def main_check_cyrillic(conf, check_name, *args, **kwargs):
    save_to_file(check_name=check_name, content=search_cyrillic(conf=conf))


if __name__ == '__main__':
    main_check_cyrillic()
