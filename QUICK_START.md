# 🚀 Быстрый старт - Belle Croissant Lyonnais
## Система управления промоакциями и лояльностью (SQLite)

---

## ⚡ Запуск за 3 минуты

### 1️⃣ Установка зависимостей (30 сек)

```bash
pip install -r requirements.txt
```

### 2️⃣ Создание базы данных (30 сек)

```bash
python create_database.py
```

### 3️⃣ Инициализация данных (30 сек)

```bash
python initialize_loyalty_data.py
```

### 4️⃣ Запуск приложений (готово!)

```bash
# Приложение промоакций
python promotions_management_app.py

# Приложение лояльности
python loyalty_management_app.py
```

---

## 📁 Структура проекта

```
belle-croissant-session5/
│
├── belle_croissant.db              # База данных SQLite (создается автоматически)
│
├── SQL Scripts:
│   ├── Session5_Database_Schema.sql         # Схема БД
│   └── Session5_DatabaseVerification.sql    # Проверочные запросы
│
├── Python Scripts:
│   ├── create_database.py                   # Создание БД
│   ├── initialize_loyalty_data.py           # Инициализация данных
│   ├── verify_database.py                   # Проверка БД
│   ├── promotions_management_app.py         # Приложение промоакций
│   └── loyalty_management_app.py            # Приложение лояльности
│
└── Documentation:
    ├── README_RU.md                         # Полное руководство
    ├── QUICK_START.md                       # Этот файл
    ├── BUILD_INSTRUCTIONS.md                # Создание .exe
    ├── SESSION5_DatabaseCredentials.txt     # Информация о БД
    ├── PROJECT_SUMMARY.md                   # Описание проекта
    └── requirements.txt                     # Python зависимости
```

---

## ✅ Что получите после установки

### База данных `belle_croissant.db` с:
- ✅ 12 тестовых промоакций (включая одну с неверными датами)
- ✅ 500 клиентов в программе лояльности
- ✅ 250 клиентов с баллами от 50 до 1500
- ✅ Все индексы и триггеры

### Два готовых приложения:
- ✅ **Session5_PromotionsApp** - управление промоакциями с мастером конфликтов
- ✅ **Session5_LoyaltyApp** - управление программой лояльности

---

## 🎯 Основные команды

### Создание и проверка БД

```bash
# Создать новую БД
python create_database.py

# Проверить БД
python verify_database.py

# Заполнить данными лояльности
python initialize_loyalty_data.py
```

### Работа с SQLite напрямую

```bash
# Открыть БД в командной строке
sqlite3 belle_croissant.db

# Показать таблицы
.tables

# Запрос
SELECT * FROM Promotions;

# Выход
.quit
```

### Создание .exe файлов

```bash
# Приложение промоакций
pyinstaller --onefile --windowed --name Session5_PromotionsApp promotions_management_app.py

# Приложение лояльности
pyinstaller --onefile --windowed --name Session5_LoyaltyApp loyalty_management_app.py
```

Файлы будут в папке `dist/`

---

## 🔑 Ключевые особенности

### SQLite - Простота и удобство
- 🎯 **Нулевая конфигурация** - не нужен MySQL сервер
- 📦 **Один файл** - вся БД в `belle_croissant.db`
- 🚀 **Встроен в Python** - дополнительные пакеты не нужны
- 💾 **Простое резервирование** - скопируйте файл .db
- 🌍 **Кроссплатформенность** - работает везде

### Приложение промоакций
- ➕ Добавление/редактирование/удаление промоакций
- 🔍 Автоматическое обнаружение конфликтов
- 🧙 Мастер разрешения конфликтов (5 шагов)
- ✅ Полная валидация данных

### Приложение лояльности
- 👥 Управление 500 клиентами
- 🔎 Поиск и сортировка
- 🔢 Автоматический пересчет баллов
- 🎁 Система вознаграждений (скидки, повышение статуса)
- 📊 Детальная разбивка начисления

---

## ⚠️ Частые вопросы

### Где база данных?
В той же папке, где запускаете скрипты: `belle_croissant.db`

### Как сбросить базу данных?
```bash
# Удалить старую
rm belle_croissant.db  # Linux/Mac
del belle_croissant.db  # Windows

# Создать новую
python create_database.py
python initialize_loyalty_data.py
```

### Как посмотреть данные в БД?
1. Скачайте DB Browser for SQLite: https://sqlitebrowser.org/
2. Откройте файл `belle_croissant.db`
3. Просматривайте и редактируйте данные визуально

### Как сделать резервную копию?
Просто скопируйте файл:
```bash
cp belle_croissant.db belle_croissant_backup.db
```

### Приложение не находит БД?
Убедитесь, что файл `belle_croissant.db` находится в той же папке, откуда запускаете приложение.

---

## 📊 Проверка установки

Запустите проверочный скрипт:
```bash
python verify_database.py
```

Вы должны увидеть:
- ✅ База данных создана
- ✅ 2 таблицы (Promotions, LoyaltyProgram)
- ✅ 12 промоакций
- ✅ 500 клиентов
- ✅ 250 клиентов с баллами

---

## 🎓 Дальнейшие шаги

1. **Изучите приложения:**
   - Запустите оба приложения
   - Попробуйте все функции
   - Создайте тестовые промоакции
   - Поэкспериментируйте с баллами лояльности

2. **Создайте .exe файлы:**
   - Следуйте инструкциям в `BUILD_INSTRUCTIONS.md`
   - Протестируйте на другом компьютере

3. **Изучите код:**
   - `promotions_management_app.py` - 2000+ строк
   - `loyalty_management_app.py` - 1800+ строк
   - Все функции документированы

4. **Интеграция с реальным API:**
   - Замените mock-функции на реальные HTTP запросы
   - См. комментарии в коде

---

## 💡 Полезные советы

### Разработка
- Используйте `verify_database.py` для проверки данных
- DB Browser for SQLite для визуального просмотра
- PyCharm/VSCode для редактирования кода

### Тестирование
- Создайте тестовую копию БД
- Проверьте все граничные случаи
- Тестируйте на чистой системе

### Деплой
- Создайте .exe файлы
- Включите `belle_croissant.db` в пакет
- Добавьте README для пользователей

---

## 📞 Нужна помощь?

1. **Проверьте документацию:**
   - `README_RU.md` - полное руководство
   - `BUILD_INSTRUCTIONS.md` - создание .exe
   - `PROJECT_SUMMARY.md` - обзор проекта

2. **Проверьте базу данных:**
   ```bash
   python verify_database.py
   ```

3. **Пересоздайте БД:**
   ```bash
   python create_database.py
   python initialize_loyalty_data.py
   ```

---

## 🏆 Готово к использованию!

Все компоненты установлены и готовы к работе. Удачи на WorldSkills Competition 2024! 🎉

---

**Время установки:** ~3 минуты  
**Сложность:** 🟢 Легко  
**Python версия:** 3.8+  
**ОС:** Windows / Linux / macOS