"""
Script to precompute typical departure times from subtrips data
Run this script to generate the optimized typical_departure_times.parquet file
"""
import pandas as pd
from pathlib import Path

def create_typical_departure_times():
    """
    Creates a lightweight parquet file with typical departure times
    for each train/route/weekday combination
    """
    base_dir = Path(__file__).parent.parent.parent.parent
    
    # Input file
    input_path = base_dir / "data/bahn_data/processed/subtrips_data.parquet"
    
    # Output file  
    output_path = base_dir / "data/streamlit_data/typical_departure_times.parquet"
    
    print(f"Loading data from: {input_path}")
    if not input_path.exists():
        print(f"Error: Input file does not exist: {input_path}")
        return
    
    # Load full dataset
    df = pd.read_parquet(input_path)
    print(f"Loaded {len(df):,} records")
    
    # Only keep necessary columns
    df_light = df[['origin_station', 'destination_station', 'train_name', 'departure_time_origin']].copy()
    
    # Convert to datetime if needed
    if not pd.api.types.is_datetime64_any_dtype(df_light['departure_time_origin']):
        df_light['departure_time_origin'] = pd.to_datetime(df_light['departure_time_origin'])
    
    # Add weekday column
    df_light['weekday'] = df_light['departure_time_origin'].dt.weekday
    df_light['dep_time_str'] = df_light['departure_time_origin'].dt.strftime('%H:%M')
    
    print("Aggregating typical departure times...")
    
    # Group by train/route/weekday and get the most common departure time
    typical_times = (df_light.groupby(['origin_station', 'destination_station', 'train_name', 'weekday'])
                    ['dep_time_str']
                    .agg(lambda x: x.mode().iloc[0] if not x.mode().empty else None)
                    .reset_index())
    
    # Remove rows where no typical time could be determined
    typical_times = typical_times.dropna(subset=['dep_time_str'])
    
    print(f"Aggregated to {len(typical_times):,} unique combinations")
    print(f"Data reduction: {len(df):,} → {len(typical_times):,} ({len(typical_times)/len(df)*100:.2f}%)")
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save as parquet
    typical_times.to_parquet(output_path, index=False)
    print(f"Saved to: {output_path}")
    
    # Show some stats
    print(f"\nFile sizes:")
    input_size = input_path.stat().st_size / (1024*1024)  # MB
    output_size = output_path.stat().st_size / (1024*1024)  # MB
    print(f"  Original: {input_size:.1f} MB")
    print(f"  Optimized: {output_size:.1f} MB")
    print(f"  Size reduction: {(1 - output_size/input_size)*100:.1f}%")
    
    return typical_times

if __name__ == "__main__":
    result = create_typical_departure_times()
    if result is not None:
        print("\nSuccessfully created typical_departure_times.parquet")
        print("\nSample data:")
        print(result.head(10))
    else:
        print("\nFailed to create file")
