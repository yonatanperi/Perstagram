from .gui_form import GUIForm
from tkinter import *


class AppForm(GUIForm):

    PAGES = ["Home", "Profile", "Search", "Upload"]

    def __init__(self, client, page_class):
        """
        After login, the user will navigate in the main app.
        this class creates the navigation bar on the bottom.
        In order to add a page, add it's name to  PAGES list and add an if statement in the for loop.
        """
        super().__init__(client)

        # Create A Bottom Bar Frame
        self.bar_frame = Frame(self.root)
        self.bar_frame.pack(side="bottom", fill="x")

        column_index = 0
        for current_page_name in self.PAGES:
            current_button = Button(self.bar_frame, text=current_page_name)
            if current_page_name == page_class.__class__.__name__[:-4]:
                current_button.configure(command=lambda: self.go_to_page(page_class))
            else:
                if current_page_name == "Home":
                    from .home_page import HomePage
                    self.home_page = HomePage
                    current_button.configure(command=lambda: self.go_to_page(HomePage))
                elif current_page_name == "Profile":
                    from .profile_page import ProfilePage
                    current_button.configure(command=lambda: self.go_to_page(ProfilePage))
                elif current_page_name == "Upload":
                    from .upload_page import UploadPage
                    current_button.configure(command=lambda: self.go_to_page(UploadPage))
                elif current_page_name == "Search":
                    from .search_page import SearchPage
                    current_button.configure(command=lambda: self.go_to_page(SearchPage))

            current_button.grid(row=0, column=column_index)

            column_index += 1

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def get_scrollbar_frame(self):
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
