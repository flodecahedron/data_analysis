import os
import pandas as pd

def data_preprocessing(filepath):
        '''Find the plate name and the line where the data begins to skip header'''
        
        plate_name = "unknown_name"
        start = None

        with open(filepath, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                
                try:
                    if line.split()[0] == 'Plate':
                        plate_name = line.split()[-1]
                except:
                     None
                
                if line.strip() == "[Data]": # Expected to start after [Data] header
                    start = i + 1
                    break

        if start is None:
            raise ValueError("Impossible d'identifier où le tableau de données débute dans le fichier")

        return start,plate_name

def data_processing(filepath, well_map, start, plate_name):
    '''
    Extract and process the data from the txt file according to the given well map &
    Export data into two csv file: 
        - 'results_sorted.csv' containing the relevant data (see 'cols' list)
        - 'results_plot.csv' which will be used to plot the figures (mean and std against time for each condition)
    '''
    output_dir = plate_name + "/csv"

    # Data load
    df = pd.read_csv(
        filepath,
        sep="\t",
        skiprows=start,
        engine="python"
    )

    ## Robustly rename columns
    df=df.copy()
    columns = df.columns

    # Identify area column
    area_col = None
    for col in columns:
        if "Area" in col:
            area_col = col
            break

    if area_col is None:
        raise ValueError("Aucune colonne contenant 'Area' ou 'µm²' trouvée dans les données")

    # Identify time column
    time_col = None
    for col in columns:
        if "Time [s]" in col:
            time_col = col
            break

    if time_col is None:
        raise ValueError("Aucune colonne contenant 'Time' trouvée dans les données")

    # Rename columns consistently
    df = df.rename(columns={
        area_col: "Area_um2",
        time_col: "Time_s"
    })

    ## Create results data
    # Well
    df["Well"] = df.apply(
        lambda x: f"{chr(ord('A') + int(x['Row']) - 1)}{x['Column']}",
        axis=1
    )

    # Well information
    df["Condition"] = df["Well"].map(lambda w: well_map.get(w, {}).get("condition"))
    df["Replicate"] = df["Well"].map(lambda w: well_map.get(w, {}).get("replicate"))

    # Time in hours
    df['Time_s'] = df['Time_s'].round().astype(int)
    df["Time_h"] = (df["Time_s"]/3600).round().astype(int)

    # Area_t0 (Time_s = 0)
    Area_t0 = df[df["Time_s"] == 0].set_index("Well")["Area_um2"]
    df["Area_t0"] = df["Well"].map(Area_t0)

    # %Closure
    df["Closure"] = 100 * (df["Area_t0"] - df["Area_um2"]) / df["Area_t0"]
    df["Closure"] = df["Closure"].clip(lower=0)

    # Sort 
    cols = [
        "Row", "Column", "Well", 
        "Condition", "Replicate",
        "Time_s", "Time_h", 
        "Area_t0", "Area_um2", "Closure"
    ]

    df = df.sort_values(by=['Well', 'Time_h'], ascending=[True, True])

    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "results_sorted.csv")
    df[cols].to_csv(output_file, index=False, encoding="utf-8")

    ## Calculate mean and standard deviation
    df = df.groupby(['Condition', 'Time_h'])['Closure']

    df = df.agg(['mean', 'std']).reset_index()

    # Sort by condition and ascending time
    df = df.sort_values(by=['Condition', 'Time_h'])

    output_file = os.path.join(output_dir, "results_plot.csv")
    df.to_csv(output_file, index=False, encoding="utf-8")

    return df