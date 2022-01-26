from tkinter import *
from tkinter.ttk import *

from PIL import ImageTk


class TinyUser:
    def __init__(self, client, username: str, root_frame, view_profile: bool, ProfilePage=None, go_to_page=None):
        """
        create a tiny user frame with all the information about it.
        :param client: the regular client
        :param username: the tiny user
        :param view_profile: set a view profile button
        """

        # Create A tiny user Frame
        self.tiny_user_frame = Frame(root_frame)

        # profile photo
        profile_photo = ImageTk.PhotoImage(client.get_answer(("get profile photo", username)))
        profile_photo_lbl = Label(self.tiny_user_frame, image=profile_photo)
        profile_photo_lbl.image = profile_photo
        profile_photo_lbl.grid(row=0, column=0, pady=5, padx=20)

        # username
        Label(self.tiny_user_frame, text=f"@{username}", font=("Bebas", 10)).grid(row=1, column=0, pady=10)

        # view profile
        if view_profile:
            Button(self.tiny_user_frame, text="View profile", command=lambda: go_to_page(ProfilePage, username)).grid(
                row=2, column=0)
