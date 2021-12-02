from .gui_form import GUIForm
from tkinter import *
from tkinter import filedialog
from tkinter.ttk import *
from PIL import Image, ImageTk


class UploadPage(GUIForm):
    BASE_HEIGHT = 300

    def __init__(self, client, HomePage):
        super().__init__(client)
        self.home_page = HomePage

        # Create A Bottom Bar Frame
        bar_frame = Frame(self.root)
        bar_frame.pack(side="bottom", fill="x")

        Button(bar_frame, text="Home", command=lambda: self.go_to_page(self.home_page)).grid(row=0, column=0)
        Button(bar_frame, text="Search", command=lambda: self.go_to_page("SearchPage")).grid(row=0, column=1)

        # Create A Main Frame
        self.main_frame = Frame(self.root)
        self.main_frame.pack()

        self.image_lbl = Label(self.main_frame)  # just to grid forget later
        self.img = None

        Button(self.main_frame, text="Browse A File", command=self.file_dialog).grid(row=1, column=0)
        Button(self.main_frame, text="POST", command=self.post).grid(row=3, column=0)
        Button(self.main_frame, text="POST 2 Story", command=self.post2story).grid(row=3, column=1)

    def file_dialog(self):
        filename = filedialog.askopenfilename(
            initialdir="/", title="Select A File", filetype=(("jpeg files", "*.jpg"), ("all files", "*.*")))

        self.img = Image.open(filename)

        # resize image
        h_percent = (self.BASE_HEIGHT / self.img.size[1])
        w_size = int(self.img.size[0] * h_percent)
        self.img = self.img.resize((w_size, self.BASE_HEIGHT), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(self.img)

        self.image_lbl.grid_forget()
        self.image_lbl = Label(self.main_frame, image=photo)
        self.image_lbl.image = photo
        self.image_lbl.grid(row=2, column=2)

    def post(self):
        if self.img:
            self.client.send_message(["post", self.img])
            self.go_to_page(self.home_page)

    def post2story(self):
        if self.img:
            self.client.send_message(["post2story", self.img])
            self.go_to_page(self.home_page)
