import json
from pathlib import Path
import pandas as pd
from datetime import datetime
import streamlit as st
from src.ml_models.predict import CAT_FEATURES, ALL_FEATURES, ALL_FEATURES_NO_WEATHER, canceled_model_with_weather, \
    canceled_model_without_weather, model_with_weather, model_without_weather
import requests

base_dir = Path(__file__).parent.parent.parent.parent
data_dir = base_dir / "data" / "streamlit_data"

# Load all direct routes from JSON file
def load_overview(json_path: str = data_dir / "direct_train_overview") -> dict:
    with open(json_path, encoding="utf-8") as f:
        return json.load(f)

def get_trains_for_route(start: str, end: str) -> list:
    """Return a list of IC/ICE train names for the given start and end station."""
    import os
    route_filename = f"{start}_to_{end}.json".replace(" ", "_")
    route_path = data_dir / "direct_trains" / route_filename
    if os.path.exists(route_path):
        with open(route_path, encoding="utf-8") as f:
            train_data = json.load(f)
            # Only allow IC and ICE trains
            return [entry["Zug"] for entry in train_data if str(entry["Zug"]).startswith(("IC", "ICE"))]
    return []

def predict_delay(start, end, train_name, date, time, weather, weather_data=None):
    """
    Returns the predicted delay in minutes.
    :param start: Departure station
    :param end: Arrival station
    :param train_name: Train name
    :param date: datetime.date
    :param time: datetime.time
    :param weather: bool, whether to use weather data
    :param weather_data: dict with weather data (optional)
    :return: float (delay in minutes)
    """

    dt = datetime.combine(date, time)
    features = {
        'start_station': start,
        'end_station': end,
        'train_name': train_name,
        'hour': dt.hour,
        'dayofweek': dt.weekday(),
        'month': dt.month,
    }
    if weather:
        if weather_data is None:
            features.update({
                'temperature': 0.0,
                'humidity': 0.0,
                'wind_speed': 0.0,
                'precipitation': 0.0,
                'snow_amount': 0.0
            })
        else:
            features.update(weather_data)
        df = pd.DataFrame([features])
        for col in CAT_FEATURES:
            df[col] = df[col].astype('category')
        prediction = model_with_weather.predict(df[ALL_FEATURES])[0]
    else:
        df = pd.DataFrame([features])
        for col in CAT_FEATURES:
            df[col] = df[col].astype('category')
        prediction = model_without_weather.predict(df[ALL_FEATURES_NO_WEATHER])[0]
    return prediction

def predict_canceled(start, end, train_name, date, time, delay_minutes, weather, weather_data=None):
    """
    Gives the predicted cancellation probability.
    :param start: Departure station
    :param end: Arrival station
    :param train_name: Train name
    :param date: datetime.date
    :param time: datetime.time
    :param delay_minutes: float, predicted delay
    :param weather: bool, whether to use weather data
    :param weather_data: dict with weather data (optional)
    :return: float (cancellation probability)
    """

    dt = datetime.combine(date, time)
    features = {
        'start_station': start,
        'end_station': end,
        'train_name': train_name,
        'hour': dt.hour,
        'dayofweek': dt.weekday(),
        'month': dt.month,
        'delay_minutes': delay_minutes
    }
    if weather:
        if weather_data is None:
            features.update({
                'temperature': 0.0,
                'humidity': 0.0,
                'wind_speed': 0.0,
                'precipitation': 0.0,
                'snow_amount': 0.0
            })
        else:
            features.update(weather_data)
        df = pd.DataFrame([features])
        for col in CAT_FEATURES:
            df[col] = df[col].astype('category')
        prediction = canceled_model_with_weather.predict(df[ALL_FEATURES + ['delay_minutes']])[0]
    else:
        df = pd.DataFrame([features])
        for col in CAT_FEATURES:
            df[col] = df[col].astype('category')
        prediction = canceled_model_without_weather.predict(df[ALL_FEATURES_NO_WEATHER + ['delay_minutes']])[0]
    return prediction

