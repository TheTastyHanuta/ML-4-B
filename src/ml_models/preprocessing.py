import pandas as pd
from sklearn.model_selection import train_test_split

def load_and_rename(path: str) -> pd.DataFrame:
    """
    Load a parquet file and rename its columns to a standardized format.
    This function assumes the parquet file contains columns that need to be renamed for consistency.
    It renames the following columns:
    - 'station' to 'start_station'
    - 'destination_station' to 'end_station'
    - 'departure_time_origin' to 'departure_datetime'
    - 'delay_at_dest' to 'delay_minutes'
    - 'temp_celsius' to 'temperature'
    - 'rain_amount' to 'precipitation'
    :param path: Path to the parquet file.
    :return: DataFrame with renamed columns.
    """
    df = pd.read_parquet(path)

    # Only take a subset of rows
    #df = df.iloc[:100000]

    df = df.rename(columns={
        'station': 'start_station',
        'destination_station': 'end_station',
        'departure_time_origin': 'departure_datetime',
        'delay_at_dest': 'delay_minutes',
        'temp_celsius': 'temperature',
        'rain_amount': 'precipitation'
    })
    return df


def extract_datetime_features(df: pd.DataFrame, datetime_col: str = 'departure_datetime') -> pd.DataFrame:
    """
    Extract hour, day of week, and month from a datetime column in the DataFrame.
    This function assumes the datetime column is in a standard format that can be parsed by pandas.
    It adds three new columns: 'hour', 'dayofweek', and 'month'.
    :param df: DataFrame containing the data.
    :param datetime_col: Name of the datetime column to extract features from.
    :return: DataFrame with additional datetime features.
    """
    df[datetime_col] = pd.to_datetime(df[datetime_col])
    df['hour'] = df[datetime_col].dt.hour
    df['dayofweek'] = df[datetime_col].dt.dayofweek
    df['month'] = df[datetime_col].dt.month
    return df


def get_feature_target_split(df: pd.DataFrame,
                             cat_features: list,
                             num_features: list,
                             target: str = 'delay_minutes'):
    """
    Split the DataFrame into features (X) and target (y).
    This function assumes that the DataFrame contains the specified categorical and numerical features,
    :param df: DataFrame containing the data.
    :param cat_features: Categorical feature names.
    :param num_features: Numerical feature names.
    :param target: Target variable name.
    :return: Tuple of (X, y) where X is the feature DataFrame and y is the target Series.
    """
    X = df[cat_features + num_features]
    y = df[target]
    return X, y


def train_test_data(path: str,
                    cat_features: list,
                    num_features: list,
                    target: str = 'delay_minutes',
                    test_size: float = 0.2,
                    random_state: int = 42):
    """
    Load data, extract datetime features, and split into training and test sets.
    This function combines loading the data, renaming columns, extracting datetime features,
    and splitting the data into training and test sets.
    It returns the training and test sets as tuples (X_train, X_test, y_train, y_test).
    :param path: Path to the parquet file.
    :param cat_features: Categorical feature names.
    :param num_features: Numerical feature names.
    :param target: Target variable name.
    :param test_size: Proportion of the dataset to include in the test split.
    :param random_state: Random seed for reproducibility.
    :return: Returns a tuple of (X_train, X_test, y_train, y_test).
    """
    df = load_and_rename(path)
    df = extract_datetime_features(df)

    # Remove rows with NaN values in the target column
    df = df.dropna(subset=[target])

    # Remove outliers in the target column
    df = df[(df[target] >= -10) & (df[target] <= 120)]

    # Remove rows with NaN values in the feature columns
    df = df.dropna(subset=cat_features + num_features)

    X, y = get_feature_target_split(df, cat_features, num_features, target)

    return train_test_split(X, y, test_size=test_size, random_state=random_state)


# Feature lists
CAT_FEATURES = ['start_station', 'end_station', 'train_name', 'weather']
NUM_FEATURES = ['hour', 'dayofweek', 'month', 'temperature', 'humidity', 'wind_speed', 'precipitation', 'snow_amount']
