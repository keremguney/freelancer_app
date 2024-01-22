from PyQt5.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout, QLineEdit, QTextEdit, QMessageBox
from database import insert_job

class AddJobWindow(QDialog):
    def __init__(self, user_id, db_connection, update_callback):
        super().__init__()

        self.user_id = user_id
        self.db_connection = db_connection
        self.update_callback = update_callback

        self.setWindowTitle("Add Job")
        self.setGeometry(200, 200, 400, 300)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.title_label = QLabel("Job Title:", self)
        layout.addWidget(self.title_label)

        self.title_input = QLineEdit(self)
        layout.addWidget(self.title_input)

        self.description_label = QLabel("Job Description:", self)
        layout.addWidget(self.description_label)

        self.description_input = QTextEdit(self)
        layout.addWidget(self.description_input)

        self.price_label = QLabel("Job Price:", self)
        layout.addWidget(self.price_label)

        self.price_input = QLineEdit(self)
        layout.addWidget(self.price_input)

        self.add_job_button = QPushButton("Add Job", self)
        self.add_job_button.clicked.connect(self.add_job)
        layout.addWidget(self.add_job_button)

    def add_job(self):
        title = self.title_input.text()
        description = self.description_input.toPlainText()
        price = self.price_input.text()

        try:
            price = int(price)
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid integer for the job price.")
            return

        if title and description and price >= 0:
            if insert_job(self.db_connection, title, description, price, self.user_id):
                self.update_callback()
                self.close()
            else:
                QMessageBox.warning(self, "Error", "Failed to insert job.")
        else:
            QMessageBox.warning(self, "Invalid Input", "Please provide both title and description, and ensure the price is a non-negative integer.")
