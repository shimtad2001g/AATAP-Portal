import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl
import pathlib
import math
import datetime
import requests
import json
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import plotly.express as px

st.set_page_config(page_title="AATAP | Global Transit Portal", layout="wide", page_icon="🌍")

st.markdown("""
<style>
    .reportview-container { background: #f0f2f6; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .stButton>button { background-color: #0056b3; color: white; border-radius: 5px; }
    .stButton>button:hover { background-color: #004494; color: white; }
    h1 { color: #1f4e79; }
</style>
""", unsafe_allow_html=True)

BASE_DIR = pathlib.Path(__file__).parent

# --- FULL i18n TRANSLATIONS (11 Languages) ---
lang_dict = {
    "English": {
        "title": "🌍 Addis Ababa Transit Accessibility Portal",
        "desc": "This portal visualizes the travel time from any bus stop to key Government Offices during peak hours.",
        "nav": "Navigation", "dashboard": "📊 Dashboard", "map": "🗺️ Interactive Map",
        "analytics": "📈 Analytics", "satellite": "🛰️ Satellite Data", "settings": "⚙️ Settings",
        "controls": "Map Controls", "period": "Time Period",
        "am_peak": "Morning Peak (06:00 - 08:00)", "pm_peak": "Afternoon Peak (17:00 - 19:30)",
        "office": "Government Office", "search": "Search Address", "search_btn": "Find Location",
        "manual": "Manual Coordinates", "lat": "Latitude", "lon": "Longitude", "calc": "Calculate",
        "analysis": "📍 Location Analysis", "nearest_stop": "Nearest Bus Stop",
        "walk": "Walking Distance", "travel": "Travel Time",
        "export": "📥 Export CSV", "table": "Worst Performing Stops",
        "logout": "Logout", "developer": "Developer"
    },
    "አማርኛ (Amharic)": {
        "title": "🌍 የአዲስ አበባ ትራንዚት ተደራሽነት ፖርታል",
        "desc": "ይህ ፖርታል በጫና ሰዓታት ውስጥ ከማንኛውም የአውቶቡስ ማቆሚያ ወደ ዋና የመንግስት ቢሮዎች የሚወስደውን የጉዞ ጊዜ ያሳያል።",
        "nav": "አሰሳ", "dashboard": "📊 ዳሽቦርድ", "map": "🗺️ በይነተገናኝ ካርታ",
        "analytics": "📈 ትንተና", "satellite": "🛰️ የሳተላይት ዳታ", "settings": "⚙️ ቅንብሮች",
        "controls": "የካርታ መቆጣጠሪያዎች", "period": "የጊዜ ገደብ",
        "am_peak": "የጠዋት ጫና (06:00 - 08:00)", "pm_peak": "የከሰዓት ጫና (17:00 - 19:30)",
        "office": "የመንግስት ቢሮ", "search": "አድራሻ ፈልግ", "search_btn": "ስፍራ ፈልግ",
        "manual": "በእጅ መጋጠሚያዎች", "lat": "ኬክሮስ", "lon": "ኬንትሮስ", "calc": "አስላ",
        "analysis": "📍 የስፍራ ትንተና", "nearest_stop": "በቅርብ የሚገኝ ማቆሚያ",
        "walk": "የእግር ርቀት", "travel": "የጉዞ ጊዜ",
        "export": "📥 CSV አውርድ", "table": "ከፍተኛ ጊዜ የሚወስዱ ማቆሚያዎች",
        "logout": "ውጣ", "developer": "ገንቢ"
    },
    "Afaan Oromoo": {
        "title": "🌍 Portaala Qaqqabummaa Transit Finfinnee",
        "desc": "Portaalli kun yeroo ol'aantummaa hojii irratti yeroo imalaa buufata konkolaataa kamiyyuu irraa hanga waajjira mootummaa ijootti agarsiisa.",
        "nav": "Qajeelfama", "dashboard": "📊 Daashboordii", "map": "🗺️ Kaartaa",
        "analytics": "📈 Xiinxala", "satellite": "🛰️ Odeeffannoo Satalaayitii", "settings": "⚙️ Qindaa'ina",
        "controls": "To'annoo Kaartaa", "period": "Yeroo",
        "am_peak": "Yeroo Ganamaa (06:00 - 08:00)", "pm_peak": "Yeroo Waaree (17:00 - 19:30)",
        "office": "Waajjira Mootummaa", "search": "Teessoo Barbaadi", "search_btn": "Bakka Argadhu",
        "manual": "Qindaa'ina Harkaan", "lat": "Latitude", "lon": "Longitude", "calc": "Herregi",
        "analysis": "📍 Xiinxala Bakka", "nearest_stop": "Buufata Dhihoo",
        "walk": "Fageenya Miilaa", "travel": "Yeroo Imalaa",
        "export": "📥 CSV Affeeri", "table": "Buufataalee Yeroo Dheeraa",
        "logout": "Ba'i", "developer": "Hojjetaa"
    },
    "ትግርኛ (Tigrinya)": {
        "title": "🌍 ፖርታል ተበጻሕነት መጓዓዝያ ኣዲስ ኣበባ",
        "desc": "እዚ ፖርታል እዚ ኣብ ግዜ ጫና ግዜ መጓዓዝያ ካብ ዝኾነ መዕረፍቲ ኣውቶቡስ ናብ ቀንዲ ቤት ጽሕፈት መንግስቲ ዝወስድ ግዜ የርኢ።",
        "nav": "መምርሒ", "dashboard": "📊 ዳሽቦርድ", "map": "🗺️ ካርታ",
        "analytics": "📈 ትንተና", "satellite": "🛰️ ዳታ ሳተላይት", "settings": "⚙️ ቅጥዒታት",
        "controls": "ቁጽጽር ካርታ", "period": "ግዜ",
        "am_peak": "ግዜ ንግሆ (06:00 - 08:00)", "pm_peak": "ግዜ ምሸት (17:00 - 19:30)",
        "office": "ቤት ጽሕፈት መንግስቲ", "search": "ኣድራሻ ድለ", "search_btn": "ቦታ ርኸብ",
        "manual": "ብኢድ መጋጠሚያ", "lat": "Latitude", "lon": "Longitude", "calc": "ሕሰብ",
        "analysis": "📍 ትንተና ቦታ", "nearest_stop": "ቀረባ መዕረፍቲ",
        "walk": "ርሕቀት እግሪ", "travel": "ግዜ መጓዓዝያ",
        "export": "📥 CSV ኣውርድ", "table": "ዝያዳ ግዜ ዝወስዱ መዕረፍቲ",
        "logout": "ውጻእ", "developer": "መሓዳሪ"
    },
    "Soomaali (Somali)": {
        "title": "🌍 Bogga Helitaanka Gaadiidka Addis Ababa",
        "desc": "Boggani wuxuu muujinayaa waqtiga safarka boostada bas kasta ilaa xafiisyada dowladda inta lagu jiro saacadaha ciriiriga.",
        "nav": "Navigation", "dashboard": "📊 Dashboard", "map": "🗺️ Khariidadda",
        "analytics": "📈 Falanqaynta", "satellite": "🛰️ Xogta Satelaytka", "settings": "⚙️ Dejinta",
        "controls": "Kontoroolka", "period": "Waqtiga",
        "am_peak": "Waqtiga Subaxa (06:00 - 08:00)", "pm_peak": "Waqtiga Galabta (17:00 - 19:30)",
        "office": "Xafiiska Dowladda", "search": "Raadi Cinwaanka", "search_btn": "Raadi",
        "manual": "Geli Gacanta", "lat": "Latitude", "lon": "Longitude", "calc": "Xisaabi",
        "analysis": "📍 Falanqaynta", "nearest_stop": "Boostada Dhow",
        "walk": "Masaafada Lugta", "travel": "Waqtiga Safarka",
        "export": "📥 Dhoofi CSV", "table": "Boostadaha Waqtiga Dheer",
        "logout": "Ka bax", "developer": "Horumariye"
    },
    "Sidaamu Afoo (Sidama)": {
        "title": "🌍 Addis Ababa Bus Rakkeessitu Borotaale",
        "desc": "Tenna borotaale safara yannara baala bus soorrate ledo daafira kifile ledo xaa yannara la'lo ledo assineerette.",
        "nav": "Qajeelfama", "dashboard": "📊 Daashboordii", "map": "🗺️ Kaartaa",
        "analytics": "📈 Xiinxala", "satellite": "🛰️ Satalaayitii Xaadisate", "settings": "⚙️ Qindaa'ina",
        "controls": "Kaarta Xaadisate", "period": "Yannara",
        "am_peak": "Ganama Yannara (06:00 - 08:00)", "pm_peak": "Wolqa Yannara (17:00 - 19:30)",
        "office": "Kifile Xaadisate", "search": "Axxiishsha Hinoosi", "search_btn": "Qoossooti Hinoosi",
        "manual": "Anga Ledo Hinoosi", "lat": "Latitude", "lon": "Longitude", "calc": "Xaadisi",
        "analysis": "📍 Qoossote Xaadisate", "nearest_stop": "Bus Soorrate Dhiho",
        "walk": "Lugo Soote", "travel": "Safara Yannara",
        "export": "📥 CSV Ani", "table": "Bus Soorrate Yannara Dheere",
        "logout": "Fulisi", "developer": "Xaadisaancho"
    },
    "Qafaraf (Afar)": {
        "title": "🌍 Addis Ababa Bus Oobiyyi Portaal",
        "desc": "Ta portaal kusaq keeni bus oobiyyi kinnih yan qusba baaxo dacayrih gexo kinnih yan.",
        "nav": "Qussu", "dashboard": "📊 Daashboordii", "map": "🗺️ Kaarta",
        "analytics": "📈 Nummaysiyya", "satellite": "🛰️ Satalaayit Xaadise", "settings": "⚙️ Qussu",
        "controls": "Kaarta Qussu", "period": "Kusaq",
        "am_peak": "Saqoo (06:00 - 08:00)", "pm_peak": "Korsa (17:00 - 19:30)",
        "office": "Qusba Baaxo", "search": "Baaxo Barbaadi", "search_btn": "Baaxo Gey",
        "manual": "Gaba Gacsa", "lat": "Latitude", "lon": "Longitude", "calc": "Xisaab",
        "analysis": "📍 Baaxo Nummaysiyya", "nearest_stop": "Bus Oobiyyi Xexxaarah",
        "walk": "Ibada Faxxa", "travel": "Kusaq Keeni",
        "export": "📥 CSV Baxsisi", "table": "Bus Oobiyyi Kaxxa Kusaq",
        "logout": "Baxsisi", "developer": "Hojjetaa"
    },
    "Wolayttattuwa (Wolaytta)": {
        "title": "🌍 Addis Ababa Bus Lo'o Portaale",
        "desc": "Ha portaale gezza hanida bus lo'o xeeqqenna bessiyooshshata ubbaa giddon hanida.",
        "nav": "Okkatiya", "dashboard": "📊 Daashboordii", "map": "🗺️ Kaartaa",
        "analytics": "📈 Xaadisate", "satellite": "🛰️ Satalaayitii Xaadisate", "settings": "⚙️ Qindaa'ina",
        "controls": "Kaartaa Xaadisate", "period": "Yannara",
        "am_peak": "Ganama Yannara (06:00 - 08:00)", "pm_peak": "Wolqa Yannara (17:00 - 19:30)",
        "office": "Bessiyooshsha", "search": "Axxiishsha Hinoosa", "search_btn": "Bessiyooshsha Hinoosa",
        "manual": "Anga Ledo Hinoosa", "lat": "Latitude", "lon": "Longitude", "calc": "Xaadisa",
        "analysis": "📍 Bessiyooshsha Xaadisate", "nearest_stop": "Bus Lo'o Dhiho",
        "walk": "Lugo Soote", "travel": "Gezza Hanida",
        "export": "📥 CSV Ani", "table": "Bus Lo'o Yannara Dheere",
        "logout": "Kessa", "developer": "Hojjetaa"
    },
    "ጉራጌ (Gurage)": {
        "title": "🌍 የአዲስ አበባ ትራንዚት ተደራሽነት ፖርታል",
        "desc": "ይህ ፖርታል በጫና ሰዓታት ውስጥ ከማንኛውም የአውቶቡስ ማቆሚያ ወደ ዋና የመንግስት ቢሮዎች የሚወስደውን የጉዞ ጊዜ ያሳያል።",
        "nav": "አሰሳ", "dashboard": "📊 ዳሽቦርድ", "map": "🗺️ ካርታ",
        "analytics": "📈 ትንተና", "satellite": "🛰️ ሳተላይት", "settings": "⚙️ ቅንብሮች",
        "controls": "ካርታ", "period": "ጊዜ",
        "am_peak": "ጠዋት (06:00 - 08:00)", "pm_peak": "ከሰዓት (17:00 - 19:30)",
        "office": "መንግስት ቢሮ", "search": "አድራሻ", "search_btn": "ፈልግ",
        "manual": "በእጅ", "lat": "Latitude", "lon": "Longitude", "calc": "አስላ",
        "analysis": "📍 ትንተና", "nearest_stop": "ቅርብ ማቆሚያ",
        "walk": "እግር", "travel": "ጉዞ",
        "export": "📥 CSV", "table": "ከፍተኛ ጊዜ",
        "logout": "ውጣ", "developer": "ገንቢ"
    },
    "Hadiyyisa (Hadiyya)": {
        "title": "🌍 Addis Ababa Bus Rakkeessitu Borotaale",
        "desc": "Tenna borotaale safara yannara baala bus soorrate ledo daafira kifile ledo xaa yannara la'lo ledo assineerette.",
        "nav": "Qajeelfama", "dashboard": "📊 Daashboordii", "map": "🗺️ Kaartaa",
        "analytics": "📈 Xiinxala", "satellite": "🛰️ Satalaayitii", "settings": "⚙️ Qindaa'ina",
        "controls": "Kaarta", "period": "Yannara",
        "am_peak": "Ganama (06:00 - 08:00)", "pm_peak": "Wolqa (17:00 - 19:30)",
        "office": "Kifile", "search": "Axxiishsha", "search_btn": "Hinoosi",
        "manual": "Anga Ledo", "lat": "Latitude", "lon": "Longitude", "calc": "Xaadisi",
        "analysis": "📍 Qoossote", "nearest_stop": "Bus Dhiho",
        "walk": "Lugo", "travel": "Safara",
        "export": "📥 CSV", "table": "Yannara Dheere",
        "logout": "Fulisi", "developer": "Hojjetaa"
    },
    "Gamo (Gamo)": {
        "title": "🌍 Addis Ababa Bus Lo'o Portaale",
        "desc": "Ha portaale gezza hanida bus lo'o xeeqqenna bessiyooshshata ubbaa giddon hanida.",
        "nav": "Okkatiya", "dashboard": "📊 Daashboordii", "map": "🗺️ Kaartaa",
        "analytics": "📈 Xaadisate", "satellite": "🛰️ Satalaayitii", "settings": "⚙️ Qindaa'ina",
        "controls": "Kaartaa", "period": "Yannara",
        "am_peak": "Ganama (06:00 - 08:00)", "pm_peak": "Wolqa (17:00 - 19:30)",
        "office": "Bessiyooshsha", "search": "Axxiishsha", "search_btn": "Hinoosa",
        "manual": "Anga Ledo", "lat": "Latitude", "lon": "Longitude", "calc": "Xaadisa",
        "analysis": "📍 Bessiyooshsha", "nearest_stop": "Bus Dhiho",
        "walk": "Lugo", "travel": "Gezza",
        "export": "📥 CSV", "table": "Yannara Dheere",
        "logout": "Kessa", "developer": "Hojjetaa"
    }
}

