[![infra_check_workflow](https://github.com/rshafikov/infra_check/actions/workflows/main.yml/badge.svg)](https://github.com/rshafikov/infra_check/actions/workflows/main.yml)

# Проверка инфраструктуры заказчика на Cobbler

- Данные проверки условно разделены на две части: 

	1. Парсинг данных из init конфигурации `FirstBoot`, реализовано на `bash`, файл `launch_check.sh`
	
	2. Запуск проверок из папки `/custom_checks`, релизовано на `python`, требуются root права для 

- Список проверок:

	1. Проверка DHCP-серверов

	2. Проверка DNS-серверов

	3. Проверка NTP-серверов

	4. Проверка MTU в определенной сети

	5. Проверка LDAP-серверов 

	6. Проверка СХД

	7. Проверка наличия кириллицы в файлах конфигурации FB

	8. Проверка совпадение MAC-адрессов у разворачиваемой инфраструктуры 

	9. Проверка конфигурации будушего кластера OCFS2 для nova

<br>

# Запуск

 1.	Архив `infra_check_<>.tar` загружается на развернутый `Firstboot` в корень `/root/`.

- Для корретной работы проверок необходимы установленные пакеты в ОС такие как
		
	`curl`, `ldap-utils`, `isc-dhcp-client`

- Установка может быть выполнена без подключенных репозиториев следующим образом:

```shell
# Проверьте релиз ОС
lsb_release -a
# Распакуйте сначала скачанный архив
tar xvf infra_check.tar
cd infra_checks
# Для Debian 10
tar xvf deb10_packages.tar
# Для Debian 11
tar xvf deb11_packages.tar
apt-get install ./*.deb
```

2. Настроить окружение:

```sh
# если есть подключенный репозиторий для скачивания и установки python пакетов
python3 -m venv venv
. venv/bin/activate
pip3 install -r requirements.txt
# если нет, то распаковываем venv с вашей версией питона:
python3 -V
tar xvf venv_<your_python_version>
. venv/bin/activate
```

3. Запустить скрипт проверки:

```sh
./launch_check.sh
```

4Проанализировать результаты работы скрипта, при необходимости внести правки в `FirstBoot.

	- Логи работы проверок на находятся по пути `.../<PWD>/infra_check.log`. В них детально описаны все вызванные python-функции, а также полученные ошибки. 

	- Скрипты проверок можно посмотреть в `/root/custom_checks/`

<br>

# Примечание. Принцип работы проверок

	1. При запуске скрипта выходит диалог, который предлагает выбрать версию устанавливаемой ОС Астра
	Необходимо с клавиатуры ввести цифру 1 -  Астра 1.6 или 2 - Астра 1.7.
	При нажатии другой клавиши скрипт завершит работу и попросит ввести правильные версии.

	2. Проверка установлены ли пакеты для работы скрипта в ОС

	3. Парсинг полей в определенных файлах и вывод на экран найденных значений 
	
	4. Запуск проверок 

	5. Результаты выводятся на экран, а также в файл /root/endtest.txt
