import pandas as pd
import itertools
from pathlib import Path

def transform_data(path="../../data/bahn_data"):
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
    This function assumes that the input data is in Parquet format and contains the necessary columns.
    :param path: Path to the directory containing the Bahn data in Parquet format.
    :type path: str
    :return: DataFrame containing the transformed sub-trip data.
    """
    # Datensatz laden
    df = pd.concat(
        [pd.read_parquet(f, engine="pyarrow") for f in sorted(Path(path).glob("*.parquet"))[-4:]],
        ignore_index=True)
    # Nur ICE
    df = df[df['train_type'] == 'ICE']

    # Shape
    print(f"Shape des DataFrames: {df.shape}")

    df['departure_planned_time'] = pd.to_datetime(df['departure_planned_time'], errors='coerce')
    df['arrival_planned_time'] = pd.to_datetime(df['arrival_planned_time'], errors='coerce')

    # Verzögerung an jedem Halt
    df['delay'] = df['delay_in_min']

    # Gruppieren nach train_line_ride_id (jede Gruppe ist eine vollständige Fahrt)
    groups = df.groupby('train_line_ride_id')

    records = []

    for ride_id, group in groups:

        train_name = group['train_name'].iloc[0]

        # Nur Zeilen mit gültiger Zeit und Station verwenden
        valid = group.dropna(subset=['station'])  # Station darf nicht fehlen
        if len(valid) < 2:
            continue  # Mindestens zwei Halte nötig, um Sub-Trips zu bilden

        # Sortierzeitpunkt: fallback von departure auf arrival, falls departure NaT ist
        valid = valid.assign(
            sort_time=valid['departure_planned_time'].fillna(valid['arrival_planned_time'])
        ).sort_values('sort_time')

        # Liste der Stops: jedes Element ist dict mit Station, Zeiten und Delay
        stops = valid[['station', 'departure_planned_time', 'arrival_planned_time', 'delay']].to_dict('records')

        # Alle Kombinationen von Stop i < j zu Sub-Trips machen
        for i, j in itertools.combinations(range(len(stops)), 2):
            origin = stops[i]
            dest = stops[j]

            # Nutze Abfahrtszeit am Origin (oder arrival, falls departure fehlt)
            origin_dt = origin['departure_planned_time'] if pd.notna(origin['departure_planned_time']) else origin[
                'arrival_planned_time']
            day_of_week = origin_dt.dayofweek
            hour_of_day = origin_dt.hour

            records.append({
                'ride_id': ride_id,
                'train_name': train_name,
                'origin_station': origin['station'],
                'destination_station': dest['station'],
                'departure_time_origin': origin_dt,
                'day_of_week': day_of_week,
                'hour_of_day': hour_of_day,
                'delay_at_dest': dest['delay']
            })

    # Neues DataFrame mit allen Sub-Trip-Datensätzen
    df_subtrips = pd.DataFrame(records)

    return df_subtrips