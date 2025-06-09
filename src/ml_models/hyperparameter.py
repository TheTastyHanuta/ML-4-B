import pandas as pd
import numpy as np
import json
from lightgbm import LGBMRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import make_scorer, mean_squared_error

# Read the dataset
df = pd.read_parquet("../../data/subtrips_with_weather.parquet")

# Feature Engineering
features = ['station', 'destination_station', 'day_of_week', 'hour_of_day', 'train_name', 'rain_amount', 'snow_amount', 'wind_speed', 'temp_celsius', 'weather']
target = 'delay_at_dest'

# Remove rows with NaN values in the target column
df = df.dropna(subset=[target])

# Remove rows with NaN values in the feature columns
df = df.dropna(subset=features)

# Outliers removal
df = df[(df[target] >= -10) & (df[target] <= 120)]

# Encode categorical features
for col in ['station', 'destination_station', 'train_name', 'weather']:
    df[col] = df[col].astype('category')

X = df[features]
y = df[target]

# Split the dataset into training and validation sets
X_train, X_valid, y_train, y_valid = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# LightGBM init
model = LGBMRegressor(
    objective='regression',
    verbosity=-1,
    device='cuda',
    random_state=42
)

# Parameter grid for hyperparameter tuning
param_grid = {
    'learning_rate': [0.01, 0.05, 0.1],
    'num_leaves': [31, 50, 100],
    'max_depth': [-1, 10, 20],
    'min_child_samples': [5, 10, 20],
    'subsample': [0.6, 0.8, 1.0],
    'colsample_bytree': [0.6, 0.8, 1.0]
}

# Define RMSE scorer
def rmse(y_true, y_pred):
    return np.sqrt(mean_squared_error(y_true, y_pred))

rmse_scorer = make_scorer(
    rmse,
    greater_is_better=False
)

# grid search
grid_search = GridSearchCV(
    estimator=model,
    param_grid=param_grid,
    scoring=rmse_scorer,
    cv=5,
    n_jobs=-1,
    verbose=2
)

# Fit the grid search
grid_search.fit(X_train, y_train)

# Evaluate the best model on the validation set
print("Beste Parameter:", grid_search.best_params_)
print("Bestes CV-RMSE:", -grid_search.best_score_)

# Save the results of the best parameters and score to a JSON file
with open('../../models/grid_search_results.json', 'w') as f:
    json.dump({
        'best_params': grid_search.best_params_,
        'best_score':  -grid_search.best_score_
    }, f, indent=4)

# Save the full CV results to a CSV file
cv_results_df = pd.DataFrame(grid_search.cv_results_)
cv_results_df.to_csv('../../models/grid_search_cv_results.csv', index=False)

print("Ergebnisse gespeichert in 'grid_search_results.json' und 'grid_search_cv_results.csv'")
