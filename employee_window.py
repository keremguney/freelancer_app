from PyQt5.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QScrollArea, QWidget, QPushButton, QHBoxLayout, QMessageBox, QInputDialog, QLineEdit, QDialog
from database import list_all_jobs, insert_offer, select_offers_for_job, select_job_details, get_user_balance, update_user_balance, update_job_status
import praw

class MoneyAddedDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Money Added")
        self.setGeometry(200, 200, 300, 150)

        layout = QVBoxLayout(self)

        label = QLabel("200 added to your balance.", self)
        layout.addWidget(label)

        ok_button = QPushButton("OK", self)
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)

class UsernameNotFoundDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Username Not Found")
        self.setGeometry(200, 200, 300, 150)

        layout = QVBoxLayout(self)

        label = QLabel("Username not found.", self)
        layout.addWidget(label)

        ok_button = QPushButton("OK", self)
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)

class AlreadyCollectedDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("You've already collected your gift")
        self.setGeometry(200, 200, 300, 150)

        layout = QVBoxLayout(self)

        label = QLabel("You've already collected your gift.", self)
        layout.addWidget(label)

        ok_button = QPushButton("OK", self)
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)

class RedditUsernameWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Enter Reddit Username")
        self.setGeometry(200, 200, 300, 150)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.username_label = QLabel("Enter your Reddit username:", self)
        layout.addWidget(self.username_label)

        self.username_input = QLineEdit(self)
        layout.addWidget(self.username_input)

        self.submit_button = QPushButton("Submit", self)
        self.submit_button.clicked.connect(self.accept)
        layout.addWidget(self.submit_button)

    def submit_username(self):
        username = self.username_input.text()
        if username:
            self.parent().set_reddit_username(username)
            self.close()

