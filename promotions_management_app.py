"""
Belle Croissant Lyonnais - Приложение управления промоакциями
Session 5: Promotions Management Application
Требуется: PyQt5, mysql-connector-python
"""

import sys
import sqlite3
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton,
                             QLabel, QLineEdit, QComboBox, QDateEdit, QMessageBox,
                             QDialog, QDialogButtonBox, QTextEdit, QListWidget,
                             QSpinBox, QCheckBox, QGroupBox, QScrollArea)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor

# Конфигурация БД
DB_PATH = 'belle_croissant.db'

# Тестовые продукты (в реальном приложении из API)
MOCK_PRODUCTS = {
    1: "Круассан классический",
    2: "Круассан с шоколадом",
    3: "Круассан с миндалем",
    4: "Багет французский",
    5: "Эклер",
    6: "Макарон ассорти",
    7: "Тарт лимонный",
    8: "Профитроли",
    9: "Мильфей",
    10: "Бриош",
    11: "Канеле",
    12: "Мадлен",
    13: "Финансье",
    14: "Кофе эспрессо",
    15: "Капучино",
    16: "Латте",
    17: "Шоколадный торт",
    18: "Ванильный торт",
    19: "Фруктовый тарт",
    20: "Наполеон",
    21: "Американо",
    22: "Раф кофе"
}


