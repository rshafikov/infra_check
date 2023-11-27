import unittest
from unittest.mock import patch
from tempfile import NamedTemporaryFile
from pathlib import Path
import logging

from custom_checks.parse_config import Config, ConfigurationException, FileNotFound, load_conf

logging.disable(logging.CRITICAL)


class TestConfig(unittest.TestCase):

    def setUp(self):
        self.temp_config_file = NamedTemporaryFile(delete=False)
        self.temp_config_file.write(b"[INITRC]\nkey1 = value1\nkey2 = value2\n")
        self.temp_config_file.write(b"[BIND9]\nkey3 = value3\nkey4 = value4\n")
        self.temp_config_file.close()
        self.config = Config(self.temp_config_file.name)

    def tearDown(self):
        Path(self.temp_config_file.name).unlink()

    def test_init_with_default_path(self):
        self.assertEqual(
            self.config.path,
            Path(self.temp_config_file.name))

    def test_init_with_custom_path(self):
        custom_path = Path('./custom.conf')
        config = Config(custom_path)
        self.assertEqual(config.path, custom_path)

    def test_get_section_existing(self):
        section_data = self.config.get_section('INITRC')
        self.assertEqual(
            section_data, {
                'key1': "DOESN'T EXIST value1",
                'key2': "DOESN'T EXIST value2"}
        )

    def test_get_section_nonexistent(self):
        with self.assertRaises(ConfigurationException):
            self.config.get_section('NONEXISTENT_SECTION')

    def test_is_section_existing(self):
        self.assertTrue(self.config.is_section('INITRC'))

    def test_is_section_nonexistent(self):
        config = Config(Path(self.temp_config_file.name))
        self.assertFalse(config.is_section('NONEXISTENT_SECTION'))

    @patch('custom_checks.parse_config.Config._check_path')
    def test_read_existing_sections(self, mock_check_path):
        self.config.read()
        self.assertEqual(self.config.params, {
            'INITRC': {'key1': mock_check_path.return_value, 'key2': mock_check_path.return_value},
            'BIND9': {'key3': mock_check_path.return_value, 'key4': mock_check_path.return_value}
        })

    @patch('custom_checks.parse_config.Config._check_path')
    def test_read_nonexistent_section(self, mock_check_path):
        with patch.object(self.config, 'get_section', side_effect=ConfigurationException('Error')):
            self.config.read()
        self.assertEqual(self.config.params, {})

    @patch('custom_checks.parse_config.Config._check_path', return_value='mocked_path')
    def test_check_path_existing_file(self, mock_check_path):
        result = Config._check_path(self.temp_config_file.name)
        self.assertEqual(result, 'mocked_path')

    @patch('custom_checks.parse_config.LOG')
    def test_check_path_nonexistent_file(self, mock_log):
        result = Config._check_path('nonexistent_file.txt')
        self.assertEqual(result, 'DOESN\'T EXIST nonexistent_file.txt')
        self.assertTrue(mock_log.warning.called)


class TestLoadConf(unittest.TestCase):

    @patch('custom_checks.parse_config.Config')
    @patch('custom_checks.parse_config.CONF_PATH', Path('existing_file.conf'))
    def test_load_conf_existing_file(self, mock_config):
        with self.assertRaises(FileNotFound):
            load_conf()

    @patch('custom_checks.parse_config.CONF_PATH', Path('nonexistent_file.conf'))
    def test_load_conf_nonexistent_file(self):
        with self.assertRaises(FileNotFound):
            load_conf()


if __name__ == '__main__':
    unittest.main()
