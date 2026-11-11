import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl
import pathlib
import json
import math
import requests
import datetime
from geopy.geocoders import Nominatim

# --- CONFIGURATION & UI THEMING ---
st.set_page_config(page_title="AATAP | Global Transit Portal", layout="wide", page_icon="🌍")

st.markdown("""
<style>
    .reportview-container { background: #f0f2f6; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .stButton>button { background-color: #0056b3; color: white; border-radius: 5px; width: 100%; }
    .stButton>button:hover { background-color: #004494; color: white; }
    h1 { color: #1f4e79; }
</style>
""", unsafe_allow_html=True)

# --- INTERNATIONALIZATION (i18n) ---
lang_dict = {
    "English": {
        "title": "🌍 Addis Ababa Transit Accessibility Portal",
        "desc": "This portal visualizes the **travel time** from any bus stop to key **Government Offices** during peak hours.",
        "controls": "Map Controls", "period": "Select Time Period",
        "am_peak": "Morning Peak (06:00 - 08:00)", "pm_peak": "Afternoon Peak (17:00 - 19:30)",
        "office": "Select a Government Office", "search": "Search Address or Landmark",
        "search_btn": "Find Location", "manual": "Manual Coordinates Entry",
        "lat": "Latitude", "lon": "Longitude", "calc_manual": "Calculate Coordinates",
        "analysis": "📍 Location Analysis", "nearest_stop": "Nearest Bus Stop",
        "walk_dist": "Walking Distance", "travel_time": "Travel Time",
        "export": "📥 Export Data to CSV", "table": "Data Table: Worst Performing Stops"
    },
    "አማርኛ (Amharic)": {
        "title": "🌍 የአዲስ አበባ ትራንዚት ተደራሽነት ፖርታል",
        "desc": "ይህ ፖርታል በጫና ሰዓታት ውስጥ ከማንኛውም የአውቶቡስ ማቆሚያ ወደ ዋና የመንግስት ቢሮዎች የሚወስደውን **የጉዞ ጊዜ** ያሳያል።",
        "controls": "የካርታ መቆጣጠሪያዎች", "period": "የጊዜ ገደብ ይምረጡ",
        "am_peak": "የጠዋት ጫና (06:00 - 08:00)", "pm_peak": "የከሰዓት ጫና (17:00 - 19:30)",
        "office": "የመንግስት ቢሮ ይምረጡ", "search": "አድራሻ ወይም ስፍራ ይፈልጉ",
        "search_btn": "ስፍራ ፈልግ", "manual": "በእጅ መጋጠሚያዎችን ማስገባት",
        "lat": "ኬክሮስ (Latitude)", "lon": "ኬንትሮስ (Longitude)", "calc_manual": "አስላ",
        "analysis": "📍 የስፍራ ትንተና", "nearest_stop": "በቅርብ የሚገኝ ማቆሚያ",
        "walk_dist": "የእግር ርቀት", "travel_time": "የጉዞ ጊዜ",
        "export": "📥 መረጃውን ወደ CSV አውርድ", "table": "የመረጃ ሰንጠረዥ፡ ከፍተኛ ጊዜ የሚወስዱ ማቆሚያዎች"
    },
    "Afaan Oromoo": {
        "title": "🌍 Portaala Qaqqabummaa Transit Finfinnee",
        "desc": "Portaalli kun yeroo ol'aantummaa hojii irratti **yeroo imalaa** buufata konkolaataa kamiyyuu irraa hanga waajjira mootummaa ijootti agarsiisa.",
        "controls": "To'annoo Kaartaa", "period": "Yeroo Filadhu",
        "am_peak": "Yeroo Ganamaa (06:00 - 08:00)", "pm_peak": "Yeroo Waaree (17:00 - 19:30)",
        "office": "Waajjira Mootummaa Filadhu", "search": "Teessoo ykn Bakka Barbaadi",
        "search_btn": "Bakka Argadhu", "manual": "Qindaa'ina Harkaan Galchuu",
        "lat": "Latitude", "lon": "Longitude", "calc_manual": "Qindaa'ina Herregi",
        "analysis": "📍 Xiinxala Bakka", "nearest_stop": "Buufata Konkolaataa Dhihoo",
        "walk_dist": "Fageenya Miilaa", "travel_time": "Yeroo Imalaa",
        "export": "📥 Odeeffannoo CSV Affeeri", "table": "Gabatee Odeeffannoo: Buufataalee Yeroo Dheeraa Fudhatan"
    },
    "ትግርኛ (Tigrinya)": {
        "title": "🌍 ፖርታል ተበጻሕነት መጓዓዝያ ኣዲስ ኣበባ",
        "desc": "እዚ ፖርታል እዚ ኣብ ግዜ ጫና **ግዜ መጓዓዝያ** ካብ ዝኾነ መዕረፍቲ ኣውቶቡስ ናብ ቀንዲ ቤት ጽሕፈት መንግስቲ ዝወስድ ግዜ የርኢ።",
        "controls": "ቁጽጽር ካርታ", "period": "ግዜ ምረጽ",
        "am_peak": "ግዜ ንግሆ (06:00 - 08:00)", "pm_peak": "ግዜ ምሸት (17:00 - 19:30)",
        "office": "ቤት ጽሕፈት መንግስቲ ምረጽ", "search": "ኣድራሻ ወይ ቦታ ድለ",
        "search_btn": "ቦታ ርኸብ", "manual": "ብኢድ መጋጠሚያ ኣእቱ",
        "lat": "Latitude", "lon": "Longitude", "calc_manual": "ሕሰብ",
        "analysis": "📍 ትንተና ቦታ", "nearest_stop": "ቀረባ መዕረፍቲ ኣውቶቡስ",
        "walk_dist": "ርሕቀት እግሪ", "travel_time": "ግዜ መጓዓዝያ",
        "export": "📥 ዳታ ናብ CSV ኣውርድ", "table": "ሰደቓ ዳታ፡ ዝያዳ ግዜ ዝወስዱ መዕረፍቲ"
    },
    "Soomaali (Somali)": {
        "title": "🌍 Bogga Helitaanka Gaadiidka Addis Ababa",
        "desc": "Boggani wuxuu muujinayaa **waqtiga safarka** ee laga bilaabo boostada bas kasta ilaa xafiisyada dowladda ee muhiimka ah inta lagu jiro saacadaha ciriiriga.",
        "controls": "Kontoroolka Khariidadda", "period": "Dooro Waqtiga",
        "am_peak": "Waqtiga Subaxa (06:00 - 08:00)", "pm_peak": "Waqtiga Galabta (17:00 - 19:30)",
        "office": "Dooro Xafiiska Dowladda", "search": "Raadi Cinwaanka ama Calaamadda",
        "search_btn": "Raadi Goobta", "manual": "Geli Isku-duwayaasha Gacanta",
        "lat": "Latitude", "lon": "Longitude", "calc_manual": "Xisaabi Isku-duwayaasha",
        "analysis": "📍 Falanqaynta Goobta", "nearest_stop": "Boostada Bas ee ugu dhow",
        "walk_dist": "Masaafada Lugta", "travel_time": "Waqtiga Safarka",
        "export": "📥 Dhoofi Xogta CSV", "table": "Shaxda Xogta: Boostadaha ugu Waqtiga Dheer"
    },
    "Sidaamu Afoo (Sidama)": {
        "title": "🌍 Addis Ababa Bus Rakkeessitu Borotaale",
        "desc": "Tenna borotaale **safara yannara** baala bus soorrate ledo daafira kifile ledo xaa yannara la'lo ledo assineerette.",
        "controls": "Kaarta Xaadisate", "period": "Yannara Doori",
        "am_peak": "Ganama Yannara (06:00 - 08:00)", "pm_peak": "Wolqa Yannara (17:00 - 19:30)",
        "office": "Kifile Xaadisate Doori", "search": "Axxiishsha woma Qoossooti Hinoosi",
        "search_btn": "Qoossooti Hinoosi", "manual": "Anga Ledo Xaadisate Hinoosi",
        "lat": "Latitude", "lon": "Longitude", "calc_manual": "Xaadisi",
        "analysis": "📍 Qoossote Xaadisate", "nearest_stop": "Bus Soorrate Dhiho",
        "walk_dist": "Lugo Soote", "travel_time": "Safara Yannara",
        "export": "📥 Xaadisate CSV Ani", "table": "Xaadisate Xaadisate: Baala Soorrate Yannara Dheere"
    },
    "Qafaraf (Afar)": {
        "title": "🌍 Addis Ababa Bus Oobiyyi Portaal",
        "desc": "Ta portaal **kusaq keeni** bus oobiyyi kinnih yan qusba baaxo dacayrih gexo kinnih yan.",
        "controls": "Kaarta Qussu", "period": "Kusaq Meqe",
        "am_peak": "Saqoo (06:00 - 08:00)", "pm_peak": "Korsa (17:00 - 19:30)",
        "office": "Qusba Baaxo Meqe", "search": "Baaxo Barbaadi",
        "search_btn": "Baaxo Gey", "manual": "Gaba Gacsa",
        "lat": "Latitude", "lon": "Longitude", "calc_manual": "Xisaab",
        "analysis": "📍 Baaxo Nummaysiyya", "nearest_stop": "Bus Oobiyyi Xexxaarah",
        "walk_dist": "Ibada Faxxa", "travel_time": "Kusaq Keeni",
        "export": "📥 CSV Baxsisi", "table": "Xaadise: Bus Oobiyyi Kaxxa Kusaq"
    },
    "Wolayttattuwa (Wolaytta)": {
        "title": "🌍 Addis Ababa Bus Lo'o Portaale",
        "desc": "Ha portaale **gezza hanida** bus lo'o xeeqqenna bessiyooshshata ubbaa giddon hanida.",
        "controls": "Kaartaa Xaadisate", "period": "Yannara Doora",
        "am_peak": "Ganama Yannara (06:00 - 08:00)", "pm_peak": "Wolqa Yannara (17:00 - 19:30)",
        "office": "Bessiyooshsha Doora", "search": "Axxiishsha Bessiyooshsha Hinoosa",
        "search_btn": "Bessiyooshsha Hinoosa", "manual": "Anga Ledo Xaadisate Hinoosa",
        "lat": "Latitude", "lon": "Longitude", "calc_manual": "Xaadisa",
        "analysis": "📍 Bessiyooshsha Xaadisate", "nearest_stop": "Bus Lo'o Dhiho",
        "walk_dist": "Lugo Soote", "travel_time": "Gezza Hanida",
        "export": "📥 Xaadisate CSV Ani", "table": "Xaadisate Xaadisate: Baala Soorrate Yannara Dheere"
    },
    "ጉራጌ (Gurage)": {
        "title": "🌍 የአዲስ አበባ ትራንዚት ተደራሽነት ፖርታል",
        "desc": "ይህ ፖርታል በጫና ሰዓታት ውስጥ ከማንኛውም የአውቶቡስ ማቆሚያ ወደ ዋና የመንግስት ቢሮዎች የሚወስደውን **የጉዞ ጊዜ** ያሳያል።",
        "controls": "የካርታ መቆጣጠሪያዎች", "period": "የጊዜ ገደብ ይምረጡ",
        "am_peak": "የጠዋት ጫና (06:00 - 08:00)", "pm_peak": "የከሰዓት ጫና (17:00 - 19:30)",
        "office": "የመንግስት ቢሮ ይምረጡ", "search": "አድራሻ ወይም ስፍራ ይፈልጉ",
        "search_btn": "ስፍራ ፈልግ", "manual": "በእጅ መጋጠሚያዎችን ማስገባት",
        "lat": "ኬክሮስ (Latitude)", "lon": "ኬንትሮስ (Longitude)", "calc_manual": "አስላ",
        "analysis": "📍 የስፍራ ትንተና", "nearest_stop": "በቅርብ የሚገኝ ማቆሚያ",
        "walk_dist": "የእግር ርቀት", "travel_time": "የጉዞ ጊዜ",
        "export": "📥 መረጃውን ወደ CSV አውርድ", "table": "የመረጃ ሰንጠረዥ፡ ከፍተኛ ጊዜ የሚወስዱ ማቆሚያዎች"
    },
    "Hadiyyisa (Hadiyya)": {
        "title": "🌍 Addis Ababa Bus Rakkeessitu Borotaale",
        "desc": "Tenna borotaale **safara yannara** baala bus soorrate ledo daafira kifile ledo xaa yannara la'lo ledo assineerette.",
        "controls": "Kaarta Xaadisate", "period": "Yannara Doori",
        "am_peak": "Ganama Yannara (06:00 - 08:00)", "pm_peak": "Wolqa Yannara (17:00 - 19:30)",
        "office": "Kifile Xaadisate Doori", "search": "Axxiishsha woma Qoossooti Hinoosi",
        "search_btn": "Qoossooti Hinoosi", "manual": "Anga Ledo Xaadisate Hinoosi",
        "lat": "Latitude", "lon": "Longitude", "calc_manual": "Xaadisi",
        "analysis": "📍 Qoossote Xaadisate", "nearest_stop": "Bus Soorrate Dhiho",
        "walk_dist": "Lugo Soote", "travel_time": "Safara Yannara",
        "export": "📥 Xaadisate CSV Ani", "table": "Xaadisate Xaadisate: Baala Soorrate Yannara Dheere"
    },
    "Gamo (Gamo)": {
        "title": "🌍 Addis Ababa Bus Lo'o Portaale",
        "desc": "Ha portaale **gezza hanida** bus lo'o xeeqqenna bessiyooshshata ubbaa giddon hanida.",
        "controls": "Kaartaa Xaadisate", "period": "Yannara Doora",
        "am_peak": "Ganama Yannara (06:00 - 08:00)", "pm_peak": "Wolqa Yannara (17:00 - 19:30)",
        "office": "Bessiyooshsha Doora", "search": "Axxiishsha Bessiyooshsha Hinoosa",
        "search_btn": "Bessiyooshsha Hinoosa", "manual": "Anga Ledo Xaadisate Hinoosa",
        "lat": "Latitude", "lon": "Longitude", "calc_manual": "Xaadisa",
        "analysis": "📍 Bessiyooshsha Xaadisate", "nearest_stop": "Bus Lo'o Dhiho",
        "walk_dist": "Lugo Soote", "travel_time": "Gezza Hanida",
        "export": "📥 Xaadisate CSV Ani", "table": "Xaadisate Xaadisate: Baala Soorrate Yannara Dheere"
    }
}

