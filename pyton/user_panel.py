import mysql.connector
from PyQt5.QtWidgets import (QApplication, QDialog, QVBoxLayout, QLabel, QLineEdit,
                             QPushButton, QMessageBox, QListWidget, QComboBox)

#przenoszenie Funkcjonalności do osobnych plików
#Do zrobienia narazie robie dla testu


class UserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Panel główny")
        self.layout = QVBoxLayout()
        
        self.wyswietl_button = QPushButton("Wyświetl listę")
        self.wyswietl_button.clicked.connect(self.wyswietl_liste)
        self.layout.addWidget(self.wyswietl_button)
        
        self.produkty_list_widget = QListWidget()
        self.layout.addWidget(self.produkty_list_widget)

        self.koszyk_button = QPushButton("Dodaj do Koszyka")
        self.dodaj_button.clicked.connect(self.koszyk_dodawania)
        self.layout.addWidget(self.dodaj_button)

        self.koszyk_list_widget = QListWidget()
        self.layout.addWidget(self.koszyk_list_widget)


        self.podlicz_button = QPushButton("Podlicz")
        self.podlicz_button.clicked.connect(self.podlicz_cene)
        self.layout.addWidget(self.podlicz_button)


        
        self.setLayout(self.layout)
    ##tu ma być fukcjolaność do obsługi bazy danych
    def koszyk_dodawania(self):
        dialog = dodajDoKoszyka(self)
        if dialog.exec_() == QDialog.Accepted:
            self.wyswietl_liste()

    def wyswietl_liste(self):
        self.produkty_list_widget.clear()
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
        SELECT p.nazwa, k.nazwa, p.cena, SUM(p.ilosc) AS ilosc
        FROM produkty p 
        JOIN kategorie k ON p.kategoria_id = k.id
        GROUP BY p.nazwa, k.nazwa, p.cena
        """)
        for produkt, kategoria, cena, ilosc in cursor.fetchall():
            self.produkty_list_widget.addItem(f"{produkt} ({kategoria}) - {cena} PLN - Ilość: {ilosc}")
        conn.close()


    def podlicz_cene(self):
        total = 0
        for row in range(self.produkty_list_widget.count()):
            item = self.produkty_list_widget.item(row)
            cena = item.text().split(" - ")[1].replace(" PLN", "")
            total += float(cena)
        QMessageBox.information(self, "Suma", f"Suma produktów: {total:.2f} PLN", QMessageBox.Ok)

    def pokaz_panel(self, rola):
        if rola == 'admin':
            self.dodaj_button.setEnabled(True)
        else:
            self.dodaj_button.setEnabled(False)

class DodajKoszyk(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dodaj do Koszyka")
        self.layout = QVBoxLayout()
        
        self.nazwa_label = QLabel("Nazwa:")
        self.nazwa_input = QLineEdit()
        self.layout.addWidget(self.nazwa_label)
        self.layout.addWidget(self.nazwa_input)
        
        self.kategoria_label = QLabel("Kategoria:")
        self.kategoria_combo = QComboBox()
        self.layout.addWidget(self.kategoria_label)
        self.layout.addWidget(self.kategoria_combo)
        
        self.cena_label = QLabel("Cena:")
        self.cena_input = QLineEdit()
        self.layout.addWidget(self.cena_label)
        self.layout.addWidget(self.cena_input)
        
        self.ilosc_label = QLabel("Ilość:")
        self.ilosc_input = QLineEdit()
        self.layout.addWidget(self.ilosc_label)
        self.layout.addWidget(self.ilosc_input)
        
        self.promocja_button = QPushButton("Dodaj promocję")
        self.promocja_button.setCheckable(True)
        self.layout.addWidget(self.promocja_button)
        
        self.zapisz_button = QPushButton("Zapisz")
        self.zapisz_button.clicked.connect(self.zapisz_produkt)
        self.layout.addWidget(self.zapisz_button)
        
        self.setLayout(self.layout)
        self.wczytaj_kategorie()