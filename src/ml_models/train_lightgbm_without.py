from src.ml_models.preprocessing import train_test_data, CAT_FEATURES, NUM_FEATURES
import lightgbm as lgb
from pathlib import Path
import pickle
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

def train_lightgbm(subset: int | str = 'all', target: str = 'delay_minutes'):
    """
    Train a LightGBM model on the Bahn sub-trip data with weather conditions.
    This function loads the preprocessed data, trains the model, evaluates it,
    and saves the metrics and model to files.
    :param subset: The subset of data to use for training. Can be an integer for a specific number of rows,
                   'all' for the entire dataset or leave empty for the entire dataset.
    :param target: The target variable for the model. Default is 'delay_minutes'. You can also change it to 'canceled'
    :return: None
    """

    base_dir = Path(__file__).resolve().parent
    data_path = base_dir / '../../data/subtrips_with_weather.parquet'
    metrics_path = base_dir / f'../../models/lightgbm_metrics_without_{target}.csv'
    model_path = base_dir / f'../../models/lightgbm_model_without_{target}.pkl'

    # Remove 'temperature', 'humidity', 'wind_speed', 'precipitation', 'snow_amount' from NUM_FEATURES
    NUM_FEATURES = ['hour', 'dayofweek', 'month']

    # Load data and preprocess
    X_train, X_test, y_train, y_test = train_test_data(
        path=data_path,
        cat_features=CAT_FEATURES,
        num_features=NUM_FEATURES,
        test_size=0.2,
        random_state=42,
        subset=subset
    )

    # Ensure LightGBM-compatible dtypes: convert categorical cols to pandas 'category'
    for col in CAT_FEATURES:
        X_train[col] = X_train[col].astype('category')
        X_test[col] = X_test[col].astype('category')

    # Prepare LightGBM datasets without dropping any rows
    train_data = lgb.Dataset(
        X_train,
        label=y_train,
        categorical_feature=CAT_FEATURES,
        free_raw_data=False
    )
    valid_data = lgb.Dataset(
        X_test,
        label=y_test,
        categorical_feature=CAT_FEATURES,
        reference=train_data,
        free_raw_data=False
    )

    # Set LightGBM parameters
    params = {
        'objective': 'regression',
        'metric': 'rmse',
        'learning_rate': 0.1,
        'verbosity': -1
    }
    '''
    params = {
        'objective': 'regression',
        'metric': 'rmse',
        'boosting_type': 'gbdt',
        'num_leaves': 31,
        'learning_rate': 0.05,
        'feature_fraction': 0.9,
        'bagging_fraction': 0.8,
        'bagging_freq': 5,
        'verbose': -1,
        #'device': 'cuda' # ToDo: I need to recompile LightGBM with GPU support
    }
    '''
    max_rounds = 15000

    # Train model with early stopping via callbacks
    print("Training LightGBM model...")
    model = lgb.train(
        params,
        train_data,
        num_boost_round=max_rounds,
        valid_sets=[valid_data],
        callbacks=[
            lgb.early_stopping(stopping_rounds=50),
            lgb.log_evaluation(period=100)
        ]
    )
    print("Model training complete.")

    # Predict on test set
    y_pred = model.predict(X_test, num_iteration=model.best_iteration)

    # Compute metrics
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    metrics = {'rmse': rmse, 'mae': mae, 'r2': r2}

    # Print results
    print(f"RMSE: {rmse:.3f}")
    print(f"MAE: {mae:.3f}")
    print(f"R2: {r2:.3f}")

    # Save model and metrics
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    metrics_df = pd.DataFrame([metrics])
    metrics_df.to_csv(metrics_path, index=False)
    print("Model and metrics saved successfully.")

if __name__ == "__main__":
    print("Starting LightGBM model training...")
    train_lightgbm()
    print("Training complete.")