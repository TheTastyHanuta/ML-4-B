import pandas as pd
from pathlib import Path
def convert_parquet_to_csv(parquet_file: Path, csv_file: Path) -> None:
    """
    Convert a Parquet file to a CSV file.

    :param parquet_file: Path to the input Parquet file.
    :type parquet_file: Path
    :param csv_file: Path to the output CSV file.
    :type csv_file: Path
    """
    # Read the Parquet file into a DataFrame
    df = pd.read_parquet(parquet_file)

    # Only the first 1000 rows are needed for the CSV file
    df = df.head(1000)

    # Write the DataFrame to a CSV file
    df.to_csv(csv_file, index=False)

def main():

    #parquet_file = Path('../../data/bahn_data/processed/subtrips_data.parquet')
    #csv_file = Path('../../data/bahn_data/processed/subtrips_data.csv')

    parquet_file = Path('../../data/weather_data/weather_data.parquet')
    csv_file = Path('../../data/weather_data/weather_data.csv')

    # Convert the Parquet file to a CSV file
    convert_parquet_to_csv(parquet_file, csv_file)

if __name__ == "__main__":
    main()