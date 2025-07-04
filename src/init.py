from src.ml_models.train_lightgbm import train_lightgbm
from src.ml_models.train_lightgbm_without import train_lightgbm_without
from src.ml_models.train_xgboost import train_xgboost
from src.ml_models.train_xgboost_without import train_xgboost_without_weather
from src.data_processing.process_data import transform_and_save, map_weather_and_save


def main():
    """
    Main function to process data and train machine learning models.
    This function orchestrates the data processing and model training steps.
    It first processes the bahn and weather data, then maps the weather data to the bahn sub-trip data,
    and finally trains the LightGBM and XGBoost models on the processed data.
    :return: None
    """

    # Uncomment the following lines to enable data transformation and saving

    #print("Starting data processing...")
    #transform_and_save(bahn=True, weather=True)
    #map_weather_and_save()
    #print("Data processing completed. Data has been saved.")

    # Train machine learning models
    print("Starting model training for delays...")
    train_lightgbm(target='delay_minutes')
    print("LightGBM model training completed. Starting training without weather...")
    train_lightgbm_without(target='delay_minutes')
    print("LightGBM model training without weather completed.")

    print('Starting model training for cancellations...')
    train_lightgbm(target='canceled')
    print("LightGBM model training for cancellations completed. Starting training without weather...")
    train_lightgbm_without(target='canceled')
    print("All models trained successfully.")

if __name__ == "__main__":
    main()
    print("All processes completed successfully.")