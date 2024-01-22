from PyQt5.QtWidgets import QDialog, QLabel, QPushButton, QComboBox, QLineEdit, QMessageBox
from database import create_db_connection, check_username_availability, insert_user

class RegisterWindow(QDialog):
    def __init__(self, db_connection):
        super().__init__()

        self.db_connection = db_connection

        self.setWindowTitle("Register Now!")
        self.setGeometry(100, 100, 300, 250)

        self.username_label = QLabel("Username:", self)
        self.username_label.move(50, 50)

        self.username_input = QLineEdit(self)
        self.username_input.move(150, 50)

        self.password_label = QLabel("Password:", self)
        self.password_label.move(50, 100)

        self.password_input = QLineEdit(self)
        self.password_input.move(150, 100)
        self.password_input.setEchoMode(QLineEdit.Password)

        self.usertype_label = QLabel("User type:", self)
        self.usertype_label.move(50, 150)

        self.usertype_combobox = QComboBox(self)
        self.usertype_combobox.addItem("Employer")
        self.usertype_combobox.addItem("Employee")
        self.usertype_combobox.move(150, 150)

        self.register_button = QPushButton("Register", self)
        self.register_button.move(100, 200)
        self.register_button.clicked.connect(self.register)

    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()
        usertype = self.usertype_combobox.currentText()
        balance = 500

        if check_username_availability(self.db_connection, username):
            QMessageBox.warning(self, "Username Taken", "Username is already taken. Please choose another.")
        else:
            if insert_user(self.db_connection, username, password, usertype):
                QMessageBox.information(self, "Registration Successful", "User registered successfully")
                self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    register_window = RegisterWindow(create_db_connection())
    register_window.show()
    sys.exit(app.exec())
