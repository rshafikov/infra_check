# Проверка инфраструктуры заказчика на Cobbler

- Данные проверки условно разделены на две части: 

	1. Парсинг данных из init конфигурации `FirstBoot`, реализовано на `bash`, файл `launch_check.sh`
	
	2. Запуск проверок из папки `/custom_checks`, релизовано на `python`

- Список проверок:

	1. Проверка DHCP-серверов

	2. Проверка DNS-серверов

	3. Проверка NTP-серверов

	4. Проверка MTU в определенной сети

	5. Проверка LDAP-серверов 

	6. Проверка СХД

	7. Проверка наличия кириллицы в файлах конфигурации FB

	8. Проверка совпадение MAC-адрессов у разворачиваемой инфраструктуры 

<br>

# Запуск

 1.	Архив `cobbler_check.tgz` загружается на развернутый `Firstboot` в корень `/root/`.

	- Для корретной работы проверок необходимы установленные пакеты в ОС такие как:
		
		`curl`, `ldap-utils`, `isc-dhcp-client`
	- Наличие пакетов проверяет утилита при ее первом  запуске
	- Если пакеты отсутствуют то их надо установить	

	- Установка выполняется командой:
	```
		apt install curl ldap-utils isc-dhcp-client
	```
        - Если отсутствуют репозитории то можно скомпилировать из исходных кодов
        - Пример для компиляции пакета curl
	        tar -xvzf curl.tar.gz
               ./configure
                make
                make install

2. Распаковать архив:

```sh
	tar zxvf cobbler_check.tgz
```

3. Выдать права скрипту `launch_check.sh`, активировать виртуальное окружение и проверить его:

```sh
	chmod 755 launch_check.sh
	source /root/custom_checks/venv/bin/activate
	diff -s requirements.txt <(pip freeze)
	# пример вывода: Files requirements.txt and /dev/fd/63 are identical
```
	
4. Заполнить данные от заказчика в `FirstBoot`. 

5. Запустить скрипт проверки:

```sh
	./launch_check.sh
```

6. Проанализировать результаты работы скрипта, при необходимости внести правки в `FirstBoot.

	- Логи работы проверок на находятся по пути `/root/checks.log`. В них детально описаны все вызванные python-функции, а также полученные ошибки. 

	- Принцип работы проверок можно посмотреть в `/root/custom_checks/`

<br>

# Примечание. Принцип работы проверок

	1. При запуске скрипта выходит диалог, который предлагает выбрать версию устанавливаемой ОС Астра
	Необходимо с клавиатуры ввести цифру  1 -  Астра 1.6 или 2 - Астра 1.7.
	При нажатии другой клавиши скрипт завершит работу и попросит ввести правильные версии.

	2. Проверка установлены ли пакеты для работы скрипта в ОС

	3. Парсинг полей в определенных файлах и вывод на экран найденных значений
	
	4. Запись в лог файл с названием endpars (создается в том же каталоге где запущен скрипт). 
	
	5. Если конфиг файл отсутствует то на экран будет вывод строка NO FILE и путь файла к отсутствующему файлу. Выведены отдельно 2 функции для чистки временных файлов и подстановки цветного текста.

	6. Bash модуль делает сurl запросы к найденным адресам репозиториев.
	
	7. Запуск проверок 

	8. Результаты собираются в файл endtest и выводятся на экран.

	

