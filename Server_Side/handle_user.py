from datetime import datetime
from db_connection import SQL


class HandleUser:
    """
    After login, the user will send a lot of requests.
    This listener will handle them!
    """

    DEFAULT_SEARCH_BUFFER = 10

    def __init__(self, client, search_object):
        self.client = client
        self.sql = SQL()
        self.search_object = search_object

    def handle(self):
        recved = self.client.recv_message()  # structure: ["request", *args]

        if recved[0] == "post":

            post_date = datetime.now()

            # update the user's sql
            post_id = self.sql.upload_image(self.client.username, recved[1], "posts")

            # update all the others
            followers = self.sql.get_followers(self.client.username)
            for followed_user in followers:
                self.sql.update_latest_posts_stack(self.client.username, followed_user, post_id, post_date)

        elif recved[0] == "post2story":
            self.sql.upload_image(self.client.username, recved[1], "stories")

        elif recved[0] == "set profile photo":
            self.sql.set_profile_photo(self.client.username, recved[1])

        elif recved[0] == "get username":
            self.client.send_message(self.client.username)

        elif recved[0] == "get profile photo":
            self.client.send_message(self.sql.get_profile_photo(recved[1]))

        elif recved[0] == "get bio":
            self.client.send_message(self.sql.get_bio(recved[1]))

        elif recved[0] == "get interest users":
            follows = []
            following = []
            for interest_user in self.sql.get_interest_users(recved[1]):
                if interest_user[1]:  # follows
                    follows.append(interest_user[0])
                if interest_user[2]:  # following
                    following.append(interest_user[0])
            self.client.send_message({"follows": follows, "following": following})

        elif recved[0] == "get post":
            # send a dict: {image:, comments:, likes:}
            image = self.sql.get_photo(recved[1], recved[2], "posts", self.client.username)
            comments = self.sql.get_comments(recved[1], recved[2], self.client.username)
            likes = self.sql.get_likes(recved[1], recved[2], self.client.username)
            self.client.send_message({"image": image, "comments": comments, "likes": likes})

        elif recved[0] == "get all posts":
            # send all posts ids
            self.client.send_message(self.sql.get_user_photos_id(recved[1], "posts"))

        elif recved[0] == "search":
            # search and send back the results
            if recved[1]:
                self.client.send_message(
                    self.search_object.get_results(recved[1], self.DEFAULT_SEARCH_BUFFER)
                )
            else:
                self.client.send_message([])

        elif recved[0] == "seen post":  # , username, post_id
            self.sql.remove_from_latest_posts_stack(recved[1], recved[2])

        elif recved[0] == "get home page posts":  # , buffer
            # delete old posts from stack
            self.sql.delete_old_post_from_stack(self.client.username)

            # send posts ids
            self.client.send_message(self.sql.get_posts_from_stack(self.client.username, recved[1]))

        elif recved[0] == "get next post":
            # send post ids
            self.client.send_message(self.sql.next_post_from_stack(self.client.username))

        elif recved[0] == "follow":
            self.sql.follow(self.client.username, recved[1])

        elif recved[0] == "unfollow":
            self.sql.unfollow(self.client.username, recved[1])

        self.handle()
