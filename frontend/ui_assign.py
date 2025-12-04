import tkinter as tk
from tkinter import filedialog
import random
import importlib.util
import difflib
import os

from frontend.ui_run_backend import BackendWindow
from backend.condition_manager import ConditionManager
from backend.silent_show import silent_info, silent_warning

ROWS = ["A","B","C","D","E","F","G","H"]
COLS = [str(i) for i in range(1,13)]

def random_color():
    """Génère une couleur lisible aléatoire."""
    return "#%06x" % random.randint(0x444444, 0xFFFFFF)

class AssignWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("NAOS data analysis - Assignation des conditions aux puits")
        self.root.iconbitmap("naos.ico")

        self.current_condition = None
        self.current_control = False
        self.well_map = {}
        self.cond_colors = {}
        self.well_buttons = {}
        self.control_conditions = {}

        # Manager pour conditions existantes
        self.condition_manager = ConditionManager()
        self.condition_library = self.condition_manager.get_all()

        self.create_widgets()

    def create_widgets(self):
        # Top: input et suggestions
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)

        tk.Label(top_frame, text="Nom de la condition :").pack(side=tk.LEFT)
        self.cond_entry = tk.Entry(top_frame, width=20)
        self.cond_entry.pack(side=tk.LEFT, padx=5)
        self.cond_entry.bind("<KeyRelease>", self.update_suggestions)

        # Suggestions
        self.suggestion_box = tk.Listbox(top_frame, height=5, width=25)
        self.suggestion_box.pack(side=tk.LEFT, padx=5)
        self.suggestion_box.bind("<<ListboxSelect>>", self.select_suggestion)

        # Checkbox groupe de contrôle
        self.control_var = tk.BooleanVar(value=False)
        self.control_check = tk.Checkbutton(top_frame, text="Groupe de contrôle",
                                            variable=self.control_var)
        self.control_check.pack(side=tk.LEFT, padx=5)

        # Boutons
        tk.Button(top_frame, text="Sélectionner condition",
                  command=self.set_condition).pack(side=tk.LEFT, padx=5)
        tk.Label(top_frame,text="ou"
                 ,font=("Arial", 10, "italic"),fg="grey").pack(side=tk.LEFT, padx=3)
        tk.Button(top_frame, text="Importer répartition existante",
                  command=self.import_well_map).pack(side=tk.LEFT, padx=5)

        # Plaque
        plate_frame = tk.Frame(self.root)
        plate_frame.pack(side=tk.LEFT, padx=20, pady=10)

        for r, row in enumerate(ROWS):
            for c, col in enumerate(COLS):
                well = f"{row}{col}"
                btn = tk.Button(plate_frame, text=well, width=4, height=1)
                btn.bind("<Button-1>", lambda e, w=well: self.assign_well(w))
                btn.bind("<Button-3>", lambda e, w=well: self.unassign_well(w))
                btn.grid(row=r, column=c, padx=2, pady=2)
                self.well_buttons[well] = btn

        # Légende des couleurs
        self.legend_frame = tk.Frame(self.root)
        self.legend_frame.pack(side=tk.LEFT, padx=20, pady=10)
        self.legend_labels = {}

        # Boutons bas
        tk.Button(self.root, text="Poursuivre",
                  command=self.next_window, bg="#88ccee").pack(pady=15)

    def update_legend(self):
        """Met à jour la légende des couleurs."""
        for w in self.legend_frame.winfo_children():
            w.destroy()
        for cond, color in self.cond_colors.items():
            control = self.control_conditions.get(cond, False)
            label_text = cond + (" (Contrôle)" if control else "")
            lbl = tk.Label(self.legend_frame, text=label_text, bg=color, width=20)
            lbl.pack(pady=2)
            self.legend_labels[cond] = lbl

    def select_suggestion(self, event):
        if not self.suggestion_box.curselection():
            return
        index = self.suggestion_box.curselection()[0]
        chosen = self.suggestion_box.get(index)
        self.cond_entry.delete(0, tk.END)
        self.cond_entry.insert(0, chosen)

    def update_suggestions(self, event=None):
        typed = self.cond_entry.get().strip()
        self.suggestion_box.delete(0, tk.END)
        if not typed:
            return
        suggestions = difflib.get_close_matches(
            typed, self.condition_library, n=5, cutoff=0.1
        )
        for s in suggestions:
            self.suggestion_box.insert(tk.END, s)

    def import_well_map(self):
        """Importer un fichier well_map.py existant et mettre à jour la plaque."""
        file_path = filedialog.askopenfilename(
            title="Sélectionner well_map.py",
            filetypes=[("Python files", "*.py")]
        )
        if not file_path:
            return

        spec = importlib.util.spec_from_file_location("well_map", file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        imported_map = module.well_map

        self.well_map.clear()
        self.cond_colors.clear()
        self.control_conditions.clear()

        for well, info in imported_map.items():
            cond = info.get("condition")
            if cond is None:
                continue
            if cond not in self.well_map:
                self.well_map[cond] = []
            self.well_map[cond].append(well)
            if cond not in self.cond_colors:
                self.cond_colors[cond] = random_color()
            self.control_conditions[cond] = info.get("control_group", False)
            self.update_well_button_color(well, cond)

        self.update_legend()
        silent_info("Import réussi", "Plaque mise à jour.")

    def update_well_button_color(self, well, cond):
        """Met à jour la couleur et le contour selon le type de condition."""
        color = self.cond_colors[cond]
        control = self.control_conditions.get(cond, False)
        if control:
            self.well_buttons[well].config(bg=color, relief="solid", bd=3)
        else:
            self.well_buttons[well].config(bg=color, relief="raised", bd=1)

    def next_window(self):
        self.export_well_map_file
        self.root.destroy()
        root = tk.Tk()
        BackendWindow(root)
        root.mainloop()

    def set_condition(self):
        cond = self.cond_entry.get().strip()
        if not cond:
            silent_warning("Erreur", "Veuillez entrer un nom de condition.")
            return

        self.current_condition = cond
        self.current_control = self.control_var.get()
        self.control_conditions[cond] = self.current_control

        if cond not in self.well_map:
            self.well_map[cond] = []

        if cond not in self.cond_colors:
            self.cond_colors[cond] = random_color()

        self.condition_manager.add_condition(cond)
        self.condition_library = self.condition_manager.get_all()

        self.update_legend()
        silent_info("Condition sélectionnée",
                            f"Vous assignez maintenant les puits à : {cond} "
                            f"{'(Contrôle)' if self.current_control else ''}")

    def assign_well(self, well):
        if self.current_condition is None:
            silent_warning("Condition manquante",
                                   "Veuillez d'abord sélectionner une condition.")
            return

        cond = self.current_condition
        for k, v in self.well_map.items():
            if well in v:
                v.remove(well)
        if well not in self.well_map[cond]:
            self.well_map[cond].append(well)

        self.update_well_button_color(well, cond)
        self.update_legend()

    def unassign_well(self, well):
        for cond, wells in self.well_map.items():
            if well in wells:
                wells.remove(well)
        self.well_buttons[well].config(bg="SystemButtonFace", relief="raised", bd=1)
        self.update_legend()

    def export_well_map_file(self):
        well_to_condition = {
            w: cond
            for cond, wells in self.well_map.items()
            for w in wells
        }

        final_map = {}
        replicate_counter = {}
        for row in ROWS:
            for col in COLS:
                well = f"{row}{col}"
                cond = well_to_condition.get(well, None)
                if cond is None:
                    final_map[well] = {"condition": None, "replicate": None, "control_group": False}
                else:
                    replicate_counter.setdefault(cond, 0)
                    replicate_counter[cond] += 1
                    final_map[well] = {
                        "condition": cond,
                        "replicate": replicate_counter[cond],
                        "control_group": self.control_conditions.get(cond, False)
                    }

        lines = ["well_map = {"]
        for well in sorted(final_map.keys()):
            c = final_map[well]["condition"]
            r = final_map[well]["replicate"]
            cg = final_map[well]["control_group"]
            lines.append(
                f'    "{well}": {{"condition": {repr(c)}, "replicate": {repr(r)}, "control_group": {repr(cg)}}},'
            )
        lines.append("}")

        os.makedirs("./backend", exist_ok=True)
        with open("./backend/well_map.py", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        self.update_legend()
        