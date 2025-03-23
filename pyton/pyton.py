from dbadd import init_db, DB_CONFIG
import sys
import mysql.connector
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QLineEdit, \
                             QPushButton, QMessageBox, QListWidget, QComboBox
from PyQt5.QtGui import QIntValidator


class DodawanieProduktuDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dodawanie produktu")
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
    
    def wczytaj_kategorie(self):
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nazwa FROM kategorie")
        self.kategoria_combo.clear()
        for kat_id, nazwa in cursor.fetchall():
            self.kategoria_combo.addItem(nazwa, kat_id)
        conn.close()

    def zapisz_produkt(self):
        nazwa = self.nazwa_input.text()
        kategoria_id = self.kategoria_combo.currentData()
        cena = self.cena_input.text()
        ilosc = self.ilosc_input.text()
        promocja = self.promocja_button.isChecked()
        
        if not nazwa or not cena or not ilosc:
            QMessageBox.warning(self, "Błąd", "Wypełnij wszystkie pola.", QMessageBox.Ok)
            return
        
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO produkty (nazwa, kategoria_id, cena, ilosc, promocja) VALUES (%s, %s, %s, %s, %s)",
                       (nazwa, kategoria_id, cena, ilosc, promocja))
        conn.commit()
        conn.close()
        self.accept()

