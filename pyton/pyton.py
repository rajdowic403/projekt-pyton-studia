import sys
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, 
                            QPushButton, QMessageBox, QListWidget, QComboBox, QApplication)
from database.db import init_db
from gui.dialogs import LoginDialog
from gui.main_win import MainWindow

def main():
    init_db()
    app = QApplication(sys.argv)
    
    login_dialog = LoginDialog()
    if login_dialog.exec_() == QDialog.Accepted:
        user_role = login_dialog.authenticate()
        if user_role:
            main_window = MainWindow(user_role)
            main_window.show()
            sys.exit(app.exec_())

if __name__ == "__main__":
    main()