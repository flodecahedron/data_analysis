import os
import re
import pandas as pd

def parse_condition(cond):
    """
    Parse 'COL7A1-R 20ng' -> (main_group='COL7A1', subgroup='COL7A1-R', concentration=20.0)
    If parsing fails, returns (cond, cond, None)
    """
    if cond is None:
        return None, None, None
    parts = str(cond).split()
    subgroup = parts[0]
    main_group = subgroup.split("-")[0] if "-" in subgroup else subgroup
    concentration = None
    if len(parts) > 1:
        m = re.search(r"(\d+\.?\d*)", parts[-1])
        if m:
            try:
                concentration = float(m.group(1))
            except:
                concentration = None
    return main_group, subgroup, concentration


def save_excel(results_csv, well_map, plate_name):
    """
    Export grouped Excel with real error bars using XlsxWriter.
    - results_csv: DataFrame with columns ['Condition','Time_h','mean','std']
    - well_map: dict with keys wells -> {'condition', 'replicate', 'control_group'}
    - plate_name: folder/name prefix
    Returns path to created file.
    """

    # output paths
    out_dir = os.path.join(plate_name, "excel")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, f"{plate_name}_grouped.xlsx")

    # detect control groups from well_map
    control_groups = sorted({
        info["condition"] for info in well_map.values()
        if info.get("control_group", False) and info.get("condition") is not None
    })

    # two clearly distinct colors for controls
    control_palette = ["#000000", "#555555"]  # noir + gris foncé

    # parse
    unique_conditions = [c for c in results_csv["Condition"].unique() if c is not None]
    parsed = {c: parse_condition(c) for c in unique_conditions}

    # group by main_group
    groups = {}
    for cond, (main, sub, conc) in parsed.items():
        if main is None:
            continue
        groups.setdefault(main, []).append(cond)

    with pd.ExcelWriter(out_file, engine='xlsxwriter') as writer:
        workbook = writer.book

        base_color_hex = [
            "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
            "#9467bd", "#8c564b", "#e377c2", "#7f7f7f"
        ]

        for main_group, conds in sorted(groups.items()):
            sheet_name = str(main_group)[:31]
            ws = workbook.add_worksheet(sheet_name)
            row_cursor = 0

            chart = workbook.add_chart({'type': 'line'})
            chart.set_title({'name': f"{main_group} – Closing curves"})
            chart.set_x_axis({'name': 'Time [h]'})
            chart.set_y_axis({'name': 'Closure [%]'})
            chart.set_legend({'position': 'right'})

            subgroups = {}
            for cond in conds:
                _, subgroup, conc = parsed[cond]
                subgroups.setdefault(subgroup, []).append((cond, conc))

            for sub in subgroups:
                subgroups[sub].sort(key=lambda x: (x[1] is None, x[1]))

            # test solutions
            for s_idx, (subgroup, cond_list) in enumerate(sorted(subgroups.items())):
                base_color = base_color_hex[s_idx % len(base_color_hex)]

                def hex_to_rgb(h):
                    h = h.lstrip('#')
                    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

                def rgb_to_hex(rgb):
                    return "#{:02x}{:02x}{:02x}".format(*[max(0,min(255,int(v))) for v in rgb])

                n = max(1, len(cond_list))

                for i, (cond, conc) in enumerate(cond_list):

                    rgb = hex_to_rgb(base_color)
                    ratio = i / max(1, n-1) if n > 1 else 0.0
                    dark_rgb = tuple(int((1 - 0.5 * ratio) * c) for c in rgb)
                    color_hex = rgb_to_hex(dark_rgb)

                    dfc = results_csv[results_csv["Condition"] == cond].sort_values("Time_h")
                    if dfc.empty:
                        continue

                    ws.write(row_cursor, 0, cond)
                    row_cursor += 1
                    ws.write_row(row_cursor, 0, ["Time_h", "mean", "std"])
                    row_cursor += 1
                    start_row = row_cursor + 1

                    for _, r in dfc.iterrows():
                        ws.write_number(row_cursor, 0, float(r["Time_h"]) if not pd.isna(r["Time_h"]) else None)
                        ws.write_number(row_cursor, 1, float(r["mean"]) if not pd.isna(r["mean"]) else None)
                        ws.write_number(row_cursor, 2, float(r["std"]) if not pd.isna(r["std"]) else None)
                        row_cursor += 1

                    end_row = row_cursor

                    cat = f"='{sheet_name}'!$A${start_row}:$A${end_row}"
                    vals = f"='{sheet_name}'!$B${start_row}:$B${end_row}"
                    errs = f"='{sheet_name}'!$C${start_row}:$C${end_row}"

                    chart.add_series({
                        'name': cond,
                        'categories': cat,
                        'values': vals,
                        'y_error_bars': {
                            'type': 'custom',
                            'plus_values': errs,
                            'minus_values': errs
                        },
                        'line': {'color': color_hex, 'width': 2.0},
                        'marker': {
                            'type': 'circle',
                            'size': 5,
                            'border': {'color': color_hex},
                            'fill': {'color': color_hex}
                        }
                    })

                    row_cursor += 1

            # CONTROL groups
            for i, ctrl in enumerate(control_groups):
                dfc = results_csv[results_csv["Condition"] == ctrl].sort_values("Time_h")
                if dfc.empty:
                    continue

                ws.write(row_cursor, 0, ctrl + " (control)")
                row_cursor += 1
                ws.write_row(row_cursor, 0, ["Time_h", "mean", "std"])
                row_cursor += 1
                start_row = row_cursor + 1

                for _, r in dfc.iterrows():
                    ws.write_number(row_cursor, 0, float(r["Time_h"]) if not pd.isna(r["Time_h"]) else None)
                    ws.write_number(row_cursor, 1, float(r["mean"]) if not pd.isna(r["mean"]) else None)
                    ws.write_number(row_cursor, 2, float(r["std"]/2) if not pd.isna(r["std"]/2) else None)
                    row_cursor += 1

                end_row = row_cursor

                cat = f"='{sheet_name}'!$A${start_row}:$A${end_row}"
                vals = f"='{sheet_name}'!$B${start_row}:$B${end_row}"
                errs = f"='{sheet_name}'!$C${start_row}:$C${end_row}"

                control_color = control_palette[i % len(control_palette)]

                chart.add_series({
                    'name': ctrl + " (control)",
                    'categories': cat,
                    'values': vals,
                    'y_error_bars': {
                        'type': 'custom',
                        'plus_values': errs,
                        'minus_values': errs
                    },
                    'line': {'color': control_color, 'width': 2.5},
                    'marker': {
                        'type': 'square',
                        'size': 6,
                        'border': {'color': control_color},
                        'fill': {'color': control_color}
                    }
                })

            ws.insert_chart('F2', chart, {'x_scale': 1.4, 'y_scale': 1.1})

    return out_file
