import pandas as pd
import itertools
from pathlib import Path

def transform_bahn(path: Path) -> pd.DataFrame | None:
    """
    Transform the Bahn data to extract sub-trips from the train rides.
    This function processes the Bahn data, extracts sub-trips, and returns a DataFrame with the following columns:
    - ride_id: Unique identifier for the train ride
    - train_name: Name of the train
    - origin_station: Name of the origin station
    - destination_station: Name of the destination station
    - departure_time_origin: Planned departure time at the origin station
    - day_of_week: Day of the week of the departure
    - hour_of_day: Hour of the day of the departure
    - delay_at_dest: Delay at the destination station in minutes
    - canceled: Boolean indicating if the sub-trip was canceled
    This function assumes that the input data is in Parquet format and contains the necessary columns.
    :param path: Path to the directory containing the Bahn data in Parquet format.
    :type path: str
    :return: DataFrame containing the transformed sub-trip data.
    """

    print(f"Processing Bahn data from path: {path}")
    if not path.exists():
        print(f"Path {path} does not exist. Please check the path and try again.")
        return None

    df = pd.concat(
        [pd.read_parquet(f, engine="pyarrow") for f in sorted(Path(path).glob("*.parquet"))],
        ignore_index=True)
    # Only ICE and IC
    df = df[df['train_type'].isin(['ICE', 'IC'])]

    print(f"Shape des Bahn Dataframes nur mit ICE und IC: {df.shape}")

    df['departure_planned_time'] = pd.to_datetime(df['departure_planned_time'], errors='coerce')
    df['arrival_planned_time'] = pd.to_datetime(df['arrival_planned_time'], errors='coerce')

    df['delay'] = df['delay_in_min']

    groups = df.groupby('train_line_ride_id')

    records = []

    for ride_id, group in groups:
        train_name = group['train_name'].iloc[0]

        valid = group.dropna(subset=['station'])
        if len(valid) < 2:
            continue

        valid = valid.assign(
            sort_time=valid['departure_planned_time'].fillna(valid['arrival_planned_time'])
        ).sort_values('sort_time')

        # Use 'is_canceled' column, default to False if missing
        if 'is_canceled' in valid.columns:
            stops = valid[['station', 'departure_planned_time', 'arrival_planned_time', 'delay', 'is_canceled']].to_dict('records')
        else:
            stops = valid[['station', 'departure_planned_time', 'arrival_planned_time', 'delay']].copy()
            stops['is_canceled'] = False
            stops = stops.to_dict('records')

        for i, j in itertools.combinations(range(len(stops)), 2):
            origin = stops[i]
            dest = stops[j]

            origin_dt = origin['departure_planned_time'] if pd.notna(origin['departure_planned_time']) else origin['arrival_planned_time']
            day_of_week = origin_dt.dayofweek
            hour_of_day = origin_dt.hour

            subtrip_canceled = bool(origin.get('is_canceled', False)) or bool(dest.get('is_canceled', False))

            records.append({
                'ride_id': ride_id,
                'train_name': train_name,
                'origin_station': origin['station'],
                'destination_station': dest['station'],
                'departure_time_origin': origin_dt,
                'day_of_week': day_of_week,
                'hour_of_day': hour_of_day,
                'delay_at_dest': dest['delay'],
                'canceled': subtrip_canceled
            })

    df_subtrips = pd.DataFrame(records)

    print(f"Shape des neuen Sub-Trips DataFrames: {df_subtrips.shape}")

    return df_subtrips