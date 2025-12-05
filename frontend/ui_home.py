import tkinter as tk

# ---------------------------------------------------------------------------
# Home Page Frame

class HomePage(tk.Frame):
    """
    Home page frame.
    Displays the main title and a button to navigate to the assignment step.
    """

    def __init__(self, parent, controller):
        super().__init__(parent, bg="#F5F6F7")

        self.controller = controller

        # ------------------- Main layout container -------------------
        container = tk.Frame(self, bg="#F5F6F7", padx=40, pady=40)
        container.place(relx=0.5, rely=0.5, anchor="center")

        # ------------------- Title -------------------
        title = tk.Label(
            container,
            text="Outil d'analyse de données",
            font=("Segoe UI", 24, "bold"),
            bg="#F5F6F7",
            fg="#072939"
        )
        title.pack(pady=(0, 20))

        # ------------------- Subtitle -------------------
        subtitle = tk.Label(
            container,
            text="Bienvenue! Cliquez ci-dessous pour commencer.",
            font=("Segoe UI", 12),
            bg="#F5F6F7",
            fg="#072939"
        )
        subtitle.pack(pady=(0, 30))

        # ------------------- Start Button -------------------
        start_btn = tk.Button(
            container,
            text="Démarrer",
            bg="#072939",
            fg="white",
            font=("Segoe UI", 14),
            relief="raised",
            bd=2,
            padx=20,
            pady=8,
            command=self.go_to_assign_page
        )
        start_btn.pack()

    # ------------------------------------------------------------------
    def go_to_assign_page(self):
        """Navigate to the assignment page."""
        self.controller.show_frame("AssignPage")

    # ------------------------------------------------------------------
    def on_show(self):
        """
        Optional hook called each time the page is displayed.
        Useful for refreshing content if needed.
        """
        pass
