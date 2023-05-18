## Скрипт проверки структуры заказчика

- Скрипт написан на bash и модули поверки структуры на python (кроме модуля проверки репозиториев они на bash)
 - Скрипт загружается на развернутый Firstboot в корень и папка custom_checks
	•	Для корретной работы проверок необходимы установленные пакеты в ОС такие как curl  и ldap-utils , isc-dhcp-client
	•	Выдать права скрипту chmod 755 launch_check.sh
	•	Необходимо сначала заполнить данные от заказчика в Firstboot . Далее запустить скрипт проверки. Он будет читать из конфигов поля для проверки доступности структуры заказчика.
	•	
	•	Действия скрипта
	1.	Сначала идет проверка установлены ли пакеты для работы скрипта в ОС
	2.	Затем идет парсинг полей в определенных файлах и вывод на экран найденных значений , запись в лог файл с названием endpars (создается в том же каталоге где запущен скрипт). 
	3.	Если конфиг файл отсутствует то на экран будет вывод строка NO FILE и путь файла к отсутствующему файлу. Выведены отдельно 2 функции для чистки временных файлов и подстановки цветного текста.
	4.	Bash модуль делает сurl запросы к найденным адресам репозиториев Далее проверки идут на Python модулях. 
	5.	Результаты собираются в файл endtest и выводятся на экран.
	6.	