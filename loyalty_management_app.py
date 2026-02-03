"""
Belle Croissant Lyonnais - Приложение управления программой лояльности
Session 5: Loyalty Management Application
Требуется: PyQt5, mysql-connector-python, requests
"""

import sys
import sqlite3
import requests
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton,
                             QLabel, QLineEdit, QMessageBox, QDialog, QDialogButtonBox,
                             QGroupBox, QSpinBox, QTextEdit, QComboBox, QTableWidgetItem)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

# Конфигурация БД
DB_PATH = 'belle_croissant.db'

# API конфигурация (тестовая заглушка)
API_BASE_URL = "http://localhost:8000/api"

# Mock API данные (в реальном приложении - запросы к API)
def get_mock_customers():
    """Получение тестовых данных клиентов"""
    customers = []
    membership_statuses = ['Basic', 'Silver', 'Gold']
    
    for i in range(1, 101):
        days_ago = 30 + (i * 10) % 1000
        reg_date = datetime.now() - timedelta(days=days_ago)
        
        customers.append({
            'customer_id': i,
            'first_name': f'Клиент{i}',
            'last_name': f'Фамилия{i}',
            'email': f'customer{i}@example.com',
            'membership_status': membership_statuses[i % 3],
            'registration_date': reg_date.strftime('%Y-%m-%d'),
            'total_spending': round(50 + (i * 37.5) % 5000, 2)
        })
    
    return customers

def get_mock_orders(customer_id):
    """Получение тестовых заказов клиента"""
    import random
    orders = []
    num_orders = random.randint(3, 15)
    
    for i in range(num_orders):
        days_ago = random.randint(1, 365)
        order_date = datetime.now() - timedelta(days=days_ago)
        
        orders.append({
            'order_id': customer_id * 100 + i,
            'customer_id': customer_id,
            'order_date': order_date.strftime('%Y-%m-%d'),
            'total_amount': round(random.uniform(10, 150), 2),
            'status': 'completed'
        })
    
    return orders


class PointsCalculationDialog(QDialog):
    """Диалог расчета и подтверждения баллов"""
    
    def __init__(self, parent, customer_data, calculated_points, breakdown):
        super().__init__(parent)
        self.customer_data = customer_data
        self.calculated_points = calculated_points
        self.breakdown = breakdown
        
        self.setWindowTitle("Расчет баллов лояльности")
        self.setMinimumSize(600, 500)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Информация о клиенте
        info_label = QLabel(
            f"<h3>Клиент: {self.customer_data['first_name']} {self.customer_data['last_name']}</h3>"
            f"Статус: {self.customer_data['membership_status']}<br>"
            f"Текущие баллы: {self.customer_data['current_points']}"
        )
        layout.addWidget(info_label)
        
        # Детальная разбивка
        breakdown_group = QGroupBox("Детальная разбивка начисления баллов")
        breakdown_layout = QVBoxLayout()
        
        self.breakdown_table = QTableWidget()
        self.breakdown_table.setColumnCount(4)
        self.breakdown_table.setHorizontalHeaderLabels([
            "Дата заказа", "Сумма заказа", "Базовые баллы", "Бонусы"
        ])
        
        total_base = 0
        total_bonus = 0
        
        self.breakdown_table.setRowCount(len(self.breakdown))
        for row, item in enumerate(self.breakdown):
            self.breakdown_table.setItem(row, 0, QTableWidgetItem(item['order_date']))
            self.breakdown_table.setItem(row, 1, QTableWidgetItem(f"€{item['amount']:.2f}"))
            self.breakdown_table.setItem(row, 2, QTableWidgetItem(str(item['base_points'])))
            self.breakdown_table.setItem(row, 3, QTableWidgetItem(str(item['bonus_points'])))
            
            total_base += item['base_points']
            total_bonus += item['bonus_points']
        
        breakdown_layout.addWidget(self.breakdown_table)
        breakdown_group.setLayout(breakdown_layout)
        layout.addWidget(breakdown_group)
        
        # Итоговая информация
        summary_label = QLabel(
            f"<h3>Итого:</h3>"
            f"Базовые баллы: {total_base}<br>"
            f"Бонусные баллы: {total_bonus}<br>"
            f"<b>Всего начислено: {self.calculated_points}</b>"
        )
        summary_label.setStyleSheet("background-color: #f0f0f0; padding: 10px; border-radius: 5px;")
        layout.addWidget(summary_label)
        
        # Кнопки
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)


