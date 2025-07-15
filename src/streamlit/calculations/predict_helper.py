import json
from pathlib import Path
import pandas as pd
from datetime import datetime
import streamlit as st
import requests
import pickle

# Import feature definitions only
from src.ml_models.predict import CAT_FEATURES, ALL_FEATURES, ALL_FEATURES_NO_WEATHER

base_dir = Path(__file__).parent.parent.parent.parent
data_dir = base_dir / "data" / "streamlit_data"

# Cache models to prevent reloading on every prediction
@st.cache_resource
def load_delay_models():
    """Load delay prediction models with caching"""
    model_dir = base_dir / "models"
    
    with open(model_dir / "lightgbm_model_delay_minutes.pkl", 'rb') as f:
        model_with_weather = pickle.load(f)
    
    with open(model_dir / "lightgbm_model_without_delay_minutes.pkl", 'rb') as f:
        model_without_weather = pickle.load(f)
    
    return model_with_weather, model_without_weather

@st.cache_resource
def load_cancellation_models():
    """Load cancellation prediction models with caching"""
    model_dir = base_dir / "models"
    
    with open(model_dir / "lightgbm_model_canceled.pkl", 'rb') as f:
        canceled_model_with_weather = pickle.load(f)
    
    with open(model_dir / "lightgbm_model_without_canceled.pkl", 'rb') as f:
        canceled_model_without_weather = pickle.load(f)
    
    return canceled_model_with_weather, canceled_model_without_weather

# Load all direct routes from JSON file
@st.cache_data
def load_overview(json_path: str = str(data_dir / "direct_train_overview.json")) -> dict:
    with open(json_path, encoding="utf-8") as f:
        return json.load(f)

@st.cache_data
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
    # Load models from cache
    model_with_weather, model_without_weather = load_delay_models()
    
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
    # Load models from cache
    canceled_model_with_weather, canceled_model_without_weather = load_cancellation_models()
    
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

# Cache the expensive parquet loading separately  
@st.cache_data
def load_subtrips_data():
    """Load subtrips data with caching - this only depends on the file"""
    subtrips_path = base_dir / "data/bahn_data/processed/subtrips_data.parquet"
    if not subtrips_path.exists():
        return None
    return pd.read_parquet(subtrips_path)

# Cache the lightweight typical departure times
@st.cache_data
def load_typical_departure_times():
    """Load pre-computed typical departure times with caching"""
    typical_times_path = data_dir / "typical_departure_times.parquet"
    if not typical_times_path.exists():
        return None
    return pd.read_parquet(typical_times_path)

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
    from datetime import datetime
    df = load_subtrips_data()  # This is cached!
    if df is None:
        return None
    
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
    typical_times = load_typical_departure_times()  # Load pre-computed data!
    if typical_times is None:
        return None
    
    # Fast lookup in the pre-computed data
    result = typical_times[
        (typical_times['origin_station'] == start) & 
        (typical_times['destination_station'] == end) & 
        (typical_times['train_name'] == train_name) &
        (typical_times['weekday'] == date.weekday())
    ]
    
    if result.empty:
        return None
    
    return pd.to_datetime(result['dep_time_str'].iloc[0], format='%H:%M').time()

# Cache station IDs loading
@st.cache_data
def load_station_ids():
    """Load station IDs mapping with caching"""
    station_ids_path = base_dir / "data/streamlit_data/station_ids.json"
    with open(station_ids_path, encoding="utf-8") as f:
        return json.load(f)

@st.cache_data(ttl=3600)  # Cache for 1 hour since weather data changes
def get_weather_forecast_for_station_date(station_name, date):
    """
    Fetches weather forecast for a given station and date using OpenWeatherMap API.
    Returns a dict with temperature, humidity, wind_speed, precipitation, snow_amount.
    :param station_name: Name of the station (e.g., "Berlin Hbf")
    :param date: datetime.date for which to get the forecast
    """
    # Load API key from streamlit secrets
    api_key = st.secrets.weather_api_key

    station_ids = load_station_ids()  # This is cached!
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
