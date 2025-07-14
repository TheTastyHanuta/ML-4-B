import pandas as pd
from pathlib import Path
from src.data_processing.transform_bahn import transform_bahn
from src.data_processing.transform_weather import transform_weather
from src.data_processing.map_weather import map_weather

base_dir = Path(__file__).resolve().parent.parent.parent

def transform_and_save(bahn: bool = True, weather: bool = True) -> None:
    """
    Transform and save bahn and weather data to parquet files.
    This function processes the bahn data and weather data, transforming them into
    a suitable format and saving them as parquet files for further analysis.
    If bahn is True, it processes the bahn data; if weather is True, it processes the weather data.
    The transformed bahn data is saved to "../data/bahn_data/processed/subtrips_data.parquet",
    and the transformed weather data is saved to "../data/weather_data/weather_data.parquet".
    :param bahn: Whether to process bahn data.
    :param weather: Whether to process weather data.
    :return: None
    """

    print(f"Base directory for data processing: {base_dir}")

    if bahn:
        print("Starting bahn data transformation...")
        # Call the transform_data function to process the data
        transformed_bahn = transform_bahn(path=base_dir / "data/bahn_data")
        if transformed_bahn is None:
            print("No bahn data to process. Exiting...")
            return
        # Save the transformed bahn data to a parquet file
        bahn_output_path = Path(base_dir / "data/bahn_data/processed/subtrips_data.parquet")
        print("Saving bahn data DataFrame as Parquet...")
        transformed_bahn.to_parquet(bahn_output_path, index=False, engine="pyarrow")

    if weather:
        print("Starting weather data transformation...")
        # Call the transform_weather function to process the weather data
        transformed_weather = transform_weather(path=base_dir / "src/weatherdata/data_scraping/scrapedData/scrapedData.json")
        if transformed_weather is None:
            print("No weather data to process. Exiting...")
            return
        # Save the transformed weather data to a parquet file
        weather_output_path = Path(base_dir / "data/weather_data/weather_data.parquet")
        print("Saving weather data DataFrame as Parquet...")
        transformed_weather.to_parquet(weather_output_path, index=False, engine="pyarrow")

def map_weather_and_save() -> None:
    """
    Map weather data to the transformed bahn sub-trip data and save the merged dataset.
    This function loads the transformed bahn data and weather data from parquet files,
    maps the weather data to the bahn sub-trip data, and saves the merged dataset to a new parquet file.
    The merged data is saved to "../data/subtrips_with_weather.parquet".
    :return: None
    """
    # Load the transformed data
    transformed_bahn_data = pd.read_parquet(Path(base_dir / "data/bahn_data/processed/subtrips_data.parquet"), engine="pyarrow")

    # Load the weather data
    weather_data = pd.read_parquet(Path(base_dir / "data/weather_data/weather_data.parquet"), engine="pyarrow")

    if transformed_bahn_data.empty:
        print("Transformed bahn data is empty. Exiting...")
        return
    if weather_data.empty:
        print("Weather data is empty. Exiting...")
        return

    # Map the weather data to the transformed data
    print("Mapping weather data to sub-trips...")
    merged_data = map_weather(transformed_bahn_data, weather_data)

    # Print the shape of the merged data
    print(f"Shape of the new dataset {merged_data.shape}")
    # Print the first few rows of the merged data
    print("First few rows of the merged DataFrame:")
    print(merged_data.head())

    # Save the merged data to a new parquet file
    output_path = Path(base_dir / "data/subtrips_with_weather.parquet")
    print("Saving merged data DataFrame as Parquet...")
    merged_data.to_parquet(output_path, index=False, engine="pyarrow")

if __name__ == "__main__":
    print("Starting data processing...")
    #transform_and_save(True, True)
    map_weather_and_save()
    print("Data processing completed. Data has been saved.")