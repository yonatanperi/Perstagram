from tkinter import *
from tkinter.ttk import *

from PIL import ImageTk


class TinyUser:
    def __init__(self, client, username: str, root_frame, order: bool, button_options: tuple = None):
        """
        create a tiny user frame with all the information about it.
        :param client: the regular client
        :param username: the tiny user
        :param button_options: a tuple of: (text, go_to_page method, page to go when clicked)
        :param order: True - on the bottom, False - on the right
        """

        # Create A tiny user Frame
        self.tiny_user_frame = Frame(root_frame)

        # set order
        row_method = lambda row_index: row_index if order else 0
        column_method = lambda column_index: 0 if order else column_index

        # profile photo
        index = 0
        profile_photo = ImageTk.PhotoImage(client.get_answer(("get profile photo", username)))
        profile_photo_lbl = Label(self.tiny_user_frame, image=profile_photo)
        profile_photo_lbl.image = profile_photo
        profile_photo_lbl.grid(row=row_method(index), column=column_method(index), pady=10, padx=10)

        # username
        index = 1
        Label(self.tiny_user_frame, text=f"@{username}", font=("Bebas", 12)).grid(row=row_method(index),
                                                                                  column=column_method(index), pady=10,
                                                                                  padx=10)

        # button
        if button_options:
            index = 2
            Button(self.tiny_user_frame, text=button_options[0],
                   command=lambda u=username: button_options[1](button_options[2], u)).grid(row=row_method(index),
                                                                                            column=column_method(index),
                                                                                            pady=10,
                                                                                            padx=10)
