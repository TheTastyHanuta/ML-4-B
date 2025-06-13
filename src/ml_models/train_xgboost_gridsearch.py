import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_squared_error, r2_score
from xgboost import XGBRegressor
import pickle
from src.ml_models.preprocessing import train_test_data, CAT_FEATURES, NUM_FEATURES

def train_xgboost_gridsearch(subset: int | str = 'all'):
    base_dir = Path(__file__).resolve().parent
    data_path = base_dir / '../../data/subtrips_with_weather.parquet'
    metrics_path = base_dir / '../../models/xgboost_gridsearch_metrics.csv'
    model_path = base_dir / '../../models/xgboost_gridsearch_model.pkl'

    # Load data
    X_train, X_test, y_train, y_test = train_test_data(
        path=data_path,
        cat_features=CAT_FEATURES,
        num_features=NUM_FEATURES,
        test_size=0.2,
        random_state=42,
        subset=subset
    )

    # Preprocessing pipeline
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
            random_state=42
        ))
    ])

    # Hyperparameter grid
    param_grid = {
        'xgb__max_depth': [6, 10, 15],
        'xgb__learning_rate': [0.01, 0.1],
        'xgb__n_estimators': [100, 200],
        'xgb__subsample': [0.8, 1.0],
        'xgb__colsample_bytree': [0.8, 1.0]
    }

    # Grid search
    grid = GridSearchCV(
        pipeline,
        param_grid,
        cv=3,
        scoring='neg_root_mean_squared_error',
        n_jobs=2,
        verbose=2
    )
    print("Starting GridSearchCV for XGBoost...")
    grid.fit(X_train, y_train)
    print("Best params:", grid.best_params_)

    # Evaluate
    y_pred = grid.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    print(f"GridSearch XGBoost RMSE: {rmse:.3f}")
    print(f"GridSearch XGBoost R2: {r2:.3f}")

    # Save metrics
    metrics = {'RMSE': [rmse], 'R2': [r2]}
    pd.DataFrame(metrics).to_csv(metrics_path, index=False)

    # Save model
    with open(model_path, 'wb') as f:
        pickle.dump(grid.best_estimator_, f)
    print("Best model and metrics saved successfully.")

if __name__ == "__main__":
    train_xgboost_gridsearch()