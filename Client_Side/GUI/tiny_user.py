from tkinter import *
from tkinter.ttk import *

from PIL import ImageTk


class TinyUser:
    def __init__(self, client, username, root_frame):
        """
        create a tiny user frame with all the information about it.
        :param client: the regular client
        :param username: the tiny user
        """

        # Create A tiny user Frame
        self.tiny_user_frame = Frame(root_frame)

        # profile photo
        profile_photo = ImageTk.PhotoImage(client.get_answer(("get profile photo", username)))
        profile_photo_lbl = Label(self.tiny_user_frame, image=profile_photo)
        profile_photo_lbl.image = profile_photo
        profile_photo_lbl.grid(row=0, column=0, pady=5, padx=20)

        # username
        Label(self.tiny_user_frame, text=f"@{username}", font=("Bebas", 12)).grid(row=1, column=0, pady=10)
