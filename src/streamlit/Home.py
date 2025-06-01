# Create streamlit home page
import streamlit as st
import json

st.set_page_config(
    page_title="DB-Statistik – Übersicht",
    layout="wide",
)
st.title("Deutsche Bahn – Gesamtübersicht")

# Read and display json data with cacheing
@st.cache_data
def load_json_data():
    with open("data/data.json", "r") as file:
        return json.load(file)

data = load_json_data()

# Display statistics
st.subheader("Statistiken")
st.json(data)

# Display the images from data folder
st.image(
    "data/cumulative_distribution.png",
    caption="Deutsche Bahn – Kumulative Verteilung",
    use_container_width=True,
)

st.image(
    "data/delay_distribution.png",
    caption="Deutsche Bahn – Delay-Verteilung",
    use_container_width=True,
)