st.sidebar.header("🌐 Language / ቋንቋ")
lang_choice = st.sidebar.radio("Select Language", list(lang_dict.keys()))
L = lang_dict[lang_choice]

BASE_DIR = pathlib.Path(__file__).parent

# --- TITLE AND DEVELOPER INFO ---
# --- ADD LOGO AND PROFILE PHOTO ---
# Sidebar Logo
try:
    st.sidebar.image(str(BASE_DIR / 'assets' / 'logo.jpg'), use_container_width=True)
    st.sidebar.markdown("---")
except:
    pass

# Top Center Profile Photo
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    try:
        st.image(str(BASE_DIR / 'assets' / 'profile.jpg'), use_container_width=True)
    except:
        pass

st.markdown("---")
st.title(L["title"])

# Developer Info Callout Box
st.markdown("""
<div style="background-color:#f8f9fa; padding: 12px; border-radius: 8px; margin-bottom: 20px; border-left: 6px solid #1f4e79; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
    <b>Developed by:</b> Shimeles Tadesse Zelelew <br>
    📧 <b>Email:</b> <a href="mailto:shimtad2001g@gmail.com" style="color:#0056b3; text-decoration:none;">shimtad2001g@gmail.com</a> <br>
    🏢 Associate researcher @ Space Science and Geospatial Institute
</div>
""", unsafe_allow_html=True)

