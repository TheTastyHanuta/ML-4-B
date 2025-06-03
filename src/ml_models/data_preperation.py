# Call transform_data.py to transform the data
import pandas as pd
from pathlib import Path
from src.data_processing.transform_bahn import transform_bahn
from src.data_processing.transform_weather import transform_weather
from src.data_processing.map_weather import map_weather

def transform_and_save() -> None:
    # Call the transform_data function to process the data
    transformed_bahn = transform_bahn(path="../../data/bahn_data")
    transformed_weather = transform_weather(path="../weatherdata/data_scraping/scrapedData/scrapedData.json")

    # Save the transformed bahn data to a parquet file
    bahn_output_path = Path("../../data/bahn_data/processed/subtrips_data.parquet")
    print("Speichere Sub-Trips DataFrame als Parquet...")
    transformed_bahn.to_parquet(bahn_output_path, index=False, engine="pyarrow")

    # Save the transformed weather data to a parquet file
    weather_output_path = Path("../../data/weather_data/weather_data.parquet")
    print("Speichere Wetterdaten DataFrame als Parquet...")
    transformed_weather.to_parquet(weather_output_path, index=False, engine="pyarrow")

def map_weather_and_save() -> None:
    # Load the transformed data
    transformed_data = pd.read_parquet(Path("../../data/bahn_data/processed/subtrips_data.parquet"), engine="pyarrow")

    # Load the weather data
    weather_data = pd.read_parquet(Path("../../data/weather_data/weather_data.parquet"), engine="pyarrow")

    # Map the weather data to the transformed data
    print("Wende Wetterdaten auf Sub-Trips DataFrame an...")
    merged_data = map_weather(transformed_data, weather_data)

    # Save the merged data to a new parquet file
    output_path = Path("../../data/bahn_data/processed/subtrips_with_weather.parquet")
    print("Speichere Sub-Trips DataFrame mit Wetterdaten als Parquet...")
    merged_data.to_parquet(output_path, index=False, engine="pyarrow")

if __name__ == "__main__":
    transform_and_save()
    #map_weather_and_save()
    print("Datenverarbeitung abgeschlossen. Die Daten wurden gespeichert.")