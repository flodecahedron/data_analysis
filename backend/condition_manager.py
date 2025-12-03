import json
import os

DEFAULT_CONDITIONS = [
    "DMEM vide", "DMEM+SVF",
    "COL1", "COL3", "COL10",
    "NRP1-L", "NRP1-H",
    "PTX-1", "PTX-10",
    "VEGFA-10", "VEGFA-50"
]

class ConditionManager:
    def __init__(self, json_path="./data/conditions.json"):
        self.json_path = json_path

        # si dossier data/ n'existe pas → créer
        os.makedirs(os.path.dirname(json_path), exist_ok=True)

        # charger ou créer
        self.conditions = self.load_conditions()

    def load_conditions(self):
        """Charge conditions depuis JSON. Sinon crée un fichier par défaut."""
        if not os.path.exists(self.json_path):
            self.save_conditions(DEFAULT_CONDITIONS.copy())
            return DEFAULT_CONDITIONS.copy()

        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("conditions", DEFAULT_CONDITIONS.copy())
        except:
            return DEFAULT_CONDITIONS.copy()

    def save_conditions(self, cond_list):
        """Écrit la liste complète dans le JSON."""
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump({"conditions": cond_list}, f, indent=4)

    def add_condition(self, cond):
        """Ajoute une condition et sauvegarde, sans doublon."""
        cond = cond.strip()
        if cond and cond not in self.conditions:
            self.conditions.append(cond)
            self.save_conditions(self.conditions)

    def get_all(self):
        return self.conditions
