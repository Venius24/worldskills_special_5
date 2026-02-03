# Belle Croissant Lyonnais - Система управления промоакциями и лояльностью

## 📋 Описание проекта

Django-приложение для управления промоакциями и программой лояльности французской пекарни Belle Croissant Lyonnais.

**WorldSkills 2024 - Session 5**

## ✨ Возможности

### 🏷️ Управление промоакциями
- Создание и редактирование промоакций
- Процентные и фиксированные скидки
- Применение к нескольким продуктам
- Система приоритетов
- **Мастер разрешения конфликтов (5 шагов)**:
  1. Список всех конфликтов
  2. Детальная информация о конфликте
  3. Изменение приоритета
  4. Корректировка дат или удаление продуктов
  5. Отмена создания промоакции

### ⭐ Программа лояльности
- Три уровня членства (Basic, Silver, Gold)
- Автоматический расчёт баллов по заказам
- Бонусы за покупки в период промоакций (+5 баллов)
- Бонусы в день годовщины регистрации (+25 баллов)
- Обмен баллов на награды (1000 баллов):
  - Скидка 5€ на следующую покупку
  - Скидка 10% на следующую покупку
  - Повышение уровня членства
- Поиск и фильтрация клиентов
- История транзакций и обменов

## 🛠️ Технологии

- **Backend**: Django 4.2+
- **Database**: SQLite3
- **Frontend**: Bootstrap 5, Bootstrap Icons
- **Python**: 3.8+

## 📦 Установка

### 1. Создание структуры проекта

```bash
# Создаём главную папку проекта
mkdir belle_croissant_project
cd belle_croissant_project

# Создаём виртуальное окружение
python -m venv venv

# Активируем виртуальное окружение
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Устанавливаем Django
pip install django

# Создаём Django проект
django-admin startproject belle_croissant .

# Создаём приложения
python manage.py startapp promotions
python manage.py startapp loyalty
python manage.py startapp api_mock

# Создаём папку для шаблонов
mkdir templates
mkdir templates/promotions
mkdir templates/loyalty
```

### 2. Копирование файлов

Скопируйте содержимое артефактов в соответствующие файлы:

**Конфигурация проекта:**
- `belle_croissant/settings.py`
- `belle_croissant/urls.py`

**Приложение Promotions:**
- `promotions/models.py`
- `promotions/views.py`
- `promotions/urls.py`
- `promotions/admin.py`

**Приложение Loyalty:**
- `loyalty/models.py`
- `loyalty/views.py`
- `loyalty/urls.py`
- `loyalty/admin.py`

**Приложение API Mock:**
- `api_mock/models.py`
- `api_mock/views.py`
- `api_mock/urls.py`
- `api_mock/admin.py`

**Шаблоны:**
- `templates/base.html`
- `templates/index.html`
- `templates/promotions/list.html`
- `templates/promotions/conflict_wizard.html`
- `templates/loyalty/list.html`
- `templates/loyalty/detail.html`
- `templates/loyalty/confirm_recalculation.html`
- `templates/loyalty/redeem.html`

**Скрипты:**
- `initialize_database.py` (в корне проекта)
- `Session5_DatabaseVerification.sql`
- `Session5_DatabaseCredentials.txt`

### 3. Инициализация базы данных

```bash
# Создание миграций
python manage.py makemigrations

# Применение миграций
python manage.py migrate

# Создание суперпользователя (для админки)
python manage.py createsuperuser
# Введите логин, email и пароль

# Инициализация данных (1000 клиентов, продукты, заказы, промоакции)
python manage.py shell < initialize_database.py
```

### 4. Запуск сервера

```bash
python manage.py runserver
```

Откройте в браузере: http://127.0.0.1:8000/

## 📱 Интерфейсы

### Главная страница
`/` - Главная страница с описанием и статистикой

### Промоакции
- `/promotions/` - Список промоакций (CRUD)
- `/promotions/conflict-wizard/` - Мастер разрешения конфликтов

### Программа лояльности
- `/loyalty/` - Список клиентов с поиском и фильтрацией
- `/loyalty/customer/<id>/` - Детали клиента и баллы
- `/loyalty/customer/<id>/recalculate/` - Пересчёт баллов
- `/loyalty/customer/<id>/confirm-recalculation/` - Подтверждение пересчёта
- `/loyalty/customer/<id>/redeem/` - Обмен баллов на награды

### API (Mock)
- `/api/customers/` - Список клиентов
- `/api/customers/<id>/` - Детали клиента
- `/api/products/` - Список продуктов
- `/api/orders/` - Список заказов
- `/api/orders/<id>/` - Детали заказа