class RewardsDialog(QDialog):
    """Диалог выбора вознаграждения"""
    
    def __init__(self, parent, customer_data):
        super().__init__(parent)
        self.customer_data = customer_data
        self.selected_reward = None
        
        self.setWindowTitle("Получение вознаграждения")
        self.setMinimumSize(500, 400)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Информация
        info_label = QLabel(
            f"<h3>Клиент: {self.customer_data['first_name']} {self.customer_data['last_name']}</h3>"
            f"Текущие баллы: <b>{self.customer_data['loyalty_points']}</b><br>"
            f"Статус: {self.customer_data['membership_status']}"
        )
        layout.addWidget(info_label)
        
        info_text = QLabel(
            "Для получения вознаграждения будет списано 1000 баллов.<br>"
            "Выберите один из вариантов вознаграждения:"
        )
        info_text.setWordWrap(True)
        layout.addWidget(info_text)
        
        # Варианты вознаграждений
        rewards_group = QGroupBox("Доступные вознаграждения")
        rewards_layout = QVBoxLayout()
        
        # Скидка 5 евро
        discount_5_btn = QPushButton("💰 Скидка 5€ на следующую покупку")
        discount_5_btn.setMinimumHeight(50)
        discount_5_btn.clicked.connect(lambda: self.select_reward('discount_5'))
        rewards_layout.addWidget(discount_5_btn)
        
        # Скидка 10%
        discount_10_btn = QPushButton("🎫 Скидка 10% на следующую покупку")
        discount_10_btn.setMinimumHeight(50)
        discount_10_btn.clicked.connect(lambda: self.select_reward('discount_10'))
        rewards_layout.addWidget(discount_10_btn)
        
        # Повышение статуса
        current_status = self.customer_data['membership_status']
        if current_status == 'Basic':
            upgrade_text = "⭐ Повышение до Silver статуса"
            upgrade_available = True
        elif current_status == 'Silver':
            upgrade_text = "⭐⭐ Повышение до Gold статуса"
            upgrade_available = True
        else:
            upgrade_text = "⭐⭐⭐ Вы уже на максимальном уровне"
            upgrade_available = False
        
        upgrade_btn = QPushButton(upgrade_text)
        upgrade_btn.setMinimumHeight(50)
        upgrade_btn.setEnabled(upgrade_available)
        if upgrade_available:
            upgrade_btn.clicked.connect(lambda: self.select_reward('upgrade'))
        rewards_layout.addWidget(upgrade_btn)
        
        rewards_group.setLayout(rewards_layout)
        layout.addWidget(rewards_group)
        
        # Кнопка отмены
        cancel_btn = QPushButton("Отменить")
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)
        
        self.setLayout(layout)
        
    def select_reward(self, reward_type):
        """Выбор вознаграждения"""
        self.selected_reward = reward_type
        self.accept()


