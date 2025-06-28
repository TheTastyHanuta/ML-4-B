import streamlit as st
import pandas as pd
from pathlib import Path

# Define the path to the data directory
path = Path(__file__).parent.parent.parent.parent / "data/streamlit_data"

# --- Title and Description ---
st.markdown("""
Die Tabellen zeigen, wie die durchschnittlichen Verspätungen und Ausfallquote pro Bahnhof sind.
Dabei ist zu beachten, dass die durchschnittliche Verspätung stark damit zusammenhängt, 
welche Zuggattungen an dem Bahnhof halten.
Die Stichprobengröße gibt an, wie viele Zughalte es an dem Bahnhof gab und damit auch 
wie viele Datensätze zur Berechnung verwendet wurden.
""")

# --- Dropdown Menu ---
FILES = {
    "Alle Züge": "Durchschnittliche Verspätungen an Bahnhöfen und Anzahl an Halten.json",
    "ICE": "[ICE] Durchschnittliche Verspätungen an Bahnhöfen und Anzahl an Halten.json",
    "IC": "[IC] Durchschnittliche Verspätungen an Bahnhöfen und Anzahl an Halten.json",
    "RB": "[RB] Durchschnittliche Verspätungen an Bahnhöfen und Anzahl an Halten.json",
    "RE": "[RE] Durchschnittliche Verspätungen an Bahnhöfen und Anzahl an Halten.json",
    "S": "[S] Durchschnittliche Verspätungen an Bahnhöfen und Anzahl an Halten.json",
}

selection = st.selectbox("Zuggattung auswählen", list(FILES.keys()))

# --- Path to JSON files ---
data_dir = path / "stations"
json_path = data_dir / FILES[selection]

# Load the data into a DataFrame
df = pd.read_json(json_path)

# Remove leading and trailing whitespace from column names
df.columns = [col.strip() for col in df.columns]

# Check if the expected columns are present
if "Durchschnittliche Verspätung [min]" in df.columns:
    df = df.sort_values(by="Durchschnittliche Verspätung [min]", ascending=False)
else:
    st.warning("Spalte 'Durchschnittliche Verspätung [min]' nicht gefunden. Verfügbare Spalten: " + str(df.columns.tolist()))

# --- Show dataframe ---
st.dataframe(df, use_container_width=True)

# --- Footer ---
st.markdown("""
---
Datenbasis: Deutsche Bahn, gesammelt vom 2025-01-01 bis 2025-05-31.
""")