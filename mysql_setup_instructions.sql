-- Belle Croissant Lyonnais - MySQL Setup Instructions
-- Инструкции по настройке MySQL для Session 5

-- ============================================================================
-- ШАГ 1: Подключение к MySQL как root
-- ============================================================================
-- Выполните в командной строке:
-- mysql -u root -p

-- ============================================================================
-- ШАГ 2: Создание пользователя для приложения
-- ============================================================================

-- Создание пользователя (если не существует)
CREATE USER IF NOT EXISTS 'belle_user'@'localhost' IDENTIFIED BY 'Belle2026!';

-- Альтернативный вариант для старых версий MySQL:
-- DROP USER IF EXISTS 'belle_user'@'localhost';
-- CREATE USER 'belle_user'@'localhost' IDENTIFIED BY 'Belle2026!';

-- ============================================================================
-- ШАГ 3: Создание базы данных
-- ============================================================================

CREATE DATABASE IF NOT EXISTS belle_croissant_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- ============================================================================
-- ШАГ 4: Предоставление прав доступа
-- ============================================================================

-- Полные права на базу данных
GRANT ALL PRIVILEGES ON belle_croissant_db.* TO 'belle_user'@'localhost';

-- Применение изменений
FLUSH PRIVILEGES;

-- ============================================================================
-- ШАГ 5: Проверка созданного пользователя
-- ============================================================================

-- Показать всех пользователей
SELECT User, Host FROM mysql.user WHERE User = 'belle_user';

-- Показать права пользователя
SHOW GRANTS FOR 'belle_user'@'localhost';

-- ============================================================================
-- ШАГ 6: Проверка базы данных
-- ============================================================================

SHOW DATABASES LIKE 'belle_croissant_db';

USE belle_croissant_db;
SHOW TABLES;

-- ============================================================================
-- АЛЬТЕРНАТИВНЫЙ ВАРИАНТ: Если используете Docker
-- ============================================================================

-- Создайте файл docker-compose.yml:
/*
version: '3.8'
services:
  mysql:
    image: mysql:8.0
    container_name: belle_croissant_mysql
    environment:
      MYSQL_ROOT_PASSWORD: root_password
      MYSQL_DATABASE: belle_croissant_db
      MYSQL_USER: belle_user
      MYSQL_PASSWORD: Belle2026!
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./Session5_Database_Schema.sql:/docker-entrypoint-initdb.d/schema.sql

volumes:
  mysql_data:
*/

-- Запустите: docker-compose up -d

-- ============================================================================
-- УСТРАНЕНИЕ НЕПОЛАДОК
-- ============================================================================

-- Проблема: Access denied for user 'belle_user'
-- Решение 1: Проверьте пароль
-- Решение 2: Пересоздайте пользователя
DROP USER IF EXISTS 'belle_user'@'localhost';
CREATE USER 'belle_user'@'localhost' IDENTIFIED BY 'Belle2026!';
GRANT ALL PRIVILEGES ON belle_croissant_db.* TO 'belle_user'@'localhost';
FLUSH PRIVILEGES;

-- Проблема: Can't connect to MySQL server
-- Решение 1: Проверьте, что сервер запущен
-- В Windows: services.msc -> MySQL
-- В Linux: sudo systemctl status mysql
-- В macOS: brew services list

-- Проблема: Unknown database 'belle_croissant_db'
-- Решение:
CREATE DATABASE IF NOT EXISTS belle_croissant_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- ============================================================================
-- ДОПОЛНИТЕЛЬНЫЕ НАСТРОЙКИ (опционально)
-- ============================================================================

-- Увеличение лимита соединений (если нужно)
SET GLOBAL max_connections = 200;

-- Включение логирования запросов (для отладки)
SET GLOBAL general_log = 'ON';
SET GLOBAL log_output = 'TABLE';

-- Просмотр логов
SELECT * FROM mysql.general_log ORDER BY event_time DESC LIMIT 20;

-- ============================================================================
-- ПРОВЕРКА ПОДКЛЮЧЕНИЯ ИЗ КОМАНДНОЙ СТРОКИ
-- ============================================================================

-- После настройки попробуйте подключиться:
-- mysql -u belle_user -pBelle2026! belle_croissant_db

-- Или с запросом пароля:
-- mysql -u belle_user -p belle_croissant_db

-- ============================================================================
-- РЕЗЕРВНОЕ КОПИРОВАНИЕ
-- ============================================================================

-- Создание резервной копии (выполнить в командной строке):
-- mysqldump -u belle_user -p belle_croissant_db > backup.sql

-- Восстановление из резервной копии:
-- mysql -u belle_user -p belle_croissant_db < backup.sql

-- ============================================================================
-- ОЧИСТКА (если нужно начать заново)
-- ============================================================================

-- ВНИМАНИЕ: Это удалит все данные!
-- Раскомментируйте, если уверены:

-- DROP DATABASE IF EXISTS belle_croissant_db;
-- DROP USER IF EXISTS 'belle_user'@'localhost';

-- После этого выполните шаги 2-4 снова

-- ============================================================================
-- ГОТОВО!
-- ============================================================================

-- Теперь вы можете:
-- 1. Выполнить Session5_Database_Schema.sql
-- 2. Запустить initialize_loyalty_data.py
-- 3. Использовать приложения Session5_PromotionsApp.exe и Session5_LoyaltyApp.exe