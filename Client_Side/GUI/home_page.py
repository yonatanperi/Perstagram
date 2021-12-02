from .app_form import AppForm
from tkinter import *
from tkinter.ttk import *


class HomePage(AppForm):

    def __init__(self, client):
        super().__init__(client, self)
        self.scroll_frame = self.set_scrollbar()
        Label(self.scroll_frame, text="Welcome to PERSTAGRAM!", font=("Helvetica 18 bold", 25)).pack(pady=15, padx=10,
                                                                                                     fill='x',
                                                                                                     expand=True)

        for thing in range(100):
            Button(self.scroll_frame, text=f'Button {thing + 1} Yo!').pack(pady=10, padx=10, fill='x')

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def set_scrollbar(self):
        # Create A Main Frame
        main_frame = Frame(self.root)
        main_frame.pack(fill=BOTH, expand=1)

        # Create A Canvas
        self.canvas = Canvas(main_frame)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=1)

        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

        # Add A Scrollbar To The Canvas
        self.scrollbar = Scrollbar(main_frame, orient=VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        # Configure The Canvas
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Create ANOTHER Frame INSIDE the Canvas
        scroll_frame = Frame(self.canvas)

        # Add that New frame To a Window In The Canvas
        self.canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

        return scroll_frame
