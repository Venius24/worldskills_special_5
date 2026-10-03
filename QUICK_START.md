# Быстрый старт

Актуальные команды для настольного варианта и Django приведены в [README.md](README.md). Это два самостоятельных интерфейса с отдельными SQLite базами.

Для настольного варианта создайте базу командой `python create_database.py`, затем запустите `promotions_management_app.py` или `loyalty_management_app.py`. Для Django выполните `python manage.py migrate`, затем `python manage.py runserver` из `ws_5_django_ver/belle_croissant`. Демонстрационное наполнение `manage.py init_db` удаляет текущие записи.
