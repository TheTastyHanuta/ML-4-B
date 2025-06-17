import json
from pathlib import Path
import pandas as pd

data_dir = "../../../data/bahn_data"
save_dir = "../../../data/streamlit_data/stations"

# Load data from parquet files
data_dir = Path(data_dir)
print(f"Reading data from {data_dir}")
files = sorted(data_dir.glob("*.parquet"))
df_list = [pd.read_parquet(fp)[["delay_in_min", "station", "is_canceled", "train_type"]] for fp in files]
df = pd.concat(df_list, ignore_index=True)

# Process data for different train types
for train_type in ["all", "ICE", "IC", "RE", "RB", "S"]:
    # Set up the title and filter data if necessary
    title = "Durchschnittliche Verspätungen an Bahnhöfen und Anzahl an Halten"
    if train_type == "all":
        df_train_type = df
    else:
        df_train_type = df[df["train_type"] == train_type]
        title = f"[{train_type}] {title}"

    # Calculate average delays and stop counts for each station
    station_df = (
        df_train_type[~df_train_type["is_canceled"]]
        .groupby("station")["delay_in_min"]
        .agg(["mean"])
        .reset_index()
        .sort_values("mean", ascending=False)
        .reset_index(drop=True)
    )
    station_df.columns = ["station", "average_delay"]

    # Calculate cancellation rates and sample sizes for each station
    cancellation_sample_size_df = (
        df_train_type.groupby("station")
        .agg({"is_canceled": "mean", "station": "size"})
        .rename(
            columns={
                "is_canceled": "cancellation_rate",
                "station": "sample_size",
            }
        )
    )

    # Combine all statistics for each station
    station_df = station_df.merge(cancellation_sample_size_df, on="station")

    # Rename columns for clarity
    station_df.columns = [
        "Bahnhof",
        "Durchschnittliche Verspätung [min]",
        "Ausfallquote [%]",
        "Stichprobengröße",
    ]

    # Round values for better readability
    station_df["Ausfallquote [%]"] = station_df["Ausfallquote [%]"] * 100
    station_df["Ausfallquote [%]"] = station_df["Ausfallquote [%]"].round(2)
    station_df["Durchschnittliche Verspätung [min]"] = station_df["Durchschnittliche Verspätung [min]"].round(2)
    station_df["Stichprobengröße"] = station_df["Stichprobengröße"].astype(int)

    station_df.sort_values("Durchschnittliche Verspätung [min]")

    # Convert the results to JSON and save to a file
    json_data = station_df.to_json(orient="records", force_ascii=False)
    save_path = Path(save_dir) / f"{title}.json"
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(json_data)
