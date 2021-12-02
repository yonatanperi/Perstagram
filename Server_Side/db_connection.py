import mysql.connector
import pickle
import hashlib


class SQL:
    NAME_MAX_LENGTH = 50
    EMAIL_MAX_LENGTH = 100
    BIO_MAX_LENGTH = 500
    SHA256_LENGTH = 64

    def __init__(self):
        """
        connects to the sql server and database.
        """
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="7324545",
            database="perstagram"  # assuming the data base already exists
        )

        self.cursor = self.db.cursor()

    def create_db(self):
        """
        TODO before running with database connection
        """
        self.cursor.execute("CREATE DATABASE IF NOT EXISTS perstagram")
        self.db.commit()

    def create_tables(self):
        """
        initializing and create essential tables.
        registers the admin user.
        """
        self.cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS users_info (
                    username VARCHAR({self.NAME_MAX_LENGTH}) NOT NULL PRIMARY KEY,
                    first_name VARCHAR({self.NAME_MAX_LENGTH}) NOT NULL,
                    last_name VARCHAR({self.NAME_MAX_LENGTH}) NOT NULL,
                    email VARCHAR({self.EMAIL_MAX_LENGTH}) NOT NULL)""")

        self.cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS users_authentication (
                    username VARCHAR({self.NAME_MAX_LENGTH}) NOT NULL,
                    FOREIGN KEY (username) REFERENCES users_info(username) ON DELETE CASCADE,
                    password VARCHAR({self.SHA256_LENGTH}) NOT NULL,
                    user_type VARCHAR(20) NOT NULL)""")

        self.cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS users_profile (
                    username VARCHAR({self.NAME_MAX_LENGTH}) NOT NULL,
                    FOREIGN KEY (username) REFERENCES users_info(username) ON DELETE CASCADE,
                    bio VARCHAR({self.BIO_MAX_LENGTH}),
                    last_post_date DATETIME,
                    last_story_date DATETIME)""")

        self.db.commit()
        self.register_admin()

    def register_admin(self):
        self.register("yonatan", "7324545", "yonatan", "peri", "yonatanperi333@gmail.com", "admin")

    def register(self, username, password, first_name, last_name, email, user_type="client"):
        """
        register a user into the database.
        updates the default schema and creates a special schema for the user.
        :return:
                True - the registration proses was successful
                False - the registration proses wasn't successful - something went wrong.
        """

        # pre-checks to username and password
        if not username.isalnum():  # has no special characters
            return False

        # the username and password are hashed.
        password = self.sha256(password)

        # check there isn't already a user with that username or the user entered to long values
        self.cursor.execute("SELECT * FROM users_authentication WHERE username = %s", (username,))
        if self.cursor.fetchall():
            return False

        # updating the sql - default schema
        self.cursor.execute("INSERT INTO users_info (username, first_name, last_name, email) VALUES (%s, %s, %s, %s)",
                            (username, first_name, last_name, email))
        self.cursor.execute("INSERT INTO users_authentication (username, password, user_type) VALUES (%s, %s, %s)",
                            (username, password, user_type))
        self.cursor.execute("INSERT INTO users_profile (username) VALUES (%s)",
                            (username,))

        # create new schema for the new user

        self.cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {username}")
        self.cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {username}.posts (
                    post_id INT NOT NULL PRIMARY KEY,
                    date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    byte_photo BLOB NOT NULL)""")

        self.cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {username}.comments (
                    comment_id INT NOT NULL PRIMARY KEY,
                    post_id INT NOT NULL,
                    FOREIGN KEY (post_id) REFERENCES {username}.posts(post_id) ON DELETE CASCADE,
                    username VARCHAR({self.NAME_MAX_LENGTH}) NOT NULL,
                    FOREIGN KEY (username) REFERENCES perstagram.users_info(username) ON DELETE CASCADE,
                    comment VARCHAR({self.BIO_MAX_LENGTH}))""")

        self.cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {username}.likes (
                            post_id INT NOT NULL,
                            FOREIGN KEY (post_id) REFERENCES {username}.posts(post_id) ON DELETE CASCADE,
                            username VARCHAR({self.NAME_MAX_LENGTH}) NOT NULL,
                            FOREIGN KEY (username) REFERENCES perstagram.users_info(username) ON DELETE CASCADE)""")

        self.cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {username}.stories (
                            story_id INT NOT NULL PRIMARY KEY,
                            date DATETIME DEFAULT CURRENT_TIMESTAMP,
                            byte_photo BLOB NOT NULL)""")

        self.cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {username}.interest_users (
                                    username VARCHAR({self.NAME_MAX_LENGTH}) NOT NULL,
                                    FOREIGN KEY (username) REFERENCES perstagram.users_info(username) ON DELETE CASCADE,
                                    follows BOOLEAN,
                                    following BOOLEAN)""")

        self.db.commit()

        return True

    def login(self, username, password):
        """
        authenticates the user.
        :return:
                True - authenticated!
                False - username and password doesn't match.
        """
        self.cursor.execute("SELECT * FROM users_authentication WHERE username = %s AND password = %s",
                            (username, self.sha256(password)))
        if self.cursor.fetchall():
            return True
        return False

    def get_user_type(self, username):
        self.cursor.execute('SELECT user_type FROM users_authentication WHERE username = %s', (username,))
        return self.cursor.fetchall()[0][0]

    def execute_query(self, query, commit=False, get_results=False):
        """
        execute query in the sql database
        :param query: the string query
        :param commit: commit the sql?
        :param get_results: return the results?
        """
        self.cursor.execute(query)
        if commit:
            self.db.commit()
        if get_results:
            return self.cursor.fetchall()
        return "Nothing returned!"

    def upload_post(self, username, image):
        """
        upload post and insert it to the db.
        :param username: the username
        :param image: PIL.Image object
        """
        # updating the sql - username schema
        self.cursor.execute("SELECT post_id FROM %s.posts", (username,))
        post_id = len(self.cursor.fetchall())
        self.cursor.execute("INSERT INTO %s.posts (post_id, byte_photo) VALUES (%s, %s)",
                            (username, post_id, pickle.dumps(image)))
        self.db.commit()

    def reset_db(self):
        """
        delete all data from the default schema's tables,
        delete all user schemas.
        """

        self.cursor.execute("SELECT username from users_info")
        for schema in self.cursor.fetchall():
            self.cursor.execute(f"DROP SCHEMA IF EXISTS {schema[0]}")

        self.cursor.execute("SHOW TABLES")
        for table in self.cursor.fetchall():
            self.cursor.execute(f"DELETE FROM {table[0]}")

        self.db.commit()

        self.register_admin()
    
    @staticmethod
    def sha256(string):
        return hashlib.sha224(string.encode()).hexdigest()


s = SQL()
s.reset_db()
