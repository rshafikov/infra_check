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

### Содержание архива:

- `dist/icarus-<version>.tar.gz` - python-пакет со всеми проверками

- `README.md` - инструкция

- `infra.conf` - пример файла конфигурации, который должен быть расположен в директории пользователя как скрытый файл `/home/user/.infra.conf`

- `deb1*_packages.tar` - необходимые deb-пакеты для работы модуля

### Установка

1. Архив `icar.tar` загружается на `Cobbler`.

- Для корретной работы проверок в ОС должны быть установленные следующие пакеты:
		
	- `ldap-utils`

- Если они не установлены, то проверка, используюшая данный пакет сообщит о его отсутствии. 

- Установите их из `deb1*_packages.tar`

- Установка выполняется в виртуальное окружение:

```shell
mkdir icar # создадим папку, что не мусорить
mv icar.tar.gz icar # переместим главный архив в созданную директорию
python3 -m venv venv # создадим виртуальное окружение
source venv/bin/activate # активируем окружение
pip3 install icarus-<version>.tar.gz # установим пакет
```

### Запуск:

1. Можно запустить проверку без заполнения файла конфигурации `.infra.conf`, взяв образец в главном архиве и разместить его в домашней директории пользователя 

```shell
# Находимся все еще в дирекотории icar
mv infra.conf ~/home/$USER/.infra.conf
```

2. Образец конфигурации с примерами заполнения:

```toml
# каждый путь до файла должен быть либо в таких '' кавычках, либо без
# не допускается ставить пробелы перед значением:
# НЕЛЬЗЯ:(начало строки) test = 1234 # лишний пробел перед "test"
# не допускается указывать значение и комментарий на одной строке:
# НЕЛЬЗЯ:(начало строки)test = 1234 # "комментарий" # комментарий и значение на одной строке
# ВСЕ закоменченные ниже строки - есть ЗНАЧЕНИЯ по-умолчанию

[DEFAULT]
# ПАРАМЕТР = ЗНАЧЕНИЕ ПО-УМОЛЧАНИЮ # не нужно раскоменчивать эти значения
# mtu_dest = localhost ya.ru # укажите ip/dn для проверки MTU, желательно один и тот же физический хост, но с интерфейсами из разных подсетей
# san_servers = raise NoSANSetupError # укажите хосты, которые хотите проверить
# log_level = INFO # можно поднять до уровня DEBUG
# mtu_size_step = 9000 100 # максимальный MTU для проверки, а также шаг проверки
# cyrillic_search_dir = '/var/www/html/' # путь до директории для рекурсивного поиска кириллицы
# dhcpd_path = /etc/dhcp/dhcpd.conf # путь до файла с содержанием MAC-адресов кобблера
# repo_pattern = REPO[0-9]? # паттерн регулярного выражения, для поиска репозиториев в INITRC-файлах
# ntp_pattern =\w+_NTP[0-9]? # паттерн регулярного выражения, для поиска NTP-серверов в INITRC-файлах
# dns_pattern = \w+_DNS[0-9]? # паттерн регулярного выражения, для поиска DNS-серверов в INITRC-файлах

san_servers = ya.ru google.com
mtu_size_step = 2000 100
mtu_dest = ya.ru google.com
[INITRC]
# REQUIRED
initrc_ = '/var/www/html/ha/stable/astra/1.7/initrc_'
# REQUIRED
initrc_2 = '/var/www/html/ha/stable/astra/1.7/initrc_2'
[KEYSTONE]
# заполните эту секцию путями до файлов с конфигурации внещних LDAP-доменов, включите "check_ldap"
# keystone_conf_msad = '/tmp/keystone/keystone.msad.conf'
# keystone_conf_ipa = '/tmp/keystone/keystone.ipa.conf'
[CHECK]
check_repo = True
check_cyrillic = True
check_macs = True
check_san = True
check_ntp = True
check_dns = True
check_mtu = True
check_ldap = False
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
