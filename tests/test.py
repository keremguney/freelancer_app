import unittest
import sqlite3
from database import insert_job, insert_user, delete_job

class TestInsertJobFunction(unittest.TestCase):
    def setUp(self):
        self.connection = sqlite3.connect(':memory:')
        self.create_user_table()
        self.create_job_table()

    def create_user_table(self):
        create_user_table_query = """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                usertype TEXT NOT NULL,
                balance INTEGER NOT NULL
            )
        """
        cursor = self.connection.cursor()
        cursor.execute(create_user_table_query)
        self.connection.commit()

    def create_job_table(self):
        create_job_table_query = """
            CREATE TABLE jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                price INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """
        cursor = self.connection.cursor()
        cursor.execute(create_job_table_query)
        self.connection.commit()

    def test_insert_job_success(self):
        user_id = self.insert_user_for_testing()

        title = "Test Job"
        description = "This is a test job"
        price = 100

        result = insert_job(self.connection, title, description, price, user_id)

        self.assertTrue(result)

        cursor = self.connection.cursor()
        select_job_query = "SELECT * FROM jobs WHERE title = ?"
        cursor.execute(select_job_query, (title,))
        job = cursor.fetchone()

        self.assertIsNotNone(job)
        self.assertEqual(job[1], title)
        self.assertEqual(job[2], description)
        self.assertEqual(job[3], price)
        self.assertEqual(job[4], user_id)

    def test_insert_user_success(self):
        username = "testuser"
        password = "testpassword"
        usertype = "employee"

        result = insert_user(self.connection, username, password, usertype)

        self.assertTrue(result)

        cursor = self.connection.cursor()
        select_user_query = "SELECT * FROM users WHERE username = ?"
        cursor.execute(select_user_query, (username,))
        user = cursor.fetchone()

        self.assertIsNotNone(user)
        self.assertEqual(user[1], username)
        self.assertEqual(user[2], password)
        self.assertEqual(user[3], usertype)
        self.assertEqual(user[4], 500)

    def test_delete_job_success(self):
        user_id = self.insert_user_for_testing()
        job_id = self.insert_job_for_testing(user_id)

        result = delete_job(self.connection, job_id)

        self.assertTrue(result)

        cursor = self.connection.cursor()
        select_job_query = "SELECT * FROM jobs WHERE id = ?"
        cursor.execute(select_job_query, (job_id,))
        job = cursor.fetchone()

        self.assertIsNone(job, f"Job with ID {job_id} still exists in the database")


    def insert_user_for_testing(self):
        username = "testuser"
        password = "testpassword"
        usertype = "employee"

        insert_user(self.connection, username, password, usertype)

        cursor = self.connection.cursor()
        select_user_query = "SELECT id FROM users WHERE username = ?"
        cursor.execute(select_user_query, (username,))
        user_id = cursor.fetchone()[0]

        return user_id

    def insert_job_for_testing(self, user_id):
        title = "Test Job"
        description = "This is a test job"
        price = 100

        insert_job(self.connection, title, description, price, user_id)

        cursor = self.connection.cursor()
        select_job_query = "SELECT id FROM jobs WHERE title = ?"
        cursor.execute(select_job_query, (title,))
        job_id = cursor.fetchone()[0]

        return job_id


    def tearDown(self):
        self.connection.close()

if __name__ == '__main__':
    unittest.main()
