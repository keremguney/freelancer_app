import sys
from PyQt5.QtWidgets import QMainWindow, QLabel, QPushButton, QComboBox, QLineEdit, QMessageBox, QDialog
from register_window import RegisterWindow
from employer_window import EmployerWindow
from employee_window import EmployeeWindow
from database import create_db_connection, create_user_table, select_user, create_tables

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.db_connection = create_db_connection()
        create_tables()

        self.setWindowTitle("Register and Log In")
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

        self.usertype_label = QLabel("User Type:", self)
        self.usertype_label.move(50, 150)

        self.usertype_combobox = QComboBox(self)
        self.usertype_combobox.addItem("Employer")
        self.usertype_combobox.addItem("Employee")
        self.usertype_combobox.move(150, 150)

        self.login_button = QPushButton("Log In", self)
        self.login_button.move(50, 200)
        self.login_button.clicked.connect(self.login)

        self.register_button = QPushButton("Register", self)
        self.register_button.move(160, 200)
        self.register_button.clicked.connect(self.open_register_window)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        usertype = self.usertype_combobox.currentText()

        user = select_user(self.db_connection, username, password, usertype)
        if user is not None:
            self.close()
            if usertype == "Employer":
                self.open_employer_window(user[0])
            elif usertype == "Employee":
                self.open_employee_window(user[0])
        else:
            QMessageBox.warning(self, "Could not log in", "Username or password is not correct")

    def open_register_window(self):
        self.register_window = RegisterWindow(self.db_connection)
        self.register_window.show()

    def open_employer_window(self, user_id):
        self.employer_window = EmployerWindow(user_id, self.db_connection)
        self.employer_window.show()

    def open_employee_window(self, user_id):
        self.employee_window = EmployeeWindow(user_id, self.db_connection)
        self.employee_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec())
