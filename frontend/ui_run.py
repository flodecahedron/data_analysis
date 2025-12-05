import tkinter as tk
from tkinter import filedialog
import os
import webbrowser

from backend.data_processing import data_preprocessing, data_processing
from backend.save_excel import save_excel
from backend.well_map import well_map

class RunPage(tk.Frame):
    """
    Select a data file and run processing.
    Status messages appear directly in the page.
    """

    def __init__(self, parent, controller):
        super().__init__(parent, bg="#F5F6F7")
        self.controller = controller
        self.filepath = None
        self.excel_path = None

        # --- Main container ---
        main = tk.Frame(self, bg="#F5F6F7", padx=20, pady=20)
        main.pack(expand=True, fill="both")

        tk.Label(
            main, text="Choisir un fichier de données à traiter",
            font=("Segoe UI", 14, "bold"), bg="#F5F6F7", fg="#072939"
        ).pack(pady=15)

        # Select file button
        tk.Button(
            main, text="Sélectionner un fichier", width=25,
            bg="#072939", fg="white", command=self._open_file
        ).pack(pady=10)

        # File label
        self.file_label = tk.Label(
            main, text="Aucun fichier choisi", fg="gray",
            font=("Segoe UI", 10), bg="#F5F6F7"
        )
        self.file_label.pack(pady=5)

        # Run processing button
        tk.Button(
            main, text="Lancer le traitement", width=25, bg="#072939", fg="white",
            command=self._run_backend
        ).pack(pady=25)

        # Status label
        self.status_label = tk.Label(
            self, text="", bg="#F5F6F7", fg="#333", font=("Segoe UI", 10), anchor="w"
        )
        self.status_label.pack(fill="x", pady=(5, 10))

        # Buttons shown after run
        self.open_excel_btn = tk.Button(
            self, text="Ouvrir le fichier Excel de résultats",
            width=25, bg="#049b0f", fg="white", command=self._open_excel
        )
        self.home_btn = tk.Button(
            self, text="Accueil",
            width=25, bg="#072939", fg="white", command=self._back_to_home
        )

    # ----------------------------------------------------------------------
    # UI LOGIC
    # ----------------------------------------------------------------------
    def _set_status(self, message: str, warning: bool = False):
        """Update the status label with message and color."""
        color = "#cc0000" if warning else "#006600"
        self.status_label.config(text=message, fg=color)

    def _open_file(self):
        self.filepath = filedialog.askopenfilename(
            title="Choisir un fichier de données",
            filetypes=[("TXT files", "*.txt"), ("All files", "*.*")]
        )
        if self.filepath:
            self.file_label.config(text=self.filepath, fg="gray")
            self._set_status("Fichier choisi.", warning=False)

    def _run_backend(self):
        if not self.filepath:
            return self._set_status("Choisissez d'abord un fichier.", warning=True)

        try:
            self._set_status("Traitement en cours...", warning=False)
            self.update()

            # Preprocessing
            start, plate_name = data_preprocessing(self.filepath)

            # Main processing
            results = data_processing(
                self.filepath,
                well_map,
                start,
                plate_name
            )

            # Save Excel
            self.excel_path = save_excel(results, well_map, plate_name)
            if self.excel_path:
                self._set_status("Traitement réussi!", warning=False)
                self.open_excel_btn.pack(pady=10)
                self.home_btn.pack(pady=5)

        except Exception as e:
            self._set_status(f"Erreur pendant le traitement: {str(e)}", warning=True)

    def _open_excel(self):
        if self.excel_path and os.path.exists(self.excel_path):
            webbrowser.open(self.excel_path)
        else:
            self._set_status("Fichier de résultats non trouvé.", warning=True)

    def _back_to_home(self):
        """Clear all page data and return to Home page."""
        self.filepath = None
        self.excel_path = None
        self.file_label.config(text="Aucun fichier choisi", fg="gray")
        self.status_label.config(text="")
        self.open_excel_btn.pack_forget()
        self.home_btn.pack_forget()

        # Reset other pages if controller supports it
        if hasattr(self.controller, "reset_pages"):
            self.controller.reset_pages()

        # Show home page
        self.controller.show_frame("HomePage")

    def on_show(self):
        """Optional hook when page is shown."""
        pass
