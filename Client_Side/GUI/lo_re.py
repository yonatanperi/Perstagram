from PIL import ImageTk

from .gui_form import GUIForm
from .home_page import HomePage
from .reset_password import ResetPassword
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
        self.captcha_text = StringVar()

        # password label and password entry box
        Label(self.root, text="Password").grid(row=2, column=0)
        self.password = StringVar()
        Entry(self.root, textvariable=self.password, show='*').grid(row=2, column=1)
        self.forgot_password = Button(self.root, text="Forgot Password",
                                      command=lambda: self.go_to_page(ResetPassword, LoRe))
        self.forgot_password.grid(row=2, column=2, padx=18)
        self.forgot_password["state"] = "disabled"  # will be enabled after captcha

        # login button
        self.login_button = Button(self.root, text="Login",
                                   command=lambda: self.lo_re(self.username.get(), self.password.get()))
        self.login_button.grid(row=10, column=0)
        self.login_button["state"] = "disabled"  # will be enabled after captcha

        self.open_user = BooleanVar(self.root, True)

        # register button and label
        self.or_instead = Label(self.root, text="or instead")
        self.or_instead.grid(row=10, column=1)
        self.register_button = Button(self.root, text="Register",
                                      command=lambda: self.register(self.username.get(),
                                                                    self.password.get(),
                                                                    self.first_name.get(),
                                                                    self.last_name.get(),
                                                                    self.email.get(),
                                                                    self.open_user.get()))
        self.register_button.grid(row=10, column=2)
        self.register_button["state"] = "disabled"  # will be enabled after captcha

        # captcha
        photo = ImageTk.PhotoImage(self.client.recv_message())
        self.captcha_img_lbl = Label(self.root, image=photo)
        self.captcha_img_lbl.image = photo
        self.captcha_img_lbl.grid(row=4, column=0, pady=30, columnspan=10)

        Label(self.root, text="Enter the text on top: \n(No spaces)").grid(row=5, column=0, pady=15)
        Entry(self.root, textvariable=self.captcha_text).grid(row=5, column=1)

        self.captcha_verify_button = Button(self.root, text="Verify", command=self.verify_captcha)
        self.captcha_verify_button.grid(row=5, column=2, padx=10)
        # error label
        self.error_text = StringVar()
        Label(self.root, textvariable=self.error_text, wraplength=250).grid(ipady=20, row=11, columnspan=4)

    def verify_captcha(self):
        server_verification = self.client.get_answer(self.captcha_text.get())
        if server_verification == "code changed":
            photo = ImageTk.PhotoImage(self.client.recv_message())
            self.captcha_img_lbl.configure(image=photo)
            self.captcha_img_lbl.image = photo

        elif server_verification:
            # correct text
            self.login_button["state"] = "normal"
            self.register_button["state"] = "normal"
            self.forgot_password["state"] = "normal"

            self.captcha_verify_button["state"] = "disabled"

            self.error_text.set("CAPTCHA is correct!")
        else:
            self.error_text.set("Wrong CAPTCHA text!")

    def lo_re(self, *args):
        if self.client.get_answer(args):
            self.go_to_page(HomePage)
        else:
            self.error_text.set("Something went wrong...\nPlease try again with different values.")

    def register_instead(self):
        # add labels and text entry boxes
        Label(self.root, text="First Name").grid(row=0, column=2, padx=18)
        Entry(self.root, textvariable=self.first_name).grid(row=0, column=3)

        Label(self.root, text="Last Name").grid(row=1, column=2),
        Entry(self.root, textvariable=self.last_name).grid(row=1, column=3)

        Label(self.root, text="Email").grid(row=1, column=0),
        Entry(self.root, textvariable=self.email).grid(row=1, column=1)

        Checkbutton(self.root, text='Open', variable=self.open_user).grid(row=3, column=0)

        # move register button
        self.or_instead.grid_forget()
        self.login_button.grid_forget()
        self.forgot_password.grid_forget()
        self.register_button.grid_forget()
        self.register_button.grid(row=10, column=0, pady=7)

        self.register_flag = True

    def register(self, *args):
        if not self.register_flag:
            self.register_instead()
        else:
            self.lo_re(*args)
