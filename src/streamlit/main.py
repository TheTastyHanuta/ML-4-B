import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))
# Create streamlit home page
import streamlit as st
import json
from pathlib import Path

# Set the page configuration
st.set_page_config(
    page_title="DB-Statistik – Übersicht",
    layout="wide",
)
st.title("Deutsche Bahn – Gesamtübersicht")

# Define the path to the data directory
path = Path(__file__).parent.parent.parent / "data/streamlit_data"

# Read and display json data with cacheing
@st.cache_data
def load_json_data():
    with open(path / "data.json", "r") as file:
        return json.load(file)

data = load_json_data()

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
        cols[0].metric("Pünktlich", data.get(f"puenktlich_{key}", "-"))
        cols[1].metric("Durchschn. Verspätung", data.get(f"durchschnittliche_verspaetung_{key}", "-"))
        cols[2].metric("Ausgefallen", data.get(f"ausgefallen_{key}", "-"))
        cols[3].metric("Zughalte", f"{data.get(f'summe_zughalte_{key}', '-'):,}")

# Display the images from data folder
col1, col2 = st.columns(2)
with col1:
    st.image(
        path / "cumulative_distribution.png",
        caption="\n**Kumulative Verteilung**",
        use_container_width=True,
    )
with col2:
    st.image(
        path / "delay_distribution.png",
        caption="\n**Delay-Verteilung**",
        use_container_width=True,
    )
