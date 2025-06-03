import pandas as pd
from datetime import datetime

def transform_weather(path: str = "../weatherdata/data_scraping/scrapedData/scrapedData.json") -> pd.DataFrame:
    """
    Transform weather data from a given path into a DataFrame.
    This function processes weather data, extracting relevant fields and converting them into a structured DataFrame format.
    :param path: Path to the directory containing weather data files.
    :type path: str
    :rtype: pd.DataFrame
    :return: DataFrame containing transformed weather data with columns:
             - station: Weather station name
             - time: Timestamp of the weather data
             - temp_celsius: Temperature in Celsius
             - humidity: Humidity percentage
             - wind_speed: Wind speed in m/s
             - weather: Weather description
             - rain_amount: Rain amount in mm (if available)
             - snow_amount: Snow amount in mm (if available)
    """

    # Load the JSON data
    with open(path, 'r') as file:
        data = pd.read_json(file)

    # Transform the data to a more usable format
    records = []
    for station, entries in data.items():
        for entry in entries:
            dt = datetime.fromtimestamp(entry['dt'])
            temp_k = entry['main']['temp']
            temp_c = temp_k - 273.15  # Convert from Kelvin to Celsius
            weather_desc = entry['weather'][0]['description'] if entry.get('weather') else None
            rain_amount = entry.get('rain', {}).get('1h', 0.0)
            snow_amount = entry.get('snow', {}).get('1h', 0.0)
            humidity = entry['main']['humidity']
            wind_speed = entry['wind']['speed']
            records.append({
                'station': station,
                'time': dt,
                'temp_celsius': round(temp_c, 2),
                'humidity': humidity,
                'wind_speed': wind_speed,
                'weather': weather_desc,
                'rain_amount': rain_amount,
                'snow_amount': snow_amount
            })

    # Create DataFrame
    df = pd.DataFrame(records)
    return df
