"""
Скрипт для создания и инициализации базы данных SQLite
Belle Croissant Lyonnais - Session 5
"""

import sqlite3
import os

DB_PATH = 'belle_croissant.db'
SCHEMA_FILE = 'Session5_Database_Schema.sql'

def create_database():
    """Создание базы данных из SQL схемы"""
    
    print("="*60)
    print("Belle Croissant Lyonnais - Session 5")
    print("Создание базы данных SQLite")
    print("="*60)
    print()
    
    # Проверка существования файла схемы
    if not os.path.exists(SCHEMA_FILE):
        print(f"❌ Файл схемы '{SCHEMA_FILE}' не найден!")
        print("Пожалуйста, убедитесь, что файл находится в текущей директории.")
        return False
    
    # Удаление старой базы данных (если нужно начать заново)
    if os.path.exists(DB_PATH):
        response = input(f"⚠️  База данных '{DB_PATH}' уже существует. Пересоздать? (y/n): ")
        if response.lower() == 'y':
            os.remove(DB_PATH)
            print(f"✓ Старая база данных удалена")
        else:
            print("ℹ️  Используется существующая база данных")
            return True
    
    try:
        # Создание подключения
        print(f"\n📁 Создание базы данных: {DB_PATH}")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Чтение и выполнение SQL схемы
        print(f"📄 Чтение схемы из: {SCHEMA_FILE}")
        with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        print("⚙️  Выполнение SQL скрипта...")
        cursor.executescript(schema_sql)
        
        conn.commit()
        print("✓ Схема базы данных создана успешно!")
        
        # Проверка созданных таблиц
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        print(f"\n📊 Созданные таблицы ({len(tables)}):")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"  • {table[0]}: {count} записей")
        
        cursor.close()
        conn.close()
        
        print(f"\n✅ База данных успешно создана!")
        print(f"📍 Расположение: {os.path.abspath(DB_PATH)}")
        print(f"💾 Размер: {os.path.getsize(DB_PATH)} байт")
        
        return True
        
    except sqlite3.Error as e:
        print(f"\n❌ Ошибка SQLite: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return False

def verify_database():
    """Проверка базы данных"""
    if not os.path.exists(DB_PATH):
        print(f"❌ База данных '{DB_PATH}' не найдена!")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print(f"\n🔍 Проверка базы данных...")
        
        # Проверка таблиц
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        required_tables = ['Promotions', 'LoyaltyProgram']
        existing_tables = [t[0] for t in tables]
        
        for table in required_tables:
            if table in existing_tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  ✓ {table}: {count} записей")
            else:
                print(f"  ❌ {table}: таблица отсутствует!")
        
        cursor.close()
        conn.close()
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    success = create_database()
    
    if success:
        print("\n" + "="*60)
        print("СЛЕДУЮЩИЕ ШАГИ:")
        print("="*60)
        print("1. Запустите: python initialize_loyalty_data.py")
        print("   (для инициализации данных программы лояльности)")
        print()
        print("2. Проверьте данные: python verify_database.py")
        print("   (опционально)")
        print()
        print("3. Запустите приложения:")
        print("   python promotions_management_app.py")
        print("   python loyalty_management_app.py")
        print("="*60)
    else:
        print("\n❌ Не удалось создать базу данных.")
        print("Проверьте ошибки выше и попробуйте снова.")