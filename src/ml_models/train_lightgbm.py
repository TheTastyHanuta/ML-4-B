from src.ml_models.preprocessing import train_test_data, CAT_FEATURES, NUM_FEATURES
import lightgbm as lgb
from pathlib import Path
import pickle
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.model_selection import KFold
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
    metrics_path = base_dir / f'../../models/metrics/lightgbm_metrics_{target}.csv'
    model_path = base_dir / f'../../models/lightgbm_model_{target}.pkl'
    feature_importance_path = base_dir / f'../../models/lightgbm_feature_importance_{target}.csv'

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

    if target == 'delay_minutes':
        # For regression ('delay_minutes'), use regression objective
        params = {
            'objective': 'regression',
            'metric': 'rmse',
            'learning_rate': 0.1,
            'verbosity': -1
        }
    else:
        # For binary classification ('canceled'), use binary objective
        params = {
            'objective': 'binary',
            'metric': 'binary_logloss',
            'learning_rate': 0.1,
            'verbosity': -1,
        }

    max_rounds = 5000

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

    if target == 'delay_minutes':
        # Cross validation for RMSE
        cross_val_rmse(X_train, y_train, params, CAT_FEATURES)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        metrics = {'rmse': rmse, 'mae': mae, 'r2': r2}
        # Print results
        print(f"RMSE: {rmse:.3f}")
        print(f"MAE: {mae:.3f}")
        print(f"R2: {r2:.3f}")
    else:
        # For binary classification, threshold predictions at 0.5
        y_pred_binary = (y_pred > 0.5).astype(int)
        accuracy = accuracy_score(y_test, y_pred_binary)
        precision = precision_score(y_test, y_pred_binary)
        recall = recall_score(y_test, y_pred_binary)
        f1 = f1_score(y_test, y_pred_binary)
        auc = roc_auc_score(y_test, y_pred)
        metrics = {'accuracy': accuracy, 'precision': precision, 'recall': recall, 'f1': f1, 'auc': auc}
        # Print results
        print(f"Accuracy: {accuracy:.3f}")
        print(f"Precision: {precision:.3f}")
        print(f"Recall: {recall:.3f}")
        print(f"F1 Score: {f1:.3f}")
        print(f"AUC: {auc:.3f}")

    # Save model and metrics
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    metrics_df = pd.DataFrame([metrics])
    metrics_df.to_csv(metrics_path, index=False)
    print("Model and metrics saved successfully.")

    # Save feature importance
    importances = model.feature_importance(importance_type='gain')
    feature_names = X_train.columns
    feature_importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': importances
    }).sort_values(by='importance', ascending=False)
    feature_importance_df.to_csv(feature_importance_path, index=False)
    print(feature_importance_df)

def cross_val_rmse(X, y, params, cat_features, n_splits=5):
    print("Performing cross-validation for RMSE...")
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)
    rmses = []
    for train_idx, val_idx in kf.split(X):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
        for col in CAT_FEATURES:
            X_train.loc[:, col] = X_train[col].astype('category')
            X_val.loc[:, col] = X_val[col].astype('category')
        train_data = lgb.Dataset(X_train, label=y_train, categorical_feature=cat_features, free_raw_data=False)
        val_data = lgb.Dataset(X_val, label=y_val, categorical_feature=cat_features, free_raw_data=False)
        model = lgb.train(
            params,
            train_data,
            num_boost_round=10000,
            valid_sets=[val_data],
            callbacks=[lgb.early_stopping(stopping_rounds=100)],
        )
        y_pred = model.predict(X_val, num_iteration=model.best_iteration)
        rmse = np.sqrt(mean_squared_error(y_val, y_pred))
        rmses.append(rmse)
    print(f"Mean CV RMSE: {np.mean(rmses):.3f} ± {np.std(rmses):.3f}")
    return rmses


if __name__ == "__main__":
    print("Starting LightGBM model training...")
    train_lightgbm(target="canceled")
    print("Training complete.")