class LoyaltyApp(QMainWindow):
    """Главное приложение управления программой лояльности"""
    
    def __init__(self):
        super().__init__()
        self.db_conn = None
        self.customers_data = []
        self.current_customer = None
        self.page = 0
        self.page_size = 10
        self.search_query = ""
        
        self.init_ui()
        self.connect_database()
        self.load_customers()
        
    def init_ui(self):
        self.setWindowTitle("Belle Croissant Lyonnais - Управление программой лояльности")
        self.setGeometry(100, 100, 1400, 800)
        
        # Главный виджет
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout()
        
        # Левая панель - список клиентов
        left_panel = QVBoxLayout()
        
        # Заголовок
        header = QLabel("Программа лояльности клиентов")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setStyleSheet("color: #8B4513; padding: 10px;")
        left_panel.addWidget(header)
        
        # Поиск
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Поиск:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Имя, ID или Email клиента...")
        self.search_input.textChanged.connect(self.filter_customers)
        search_layout.addWidget(self.search_input)
        left_panel.addLayout(search_layout)
        
        # Сортировка
        sort_layout = QHBoxLayout()
        sort_layout.addWidget(QLabel("Сортировка:"))
        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            "ID (убывание)",
            "ID (возрастание)",
            "Имя (А-Я)",
            "Имя (Я-А)",
            "Баллы (убывание)",
            "Баллы (возрастание)"
        ])
        self.sort_combo.currentTextChanged.connect(self.sort_customers)
        sort_layout.addWidget(self.sort_combo)
        left_panel.addLayout(sort_layout)
        
        # Таблица клиентов
        self.customers_table = QTableWidget()
        self.customers_table.setColumnCount(6)
        self.customers_table.setHorizontalHeaderLabels([
            "ID", "Имя", "Фамилия", "Email", "Статус", "Баллы"
        ])
        self.customers_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.customers_table.setSelectionMode(QTableWidget.SingleSelection)
        self.customers_table.cellClicked.connect(self.load_customer_details)
        self.customers_table.setColumnWidth(3, 200)
        left_panel.addWidget(self.customers_table)
        
        # Пагинация
        pagination_layout = QHBoxLayout()
        self.prev_page_btn = QPushButton("← Предыдущая")
        self.prev_page_btn.clicked.connect(self.prev_page)
        pagination_layout.addWidget(self.prev_page_btn)
        
        self.page_label = QLabel("Страница 1")
        self.page_label.setAlignment(Qt.AlignCenter)
        pagination_layout.addWidget(self.page_label)
        
        self.next_page_btn = QPushButton("Следующая →")
        self.next_page_btn.clicked.connect(self.next_page)
        pagination_layout.addWidget(self.next_page_btn)
        
        left_panel.addLayout(pagination_layout)
        
        # Правая панель - детали клиента
        right_panel = QVBoxLayout()
        
        details_header = QLabel("Детали клиента")
        details_header.setFont(QFont("Arial", 14, QFont.Bold))
        details_header.setStyleSheet("color: #8B4513; padding: 10px;")
        right_panel.addWidget(details_header)
        
        # Форма деталей
        details_group = QGroupBox("Информация о клиенте")
        details_layout = QVBoxLayout()
        
        self.customer_id_label = QLabel("ID: -")
        details_layout.addWidget(self.customer_id_label)
        
        self.customer_name_label = QLabel("Имя: -")
        details_layout.addWidget(self.customer_name_label)
        
        self.customer_email_label = QLabel("Email: -")
        details_layout.addWidget(self.customer_email_label)
        
        self.customer_status_label = QLabel("Статус: -")
        details_layout.addWidget(self.customer_status_label)
        
        # Баллы лояльности (редактируемое поле)
        points_layout = QHBoxLayout()
        points_layout.addWidget(QLabel("Баллы лояльности:"))
        self.points_input = QSpinBox()
        self.points_input.setRange(0, 999999)
        self.points_input.setEnabled(False)
        points_layout.addWidget(self.points_input)
        details_layout.addLayout(points_layout)
        
        details_group.setLayout(details_layout)
        right_panel.addWidget(details_group)
        
        # Кнопки действий
        actions_group = QGroupBox("Действия")
        actions_layout = QVBoxLayout()
        
        self.save_changes_btn = QPushButton("💾 Сохранить изменения")
        self.save_changes_btn.clicked.connect(self.save_changes)
        self.save_changes_btn.setEnabled(False)
        self.save_changes_btn.setMinimumHeight(40)
        actions_layout.addWidget(self.save_changes_btn)
        
        self.cancel_btn = QPushButton("❌ Отменить")
        self.cancel_btn.clicked.connect(self.cancel_changes)
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.setMinimumHeight(40)
        actions_layout.addWidget(self.cancel_btn)
        
        self.recalculate_btn = QPushButton("🔄 Пересчитать баллы")
        self.recalculate_btn.clicked.connect(self.recalculate_points)
        self.recalculate_btn.setEnabled(False)
        self.recalculate_btn.setMinimumHeight(40)
        actions_layout.addWidget(self.recalculate_btn)
        
        self.redeem_btn = QPushButton("🎁 Получить вознаграждение")
        self.redeem_btn.clicked.connect(self.redeem_rewards)
        self.redeem_btn.setEnabled(False)
        self.redeem_btn.setMinimumHeight(40)
        actions_layout.addWidget(self.redeem_btn)
        
        actions_group.setLayout(actions_layout)
        right_panel.addWidget(actions_group)
        
        right_panel.addStretch()
        
        # Добавление панелей в главный layout
        main_layout.addLayout(left_panel, 2)
        main_layout.addLayout(right_panel, 1)
        
        main_widget.setLayout(main_layout)
        
    def connect_database(self):
        """Подключение к базе данных"""
        try:
            self.db_conn = sqlite3.connect(DB_PATH)
            self.db_conn.row_factory = sqlite3.Row
            print("✓ Подключено к базе данных")
        except sqlite3.Error as err:
            QMessageBox.critical(self, "Ошибка БД", f"Не удалось подключиться к базе данных:\n{err}")
            
    def load_customers(self):
        """Загрузка клиентов из API и БД"""
        try:
            # Получаем данные клиентов из "API" (mock данные)
            api_customers = get_mock_customers()
            
            # Получаем баллы лояльности из БД
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT CustomerId, LoyaltyPoints FROM LoyaltyProgram")
            loyalty_data = {row['CustomerId']: row['LoyaltyPoints'] for row in cursor.fetchall()}
            cursor.close()
            
            # Объединяем данные
            self.customers_data = []
            for customer in api_customers:
                customer['loyalty_points'] = loyalty_data.get(customer['customer_id'], 0)
                self.customers_data.append(customer)
            
            self.display_customers()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки клиентов:\n{e}")
            
    def filter_customers(self):
        """Фильтрация клиентов по поисковому запросу"""
        self.search_query = self.search_input.text().lower()
        self.page = 0
        self.display_customers()
        
    def sort_customers(self):
        """Сортировка клиентов"""
        sort_option = self.sort_combo.currentText()
        
        if "ID (убывание)" in sort_option:
            self.customers_data.sort(key=lambda x: x['customer_id'], reverse=True)
        elif "ID (возрастание)" in sort_option:
            self.customers_data.sort(key=lambda x: x['customer_id'])
        elif "Имя (А-Я)" in sort_option:
            self.customers_data.sort(key=lambda x: x['first_name'])
        elif "Имя (Я-А)" in sort_option:
            self.customers_data.sort(key=lambda x: x['first_name'], reverse=True)
        elif "Баллы (убывание)" in sort_option:
            self.customers_data.sort(key=lambda x: x['loyalty_points'], reverse=True)
        elif "Баллы (возрастание)" in sort_option:
            self.customers_data.sort(key=lambda x: x['loyalty_points'])
        
        self.display_customers()
        
    def display_customers(self):
        """Отображение клиентов в таблице с пагинацией"""
        # Фильтрация
        filtered = self.customers_data
        if self.search_query:
            filtered = [c for c in self.customers_data if 
                       self.search_query in str(c['customer_id']) or
                       self.search_query in c['first_name'].lower() or
                       self.search_query in c['last_name'].lower() or
                       self.search_query in c['email'].lower()]
        
        # Пагинация
        start_idx = self.page * self.page_size
        end_idx = start_idx + self.page_size
        page_data = filtered[start_idx:end_idx]
        
        # Заполнение таблицы
        self.customers_table.setRowCount(len(page_data))
        
        for row, customer in enumerate(page_data):
            self.customers_table.setItem(row, 0, QTableWidgetItem(str(customer['customer_id'])))
            self.customers_table.setItem(row, 1, QTableWidgetItem(customer['first_name']))
            self.customers_table.setItem(row, 2, QTableWidgetItem(customer['last_name']))
            self.customers_table.setItem(row, 3, QTableWidgetItem(customer['email']))
            
            status_item = QTableWidgetItem(customer['membership_status'])
            if customer['membership_status'] == 'Gold':
                status_item.setBackground(QColor(255, 215, 0, 100))
            elif customer['membership_status'] == 'Silver':
                status_item.setBackground(QColor(192, 192, 192, 100))
            self.customers_table.setItem(row, 4, status_item)
            
            points_item = QTableWidgetItem(str(customer['loyalty_points']))
            if customer['loyalty_points'] >= 1000:
                points_item.setBackground(QColor(144, 238, 144, 100))
            self.customers_table.setItem(row, 5, points_item)
        
        # Обновление пагинации
        total_pages = (len(filtered) + self.page_size - 1) // self.page_size
        self.page_label.setText(f"Страница {self.page + 1} из {max(1, total_pages)}")
        self.prev_page_btn.setEnabled(self.page > 0)
        self.next_page_btn.setEnabled(end_idx < len(filtered))
        
    def next_page(self):
        """Следующая страница"""
        self.page += 1
        self.display_customers()
        
    def prev_page(self):
        """Предыдущая страница"""
        if self.page > 0:
            self.page -= 1
            self.display_customers()
            
    def load_customer_details(self, row, column):
        """Загрузка деталей выбранного клиента"""
        customer_id = int(self.customers_table.item(row, 0).text())
        
        # Находим клиента в данных
        customer = next((c for c in self.customers_data if c['customer_id'] == customer_id), None)
        
        if customer:
            self.current_customer = customer.copy()
            
            self.customer_id_label.setText(f"ID: {customer['customer_id']}")
            self.customer_name_label.setText(f"Имя: {customer['first_name']} {customer['last_name']}")
            self.customer_email_label.setText(f"Email: {customer['email']}")
            self.customer_status_label.setText(f"Статус: {customer['membership_status']}")
            
            self.points_input.setValue(customer['loyalty_points'])
            self.points_input.setEnabled(True)
            self.points_input.valueChanged.connect(self.enable_save_buttons)
            
            self.recalculate_btn.setEnabled(True)
            
            # Проверка доступности получения вознаграждения
            self.redeem_btn.setEnabled(customer['loyalty_points'] >= 1000)
            
    def enable_save_buttons(self):
        """Активация кнопок сохранения при изменении"""
        self.save_changes_btn.setEnabled(True)
        self.cancel_btn.setEnabled(True)
        
    def save_changes(self):
        """Сохранение изменений баллов"""
        if not self.current_customer:
            return
        
        new_points = self.points_input.value()
        
        try:
            cursor = self.db_conn.cursor()
            cursor.execute(
                "UPDATE LoyaltyProgram SET LoyaltyPoints = ? WHERE CustomerId = ?",
                (new_points, self.current_customer['customer_id'])
            )
            self.db_conn.commit()
            cursor.close()
            
            # Обновляем локальные данные
            for customer in self.customers_data:
                if customer['customer_id'] == self.current_customer['customer_id']:
                    customer['loyalty_points'] = new_points
                    break
            
            QMessageBox.information(self, "Успех", "Баллы успешно обновлены!")
            self.display_customers()
            self.save_changes_btn.setEnabled(False)
            self.cancel_btn.setEnabled(False)
            self.redeem_btn.setEnabled(new_points >= 1000)
            
        except sqlite3.Error as err:
            QMessageBox.critical(self, "Ошибка БД", f"Ошибка сохранения:\n{err}")
            
    def cancel_changes(self):
        """Отмена изменений"""
        if self.current_customer:
            self.points_input.setValue(self.current_customer['loyalty_points'])
            self.save_changes_btn.setEnabled(False)
            self.cancel_btn.setEnabled(False)
            
    def recalculate_points(self):
        """Пересчет баллов лояльности"""
        if not self.current_customer:
            return
        
        try:
            # Получаем историю заказов из "API"
            orders = get_mock_orders(self.current_customer['customer_id'])
            
            # Расчет баллов
            membership_status = self.current_customer['membership_status']
            registration_date = datetime.strptime(self.current_customer['registration_date'], '%Y-%m-%d')
            
            # Коэффициенты начисления
            multipliers = {'Basic': 10, 'Silver': 12, 'Gold': 15}
            multiplier = multipliers[membership_status]
            
            breakdown = []
            total_points = 0
            
            for order in orders:
                order_amount = order['total_amount']
                base_points = int(order_amount // 10) * (multiplier // 10)
                
                # Проверка бонусов
                bonus_points = 0
                
                # Бонус за покупку в период промоакции (упрощенно - 5 баллов)
                bonus_points += 5
                
                total_points += base_points + bonus_points
                
                breakdown.append({
                    'order_date': order['order_date'],
                    'amount': order_amount,
                    'base_points': base_points,
                    'bonus_points': bonus_points
                })
            
            # Проверка годовщины регистрации
            today = datetime.now()
            if (registration_date.month == today.month and 
                registration_date.day == today.day and 
                registration_date.year < today.year):
                total_points += 25
                breakdown.append({
                    'order_date': today.strftime('%Y-%m-%d'),
                    'amount': 0,
                    'base_points': 0,
                    'bonus_points': 25  # Бонус за годовщину
                })
            
            # Показываем диалог с детальной разбивкой
            dialog = PointsCalculationDialog(self, {
                'first_name': self.current_customer['first_name'],
                'last_name': self.current_customer['last_name'],
                'membership_status': membership_status,
                'current_points': self.current_customer['loyalty_points']
            }, total_points, breakdown)
            
            if dialog.exec_() == QDialog.Accepted:
                # Обновляем баллы
                try:
                    cursor = self.db_conn.cursor()
                    cursor.execute(
                        "UPDATE LoyaltyProgram SET LoyaltyPoints = ? WHERE CustomerId = ?",
                        (total_points, self.current_customer['customer_id'])
                    )
                    self.db_conn.commit()
                    cursor.close()
                    
                    # Обновляем локальные данные
                    for customer in self.customers_data:
                        if customer['customer_id'] == self.current_customer['customer_id']:
                            customer['loyalty_points'] = total_points
                            self.current_customer = customer.copy()
                            break
                    
                    self.points_input.setValue(total_points)
                    self.display_customers()
                    self.redeem_btn.setEnabled(total_points >= 1000)
                    
                    QMessageBox.information(self, "Успех", f"Баллы пересчитаны! Новый баланс: {total_points}")
                    
                except sqlite3.Error as err:
                    QMessageBox.critical(self, "Ошибка БД", f"Ошибка обновления баллов:\n{err}")
                    
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка пересчета баллов:\n{e}")
            
    def redeem_rewards(self):
        """Получение вознаграждения"""
        if not self.current_customer or self.current_customer['loyalty_points'] < 1000:
            return
        
        dialog = RewardsDialog(self, self.current_customer)
        
        if dialog.exec_() == QDialog.Accepted and dialog.selected_reward:
            try:
                cursor = self.db_conn.cursor()
                
                # Списываем 1000 баллов
                new_points = self.current_customer['loyalty_points'] - 1000
                cursor.execute(
                    "UPDATE LoyaltyProgram SET LoyaltyPoints = %s WHERE CustomerId = %s",
                    (new_points, self.current_customer['customer_id'])
                )
                
                reward_description = ""
                
                if dialog.selected_reward == 'discount_5':
                    # Создаем промоакцию скидки 5 евро
                    promo_name = f"Награда: Скидка 5€ - Клиент {self.current_customer['customer_id']}"
                    start_date = datetime.now().strftime('%Y-%m-%d')
                    end_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
                    
                    cursor.execute("""
                        INSERT INTO Promotions 
                        (PromotionName, DiscountType, DiscountValue, ApplicableProducts, 
                         StartDate, EndDate, MinimumOrderValue, Priority)
                        VALUES (%s, 'fixed_amount', 5.00, '1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22', 
                                %s, %s, NULL, 99)
                    """, (promo_name, start_date, end_date))
                    
                    reward_description = "Скидка 5€ на следующую покупку"
                    
                elif dialog.selected_reward == 'discount_10':
                    # Создаем промоакцию скидки 10%
                    promo_name = f"Награда: Скидка 10% - Клиент {self.current_customer['customer_id']}"
                    start_date = datetime.now().strftime('%Y-%m-%d')
                    end_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
                    
                    cursor.execute("""
                        INSERT INTO Promotions 
                        (PromotionName, DiscountType, DiscountValue, ApplicableProducts, 
                         StartDate, EndDate, MinimumOrderValue, Priority)
                        VALUES (%s, 'percentage', 10.00, '1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22', 
                                %s, %s, NULL, 99)
                    """, (promo_name, start_date, end_date))
                    
                    reward_description = "Скидка 10% на следующую покупку"
                    
                elif dialog.selected_reward == 'upgrade':
                    # Повышение статуса
                    current_status = self.current_customer['membership_status']
                    new_status = 'Silver' if current_status == 'Basic' else 'Gold'
                    
                    cursor.execute(
                        "UPDATE LoyaltyProgram SET MembershipStatus = %s WHERE CustomerId = %s",
                        (new_status, self.current_customer['customer_id'])
                    )
                    
                    reward_description = f"Повышение статуса до {new_status}"
                    self.current_customer['membership_status'] = new_status
                
                self.db_conn.commit()
                cursor.close()
                
                # Обновляем локальные данные
                for customer in self.customers_data:
                    if customer['customer_id'] == self.current_customer['customer_id']:
                        customer['loyalty_points'] = new_points
                        if dialog.selected_reward == 'upgrade':
                            customer['membership_status'] = self.current_customer['membership_status']
                        self.current_customer = customer.copy()
                        break
                
                self.points_input.setValue(new_points)
                self.display_customers()
                self.load_customer_details(self.customers_table.currentRow(), 0)
                
                QMessageBox.information(
                    self, 
                    "Успех", 
                    f"Вознаграждение получено!\n\n"
                    f"{reward_description}\n"
                    f"Списано: 1000 баллов\n"
                    f"Новый баланс: {new_points} баллов"
                )
                
            except mysql.connector.Error as err:
                self.db_conn.rollback()
                QMessageBox.critical(self, "Ошибка БД", f"Ошибка получения вознаграждения:\n{err}")
            except Exception as e:
                self.db_conn.rollback()
                QMessageBox.critical(self, "Ошибка", f"Ошибка:\n{e}")
    
    def closeEvent(self, event):
        """Закрытие соединения с БД"""
        if self.db_conn:
            self.db_conn.close()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LoyaltyApp()
    window.show()
    sys.exit(app.exec_())