st.markdown(L["desc"])

st.sidebar.header(L["controls"])

period_choice = st.sidebar.radio(L["period"], [L["am_peak"], L["pm_peak"]])
period_code = "AMPK" if period_choice == L["am_peak"] else "PMPK"

@st.cache_data
def load_data(period_code):
    csv_path = BASE_DIR / 'data' / f'AATAP_ACC_MET_{period_code}_TAB_v1.0.csv'
    df = pd.read_csv(csv_path)
    stops_path = BASE_DIR / 'data' / 'stops.txt'
    stops = pd.read_csv(stops_path)
    df = df.merge(stops[['stop_id', 'stop_lat', 'stop_lon', 'stop_name']], on='stop_id')
    offices_path = BASE_DIR / 'data' / 'AATAP_GOVOFF_MET_SRC_TAB_v1.0.csv'
    offices = pd.read_csv(offices_path)
    return df, offices

try:
    df, offices = load_data(period_code)
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

office_list = df['office_name'].unique()
selected_office = st.sidebar.selectbox(L["office"], office_list)

office_data = df[df['office_name'] == selected_office].copy()
office_loc = offices[offices['office_name'] == selected_office].iloc[0]

st.sidebar.markdown("---")
st.sidebar.subheader(L["search"])
search_query = st.sidebar.text_input(L["search"], placeholder="e.g., Bole Airport")
if st.sidebar.button(L["search_btn"]):
    try:
        url = f"https://photon.komoot.io/api/?q={search_query}+Addis+Ababa+Ethiopia&limit=1"
        headers = {'User-Agent': 'AATAP-Portal/2.0'}
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        if data and 'features' in data and len(data['features']) > 0:
            coords = data['features'][0]['geometry']['coordinates']
            st.session_state.user_lon = coords[0]
            st.session_state.user_lat = coords[1]
            st.sidebar.success("Location found!")
        else:
            st.sidebar.error("Location not found. Try a different landmark.")
    except Exception as e:
        st.sidebar.error(f"Search failed: {str(e)}")

