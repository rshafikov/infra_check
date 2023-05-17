import os
import glob


def search_cyrillic(cobbler_directory='./'):
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
                        for char_number, char in enumerate(line, start=0):
                            if char == '#':
                                break
                            if '\u0400' <= char <= '\u04FF':
                                cyrillic_word = ''
                                while '\u0400' <= line[char_number] <= '\u04FF' or line[char_number] == ' ':
                                    cyrillic_word += line[char_number]
                                    char_number += 1
                                print(
                                    "Found cyrillic symbols "
                                    "'{}' in line {}:{} "
                                    "of file '{}'".format(
                                        cyrillic_word,
                                        line_number,
                                        char_number,
                                        ('.../'+filename[(len(
                                            cobbler_directory)):])
                                    )
                                )
                                break
            except Exception as error:
                errors_with_files += 1
                print('There is an error {} in file {}'.format(
                    error, filename)
                    )
    # print(errors_with_files)


def main():
    search_cyrillic('/Users/rshafikov/Desktop/_work/modulo/fake_cobbler/')


if __name__ == '__main__':
    main()
