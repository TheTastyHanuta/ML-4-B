import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[3]))
import streamlit as st
from pathlib import Path

# Define the path to the data directory
path = Path(__file__).parent.parent.parent.parent / "data/streamlit_data"

st.markdown("""
Hier findest du verschiedene Visualisierungen zu Pünktlichkeit, Verspätungen und Ausfällen der Züge.
""")

st.header("Verteilungen der Verspätungen")
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

st.header("Verspätungen und Pünktlichkeit nach Uhrzeit")
time_dist_path = path / "time_dist" / "uhrzeit"

col3, col4 = st.columns(2)
with col3:
    st.image(
        time_dist_path / "punctuality.png",
        caption="\n**Pünktlichkeit nach Stunde**",
        use_container_width=True,
    )
with col4:
    st.image(
        time_dist_path / "delays.png",
        caption="\n**Durchschnittliche Verspätung nach Stunde**",
        use_container_width=True,
    )

st.header("Ausgefallene Züge über den Tag verteilt")
st.image(
    time_dist_path / "cancellations.png",
    caption="\n**Ausgefallene Züge nach Stunde**",
    use_container_width=True,
)

st.markdown(
    """
---
Datenbasis: Deutsche Bahn, gesammelt vom 2024-08-01 bis 2025-06-30.
"""
)