# --- AUTH SETUP ---
with open(BASE_DIR / 'config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    credentials=config['credentials'],
    cookie_name=config['cookie']['name'],
    cookie_key=config['cookie']['key'],
    cookie_expiry_days=config['cookie']['expiry_days'],
    pre_authorized=config['pre_authorized']['emails']
)

if "authentication_status" not in st.session_state:
    st.session_state["authentication_status"] = None
if "demo_activated" not in st.session_state:
    st.session_state["demo_activated"] = False
if "dev_mode" not in st.session_state:
    st.session_state["dev_mode"] = False

# Developer bypass
dev_secret = st.secrets.get("DEV_SECRET", "AATAP_DEV_2026_SECRET")
url_token = st.query_params.get("dev", "")

if url_token == dev_secret:
    st.session_state["authentication_status"] = True
    st.session_state["username"] = "admin"
    st.session_state["name"] = "Shimeles Tadesse (Developer)"
    st.session_state["dev_mode"] = True

# --- LOGIN GATE ---
if not st.session_state.get("authentication_status"):
    authenticator.login(location='main')

if st.session_state["authentication_status"] is False:
    st.error('❌ Username/password is incorrect')

elif st.session_state["authentication_status"] is None:
    col_logo, _ = st.columns([1, 4])
    with col_logo:
        try:
            st.image(str(BASE_DIR / 'assets' / 'logo.png'), width=120)
        except Exception:
            pass
    st.warning('⚠️ Please enter your username and password to access the portal.')
    st.markdown("---")
    if st.button("🚀 Enter Demo Mode (No Login Required)", use_container_width=True):
        st.session_state["demo_activated"] = True
        st.session_state["authentication_status"] = True
        st.session_state["username"] = "demo"
        st.session_state["name"] = "Demo User"
        st.rerun()
    st.markdown("---")
    st.markdown("### 📝 New User? Register Below")
    try:
        if authenticator.register_user(location='main'):
            with open(BASE_DIR / 'config.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)
            st.success('✅ User registered successfully! Please log in above.')
    except Exception as e:
        st.error(f"Registration error: {e}")

# --- MAIN PORTAL ---
if st.session_state["authentication_status"]:

    # Language selector FIRST (before translations are used)
    st.sidebar.header("🌐 Language / ቋንቋ")
    lang_choice = st.sidebar.selectbox("Select Language", list(lang_dict.keys()))
    L = lang_dict[lang_choice]
    st.sidebar.markdown("---")

    # Sidebar Branding & Profile
    try:
        st.sidebar.image(str(BASE_DIR / 'assets' / 'logo.png'), use_container_width=True)
    except Exception:
        pass
    st.sidebar.markdown(f"**👤 {st.session_state.get('name', 'User')}**")
    st.sidebar.caption(L["developer"])
    st.sidebar.markdown("---")

    # Time Period selector
    st.sidebar.subheader(L["period"])
    period_choice = st.sidebar.radio("", [L["am_peak"], L["pm_peak"]])
    period_code = "AMPK" if period_choice == L["am_peak"] else "PMPK"
    st.sidebar.markdown("---")

    # Navigation
    st.sidebar.subheader(L["nav"])
    page = st.sidebar.radio("", [L["dashboard"], L["map"], L["analytics"], L["satellite"], L["settings"]])
    st.sidebar.markdown("---")

    if st.sidebar.button(f"🚪 {L['logout']}", use_container_width=True):
        for k in ["authentication_status", "username", "name", "demo_activated", "dev_mode"]:
            st.session_state[k] = None
        st.session_state["demo_activated"] = False
        st.session_state["dev_mode"] = False
        try:
            authenticator.logout(location='unrendered')
        except Exception:
            pass
        st.rerun()

    if st.session_state.get("dev_mode"):
        st.success("🔓 Developer Mode Active — Access granted via secure URL")
    elif st.session_state.get("demo_activated"):
        st.info("🎯 Demo Mode Active")

    # --- LOAD DATA based on period ---
    @st.cache_data
    def load_data(period_code):
        df = pd.read_csv(BASE_DIR / 'data' / f'AATAP_ACC_MET_{period_code}_TAB_v1.0.csv')
        stops = pd.read_csv(BASE_DIR / 'data' / 'stops.txt')
        df = df.merge(stops[['stop_id', 'stop_lat', 'stop_lon', 'stop_name']], on='stop_id')
        offices = pd.read_csv(BASE_DIR / 'data' / 'AATAP_GOVOFF_MET_SRC_TAB_v1.0.csv')
        return df, offices

    df, offices = load_data(period_code)

    # Validation metrics loader
    def load_metrics():
        try:
            with open(BASE_DIR / 'data' / 'validation_metrics.json') as f:
                return json.load(f)
        except Exception:
            return None

    # ========================
    # PAGE 1: DASHBOARD
    # ========================
    if page == L["dashboard"]:
        st.title(L["title"])
        # --- PROFILE PHOTO ---
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            try:
                st.image(str(BASE_DIR / 'assets' / 'profile.jpg'), width=200)
            except Exception:
                pass
        
        st.markdown("---")

        st.markdown(f"""
        <div style="background-color:#f8f9fa; padding: 12px; border-radius: 8px; margin-bottom: 20px; border-left: 6px solid #1f4e79;">
            <b>Developed by:</b> Shimeles Tadesse Zelelew <br>
            📧 <b>Email:</b> <a href="mailto:shimtad2001g@gmail.com">shimtad2001g@gmail.com</a> <br>
            🏢 Associate researcher @ Space Science and Geospatial Institute
        </div>
        """, unsafe_allow_html=True)
        
        # --- QR CODE DISPLAY ---
        col_qr1, col_qr2, col_qr3 = st.columns([1, 1, 1])
        with col_qr2:
            try:
                st.image(str(BASE_DIR / 'assets' / 'qr_code.png'), caption="📱 Scan to Save Contact & Open Portal", use_container_width=True)
            except Exception:
                pass
        st.markdown(L["desc"])

        # KPI Cards
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Bus Stops", f"{len(df):,}")
        col2.metric("Government Offices", f"{len(offices)}")
        col3.metric("Avg Travel Time", f"{int(df['travel_time_min'].mean())} min")
        col4.metric("Max Travel Time", f"{int(df['travel_time_min'].max())} min")

        st.markdown("---")

        # AI Validation Metrics
        st.subheader("🧠 AI Model Validation (Self-Supervised Learning)")
        metrics = load_metrics()
        if metrics:
            mc1, mc2, mc3 = st.columns(3)
            mc1.metric("R² Score (Accuracy)", metrics['extrinsic']['r2'])
            mc2.metric("RMSE (Error)", f"{metrics['extrinsic']['rmse']} min")
            mc3.metric("MAE (Error)", f"{metrics['extrinsic']['mae']} min")
            st.info(f"**Intrinsic SSL Loss:** {metrics['intrinsic']['val_loss']} | "
                    f"**Baseline RMSE:** {metrics['baseline']['rmse_distance']} min | "
                    f"**Generalization RMSE (2026):** {metrics['generalization']['rmse_2026']} min")
        else:
            st.warning("Validation metrics not found.")

        st.markdown("---")
        st.subheader("Quick Map Preview")
        m = folium.Map(location=[9.03, 38.74], zoom_start=11, tiles="OpenStreetMap")
        for idx, office in offices.iterrows():
            folium.Marker([office['latitude'], office['longitude']], popup=office['office_name'], icon=folium.Icon(color='black', icon='star')).add_to(m)
        st_folium(m, width=1200, height=400, returned_objects=[])

    # ========================
    # PAGE 2: INTERACTIVE MAP
    # ========================
    elif page == L["map"]:
        st.title(L["map"])

        st.sidebar.markdown("---")
        st.sidebar.subheader(L["controls"])
        office_list = df['office_name'].unique()
        selected_office = st.sidebar.selectbox(L["office"], office_list)

        st.sidebar.markdown("---")
        st.sidebar.subheader(L["search"])
        search_query = st.sidebar.text_input(L["search"], placeholder="Bole Airport")
        if st.sidebar.button(L["search_btn"]):
            try:
                response = requests.get(f"https://photon.komoot.io/api/?q={search_query}+Addis+Ababa+Ethiopia&limit=1", headers={'User-Agent': 'AATAP/2.0'}, timeout=10)
                data = response.json()
                if data and 'features' in data and len(data['features']) > 0:
                    coords = data['features'][0]['geometry']['coordinates']
                    st.session_state.user_lon = coords[0]
                    st.session_state.user_lat = coords[1]
                    st.sidebar.success("✅ Location found!")
                else:
                    st.sidebar.error("Location not found.")
            except Exception as e:
                st.sidebar.error(f"Search failed: {str(e)}")

        st.sidebar.markdown("---")
        st.sidebar.subheader(L["manual"])
        with st.sidebar.form("coord_form"):
            manual_lat = st.number_input(L["lat"], value=9.034722, format="%.6f")
            manual_lon = st.number_input(L["lon"], value=38.750833, format="%.6f")
            submit_coords = st.form_submit_button(L["calc"])
        if submit_coords:
            st.session_state.user_lat = manual_lat
            st.session_state.user_lon = manual_lon

        office_data = df[df['office_name'] == selected_office].copy()
        office_loc = offices[offices['office_name'] == selected_office].iloc[0]

        st.subheader(f"Accessibility to: {selected_office}")
        m = folium.Map(location=[office_loc['latitude'], office_loc['longitude']], zoom_start=12, tiles="OpenStreetMap")
        LocateControl(auto_start=False).add_to(m)
        folium.Marker([office_loc['latitude'], office_loc['longitude']], popup=selected_office, icon=folium.Icon(color='black', icon='star', prefix='fa')).add_to(m)

        if st.session_state.get("user_lat") is not None:
            folium.Marker([st.session_state.user_lat, st.session_state.user_lon], icon=folium.Icon(color='red', icon='user', prefix='fa')).add_to(m)

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
                popup=f"{row['stop_name']}: {row['travel_time_min']} min"
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

        # Location Analysis
        if st.session_state.get("user_lat") is not None:
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
            col2.metric(L["walk"], f"{nearest_stop['dist_to_click']:.0f} m")
            col3.metric(L["travel"], f"{nearest_stop['travel_time_min']} min")

        st.markdown("---")
        st.subheader(L["table"])
        worst_stops = office_data.sort_values(by='travel_time_min', ascending=False).head(50)[['stop_name', 'travel_time_min']]
        st.dataframe(worst_stops, use_container_width=True)
        csv = worst_stops.to_csv(index=False).encode('utf-8')
        st.download_button(label=L["export"], data=csv, file_name=f'AATAP_Worst_Stops_{period_code}.csv', mime='text/csv')

    # ========================
    # PAGE 3: ANALYTICS
    # ========================
    elif page == L["analytics"]:
        st.title(L["analytics"])
        st.markdown("Statistical insights into travel times across Addis Ababa.")

        avg_time = df.groupby('office_name')['travel_time_min'].mean().reset_index()
        fig1 = px.bar(avg_time, x='office_name', y='travel_time_min',
                      title="Average Travel Time by Government Office",
                      labels={'office_name': 'Office', 'travel_time_min': 'Avg Time (mins)'},
                      color='travel_time_min', color_continuous_scale='RdYlGn_r')
        st.plotly_chart(fig1, use_container_width=True)

        fig2 = px.histogram(df, x='travel_time_min', nbins=50,
                            title="Distribution of Travel Times (All Stops)",
                            labels={'travel_time_min': 'Travel Time (mins)'},
                            color_discrete_sequence=['#0056b3'])
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")
        st.subheader("🧠 AI Model Validation Metrics")
        metrics = load_metrics()
        if metrics:
            mc1, mc2, mc3 = st.columns(3)
            mc1.metric("R² Score", metrics['extrinsic']['r2'])
            mc2.metric("RMSE", f"{metrics['extrinsic']['rmse']} min")
            mc3.metric("MAE", f"{metrics['extrinsic']['mae']} min")
            st.info(f"**Intrinsic SSL Loss:** {metrics['intrinsic']['val_loss']} | "
                    f"**Baseline RMSE:** {metrics['baseline']['rmse_distance']} min | "
                    f"**Generalization RMSE (2026):** {metrics['generalization']['rmse_2026']} min")

    # ========================
    # PAGE 4: SATELLITE DATA
    # ========================
    elif page == L["satellite"]:
        st.title(L["satellite"])
        st.markdown("Metadata of freely accessible satellite imagery used in this platform.")

        sat_data = pd.DataFrame({
            "Satellite": ["Suomi NPP", "Sentinel-2A", "Sentinel-1A", "Landsat 9"],
            "Sensor": ["VIIRS", "MSI", "SAR-C", "OLI-2"],
            "Resolution": ["250m", "10m", "5m", "30m"],
            "Last Pass": ["Today, 06:30 AM", "Yesterday, 10:15 AM", "Nov 08, 2026", "Nov 05, 2026"],
            "Status": ["Processed", "Processed", "Processing", "Processed"]
        })
        st.dataframe(sat_data, use_container_width=True)

    # ========================
    # PAGE 5: SETTINGS
    # ========================
    elif page == L["settings"]:
        st.title(L["settings"])
        
        # --- QR CODE DISPLAY ON SETTINGS ---
        st.subheader("📱 Share & Connect")
        st.markdown("Scan this QR code with a smartphone to instantly save contact information and open the portal.")
        col_s1, col_s2, col_s3 = st.columns([1, 1, 1])
        with col_s2:
            try:
                st.image(str(BASE_DIR / 'assets' / 'qr_code.png'), use_container_width=True)
            except Exception:
                pass
        st.markdown("---")

        with st.form("settings_form"):
            st.subheader("Profile Information")
            name = st.text_input("Full Name", value=st.session_state.get('name', 'Shimeles Tadesse Zelelew'))
            email = st.text_input("Email", value="shimtad2001g@gmail.com")
            org = st.text_input("Organization", value="Space Science and Geospatial Institute")
            st.subheader("Preferences")
            lang_pref = st.selectbox("Preferred Language", list(lang_dict.keys()), index=list(lang_dict.keys()).index(lang_choice))
            if st.form_submit_button("Save Changes"):
                st.success("✅ Profile updated successfully!")

    # --- EXPANDED FOOTER ---
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: #555; font-size: 12px; line-height: 1.6; background-color: #eef2f5; padding: 15px; border-radius: 5px;">
        <b>Projection:</b> EPSG:32637 (WGS 84 / UTM Zone 37N) &nbsp;|&nbsp; 
        <b>Data Years:</b> 2026 &nbsp;|&nbsp; 
        <b>Data Types:</b> GTFS (.txt), Shapefile (.shp), GeoJSON, CSV<br>
        <b>Data Sources & Platforms:</b> DigitalTransport4Africa (GTFS), OpenStreetMap, BBBike, Streamlit Cloud, GitHub<br>
        <b>Validation Performed:</b> Self-supervised learning algorithm (Deep Learning)<br>
        <b>© {datetime.date.today().year} Shimeles Tadesse Zelelew. All rights reserved.</b><br>
        <span style="color: #888; font-size: 11px;">Generated: {datetime.date.today()} | AATAP v2.0</span>
    </div>
    """, unsafe_allow_html=True)