class ConflictResolutionWizard(QDialog):
    """Мастер разрешения конфликтов промоакций"""
    
    def __init__(self, parent, conflicts, new_promotion):
        super().__init__(parent)
        self.conflicts = conflicts
        self.new_promotion = new_promotion
        self.current_step = 0
        self.resolution_actions = []
        
        self.setWindowTitle("Мастер разрешения конфликтов")
        self.setMinimumSize(700, 500)
        self.setup_ui()
        self.show_step()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Заголовок
        self.title_label = QLabel()
        self.title_label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(self.title_label)
        
        # Основная область контента
        self.content_area = QScrollArea()
        self.content_area.setWidgetResizable(True)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_area.setWidget(self.content_widget)
        layout.addWidget(self.content_area)
        
        # Кнопки навигации
        button_layout = QHBoxLayout()
        self.prev_button = QPushButton("← Назад")
        self.next_button = QPushButton("Далее →")
        self.cancel_button = QPushButton("Отменить")
        self.finish_button = QPushButton("Завершить")
        
        self.prev_button.clicked.connect(self.prev_step)
        self.next_button.clicked.connect(self.next_step)
        self.cancel_button.clicked.connect(self.reject)
        self.finish_button.clicked.connect(self.accept)
        
        button_layout.addWidget(self.prev_button)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.next_button)
        button_layout.addWidget(self.finish_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def show_step(self):
        # Очистка предыдущего контента
        for i in reversed(range(self.content_layout.count())): 
            self.content_layout.itemAt(i).widget().setParent(None)
        
        if self.current_step == 0:
            self.show_conflicts_list()
        elif self.current_step == 1:
            self.show_conflict_details()
        elif self.current_step == 2:
            self.show_priority_adjustment()
        elif self.current_step == 3:
            self.show_date_product_adjustment()
        
        # Обновление кнопок
        self.prev_button.setEnabled(self.current_step > 0)
        self.next_button.setEnabled(self.current_step < 3)
        self.finish_button.setEnabled(self.current_step == 3)
        
    def show_conflicts_list(self):
        self.title_label.setText("Шаг 1: Список конфликтов")
        
        info = QLabel(
            f"Обнаружено {len(self.conflicts)} конфликт(ов) с существующими промоакциями.\n"
            "Конфликт возникает когда продукты участвуют в нескольких промоакциях "
            "с одинаковым приоритетом в один и тот же период."
        )
        info.setWordWrap(True)
        self.content_layout.addWidget(info)
        
        for i, conflict in enumerate(self.conflicts, 1):
            group = QGroupBox(f"Конфликт {i}")
            group_layout = QVBoxLayout()
            
            details = QLabel(
                f"<b>Конфликтующие промоакции:</b><br>"
                f"• Новая: {self.new_promotion['name']}<br>"
                f"• Существующая: {conflict['existing_promo']['name']}<br><br>"
                f"<b>Конфликтующие продукты:</b> {', '.join(conflict['products'])}<br>"
                f"<b>Период пересечения:</b> {conflict['overlap_start']} - {conflict['overlap_end']}<br>"
                f"<b>Приоритет:</b> {conflict['existing_promo']['priority']}"
            )
            details.setWordWrap(True)
            group_layout.addWidget(details)
            
            group.setLayout(group_layout)
            self.content_layout.addWidget(group)
        
        self.content_layout.addStretch()
        
    def show_conflict_details(self):
        self.title_label.setText("Шаг 2: Детали конфликта")
        
        if not self.conflicts:
            return
        
        conflict = self.conflicts[0]
        
        explanation = QLabel(
            "<b>Объяснение конфликта:</b><br><br>"
            f"Продукты {', '.join(conflict['products'])} одновременно участвуют "
            f"в двух промоакциях с одинаковым приоритетом {conflict['existing_promo']['priority']}:<br><br>"
            f"1. <b>{self.new_promotion['name']}</b><br>"
            f"   Период: {self.new_promotion['start_date']} - {self.new_promotion['end_date']}<br><br>"
            f"2. <b>{conflict['existing_promo']['name']}</b><br>"
            f"   Период: {conflict['existing_promo']['start_date']} - {conflict['existing_promo']['end_date']}<br><br>"
            "Это создает неопределенность в том, какая скидка должна применяться."
        )
        explanation.setWordWrap(True)
        self.content_layout.addWidget(explanation)
        
        # Визуальная временная шкала
        timeline_group = QGroupBox("Временная шкала конфликта")
        timeline_layout = QVBoxLayout()
        
        timeline_text = QTextEdit()
        timeline_text.setReadOnly(True)
        timeline_text.setMaximumHeight(150)
        timeline_text.setHtml(
            f"<pre>"
            f"Новая промоакция:       |{'='*30}|\n"
            f"                        {self.new_promotion['start_date']}{'  '*10}{self.new_promotion['end_date']}\n\n"
            f"Существующая:      |{'='*30}|\n"
            f"                   {conflict['existing_promo']['start_date']}{'  '*10}{conflict['existing_promo']['end_date']}\n\n"
            f"Период конфликта:       |<span style='color: red;'>{'X'*15}</span>|\n"
            f"                        {conflict['overlap_start']}  {conflict['overlap_end']}"
            f"</pre>"
        )
        timeline_layout.addWidget(timeline_text)
        timeline_group.setLayout(timeline_layout)
        self.content_layout.addWidget(timeline_group)
        
        self.content_layout.addStretch()
        
    def show_priority_adjustment(self):
        self.title_label.setText("Шаг 3: Изменение приоритета")
        
        explanation = QLabel(
            "<b>Изменение приоритета</b><br><br>"
            "Приоритет определяет, какая промоакция будет применена, "
            "когда продукт участвует в нескольких акциях одновременно. "
            "Промоакция с более высоким приоритетом имеет преимущество.<br><br>"
            "<b>Внимание:</b> Изменение приоритета может повлиять на применение "
            "других промоакций и привести к непредвиденным последствиям."
        )
        explanation.setWordWrap(True)
        self.content_layout.addWidget(explanation)
        
        # Выбор нового приоритета
        priority_group = QGroupBox("Выбор приоритета")
        priority_layout = QVBoxLayout()
        
        current_priority = self.new_promotion.get('priority', 1)
        priority_label = QLabel(f"Текущий приоритет: {current_priority}")
        priority_layout.addWidget(priority_label)
        
        self.priority_spin = QSpinBox()
        self.priority_spin.setRange(1, 100)
        self.priority_spin.setValue(current_priority)
        priority_layout.addWidget(QLabel("Новый приоритет:"))
        priority_layout.addWidget(self.priority_spin)
        
        priority_group.setLayout(priority_layout)
        self.content_layout.addWidget(priority_group)
        
        self.content_layout.addStretch()
        
    def show_date_product_adjustment(self):
        self.title_label.setText("Шаг 4: Корректировка даты/продуктов")
        
        explanation = QLabel(
            "<b>Варианты разрешения конфликта:</b><br><br>"
            "1. Изменить даты промоакции, чтобы избежать пересечения<br>"
            "2. Удалить конфликтующие продукты из одной из промоакций"
        )
        explanation.setWordWrap(True)
        self.content_layout.addWidget(explanation)
        
        # Корректировка дат
        date_group = QGroupBox("Корректировка дат")
        date_layout = QVBoxLayout()
        
        date_layout.addWidget(QLabel("Новая дата начала:"))
        self.new_start_date = QDateEdit()
        self.new_start_date.setCalendarPopup(True)
        self.new_start_date.setDate(QDate.fromString(self.new_promotion['start_date'], "yyyy-MM-dd"))
        date_layout.addWidget(self.new_start_date)
        
        date_layout.addWidget(QLabel("Новая дата окончания:"))
        self.new_end_date = QDateEdit()
        self.new_end_date.setCalendarPopup(True)
        self.new_end_date.setDate(QDate.fromString(self.new_promotion['end_date'], "yyyy-MM-dd"))
        date_layout.addWidget(self.new_end_date)
        
        date_group.setLayout(date_layout)
        self.content_layout.addWidget(date_group)
        
        # Удаление продуктов
        product_group = QGroupBox("Удаление конфликтующих продуктов")
        product_layout = QVBoxLayout()
        
        product_layout.addWidget(QLabel("Выберите продукты для удаления из промоакции:"))
        self.product_checkboxes = []
        
        if self.conflicts:
            for product_id in self.conflicts[0]['products']:
                checkbox = QCheckBox(f"{product_id} - {MOCK_PRODUCTS.get(int(product_id.split(':')[0]), 'Неизвестно')}")
                self.product_checkboxes.append((product_id, checkbox))
                product_layout.addWidget(checkbox)
        
        product_group.setLayout(product_layout)
        self.content_layout.addWidget(product_group)
        
        self.content_layout.addStretch()
        
    def next_step(self):
        if self.current_step < 3:
            self.current_step += 1
            self.show_step()
            
    def prev_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.show_step()
            
    def get_resolutions(self):
        """Получить действия по разрешению конфликтов"""
        resolutions = {}
        
        if hasattr(self, 'priority_spin'):
            resolutions['new_priority'] = self.priority_spin.value()
        
        if hasattr(self, 'new_start_date'):
            resolutions['new_start_date'] = self.new_start_date.date().toString("yyyy-MM-dd")
            resolutions['new_end_date'] = self.new_end_date.date().toString("yyyy-MM-dd")
        
        if hasattr(self, 'product_checkboxes'):
            products_to_remove = [pid for pid, cb in self.product_checkboxes if cb.isChecked()]
            resolutions['remove_products'] = products_to_remove
        
        return resolutions


class PromotionsApp(QMainWindow):
    """Главное приложение управления промоакциями"""
    
    def __init__(self):
        super().__init__()
        self.db_conn = None
        self.current_promotion = None
        self.init_ui()
        self.connect_database()
        self.load_promotions()
        
    def init_ui(self):
        self.setWindowTitle("Belle Croissant Lyonnais - Управление промоакциями")
        self.setGeometry(100, 100, 1200, 700)
        
        # Главный виджет
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        
        # Заголовок
        header = QLabel("Управление промоакциями")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setStyleSheet("color: #8B4513; padding: 10px;")
        main_layout.addWidget(header)
        
        # Таблица промоакций
        self.promotions_table = QTableWidget()
        self.promotions_table.setColumnCount(9)
        self.promotions_table.setHorizontalHeaderLabels([
            "ID", "Название", "Тип скидки", "Значение", "Продукты",
            "Дата начала", "Дата окончания", "Мин. сумма", "Приоритет"
        ])
        self.promotions_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.promotions_table.setSelectionMode(QTableWidget.SingleSelection)
        self.promotions_table.cellClicked.connect(self.load_promotion_details)
        main_layout.addWidget(self.promotions_table)
        
        # Форма редактирования
        form_group = QGroupBox("Детали промоакции")
        form_layout = QVBoxLayout()
        
        # Поля формы
        fields_layout = QHBoxLayout()
        
        # Левая колонка
        left_column = QVBoxLayout()
        
        left_column.addWidget(QLabel("Название промоакции:"))
        self.name_input = QLineEdit()
        left_column.addWidget(self.name_input)
        
        left_column.addWidget(QLabel("Тип скидки:"))
        self.discount_type_combo = QComboBox()
        self.discount_type_combo.addItems(["percentage", "fixed_amount"])
        left_column.addWidget(self.discount_type_combo)
        
        left_column.addWidget(QLabel("Значение скидки:"))
        self.discount_value_input = QLineEdit()
        left_column.addWidget(self.discount_value_input)
        
        left_column.addWidget(QLabel("Минимальная сумма заказа:"))
        self.min_order_input = QLineEdit()
        self.min_order_input.setPlaceholderText("Опционально")
        left_column.addWidget(self.min_order_input)
        
        fields_layout.addLayout(left_column)
        
        # Правая колонка
        right_column = QVBoxLayout()
        
        right_column.addWidget(QLabel("Дата начала:"))
        self.start_date_input = QDateEdit()
        self.start_date_input.setCalendarPopup(True)
        self.start_date_input.setDate(QDate.currentDate())
        right_column.addWidget(self.start_date_input)
        
        right_column.addWidget(QLabel("Дата окончания:"))
        self.end_date_input = QDateEdit()
        self.end_date_input.setCalendarPopup(True)
        self.end_date_input.setDate(QDate.currentDate().addDays(30))
        right_column.addWidget(self.end_date_input)
        
        right_column.addWidget(QLabel("Приоритет:"))
        self.priority_input = QSpinBox()
        self.priority_input.setRange(1, 100)
        self.priority_input.setValue(1)
        right_column.addWidget(self.priority_input)
        
        right_column.addWidget(QLabel("Применимые продукты:"))
        self.products_list = QListWidget()
        self.products_list.setSelectionMode(QListWidget.MultiSelection)
        for prod_id, prod_name in MOCK_PRODUCTS.items():
            self.products_list.addItem(f"{prod_id} - {prod_name}")
        right_column.addWidget(self.products_list)
        
        fields_layout.addLayout(right_column)
        form_layout.addLayout(fields_layout)
        
        # Кнопки действий
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Добавить новую промоакцию")
        self.add_button.clicked.connect(self.add_promotion)
        button_layout.addWidget(self.add_button)
        
        self.save_button = QPushButton("Сохранить изменения")
        self.save_button.clicked.connect(self.save_promotion)
        self.save_button.setEnabled(False)
        button_layout.addWidget(self.save_button)
        
        self.delete_button = QPushButton("Удалить промоакцию")
        self.delete_button.clicked.connect(self.delete_promotion)
        self.delete_button.setEnabled(False)
        button_layout.addWidget(self.delete_button)
        
        self.clear_button = QPushButton("Очистить форму")
        self.clear_button.clicked.connect(self.clear_form)
        button_layout.addWidget(self.clear_button)
        
        form_layout.addLayout(button_layout)
        form_group.setLayout(form_layout)
        main_layout.addWidget(form_group)
        
        main_widget.setLayout(main_layout)
        
    def connect_database(self):
        """Подключение к базе данных"""
        try:
            self.db_conn = sqlite3.connect(DB_PATH)
            self.db_conn.row_factory = sqlite3.Row
            print("✓ Подключено к базе данных")
        except sqlite3.Error as err:
            QMessageBox.critical(self, "Ошибка БД", f"Не удалось подключиться к базе данных:\n{err}")
            
    def load_promotions(self):
        """Загрузка промоакций из БД"""
        if not self.db_conn:
            return
        
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT * FROM Promotions ORDER BY PromotionId DESC")
            promotions = cursor.fetchall()
            
            self.promotions_table.setRowCount(len(promotions))
            
            for row, promo in enumerate(promotions):
                self.promotions_table.setItem(row, 0, QTableWidgetItem(str(promo['PromotionId'])))
                self.promotions_table.setItem(row, 1, QTableWidgetItem(promo['PromotionName']))
                self.promotions_table.setItem(row, 2, QTableWidgetItem(promo['DiscountType']))
                self.promotions_table.setItem(row, 3, QTableWidgetItem(str(promo['DiscountValue'])))
                self.promotions_table.setItem(row, 4, QTableWidgetItem(promo['ApplicableProducts']))
                self.promotions_table.setItem(row, 5, QTableWidgetItem(str(promo['StartDate'])))
                self.promotions_table.setItem(row, 6, QTableWidgetItem(str(promo['EndDate'])))
                self.promotions_table.setItem(row, 7, QTableWidgetItem(str(promo['MinimumOrderValue']) if promo['MinimumOrderValue'] else ""))
                self.promotions_table.setItem(row, 8, QTableWidgetItem(str(promo['Priority'])))
                
            cursor.close()
            
        except sqlite3.Error as err:
            QMessageBox.critical(self, "Ошибка БД", f"Ошибка загрузки промоакций:\n{err}")
            
    def load_promotion_details(self, row, column):
        """Загрузка деталей выбранной промоакции"""
        promo_id = int(self.promotions_table.item(row, 0).text())
        
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT * FROM Promotions WHERE PromotionId = ?", (promo_id,))
            promo = cursor.fetchone()
            cursor.close()
            
            if promo:
                self.current_promotion = dict(promo)
                self.name_input.setText(promo['PromotionName'])
                self.discount_type_combo.setCurrentText(promo['DiscountType'])
                self.discount_value_input.setText(str(promo['DiscountValue']))
                self.start_date_input.setDate(QDate.fromString(str(promo['StartDate']), "yyyy-MM-dd"))
                self.end_date_input.setDate(QDate.fromString(str(promo['EndDate']), "yyyy-MM-dd"))
                self.min_order_input.setText(str(promo['MinimumOrderValue']) if promo['MinimumOrderValue'] else "")
                self.priority_input.setValue(promo['Priority'])
                
                # Выбор продуктов
                product_ids = [int(p.strip()) for p in promo['ApplicableProducts'].split(',')]
                for i in range(self.products_list.count()):
                    item = self.products_list.item(i)
                    prod_id = int(item.text().split(' - ')[0])
                    item.setSelected(prod_id in product_ids)
                
                self.save_button.setEnabled(True)
                self.delete_button.setEnabled(True)
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки промоакции:\n{e}")
            
    def check_conflicts(self, promo_data, exclude_id=None):
        """Проверка конфликтов с существующими промоакциями"""
        try:
            cursor = self.db_conn.cursor()
            
            # Получаем все существующие промоакции с тем же приоритетом
            query = """
            SELECT * FROM Promotions 
            WHERE Priority = ?
            AND (DATE(StartDate) <= DATE(?) AND DATE(EndDate) >= DATE(?))
            """
            params = [promo_data['priority'], promo_data['end_date'], promo_data['start_date']]
            
            if exclude_id:
                query += " AND PromotionId != ?"
                params.append(exclude_id)
            
            cursor.execute(query, params)
            potential_conflicts = cursor.fetchall()
            cursor.close()
            
            conflicts = []
            new_products = set(promo_data['products'])
            
            for existing in potential_conflicts:
                existing_dict = dict(existing)
                existing_products = set(existing_dict['ApplicableProducts'].split(','))
                conflicting_products = new_products.intersection(existing_products)
                
                if conflicting_products:
                    # Вычисляем период пересечения
                    overlap_start = max(
                        datetime.strptime(promo_data['start_date'], '%Y-%m-%d'),
                        datetime.strptime(existing_dict['StartDate'], '%Y-%m-%d')
                    )
                    overlap_end = min(
                        datetime.strptime(promo_data['end_date'], '%Y-%m-%d'),
                        datetime.strptime(existing_dict['EndDate'], '%Y-%m-%d')
                    )
                    
                    conflicts.append({
                        'existing_promo': {
                            'id': existing_dict['PromotionId'],
                            'name': existing_dict['PromotionName'],
                            'priority': existing_dict['Priority'],
                            'start_date': str(existing_dict['StartDate']),
                            'end_date': str(existing_dict['EndDate'])
                        },
                        'products': [f"{p}:{MOCK_PRODUCTS.get(int(p), 'Unknown')}" for p in conflicting_products],
                        'overlap_start': overlap_start.strftime('%Y-%m-%d'),
                        'overlap_end': overlap_end.strftime('%Y-%m-%d')
                    })
            
            return conflicts
            
        except Exception as e:
            print(f"Ошибка проверки конфликтов: {e}")
            return []
            
    def add_promotion(self):
        """Добавление новой промоакции"""
        if not self.validate_form():
            return
        
        promo_data = self.get_form_data()
        
        # Проверка конфликтов
        conflicts = self.check_conflicts(promo_data)
        
        if conflicts:
            wizard = ConflictResolutionWizard(self, conflicts, promo_data)
            if wizard.exec_() == QDialog.Accepted:
                resolutions = wizard.get_resolutions()
                # Применяем разрешения
                if 'new_priority' in resolutions:
                    promo_data['priority'] = resolutions['new_priority']
                if 'new_start_date' in resolutions:
                    promo_data['start_date'] = resolutions['new_start_date']
                    promo_data['end_date'] = resolutions['new_end_date']
                if 'remove_products' in resolutions:
                    for prod in resolutions['remove_products']:
                        prod_id = prod.split(':')[0]
                        if prod_id in promo_data['products']:
                            promo_data['products'].remove(prod_id)
            else:
                return  # Пользователь отменил
        
        # Сохраняем промоакцию
        try:
            cursor = self.db_conn.cursor()
            query = """
            INSERT INTO Promotions 
            (PromotionName, DiscountType, DiscountValue, ApplicableProducts, 
             StartDate, EndDate, MinimumOrderValue, Priority)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            cursor.execute(query, (
                promo_data['name'],
                promo_data['discount_type'],
                promo_data['discount_value'],
                ','.join(promo_data['products']),
                promo_data['start_date'],
                promo_data['end_date'],
                promo_data['min_order'] if promo_data['min_order'] else None,
                promo_data['priority']
            ))
            
            self.db_conn.commit()
            cursor.close()
            
            QMessageBox.information(self, "Успех", "Промоакция успешно добавлена!")
            self.load_promotions()
            self.clear_form()
            
        except sqlite3.Error as err:
            QMessageBox.critical(self, "Ошибка БД", f"Ошибка добавления промоакции:\n{err}")
            
    def save_promotion(self):
        """Сохранение изменений промоакции"""
        if not self.current_promotion or not self.validate_form():
            return
        
        promo_data = self.get_form_data()
        conflicts = self.check_conflicts(promo_data, self.current_promotion['PromotionId'])
        
        if conflicts:
            wizard = ConflictResolutionWizard(self, conflicts, promo_data)
            if wizard.exec_() == QDialog.Accepted:
                resolutions = wizard.get_resolutions()
                if 'new_priority' in resolutions:
                    promo_data['priority'] = resolutions['new_priority']
                if 'new_start_date' in resolutions:
                    promo_data['start_date'] = resolutions['new_start_date']
                    promo_data['end_date'] = resolutions['new_end_date']
                if 'remove_products' in resolutions:
                    for prod in resolutions['remove_products']:
                        prod_id = prod.split(':')[0]
                        if prod_id in promo_data['products']:
                            promo_data['products'].remove(prod_id)
            else:
                return
        
        try:
            cursor = self.db_conn.cursor()
            query = """
            UPDATE Promotions SET
            PromotionName = ?, DiscountType = ?, DiscountValue = ?,
            ApplicableProducts = ?, StartDate = ?, EndDate = ?,
            MinimumOrderValue = ?, Priority = ?
            WHERE PromotionId = ?
            """
            
            cursor.execute(query, (
                promo_data['name'], promo_data['discount_type'], promo_data['discount_value'],
                ','.join(promo_data['products']), promo_data['start_date'], promo_data['end_date'],
                promo_data['min_order'] if promo_data['min_order'] else None,
                promo_data['priority'], self.current_promotion['PromotionId']
            ))
            
            self.db_conn.commit()
            cursor.close()
            
            QMessageBox.information(self, "Успех", "Изменения сохранены!")
            self.load_promotions()
            self.clear_form()
            
        except sqlite3.Error as err:
            QMessageBox.critical(self, "Ошибка БД", f"Ошибка сохранения:\n{err}")
    
    def delete_promotion(self):
        """Удаление промоакции"""
        if not self.current_promotion:
            return
        
        reply = QMessageBox.question(self, "Подтверждение", 
                                     f"Вы уверены, что хотите удалить промоакцию '{self.current_promotion['PromotionName']}'?",
                                     QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                cursor = self.db_conn.cursor()
                cursor.execute("DELETE FROM Promotions WHERE PromotionId = ?", 
                             (self.current_promotion['PromotionId'],))
                self.db_conn.commit()
                cursor.close()
                
                QMessageBox.information(self, "Успех", "Промоакция удалена!")
                self.load_promotions()
                self.clear_form()
                
            except sqlite3.Error as err:
                QMessageBox.critical(self, "Ошибка БД", f"Ошибка удаления:\n{err}")
    
    def validate_form(self):
        """Валидация формы"""
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите название промоакции")
            return False
        
        try:
            discount_value = float(self.discount_value_input.text())
            if discount_value <= 0:
                raise ValueError
        except:
            QMessageBox.warning(self, "Ошибка", "Введите корректное значение скидки")
            return False
        
        if self.start_date_input.date() > self.end_date_input.date():
            QMessageBox.warning(self, "Ошибка", "Дата окончания должна быть позже даты начала")
            return False
        
        if not self.products_list.selectedItems():
            QMessageBox.warning(self, "Ошибка", "Выберите хотя бы один продукт")
            return False
        
        return True
    
    def get_form_data(self):
        """Получение данных из формы"""
        selected_products = []
        for item in self.products_list.selectedItems():
            prod_id = item.text().split(' - ')[0]
            selected_products.append(prod_id)
        
        return {
            'name': self.name_input.text().strip(),
            'discount_type': self.discount_type_combo.currentText(),
            'discount_value': float(self.discount_value_input.text()),
            'products': selected_products,
            'start_date': self.start_date_input.date().toString("yyyy-MM-dd"),
            'end_date': self.end_date_input.date().toString("yyyy-MM-dd"),
            'min_order': self.min_order_input.text().strip() if self.min_order_input.text().strip() else None,
            'priority': self.priority_input.value()
        }
    
    def clear_form(self):
        """Очистка формы"""
        self.name_input.clear()
        self.discount_type_combo.setCurrentIndex(0)
        self.discount_value_input.clear()
        self.min_order_input.clear()
        self.start_date_input.setDate(QDate.currentDate())
        self.end_date_input.setDate(QDate.currentDate().addDays(30))
        self.priority_input.setValue(1)
        self.products_list.clearSelection()
        self.current_promotion = None
        self.save_button.setEnabled(False)
        self.delete_button.setEnabled(False)
    
    def closeEvent(self, event):
        """Закрытие соединения с БД"""
        if self.db_conn:
            self.db_conn.close()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PromotionsApp()
    window.show()
    sys.exit(app.exec_())
    