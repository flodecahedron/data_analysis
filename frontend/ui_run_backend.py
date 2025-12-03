import tkinter as tk
from tkinter import filedialog, messagebox

from backend.data_processing import data_preprocessing, data_processing
from backend.save_fig import save_fig
from backend.well_map import well_map

class BackendWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Exécution du traitement")

        frame = tk.Frame(root, padx=20, pady=20)
        frame.pack()

        tk.Label(frame, text="Choisir un fichier de données",
                 font=("Arial", 14)).pack(pady=10)

        tk.Button(frame, text="Sélectionner fichier", command=self.open_file
                  ).pack(pady=10)

        self.filepath = None

        tk.Button(frame, text="Lancer le traitement", bg="#4477aa",
                  fg="white", command=self.run_backend).pack(pady=20)

    def open_file(self):
        self.filepath = filedialog.askopenfilename(
            title="Choisir le fichier de données",
            filetypes=[("TXT files", "*.txt"), ("All files", "*.*")]
        )
        if self.filepath:
            messagebox.showinfo("Fichier sélectionné",
                                f"Fichier choisi :\n{self.filepath}")

    def run_backend(self):
        if not self.filepath:
            messagebox.showerror("Erreur", "Veuillez d’abord choisir un fichier.")
            return

        try:
            end=0
            start, plate_name = data_preprocessing(self.filepath)
            results = data_processing(self.filepath, well_map, start, plate_name)
            end = save_fig(results, well_map, plate_name)

            if end:
                messagebox.showinfo("Succès", "Traitement terminé !")

        except Exception as e:
            messagebox.showerror("Erreur pendant le traitement", str(e))
