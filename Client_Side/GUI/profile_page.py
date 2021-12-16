from .app_form import AppForm
from .post_object import Post
from tkinter import *
from tkinter.ttk import *
from PIL import ImageTk


class ProfilePage(AppForm):

    def __init__(self, client, username=None):
        super().__init__(client, self)
        if not username:  # set default username
            self.username = client.get_answer(("get username",))
            self.default_user = True
        else:
            self.username = username
            self.default_user = False

        self.scroll_frame = self.get_scrollbar_frame()
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

        # edit profile / follow button
        if self.default_user:  # edit profile
            self.e_f_button = Button(about_frame, text="Edit Profile", command=self.edit_profile)
        else:
            if self.username in self.interest_users['following']:
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

        # All the user's posts
        self.posts_ids = self.client.get_answer(("get all posts", self.username))
        Label(about_frame, text=f"{len(self.posts_ids)}\nPosts").grid(row=0, column=1, padx=10)  # posts number

        for post_id in self.posts_ids:
            Post(self.client, self.username, post_id[0], self.scroll_frame).post_frame.pack()

    def edit_profile(self):
        # TODO
        pass

    def follow(self):
        if self.e_f_button["text"] == "follow":
            # TODO
            pass
        else:
            # TODO
            pass
