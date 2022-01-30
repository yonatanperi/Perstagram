from datetime import datetime
from db_connection import SQL


class HandleUser:
    """
    After login, the user will send a lot of requests.
    This listener will handle them!
    """

    DEFAULT_SEARCH_BUFFER = 10

    def __init__(self, client, server, LoRe):
        self.client = client
        self.sql = SQL(server)
        self.server = server
        self.LoRe = LoRe

    def handle(self):
        recved = self.client.recv_message()  # structure: ["request", *args]

        # TODO put all the commands in lambda dict

        if recved[0] == "post":

            post_date = datetime.now()

            # update the user's sql
            post_id = self.sql.upload_image(self.client.username, recved[1], "posts")

            # update all the others
            followers = self.sql.get_followers(self.client.username)
            for followed_user in followers:
                self.sql.update_latest_posts_stack(self.client.username, followed_user, post_id, post_date)

        elif recved[0] == "post2story":

            self.sql.upload_image(self.client.username, recved[1], "stories", close_friends=recved[2])

        elif recved[0] == "add to close friends":  # , username
            self.sql.add_to_close_friends(self.client.username, recved[1])

        elif recved[0] == "get close friends":
            self.client.send_message(self.sql.get_close_friends(self.client.username))

        elif recved[0] == "set profile photo":
            self.sql.set_profile_photo(self.client.username, recved[1])

        elif recved[0] == "get username":
            self.client.send_message(self.client.username)

        elif recved[0] == "is open":  # ,  username
            self.client.send_message(self.sql.is_open_user(recved[1]))

        elif recved[0] == "get profile photo":
            self.client.send_message(self.sql.get_profile_photo(recved[1]))

        elif recved[0] == "get bio":
            self.client.send_message(self.sql.get_bio(recved[1]))

        elif recved[0] == "get interest users":
            followers = []
            following = []
            for interest_user in self.sql.get_interest_users(recved[1]):
                if interest_user[1]:  # follows
                    followers.append(interest_user[0])
                if interest_user[2]:  # following
                    following.append(interest_user[0])
            self.client.send_message({"followers": followers, "following": following})

        elif recved[0] == "get suggestions":
            self.client.send_message(self.sql.get_suggestions(self.client.username))

        elif recved[0] == "get post":
            # send a dict: {image:, comments:, likes:}
            image = self.sql.get_photo(*recved[1:], "posts", self.client.username)
            comments = self.sql.get_comments(*recved[1:], self.client.username)
            likes = self.sql.get_likes(*recved[1:], self.client.username)
            self.client.send_message({"image": image, "comments": comments, "likes": likes})

        elif recved[0] == "get all posts":
            # send all posts ids
            self.client.send_message(self.sql.get_user_photos_id(recved[1], "posts"))

        elif recved[0] == "get stories":  # , username
            # sends the id's
            self.client.send_message(
                self.sql.get_user_photos_id(recved[1], "stories", client_username=self.client.username))

        elif recved[0] == "get story":  # , username, id
            self.client.send_message(self.sql.get_photo(*recved[1:], "stories", self.client.username))

        elif recved[0] == "get seen stories":
            self.client.send_message(self.sql.get_seen_stories(self.client.username))

        elif recved[0] == "get follow requests":
            self.client.send_message(self.sql.get_follow_requests(self.client.username))

        elif recved[0] == "admit":  # , username
            self.sql.admit(self.client.username, recved[1])  # admit the user

        elif recved[0] == "seen story":  # , username, id
            self.sql.seen_story(self.client.username, *recved[1:])

        elif recved[0] == "search":
            # search and send back the results
            if recved[1]:
                results = self.server.search_object.get_results(recved[1], self.DEFAULT_SEARCH_BUFFER)
                try:
                    results.remove(self.client.username)
                except ValueError:  # not in results
                    pass
                self.client.send_message(results)
            else:
                self.client.send_message([])

        elif recved[0] == "change profile":  # , **kwargs
            self.sql.change_profile(self.client.username, **recved[1])

        elif recved[0] == "seen post":  # , username, post_id
            self.sql.remove_from_latest_posts_stack(self.client.username, *recved[1:])

        elif recved[0] == "get next post":  # , posts buffer
            # send username, post ids
            self.client.send_message(self.sql.next_post_from_stack(self.client.username, recved[1]))

        elif recved[0] == "follow":
            self.sql.follow(self.client.username, recved[1])

        elif recved[0] == "unfollow":
            self.sql.unfollow(self.client.username, recved[1])

        elif recved[0] == "get direct messages":
            # only the unseen ones.
            temp_sql = SQL(self.server)  # Sometimes there is a problem in the sql connection at this point
            self.client.send_message(temp_sql.get_direct_messages(self.client.username))
            temp_sql.db.close()

        elif recved[0] == "get specific direct messages":  # , username
            # only the unseen ones.
            self.client.send_message(self.sql.get_specific_direct_messages(self.client.username, recved[1]))

        elif recved[0] == "send direct message":  # , username, message
            self.sql.insert_direct_message(self.client.username, *recved[1:])

        elif recved[0] in ("like", "dislike"):  # , username,  post_id
            {"like": self.sql.like,
             "dislike": self.sql.dislike}[recved[0]](self.client.username, *recved[1:])

        elif recved[0] == "done":
            # for the thread in the chat to know that's it.
            self.client.send_message("done")

        elif recved[0] == "logout":
            return self.LoRe(self.client, self.server).authenticate_client()

        else:
            self.client.send_message("unknown command.")

        self.handle()
