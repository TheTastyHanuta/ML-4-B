from preprocessing import train_test_data, CAT_FEATURES, NUM_FEATURES
import lightgbm as lgb
import pickle
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# 1. Load, preprocess, and split data using shared features module
X_train, X_test, y_train, y_test = train_test_data(
    path='../../data/subtrips_with_weather.parquet',
    cat_features=CAT_FEATURES,
    num_features=NUM_FEATURES,
    test_size=0.2,
    random_state=42
)

# 2. Ensure LightGBM-compatible dtypes: convert categorical cols to pandas 'category'
for col in CAT_FEATURES:
    X_train[col] = X_train[col].astype('category')
    X_test[col] = X_test[col].astype('category')

# 3. Prepare LightGBM datasets without dropping any rows
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

# 4. Set LightGBM parameters
params = {
    'objective': 'regression',
    'metric': 'rmse',
    'learning_rate': 0.05,
    'verbosity': -1
}
max_rounds = 10000

# 5. Train model with early stopping via callbacks
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

# 6. Predict on test set
y_pred = model.predict(X_test, num_iteration=model.best_iteration)

# 7. Compute metrics
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
metrics = {'rmse': rmse, 'mae': mae, 'r2': r2}

# 8. Save model and metrics
with open('../../models/lightgbm_model.pkl', 'wb') as f:
    pickle.dump(model, f)
metrics_df = pd.DataFrame([metrics])
metrics_df.to_csv('../../models/lightgbm_metrics.csv', index=False)

# 9. Print results
print(f"RMSE: {rmse:.3f}")
print(f"MAE: {mae:.3f}")
print(f"R2: {r2:.3f}")