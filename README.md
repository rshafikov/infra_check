[![infra_check_workflow](https://github.com/rshafikov/infra_check/actions/workflows/main.yml/badge.svg)](https://github.com/rshafikov/infra_check/actions/workflows/main.yml)

## Проверка инфраструктуры заказчика на Cobbler

- Список проверок:

	1. Проверка DHCP-серверов

	2. Проверка DNS-серверов

	3. Проверка NTP-серверов

	4. Проверка MTU в определенной сети

	5. Проверка LDAP-серверов 

	6. Проверка доступности СХД-консолей

	7. Проверка наличия кириллицы в файлах конфигурации FB

	8. Проверка совпадение MAC-адрессов у разворачиваемой инфраструктуры 

	9. Проверка конфигурации будушего кластера OCFS2 (Не работает для версии 0.10.2)

<br>

### Установка

1. Архив `icarus-<version>.tar.gz` загружается на `Cobbler`.

- Для корретной работы проверок в ОС должны быть установленные следующие пакеты:
		
	- `ldap-utils`

    - `isc-dhcp-client`

- Установка выполняется в виртуальное окружение:

```shell
python3 -m venv venv
source venv/bin/activate
pip3 install icarus-<version>.tar.gz
```

### Запуск:

1. Перед запуском необходимо заполнить файл конфигурации `.infra.conf` и разместить его в домашней директории пользователя 

2. Образец конфигурации с примерами заполнения:

```toml
# every path should be either quoted with "''" or unquoted
# first line is default value, next line - your value
[DEFAULT]
log_level = INFO

# cyrillic_search_dir = '/var/www/html/' # default
cyrillic_search_dir = '/Users/rshafikov/Desktop/_work/modulo/cobbler/custom_checks/1.7/'

# mtu_dest = localhost ya.ru default
mtu_dest = ya.ru google.com

# mtu_size_step = '9000 100' default
mtu_size_step = 1600 200

# dhcpd_path = '/etc/dhcp/dhcpd.conf' # default
# san_servers = raise NoSANSetupError # can be empty
san_servers = ya.ru 127.0.0.1

# repo_pattern = REPO[0-9]? # default
# ntp_pattern =\w+_NTP[0-9]? # default
# dns_pattern = \w+_DNS[0-9]? # default
[INITRC]
# this section must be filled
initrc_ = '/home/user/cobbler/initrc_'
initrc_2 = '/home/user/cobbler/initrc_'
[KEYSTONE]
# this section must be filled for LDAP-check
keystone_conf_msad = '/home/user/cobbler/keystone.msad.conf'
keystone_conf_ipa = '/home/user/cobbler/keystone.ipa.conf'
[CHECK]
# checks with True state will be started
check_repo = True
check_cyrillic = True
check_macs = True
check_san = True
check_ntp = True
check_dns = True
check_mtu = True
check_ldap = False
# this checks don't work yet
check_ocfs2 = False
check_dhcp = False
```

3. Запустить проверку:

```shell
icarus-go
```

### Результаты и дебаг

1. Результаты будут собраны в файл `/tmp/endtest.txt` после запуска

2. Логи будут собраны в файл `/tmp/infra_check.log`

<br>