st.sidebar.markdown("---")
st.sidebar.subheader(L["manual"])
with st.sidebar.form("coord_form"):
    manual_lat = st.number_input(L["lat"], value=9.034722, format="%.6f")
    manual_lon = st.number_input(L["lon"], value=38.750833, format="%.6f")
    submit_coords = st.form_submit_button(L["calc_manual"])

if "user_lat" not in st.session_state:
    st.session_state.user_lat = None
    st.session_state.user_lon = None

if submit_coords:
    st.session_state.user_lat = manual_lat
    st.session_state.user_lon = manual_lon

st.subheader(f"Accessibility to: {selected_office}")
m = folium.Map(location=[office_loc['latitude'], office_loc['longitude']], zoom_start=12, tiles="OpenStreetMap")
LocateControl(auto_start=False).add_to(m)

folium.Marker(
    location=[office_loc['latitude'], office_loc['longitude']],
    popup=f"<b>{selected_office}</b><br>Type: {office_loc['office_type']}",
    icon=folium.Icon(color='black', icon='star', prefix='fa')
).add_to(m)

if st.session_state.user_lat is not None:
    folium.Marker(
        location=[st.session_state.user_lat, st.session_state.user_lon],
        icon=folium.Icon(color='red', icon='user', prefix='fa'),
        popup="Selected Location"
    ).add_to(m)

