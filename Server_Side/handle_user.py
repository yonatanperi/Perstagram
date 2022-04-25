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

        self.handle_command_dict = self.get_handle_command_dict()

    def post(self, recved):
        post_date = datetime.now()

        # update the user's sql
        post_id = self.sql.upload_image(self.client.username, recved[1], "posts")

        # update all the others
        followers = self.sql.get_followers(self.client.username)
        for follower in followers:
            self.sql.update_latest_posts_stack(follower, self.client.username, post_id, post_date)

    def get_interest_users(self, recved):
        followers = []
        following = []
        for interest_user in self.sql.get_interest_users(recved[1]):
            if interest_user[1]:  # follows
                followers.append(interest_user[0])
            if interest_user[2]:  # following
                following.append(interest_user[0])
        self.client.send_message({"followers": followers, "following": following})

    def get_post(self, recved):
        # send a dict: {image:, comments:, likes:}
        image = self.sql.get_photo(*recved[1:], "posts", self.client.username)
        comments = self.sql.get_comments(*recved[1:], self.client.username)
        likes = self.sql.get_likes(*recved[1:], self.client.username)
        self.client.send_message({"image": image, "comments": comments, "likes": likes})

    def search(self, recved):
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

    def get_direct_messages(self, recved):
        # only the unseen ones.
        temp_sql = SQL(self.server)  # Sometimes there is a problem in the sql connection at this point
        self.client.send_message(temp_sql.get_direct_messages(self.client.username))
        temp_sql.db.close()

    def get_handle_command_dict(self):
        return {
            "post": self.post,
            "post2story": lambda recved: self.sql.upload_image(self.client.username, recved[1], "stories",
                                                               close_friends=recved[2]),
            "add to close friends": lambda recved: self.sql.add_to_close_friends(self.client.username, recved[1]),
            # , username
            "get close friends": lambda recved: self.client.send_message(
                self.sql.get_close_friends(self.client.username)),
            "set profile photo": lambda recved: self.sql.set_profile_photo(self.client.username, recved[1]),
            "get username": lambda recved: self.client.send_message(self.client.username),
            "is open": lambda recved: self.client.send_message(self.sql.is_open_user(recved[1])),  # , username
            "get profile photo": lambda recved: self.client.send_message(self.sql.get_profile_photo(recved[1])),
            "get bio": lambda recved: self.client.send_message(self.sql.get_bio(recved[1])),  # , username
            "get interest users": self.get_interest_users,  # , username
            "get suggestions": lambda recved: self.client.send_message(self.sql.get_suggestions(self.client.username)),
            "get post": self.get_post,  # , username, post_id
            "get all posts": lambda recved: self.client.send_message(self.sql.get_user_photos_id(recved[1], "posts")),
            # username
            "get stories": lambda recved: self.client.send_message(
                self.sql.get_user_photos_id(recved[1], "stories", client_username=self.client.username)),  # , username
            "get story": lambda recved: self.client.send_message(
                self.sql.get_photo(*recved[1:], "stories", self.client.username)),  # , username, id
            "get seen stories": lambda recved: self.client.send_message(
                self.sql.get_seen_stories(self.client.username)),
            "get follow requests": lambda recved: self.client.send_message(
                self.sql.get_follow_requests(self.client.username)),
            "admit": lambda recved: self.sql.admit(self.client.username, recved[1]),  # , username
            "seen story": lambda recved: self.sql.seen_story(self.client.username, *recved[1:]),  # , username, id
            "search": self.search,
            "change profile": lambda recved: self.sql.change_profile(self.client.username, **recved[1]),  # , **kwargs
            "seen post": lambda recved: self.sql.remove_from_latest_posts_stack(self.client.username, *recved[1:]),
            # , username, post_id
            "get next post": lambda recved: self.client.send_message(
                self.sql.next_post_from_stack(self.client.username, recved[1])),  # , posts buffer
            "follow": lambda recved: self.sql.follow(self.client.username, recved[1]),
            "unfollow": lambda recved: self.sql.unfollow(self.client.username, recved[1]),
            "get direct messages": self.get_direct_messages,
            "get specific direct messages": lambda recved: self.client.send_message(
                self.sql.get_specific_direct_messages(self.client.username, recved[1])),  # , username
            "send direct message": lambda recved: self.sql.insert_direct_message(self.client.username, *recved[1:]),
            # , username, message
            "like": lambda recved: self.sql.like(self.client.username, *recved[1:]),  # , username,  post_id
            "dislike": lambda recved: self.sql.dislike(self.client.username, *recved[1:]),  # , username,  post_id
            "comment": lambda recved: self.sql.comment(self.client.username, *recved[1:]),
            # , username, post_id, comment
            "done": lambda recved: self.client.send_message("done"),  # for the thread in the chat to know that's it.
            "logout": lambda recved: self.LoRe(self.client, self.server).authenticate_client()
        }

    def handle(self):
        recved = self.client.recv_message()  # structure: ["request", *args]

        if recved[0] in self.handle_command_dict:
            self.handle_command_dict[recved[0]](recved)
        else:
            self.client.send_message("unknown command.")

        self.handle()
