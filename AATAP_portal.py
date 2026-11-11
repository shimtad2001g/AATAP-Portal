import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os
import pathlib

BASE_DIR = pathlib.Path(__file__).parent

st.set_page_config(page_title="AATAP - Addis Transit Portal", layout="wide", page_icon="🚌")

st.title("🚌 Addis Ababa Transit Accessibility Portal")
st.markdown("""
This portal visualizes the **travel time** from any bus stop to key **Government Offices** during peak hours. 
Use the sidebar to filter by time of day and select a specific government office.
""")

st.sidebar.header("Map Controls")
period = st.sidebar.radio("Select Time Period:", ["Morning Peak (06:00 - 08:00)", "Afternoon Peak (17:00 - 19:30)"])
period_code = "AMPK" if "Morning" in period else "PMPK"

@st.cache_data
def load_data(period_code):
    csv_path = BASE_DIR / 'data' / f'AATAP_ACC_MET_{period_code}_TAB_v1.0.csv'
    df = pd.read_csv(csv_path)
    stops = pd.read_csv('BASE_DIR / 'data' / stops.txt')
    df = df.merge(stops[['stop_id', 'stop_lat', 'stop_lon', 'stop_name']], on='stop_id')
    offices = pd.read_csv('BASE_DIR / 'data' / AATAP_GOVOFF_MET_SRC_TAB_v1.0.csv')
    return df, offices

df, offices = load_data(period_code)

office_list = df['office_name'].unique()
selected_office = st.sidebar.selectbox("Select a Government Office:", office_list)

office_data = df[df['office_name'] == selected_office].copy()
office_loc = offices[offices['office_name'] == selected_office].iloc[0]

st.subheader(f"Accessibility to: {selected_office}")
st.markdown(f"**Peak Period:** {period} | **Total Reachable Bus Stops:** {len(office_data)}")

m = folium.Map(location=[office_loc['latitude'], office_loc['longitude']], zoom_start=12, tiles="CartoDB positron")

folium.Marker(
    location=[office_loc['latitude'], office_loc['longitude']],
    popup=f"<b>{selected_office}</b><br>Type: {office_loc['office_type']}",
    icon=folium.Icon(color='black', icon='star', prefix='fa')
).add_to(m)

def get_color(time):
    if time <= 15: return '#00FF00'
    elif time <= 30: return '#FFFF00'
    elif time <= 45: return '#FFA500'
    elif time <= 60: return '#FF0000'
    else: return '#800080'

for idx, row in office_data.iterrows():
    color = get_color(row['travel_time_min'])
    folium.CircleMarker(
        location=[row['stop_lat'], row['stop_lon']],
        radius=3,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.7,
        popup=f"<b>{row['stop_name']}</b><br>Travel Time: {row['travel_time_min']} mins"
    ).add_to(m)

st_folium(m, width=1200, height=600)

st.subheader("Data Table: Worst Performing Stops")
st.dataframe(office_data.sort_values(by='travel_time_min', ascending=False).head(20)[['stop_name', 'travel_time_min']])

