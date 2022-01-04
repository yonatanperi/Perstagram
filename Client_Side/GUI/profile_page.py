import time

from .scroll_posts_frame import ScrollPostsFrame
from tkinter import *
from tkinter.ttk import *
from PIL import ImageTk


class ProfilePage(ScrollPostsFrame):

    def __init__(self, client, username=None):

        if not username:  # set default username
            self.username = client.get_answer(("get username",))
            self.default_user = True  # The client is in his own profile page
        else:
            self.username = username
            self.default_user = False

        self.posts_ids = client.get_answer(("get all posts", self.username))
        self.add_username(self.posts_ids)

        super().__init__(client, 0.7, iter(self.posts_ids))

        # About bar
        about_frame = Frame(self.scroll_frame)
        about_frame.pack(pady=10)

        # profile photo
        profile_photo = ImageTk.PhotoImage(self.client.get_answer(("get profile photo", self.username)))
        profile_photo_lbl = Label(about_frame, image=profile_photo)
        profile_photo_lbl.image = profile_photo
        profile_photo_lbl.grid(row=0, column=0, padx=20)

        # interest users
        self.interest_users = self.client.get_answer(("get interest users", self.username))
        Label(about_frame, text=f"{len(self.interest_users['follows'])}\nFollows").grid(row=0, column=2, padx=10)
        Label(about_frame, text=f"{len(self.interest_users['following'])}\nFollowing").grid(row=0, column=3, padx=10)

        # username
        Label(about_frame, text=self.username, font=("Helvetica 14 bold", 14)).grid(row=1, column=0, pady=10)

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
        self.e_f_button.grid(row=2, column=0, columnspan=4, pady=5, sticky="we")

        # bio
        Label(about_frame, text=f"bio: {self.client.get_answer(('get bio', self.username))}").grid(row=3, column=0,
                                                                                                   padx=10,
                                                                                                   columnspan=4,
                                                                                                   sticky="w")

        # All the user's posts
        Label(about_frame, text=f"{len(self.posts_ids)}\nPosts").grid(row=0, column=1, padx=10)  # posts number

        # Start packing
        self.start_packing(about_frame)

    def add_username(self, posts_id):
        for i in range(len(posts_id)):
            posts_id[i] = (self.username, posts_id[i][0])

    def edit_profile(self):
        # TODO
        pass

    def follow(self):
        self.client.send_message((self.e_f_button["text"], self.username))
        time.sleep(1)  # for the server to update the sql
        self.e_f_button.config(text="follow" if self.e_f_button["text"] == "unfollow" else "unfollow")
