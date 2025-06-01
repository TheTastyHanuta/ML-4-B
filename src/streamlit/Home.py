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
st.json(data)

# Display the images from data folder
st.image(
    path / "cumulative_distribution.png",
    caption="Deutsche Bahn – Kumulative Verteilung",
    use_container_width=True,
)

st.image(
    path / "delay_distribution.png",
    caption="Deutsche Bahn – Delay-Verteilung",
    use_container_width=True,
)