from .app_form import AppForm
from tkinter import *
from tkinter import filedialog
from tkinter.ttk import *
from PIL import Image, ImageTk


class UploadPage(AppForm):
    BASE_HEIGHT = 300

    def __init__(self, client):
        super().__init__(client, self)

        # Create A Main Frame
        self.main_frame = Frame(self.root)
        self.main_frame.pack()

        self.image_lbl = Label(self.main_frame)  # just to grid forget later
        self.img = None

        Button(self.main_frame, text="Browse A File", command=self.file_dialog).grid(row=1, column=0)

        Button(self.main_frame, text="POST", command=lambda: self.button_click("post")).grid(row=3, column=0)
        Button(self.main_frame, text="POST 2 Story", command=lambda: self.button_click("post2story", False)).grid(row=3,
                                                                                                                  column=1)
        Button(self.main_frame, text="POST 2 Close Friends Story",
               command=lambda: self.button_click("post2story", True)).grid(row=4, column=1)
        Button(self.main_frame, text="Set Profile Photo", command=lambda: self.button_click("set profile photo")).grid(
            row=3, column=2)

    def file_dialog(self):
        filename = filedialog.askopenfilename(
            initialdir="/", title="Select A File", filetype=(("jpeg files", "*.jpg"), ("all files", "*.*")))

        if filename:
            self.img = Image.open(filename)

            # resize image
            h_percent = (self.BASE_HEIGHT / self.img.size[1])
            w_size = int(self.img.size[0] * h_percent)
            self.img = self.img.resize((w_size, self.BASE_HEIGHT), Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(self.img)

            self.image_lbl.grid_forget()
            self.image_lbl = Label(self.main_frame, image=photo)
            self.image_lbl.image = photo
            self.image_lbl.grid(row=2, column=0, columnspan=3)

    def button_click(self, button, *args):
        if self.img:
            self.client.send_message([button, self.img, *args])
            self.go_to_page(self.home_page)
