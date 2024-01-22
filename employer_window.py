from PyQt5.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QScrollArea, QMessageBox, QDialog
from add_job_window import AddJobWindow
from update_job_window import UpdateJobWindow
from database import select_jobs, insert_job, delete_job, get_user_balance, list_offers_for_job, accept_offer

class EmployerWindow(QMainWindow):
    def __init__(self, user_id, db_connection):
        super().__init__()

        self.user_id = user_id
        self.db_connection = db_connection

        self.setWindowTitle("Employer")
        self.setGeometry(100, 100, 800, 600)

        self.init_ui()

    def init_ui(self):

        self.balance = get_user_balance(self.db_connection, self.user_id)
        self.balance_label = QLabel(f"Balance: {self.balance}", self)

        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)

        layout.addWidget(self.balance_label)

        self.job_list_label = QLabel("Your Jobs:", self)
        layout.addWidget(self.job_list_label)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        layout.addWidget(self.scroll_area)

        self.job_list_widget = QWidget(self)
        self.job_list_layout = QVBoxLayout(self.job_list_widget)
        self.scroll_area.setWidget(self.job_list_widget)

        self.add_job_button = QPushButton("Add Job", self)
        self.add_job_button.clicked.connect(self.open_add_job_window)
        layout.addWidget(self.add_job_button)

        self.update_job_list()

        self.setCentralWidget(central_widget)
    
    def update_job_list(self):
        jobs = select_jobs(self.db_connection, self.user_id)

        for i in reversed(range(self.job_list_layout.count())):
            item = self.job_list_layout.takeAt(i)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        for job in jobs:
            job_widget = QWidget(self)
            job_layout = QVBoxLayout(job_widget)

            job_label = QLabel(f"Job Title: {job[1]}\nDescription: {job[2]}\nPrice: {job[3]}", self)
            job_layout.addWidget(job_label)

            delete_button = QPushButton("Delete", self)
            delete_button.clicked.connect(lambda _, job_id=job[0]: self.delete_job(job_id))
            job_layout.addWidget(delete_button)

            update_button = QPushButton("Update", self)
            update_button.clicked.connect(lambda _, job_id=job[0]: self.update_job(job_id))
            job_layout.addWidget(update_button)


            list_offers_button = QPushButton("List Offers", self)
            list_offers_button.clicked.connect(lambda _, job_id=job[0]: self.list_offers(job_id))
            job_layout.addWidget(list_offers_button)
           
            self.job_list_layout.addWidget(job_widget)

        self.balance_label.repaint()
        self.scroll_area.repaint()

    def update_job(self, job_id):
        update_job_window = UpdateJobWindow(job_id, self.db_connection, self.update_job_list)
        update_job_window.exec_()
    
    def open_add_job_window(self):
        add_job_window = AddJobWindow(self.user_id, self.db_connection, self.update_job_list)
        add_job_window.exec_()

    def delete_job(self, job_id):
        if delete_job(self.db_connection, job_id):
            self.update_job_list()
            print(f"Job with ID {job_id} deleted successfully.")
        else:
            print(f"Failed to delete job with ID {job_id}.")
    
    def list_offers(self, job_id):
        offers = list_offers_for_job(self.db_connection, job_id)

        if offers:
            offers_text = "\n".join(f"Employee ID: {offer[2]}, Offer Price: {offer[3]}" for offer in offers)

            offer_list_window = QDialog(self)
            offer_list_window.setWindowTitle(f"Offers for Job ID {job_id}")
            offer_list_window.setGeometry(300, 300, 400, 200)

            layout = QVBoxLayout(offer_list_window)

            offers_label = QLabel(f"Offers for Job ID {job_id}:\n{offers_text}", offer_list_window)
            layout.addWidget(offers_label)

            for offer in offers:
                accept_button = QPushButton(f"Accept Offer {offer[3]}", offer_list_window)
                accept_button.clicked.connect(lambda _, offer_id=offer[0]: self.accept_offer(offer_id))
                layout.addWidget(accept_button)

            offer_list_window.exec_()

        else:
            QMessageBox.information(self, "No Offers", f"No offers have been made for Job ID {job_id}")

    def accept_offer(self, offer_id):
        if accept_offer(self.db_connection, offer_id):
            QMessageBox.information(self, "Offer Accepted", f"Offer with ID {offer_id} accepted successfully.")
            self.update_job_list()
        else:
            QMessageBox.warning(self, "Error", f"Failed to accept offer with ID {offer_id}.")
