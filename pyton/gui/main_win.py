from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, 
                            QListWidget, QMessageBox)
from database.db import get_connection
from .dialogs import ProductDialog, CartDialog

class MainWindow(QDialog):
    def __init__(self, user_role, parent=None):
        super().__init__(parent)
        self.user_role = user_role
        self.setWindowTitle("Sklep - Panel główny")
        self.setup_ui()
        self.load_products()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        self.products_list = QListWidget()
        
        self.add_to_cart_btn = QPushButton("Dodaj do koszyka")
        self.add_to_cart_btn.clicked.connect(self.add_to_cart)
        
        self.add_product_btn = QPushButton("Dodaj produkt")
        self.add_product_btn.clicked.connect(self.add_product)
        self.add_product_btn.setEnabled(self.user_role == 'admin')
        
        self.view_cart_btn = QPushButton("Pokaż koszyk")
        self.view_cart_btn.clicked.connect(self.view_cart)
        
        self.refresh_btn = QPushButton("Odśwież listę")
        self.refresh_btn.clicked.connect(self.load_products)
        
        layout.addWidget(self.products_list)
        layout.addWidget(self.add_to_cart_btn)
        layout.addWidget(self.add_product_btn)
        layout.addWidget(self.view_cart_btn)
        layout.addWidget(self.refresh_btn)
        
        self.setLayout(layout)

    def load_products(self):
        self.products_list.clear()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT p.nazwa, k.nazwa, p.cena, p.ilosc 
        FROM produkty p JOIN kategorie k ON p.kategoria_id = k.id
        """)
        
        for name, category, price, quantity in cursor.fetchall():
            self.products_list.addItem(f"{name} ({category}) - {price} PLN - Dostępne: {quantity}")
        
        conn.close()

    def add_to_cart(self):
        selected = self.products_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "Błąd", "Wybierz produkt z listy")
            return
            
        product_info = selected.text().split(" - ")
        name = product_info[0].split(" (")[0]
        price = product_info[1].split()[0]
        quantity = int(product_info[2].split(": ")[1])
        
        dialog = CartDialog(name, price, quantity, self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_products()

    def add_product(self):
        dialog = ProductDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_products()

    def view_cart(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT p.nazwa, k.ilosc, p.cena 
        FROM koszyk k JOIN produkty p ON k.produkt_id = p.id
        WHERE k.uzytkownik_id = (SELECT id FROM uzytkownicy WHERE login = 'klient')
        """)
        
        cart_dialog = QDialog(self)
        cart_dialog.setWindowTitle("Twój koszyk")
        layout = QVBoxLayout()
        
        cart_list = QListWidget()
        total = 0
        
        for name, quantity, price in cursor.fetchall():
            item_total = float(price) * int(quantity)
            cart_list.addItem(f"{name} - {quantity} x {price} PLN = {item_total:.2f} PLN")
            total += item_total
        
        layout.addWidget(cart_list)
        layout.addWidget(QLabel(f"Suma całkowita: {total:.2f} PLN"))
        
        checkout_btn = QPushButton("Złóż zamówienie")
        checkout_btn.clicked.connect(lambda: self.checkout(cart_dialog))
        layout.addWidget(checkout_btn)
        
        cart_dialog.setLayout(layout)
        cart_dialog.exec_()
        conn.close()

    def checkout(self, dialog):
        # Implementacja składania zamówienia
        QMessageBox.information(self, "Sukces", "Zamówienie zostało złożone!")
        dialog.accept()
        self.load_products()