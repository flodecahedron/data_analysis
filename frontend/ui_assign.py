import tkinter as tk
from tkinter import filedialog

from backend.assign import (
    ROWS, COLS,
    random_color, get_suggestions,
    import_existing_map, export_well_map
)
from backend.condition_manager import ConditionManager

class AssignPage(tk.Frame):
    """
    Assign conditions to wells.
    All feedback appears directly in the page (no pop-ups).
    """

    def __init__(self, parent, controller):
        super().__init__(parent, bg="#F5F6F7")
        self.controller = controller

        # --- State ---
        self.current_condition = None
        self.current_control = False
        self.well_map = {}
        self.cond_colors = {}
        self.control_conditions = {}
        self.well_buttons = {}

        # Condition manager
        self.condition_manager = ConditionManager()
        self.condition_library = self.condition_manager.get_all()

        self._build_ui()

        # --- Status label at bottom ---
        self.status_label = tk.Label(
            self, text="", bg="#F5F6F7", fg="#333", font=("Segoe UI", 10)
        )
        self.status_label.pack(pady=(5, 5), fill="x")

        # --- Poursuivre button ---
        self.next_btn = tk.Button(self, text="Poursuivre", bg="#072939",fg="white", command=self._go_next)
        self.next_btn.pack(pady=(0, 15))

    # ----------------------------------------------------------------------
    #                            UI BUILD
    # ----------------------------------------------------------------------
    def _build_ui(self):
        main = tk.Frame(self, bg="#F5F6F7")
        main.pack(expand=True, fill="both", padx=20, pady=20)

        # --- Left frame: assign conditions ---
        assign_frame = tk.Frame(main, bg="#F5F6F7")
        assign_frame.pack(side="left", fill="both", expand=True)

        tk.Label(assign_frame, text="Assigner les conditions à la plaque", 
                 font=("Segoe UI", 12, "bold"), bg="#F5F6F7",fg="#072939").pack(pady=(0,10))

        top = tk.Frame(assign_frame, bg="#F5F6F7")
        top.pack(pady=5)

        tk.Label(top, text="Nom condition :", bg="#F5F6F7").pack(side=tk.LEFT)
        self.cond_entry = tk.Entry(top, width=20)
        self.cond_entry.pack(side=tk.LEFT, padx=5)
        self.cond_entry.bind("<KeyRelease>", self._update_suggestions)

        self.suggestion_box = tk.Listbox(top, height=5, width=25)
        self.suggestion_box.pack(side=tk.LEFT, padx=5)
        self.suggestion_box.bind("<<ListboxSelect>>", self._select_suggestion)

        self.control_var = tk.BooleanVar(value=False)
        tk.Checkbutton(top, text="Contrôle", bg="#F5F6F7",
                       variable=self.control_var).pack(side=tk.LEFT, padx=5)

        tk.Button(top, text="Sélectionner", command=self._set_condition, bg="#072939", fg="white").pack(side=tk.LEFT, padx=5)

        # Plate grid
        grid = tk.Frame(assign_frame, bg="#F5F6F7")
        grid.pack(pady=10)

        for r, row in enumerate(ROWS):
            for c, col in enumerate(COLS):
                well = f"{row}{col}"
                btn = tk.Button(grid, text=well, width=4,
                                command=lambda w=well: self._assign_well(w))
                btn.grid(row=r, column=c, padx=2, pady=2)
                btn.bind("<Button-3>", lambda e, w=well: self._unassign_well(w))
                self.well_buttons[well] = btn

        # --- Separator ---
        sep = tk.Frame(main, width=2, bg="#072939")
        sep.pack(side="left", fill="y", padx=10)

        # --- Right frame: import existing plaque ---
        import_frame = tk.Frame(main, bg="#F5F6F7")
        import_frame.pack(side="left", fill="both", expand=True)

        tk.Label(import_frame, text="Importer une plaque existante",
                 font=("Segoe UI", 12, "bold"), bg="#F5F6F7", fg="#072939").pack(pady=(0,10))

        tk.Button(import_frame, text="Importer", bg="#072939", fg="white", command=self._import_map).pack(pady=(0,15))

        # Legend
        tk.Label(import_frame, text="Légende", font=("Segoe UI", 10, "bold"), bg="#F5F6F7", fg="#072939").pack()
        self.legend_frame = tk.Frame(import_frame, bg="#F5F6F7")
        self.legend_frame.pack(pady=5)
        self.legend_labels = {}

    # ----------------------------------------------------------------------
    #                            UI LOGIC
    # ----------------------------------------------------------------------
    def _set_status(self, message: str, warning: bool = False):
        color = "#cc0000" if warning else "#006600"
        self.status_label.config(text=message, fg=color, anchor="w")

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
            return self._set_status("Entrer un nom de condition.", warning=True)

        self.current_condition = cond
        self.current_control = self.control_var.get()
        self.control_conditions[cond] = self.current_control

        self.well_map.setdefault(cond, [])
        self.cond_colors.setdefault(cond, random_color())

        self.condition_manager.add_condition(cond)
        self.condition_library = self.condition_manager.get_all()

        self._update_legend()
        self._set_status(f"Condition active: {cond}", warning=False)

    def _assign_well(self, well):
        if not self.current_condition:
            return self._set_status("Sélectionnez d'abord une condition.", warning=True)
        cond = self.current_condition
        for k in self.well_map:
            if well in self.well_map[k]:
                self.well_map[k].remove(well)
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

    def _refresh_button(self, well, cond):
        color = self.cond_colors[cond]
        is_ctrl = self.control_conditions.get(cond, False)
        self.well_buttons[well].config(
            bg=color,
            relief="solid" if is_ctrl else "raised",
            bd=3 if is_ctrl else 1
        )

    def _update_legend(self):
        for w in self.legend_frame.winfo_children():
            w.destroy()
        for cond, col in self.cond_colors.items():
            txt = cond + (" (Ctrl)" if self.control_conditions.get(cond) else "")
            tk.Label(self.legend_frame, text=txt, bg=col, width=20).pack(pady=2)

    def _import_map(self):
        path = filedialog.askopenfilename(
            title="Choisir un fichier de plaque existant",
            filetypes=[("Python", "*.py")]
        )
        if not path:
            return

        loaded = import_existing_map(path)

        self.well_map.clear()
        self.cond_colors.clear()
        self.control_conditions.clear()

        for well, info in loaded.items():
            cond = info.get("condition")
            if not cond:
                continue
            self.well_map.setdefault(cond, []).append(well)
            self.cond_colors.setdefault(cond, random_color())
            self.control_conditions[cond] = info.get("control_group", False)
            self._refresh_button(well, cond)

        self._update_legend()
        self._set_status("Plaque importée avec succès.", warning=False)

    def _go_next(self):
        """Export + navigate to next page."""
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
        # self.controller.set_state("well_map", final)
        self.controller.show_frame("RunPage")

    def on_show(self):
        """Optional hook when page is shown."""
        pass
