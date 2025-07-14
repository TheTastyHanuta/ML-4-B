import pandas as pd
import streamlit as st
from src.streamlit.calculations.worst_trains_helper import (
    load_all_trains, 
    get_train_type,
    filter_trains,
    format_display_data,
    get_top_trains
)

# Main page
st.markdown("Hier siehst Du alle verfügbaren Züge aus dem gesamten Datensatz, unabhängig von der Route.")

# Load all train data
with st.spinner("Lade alle Zugdaten..."):
    df_all = load_all_trains()

if df_all.empty:
    st.error("Keine Zugdaten gefunden!")
    st.stop()

# Add train type column
df_all['Zugtyp'] = df_all['Zug'].apply(get_train_type)

# Filter options
st.subheader("🔍 Filter")
col1, col2, col3 = st.columns(3)

with col1:
    # Train name search
    train_search = st.text_input(
        "🔎 Zugname suchen:",
        placeholder="z.B. ICE 1, RE 3, FLX 10...",
        help="Suche nach spezifischen Zügen"
    )

with col2:
    selected_train_types = st.multiselect(
        "Zugtyp",
        options=["Fernverkehr", "Nahverkehr", "Sonstige"],
        default=["Fernverkehr", "Nahverkehr", "Sonstige"]
    )

with col3:
    min_samples = st.number_input(
        "Mindest-Stichprobengröße",
        min_value=1,
        max_value=int(df_all['Stichprobengröße'].max()),
        value=20,
        step=1
    )

# Sorting options
st.subheader("📈 Sortierung")
col1, col2 = st.columns(2)

with col1:
    sort_column = st.selectbox(
        "Sortieren nach",
        options=[
            "Verspätung Ankunft [min]",
            "Verspätung Abfahrt [min]",
            "Ausfallquote [%]",
            "Fahrzeit inkl. Verspätungen [min]",
            "Stichprobengröße"
        ],
        index=0
    )

with col2:
    sort_ascending = st.selectbox(
        "Reihenfolge",
        options=["Absteigend (schlechteste zuerst)", "Aufsteigend (beste zuerst)"],
        index=0
    ) == "Aufsteigend (beste zuerst)"

# Apply filters
df_filtered = filter_trains(df_all, selected_train_types, min_samples, train_search)

# Apply sorting
df_filtered = df_filtered.sort_values(sort_column, ascending=sort_ascending)

# Display results
st.subheader(f"🚂 Gefilterte Züge ({len(df_filtered)} von {len(df_all)})")

if not df_filtered.empty:
    # Format data for display
    df_display = format_display_data(df_filtered)
    
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True
    )
    
    # Download button
    csv_data = df_display.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="📥 Als CSV herunterladen",
        data=csv_data,
        file_name=f"alle_zuege_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
    
    # Top 10 lists
    st.subheader("🏆 Top 10 Listen")
    
    col1, col2 = st.columns(2)
    
    top_delayed, top_cancelled = get_top_trains(df_filtered)
    
    with col1:
        st.markdown("**🚨 Züge mit höchster Verspätung**")
        if top_delayed is not None:
            st.dataframe(top_delayed, hide_index=True)
        else:
            st.info("Keine Züge mit Verspätungsdaten verfügbar")
    
    with col2:
        st.markdown("**❌ Züge mit höchster Ausfallquote**")
        st.dataframe(top_cancelled, hide_index=True)

else:
    st.warning("Keine Züge entsprechen den aktuellen Filterkriterien.")

# Footer
st.markdown("""
---
**Datenbasis:** Deutsche Bahn, gesammelt vom 2025-01-01 bis 2025-05-31.  
**Hinweis:** Die Daten zeigen alle verfügbaren Direktverbindungen zwischen den Bahnhöfen im Datensatz.
""")