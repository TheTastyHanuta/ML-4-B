import pandas as pd
from datetime import datetime

def map_weather(bahn: pd.DataFrame, weather: pd.DataFrame) -> pd.DataFrame:
    """
    Map weather data to Bahn sub-trips.
    This function takes Bahn sub-trip data and weather data, and maps the weather conditions to each sub-trip based on the departure time and location.
    The function returns a DataFrame with the following columns:
    - ride_id: Unique identifier for the sub-trip
    - train_name: Name of the train
    - origin_station: Name of the origin station
    - destination_station: Name of the destination station
    - departure_time_origin: Planned departure time at the origin station
    - day_of_week: Day of the week of the departure
    - hour_of_day: Hour of the day of the departure
    - delay_at_dest: Delay at the destination station in minutes
    - weather_conditions: Weather conditions at the origin station at the time of departure
    This function assumes that the input data is in DataFrame format and contains the necessary columns.
    :param bahn: DataFrame containing Bahn sub-trip data with necessary columns.
    :type bahn: pd.DataFrame
    :param weather: DataFrame containing weather data with necessary columns.
    :type weather: pd.DataFrame
    :rtype: pd.DataFrame
    :return: DataFrame containing Bahn sub-trip data with mapped weather conditions.
    """

    # Convert time columns to datetime
    bahn['departure_time_origin'] = pd.to_datetime(bahn['departure_time_origin'])
    weather['time'] = pd.to_datetime(weather['time'])

    # Round the time to the nearest hour for both DataFrames
    bahn['time_hour'] = bahn['departure_time_origin'].dt.floor('H')
    weather['time_hour'] = weather['time']

    print("Subtrips:", bahn['departure_time_origin'].min(), "bis", bahn['departure_time_origin'].max())
    print("Weather:  ", weather['time'].min(), "bis", weather['time'].max())

    # Rename columns for clarity
    bahn = bahn.rename(columns={'origin_station': 'station'})

    # Inner join the Bahn and weather DataFrames on station and time_hour
    merged = pd.merge(bahn, weather, on=['station', 'time_hour'], how='left')

    print(f"Anzahl weather original: {len(weather)}")
    print(f"Anzahl subtrips original: {len(bahn)}")
    print(f"Anzahl Zeilen nach Merge:  {len(merged)}")

    missing_weather = merged['temp_celsius'].isna().sum()
    print(f"Subtrips ohne passenden Wetter-Eintrag: {missing_weather}")

    # ToDo: Maybe i can make it work so that the weather data is also available for the destination station

    return merged