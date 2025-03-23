import mysql.connector

# Konfiguracja bazy danych
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',  
    'password': '', 
    'database': 'sklep'
}

def init_db():
    conn = mysql.connector.connect(host=DB_CONFIG['host'], user=DB_CONFIG['user'], password=DB_CONFIG['password'])
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS sklep")
    cursor.execute("USE sklep")  
    cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS uzytkownicy (
        id INT AUTO_INCREMENT PRIMARY KEY,
        login VARCHAR(255) NOT NULL UNIQUE,
        haslo VARCHAR(255) NOT NULL,
        rola ENUM('admin', 'klient') DEFAULT 'klient'
    )""")
    cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS koszyk (
        id INT AUTO_INCREMENT PRIMARY KEY,
        uzytkownik_id INT,
        produkt_id INT,
        ilosc INT,
        FOREIGN KEY (produkt_id) REFERENCES produkty(id));
    """)
    cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS kategorie (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nazwa VARCHAR(255) NOT NULL
    )""")
    cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS produkty (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nazwa VARCHAR(255) NOT NULL,
        kategoria_id INT,
        cena DECIMAL(10,2),
        ilosc INT,
        promocja BOOLEAN DEFAULT FALSE,
        FOREIGN KEY (kategoria_id) REFERENCES kategorie(id)
    )""")
    cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS zamowienia (
        id INT AUTO_INCREMENT PRIMARY KEY,
        uzytkownik_id INT,
        data_zlozenia TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS zamowienia_produkty (
        id INT AUTO_INCREMENT PRIMARY KEY,
        zamowienie_id INT,
        produkt_id INT,
        ilosc INT,
        cena DECIMAL(10,2),
        FOREIGN KEY (zamowienie_id) REFERENCES zamowienia(id),
        FOREIGN KEY (produkt_id) REFERENCES produkty(id)
    )""")

    # Wstawianie przykładowych wartości
    cursor.execute("INSERT IGNORE INTO uzytkownicy (login, haslo, rola) VALUES ('admin', 'admin123', 'admin')")
    cursor.execute("INSERT IGNORE INTO uzytkownicy (login, haslo, rola) VALUES ('klient', 'klient', 'klient')")
    cursor.execute("INSERT IGNORE INTO kategorie (nazwa) VALUES ('Elektronika')")
    cursor.execute("INSERT IGNORE INTO kategorie (nazwa) VALUES ('Odzież')")
    cursor.execute("INSERT IGNORE INTO kategorie (nazwa) VALUES ('Sport')")
    cursor.execute(""" 
    INSERT IGNORE INTO produkty (nazwa, kategoria_id, cena, ilosc, promocja)
    VALUES
    ('Laptop', 1, 3000.00, 10, FALSE),
    ('Smartfon', 1, 1500.00, 20, TRUE),
    ('Koszulka', 2, 50.00, 100, FALSE),
    ('Buty sportowe', 3, 250.00, 50, TRUE)
    """)

    conn.commit()
    conn.close()

def get_connection():
    """Zwróć połączenie z bazą danych"""
    conn = mysql.connector.connect(**DB_CONFIG)
    return conn
