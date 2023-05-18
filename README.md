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

	- Установка выполняется командой:
	```sh
		apt install curl ldap-utils isc-dhcp-client
	```

2. Распаковать архив:

```sh
	tar zxvf cobbler_check.tgz
```

3. Выдать права скрипту `launch_check.sh`:

```sh
	chmod 755 launch_check.sh
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

	1. Проверка установлены ли пакеты для работы скрипта в ОС

	2. Парсинг полей в определенных файлах и вывод на экран найденных значений
	
	3. Запись в лог файл с названием endpars (создается в том же каталоге где запущен скрипт). 
	
	4. Если конфиг файл отсутствует то на экран будет вывод строка NO FILE и путь файла к отсутствующему файлу. Выведены отдельно 2 функции для чистки временных файлов и подстановки цветного текста.

	5.	Bash модуль делает сurl запросы к найденным адресам репозиториев.
	
	6. Запуск проверок 

	7.	Результаты собираются в файл endtest и выводятся на экран.
