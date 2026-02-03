"""
Скрипт для проверки базы данных SQLite
Belle Croissant Lyonnais - Session 5
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = 'belle_croissant.db'

def print_section(title):
    """Печать заголовка секции"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

def verify_database():
    """Полная проверка базы данных"""
    
    print("="*70)
    print("  Belle Croissant Lyonnais - Session 5")
    print("  Проверка базы данных SQLite")
    print("="*70)
    
    # Проверка существования файла
    if not os.path.exists(DB_PATH):
        print(f"\n❌ База данных '{DB_PATH}' не найдена!")
        print("Пожалуйста, сначала создайте базу данных:")
        print("  python create_database.py")
        return False
    
    print(f"\n📁 База данных: {os.path.abspath(DB_PATH)}")
    print(f"💾 Размер файла: {os.path.getsize(DB_PATH):,} байт")
    print(f"📅 Последнее изменение: {datetime.fromtimestamp(os.path.getmtime(DB_PATH))}")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 1. Проверка таблиц
        print_section("1. ПРОВЕРКА ТАБЛИЦ")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        if tables:
            print(f"Найдено таблиц: {len(tables)}")
            for table in tables:
                print(f"  ✓ {table['name']}")
        else:
            print("❌ Таблицы не найдены!")
            return False
        
        # 2. Проверка структуры таблиц
        print_section("2. СТРУКТУРА ТАБЛИЦ")
        
        for table in ['Promotions', 'LoyaltyProgram']:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            print(f"\n{table} ({len(columns)} колонок):")
            for col in columns:
                print(f"  • {col['name']}: {col['type']}")
        
        # 3. Количество записей
        print_section("3. КОЛИЧЕСТВО ЗАПИСЕЙ")
        
        cursor.execute("SELECT COUNT(*) as count FROM Promotions")
        promo_count = cursor.fetchone()['count']
        print(f"Promotions: {promo_count} записей")
        
        cursor.execute("SELECT COUNT(*) as count FROM LoyaltyProgram")
        loyalty_count = cursor.fetchone()['count']
        print(f"LoyaltyProgram: {loyalty_count} записей")
        
        # 4. Примеры данных из Promotions
        print_section("4. ПРИМЕРЫ ДАННЫХ - PROMOTIONS (первые 5)")
        
        cursor.execute("""
            SELECT PromotionId, PromotionName, DiscountType, DiscountValue, Priority
            FROM Promotions 
            ORDER BY PromotionId 
            LIMIT 5
        """)
        promotions = cursor.fetchall()
        
        if promotions:
            for promo in promotions:
                print(f"\n  ID {promo['PromotionId']}: {promo['PromotionName']}")
                print(f"    Скидка: {promo['DiscountValue']} ({promo['DiscountType']})")
                print(f"    Приоритет: {promo['Priority']}")
        else:
            print("  ⚠️  Нет данных")
        
        # 5. Примеры данных из LoyaltyProgram
        print_section("5. ПРИМЕРЫ ДАННЫХ - LOYALTY PROGRAM (первые 5)")
        
        cursor.execute("""
            SELECT CustomerId, LoyaltyPoints, MembershipStatus, RegistrationDate
            FROM LoyaltyProgram 
            ORDER BY CustomerId 
            LIMIT 5
        """)
        customers = cursor.fetchall()
        
        if customers:
            for customer in customers:
                print(f"\n  ID {customer['CustomerId']}: {customer['MembershipStatus']}")
                print(f"    Баллы: {customer['LoyaltyPoints']}")
                print(f"    Регистрация: {customer['RegistrationDate']}")
        else:
            print("  ⚠️  Нет данных")
        
        # 6. Поиск промоакции с неверными датами
        print_section("6. ПРОВЕРКА ДАННЫХ - НЕВЕРНЫЕ ДАТЫ")
        
        cursor.execute("""
            SELECT PromotionId, PromotionName, StartDate, EndDate
            FROM Promotions 
            WHERE DATE(EndDate) < DATE(StartDate)
        """)
        invalid_promos = cursor.fetchall()
        
        if invalid_promos:
            print(f"Найдено промоакций с неверными датами: {len(invalid_promos)}")
            for promo in invalid_promos:
                print(f"  ⚠️  ID {promo['PromotionId']}: {promo['PromotionName']}")
                print(f"     Начало: {promo['StartDate']}, Конец: {promo['EndDate']}")
        else:
            print("✓ Все даты корректны")
        
        # 7. Клиенты с баллами
        print_section("7. КЛИЕНТЫ С БАЛЛАМИ ЛОЯЛЬНОСТИ")
        
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM LoyaltyProgram 
            WHERE LoyaltyPoints > 0
        """)
        with_points = cursor.fetchone()['count']
        
        cursor.execute("""
            SELECT AVG(LoyaltyPoints) as avg, MAX(LoyaltyPoints) as max
            FROM LoyaltyProgram 
            WHERE LoyaltyPoints > 0
        """)
        stats = cursor.fetchone()
        
        print(f"Клиентов с баллами: {with_points}")
        if with_points > 0:
            print(f"Средний балл: {stats['avg']:.2f}")
            print(f"Максимальный балл: {stats['max']}")
        
        # 8. Топ-5 клиентов по баллам
        print_section("8. ТОП-5 КЛИЕНТОВ ПО БАЛЛАМ")
        
        cursor.execute("""
            SELECT CustomerId, LoyaltyPoints, MembershipStatus
            FROM LoyaltyProgram 
            WHERE LoyaltyPoints > 0
            ORDER BY LoyaltyPoints DESC
            LIMIT 5
        """)
        top_customers = cursor.fetchall()
        
        if top_customers:
            for i, customer in enumerate(top_customers, 1):
                print(f"  {i}. Клиент #{customer['CustomerId']}: {customer['LoyaltyPoints']} баллов ({customer['MembershipStatus']})")
        else:
            print("  ⚠️  Нет клиентов с баллами")
        
        # 9. Статистика по статусам
        print_section("9. СТАТИСТИКА ПО СТАТУСАМ КЛИЕНТОВ")
        
        cursor.execute("""
            SELECT MembershipStatus, COUNT(*) as count, AVG(LoyaltyPoints) as avg_points
            FROM LoyaltyProgram
            GROUP BY MembershipStatus
            ORDER BY MembershipStatus
        """)
        status_stats = cursor.fetchall()
        
        if status_stats:
            for stat in status_stats:
                print(f"  {stat['MembershipStatus']}: {stat['count']} клиентов, средний балл: {stat['avg_points']:.2f}")
        
        # 10. Индексы
        print_section("10. ИНДЕКСЫ")
        
        cursor.execute("SELECT name, tbl_name FROM sqlite_master WHERE type='index' ORDER BY tbl_name, name")
        indexes = cursor.fetchall()
        
        if indexes:
            current_table = None
            for idx in indexes:
                if idx['tbl_name'] != current_table:
                    print(f"\n{idx['tbl_name']}:")
                    current_table = idx['tbl_name']
                print(f"  ✓ {idx['name']}")
        else:
            print("  ⚠️  Индексы не найдены")
        
        cursor.close()
        conn.close()
        
        # Итоговый статус
        print_section("ИТОГ")
        print("✅ Проверка завершена успешно!")
        print(f"✅ База данных содержит {promo_count} промоакций")
        print(f"✅ База данных содержит {loyalty_count} клиентов")
        print(f"✅ {with_points} клиентов имеют баллы лояльности")
        
        if promo_count == 0:
            print("\n⚠️  ВНИМАНИЕ: В таблице Promotions нет данных!")
        if loyalty_count == 0:
            print("\n⚠️  ВНИМАНИЕ: В таблице LoyaltyProgram нет данных!")
            print("Запустите: python initialize_loyalty_data.py")
        
        print("\n" + "="*70)
        
        return True
        
    except sqlite3.Error as e:
        print(f"\n❌ Ошибка SQLite: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    verify_database()