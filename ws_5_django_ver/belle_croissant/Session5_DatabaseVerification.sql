-- ============================================================
-- ПРОВЕРКА БАЗЫ ДАННЫХ BELLE CROISSANT LYONNAIS
-- Session 5 - Database Verification Script
-- ============================================================

-- 1. ПРОВЕРКА СУЩЕСТВОВАНИЯ ТАБЛИЦ
-- ============================================================
SELECT '=== 1. ПРОВЕРКА СУЩЕСТВОВАНИЯ ТАБЛИЦ ===' AS step;

SELECT 
    name AS table_name,
    CASE 
        WHEN type = 'table' THEN 'Существует'
        ELSE 'Не найдена'
    END AS status
FROM sqlite_master 
WHERE type = 'table' 
    AND name IN ('promotions', 'loyalty_program', 'mock_customers', 'mock_products', 'mock_orders')
ORDER BY name;


-- 2. КОЛИЧЕСТВО СТРОК В КАЖДОЙ ТАБЛИЦЕ
-- ============================================================
SELECT '=== 2. КОЛИЧЕСТВО СТРОК В ТАБЛИЦАХ ===' AS step;

SELECT 'promotions' AS table_name, COUNT(*) AS row_count FROM promotions
UNION ALL
SELECT 'loyalty_program' AS table_name, COUNT(*) AS row_count FROM loyalty_program
UNION ALL
SELECT 'mock_customers' AS table_name, COUNT(*) AS row_count FROM mock_customers
UNION ALL
SELECT 'mock_products' AS table_name, COUNT(*) AS row_count FROM mock_products
UNION ALL
SELECT 'mock_orders' AS table_name, COUNT(*) AS row_count FROM mock_orders;


-- 3. ПЕРВЫЕ 5 СТРОК ТАБЛИЦЫ PROMOTIONS
-- ============================================================
SELECT '=== 3. ПЕРВЫЕ 5 СТРОК ТАБЛИЦЫ PROMOTIONS ===' AS step;

SELECT 
    id,
    name,
    discount_type,
    discount_value,
    applicable_products,
    start_date,
    end_date,
    priority
FROM promotions
ORDER BY id
LIMIT 5;


-- 4. ПЕРВЫЕ 5 СТРОК ТАБЛИЦЫ LOYALTY_PROGRAM
-- ============================================================
SELECT '=== 4. ПЕРВЫЕ 5 СТРОК ТАБЛИЦЫ LOYALTY_PROGRAM ===' AS step;

SELECT 
    customer_id,
    loyalty_points,
    membership_status,
    registration_date
FROM loyalty_program
ORDER BY customer_id
LIMIT 5;


-- 5. ПЕРВЫЕ 5 СТРОК ТАБЛИЦЫ MOCK_CUSTOMERS
-- ============================================================
SELECT '=== 5. ПЕРВЫЕ 5 СТРОК ТАБЛИЦЫ MOCK_CUSTOMERS ===' AS step;

SELECT 
    id,
    first_name,
    last_name,
    email,
    membership_status,
    total_spending
FROM mock_customers
ORDER BY id
LIMIT 5;


-- 6. ПЕРВЫЕ 5 СТРОК ТАБЛИЦЫ MOCK_PRODUCTS
-- ============================================================
SELECT '=== 6. ПЕРВЫЕ 5 СТРОК ТАБЛИЦЫ MOCK_PRODUCTS ===' AS step;

SELECT 
    id,
    name,
    category,
    price,
    is_available
FROM mock_products
ORDER BY id
LIMIT 5;


-- 7. ПЕРВЫЕ 5 СТРОК ТАБЛИЦЫ MOCK_ORDERS
-- ============================================================
SELECT '=== 7. ПЕРВЫЕ 5 СТРОК ТАБЛИЦЫ MOCK_ORDERS ===' AS step;

SELECT 
    id,
    customer_id,
    order_date,
    status,
    total_amount
FROM mock_orders
ORDER BY id
LIMIT 5;


-- 8. ПОИСК ПРОМОАКЦИИ С НЕПРАВИЛЬНОЙ ДАТОЙ
-- ============================================================
SELECT '=== 8. ПРОМОАКЦИЯ С НЕПРАВИЛЬНОЙ ДАТОЙ (end_date < start_date) ===' AS step;

SELECT 
    id,
    name,
    discount_type,
    discount_value,
    start_date,
    end_date,
    CASE 
        WHEN end_date < start_date THEN 'ОШИБКА: Дата окончания раньше начала'
        ELSE 'Даты корректны'
    END AS date_validation