def get_last_trips(start, end, train_name, date, time, n=5):
    """
    Returns the n trips closest in time to date+time for the selected connection.
    :param start: Departure station
    :param end: Arrival station
    :param train_name: Train name
    :param date: datetime.date
    :param time: datetime.time
    :param n: Number of trips
    :return: DataFrame with the n next trips
    """
    import pandas as pd
    from datetime import datetime
    subtrips_path = base_dir / "data/bahn_data/processed/subtrips_data.parquet"
    if not subtrips_path.exists():
        return None
    df = pd.read_parquet(subtrips_path)
    filtered = df[(df['origin_station'] == start) & (df['destination_station'] == end) & (df['train_name'] == train_name)]
    if filtered.empty:
        return None

    if not pd.api.types.is_datetime64_any_dtype(filtered['departure_time_origin']):
        filtered['departure_time_origin'] = pd.to_datetime(filtered['departure_time_origin'])
    target_dt = datetime.combine(date, time)
    filtered['abs_time_diff'] = (filtered['departure_time_origin'] - target_dt).abs()
    filtered = filtered.sort_values('abs_time_diff').head(n)
    return filtered[['departure_time_origin', 'delay_at_dest', 'canceled']]

def get_typical_departure_time(start, end, train_name, date):
    """
    Returns the most common departure time (as datetime.time) for the given train, route, and weekday.
    If no time is found, returns None.
    :param start: Departure station
    :param end: Arrival station
    :param train_name: Train name
    :param date: datetime.date
    :return: datetime.time or None
    """
    subtrips_path = base_dir / "data/bahn_data/processed/subtrips_data.parquet"
    if not subtrips_path.exists():
        return None
    df = pd.read_parquet(subtrips_path)
    filtered = df[(df['origin_station'] == start) & (df['destination_station'] == end) & (df['train_name'] == train_name)]
    if filtered.empty:
        return None
    filtered['departure_time_origin'] = pd.to_datetime(filtered['departure_time_origin'])
    filtered = filtered[filtered['departure_time_origin'].dt.weekday == date.weekday()]
    if filtered.empty:
        return None
    filtered['dep_time_str'] = filtered['departure_time_origin'].dt.strftime('%H:%M')
    most_common_time = filtered['dep_time_str'].mode()
    if not most_common_time.empty:
        return pd.to_datetime(most_common_time.iloc[0], format='%H:%M').time()
    return None

def get_weather_forecast_for_station_date(station_name, date):
    """
    Fetches weather forecast for a given station and date using OpenWeatherMap API.
    Returns a dict with temperature, humidity, wind_speed, precipitation, snow_amount.
    :param station_name: Name of the station (e.g., "Berlin Hbf")
    :param date: datetime.date for which to get the forecast
    """
    # Load API key from streamlit secrets
    api_key = st.secrets.weather_api_key

    station_ids_path = base_dir / "data/streamlit_data/station_ids.json"
    with open(station_ids_path, encoding="utf-8") as f:
        station_ids = json.load(f)
    city_id = station_ids.get(station_name)
    if not city_id:
        return None
    # OpenWeatherMap API expects cnt as number of days (max 16)
    url = f"https://api.openweathermap.org/data/2.5/forecast/daily?id={city_id}&cnt=16&appid={api_key}&units=metric"
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
        # Find the forecast for the requested date
        for day in data.get("list", []):
            forecast_date = datetime.utcfromtimestamp(day["dt"]).date()
            if forecast_date == date:
                return {
                    "temperature": day["temp"]["day"],
                    "humidity": day["humidity"],
                    "wind_speed": day["speed"],
                    "precipitation": day.get("rain", 0.0),
                    "snow_amount": day.get("snow", 0.0)
                }
        return None
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return None