class LogowanieDialog(QDialog):
    def __init__(self, main_window=None):
        super().__init__()
        self.setWindowTitle("Logowanie")
        
        self.main_window = main_window
        self.layout = QVBoxLayout()
        
        self.username_label = QLabel("Nazwa użytkownika:")
        self.username_input = QLineEdit()
        self.layout.addWidget(self.username_label)
        self.layout.addWidget(self.username_input)
        
        self.password_label = QLabel("Hasło:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password_input)
        
        self.login_button = QPushButton("Zaloguj")
        self.login_button.clicked.connect(self.zaloguj)
        self.layout.addWidget(self.login_button)
        
        self.setLayout(self.layout)
    
    def zaloguj(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if username == "admin" and password == "admin":
            self.main_window.pokaz_panel("admin")
        else:
            self.main_window.pokaz_panel("user")
        
        self.accept()

#Okno dodawania do koszyka produktów 

class DodajDoKoszykaDialog(QDialog):
    def __init__(self, produkt_nazwa, produkt_cena, produkt_ilosc, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dodaj do koszyka")
        self.layout = QVBoxLayout()

        self.produkt_label = QLabel(f"Produkt: {produkt_nazwa}")
        self.layout.addWidget(self.produkt_label)

        self.ilosc_label = QLabel("Ilość:")
        self.ilosc_input = QLineEdit()
        
        # Konwertujemy produkt_ilosc na liczbę całkowitą
        self.ilosc_input.setValidator(QIntValidator(1, int(produkt_ilosc)))  # Maksymalna ilość dostępna
        self.layout.addWidget(self.ilosc_label)
        self.layout.addWidget(self.ilosc_input)

        self.dodaj_button = QPushButton("Dodaj do koszyka")
        self.dodaj_button.clicked.connect(lambda: self.dodaj_do_koszyka(produkt_nazwa, produkt_cena))
        self.layout.addWidget(self.dodaj_button)

        self.setLayout(self.layout)

    def dodaj_do_koszyka(self, produkt_nazwa, produkt_cena):
        ilosc = self.ilosc_input.text()

        if not ilosc or int(ilosc) <= 0:
            QMessageBox.warning(self, "Błąd", "Podaj poprawną ilość.", QMessageBox.Ok)
            return
        

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Sprawdzamy, czy produkt już istnieje w koszyku
        cursor.execute("""
        SELECT id FROM koszyk 
        WHERE uzytkownik_id = (SELECT id FROM uzytkownicy WHERE login = 'klient') 
        AND produkt_id = (SELECT id FROM produkty WHERE nazwa = %s)
        """, (produkt_nazwa,))
        
        produkt_w_koszyku = cursor.fetchone()

        if produkt_w_koszyku:
            # Jeśli produkt już jest w koszyku, zaktualizuj ilość
            cursor.execute("""
            UPDATE koszyk SET ilosc = ilosc + %s
            WHERE id = %s
            """, (ilosc, produkt_w_koszyku[0]))
        else:
            # Jeśli produkt nie ma w koszyku, dodaj go
            cursor.execute("""
            INSERT INTO koszyk (uzytkownik_id, produkt_id, ilosc) 
            SELECT (SELECT id FROM uzytkownicy WHERE login = 'klient'), id, %s 
            FROM produkty WHERE nazwa = %s
            """, (ilosc, produkt_nazwa))

        conn.commit()
        conn.close()
        self.accept()


class MainDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Panel główny")
        self.layout = QVBoxLayout()

        #dodaj do koszyka
        self.dodaj_do_koszyka_button = QPushButton("Dodaj do koszyka")
        self.dodaj_do_koszyka_button.clicked.connect(self.dodaj_do_koszyka)
        self.layout.addWidget(self.dodaj_do_koszyka_button)
        
        #dodaj podukt
        self.dodaj_button = QPushButton("Dodaj produkt")
        self.dodaj_button.clicked.connect(self.pokaz_okno_dodawania)
        self.layout.addWidget(self.dodaj_button)
        
        #Wyświetl listę
        self.wyswietl_button = QPushButton("Wyświetl listę")
        self.wyswietl_button.clicked.connect(self.wyswietl_liste)
        self.layout.addWidget(self.wyswietl_button)
        
        #Wyświetlanie listy
        self.produkty_list_widget = QListWidget()
        self.layout.addWidget(self.produkty_list_widget)
        
        #Podlicz koszyk
        self.podlicz_button = QPushButton("Podlicz")
        self.podlicz_button.clicked.connect(self.podlicz_cene)
        self.layout.addWidget(self.podlicz_button)
        
        self.setLayout(self.layout)
    
    #wywołanie okna dodawania
    def pokaz_okno_dodawania(self):
        dialog = DodawanieProduktuDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.wyswietl_liste()
    
    #wywołanie okna dodawania do koszyka
    def dodaj_do_koszyka(self):
        selected_item = self.produkty_list_widget.currentItem()
        if selected_item:
            produkt_info = selected_item.text().split(" - ")
            produkt_nazwa = produkt_info[0]
            produkt_cena = produkt_info[1].replace(" PLN", "")
            produkt_ilosc = produkt_info[2].replace("Ilość: ", "")
            
            dialog = DodajDoKoszykaDialog(produkt_nazwa, produkt_cena, produkt_ilosc, self)
            dialog.exec_()
    
    #funkcja wyświelnie listy
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

    #funkcja podliczenia ceny
    def podlicz_cene(self):
        total = 0
        for row in range(self.produkty_list_widget.count()):
            item = self.produkty_list_widget.item(row)
            cena = item.text().split(" - ")[1].replace(" PLN", "")
            total += float(cena)
        QMessageBox.information(self, "Suma", f"Suma produktów: {total:.2f} PLN", QMessageBox.Ok)

    #sprawdzenie użytkownika admin/user
    def pokaz_panel(self, rola):
        if rola == 'admin':
            self.dodaj_button.setEnabled(True)
        else:
            self.dodaj_button.setEnabled(False)

def main():
    init_db()
    
    app = QApplication(sys.argv)
    
    # Tworzymy główne okno aplikacji
    main_window = MainDialog()
    
    # Tworzymy okno logowania i przekazujemy główne okno
    logowanie = LogowanieDialog(main_window=main_window)
    if logowanie.exec_() == QDialog.Accepted:
        main_window.show()
        sys.exit(app.exec_())

if __name__ == "__main__":
    main()