def get_color(time):
    if time <= 15: return '#00FF00'
    elif time <= 30: return '#FFFF00'
    elif time <= 45: return '#FFA500'
    elif time <= 60: return '#FF0000'
    else: return '#800080'

for idx, row in office_data.iterrows():
    folium.CircleMarker(
        location=[row['stop_lat'], row['stop_lon']],
        radius=3, color=get_color(row['travel_time_min']),
        fill=True, fill_color=get_color(row['travel_time_min']), fill_opacity=0.7,
        popup=f"<b>{row['stop_name']}</b><br>Travel Time: {row['travel_time_min']} mins"
    ).add_to(m)

legend_html = """
<div style="position: fixed; bottom: 50px; left: 50px; width: 220px; height: 220px; 
     background-color: white; border:2px solid grey; z-index:9999; font-size:14px;
     padding: 10px; border-radius: 5px; box-shadow: 2px 2px 5px rgba(0,0,0,0.5);">
     <b>Legend</b><br>
     <i class="fa fa-star" style="color:black"></i> Gov. Office<br>
     <i class="fa fa-user" style="color:red"></i> Selected Loc.<br><br>
     <i style="background:#00FF00; width:12px; height:12px; display:inline-block; border-radius:50%;"></i> ≤ 15 mins<br>
     <i style="background:#FFFF00; width:12px; height:12px; display:inline-block; border-radius:50%;"></i> 15 - 30 mins<br>
     <i style="background:#FFA500; width:12px; height:12px; display:inline-block; border-radius:50%;"></i> 30 - 45 mins<br>
     <i style="background:#FF0000; width:12px; height:12px; display:inline-block; border-radius:50%;"></i> 45 - 60 mins<br>
     <i style="background:#800080; width:12px; height:12px; display:inline-block; border-radius:50%;"></i> > 60 mins
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

map_data = st_folium(m, width=1200, height=500, returned_objects=["last_clicked"])

if map_data and map_data.get("last_clicked"):
    st.session_state.user_lat = map_data["last_clicked"]["lat"]
    st.session_state.user_lon = map_data["last_clicked"]["lng"]

if st.session_state.user_lat is not None:
    st.markdown("---")
    st.subheader(L["analysis"])
    
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371000
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
        return 2*R*math.atan2(math.sqrt(a), math.sqrt(1-a))

    office_data['dist_to_click'] = office_data.apply(
        lambda row: haversine(st.session_state.user_lat, st.session_state.user_lon, row['stop_lat'], row['stop_lon']), axis=1
    )
    nearest_stop = office_data.loc[office_data['dist_to_click'].idxmin()]
    
    col1, col2, col3 = st.columns(3)
    col1.metric(L["nearest_stop"], nearest_stop['stop_name'])
    col2.metric(L["walk_dist"], f"{nearest_stop['dist_to_click']:.0f} m")
    col3.metric(L["travel_time"], f"{nearest_stop['travel_time_min']} min")

st.markdown("---")
st.subheader(L["table"])
worst_stops = office_data.sort_values(by='travel_time_min', ascending=False).head(50)[['stop_name', 'travel_time_min']]
st.dataframe(worst_stops, use_container_width=True)

csv = worst_stops.to_csv(index=False).encode('utf-8')
st.download_button(
    label=L["export"],
    data=csv,
    file_name=f'AATAP_Worst_Stops_{period_code}.csv',
    mime='text/csv',
)


# --- MODEL VALIDATION METRICS ---
st.markdown("---")
st.subheader("🧠 AI Model Validation (Self-Supervised Learning)")
try:
    with open(BASE_DIR / 'data' / 'validation_metrics.json') as f:
        metrics = json.load(f)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("R² Score (Accuracy)", metrics['extrinsic']['r2'])
    col2.metric("RMSE (Error)", f"{metrics['extrinsic']['rmse']} min")
    col3.metric("MAE (Error)", f"{metrics['extrinsic']['mae']} min")
    
    st.info(f"**Intrinsic SSL Loss:** {metrics['intrinsic']['val_loss']} | "
            f"**Baseline RMSE:** {metrics['baseline']['rmse_distance']} min | "
            f"**Generalization RMSE (2026):** {metrics['generalization']['rmse_2026']} min")
except Exception as e:
    st.warning("Validation metrics not yet generated.")
# --- EXPANDED FOOTER WITH METADATA ---
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #555; font-size: 12px; line-height: 1.6; background-color: #eef2f5; padding: 15px; border-radius: 5px;">
    <b>Projection:</b> EPSG:32637 (WGS 84 / UTM Zone 37N) &nbsp;|&nbsp; 
    <b>Data Years:</b> 2025 &nbsp;|&nbsp; 
    <b>Data Types:</b> GTFS (.txt), Shapefile (.shp), GeoJSON, CSV<br>
    <b>Data Sources & Platforms:</b> DigitalTransport4Africa (GTFS), OpenStreetMap, BBBike, Streamlit Cloud, GitHub<br>
    <b>Validation Performed:</b> Self-supervised learning algorithm (Deep Learning)<br>
    <span style="color: #888; font-size: 11px;">Generated: {datetime.date.today()} | AATAP v2.0</span>
</div>
""", unsafe_allow_html=True)





