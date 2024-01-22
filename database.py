import sqlite3

def create_db_connection():
    conn = None
    try:
        conn = sqlite3.connect("users.db")
        print("Connection successful.")
    except sqlite3.Error as e:
        print(f"Connection failed: {e}")
    return conn

def create_user_table(connection):
    create_table_query = """
        CREATE TABLE IF NOT EXISTS users ( 
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            usertype TEXT NOT NULL,
            balance INTEGER DEFAULT 500
        )
    """
    try:
        cursor = connection.cursor()
        cursor.execute(create_table_query)
        connection.commit()
        print("Table 'users' created successfully")
    except sqlite3.Error as e:
        print(f"Table creation failed: {e}")

def create_jobs_table(connection):
    create_table_query = """
        CREATE TABLE IF NOT EXISTS jobs ( 
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            price INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """
    try:
        cursor = connection.cursor()
        cursor.execute(create_table_query)
        connection.commit()
        print("Table 'jobs' created successfully")
    except sqlite3.Error as e:
        print(f"Table creation failed: {e}")

def create_offers_table(connection):
    create_table_query = """
        CREATE TABLE IF NOT EXISTS offers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            employee_id INTEGER NOT NULL,
            price INTEGER NOT NULL,
            accepted BOOLEAN DEFAULT 0,
            UNIQUE (job_id, employee_id),
            FOREIGN KEY (job_id) REFERENCES jobs(id),
            FOREIGN KEY (employee_id) REFERENCES users(id)
        )
    """
    try:
        cursor = connection.cursor()
        cursor.execute(create_table_query)
        connection.commit()
        print("Table 'offers' created successfully")
    except sqlite3.Error as e:
        print(f"Table creation failed: {e}")


def insert_offer(connection, job_id, employee_id, price):
    insert_offer_query = "INSERT INTO offers (job_id, employee_id, price) VALUES (?, ?, ?)"
    try:
        cursor = connection.cursor()
        cursor.execute(insert_offer_query, (job_id, employee_id, price))
        connection.commit()
        print("Offer inserted successfully")
        return True
    except sqlite3.IntegrityError as e:
        print(f"Error inserting offer: {e}")
        return False
    except sqlite3.Error as e:
        print(f"Other error inserting offer: {e}")
        return False

def check_username_availability(connection, username):
    check_username_query = "SELECT * FROM users WHERE username = ?"
    try:
        cursor = connection.cursor()
        cursor.execute(check_username_query, (username,))
        existing_user = cursor.fetchone()
        return existing_user is not None
    except sqlite3.Error as e:
        print(f"Error checking username availability: {e}")

def insert_user(connection, username, password, usertype):
    insert_user_query = "INSERT INTO users (username, password, usertype, balance) VALUES (?, ?, ?, ?)"
    try:
        cursor = connection.cursor()
        cursor.execute(insert_user_query, (username, password, usertype, 500))
        connection.commit()
        print("User inserted successfully")
        return True
    except sqlite3.Error as e:
        print(f"Error inserting user: {e}")
        return False

def select_user(connection, username, password, usertype):
    select_user_query = """
        SELECT * FROM users WHERE username=? AND password=? AND usertype=?
    """
    try:
        cursor = connection.cursor()
        cursor.execute(select_user_query, (username, password, usertype))
        user = cursor.fetchone()
        return user
    except sqlite3.Error as e:
        print(f"Error selecting user: {e}")
        return None

def select_user_id(connection, username):
    select_user_id_query = "SELECT id FROM users WHERE username = ?"
    try:
        cursor = connection.cursor()
        cursor.execute(select_user_id_query, (username,))
        user_id = cursor.fetchone()
        return user_id[0] if user_id else None
    except sqlite3.Error as e:
        print(f"Error selecting user ID: {e}")

def insert_job(connection, title, description, price, user_id):
    insert_job_query = "INSERT INTO jobs (title, description, price, user_id) VALUES (?, ?, ?, ?)"
    try:
        cursor = connection.cursor()
        cursor.execute(insert_job_query, (title, description, price, user_id))
        connection.commit()
        print("Job inserted successfully")
        return True
    except sqlite3.Error as e:
        print(f"Error inserting job: {e}")
        return False

def delete_job(connection, job_id):
    delete_job_query = "DELETE FROM jobs WHERE id = ?"
    try:
        cursor = connection.cursor()
        cursor.execute(delete_job_query, (job_id,))
        connection.commit()
        print(f"Job with ID {job_id} deleted successfully")
        return True
    except sqlite3.Error as e:
        print(f"Error deleting job with ID {job_id}: {e}")
        return False

