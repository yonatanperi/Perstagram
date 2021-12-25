import datetime
from typing import List

import mysql.connector
import pickle
import hashlib


class SQL:
    NAME_MAX_LENGTH = 50
    EMAIL_MAX_LENGTH = 100
    BIO_MAX_LENGTH = 500
    SHA256_LENGTH = 64
    POST_MAX_DATE_IN_STACK = datetime.timedelta(weeks=2)

    def __init__(self):
        """
        connects to the sql server and database.
        """
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="7324545",
            database="perstagram"  # assuming the database already exists
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
                    profile_photo MEDIUMBLOB,
                    bio VARCHAR({self.BIO_MAX_LENGTH}),
                    open BOOLEAN NOT NULL DEFAULT True)""")

        self.db.commit()
        self.register_admin()

    def register_admin(self):
        self.register("yonatan", "7324545", "yonatan", "peri", "yonatanperi333@gmail.com", user_type="admin")

    def register(self, username, password, first_name, last_name, email, open_user=True, search_object=None,
                 user_type="client"):
        """
        register a user into the database.
        updates the default schema and creates a special schema for the user.
        insert the username in the search_object
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
        self.cursor.execute("INSERT INTO users_profile (username, open) VALUES (%s, %s)",
                            (username, open_user))

        # create new schema for the new user

        self.cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {username}")
        self.cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {username}.posts (
                    id INT NOT NULL PRIMARY KEY,
                    date DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    byte_photo MEDIUMBLOB NOT NULL)""")

        self.cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {username}.comments (
                    comment_id INT NOT NULL PRIMARY KEY,
                    post_id INT NOT NULL,
                    FOREIGN KEY (post_id) REFERENCES {username}.posts(id) ON DELETE CASCADE,
                    username VARCHAR({self.NAME_MAX_LENGTH}) NOT NULL,
                    FOREIGN KEY (username) REFERENCES perstagram.users_info(username) ON DELETE CASCADE,
                    comment VARCHAR({self.BIO_MAX_LENGTH}))""")

        self.cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {username}.likes (
                            post_id INT NOT NULL,
                            FOREIGN KEY (post_id) REFERENCES {username}.posts(id) ON DELETE CASCADE,
                            username VARCHAR({self.NAME_MAX_LENGTH}) NOT NULL,
                            FOREIGN KEY (username) REFERENCES perstagram.users_info(username) ON DELETE CASCADE)""")

        self.cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {username}.stories (
                            id INT NOT NULL PRIMARY KEY,
                            date DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                            byte_photo MEDIUMBLOB NOT NULL)""")

        self.cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {username}.interest_users (
                                    username VARCHAR({self.NAME_MAX_LENGTH}) NOT NULL,
                                    FOREIGN KEY (username) REFERENCES perstagram.users_info(username) ON DELETE CASCADE,
                                    follows BOOLEAN,
                                    following BOOLEAN)""")
        # followers - people follows me
        # following - people I follow

        self.cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {username}.latest_posts_stack (
                                                username VARCHAR({self.NAME_MAX_LENGTH}) NOT NULL,
                                                FOREIGN KEY (username) REFERENCES perstagram.users_info(username) ON DELETE CASCADE,
                                                post_id INT NOT NULL,
                                                date DATETIME NOT NULL)""")
        if not open_user:
            self.cursor.execute(
                f"""CREATE TABLE IF NOT EXISTS {username}.follow_requests (
                                                            username VARCHAR({self.NAME_MAX_LENGTH}) NOT NULL,
                                                            FOREIGN KEY (username) REFERENCES perstagram.users_info(username) ON DELETE CASCADE""")

        self.db.commit()

        # insert to search object
        if search_object:
            search_object.insert_to_tree(username)

        return True

    def is_open_user(self, username: str) -> bool:
        """
        Check if the user is open or closed
        :param username:
        :return: boolean...
        """
        self.cursor.execute(f'select open from users_profile where username = %s',
                            (username,))
        return self.cursor.fetchall()[0][0] == 1

    def get_posts_from_stack(self, username, buffer):
        """
        When the homepage is starting, it presents the buffer amount of posts
        :param username: who uses
        :param buffer: of posts
        :return: the username and post id of each post
        """
        self.cursor.execute(f'SELECT username, post_id FROM {username}.latest_posts_stack ORDER BY date DESC LIMIT %s',
                            (buffer,))
        return self.cursor.fetchall()

    def delete_old_post_from_stack(self, username):
        """
        When the user don't open the app long time, the very old post gets deleted from the stack
        :param username: the user who didn't open the app long time
        """

        self.cursor.execute(
            f'DELETE FROM {username}.latest_posts_stack WHERE date < "{(datetime.datetime.now() - self.POST_MAX_DATE_IN_STACK).strftime("%Y-%m-%d")}"')

    def next_post_from_stack(self, username):
        """
        When the homepage is running, it loads posts.
        :param username: who uses
        :return: the username and post id of each post
        """
        self.cursor.execute(f'SELECT username, post_id FROM {username}.latest_posts_stack ORDER BY date DESC LIMIT 1')
        return self.cursor.fetchall()[0][0]

    def remove_from_latest_posts_stack(self, username, post_id):
        """
        When the user seen post, it gets deleted from the posts stack.
        :param username: who have seen the post
        :param post_id:
        """
        self.cursor.execute(
            f"REMOVE FROM {username}.latest_posts_stack WHERE username = %s AND post_id = %s",
            (username, post_id))

        self.db.commit()

    def update_latest_posts_stack(self, username_to_update, username_who_posted, post_id, post_date):
        self.cursor.execute(
            f"INSERT INTO {username_to_update}.latest_posts_stack (username, post_id, date) VALUES (%s, %s, %s)",
            (username_who_posted, post_id, post_date))

        self.db.commit()

    def get_followers(self, username):
        self.cursor.execute(f'SELECT username FROM {username}.interest_users WHERE follows = 1')
        return self.ugly_list_2_list(self.cursor.fetchall())

    def get_comments(self, username, post_id, client_username):
        """
        :return tuple of all the comments ((username, comment), ...)
        """
        if self.is_open_user(username) and client_username not in self.get_followers(username):
            self.cursor.execute(f'SELECT username, comment FROM {username}.comments WHERE post_id = %s', (post_id,))
            return self.cursor.fetchall()
        else:
            return "closed!"

    def get_likes(self, username, post_id, client_username):
        """
        :return tuple of all the username of the users who liked the post ((username), ...)
        """
        if self.is_open_user(username) and client_username not in self.get_followers(username):
            self.cursor.execute(f'SELECT username FROM {username}.likes WHERE post_id = %s', (post_id,))
            return self.cursor.fetchall()
        else:
            return "closed!"

    def get_date(self, username, post_id, client_username):
        """
        :return tuple of all the username of the users who liked the post ((username), ...)
        """
        if self.is_open_user(username) and client_username not in self.get_followers(username):
            self.cursor.execute(f'SELECT username FROM {username}.date WHERE post_id = %s', (post_id,))
            return self.cursor.fetchall()
        else:
            return "closed!"

    def get_photo(self, username, photo_id, table, client_username):
        """
        :param username: the username
        :param photo_id: id of the post or story
        :param table: posts or stories
        :param client_username: the client's username

        :return tuple of all the username of the users who liked the post ((username), ...)
        """
        if self.is_open_user(username) or client_username not in self.get_followers(username):
            self.cursor.execute(f'SELECT byte_photo FROM {username}.{table} WHERE id = %s', (photo_id,))
            return pickle.loads(self.cursor.fetchall()[0][0])
        else:
            return "closed!"

    def get_profile_photo(self, username):
        """
        :param username: the username
        :return PIL image object of the profile photo
        """
        self.cursor.execute("SELECT profile_photo FROM users_profile WHERE username = %s", (username,))
        profile_photo = self.cursor.fetchall()[0][0]
        if not profile_photo:  # the user has no profile photo
            # return the default profile photo of the admin: yonatan
            self.cursor.execute("SELECT profile_photo FROM users_profile WHERE username = %s", ("yonatan",))
            profile_photo = self.cursor.fetchall()[0][0]

        return pickle.loads(profile_photo)

    def get_bio(self, username):
        """
        :param username: the username
        :return the bio as text
        """
        self.cursor.execute("SELECT bio FROM users_profile WHERE username = %s", (username,))
        return self.cursor.fetchall()[0][0]

    def follow(self, follower: str, followed: str, check_for_open: bool = True):
        """
        insert the interest users and the stack on both users
        :param check_for_open: whether to check if the followed user is open
        :param follower: the one who ask to follow
        :param followed: the one who asked to be followed
        """
        # check if open
        if self.is_open_user(followed) or not check_for_open:
            # interest users
            fs_str = ("follows", "following")
            fs = (follower, followed)
            for i in range(2):
                self.cursor.execute(f"SELECT * FROM {fs[i]}.interest_users WHERE username = %s", (fs[1 - i],))
                if self.cursor.fetchall():  # it exists
                    self.cursor.execute(f"UPDATE {fs[i]}.interest_users SET {fs_str[i]} = TRUE")
                else:
                    self.cursor.execute(
                        f"INSERT INTO {fs[i]}.interest_users (username, follows, following) VALUES (%s, %s, %s)",
                        (fs[1 - i], i, 1 - i))

            # latest_posts_stack
            self.cursor.execute(
                f'SELECT id, date FROM {followed}.posts WHERE date > "{(datetime.datetime.now() - self.POST_MAX_DATE_IN_STACK).strftime("%Y-%m-%d")}"')
            posts_details = self.cursor.fetchall()

            for post_details in posts_details:
                self.cursor.execute(
                    f"INSERT INTO {follower}.latest_posts_stack (username, post_id, date) VALUES (%s, %s, %s)",
                    (followed, post_details[0], post_details[1]))

            self.db.commit()
        else:
            # add to requests
            self.cursor.execute(
                f"INSERT INTO {followed}.follow_requests (username) VALUES (%s)",
                (follower,))
            self.db.commit()

    def unfollow(self, follower: str, followed: str):
        """
        deletes from interest users and the stack on both users
        :param follower: the one who ask to unfollow
        :param followed: the one who is unfollowed
        """
        # interest users
        fs_str = ("follows", "following")
        fs = (follower, followed)
        for i in range(2):
            self.cursor.execute(f"UPDATE {fs[i]}.interest_users SET {fs_str[i]} = FALSE")

        # latest_posts_stack
        self.cursor.execute(
            f"DELETE FROM {follower}.latest_posts_stack WHERE username = %s", (followed,))

        self.db.commit()

    def get_interest_users(self, username):
        """
        :param username: the username
        :return tuple: ((username, follows?, following?), ...)
        """
        self.cursor.execute(f"SELECT * FROM {username}.interest_users")
        return self.cursor.fetchall()

    def get_user_photos_id(self, username, table):
        """
        :param username: the username
        :param table: posts or stories

        :return tuple of all the images ids.
        """
        self.cursor.execute(f'SELECT id FROM {username}.{table}')
        return self.cursor.fetchall()

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

    def get_all_usernames(self):
        """
        :return: all the usernames in the db
        """
        self.cursor.execute("SELECT username FROM users_info")
        return self.cursor.fetchall()

    def get_user_type(self, username):
        self.cursor.execute('SELECT user_type FROM users_authentication WHERE username = %s', (username,))
        return self.cursor.fetchall()[0][0]

    '''def execute_query(self, query, commit=False, get_results=False):
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
        return "Nothing returned!"'''

    def upload_image(self, username, image, table):
        """
        upload post and insert it to the db.
        :param username: the username
        :param image: PIL.Image object
        :param table: posts or stories

        :return: the post id
        """
        # updating the sql - username schema
        self.cursor.execute(f"SELECT max(id) from {username}.{table}")

        post_id = self.cursor.fetchall()[0][0]
        if post_id == None:  # first post!
            post_id = 0
        else:
            post_id += 1

        self.cursor.execute(f"INSERT INTO {username}.{table} (id, byte_photo) VALUES (%s, %s)",
                            (post_id, pickle.dumps(image)))
        self.db.commit()

        return post_id

    def set_profile_photo(self, username, image):
        """
        Set the image to profile photo.
        :param username: the username
        :param image: PIL.Image object
        """
        # updating the sql
        width, height = image.size

        if width > height:
            (left, upper, right, lower) = ((width - height) / 2, 0, (width + height) / 2, height)
        else:
            (left, upper, right, lower) = (0, (height - width) / 2, width, (height + width) / 2)

        # Here the image "im" is cropped and assigned to new variable im_crop
        image = image.crop((left, upper, right, lower))
        image = image.resize((100, 100))
        self.cursor.execute("UPDATE users_profile SET profile_photo = %s WHERE username = %s",
                            (pickle.dumps(image), username))
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
            if table[0] != "users_info":
                self.cursor.execute(f"DROP TABLE {table[0]}")
        self.cursor.execute(f"DROP TABLE users_info")

        self.db.commit()

        self.create_tables()

    @staticmethod
    def sha256(string):
        return hashlib.sha224(string.encode()).hexdigest()

    @staticmethod
    def ugly_list_2_list(ugly_list: List[tuple]):
        # [(a), (b), ...] -> [a, b, ...]
        return list(map(lambda t: t[0], ugly_list))

# SQL().reset_db()
