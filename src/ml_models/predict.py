import lightgbm as lgb
import pandas as pd
from pathlib import Path
import pickle

CAT_FEATURES = ['start_station', 'end_station', 'train_name']
NUM_FEATURES = ['hour', 'dayofweek', 'month', 'temperature', 'humidity', 'wind_speed', 'precipitation', 'snow_amount']
ALL_FEATURES = CAT_FEATURES + NUM_FEATURES

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

# Load the model
base_dir = Path(__file__).resolve().parent
model_path = base_dir / '../../models/lightgbm_model_delay_minutes.pkl'
model = load_model(model_path)

# Example input for a single train
sample1 = pd.DataFrame([{
    'start_station': 'Nürnberg Hbf',
    'end_station': 'Berlin Hbf',
    'train_name': 'ICE 1108',
    'hour': 14,
    'dayofweek': 2,
    'month': 4,
    'temperature': 22.5,
    'humidity': 55.0,
    'wind_speed': 10.2,
    'precipitation': 0.0,
    'snow_amount': 0.0
}])

sample2 = pd.DataFrame([{
    'start_station': 'Nürnberg Hbf',
    'end_station': 'Berlin Hbf',
    'train_name': 'ICE 500',
    'hour': 20,
    'dayofweek': 2,
    'month': 4,
    'temperature': 22.5,
    'humidity': 55.0,
    'wind_speed': 10.2,
    'precipitation': 0.0,
    'snow_amount': 0.0
}])

# Set categorical dtype (set categories if you have them from training)
for col in CAT_FEATURES:
    sample1[col] = sample1[col].astype('category')
    sample2[col] = sample2[col].astype('category')

# Predict
prediction = model.predict(sample1[ALL_FEATURES])
print('Prediction ICE 1108:', prediction[0])

prediction2 = model.predict(sample2[ALL_FEATURES])
print('Prediction ICE 500:', prediction2[0])

# Add delay minutes to the sample DataFrame
sample1['delay_minutes'] = prediction[0]
sample2['delay_minutes'] = prediction2[0]

ALL_FEATURES = CAT_FEATURES + NUM_FEATURES + ['delay_minutes']

# Load cancelled model
canceled_model = load_model(base_dir / '../../models/lightgbm_model_canceled.pkl')
# Predict cancellation
cancellation_prediction = canceled_model.predict(sample1[ALL_FEATURES])
print('Cancellation Prediction ICE 1108:', cancellation_prediction[0])
# Predict cancellation for second sample
cancellation_prediction2 = canceled_model.predict(sample2[ALL_FEATURES])
print('Cancellation Prediction ICE 500:', cancellation_prediction2[0])

'''
Prediction ICE 1108: 4.465959811103615
Prediction ICE 500: 30.139822682872044
Cancellation Prediction ICE 1108: 0.00028551445178091607
Cancellation Prediction ICE 500: 0.01010822777836091
'''