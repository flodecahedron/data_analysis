import tkinter as tk


class HomePage(tk.Frame):
    """
    Page d'accueil.
    Affiche un titre et un bouton pour aller à l'étape d'import.
    """

    def __init__(self, parent, controller):
        super().__init__(parent, bg="#F5F6F7")

        self.controller = controller

        # --- Layout principal ---
        container = tk.Frame(self, bg="#F5F6F7", padx=40, pady=40)
        container.place(relx=0.5, rely=0.5, anchor="center")

        # --- Titre ---
        title = tk.Label(
            container,
            text="Outil d'analyse de données NAOS",
            font=("Segoe UI", 24, "bold"),
            bg="#F5F6F7",
            fg="#333"
        )
        title.pack(pady=(0, 20))

        # --- Sous-titre ---
        subtitle = tk.Label(
            container,
            text="Bienvenue. Cliquez ci-dessous pour commencer.",
            font=("Segoe UI", 12),
            bg="#F5F6F7",
            fg="#555"
        )
        subtitle.pack(pady=(0, 30))

        # --- Bouton Commencer ---
        start_btn = tk.Button(
            container,
            text="Commencer",
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
        """Navigation vers la première étape."""
        self.controller.show_frame("AssignPage")

    # ------------------------------------------------------------------

    def on_show(self):
        """
        Hook optionnel appelé à chaque affichage.
        Utile plus tard si on veut rafraîchir la page.
        """
        pass
