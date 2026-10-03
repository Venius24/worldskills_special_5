# Belle Croissant Lyonnais — Django вариант Session 5

Здесь находится учебный Django проект с локальными моделями клиентов, заказов и продуктов (`api_mock`), управлением промоакциями и программой лояльности. Подробности и команды запуска — в [корневом README](../README.md).

Требуются Python 3.12+ и зависимости из `ws_5_django_ver/requirements.txt`. После установки из этой папки выполните `python manage.py migrate`, затем `python manage.py runserver`. Для проверки используйте `python manage.py test loyalty` и `python manage.py check`; тесты не затрагивают локальный `db.sqlite3`.

`python manage.py init_db` создаёт демонстрационные записи, предварительно удаляя текущие. Используйте только на отдельной тестовой базе. Настройки `DJANGO_SECRET_KEY`, `DJANGO_DEBUG` и `DJANGO_ALLOWED_HOSTS` читаются из переменных окружения. В production задайте свой ключ и `DJANGO_DEBUG=0`.
