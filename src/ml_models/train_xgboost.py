from pathlib import Path
from src.ml_models.preprocessing import train_test_data, CAT_FEATURES, NUM_FEATURES
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from xgboost import XGBRegressor
import pandas as pd
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np
import pickle
import xgboost

def train_xgboost(subset: int | str = 'all', target: str = 'delay_minutes'):
    """
    Train an XGBoost model on the Bahn sub-trip data with weather conditions.
    This function loads the preprocessed data, defines a preprocessing and model pipeline,
    trains the model, evaluates it, and saves the metrics and model to files.
    :param subset: The subset of data to use for training. Can be an integer for a specific number of rows,
                   'all' for the entire dataset or leave empty for the entire dataset.
    :param target: The target variable for the model. Default is 'delay_minutes'. You can also change it to 'canceled'
    :return: None
    """

    # Print XGBoost build information
    build_info = xgboost.build_info()
    for name in sorted(build_info.keys()):
        print(f'{name}: {build_info[name]}')

    base_dir = Path(__file__).resolve().parent
    data_path = base_dir / '../../data/subtrips_with_weather.parquet'
    metrics_path = base_dir / '../../models/xgboost_metrics.csv'
    model_path = base_dir / '../../models/xgboost_model.pkl'

    # Load data and preprocess
    X_train, X_test, y_train, y_test = train_test_data(
        path=data_path,
        cat_features=CAT_FEATURES,
        num_features=NUM_FEATURES,
        test_size=0.2,
        random_state=42,
        subset=subset,
        target=target
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
            device='cuda:0',
            n_estimators=100,
            learning_rate=0.1,
            max_depth=10,
            verbosity=1,
            random_state=42
        ))
    ])

    # Train the model
    print("Training XGBoost model...")
    pipeline.fit(X_train, y_train)
    print("Model training complete.")

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
    metrics_df.to_csv(metrics_path, index=False)

    # Save the model
    with open(model_path, 'wb') as f:
        pickle.dump(pipeline, f)
    print("Model and metrics saved successfully.")

if __name__ == "__main__":
    print("Starting XGBoost model training...")
    train_xgboost()
    print("XGBoost model training completed.")