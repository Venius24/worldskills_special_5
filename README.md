# Belle Croissant Lyonnais — учебная работа, Session 5

Репозиторий содержит два варианта интерфейса для демонстрационной системы промоакций и лояльности: настольные приложения PyQt с SQLite в корне и отдельный веб-вариант Django в `ws_5_django_ver/belle_croissant`. Их базы данных и команды запуска различаются.

## Настольный вариант

Создайте окружение Python и установите зависимости из корневого `requirements.txt`:

```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe create_database.py
.\venv\Scripts\python.exe verify_database.py
.\venv\Scripts\python.exe promotions_management_app.py
# Во втором терминале:
.\venv\Scripts\python.exe loyalty_management_app.py
```

`create_database.py` работает с `belle_croissant.db` в текущей папке и при наличии файла спрашивает о пересоздании. Сохраните свою базу перед подтверждением. `setup_all.py` также может пересоздать базу; он не нужен для обычного запуска. На Linux/macOS путь к Python в окружении — `venv/bin/python`.

## Веб-вариант Django

Для Django 6.0.1 из вложенного `requirements.txt` нужен Python 3.12+.

```powershell
cd ws_5_django_ver\belle_croissant
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r ..\requirements.txt
$env:DJANGO_SECRET_KEY = 'local-development-key-replace-me'
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

Откройте `http://127.0.0.1:8000/`. Пустая база создаётся миграциями. Для демонстрационных записей можно запустить `manage.py init_db`, **только если допустимо удалить текущие записи**: эта команда очищает таблицы перед заполнением. Настройки Django: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG` (`1` по умолчанию), `DJANGO_ALLOWED_HOSTS` (список через запятую). Пример значений — `.env.example`; файл не загружается автоматически. При `DJANGO_DEBUG=0` секретный ключ обязателен.

Проверка веб-варианта без изменения локальной базы:

```powershell
python manage.py test loyalty
python manage.py check
```

Тесты используют временную базу. Проект учебный: настройки production, доступы и реальные внешние интеграции здесь не подтверждены. Локальные `.db`, `db.sqlite3` и `Session5_DatabaseCredentials.txt` сохранены на диске, но исключены из отслеживания Git. Если файл credentials содержал действующие пароли, их следует сменить до публикации: удаление из index не удаляет их из истории.
