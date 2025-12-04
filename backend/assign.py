import random
import importlib.util
import difflib
import os

ROWS = ["A","B","C","D","E","F","G","H"]
COLS = [str(i) for i in range(1,13)]


def random_color():
    """Couleur lisible aléatoire."""
    return "#%06x" % random.randint(0x444444, 0xFFFFFF)


# ----------------------------------------------------------------------
#   TRAITEMENT DES CONDITIONS
# ----------------------------------------------------------------------

def get_suggestions(typed: str, library: list):
    """Retourne les conditions ressemblantes."""
    if not typed:
        return []
    return difflib.get_close_matches(typed, library, n=5, cutoff=0.1)


# ----------------------------------------------------------------------
#   IMPORT WELL_MAP
# ----------------------------------------------------------------------

def import_existing_map(path: str):
    """
    Charge un fichier Python well_map.py existant.
    Retourne le dict {well: {...}}.
    """
    spec = importlib.util.spec_from_file_location("well_map", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.well_map


# ----------------------------------------------------------------------
#   EXPORT WELL_MAP
# ----------------------------------------------------------------------

def export_well_map(final_map: dict, output_path="./backend/well_map.py"):
    """Écrit un fichier Python well_map.py standardisé."""
    lines = ["well_map = {"]
    for well in sorted(final_map.keys()):
        info = final_map[well]
        lines.append(
            f'    "{well}": {{"condition": {repr(info["condition"])}, '
            f'"replicate": {repr(info["replicate"])}, '
            f'"control_group": {repr(info["control_group"])}}},'
        )
    lines.append("}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
