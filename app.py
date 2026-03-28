import streamlit as st
import pandas as pd
import time
import json
import os
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="AIS Anomaly Detection",
    layout="wide"
)

st_autorefresh(interval=3000, key="flee_refresh")

st.title("Real Time AIS Intrusion & Anomaly Detection")
st.markdown("Singapore Strait")
st.divider()

json_path = os.path.join("data", "fleet_state.json")

def load_fleet_data():
    empty_state = {"green_fleet": [], "yellow_fleet": [], "red_fleet": []}
    
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            # Αν το αρχείο είναι μισογραμμένο εκείνη τη στιγμή, επιστρέφει κενό
            return empty_state
    else:
        # Αν δεν υπάρχει ακόμα το αρχείο, επιστρέφει κενό
        return empty_state

# Φορτώνουμε την τρέχουσα κατάσταση
state = load_fleet_data()

green_ships = state.get("green_fleet", [])
yellow_ships = state.get("yellow_fleet", [])
red_ships = state.get("red_fleet", [])

# --- 4. KPIs (ΜΕΤΡΗΤΕΣ ΚΟΡΥΦΗΣ) ---
# Φτιάχνουμε 3 στήλες
col1, col2, col3 = st.columns(3)

# Εμφανίζουμε τους μετρητές με τα σωστά χρώματα
with col1:
    st.metric(label="🟢 Green Fleet (Active)", value=len(green_ships))
with col2:
    st.metric(label="🟡 Yellow Fleet (Missing)", value=len(yellow_ships))
with col3:
    st.metric(label="🔴 Red Fleet (Anomalies)", value=len(red_ships), delta_color="inverse")

st.divider()

# --- 5. ΠΡΟΕΤΟΙΜΑΣΙΑ ΔΕΔΟΜΕΝΩΝ ΓΙΑ ΤΟΝ ΧΑΡΤΗ ---
all_ships_for_map = []

# Μαζεύουμε όλα τα πλοία και τους δίνουμε χρώμα βάσει του status
for s in green_ships:
    all_ships_for_map.append({"lat": s["lat"], "lon": s["lon"], "color": "#00FF00", "mmsi": s["mmsi"]})

for s in yellow_ships:
    all_ships_for_map.append({"lat": s["lat"], "lon": s["lon"], "color": "#FFFF00", "mmsi": s["mmsi"]})

for s in red_ships:
    all_ships_for_map.append({"lat": s["lat"], "lon": s["lon"], "color": "#FF0000", "mmsi": s["mmsi"]})

st.subheader("📍 Live Fleet Map")

# Αν υπάρχουν πλοία, ζωγραφίζουμε τον χάρτη!
if all_ships_for_map:
    map_df = pd.DataFrame(all_ships_for_map)
    # Η st.map() στην έκδοση >1.26 μπορεί να διαβάσει το 'color' column απευθείας!
    st.map(map_df, color="color")
else:
    st.info("Αναμονή για δεδομένα από το MOCK API... Ο χάρτης είναι άδειος.")

# --- 6. ΠΙΝΑΚΑΣ ALERTS ΓΙΑ ΤΗΝ ΚΟΚΚΙΝΗ ΛΙΣΤΑ ---
st.subheader("🚨 Active Alerts (Red Fleet Details)")

# Αν υπάρχουν ύποπτα πλοία, εμφανίζουμε πίνακα με λεπτομέρειες
if red_ships:
    # Φτιάχνουμε ένα DataFrame μόνο με τα στοιχεία που μας νοιάζουν για τον πίνακα
    alerts_df = pd.DataFrame(red_ships)
    
    # Επιλέγουμε και μετονομάζουμε τις στήλες για να φαίνονται ωραία
    alerts_to_show = alerts_df[["mmsi", "status", "lat", "lon", "speed"]]
    alerts_to_show.columns = ["MMSI", "Alert Type", "Latitude", "Longitude", "Last Known Speed (kn)"]
    
    # Εμφανίζουμε τον πίνακα σε όλο το πλάτος
    st.dataframe(alerts_to_show)
else:
    st.success("✅ Κανένα ύποπτο πλοίο αυτή τη στιγμή!")

# --- 7. FOOTER & MANUAL REFRESH ---
st.divider()
col_left, col_right = st.columns([4,1])
with col_left:
    st.caption(f"Τελευταία ενημέρωση JSON: {json_path}")
with col_right:
    # Κουμπί για χειροκίνητη ανανέωση αν βαριέσαι να περιμένεις το autorefresh
    if st.button("🔄 Manual Refresh"):
        st.rerun()