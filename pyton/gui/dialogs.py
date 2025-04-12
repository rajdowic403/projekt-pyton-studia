from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, 
                            QPushButton, QMessageBox, QListWidget, QComboBox)
from PyQt5.QtGui import QIntValidator
from database.db import get_connection

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Logowanie")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        
        layout.addWidget(QLabel("Nazwa użytkownika:"))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel("Hasło:"))
        layout.addWidget(self.password_input)
        
        login_btn = QPushButton("Zaloguj")
        login_btn.clicked.connect(self.authenticate)
        layout.addWidget(login_btn)
        
        self.setLayout(layout)

    def authenticate(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT haslo, rola FROM uzytkownicy WHERE login = %s", (username,))
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0] == password:
            self.accept()
            return result[1]  # Zwraca rolę użytkownika
        else:
            QMessageBox.warning(self, "Błąd", "Nieprawidłowy login lub hasło")
            return None

class ProductDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dodaj produkt")
        self.setup_ui()
        self.load_categories()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        self.name_input = QLineEdit()
        self.category_combo = QComboBox()
        self.price_input = QLineEdit()
        self.quantity_input = QLineEdit()
        self.discount_check = QPushButton("Promocja")
        self.discount_check.setCheckable(True)
        
        layout.addWidget(QLabel("Nazwa:"))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("Kategoria:"))
        layout.addWidget(self.category_combo)
        layout.addWidget(QLabel("Cena:"))
        layout.addWidget(self.price_input)
        layout.addWidget(QLabel("Ilość:"))
        layout.addWidget(self.quantity_input)
        layout.addWidget(self.discount_check)
        
        save_btn = QPushButton("Zapisz")
        save_btn.clicked.connect(self.save_product)
        layout.addWidget(save_btn)
        
        self.setLayout(layout)

    def load_categories(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nazwa FROM kategorie")
        self.category_combo.clear()
        for cat_id, name in cursor.fetchall():
            self.category_combo.addItem(name, cat_id)
        conn.close()

    def save_product(self):
        # Implementacja zapisywania produktu
        pass

class CartDialog(QDialog):
    def __init__(self, product_name, product_price, max_quantity, parent=None):
        super().__init__(parent)
        self.product_name = product_name
        self.product_price = product_price
        self.setWindowTitle("Dodaj do koszyka")
        self.setup_ui(max_quantity)

    def setup_ui(self, max_quantity):
        layout = QVBoxLayout()
        
        self.quantity_input = QLineEdit()
        self.quantity_input.setValidator(QIntValidator(1, max_quantity))
        
        layout.addWidget(QLabel(f"Produkt: {self.product_name}"))
        layout.addWidget(QLabel("Ilość:"))
        layout.addWidget(self.quantity_input)
        
        add_btn = QPushButton("Dodaj do koszyka")
        add_btn.clicked.connect(self.add_to_cart)
        layout.addWidget(add_btn)
        
        self.setLayout(layout)

    def add_to_cart(self):
        quantity = self.quantity_input.text()
        if not quantity or int(quantity) <= 0:
            QMessageBox.warning(self, "Błąd", "Podaj poprawną ilość")
            return
            
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            # Pobierz ID użytkownika i produktu
            cursor.execute("SELECT id FROM uzytkownicy WHERE login = 'klient'")
            user_id = cursor.fetchone()[0]
            
            cursor.execute("SELECT id FROM produkty WHERE nazwa = %s", (self.product_name,))
            product_id = cursor.fetchone()[0]
            
            # Sprawdź czy produkt już jest w koszyku
            cursor.execute("SELECT id, ilosc FROM koszyk WHERE uzytkownik_id = %s AND produkt_id = %s", 
                         (user_id, product_id))
            cart_item = cursor.fetchone()
            
            if cart_item:
                new_quantity = cart_item[1] + int(quantity)
                cursor.execute("UPDATE koszyk SET ilosc = %s WHERE id = %s", 
                             (new_quantity, cart_item[0]))
            else:
                cursor.execute("INSERT INTO koszyk (uzytkownik_id, produkt_id, ilosc) VALUES (%s, %s, %s)",
                             (user_id, product_id, quantity))
            
            # Zmniejsz ilość dostępnych produktów
            cursor.execute("UPDATE produkty SET ilosc = ilosc - %s WHERE id = %s", 
                         (quantity, product_id))
            
            conn.commit()
            QMessageBox.information(self, "Sukces", f"Dodano {quantity} szt. do koszyka")
            self.accept()
            
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Błąd", f"Wystąpił błąd: {str(e)}")
        finally:
            conn.close()