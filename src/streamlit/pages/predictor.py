from pathlib import Path
import streamlit as st
from src.streamlit.calculations.predict_helper import (
    load_overview,
    get_trains_for_route,
    predict_delay,
    predict_canceled,
)
from src.streamlit.calculations.predict_helper import (
    get_last_trips,
    get_typical_departure_time,
    get_weather_forecast_for_station_date,
)

# Define the path to the data directory
path = Path(__file__).parent.parent.parent.parent / "data/streamlit_data"


# --- Load data ---
@st.cache_data
def get_overview(path=path / "direct_train_overview.json"):
    return load_overview(str(path))


overview = get_overview()

# --- Select Route ---
col1, col2, col3 = st.columns([2, 2, 2])
with col1:
    start = st.selectbox("Startbahnhof", ["Bitte auswählen"] + sorted(overview.keys()))
with col2:
    end = st.selectbox(
        "Zielbahnhof",
        ["Bitte auswählen"] + sorted(overview.get(start, {}).keys()),
    )
with col3:
    trains = get_trains_for_route(start, end)
    if trains:
        selected_train = (
            st.selectbox("Zug", trains)
        )
    else:
        st.warning("Keine Direktverbindung gefunden.")
        st.stop()

st.divider()

date_col, filter_col = st.columns([2, 1])
# --- Select Date ---
with date_col:
    date = st.date_input("Datum", value=None)

# --- Filter Options ---

with filter_col:
    st.markdown("**Filter**")
    weather = st.checkbox("Wetterdaten einbeziehen", value=True)

# --- Display Prediction ---
if selected_train and date:
    from datetime import date as dt_date

    days_ahead = (date - dt_date.today()).days

    if days_ahead < 0:
        st.warning(
            "Das ausgewählte Datum liegt in der Vergangenheit. Bitte nutze für diese Anfrage die Verbindungs-Historie Seite."
        )
        st.stop()

    # --- Check Weather Data Availability ---
    use_weather = weather
    weather_data = None
    if weather and days_ahead > 16:
        st.warning(
            "Wetterdaten können nur für maximal 16 Tage im Voraus abgerufen werden. Die Vorhersage erfolgt ohne Wetterdaten."
        )
        use_weather = False
    elif weather:
        weather_data = get_weather_forecast_for_station_date(start, date)
        if weather_data is None:
            st.warning(
                "Keine Wetterdaten für diese Station und dieses Datum gefunden. Die Vorhersage erfolgt ohne Wetterdaten."
            )
            use_weather = False

    # --- Get Typical Departure Time ---
    time = get_typical_departure_time(start, end, selected_train, date)
    if time is None:
        st.warning(
            "Fehler bei der Abfahrtszeitbestimmung. Bitte überprüfen Sie die Eingaben oder wähle einen anderen Zug. Wenn das Problem weiterhin besteht, bitte ein Issue auf GitHub erstellen."
        )
    else:
        # --- Make Predictions ---
        prediction = predict_delay(
            start, end, selected_train, date, time, use_weather, weather_data
        )
        canceled_prob = predict_canceled(
            start,
            end,
            selected_train,
            date,
            time,
            prediction,
            use_weather,
            weather_data,
        )
        st.divider()
        st.markdown(f"### Prognosen für {start} → {end} am {date.strftime('%d.%m.%Y')}")
        st.success(f"Prognostizierte Verspätung: {prediction:.1f} Minuten")
        st.info(f"Prognostizierte Ausfallwahrscheinlichkeit: {canceled_prob:.2%}")
        st.divider()

        # --- Display Last Trips ---
        last_trips = get_last_trips(start, end, selected_train, date, time, n=5)
        st.markdown("**Die 5 Zugfahrten, die zeitlich am nächsten liegen:**")
        if last_trips is not None and not last_trips.empty:
            last_trips = last_trips.rename(
                columns={
                    "departure_time_origin": "Abfahrtszeit",
                    "delay_at_dest": "Verspätung am Ziel (min)",
                    "canceled": "Ausgefallen",
                }
            )
            last_trips["Ausgefallen"] = last_trips["Ausgefallen"].apply(
                lambda x: "Ja" if x == 1 else "Nein"
            )
            st.dataframe(last_trips)
        else:
            st.warning(
                "Keine Fahrtdaten gefunden. Bitte überprüfen Sie die Eingaben oder wählen Sie einen anderen Zug. Wenn das Problem weiterhin besteht, bitte ein Issue auf GitHub erstellen."
            )

# --- Footer ---
st.markdown(
    """
---
Datenbasis: Deutsche Bahn, gesammelt vom 2025-01-01 bis 2025-05-31.
"""
)
