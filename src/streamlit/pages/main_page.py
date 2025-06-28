import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[3]))
import streamlit as st
import json
from pathlib import Path

# Define the path to the data directory
path = Path(__file__).parent.parent.parent.parent / "data/streamlit_data"

# Read and display json data with cacheing
@st.cache_data
def load_json_data():
    with open(path / "data.json", "r") as file:
        return json.load(file)

data = load_json_data()

st.markdown("""
Dieses Streamlit-Seite ist im Rahmen eines Uniprojektes im Modul **Machine Learning for Business** an der FAU entstanden.

**Projektziel:**
Wir möchten Verspätungen und Ausfälle im deutschen Bahnverkehr anhand historischer Bahndaten vorhersagen. 
Dazu nutzen wir Methoden des maschinellen Lernens und führen verschiedene statistische Auswertungen durch. 
Ich hoffe Dir gefällt es!!
""")

# Display statistics
st.subheader("Statistiken")

zugtypen = [
    ("all", "Alle Züge"),
    ("ICE", "ICE"),
    ("IC", "IC"),
    ("RE", "RE"),
    ("RB", "RB"),
    ("S", "S-Bahn")
]

for key, name in zugtypen:
    with st.expander(f"{name}", expanded=(key=="all")):
        cols = st.columns(4)
        cols[0].metric("Pünktliche Stops", data.get(f"puenktlich_{key}", "-"))
        cols[1].metric("Durchschn. Verspätung pro Halt", data.get(f"durchschnittliche_verspaetung_{key}", "-"))
        cols[2].metric("Ausgefallen", data.get(f"ausgefallen_{key}", "-"))
        cols[3].metric("Zughalte", f"{data.get(f'summe_zughalte_{key}', '-'):,}")

st.markdown("""
---
Datenbasis: Deutsche Bahn, gesammelt vom 2025-01-01 bis 2025-05-31.
""")
