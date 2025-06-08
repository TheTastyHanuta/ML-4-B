import pandas as pd
from sklearn.model_selection import train_test_split
import lightgbm as lgb
import pickle
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# Read the dataset
df = pd.read_parquet("../../data/subtrips_with_weather.parquet")

# Feature Engineering
features = ['station', 'destination_station', 'day_of_week', 'hour_of_day', 'train_name', 'rain_amount']
target = 'delay_at_dest'

# Encode categorical features
for col in ['station', 'destination_station', 'train_name']:
    df[col] = df[col].astype('category')

X = df[features]
y = df[target]

# Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# LightGBM Dateset
train_data = lgb.Dataset(
    X_train,
    label=y_train,
    categorical_feature=['station', 'destination_station', 'train_name']
)
valid_data = lgb.Dataset(
    X_test,
    label=y_test,
    categorical_feature=['station', 'destination_station', 'train_name'],
    reference=train_data
)

# LightGBM Parameter
params = {
    'objective': 'regression',
    'metric': 'rmse',
    'verbosity': -1
}

# Callbacks für Early Stopping und Logging
callbacks = [
    lgb.early_stopping(stopping_rounds=50),
    lgb.log_evaluation(period=100)
]

# Train the model
model = lgb.train(
    params,
    train_data,
    num_boost_round=1000,
    valid_sets=[valid_data],
    callbacks=callbacks
)

y_pred = model.predict(X_test, num_iteration=model.best_iteration)

# Calculate metrics
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)

mae = mean_absolute_error(y_test, y_pred)
r2  = r2_score(y_test, y_pred)

metrics = {'rmse': rmse, 'mae': mae, 'r2': r2}

# save the model
with open('../../models/lightgbm_model.pkl', 'wb') as f:
    pickle.dump(model, f)

# Print metrics
print(f'RMSE: {rmse}')
print(f'MAE: {mae}')
print(f'R^2: {r2}')

# Save metrics to CSV
metrics_df = pd.DataFrame([metrics])
metrics_df.to_csv('../../models/lightgbm_metrics.csv', index=False)
print('Kennzahlen gespeichert in metrics.csv')
