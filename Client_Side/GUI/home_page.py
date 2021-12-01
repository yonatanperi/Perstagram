from .gui_form import GUIForm
from tkinter import *
from tkinter.ttk import *


class HomePage(GUIForm):

    def __init__(self, client):
        super().__init__(client)

        self.scroll_frame = self.set_scrollbar()

        for thing in range(100):
            Button(self.scroll_frame, text=f'Button {thing} Yo!').grid(row=thing, column=0, pady=10, padx=10)

        my_label = Label(self.scroll_frame, text="It's Friday Yo!").grid(row=3, column=2)

    def set_scrollbar(self):
        # Create A Main Frame
        main_frame = Frame(self.root)
        main_frame.pack(fill=BOTH, expand=1)

        # Create A Canvas
        my_canvas = Canvas(main_frame)
        my_canvas.pack(side=LEFT, fill=BOTH, expand=1)

        # Add A Scrollbar To The Canvas
        my_scrollbar = Scrollbar(main_frame, orient=VERTICAL, command=my_canvas.yview)
        my_scrollbar.pack(side=RIGHT, fill=Y)

        # Configure The Canvas
        my_canvas.configure(yscrollcommand=my_scrollbar.set)
        my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all")))

        # Create ANOTHER Frame INSIDE the Canvas
        scroll_frame = Frame(my_canvas)

        # Add that New frame To a Window In The Canvas
        my_canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

        return scroll_frame

    def run(self):
        self.root.mainloop()
