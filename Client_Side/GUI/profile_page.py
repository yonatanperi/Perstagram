import time
from typing import Dict, Union, Callable, Any, Tuple, Type

from .smart_scroll_form import SmartScrollForm
from .tiny_user import TinyUser
from tkinter import *
from tkinter.ttk import *
from PIL import ImageTk
from .post_object import Post


class ProfilePage(SmartScrollForm):

    def __init__(self, client, username=None):

        if not username:  # set default username
            self.username = client.get_answer(("get username",))
            self.default_user = True  # The client is in his own profile page
        else:
            self.username = username
            self.default_user = False

        self.posts_ids = client.get_answer(("get all posts", self.username))
        self.add_username(self.posts_ids)

        super().__init__(client, 1, iter(self.posts_ids),
                         lambda username, post_id: Post(self.client, username, post_id,
                                                        self.scroll_frame).post_frame.pack(pady=10))

        # About bar
        about_frame = Frame(self.scroll_frame)
        about_frame.pack(pady=10)

        # tiny user
        TinyUser(self.client, self.username, about_frame, True).tiny_user_frame.grid(row=0, column=0, padx=10, pady=10)

        # All the user's posts
        Label(about_frame, text=f"{len(self.posts_ids)}\nPosts").grid(row=0, column=1, padx=10)  # posts number

        # interest users
        self.interest_users = self.client.get_answer(("get interest users", self.username))
        Label(about_frame, text=f"{len(self.interest_users['follows'])}\nFollowers").grid(row=0, column=2, padx=10)
        Label(about_frame, text=f"{len(self.interest_users['following'])}\nFollowing").grid(row=0, column=3, padx=10)

        # edit profile / follow button
        if self.default_user:  # edit profile
            self.e_f_button = Button(about_frame, text="Edit Profile", command=self.edit_profile)
        else:
            if self.client.get_answer(("get username",)) in self.interest_users['follows']:
                # if the client follows this profile
                button_text = "unfollow"
            else:  # follow button
                button_text = "follow"
            self.e_f_button = Button(about_frame, text=button_text, command=self.follow)
        self.e_f_button.grid(row=1, column=0, columnspan=4, pady=5, sticky="we")

        # bio
        Label(about_frame, text=f"bio: {self.client.get_answer(('get bio', self.username))}").grid(row=2, column=0,
                                                                                                   padx=10,
                                                                                                   columnspan=4,
                                                                                                   sticky="w")

        # Suggestions
        suggestions = self.client.get_answer(("get suggestions",))
        if suggestions:

            Label(about_frame, text=f"Check out these users!", font=("Helvetica 16 bold", 16)).grid(row=3, column=0,
                                                                                                    pady=20)

            column_index = 0
            for current_username in suggestions:
                TinyUser(self.client, current_username, about_frame, True, ).tiny_user_frame.grid(
                    row=4,
                    column=column_index)
                column_index += 1

        # Start packing
        self.start_packing(about_frame)

    def add_username(self, posts_id):
        """
        adds the username to the posts ids
        """
        for i in range(len(posts_id)):
            posts_id[i] = (self.username, posts_id[i])

    def edit_profile(self):
        # TODO
        pass

    def follow(self):
        self.client.send_message((self.e_f_button["text"], self.username))
        time.sleep(1)  # for the server to update the sql
        self.e_f_button.config(text="follow" if self.e_f_button["text"] == "unfollow" else "unfollow")

    @staticmethod
    def get_view_profile_button_options(go_to_page) -> tuple:
        """
        A static method which makes life easier.
        :param go_to_page: just the self.go_to_page method
        :return: a dict with the text, command of the button
        """
        return "View profile", go_to_page, ProfilePage
