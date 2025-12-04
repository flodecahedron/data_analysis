"""
Main entry point for the app.
Manages window creation and dynamic page switching.
"""

import tkinter as tk

# ---------------------------------------------------------------------------
#  Import UI pages
# ---------------------------------------------------------------------------

from frontend.ui_home import HomePage
from frontend.ui_assign import AssignPage
from frontend.ui_run import RunPage

# ---------------------------------------------------------------------------
#  Main Application Class
# ---------------------------------------------------------------------------

class MainApp(tk.Tk):
    """
    Main Tkinter application.
    Handles:
    - main window style
    - page registration
    - page switching
    - centralized navigation
    """

    def __init__(self):
        super().__init__()

        # ------------------- Window config ----------------------
        self.title("NAOS data analysis")
        self.geometry("1100x750")
        self.minsize(900, 600)
        self.resizable(True, True)

        # ------------------- Container --------------------------
        # A single container holds all frames stacked on each other.
        container = tk.Frame(self, bg="#F5F6F7")
        container.pack(fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # ------------------- Frame registry ----------------------
        self.frames = {}
        self._register_pages(container)

        # Show the first page
        self.show_frame("HomePage")

    # ------------------------------------------------------------------

    def _register_pages(self, container):
        """
        Instantiate and store all pages in self.frames.
        """
        pages = (HomePage, AssignPage, RunPage)

        for PageClass in pages:
            frame = PageClass(container, controller=self)
            name = PageClass.__name__

            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

    # ------------------------------------------------------------------

    def show_frame(self, name: str):
        """
        Raises a frame by name. Handles navigation.
        """
        frame = self.frames[name]
        frame.tkraise()


# ---------------------------------------------------------------------------
#  Launch
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
