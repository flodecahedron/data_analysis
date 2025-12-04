import tkinter as tk
from tkinter import filedialog

from backend.data_processing import data_preprocessing, data_processing
from backend.save_excel import save_excel
from backend.well_map import well_map
from backend.silent_show import silent_info, silent_warning


class RunPage(tk.Frame):
    """
    Page de sélection du fichier de données et lancement du traitement.
    """

    def __init__(self, parent, controller):
        super().__init__(parent, bg="#F5F6F7")
        self.controller = controller

        self.filepath = None

        # --- UI BUILD ---
        main = tk.Frame(self, bg="#F5F6F7", padx=20, pady=20)
        main.pack(expand=True, fill="both")

        tk.Label(
            main, text="Choisir un fichier de données à traiter",
            font=("Segoe UI", 14), bg="#F5F6F7"
        ).pack(pady=15)

        # Bouton sélectionner fichier
        tk.Button(
            main, text="Sélectionner fichier", width=25,
            command=self._open_file
        ).pack(pady=10)

        # Label affichant le fichier choisi
        self.file_label = tk.Label(
            main, text="Aucun fichier sélectionné", fg="gray",
            font=("Segoe UI", 10), bg="#F5F6F7"
        )
        self.file_label.pack(pady=5)

        # Bouton lancer traitement
        tk.Button(
            main, text="Lancer le traitement",
            width=25, bg="#4477aa", fg="white",
            command=self._run_backend
        ).pack(pady=25)

    # ----------------------------------------------------------------------
    #                            UI LOGIC
    # ----------------------------------------------------------------------
    def _open_file(self):
        self.filepath = filedialog.askopenfilename(
            title="Choisir le fichier de données",
            filetypes=[("TXT files", "*.txt"), ("All files", "*.*")]
        )
        if self.filepath:
            self.file_label.config(text=self.filepath, fg="gray")

    def _run_backend(self):
        if not self.filepath:
            silent_warning("Erreur", "Veuillez d’abord choisir un fichier.")
            return

        try:
            # Prétraitement
            start, plate_name = data_preprocessing(self.filepath)

            # Traitement principal
            results = data_processing(
                self.filepath,
                well_map,
                start,
                plate_name
            )

            # Sauvegarde
            end = save_excel(results, well_map, plate_name)

            if end:
                silent_info("Succès", "Traitement terminé !")

        except Exception as e:
            silent_warning("Erreur pendant le traitement", str(e))

    # ----------------------------------------------------------------------
    def on_show(self):
        """Hook appelé lors de l'affichage de la page"""
        pass