def update_job_details(connection, job_id, title, price, description):
    update_job_query = "UPDATE jobs SET title=?, price=?, description=? WHERE id=?"
    try:
        cursor = connection.cursor()
        cursor.execute(update_job_query, (title, price, description, job_id))
        connection.commit()
        print(f"Job with ID {job_id} updated successfully")
        return True
    except sqlite3.Error as e:
        print(f"Error updating job with ID {job_id}: {e}")
        return False

def select_job_details(connection, job_id):
    select_job_query = "SELECT * FROM jobs WHERE id = ?"
    try:
        cursor = connection.cursor()
        cursor.execute(select_job_query, (job_id,))
        job_details = cursor.fetchone()
        return job_details
    except sqlite3.Error as e:
        print(f"Error selecting job details: {e}")
        return None

def select_jobs(connection, user_id):
    select_jobs_query = "SELECT * FROM jobs WHERE user_id = ?"
    try:
        cursor = connection.cursor()
        cursor.execute(select_jobs_query, (user_id,))
        jobs = cursor.fetchall()
        return jobs
    except sqlite3.Error as e:
        print(f"Error selecting jobs: {e}")
        return []

def list_all_jobs(connection):
    list_all_jobs_query = "SELECT * FROM jobs"
    try:
        cursor = connection.cursor()
        cursor.execute(list_all_jobs_query)
        jobs = cursor.fetchall()
        return jobs
    except sqlite3.Error as e:
        print(f"Error listing all jobs: {e}")
        return []

def get_user_balance(connection, user_id):
    select_balance_query = "SELECT balance FROM users WHERE id = ?"
    try:
        cursor = connection.cursor()
        cursor.execute(select_balance_query, (user_id,))
        balance = cursor.fetchone()
        return balance[0] if balance else 0  
    except sqlite3.Error as e:
        print(f"Error fetching balance: {e}")
        return 0  

def select_offers_for_job(connection, job_id, employee_id):
    select_offers_query = "SELECT * FROM offers WHERE job_id = ? AND employee_id = ?"
    try:
        cursor = connection.cursor()
        cursor.execute(select_offers_query, (job_id, employee_id))
        offers = cursor.fetchall()
        print(f"Offers for Job ID {job_id} and Employee ID {employee_id}: {offers}")  
        return offers
    except sqlite3.Error as e:
        print(f"Error selecting offers for job: {e}")
        return []

def list_offers_for_job(connection, job_id):
    list_offers_query = "SELECT * FROM offers WHERE job_id = ?"
    try:
        cursor = connection.cursor()
        cursor.execute(list_offers_query, (job_id,))
        offers = cursor.fetchall()
        return offers
    except sqlite3.Error as e:
        print(f"Error listing offers for job: {e}")
        return []

def accept_offer(connection, offer_id):
    try:
        cursor = connection.cursor()

        cursor.execute("SELECT job_id, employee_id, price FROM offers WHERE id=?", (offer_id,))
        result = cursor.fetchone()

        if result:
            job_id, employee_id, new_price = result

            cursor.execute("UPDATE jobs SET status='accepted', price=? WHERE id=?", (new_price, job_id))
            connection.commit()

            cursor.execute("UPDATE offers SET accepted=1 WHERE id=?", (offer_id,))
            connection.commit()

            print(f"Offer with ID {offer_id} accepted successfully")
            return True
        else:
            print(f"No offer found with ID {offer_id}")
            return False

    except sqlite3.Error as e:
        print(f"Error accepting offer for offer ID {offer_id}: {e}")
        return False


def update_user_balance(connection, user_id, new_balance):
    update_balance_query = "UPDATE users SET balance=? WHERE id=?"
    try:
        cursor = connection.cursor()
        cursor.execute(update_balance_query, (new_balance, user_id))
        connection.commit()
        print(f"Balance for User ID {user_id} updated successfully.")
        return True
    except sqlite3.Error as e:
        print(f"Error updating balance for User ID {user_id}: {e}")
        return False

def update_job_status(connection, job_id, new_status):
    update_status_query = "UPDATE jobs SET status=? WHERE id=?"
    try:
        cursor = connection.cursor()
        cursor.execute(update_status_query, (new_status, job_id))
        connection.commit()
        print(f"Status for Job ID {job_id} updated to {new_status} successfully.")
        return True
    except sqlite3.Error as e:
        print(f"Error updating status for Job ID {job_id}: {e}")
        return False

def create_tables():
    connection = create_db_connection()
    create_user_table(connection)
    create_jobs_table(connection)
    create_offers_table(connection)