### Административная панель
`/admin/` - Django Admin (используйте созданного суперпользователя)

## 🗄️ Структура базы данных

### Таблицы

**Промоакции:**
- `promotions` - Промоакции
- `promotion_conflicts` - Конфликты промоакций

**Программа лояльности:**
- `loyalty_program` - Программа лояльности клиентов
- `loyalty_transactions` - Транзакции баллов
- `reward_redemptions` - Обмены наград

**Mock API:**
- `mock_customers` - Клиенты (1000 записей)
- `mock_products` - Продукты (19 позиций)
- `mock_orders` - Заказы (случайное количество)
- `mock_order_items` - Элементы заказов

### Проверка базы данных

```bash
# Через SQLite CLI
sqlite3 db.sqlite3 < Session5_DatabaseVerification.sql

# Через Django shell
python manage.py dbshell < Session5_DatabaseVerification.sql
```

## 📊 Тестовые данные

После инициализации БД создаются:

- ✅ **1000 клиентов** (70% Basic, 20% Silver, 10% Gold)
- ✅ **250 активных участников** с баллами (50-1500)
- ✅ **19 продуктов** (круассаны, выпечка, хлеб, торты, напитки)
- ✅ **10+ промоакций** (включая конфликтные)
- ✅ **Одна промоакция с ошибкой в датах** (для тестирования)
- ✅ **Случайные заказы** для всех клиентов

## 🎯 Основные функции

### Мастер разрешения конфликтов

При создании или редактировании промоакции система автоматически проверяет конфликты:
- Одинаковый приоритет
- Пересечение дат
- Одинаковые применимые продукты

Мастер предлагает 5 шагов для разрешения:
1. Просмотр всех конфликтов
2. Детальная информация с временной шкалой
3. Изменение приоритета промоакции
4. Корректировка дат или удаление продуктов
5. Отмена создания (если не удалось разрешить)

### Расчёт баллов лояльности

Система автоматически рассчитывает баллы по формуле:

**Базовые баллы:**
- Basic: 10 баллов за каждые 10€
- Silver: 12 баллов за каждые 10€
- Gold: 15 баллов за каждые 10€

**Бонусы:**
- +5 баллов за покупку во время промоакции
- +25 баллов за покупку в день годовщины регистрации

### Обмен наград

При накоплении 1000+ баллов клиент может обменять их на:
1. **Скидку 5€** - создаётся промоакция на 30 дней
2. **Скидку 10%** - создаётся промоакция на 30 дней
3. **Повышение статуса** - постоянное улучшение (если возможно)

## 🔧 Дополнительные команды

```bash
# Создание дампа базы данных
python manage.py dumpdata > backup.json

# Загрузка дампа
python manage.py loaddata backup.json

# Очистка базы данных
python manage.py flush

# Запуск тестов
python manage.py test

# Сбор статических файлов (для продакшена)
python manage.py collectstatic
```

## 📝 Примечания

### Фиктивные данные
- Все данные клиентов, заказов и продуктов - **сгенерированы**
- Email'ы в формате: `имя.фамилия{номер}@example.com`
- Заказы распределены случайным образом за последние 3 года
- Даты регистрации клиентов - за последние 3 года

### Безопасность
⚠️ **Это учебный проект!** Для продакшена необходимо:
- Изменить `SECRET_KEY` в `settings.py`
- Установить `DEBUG = False`
- Настроить `ALLOWED_HOSTS`
- Использовать PostgreSQL вместо SQLite
- Добавить аутентификацию пользователей
- Настроить HTTPS

## 🆘 Решение проблем

### Ошибка "table already exists"
```bash
# Удалите базу данных и миграции
rm db.sqlite3
rm -rf promotions/migrations/*
rm -rf loyalty/migrations/*
rm -rf api_mock/migrations/*

# Создайте файлы __init__.py в папках migrations
touch promotions/migrations/__init__.py
touch loyalty/migrations/__init__.py
touch api_mock/migrations/__init__.py

# Повторите миграции
python manage.py makemigrations
python manage.py migrate
```

### Ошибка импорта модулей
Убедитесь, что все приложения добавлены в `INSTALLED_APPS` в `settings.py`:
```python
INSTALLED_APPS = [
    # ...
    'promotions',
    'loyalty',
    'api_mock',
]
```

### Шаблоны не найдены
Проверьте, что папка `templates` указана в `TEMPLATES['DIRS']`:
```python
TEMPLATES = [
    {
        'DIRS': [BASE_DIR / 'templates'],
        # ...
    }
]
```

## 👨‍💻 Автор

Проект разработан для WorldSkills 2024 - Session 5

## 📄 Лицензия

Учебный проект - свободное использование