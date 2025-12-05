import tkinter as tk
from tkinter import ttk

# ---------------------------------------------------------------------------
#  Import UI pages
from frontend.ui_home import HomePage
from frontend.ui_assign import AssignPage
from frontend.ui_run import RunPage

# ---------------------------------------------------------------------------
# Main Application Class

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

        # ------------------- Window configuration ----------------------
        self.title("NAOS Data Analysis Tool")
        self.geometry("1100x750")
        self.minsize(900, 600)
        self.resizable(True, True)

        # Set window icon
        try:
            self.iconbitmap("naos.ico")
        except Exception:
            print("Warning: naos.ico not found. Using default icon.")

        # Change title bar / menu bar color (using ttk style)
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure("TFrame", background="#F5F6F7")  # Container background
        style.configure("TLabel", background="#F5F6F7")
        style.configure("TButton", background="#4477aa", foreground="white")

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
    def reset_pages(self):
        """
        Re-instantiate all pages to reset their state.
        """
        container = self.frames["HomePage"].master  # container frame
        # Destroy old frames
        for frame in self.frames.values():
            frame.destroy()
        # Re-register
        self.frames = {}
        self._register_pages(container)

    # ------------------------------------------------------------------
    def show_frame(self, name: str):
        """
        Raises a frame by name. Handles navigation.
        """
        frame = self.frames[name]
        frame.tkraise()

# ---------------------------------------------------------------------------
#  Launch application
if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
