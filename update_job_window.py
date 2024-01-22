from PyQt5.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout, QLineEdit, QTextEdit, QMessageBox
from database import update_job_details, select_job_details

class UpdateJobWindow(QDialog):
    def __init__(self, job_id, db_connection, update_callback):
        super().__init__()

        self.job_id = job_id
        self.db_connection = db_connection
        self.update_callback = update_callback

        self.setWindowTitle("Update Job")
        self.setGeometry(200, 200, 400, 300)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        job_details = select_job_details(self.db_connection, self.job_id)

        self.title_label = QLabel("Job Title:", self)
        layout.addWidget(self.title_label)

        self.title_input = QLineEdit(self)
        self.title_input.setText(job_details[1])
        layout.addWidget(self.title_input)

        self.description_label = QLabel("Job Description:", self)
        layout.addWidget(self.description_label)

        self.description_input = QTextEdit(self)
        self.description_input.setPlainText(job_details[2])
        layout.addWidget(self.description_input)

        self.price_label = QLabel("Job Price:", self)
        layout.addWidget(self.price_label)

        self.price_input = QLineEdit(self)
        self.price_input.setText(str(job_details[3]))
        layout.addWidget(self.price_input)

        self.update_job_button = QPushButton("Update Job", self)
        self.update_job_button.clicked.connect(self.update_job)
        layout.addWidget(self.update_job_button)

    def update_job(self):
        title = self.title_input.text()
        description = self.description_input.toPlainText()
        price = self.price_input.text()

        try:
            price = int(price)

            if price < 0:
                raise ValueError("Price must be a positive integer.")
        except ValueError as e:
            QMessageBox.warning(self, "Invalid Price", str(e))
            return

        if title and description:
            if update_job_details(self.db_connection, self.job_id, title, price, description):
                self.update_callback()
                self.close()
            else:
                print("Failed to update job.")
        else:
            print("Please provide both title and description.")
