"""
Helper functions for worst trains analysis
"""
import pandas as pd
import streamlit as st
from pathlib import Path
import json
from .direct_helper import load_overview, FERN_PREFIXES, NAH_PREFIXES

# Define the path to the data directory
base_dir = Path(__file__).parent.parent.parent.parent
data_dir = base_dir / "data" / "streamlit_data"

@st.cache_data
def load_all_trains():
    """Loads all trains from all available routes"""
    overview = load_overview(str(data_dir / "direct_train_overview.json"))
    all_trains = []
    
    # Iterate through all start and destination stations
    for start_station, destinations in overview.items():
        for end_station, filename in destinations.items():
            # Load route data
            file_path = data_dir / "direct_trains" / filename
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    route_data = json.load(f)
                
                # Add start and destination station to each train
                for train in route_data:
                    train_data = train.copy()
                    train_data['Startbahnhof'] = start_station
                    train_data['Zielbahnhof'] = end_station
                    train_data['Route'] = f"{start_station} → {end_station}"
                    all_trains.append(train_data)
                    
            except FileNotFoundError:
                st.warning(f"Datei nicht gefunden: {filename}")
                continue
    
    return pd.DataFrame(all_trains)

def get_train_type(train_name):
    """Determines train type based on train name"""
    if any(train_name.startswith(prefix) for prefix in FERN_PREFIXES):
        return "Fernverkehr"
    elif any(train_name.startswith(prefix) for prefix in NAH_PREFIXES):
        return "Nahverkehr"
    else:
        return "Sonstige"

def filter_trains(df_all, selected_train_types, min_samples, train_search=None):
    """
    Filters train data based on given criteria
    
    Args:
        df_all: DataFrame with all train data
        selected_train_types: List of selected train types
        min_samples: Minimum sample size
        train_search: Search text for train names (optional)
    
    Returns:
        Filtered DataFrame
    """
    # Apply basic filters
    df_filtered = df_all[
        (df_all['Zugtyp'].isin(selected_train_types)) &
        (df_all['Stichprobengröße'] >= min_samples)
    ].copy()
    
    # Apply text search (if provided)
    if train_search:
        df_filtered = df_filtered[
            df_filtered['Zug'].str.contains(train_search, case=False, na=False)
        ]
    
    return df_filtered

def format_display_data(df_filtered):
    """
    Formats data for display
    
    Args:
        df_filtered: Filtered DataFrame
    
    Returns:
        Formatted DataFrame for display
    """
    # Reorder columns for better display
    display_columns = [
        'Zug', 'Route', 'Zugtyp',
        'Verspätung Ankunft [min]', 'Verspätung Abfahrt [min]',
        'Ausfallquote [%]', 'Fahrzeit inkl. Verspätungen [min]',
        'Stichprobengröße'
    ]
    
    df_display = df_filtered[display_columns].copy()
    
    # Format numeric values (keep NaN values)
    numeric_columns = ['Verspätung Ankunft [min]', 'Verspätung Abfahrt [min]', 
                      'Ausfallquote [%]', 'Fahrzeit inkl. Verspätungen [min]']
    
    for col in numeric_columns:
        if col in df_display.columns:
            # Only round non-NaN values
            df_display[col] = df_display[col].round(2)
    
    return df_display

def get_top_trains(df_filtered):
    """
    Creates Top 10 lists for delays and cancellations
    
    Args:
        df_filtered: Filtered DataFrame
    
    Returns:
        Tuple: (top_delayed, top_cancelled)
    """
    # Top delays (only trains with valid delay data)
    trains_with_delay = df_filtered[df_filtered['Verspätung Ankunft [min]'].notna()]
    top_delayed = None
    if not trains_with_delay.empty:
        top_delayed = trains_with_delay.nlargest(10, 'Verspätung Ankunft [min]')[
            ['Zug', 'Route', 'Verspätung Ankunft [min]']
        ]
    
    # Top cancellations
    top_cancelled = df_filtered.nlargest(10, 'Ausfallquote [%]')[
        ['Zug', 'Route', 'Ausfallquote [%]']
    ]
    
    return top_delayed, top_cancelled
