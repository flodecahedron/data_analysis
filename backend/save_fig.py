import os
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from collections import defaultdict
import numpy as np

def parse_condition(cond):
    """
    Sépare une condition du type 'COL7A1-R 20ng'
    -> ('COL7A1-R', 20)
    Si aucune concentration n'est trouvée, retourne (cond, None).
    """
    if cond is None:
        return None, None

    parts = cond.split()
    if len(parts) < 2:
        return cond, None

    base = " ".join(parts[:-1])
    value = parts[-1]

    try:
        # gère ng ou pg → converti tout en nombre
        number = float(value.replace("ng", "").replace("pg", ""))
    except:
        return cond, None

    return base, number


def save_fig(results_csv, well_map, plate_name):
    """
    Génère les figures :
    - contrôle en noir
    - groupes colorés avec gradient selon concentration
    - légende ordonnée selon concentration
    """

    output_dir = os.path.join(plate_name, "figures")
    os.makedirs(output_dir, exist_ok=True)

    # --- Détection des contrôles --- #
    control_groups = sorted({info['condition'] 
                             for info in well_map.values()
                             if info.get('control_group', False)})

    all_conditions = [c for c in results_csv['Condition'].unique() if c is not None]

    # --- Regroupement par base de condition --- #
    grouped = defaultdict(list)   # ex : "COL7A1-R": ["COL7A1-R 20ng", "COL7A1-R 50ng"]
    parsed = {}                   # cache parsing

    for cond in all_conditions:
        base, conc = parse_condition(cond)
        parsed[cond] = (base, conc)
        if base:
            grouped[base].append(cond)

    # Ajouter un groupe ALL
    grouped["ALL"] = all_conditions

    # --- Génération des figures --- #
    for group_name, conds in grouped.items():

        plt.figure(figsize=(10, 7))

        # Ajouter tous les contrôles à chaque figure
        plot_conditions = conds + [c for c in control_groups if c not in conds]

        # ---- Génération des couleurs par groupe ---- #
        # pour les conditions non-contrôles :
        non_ctrl = [c for c in plot_conditions if c not in control_groups]
        base = parsed[non_ctrl[0]][0] if non_ctrl else None

        # Si plusieurs concentrations → gradient
        if base and len(grouped[base]) > 1:
            # valeurs de concentration triées
            cond_vals = [(c, parsed[c][1]) for c in grouped[base]]
            cond_vals = [(c, v) for c, v in cond_vals if v is not None]
            cond_vals = sorted(cond_vals, key=lambda x: x[1])

            concentrations = np.array([v for _, v in cond_vals])
            cmin, cmax = concentrations.min(), concentrations.max()

            def get_color_from_conc(val):
                # Gradient du bleu clair au bleu foncé
                ratio = (val - cmin) / (cmax - cmin + 1e-6)
                return cm.Blues(0.4 + 0.5 * ratio)

            color_map = {c: get_color_from_conc(v) for c, v in cond_vals}

        else:
            # fallback normal : couleurs tab20
            fallback = cm.get_cmap("tab20", len(plot_conditions))
            color_map = {c: fallback(i) for i, c in enumerate(plot_conditions)}

        # --- Tracé des courbes --- #
        for cond in plot_conditions:

            data = results_csv[results_csv["Condition"] == cond]
            if data.empty:
                continue

            # style pour contrôles
            if cond in control_groups:
                plt.errorbar(
                    data["Time_h"], data["mean"], yerr=data["std"],
                    label=f"[CTRL] {cond}",
                    color="black",
                    marker="s",
                    markersize=7,
                    linestyle="--",
                    linewidth=2.8,
                    capsize=4
                )
            else:
                base, conc = parsed[cond]
                color = color_map.get(cond, "grey")

                plt.errorbar(
                    data["Time_h"], data["mean"], yerr=data["std"],
                    label=f"{cond}",
                    color=color,
                    marker="o",
                    markersize=6,
                    linestyle="-",
                    linewidth=2,
                    capsize=4
                )

        # Ticks & axes
        max_time = max(results_csv["Time_h"])
        plt.xlim(0, max_time)
        plt.ylim(0, 100)

        plt.grid(True, alpha=0.3)
        plt.xlabel("Temps [h]", fontsize=14)
        plt.ylabel("Fermeture moyenne [%]", fontsize=14)
        plt.title(f"Évolution de la fermeture moyenne – {group_name}", fontsize=16)

        # Légende : triée par concentration
        handles, labels = plt.gca().get_legend_handles_labels()

        def sort_key(label):
            if "CTRL" in label:
                return (0, -999)
            name = label.replace("[CTRL] ", "")
            b, c = parse_condition(name)
            return (1, c or 0)

        sorted_pairs = sorted(zip(handles, labels), key=lambda x: sort_key(x[1]))
        handles, labels = zip(*sorted_pairs)
        plt.legend(handles, labels, fontsize=11, frameon=True)

        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"fermeture_{group_name}.png"), dpi=300)
        plt.close()

    return True
