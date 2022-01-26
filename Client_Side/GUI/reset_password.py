from .gui_form import GUIForm
from tkinter import *
from tkinter.ttk import *


class ResetPassword(GUIForm):
    EMAIL_CODE_LENGTH = 7

    def __init__(self, client, LoRe):
        super().__init__(client)
        self.LoRe = LoRe

        self.lbl = Label(self.root, text="Please enter your email: ")
        self.lbl.grid(row=0, column=0, padx=18, pady=15)
        self.text_from_entry = StringVar()
        self.entry = Entry(self.root, textvariable=self.text_from_entry)
        self.entry.grid(row=0, column=1)

        # login button
        self.send_button = Button(self.root, text="Send verification code", command=self.send_verification_code)
        self.send_button.grid(row=2, column=0)

        self.error_text = StringVar()
        Label(self.root, textvariable=self.error_text, wraplength=250).grid(ipady=20, row=11, columnspan=4)

    def send_verification_code(self):
        # the server will send a code
        list(map(self.client.send_message, ("forgot password", self.text_from_entry.get())))

        # ask the user for the code
        self.text_from_entry.set("")
        self.send_button.config(text="Verify", command=self.verify_code)
        self.lbl.config(text="Enter the code from email: ")

    def verify_code(self):
        server_verification = self.client.get_answer(self.text_from_entry.get())

        if server_verification == "code changed":
            self.send_button.config(text="Send verification code", command=self.send_verification_code)
            self.lbl.config(text="Please enter your email: ")
            self.error_text.set("Code changed!")

        elif server_verification:
            # correct text
            self.lbl.config(text="Please enter your new password: ")
            self.entry.config(show="*")
            self.send_button.config(text="Confirm", command=self.complete)

            self.error_text.set("Code is correct!")
        else:
            self.error_text.set("Wrong code!")

        self.text_from_entry.set("")

    def complete(self):
        self.client.send_message(self.text_from_entry.get())
        self.go_to_page(self.LoRe)
