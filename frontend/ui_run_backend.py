import tkinter as tk
from tkinter import filedialog

from backend.data_processing import data_preprocessing, data_processing
from backend.save_excel import save_excel
from backend.well_map import well_map
from backend.silent_show import silent_info, silent_warning

class BackendWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("NAOS data analysis - Choix des données")
        self.root.iconbitmap("naos.ico")

        frame = tk.Frame(root, padx=20, pady=20)
        frame.pack()

        tk.Label(frame, text="Choisir un fichier de données",
                 font=("Arial", 14)).pack(pady=10)

        tk.Button(frame, text="Sélectionner fichier", command=self.open_file
                  ).pack(pady=10)

        # Label affichant le fichier sélectionné
        self.file_label = tk.Label(frame, text="Aucun fichier sélectionné",
                                   fg="gray", font=("Arial", 10))
        self.file_label.pack(pady=5)

        self.filepath = None

        tk.Button(frame, text="Lancer le traitement", bg="#4477aa",
                  fg="white", command=self.run_backend).pack(pady=20)

    def open_file(self):
        self.filepath = filedialog.askopenfilename(
            title="Choisir le fichier de données",
            filetypes=[("TXT files", "*.txt"), ("All files", "*.*")]
        )
        if self.filepath:
            # ➜ mettre le chemin du fichier dans la fenêtre (gris)
            self.file_label.config(text=self.filepath, fg="gray")

    def run_backend(self):
        if not self.filepath:
            silent_warning("Erreur", "Veuillez d’abord choisir un fichier.")
            return

        try:
            start, plate_name = data_preprocessing(self.filepath)
            results = data_processing(self.filepath, well_map, start, plate_name)
            end = save_excel(results, well_map, plate_name)

            if end:
                silent_info("Succès", "Traitement terminé !")

        except Exception as e:
            silent_warning("Erreur pendant le traitement", str(e))
