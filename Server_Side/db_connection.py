import datetime
from shutil import rmtree
from typing import List

import mysql.connector
import pickle
import hashlib
import os


class SQL:
    NAME_MAX_LENGTH = 50
    EMAIL_MAX_LENGTH = 100
    BIO_MAX_LENGTH = 500
    SHA256_LENGTH = 64
    POST_MAX_DATE_IN_STACK = datetime.timedelta(weeks=2)
    USER_MAX_TAGS = 4
    MAIN_TAGS_NUMBER = 10
    SUGGESTIONS_LIST_LENGTH = 4
    MAX_ACTIVITY_TAGS = 50
    MIN_SUGGESTIONS_MATCH = .3
    DIRECT_MESSAGE_MAX_LENGTH = 200

    def __init__(self, server=None):
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
        self.server = server

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
                    open BOOLEAN NOT NULL DEFAULT True,
                    main_tags MEDIUMBLOB)""")

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
                    byte_photo MEDIUMBLOB NOT NULL,
                    tags BLOB)""")

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
                            byte_photo MEDIUMBLOB NOT NULL,
                            tags BLOB)""")

        self.cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {username}.interest_users (
                                    username VARCHAR({self.NAME_MAX_LENGTH}) NOT NULL,
                                    FOREIGN KEY (username) REFERENCES perstagram.users_info(username) ON DELETE CASCADE,
                                    follows BOOLEAN,
                                    following BOOLEAN)""")

        self.cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {username}.seen_stories (
                                    username VARCHAR({self.NAME_MAX_LENGTH}) NOT NULL,
                                    id INT NOT NULL,
                                    date DATETIME NOT NULL)""")

        self.cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {username}.direct_messages (
                                            username VARCHAR({self.NAME_MAX_LENGTH}) NOT NULL,
                                            date DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                                            message VARCHAR({self.DIRECT_MESSAGE_MAX_LENGTH}) NOT NULL)""")

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
                                                            FOREIGN KEY (username) REFERENCES perstagram.users_info(username) ON DELETE CASCADE)""")

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
        self.cursor.execute(f'SELECT open FROM users_profile WHERE username = %s',
                            (username,))
        return self.cursor.fetchall()[0][0] == 1

    def get_direct_messages(self, client_username):
        """
        pops from the db the unseen messages.
        :param client_username: the chating user
        :return: tuple of: (username, date, the message)
        """
        self.cursor.execute(f'SELECT * FROM {client_username}.direct_messages')
        messages = self.cursor.fetchall()
        self.cursor.execute(f'DELETE FROM {client_username}.direct_messages')
        self.db.commit()

        return messages

    def get_specific_direct_messages(self, client_username, username):
        """
        pops from the db the unseen messages of a specific user.
        :param client_username: the chating user
        :param username: the specific user
        :return: tuple of: (username, date, the message)
        """
        self.cursor.execute(f'SELECT * FROM {client_username}.direct_messages WHERE username = %s', (username,))
        messages = self.cursor.fetchall()
        self.cursor.execute(f'DELETE FROM {client_username}.direct_messages WHERE username = %s', (username,))
        self.db.commit()

        return messages

    def insert_direct_message(self, sender, recver, message):
        """
        insert the message details in the recver schema

        :param sender: the user who sent the message
        :param recver: the user who recv the message
        :param message: the actual message
        """
        self.cursor.execute(
            f'INSERT INTO {recver}.direct_messages (username, message) VALUES (%s, %s)',
            (sender, message))
        self.db.commit()

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

    def next_post_from_stack(self, username, posts_buffer):
        """
        When the homepage is running, it loads posts.
        :param username: who uses
        :param posts_buffer: the loaded posts number buffer

        :return: the username and post id of each post
        """
        self.cursor.execute(f'SELECT username, post_id FROM {username}.latest_posts_stack ORDER BY date DESC')
        post = self.cursor.fetchall()
        if len(post) >= posts_buffer:
            return post[posts_buffer - 1]  # indexing starts from 0
        return

    def remove_from_latest_posts_stack(self, client_username, username, post_id):
        """
        When the user seen post, it gets deleted from the posts stack.
        :param client_username: who have seen the post
        :param username: who uploaded the post
        :param post_id: the post id
        """
        self.cursor.execute(
            f"DELETE FROM {client_username}.latest_posts_stack WHERE username = %s AND post_id = CAST(%s AS UNSIGNED)",
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

    def get_following(self, username):
        self.cursor.execute(f'SELECT username FROM {username}.interest_users WHERE following = 1')
        return self.ugly_list_2_list(self.cursor.fetchall())

    def get_comments(self, username, post_id, client_username):
        """
        :return tuple of all the comments ((username, comment), ...)
        """
        if self.is_open_user(username) or client_username in self.get_followers(username):
            self.cursor.execute(f'SELECT username, comment FROM {username}.comments WHERE post_id = %s', (post_id,))
            return self.cursor.fetchall()
        else:
            return "closed!"

    def get_likes(self, username, post_id, client_username):
        """
        :return tuple of all the username of the users who liked the post (username, ...)
        """
        if self.is_open_user(username) or client_username in self.get_followers(username):
            self.cursor.execute(f'SELECT username FROM {username}.likes WHERE post_id = %s', (post_id,))
            return self.ugly_list_2_list(self.cursor.fetchall())
        else:
            return "closed!"

    def get_tags(self, username, post_id):
        """
        :return tuple of tags
        """
        self.cursor.execute(f'SELECT tags FROM {username}.posts WHERE id = %s', (post_id,))
        return pickle.loads(self.cursor.fetchall()[0][0])

    def get_date(self, username, photo_id, client_username, table):
        if self.is_open_user(username) or client_username in self.get_followers(username):
            self.cursor.execute(f'SELECT date FROM {username}.{table} WHERE id = %s', (photo_id,))
            return self.cursor.fetchall()[0][0]
        else:
            return "closed!"

    def get_photo(self, username, photo_id, table, client_username):
        """
        :param username: the username
        :param photo_id: id of the post or story
        :param table: posts or stories
        :param client_username: the client's username

        :return the photo
        """
        if self.is_open_user(username) or client_username in self.get_followers(username):
            # remove old stories
            if table == "stories":
                self.remove_old_stories(username)

            self.cursor.execute(f'SELECT byte_photo FROM {username}.{table} WHERE id = %s', (photo_id,))
            return pickle.loads(self.cursor.fetchall()[0][0])
        else:
            return "closed!"

    def remove_old_stories(self, username):
        self.cursor.execute(f'DELETE FROM {username}.stories WHERE date < %s',
                            (datetime.datetime.now() - datetime.timedelta(days=1),))

        self.db.commit()

    def get_seen_stories(self, client_username):
        """
        For the user to not see stories again.
        :param client_username:
        :return: tuple of tuples of the username and id
        """
        self.cursor.execute(f'SELECT username, id FROM {client_username}.seen_stories')
        return self.cursor.fetchall()

    def get_follow_requests(self, client_username):
        """
        TO admit them in the future (or not..)
        :param client_username:
        :return: ugly tuple of usernames (on purpose)
        """
        self.cursor.execute(f'SELECT username FROM {client_username}.follow_requests')
        return self.cursor.fetchall()

    def admit(self, client_username, username):
        """
        Admit the user after the follow request.
        :param client_username: the admitting one
        :param username: the admitted one.
        """
        self.cursor.execute(f'DELETE FROM {client_username}.follow_requests WHERE username = %s', (username,))
        self.follow(username, client_username, check_for_open=False)
        self.insert_direct_message(client_username, username, "This user has just admitted your follow request!")

    def seen_story(self, client_username, *args):
        """
        registers the activity in the seen stories' table of the user
        :param client_username:
        :param args: username and story id
        """
        # remove old ones
        self.cursor.execute(
            f'DELETE FROM {client_username}.seen_stories WHERE date  < %s',
            (datetime.datetime.now() - datetime.timedelta(days=1),))

        # insert
        self.cursor.execute(
            f'INSERT INTO {client_username}.seen_stories (username, id, date) VALUES (%s, %s, %s)',
            (*args, self.get_date(*args, client_username, "stories")))
        self.db.commit()

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

    def like(self, client_username, username, post_id):
        """
        likes a post and saves the activity tags.
        :param client_username: the user who liked the post
        :param username: the owner of the post
        :param post_id: the post id
        """
        self.cursor.execute(f"INSERT INTO {username}.likes (username, post_id) VALUES (%s, %s)",
                            (client_username, post_id))

        # update the activity file system
        post_tags = self.get_tags(username, post_id)
        f_write = open(f"activity/{client_username}.txt", "a")
        f_read = open(f"activity/{client_username}.txt", "r")
        activity_tags = f_read.read().splitlines()
        f_read.close()

        line_number = len(activity_tags)
        for tag in post_tags:
            if line_number > self.MAX_ACTIVITY_TAGS:
                activity_tags[0] = tag

                open(f'activity/{client_username}.txt', 'w').close()  # reset the file

                for line in activity_tags:
                    f_write.write(line)

            else:
                f_write.write(f"{tag}\n")
            line_number += 1

        f_write.close()

    def dislike(self, client_username, username, post_id):
        """
        dislikes a post.
        :param client_username: the user who disliked the post
        :param username: the owner of the post
        :param post_id: the post id
        """
        self.cursor.execute(f"DELETE FROM {username}.likes WHERE username = %s AND post_id = %s",
                            (client_username, post_id))

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
        :return tuple: ((username, followers, following), ...)
        """
        self.cursor.execute(f"SELECT * FROM {username}.interest_users")
        return self.cursor.fetchall()

    def get_user_photos_id(self, username, table):
        """
        :param username: the username
        :param table: posts or stories

        :return tuple of all the images ids.
        """
        # remove old stories
        if table == "stories":
            self.remove_old_stories(username)

        self.cursor.execute(f'SELECT id FROM {username}.{table} ORDER BY date DESC')
        return self.ugly_list_2_list(self.cursor.fetchall())

    def get_user_tags(self, username):
        """
        :param username: the username

        :return tuple of the tags.
        """
        self.cursor.execute(f'SELECT main_tags FROM users_profile WHERE username = %s', (username,))
        dump_tags = self.cursor.fetchall()[0][0]
        if dump_tags:
            return pickle.loads(dump_tags)
        return []

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
        return self.ugly_list_2_list(self.cursor.fetchall())

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

        # update the user's schema
        self.cursor.execute(f"INSERT INTO {username}.{table} (id, byte_photo, tags) VALUES (%s, %s, %s)",
                            (post_id, pickle.dumps(image), pickle.dumps(self.server.classify_image(image))))
        self.db.commit()

        # update the main schema
        self.cursor.execute(f"UPDATE users_profile SET main_tags = %s WHERE username = %s",
                            (pickle.dumps(self.analyze_user(username)), username))

        self.db.commit()

        return post_id

    def analyze_user(self, username) -> List:
        """
        Set the main tags of the user in the sql.
        """

        # set tags_list
        tags_list = []
        for post_id in self.get_user_photos_id(username, "posts"):
            tags_list += self.get_tags(username, post_id)

        return self.get_main_tags(tags_list, self.USER_MAX_TAGS)

    @staticmethod
    def get_main_tags(tags, buffer) -> List:
        # set the main tags
        main_tags = []
        for i in range(buffer):
            if tags:
                current_tag = max(set(tags), key=tags.count)
                main_tags.append(current_tag)
                tags.remove(current_tag)  # remove one instance

        return main_tags

    def get_suggestions(self, username) -> List[str]:
        """
        finds the most matching users based on their activity
        :param username: user to match.

        :return: list of all the matching usernames
        """
        try:
            with open(f"activity/{username}.txt", "r") as f:
                activity_tags = f.read().splitlines()

        except FileNotFoundError:  # no recorded activity
            return []

        if not activity_tags:
            return []

        # sort to main tags
        activity_main_tags = self.get_main_tags(activity_tags, buffer=self.MAIN_TAGS_NUMBER)

        # get all potential users to match
        potential_users = [item for item in list(self.get_all_usernames()) if
                           item not in list(self.get_following(username))]
        potential_users.remove(username)

        suggestions = []
        for i in range(self.SUGGESTIONS_LIST_LENGTH):
            if not potential_users:
                break
            # get the best user
            best_user = ("", 0)  # username, matching percentage
            for current_username in potential_users:
                current_tags = self.get_user_tags(current_username)
                current_match = self.match_tags(activity_main_tags, current_tags)

                if current_match >= best_user[1] and current_match > self.MIN_SUGGESTIONS_MATCH:
                    best_user = (current_username, current_match)

            if best_user[0] != "":  # if it exists
                suggestions.append(best_user[0])
                potential_users.remove(best_user[0])

        return suggestions

    @staticmethod
    def match_tags(tags1, tags2):
        """
        matches tags1 to tags2

        :return: the matching rate in range: [0, 1]
        """

        matching_points = 0
        for i in tags1:
            matching_points += 1 if i in tags2 else 0

        return matching_points / len(tags1)

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

        rmtree("activity")
        os.mkdir("activity")

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

    def replace_password(self, users_email: str, password: str):
        self.cursor.execute(f"SELECT username FROM users_info WHERE email = %s", (users_email,))
        username = self.cursor.fetchall()[0][0]
        self.cursor.execute(f"UPDATE users_authentication SET password = %s WHERE username = %s",
                            (self.sha256(password), username))

        self.db.commit()

    @staticmethod
    def sha256(string):
        return hashlib.sha224(string.encode()).hexdigest()

    @staticmethod
    def ugly_list_2_list(ugly_list: List[tuple]):
        # [(a), (b), ...] -> [a, b, ...]
        return list(map(lambda t: t[0], ugly_list))

# SQL().reset_db()
