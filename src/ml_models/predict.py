from pathlib import Path
import pickle

# Features with weather data
CAT_FEATURES = ['start_station', 'end_station', 'train_name']
NUM_FEATURES = ['hour', 'dayofweek', 'month', 'temperature', 'humidity', 'wind_speed', 'precipitation', 'snow_amount']
ALL_FEATURES = CAT_FEATURES + NUM_FEATURES

# Features without weather data
NUM_FEATURES_NO_WEATHER = ['hour', 'dayofweek', 'month']
ALL_FEATURES_NO_WEATHER = CAT_FEATURES + NUM_FEATURES_NO_WEATHER

# Features for canceled prediction
ALL_FEATURES_CANCELED = CAT_FEATURES + NUM_FEATURES + ['delay_minutes']
ALL_FEATURES_CANCELED_NO_WEATHER = CAT_FEATURES + NUM_FEATURES_NO_WEATHER + ['delay_minutes']

# Load trained model with pickle
def load_model(model_path: str | Path):
    """
    Load a trained LightGBM model from a file.
    :param model_path: Path to the model file.
    :return: Loaded LightGBM model.
    """
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    return model

base_dir = Path(__file__).resolve().parent
model_path_with_weather = base_dir / '../../models/lightgbm_model_delay_minutes.pkl'
model_path_no_weather = base_dir / '../../models/lightgbm_model_without_delay_minutes.pkl'

model_with_weather = load_model(model_path_with_weather)
model_without_weather = load_model(model_path_no_weather)

# Load canceled models
canceled_model_with_weather = load_model(base_dir / '../../models/lightgbm_model_canceled.pkl')
canceled_model_without_weather = load_model(base_dir / '../../models/lightgbm_model_without_canceled.pkl')