class EmployeeWindow(QMainWindow):
    def __init__(self, user_id, db_connection):
        super().__init__()

        self.setWindowTitle("Employee")
        self.setGeometry(100, 100, 800, 600)

        self.user_id = user_id
        self.db_connection = db_connection

        self.init_ui()
        self.money_added = False

    def init_ui(self):
        self.balance = get_user_balance(self.db_connection, self.user_id)
        self.balance_label = QLabel(f"Balance: {self.balance}", self)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        layout.addWidget(self.balance_label)

        self.check_follow_button = QPushButton("Write a comment about us!", self)
        self.check_follow_button.clicked.connect(self.open_reddit_username_window)
        layout.addWidget(self.check_follow_button)

        self.job_list_label = QLabel("Available Jobs:", self)
        layout.addWidget(self.job_list_label)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        layout.addWidget(self.scroll_area)

        self.job_list_widget = QWidget(self)
        self.job_list_layout = QVBoxLayout(self.job_list_widget)
        self.scroll_area.setWidget(self.job_list_widget)

        self.refresh_button = QPushButton("Refresh Jobs", self)
        self.refresh_button.clicked.connect(self.update_job_list)
        layout.addWidget(self.refresh_button)

        self.update_job_list()

    def update_job_list(self):
        for i in reversed(range(self.job_list_layout.count())):
            item = self.job_list_layout.takeAt(i)
            widget = item.widget()
            if widget:
                widget.setParent(None)

        jobs = list_all_jobs(self.db_connection)

        for job in jobs:
            job_widget = QWidget(self)
            job_layout = QHBoxLayout(job_widget)

            job_label = QLabel(f"Job Title: {job[1]}\nDescription: {job[2]}\nPrice: {job[3]}\nStatus: {job[5]}", self)
            job_layout.addWidget(job_label)

            if job[5] == 'accepted':
                finish_job_button = QPushButton("Finish Job", self)
                finish_job_button.clicked.connect(lambda _, job_id=job[0]: self.finish_job(job_id))
                job_layout.addWidget(finish_job_button)
            elif job[5] == 'finished':
                finish_button = QPushButton("Job Finished", self)
                finish_button.clicked.connect(self.do_nothing)
                job_layout.addWidget(finish_button)
            else:
                make_offer_button = QPushButton("Make Offer", self)
                make_offer_button.clicked.connect(lambda _, job_id=job[0], job_price=job[3]: self.make_offer(job_id, job_price))
                job_layout.addWidget(make_offer_button)

            self.job_list_layout.addWidget(job_widget)

        self.balance_label.repaint()
        self.scroll_area.repaint()

    def make_offer(self, job_id, job_price):
        existing_offers = select_offers_for_job(self.db_connection, job_id, self.user_id)

        if existing_offers:
            QMessageBox.warning(self, "Duplicate Offer", "You have already made an offer for this job.")
        else:
            offer_price_input, ok_pressed = QInputDialog.getInt(
                self, "Make Offer", f"Enter your offer for the job (current price: {job_price}):", job_price, 0, job_price * 2, 10
            )

            if ok_pressed:
                if offer_price_input >= job_price:
                    if insert_offer(self.db_connection, job_id, self.user_id, offer_price_input):
                        self.update_job_list()
                        QMessageBox.information(self, "Offer Made", f"Offer of {offer_price_input} made successfully for job with ID {job_id}")
                    else:
                        QMessageBox.warning(self, "Error", "Failed to make offer.")
                else:
                    QMessageBox.warning(self, "Invalid Offer", "Your offer must be higher than the current job price.")

    def finish_job(self, job_id):
        job_details = select_job_details(self.db_connection, job_id)
        if not job_details:
            print(f"Error: Job with ID {job_id} not found.")
            return

        employer_id = job_details[4]
        job_price = job_details[3]
        job_status = job_details[5]

        if job_status != 'accepted':
            print(f"Error: Job with ID {job_id} is not in 'accepted' status.")
            return

        if not update_job_status(self.db_connection, job_id, 'finished'):
            print(f"Error updating job status for Job ID {job_id}.")
            return

        employer_balance = get_user_balance(self.db_connection, employer_id)
        if employer_balance is None:
            print(f"Error: Unable to retrieve balance for Employer ID {employer_id}.")
            return

        employer_balance -= job_price

        if not update_user_balance(self.db_connection, employer_id, employer_balance):
            print(f"Error updating balance for Employer ID {employer_id}.")
            return

        employee_balance = get_user_balance(self.db_connection, self.user_id)
        if employee_balance is None:
            print(f"Error: Unable to retrieve balance for Employee ID {self.user_id}.")
            return

        employee_balance += job_price

        if not update_user_balance(self.db_connection, self.user_id, employee_balance):
            print(f"Error updating balance for Employee ID {self.user_id}.")
            return

        print(f"Job with ID {job_id} finished successfully.")

        self.update_job_list()
        self.update_balance_label()

    def do_nothing(self):
        pass

    def check_comments(self, username):
        reddit = praw.Reddit(
            client_id='P_A7f2dBz8YNB5JNOGZI3Q',
            client_secret='Gqz7A6sDDOJT58CWi2LpzBQHMr94uA',
            user_agent='doesnt matter',
        )

        url = "https://www.reddit.com/user/garajimdakiejder/comments/18yal1v/ornek_baslik/"
        submission = reddit.submission(url=url)

        for comment in submission.comments.list():
            if comment.author.name == username:
                if not self.money_added:
                    current_balance = get_user_balance(self.db_connection, self.user_id)
                    new_balance = current_balance + 200
                    update_user_balance(self.db_connection, self.user_id, new_balance)

                    money_added_dialog = MoneyAddedDialog(self)
                    money_added_dialog.exec_()
                    print(f"Added 200 to the user balance. New balance: {new_balance}")
                    self.money_added = True
                    self.update_balance_label()
                    return True
                elif self.money_added:
                    already_collected_dialog = AlreadyCollectedDialog(self)
                    already_collected_dialog.exec()
            else:
                print("username not found")
                username_not_found_dialog = UsernameNotFoundDialog(self)
                username_not_found_dialog.exec_()

                print("Username not found.")
                return False

    def open_reddit_username_window(self):
        reddit_username_window = RedditUsernameWindow(self)
        result = reddit_username_window.exec_()

        if result == QDialog.Accepted:
            entered_username = reddit_username_window.username_input.text()
            print(f"Entered Reddit username: {entered_username}")

            has_commented = self.check_comments(entered_username)
   
    def update_balance_label(self):
        self.balance = get_user_balance(self.db_connection, self.user_id)
        self.balance_label.setText(f"Balance: {self.balance}")
        self.repaint()
