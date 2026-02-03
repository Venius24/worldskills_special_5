"""
Полная установка Belle Croissant Lyonnais - Session 5
Создание базы данных SQLite и инициализация всех данных
Запустите: python setup_all.py
"""

import sqlite3
import random
import os
from datetime import datetime, timedelta

DB_PATH = 'belle_croissant.db'

def create_database():
    """Создание базы данных и таблиц"""
    
    print("="*70)
    print("  Belle Croissant Lyonnais - Session 5")
    print("  Полная установка системы (SQLite)")
    print("="*70)
    print()
    
    # Удаление старой БД если существует
    if os.path.exists(DB_PATH):
        response = input(f"⚠️  База данных '{DB_PATH}' уже существует. Пересоздать? (y/n): ")
        if response.lower() != 'y':
            print("ℹ️  Установка отменена.")
            return False
        os.remove(DB_PATH)
        print("✓ Старая база данных удалена")
    
    print(f"\n📁 Создание базы данных: {DB_PATH}")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Создание таблицы Promotions
        print("⚙️  Создание таблицы Promotions...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Promotions (
                PromotionId INTEGER PRIMARY KEY AUTOINCREMENT,
                PromotionName TEXT NOT NULL,
                DiscountType TEXT NOT NULL CHECK(DiscountType IN ('percentage', 'fixed_amount')),
                DiscountValue REAL NOT NULL,
                ApplicableProducts TEXT NOT NULL,
                StartDate DATE NOT NULL,
                EndDate DATE NOT NULL,
                MinimumOrderValue REAL DEFAULT NULL,
                Priority INTEGER NOT NULL DEFAULT 1,
                CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Создание индексов для Promotions
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_promotions_dates ON Promotions(StartDate, EndDate)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_promotions_priority ON Promotions(Priority)")
        
        # Триггер для обновления UpdatedAt
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS update_promotions_timestamp 
            AFTER UPDATE ON Promotions
            BEGIN
                UPDATE Promotions SET UpdatedAt = CURRENT_TIMESTAMP WHERE PromotionId = NEW.PromotionId;
            END
        """)
        
        # Создание таблицы LoyaltyProgram
        print("⚙️  Создание таблицы LoyaltyProgram...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS LoyaltyProgram (
                CustomerId INTEGER PRIMARY KEY,
                LoyaltyPoints INTEGER NOT NULL DEFAULT 0,
                MembershipStatus TEXT NOT NULL DEFAULT 'Basic' CHECK(MembershipStatus IN ('Basic', 'Silver', 'Gold')),
                RegistrationDate DATE NOT NULL,
                LastUpdated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                TotalSpending REAL DEFAULT 0.00
            )
        """)
        
        # Создание индексов для LoyaltyProgram
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_loyalty_points ON LoyaltyProgram(LoyaltyPoints)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_loyalty_status ON LoyaltyProgram(MembershipStatus)")
        
        # Триггер для обновления LastUpdated
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS update_loyalty_timestamp 
            AFTER UPDATE ON LoyaltyProgram
            BEGIN
                UPDATE LoyaltyProgram SET LastUpdated = CURRENT_TIMESTAMP WHERE CustomerId = NEW.CustomerId;
            END
        """)
        
        # Добавление тестовых промоакций
        print("⚙️  Добавление 12 тестовых промоакций...")
        promotions = [
            ('Новогодняя распродажа', 'percentage', 15.00, '1,2,3,4,5', '2026-01-01', '2026-01-31', 20.00, 5),
            ('Утренний круассан', 'fixed_amount', 2.50, '1,6,7', '2026-01-15', '2026-02-15', None, 3),
            ('Счастливые выходные', 'percentage', 20.00, '8,9,10,11', '2026-01-24', '2026-01-26', 15.00, 4),
            ('Весенняя свежесть', 'percentage', 10.00, '2,3,12,13', '2026-03-01', '2026-03-31', None, 2),
            ('Кофе и выпечка', 'fixed_amount', 3.00, '5,6,7,14', '2026-01-20', '2026-02-20', 10.00, 3),
            ('Семейный набор', 'percentage', 25.00, '1,2,3,4,5,8,9', '2026-02-01', '2026-02-28', 50.00, 5),
            ('Быстрый обед', 'fixed_amount', 5.00, '10,11,15,16', '2026-01-25', '2026-02-25', 12.00, 2),
            ('Сладкий понедельник', 'percentage', 12.00, '12,13,17,18', '2026-01-27', '2026-02-27', None, 1),
            ('VIP клиент', 'percentage', 30.00, '1,2,3,4,5,6,7,8,9,10', '2026-01-15', '2026-12-31', 100.00, 10),
            ('ТЕСТ: Неверные даты', 'percentage', 5.00, '19,20', '2026-02-15', '2026-02-01', None, 1),
            ('Утренний кофе', 'fixed_amount', 1.50, '14,21,22', '2026-01-20', '2026-03-20', None, 2),
            ('Выходной день', 'percentage', 18.00, '1,5,9,13,17', '2026-01-25', '2026-02-10', 25.00, 4),
        ]
        
        cursor.executemany("""
            INSERT INTO Promotions 
            (PromotionName, DiscountType, DiscountValue, ApplicableProducts, StartDate, EndDate, MinimumOrderValue, Priority)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, promotions)
        
        conn.commit()
        print("✓ Таблицы и промоакции созданы")
        
        # Инициализация программы лояльности
        print("\n⚙️  Инициализация программы лояльности...")
        print("   Создание 500 клиентов...")
        
        customers = []
        for i in range(1, 501):
            days_ago = random.randint(30, 1095)
            registration_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
            membership_status = random.choice(['Basic', 'Silver', 'Gold'])
            total_spending = round(random.uniform(0, 5000), 2)
            
            customers.append((i, 0, membership_status, registration_date, total_spending))
        
        cursor.executemany("""
            INSERT INTO LoyaltyProgram 
            (CustomerId, LoyaltyPoints, MembershipStatus, RegistrationDate, TotalSpending)
            VALUES (?, ?, ?, ?, ?)
        """, customers)
        
        conn.commit()
        print(f"   ✓ Добавлено {len(customers)} клиентов")
        
        # Начисление баллов случайным клиентам
        print("   Начисление баллов 250 случайным клиентам...")
        
        random_customers = random.sample(range(1, 501), 250)
        for customer_id in random_customers:
            points = random.randint(50, 1500)
            cursor.execute("UPDATE LoyaltyProgram SET LoyaltyPoints = ? WHERE CustomerId = ?", 
                         (points, customer_id))
        
        conn.commit()
        print("   ✓ Баллы начислены (от 50 до 1500)")
        
        # Статистика
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN LoyaltyPoints > 0 THEN 1 ELSE 0 END) as with_points,
                AVG(LoyaltyPoints) as avg_points,
                MAX(LoyaltyPoints) as max_points
            FROM LoyaltyProgram
        """)
        stats = cursor.fetchone()
        
        cursor.execute("SELECT COUNT(*) FROM Promotions")
        promo_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        # Итоговая информация
        print("\n" + "="*70)
        print("  ✅ УСТАНОВКА ЗАВЕРШЕНА УСПЕШНО!")
        print("="*70)
        print(f"\n📊 СТАТИСТИКА:")
        print(f"  • База данных: {os.path.abspath(DB_PATH)}")
        print(f"  • Размер: {os.path.getsize(DB_PATH):,} байт")
        print(f"  • Промоакций: {promo_count}")
        print(f"  • Клиентов: {stats[0]}")
        print(f"  • Клиентов с баллами: {stats[1]}")
        print(f"  • Средний балл: {stats[2]:.2f}")
        print(f"  • Максимальный балл: {stats[3]}")
        
        print("\n" + "="*70)
        print("  СЛЕДУЮЩИЕ ШАГИ:")
        print("="*70)
        print("  1. Запустите приложение промоакций:")
        print("     python promotions_management_app.py")
        print()
        print("  2. Запустите приложение лояльности:")
        print("     python loyalty_management_app.py")
        print()
        print("  3. Для проверки БД:")
        print("     python verify_database.py")
        print("="*70)
        
        return True
        
    except sqlite3.Error as e:
        print(f"\n❌ Ошибка SQLite: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    create_database()