from preprocessing import train_test_data, CAT_FEATURES, NUM_FEATURES
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from xgboost import XGBRegressor
import pandas as pd
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np
import pickle

# Load data and preprocess
X_train, X_test, y_train, y_test = train_test_data(
    path='../../data/subtrips_with_weather.parquet',
    cat_features=CAT_FEATURES,
    num_features=NUM_FEATURES,
    test_size=0.2,
    random_state=42
)

# Define the preprocessing and model pipeline
preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), CAT_FEATURES)
    ],
    remainder='passthrough'
)

pipeline = Pipeline([
    ('preprocessing', preprocessor),
    ('xgb', XGBRegressor(
        objective='reg:squarederror',
        tree_method='hist',
        device='cuda',
        n_estimators=100,
        learning_rate=0.1,
        max_depth=6,
        random_state=42
    ))
])

# Train the model
pipeline.fit(X_train, y_train)

# Evaluate model
y_pred = pipeline.predict(X_test)
print(f"RMSE: {np.sqrt(mean_squared_error(y_test, y_pred)):.3f}")
print(f"R2 score: {r2_score(y_test, y_pred):.3f}")

# Save metrics to a csv file
metrics = {
    'RMSE': [np.sqrt(mean_squared_error(y_test, y_pred))],
    'R2': [r2_score(y_test, y_pred)]
}
metrics_df = pd.DataFrame(metrics)
metrics_df.to_csv('../../models/xgboost_metrics.csv', index=False)

# Save the model
with open('../../models/xgboost_model.pkl', 'wb') as f:
    pickle.dump(pipeline, f)
