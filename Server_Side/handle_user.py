from db_connection import SQL
from search import Search


class HandleUser:
    """
    After login, the user will send a lot of requests.
    This listener will handle them!
    """

    def __init__(self, client):
        self.client = client
        self.sql = SQL()

    def handle(self):
        recved = self.client.recv_message()  # structure: ["request", *args]

        if recved[0] == "post":
            self.sql.upload_image(self.client.username, recved[1], "posts")

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
            image = self.sql.get_photo(recved[1], recved[2], "posts")
            comments = self.sql.get_comments(recved[1], recved[2])
            likes = self.sql.get_likes(recved[1], recved[2])
            self.client.send_message({"image": image, "comments": comments, "likes": likes})

        elif recved[0] == "get all posts":
            # send all posts ids
            self.client.send_message(self.sql.get_user_photos_id(recved[1], "posts"))

        self.handle()
