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
            if current_page_name == page_class.__class__.__name__:
                current_button.configure(command=lambda: self.go_to_page(page_class))
            else:
                if current_page_name == "Home":
                    from .home_page import HomePage
                    self.HomePage = HomePage
                    current_button.configure(command=lambda: self.go_to_page(HomePage))
                elif current_page_name == "Profile":
                    from .profile_page import ProfilePage
                    current_button.configure(command=lambda: self.go_to_page(ProfilePage))
                elif current_page_name == "Upload":
                    from .upload_page import UploadPage
                    current_button.configure(command=lambda: self.go_to_page(UploadPage))

            current_button.grid(row=0, column=column_index)

            column_index += 1
