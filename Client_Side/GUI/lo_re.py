from .gui_form import GUIForm
from .home_page import HomePage
from tkinter import *
from tkinter.ttk import *


class LoRe(GUIForm):

    def __init__(self, client):
        super().__init__(client)
        self.register_flag = False

        # username label and text entry box
        Label(self.root, text="Username").grid(row=0, column=0, padx=18)
        self.username = StringVar()
        Entry(self.root, textvariable=self.username).grid(row=0, column=1)

        self.email = StringVar()
        self.first_name = StringVar()
        self.last_name = StringVar()

        # password label and password entry box
        Label(self.root, text="Password").grid(row=2, column=0)
        self.password = StringVar()
        Entry(self.root, textvariable=self.password, show='*').grid(row=2, column=1)
        self.forgot_password = Button(self.root, text="Forgot Password")  # TODO add this
        self.forgot_password.grid(row=2, column=2, padx=18)

        # login button
        self.login_button = Button(self.root, text="Login",
                                   command=lambda: self.lo_re(self.username.get(), self.password.get()))
        self.login_button.grid(row=3, column=0)
        # register button and label
        self.or_instead = Label(self.root, text="or instead")
        self.or_instead.grid(row=3, column=1)
        self.register_button = Button(self.root, text="Register",
                                      command=lambda: self.register(self.username.get(),
                                                                    self.password.get(),
                                                                    self.first_name.get(),
                                                                    self.last_name.get(),
                                                                    self.email.get()))
        self.register_button.grid(row=3, column=2)

        # error label
        self.error_text = StringVar()
        Label(self.root, textvariable=self.error_text, wraplength=250).grid(ipady=20, row=4, columnspan=4)

    def lo_re(self, *args):
        if self.client.get_answer(args):
            self.go_to_page(HomePage)
        else:
            self.error_text.set("Something went wrong...\nPlease try again with different values.")

    def register_instead(self):
        # add labels and text entry boxes
        Label(self.root, text="First Name").grid(row=0, column=2, padx=18),
        Entry(self.root, textvariable=self.first_name).grid(row=0, column=3)

        Label(self.root, text="Last Name").grid(row=1, column=2),
        Entry(self.root, textvariable=self.last_name).grid(row=1, column=3)

        Label(self.root, text="Email").grid(row=1, column=0),
        Entry(self.root, textvariable=self.email).grid(row=1, column=1)

        # move register button
        self.or_instead.grid_forget()
        self.login_button.grid_forget()
        self.forgot_password.grid_forget()
        self.register_button.grid_forget()
        self.register_button.grid(row=3, column=0, pady=7)

        self.register_flag = True

    def register(self, *args):
        if not self.register_flag:
            self.register_instead()
        else:
            self.lo_re(*args)
