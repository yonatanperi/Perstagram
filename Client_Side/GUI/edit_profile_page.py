from .app_form import AppForm
from tkinter import *
from tkinter.ttk import *
from .close_friends_page import CloseFriendsPage


class EditProfilePage(AppForm):

    def __init__(self, client):
        super().__init__(client, None)

        self.first_name = StringVar()
        self.last_name = StringVar()
        self.bio = StringVar()

        main_frame = Frame(self.root)
        main_frame.pack(side=TOP)

        """self.open_user = BooleanVar()
        self.open_user.set()
        Checkbutton(main_frame, text='Open', variable=self.open_user).grid(row=0, column=2, pady=10)"""  # TODO

        # add labels and text entry boxes
        Label(main_frame, text="First Name").grid(row=0, column=0, pady=10)
        Entry(main_frame, textvariable=self.first_name).grid(row=0, column=1, pady=10)

        Label(main_frame, text="Last Name").grid(row=1, column=0, pady=10),
        Entry(main_frame, textvariable=self.last_name).grid(row=1, column=1, pady=10)

        Label(main_frame, text="Bio").grid(row=2, column=0, pady=10),
        Entry(main_frame, textvariable=self.bio, width=20).grid(row=2, column=1, pady=10)

        Button(main_frame, text="Close Friends", command=lambda: self.go_to_page(CloseFriendsPage)).grid(row=0,
                                                                                                         column=2)

        Button(main_frame, text="Submit", command=lambda: self.client.send_message(("change profile", {
            "first_name": self.first_name.get(),
            "last_name": self.last_name.get(),
            "bio": self.bio.get()
            # "open_user": self.open_user.get(),
        }))).grid(row=3, column=0, columnspan=2)
