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

        buttons = ["POST", "POST 2 Story", "Set Profile Photo"]
        column_index = 0
        for button in buttons:
            Button(self.main_frame, text=button, command=lambda: self.button_click(button.lower()))\
                .grid(row=3, column=column_index)
            column_index += 1

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

    def button_click(self, button):
        if self.img:
            self.client.send_message([button, self.img])
            self.go_to_page(self.home_page)

