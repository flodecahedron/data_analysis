import tkinter as tk
from tkinter import filedialog

from backend.assign import (
    ROWS, COLS,
    random_color, get_suggestions,
    import_existing_map, export_well_map
)
from backend.condition_manager import ConditionManager
from backend.silent_show import silent_info, silent_warning


class AssignPage(tk.Frame):
    """
    Page d'assignation des conditions aux puits.
    UI 100% front. Aucun traitement back ici.
    """

    def __init__(self, parent, controller):
        super().__init__(parent, bg="#F5F6F7")
        self.controller = controller

        # --- ETAT ---
        self.current_condition = None
        self.current_control = False

        self.well_map = {}         # { condition : [wells] }
        self.cond_colors = {}      # { condition : color }
        self.control_conditions = {}  # { condition : bool }
        self.well_buttons = {}

        # Condition manager (persistant)
        self.condition_manager = ConditionManager()
        self.condition_library = self.condition_manager.get_all()

        self._build_ui()

    # ----------------------------------------------------------------------
    #                            UI BUILD
    # ----------------------------------------------------------------------
    def _build_ui(self):

        # Zone centrale contenant tout
        main = tk.Frame(self, bg="#F5F6F7")
        main.pack(expand=True, pady=20)

        # ---------------- TOP BAR ----------------
        top = tk.Frame(main, bg="#F5F6F7")
        top.pack(pady=10)

        tk.Label(top, text="Nom condition :", bg="#F5F6F7").pack(side=tk.LEFT)

        self.cond_entry = tk.Entry(top, width=20)
        self.cond_entry.pack(side=tk.LEFT, padx=5)
        self.cond_entry.bind("<KeyRelease>", self._update_suggestions)

        # Suggestions auto
        self.suggestion_box = tk.Listbox(top, height=5, width=25)
        self.suggestion_box.pack(side=tk.LEFT, padx=5)
        self.suggestion_box.bind("<<ListboxSelect>>", self._select_suggestion)

        # Groupe contrôle ?
        self.control_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            top, text="Contrôle", bg="#F5F6F7",
            variable=self.control_var
        ).pack(side=tk.LEFT, padx=10)

        # Bouton choisir condition
        tk.Button(
            top, text="Sélectionner", command=self._set_condition
        ).pack(side=tk.LEFT, padx=10)

        # Import
        tk.Button(
            top, text="Importer répartition", command=self._import_map
        ).pack(side=tk.LEFT, padx=10)

        # ---------------- PLATE GRID ----------------
        grid = tk.Frame(main, bg="#F5F6F7")
        grid.pack(side=tk.LEFT, padx=25, pady=10)

        for r, row in enumerate(ROWS):
            for c, col in enumerate(COLS):
                well = f"{row}{col}"
                btn = tk.Button(
                    grid, text=well, width=4,
                    command=lambda w=well: self._assign_well(w)
                )
                btn.grid(row=r, column=c, padx=2, pady=2)
                btn.bind("<Button-3>", lambda e, w=well: self._unassign_well(w))
                self.well_buttons[well] = btn

        # ---------------- LEGEND ----------------
        self.legend_frame = tk.Frame(main, bg="#F5F6F7")
        self.legend_frame.pack(side=tk.LEFT, padx=25)
        self.legend_labels = {}

        # ---------------- NEXT ----------------
        tk.Button(
            self, text="Poursuivre", bg="#88ccee",
            command=self._go_next
        ).pack(pady=25)

    # ----------------------------------------------------------------------
    #                            UI LOGIC
    # ----------------------------------------------------------------------

    def _update_suggestions(self, event=None):
        typed = self.cond_entry.get().strip()
        self.suggestion_box.delete(0, tk.END)

        for s in get_suggestions(typed, self.condition_library):
            self.suggestion_box.insert(tk.END, s)

    def _select_suggestion(self, event):
        if not self.suggestion_box.curselection():
            return
        idx = self.suggestion_box.curselection()[0]
        chosen = self.suggestion_box.get(idx)
        self.cond_entry.delete(0, tk.END)
        self.cond_entry.insert(0, chosen)

    def _set_condition(self):
        cond = self.cond_entry.get().strip()
        if not cond:
            return silent_warning("Erreur", "Entrez un nom de condition.")

        self.current_condition = cond
        self.current_control = self.control_var.get()
        self.control_conditions[cond] = self.current_control

        if cond not in self.well_map:
            self.well_map[cond] = []

        if cond not in self.cond_colors:
            self.cond_colors[cond] = random_color()

        self.condition_manager.add_condition(cond)
        self.condition_library = self.condition_manager.get_all()

        self._update_legend()
        silent_info("OK", f"Condition active : {cond}")

    # ----------------------------------------------------------------------

    def _assign_well(self, well):
        if not self.current_condition:
            return silent_warning("Erreur", "Sélectionnez une condition.")

        cond = self.current_condition

        # Retirer ce puits d'autres conditions
        for k in self.well_map:
            if well in self.well_map[k]:
                self.well_map[k].remove(well)

        # Ajouter au bon groupe
        if well not in self.well_map[cond]:
            self.well_map[cond].append(well)

        self._refresh_button(well, cond)
        self._update_legend()

    def _unassign_well(self, well):
        for cond in self.well_map:
            if well in self.well_map[cond]:
                self.well_map[cond].remove(well)

        self.well_buttons[well].config(bg="SystemButtonFace")
        self._update_legend()

    # ----------------------------------------------------------------------

    def _refresh_button(self, well, cond):
        color = self.cond_colors[cond]
        is_ctrl = self.control_conditions.get(cond, False)

        self.well_buttons[well].config(
            bg=color,
            relief="solid" if is_ctrl else "raised",
            bd=3 if is_ctrl else 1
        )

    # ----------------------------------------------------------------------

    def _update_legend(self):
        for w in self.legend_frame.winfo_children():
            w.destroy()

        for cond, col in self.cond_colors.items():
            txt = cond + (" (Ctrl)" if self.control_conditions.get(cond) else "")
            tk.Label(self.legend_frame, text=txt, bg=col, width=20).pack(pady=2)

    # ----------------------------------------------------------------------

    def _import_map(self):
        path = filedialog.askopenfilename(
            title="Choisir well_map.py",
            filetypes=[("Python", "*.py")]
        )
        if not path:
            return

        loaded = import_existing_map(path)

        # Reset
        self.well_map.clear()
        self.cond_colors.clear()
        self.control_conditions.clear()

        # Reconstruction
        for well, info in loaded.items():
            cond = info.get("condition")
            if not cond:
                continue

            self.well_map.setdefault(cond, []).append(well)

            if cond not in self.cond_colors:
                self.cond_colors[cond] = random_color()

            self.control_conditions[cond] = info.get("control_group", False)

            self._refresh_button(well, cond)

        self._update_legend()
        silent_info("OK", "Plaque importée.")

    # ----------------------------------------------------------------------

    def _go_next(self):
        """Export + navigation."""
        final = {}

        replicate = {}
        for row in ROWS:
            for col in COLS:
                well = f"{row}{col}"
                cond = None

                for c, wells in self.well_map.items():
                    if well in wells:
                        cond = c
                        break

                if cond:
                    replicate.setdefault(cond, 0)
                    replicate[cond] += 1

                    final[well] = {
                        "condition": cond,
                        "replicate": replicate[cond],
                        "control_group": self.control_conditions.get(cond, False)
                    }
                else:
                    final[well] = {
                        "condition": None,
                        "replicate": None,
                        "control_group": False
                    }

        export_well_map(final)

        # Stockage global
        #self.controller.set_state("well_map", final)

        self.controller.show_frame("RunPage")

    # ----------------------------------------------------------------------

    def on_show(self):
        """Hook appelé lorsqu'on arrive sur la page."""
        pass
