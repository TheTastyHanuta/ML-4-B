from pathlib import Path
import streamlit as st
from datetime import date as dt_date
from src.streamlit.calculations.predict_helper import (
    load_overview,
    get_trains_for_route,
    predict_delay,
    predict_canceled,
    get_typical_departure_time,
    get_weather_forecast_for_station_date,
)

# --- Load data ---
path = Path(__file__).parent.parent.parent.parent / "data/streamlit_data"


@st.cache_data
def get_overview(path=path / "direct_train_overview.json"):
    return load_overview(path) # type: ignore


overview = get_overview()

# --- User Inputs ---
col1, col2 = st.columns(2)
with col1:
    start = st.selectbox("Startbahnhof", ["Bitte auswählen"] + sorted(overview.keys()))
    if start == "Bitte auswählen":
        start = None
with col2:
    end = st.selectbox(
        "Zielbahnhof",
        ["Bitte auswählen"] + sorted(overview.get(start, {}).keys()),
    )
    if end == "Bitte auswählen":
        end = None

st.divider()

col3, col4 = st.columns([2, 1])
with col3:
    date = st.date_input("Datum", value=None)

st.divider()

with col4:
    st.markdown("**Filter**")
    weather = st.checkbox("Wetterdaten einbeziehen", value=True)

# --- Prediction Table ---
if start and end and date:
    st.markdown(f"### Prognosen für {start} → {end} am {date.strftime('%d.%m.%Y')}")

    with st.status("Erstelle Vorhersagen...", expanded=True) as status:
        st.write("Direktverbindungen laden...")

        trains = get_trains_for_route(start, end)

        if not trains:
            st.warning("Keine Direktverbindungen gefunden.")
            status.update(label="Keine Direktverbindungen gefunden.", state="error", expanded=False)
            st.stop()
        else:
            rows = []
            days_ahead = (date - dt_date.today()).days

            if days_ahead < 0:
                st.warning(
                    "Das ausgewählte Datum liegt in der Vergangenheit. Bitte nutze für diese Anfrage die Verbindungs-Historie Seite."
                )
                status.update(label="Datum liegt in der Vergangenheit.", state="error", expanded=False)
                st.stop()

            # Check if weather data can be used
            use_weather = weather and days_ahead <= 16
            weather_data = None

            if weather and days_ahead > 16:
                st.warning(
                    "Wetterdaten stehen nur für max. 16 Tage in der Zukunft zur Verfügung. Es wird ohne Wetterdaten vorhergesagt."
                )
            elif weather:
                st.write("Wetterdaten abrufen...")
                weather_data = get_weather_forecast_for_station_date(start, date)
                if weather_data is None:
                    st.warning(
                        "Keine Wetterdaten gefunden. Prognose erfolgt ohne Wetterdaten."
                    )
                    use_weather = False

            st.write("Treffe Vorhersagen...")
            progress_bar = st.progress(0, text="Treffe Vorhersagen...")
            total = len(trains)
            # Iterate over trains and make predictions
            for train in trains:
                progress_bar.progress(
                    (trains.index(train) + 1) / total,
                    text=f"Treffe Vorhersagen für {train}...",
                )
                time = get_typical_departure_time(start, end, train, date)
                if time is None:
                    continue
                delay = predict_delay(
                    start, end, train, date, time, use_weather, weather_data
                )
                cancel_prob = predict_canceled(
                    start, end, train, date, time, delay, use_weather, weather_data
                )
                # Append the results to the rows list
                rows.append(
                    {
                        "Zug": train,
                        "Abfahrtszeit": time.strftime("%H:%M"),
                        "Prognose: Verspätung am Ziel": f"{delay:.1f}",
                        "Prognose: Ausfallwahrscheinlichkeit": f"{cancel_prob:.2%}",
                    }
                )
            progress_bar.empty()
            status.update(label="Vorhersagen erstellt", state = "complete", expanded=False)

    # Display Dataframe
    if rows:
        import pandas as pd
        df = pd.DataFrame(rows)

        st.dataframe(df, use_container_width=True)
    else:
        st.info("Keine gültigen Fahrtdaten vorhanden für diese Auswahl.")

st.markdown(
    """
---
Datenbasis: Deutsche Bahn, gesammelt vom 2024-08-01 bis 2025-06-30. Modelle vom 16.07.2025.
"""
)
