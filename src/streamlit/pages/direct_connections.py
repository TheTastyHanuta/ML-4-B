from pathlib import Path
import streamlit as st
from src.streamlit.calculations.direct_helper import load_overview, load_route_df, filter_routes

# Define the path to the data directory
path = Path(__file__).parent.parent.parent.parent / "data/streamlit_data"

# --- Load data ---
@st.cache_data
def get_overview(path=path / "direct_train_overview.json"):
    return load_overview(path)

overview = get_overview()

# --- Dropdown Menu---
start = st.selectbox("Startbahnhof", sorted(overview.keys()))
end   = st.selectbox("Zielbahnhof",  sorted(overview.get(start, {}).keys()))

# --- Filters ---
st.markdown("**Filter**")
col1, col2, col3 = st.columns(3)
with col1:
    fern = st.checkbox("Fernverkehr", value=True)
with col2:
    nah  = st.checkbox("Nahverkehr",  value=True)
with col3:
    min_samp = st.checkbox("Mind. 20 Fahrten", value=True)

# --- Display DataFrame and Download Button ---
if start and end:
    df = load_route_df(start, end, overview)
    df_f = filter_routes(df, fern=fern, nah=nah, min_samples=min_samp)

    st.subheader(f"{start} → {end}")
    st.dataframe(df_f, use_container_width=True)

    json_str = df_f.to_json(orient="records", indent=2, force_ascii=False)
    st.download_button(
        "Route als JSON herunterladen",
        data=json_str,
        file_name=f"{start}_to_{end}.json",
        mime="application/json",
    )

# --- Footer ---
st.markdown("""
---
Datenbasis: Deutsche Bahn, gesammelt vom 2025-01-01 bis 2025-05-31.
""")