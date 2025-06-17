from pathlib import Path
import streamlit as st
from src.streamlit.calculations.predict_helper import load_overview, get_trains_for_route, predict_delay, predict_canceled
from src.streamlit.calculations.predict_helper import get_last_trips, get_typical_departure_time, get_weather_forecast_for_station_date

# Define the path to the data directory
path = Path(__file__).parent.parent.parent.parent / "data/streamlit_data"

st.set_page_config(page_title="Vorhersagen", layout="wide")
st.title("Zug Vorhersagen")

# --- Load data ---
@st.cache_data
def get_overview(path=path / "direct_train_overview.json"):
    return load_overview(path)

overview = get_overview()

# --- Select Route ---
col1, col2, col3 = st.columns([2,2,2])
with col1:
    start = st.selectbox("Startbahnhof", sorted(overview.keys()))
with col2:
    end = st.selectbox("Zielbahnhof", sorted(overview.get(start, {}).keys()))
with col3:
    trains = get_trains_for_route(start, end)
    selected_train = st.selectbox("Zug", trains) if trains else st.warning("Keine Direktverbindung gefunden.")

st.divider()

# --- Select Date ---
date = st.date_input("Datum", value=None)

st.divider()

# --- Filter Options ---
filter_col, _ = st.columns([1,3])
with filter_col:
    st.markdown("**Filter**")
    weather = st.checkbox("Wetterdaten einbeziehen", value=True)

st.divider()

# --- Display Prediction ---
if selected_train and date:
    from datetime import date as dt_date
    days_ahead = (date - dt_date.today()).days
    use_weather = weather
    weather_data = None
    if weather and days_ahead > 16:
        st.warning("Wetterdaten können nur für maximal 16 Tage im Voraus abgerufen werden. Die Vorhersage erfolgt ohne Wetterdaten.")
        use_weather = False
    elif weather:
        weather_data = get_weather_forecast_for_station_date(start, date)
        if weather_data is None:
            st.warning("Keine Wetterdaten für diese Station und dieses Datum gefunden. Die Vorhersage erfolgt ohne Wetterdaten.")
            use_weather = False
    time = get_typical_departure_time(start, end, selected_train, date)
    if time is None:
        st.warning("Fehler bei der Abfahrtszeitbestimmung. Bitte überprüfen Sie die Eingaben oder wähle einen anderen Zug. Wenn das Problem weiterhin besteht, bitte ein Issue auf GitHub erstellen.")
    else:
        prediction = predict_delay(start, end, selected_train, date, time, use_weather, weather_data)
        st.success(f"Prognostizierte Verspätung: {prediction:.1f} Minuten")
        st.divider()
        canceled_prob = predict_canceled(start, end, selected_train, date, time, prediction, use_weather, weather_data)
        st.info(f"Prognostizierte Ausfallwahrscheinlichkeit: {canceled_prob:.2%}")

        # --- Display Last Trips ---
        last_trips = get_last_trips(start, end, selected_train, date, time, n=5)
        st.markdown("**Die 5 Zugfahrten, die zeitlich am nächsten liegen:**")
        if last_trips is not None and not last_trips.empty:
            last_trips = last_trips.rename(columns={
                'departure_time_origin': 'Abfahrtszeit',
                'delay_at_dest': 'Verspätung am Ziel (min)',
                'canceled': 'Ausgefallen'
            })
            last_trips['Ausgefallen'] = last_trips['Ausgefallen'].apply(lambda x: 'Ja' if x == 1 else 'Nein')
            st.dataframe(last_trips)
        else:
            st.warning("Keine Fahrtdaten gefunden. Bitte überprüfen Sie die Eingaben oder wählen Sie einen anderen Zug. Wenn das Problem weiterhin besteht, bitte ein Issue auf GitHub erstellen.")

# --- Footer ---
st.markdown("""
---
Datenbasis: Deutsche Bahn, gesammelt vom 2025-01-01 bis 2025-05-31.
""")