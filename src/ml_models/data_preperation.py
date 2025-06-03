# Call transform_data.py to transform the data
import pandas as pd
from pathlib import Path
from src.ml_models.transform_data import transform_data
from src.ml_models.map_weather import map_weather

def transform_and_save():
    # Call the transform_data function to process the data
    transformed_data = transform_data(path="../../data/bahn_data")

    # Save the transformed data to a parquet file
    output_path = Path("../../data/bahn_data/processed/subtrips_data.parquet")
    print("Speichere Sub-Trips DataFrame als Parquet...")
    transformed_data.to_parquet(output_path, index=False, engine="pyarrow")

def add_weather_and_save():
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
    #add_weather_and_save()
    print("Datenverarbeitung abgeschlossen. Die Daten wurden gespeichert.")