FROM promotions
WHERE end_date < start_date;


-- 9. КЛИЕНТЫ С НАЧАЛЬНЫМИ БАЛЛАМИ (АКТИВНЫЕ УЧАСТНИКИ)
-- ============================================================
SELECT '=== 9. КЛИЕНТЫ С НАЧАЛЬНЫМИ БАЛЛАМИ ===' AS step;

SELECT 
    customer_id,
    loyalty_points,
    membership_status,
    registration_date
FROM loyalty_program
WHERE loyalty_points > 0
ORDER BY loyalty_points DESC
LIMIT 10;


-- 10. СТАТИСТИКА ПО КЛИЕНТАМ С БАЛЛАМИ
-- ============================================================
SELECT '=== 10. СТАТИСТИКА ПО БАЛЛАМ ЛОЯЛЬНОСТИ ===' AS step;

SELECT 
    'Всего клиентов' AS metric,
    COUNT(*) AS value
FROM loyalty_program
UNION ALL
SELECT 
    'Клиентов с баллами > 0' AS metric,
    COUNT(*) AS value
FROM loyalty_program
WHERE loyalty_points > 0
UNION ALL
SELECT 
    'Клиентов с баллами = 0' AS metric,
    COUNT(*) AS value
FROM loyalty_program
WHERE loyalty_points = 0
UNION ALL
SELECT 
    'Средние баллы (активные)' AS metric,
    CAST(AVG(loyalty_points) AS INTEGER) AS value
FROM loyalty_program
WHERE loyalty_points > 0
UNION ALL
SELECT 
    'Максимальные баллы' AS metric,
    MAX(loyalty_points) AS value
FROM loyalty_program;


-- 11. РАСПРЕДЕЛЕНИЕ ПО СТАТУСАМ ЧЛЕНСТВА
-- ============================================================
SELECT '=== 11. РАСПРЕДЕЛЕНИЕ ПО СТАТУСАМ ===' AS step;

SELECT 
    membership_status,
    COUNT(*) AS count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM loyalty_program), 2) AS percentage
FROM loyalty_program
GROUP BY membership_status
ORDER BY count DESC;


-- 12. СТАТИСТИКА ПО ПРОМОАКЦИЯМ
-- ============================================================
SELECT '=== 12. СТАТИСТИКА ПО ПРОМОАКЦИЯМ ===' AS step;

SELECT 
    discount_type,
    COUNT(*) AS count,
    AVG(discount_value) AS avg_discount,
    MIN(discount_value) AS min_discount,
    MAX(discount_value) AS max_discount
FROM promotions
GROUP BY discount_type;


-- 13. АКТИВНЫЕ ПРОМОАКЦИИ (ТЕКУЩАЯ ДАТА)
-- ============================================================
SELECT '=== 13. АКТИВНЫЕ ПРОМОАКЦИИ ===' AS step;

SELECT 
    id,
    name,
    discount_type,
    discount_value,
    start_date,
    end_date,
    priority
FROM promotions
WHERE datetime('now') BETWEEN start_date AND end_date
ORDER BY priority DESC, start_date;


-- 14. ПРОВЕРКА ЦЕЛОСТНОСТИ ДАННЫХ
-- ============================================================
SELECT '=== 14. ПРОВЕРКА ЦЕЛОСТНОСТИ ДАННЫХ ===' AS step;

-- Проверка: все customer_id в loyalty_program существуют в mock_customers
SELECT 
    'Несоответствие customer_id' AS issue,
    COUNT(*) AS count
FROM loyalty_program lp
LEFT JOIN mock_customers mc ON lp.customer_id = mc.id
WHERE mc.id IS NULL;


-- 15. ТОП-10 КЛИЕНТОВ ПО ТРАТАМ
-- ============================================================
SELECT '=== 15. ТОП-10 КЛИЕНТОВ ПО ОБЩИМ ТРАТАМ ===' AS step;

SELECT 
    mc.id,
    mc.first_name || ' ' || mc.last_name AS full_name,
    mc.email,
    mc.membership_status,
    mc.total_spending,
    lp.loyalty_points
FROM mock_customers mc
LEFT JOIN loyalty_program lp ON mc.id = lp.customer_id
ORDER BY mc.total_spending DESC
LIMIT 10;


-- ============================================================
-- КОНЕЦ ПРОВЕРКИ
-- ============================================================
SELECT '=== ПРОВЕРКА ЗАВЕРШЕНА ===' AS step;