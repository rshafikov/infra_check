import unittest
from unittest.mock import patch
from tempfile import NamedTemporaryFile
from pathlib import Path
import logging

from icarus.checks.parse_config import Config, ConfigurationException, FileNotFound, load_conf

logging.disable(logging.CRITICAL)


def create_custom_file(name):
    temp_config_file = NamedTemporaryFile(
        prefix=name,
        delete=False
    )
    temp_config_file.write(b"[INITRC]\nkey1 = value1\nkey2 = value2\n")
    temp_config_file.write(b"[BIND9]\nkey3 = value3\nkey4 = value4\n")
    temp_config_file.close()
    return temp_config_file, temp_config_file.name


class TestConfig(unittest.TestCase):

    def setUp(self):
        self.temp_config_file, self.temp_file_name = create_custom_file('tmp.file')
        self.config = Config(self.temp_config_file.name)

    def tearDown(self):
        Path(self.temp_config_file.name).unlink()

    def test_init_with_default_path(self):
        self.assertEqual(
            self.config.path,
            Path(self.temp_config_file.name))

    def test_init_with_custom_path(self):
        custom_file, custom_name = create_custom_file('aboba.txt')
        config = Config(custom_name)
        self.assertEqual(config.path.as_posix(), custom_name)

    def test_get_section_existing(self):
        section_data = self.config.get_section('INITRC')
        self.assertEqual(
            section_data, {
                'key1': "value1",
                'key2': "value2"}
        )

    def test_get_section_nonexistent(self):
        with self.assertRaises(ConfigurationException):
            self.config.get_section('NONEXISTENT_SECTION')

    def test_is_section_existing(self):
        self.assertTrue(self.config.is_section('INITRC'))

    def test_is_section_nonexistent(self):
        config = Config(self.temp_config_file.name)
        self.assertFalse(config.is_section('NONEXISTENT_SECTION'))

    @patch('icarus.checks.parse_config.Config._check_path')
    def test_read_nonexistent_section(self, mock_check_path):
        with patch.object(self.config, 'get_section', side_effect=ConfigurationException('Error')):
            self.config.read()
        self.assertEqual(self.config.params, {})

    @patch('icarus.checks.parse_config.Config._check_path', return_value='mocked_path')
    def test_check_path_existing_file(self, mock_check_path):
        result = Config._check_path(self.temp_config_file.name)
        self.assertEqual(result, 'mocked_path')

    @patch('icarus.checks.parse_config.LOG')
    def test_check_path_nonexistent_file(self, mock_log):
        with self.assertRaises(FileNotFound):
            Config._check_path('nonexistent_file.txt')
        self.assertTrue(mock_log.warning.called)


class TestLoadConf(unittest.TestCase):

    def test_load_conf_existing_file(self):
        load_conf()

    def test_load_conf_nonexistent_file(self):
        with self.assertRaises(FileNotFound):
            load_conf('not_existing_file.conf')


if __name__ == '__main__':
    unittest.main()
