import streamlit as st
import requests
import json
import pandas as pd
import streamlit_lottie as st_lottie
from openai import AzureOpenAI
import urllib.parse
from datetime import datetime
from rapidfuzz import process, fuzz

# ==============================================================================
# 1. CORE CONFIGURATION & ENTERPRISE DESIGN LAYOUT
# ==============================================================================
st.set_page_config(
    page_title="CoastPulse AI — Maritime Telemetry Engine",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Minimal UI Style Sheet Injection
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #f8fafc;
        color: #0f172a;
    }

    .main-header {
        background-color: #ffffff;
        padding: 25px 35px;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        margin-bottom: 25px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    .disambiguation-box {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 25px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
    }

    .result-card {
        border-radius: 16px;
        padding: 35px;
        color: white;
        margin-top: 10px;
        box-shadow: 0 10px 25px rgba(15, 23, 42, 0.1);
        background-size: cover;
        background-position: center;
        position: relative;
        min-height: 240px;
    }
    .card-overlay {
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(15, 23, 42, 0.75);
        border-radius: 16px;
        z-index: 1;
    }
    .card-content { position: relative; z-index: 2; }

    .status-badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge-safe { background-color: #10b981; color: white; }
    .badge-caution { background-color: #f59e0b; color: white; }
    .badge-danger { background-color: #ef4444; color: white; }

    .planner-card {
        background-color: white;
        padding: 16px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.01);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1 style="margin: 0; font-size: 28px; font-weight: 700; color: #0f172a;">CoastPulse AI</h1>
    <p style="margin: 5px 0 0 0; font-size: 14px; color: #64748b;">
        Real-Time Marine Sensor Telemetry Analytics & Dynamic Coastal Safety Assessment Interface
    </p>
</div>
""", unsafe_allow_html=True)

# Comprehensive Global Coastal Countries Dictionary
GLOBAL_COUNTRIES = {
    "Select Country Context": "",
    "India": "in", "Indonesia": "id", "Maldives": "mv", "Thailand": "th", "Sri Lanka": "lk",
    "United States": "us", "Australia": "au", "United Kingdom": "gb", "France": "fr", "Spain": "es",
    "Italy": "it", "Greece": "gr", "Portugal": "pt", "Japan": "jp", "Philippines": "ph",
    "Malaysia": "my", "Vietnam": "vn", "Brazil": "br", "Mexico": "mx", "Canada": "ca",
    "South Africa": "za", "New Zealand": "nz", "Egypt": "eg", "United Arab Emirates": "ae", "Oman": "om",
    "Saudi Arabia": "sa", "Turkey": "tr", "Croatia": "hr", "Norway": "no", "Denmark": "dk",
    "Netherlands": "nl", "Belgium": "be", "Ireland": "ie", "Singapore": "sg", "Mauritius": "mu",
    "Seychelles": "sc", "Fiji": "fj", "Bahamas": "bs", "Jamaica": "jm", "Barbados": "bb"
}

st.sidebar.markdown("### 📊 Operational Parameters")
selected_country = st.sidebar.selectbox("Country Jurisdiction Sector:", list(GLOBAL_COUNTRIES.keys()))
user_input = st.sidebar.text_input("Coastal Target / Beach Location Name:",
                                   placeholder="e.g., Jampore Beach, Bali, Goa").strip()
skill_level = st.sidebar.selectbox("Traveler Swimming Skill Matrix:",
                                   ["Beginner / Casual Wader", "Intermediate Swimmer", "Advanced / Surfer"])


# ==============================================================================
# 2. SERVICE FUNCTIONS WITH EXPLICIT DEPENDENCY INCORPORATION
# ==============================================================================

@st.cache_data(ttl=3600, show_spinner=False)
def get_spatial_coordinates(query_string, country_name, country_iso):
    """Fetches spatial mappings and ranks them dynamically using RapidFuzz logic loops."""
    nominatim_query = f"{query_string}, {country_name}" if country_name != "Select Country Context" else query_string
    headers = {"User-Agent": "CoastPulseMarineSafetyApp/3.0 (contact@coastpulse.ai)"}
    osm_url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote_plus(nominatim_query)}&format=json&addressdetails=1&limit=5"

    try:
        osm_res = requests.get(osm_url, headers=headers, timeout=8).json()
        if not osm_res: return []

        scored_candidates = []
        for candidate in osm_res:
            score = 0
            c_type = candidate.get("type", "").lower()
            c_class = candidate.get("class", "").lower()
            c_address = candidate.get("address", {})
            c_code = c_address.get("country_code", "").lower()

            # --- RAPIDFUZZ FUZZY MATCHING BLOCK ---
            display_name = candidate.get("display_name", "")
            label_title = display_name.split(",")[0].strip()

            # Extract ratio weights via token sort mapping
            fuzzy_ratio = fuzz.token_sort_ratio(query_string.lower(), label_title.lower())
            score += (fuzzy_ratio * 0.3)

            # Maritime Booster Rules (Beach-Aware Search Tuning)
            if c_type in ["beach", "coast", "bay", "sea", "ocean"] or c_class in ["coastline", "natural", "water"]:
                score += 45
            elif c_type in ["city", "town", "island"]:
                score += 15

            if country_iso and c_code == country_iso.lower():
                score += 40
            elif country_iso and c_code != country_iso.lower():
                score -= 60

            scored_candidates.append({"data": candidate, "score": score})

        scored_candidates = sorted(scored_candidates, key=lambda x: x["score"], reverse=True)
        return [item["data"] for item in scored_candidates if item["score"] > -5]
    except:
        return []


@st.cache_data(ttl=1800, show_spinner=False)
def get_marine_telemetry(lat, lon):
    """Fetches real-time wave predictions from global Open-Meteo arrays."""
    try:
        marine_url = f"https://marine-api.open-meteo.com/v1/marine?latitude={lat}&longitude={lon}&hourly=wave_height&daily=wave_height_max&timezone=auto"
        return requests.get(marine_url, timeout=6).json()
    except:
        return None


def analyze_safety_with_openai(loc_name, country, wave_height, skill_grade):
    """Executes structured telemetry evaluations via Azure OpenAI pipeline."""
    try:
        client = AzureOpenAI(
            api_key=st.secrets["AZURE_OPENAI_API_KEY"],
            api_version="2024-02-01",
            azure_endpoint=st.secrets["AZURE_OPENAI_ENDPOINT"]
        )

        user_payload = f"""
        Compute safety risk profile matrix parameters for:
        Target Node Location: {loc_name}, {country}
        Sensor Wave Swell Context: {wave_height} meters
        Tourist/User Competency Rating: {skill_grade}

        Return a strict raw valid JSON block string containing exactly these key attributes (no backticks, no wrapping):
        {{
            "status": "SAFE" or "CAUTION" or "CLOSED BY AUTHORITY",
            "bg_type": "safe" or "caution" or "danger",
            "description": "A clean short paragraph highlighting security metrics and risk boundaries for the traveler."
        }}
        """

        response = client.chat.completions.create(
            model=st.secrets.get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o"),
            messages=[
                {"role": "system",
                 "content": "You are an internal automated maritime telemetry safety auditor engine."},
                {"role": "user", "content": user_payload}
            ],
            max_tokens=250,
            temperature=0.1
        )

        raw_content = response.choices[0].message.content.strip()
        if raw_content.startswith("```json"):
            raw_content = raw_content.split("```json")[1].split("```")[0].strip()
        elif raw_content.startswith("```"):
            raw_content = raw_content.split("```")[1].split("```")[0].strip()

        return json.loads(raw_content)
    except:
        if wave_height > 1.8:
            return {"status": "CLOSED BY AUTHORITY", "bg_type": "danger",
                    "description": "High swell parameters exceed local safety thresholds."}
        elif wave_height > 1.1:
            return {"status": "CAUTION", "bg_type": "caution",
                    "description": "Moderate marine currents active. Watch deep lines closely."}
        else:
            return {"status": "SAFE", "bg_type": "safe",
                    "description": "Calm coastal behavior validated. Sea optimization values ideal."}


# ==============================================================================
# 3. CONTROL STREAM PIPELINE MECHANICS
# ==============================================================================

if "selected_location_data" not in st.session_state:
    st.session_state.selected_location_data = None
if "previous_query" not in st.session_state:
    st.session_state.previous_query = ""

if user_input != st.session_state.previous_query:
    st.session_state.selected_location_data = None
    st.session_state.previous_query = user_input

if not user_input:
    st.info(
        "💡 Pro Tip: Select country parameters and input your target beach destination to load live geo-spatial tracking matrix loops.")

if user_input:
    country_iso = GLOBAL_COUNTRIES[selected_country]

    if st.session_state.selected_location_data is None:
        candidates = get_spatial_coordinates(user_input, selected_country, country_iso)

        if candidates:
            st.markdown('<div class="disambiguation-box">', unsafe_allow_html=True)
            st.markdown("🎯 **High-accuracy spatial targets identified. Confirm specific node mapping:**")

            for idx, item in enumerate(candidates):
                d_name = item.get("display_name", "")
                addr = item.get("address", {})

                title = d_name.split(",")[0].strip()
                region = addr.get("state", addr.get("region", addr.get("province", "")))
                ctx_country = addr.get("country", "")

                label = f"📍 {title}"
                if region: label += f", {region}"
                if ctx_country: label += f" ({ctx_country})"

                if st.button(label, key=f"spatial_btn_{idx}"):
                    st.session_state.selected_location_data = {
                        "name": title, "latitude": float(item["lat"]), "longitude": float(item["lon"]),
                        "country": ctx_country, "admin1": region
                    }
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.error("No valid high-confidence geographic targets matching filter matrix boundaries found.")

    # CORE DATA RESOLUTION FOR REASONING RENDERING
    if st.session_state.selected_location_data is not None:
        loc = st.session_state.selected_location_data
        lat, lon = loc["latitude"], loc["longitude"]
        loc_name, country_name = loc["name"], loc["country"]
        full_display = f"{loc_name}, {loc['admin1']}, {country_name}" if loc[
            'admin1'] else f"{loc_name}, {country_name}"

        marine_data = get_marine_telemetry(lat, lon)

        if marine_data:
            wave_height = 0.0
            daily_max_forecasts = []
            forecast_dates = []

            if "hourly" in marine_data and "wave_height" in marine_data["hourly"]:
                times = marine_data["hourly"]["time"]
                heights = [h if h is not None else 0.0 for h in marine_data["hourly"]["wave_height"]]
                now_naive = datetime.now()
                closest_idx = min(range(len(times)),
                                  key=lambda i: abs(datetime.fromisoformat(times[i].replace("Z", "")) - now_naive))
                wave_height = heights[closest_idx]

            if "daily" in marine_data and "wave_height_max" in marine_data["daily"]:
                daily_max_forecasts = [w if w is not None else 0.0 for w in marine_data["daily"]["wave_height_max"]]
                forecast_dates = marine_data["daily"].get("time", [])

            analysis = analyze_safety_with_openai(loc_name, country_name, wave_height, skill_level)
            status = analysis.get("status", "SAFE")
            bg_type = analysis.get("bg_type", "safe")
            ai_desc = analysis.get("description", "")

            if bg_type == "danger":
                badge, img = "badge-danger", "https://images.unsplash.com/photo-1505118380757-91f5f5632de0?auto=format&fit=crop&w=1200&q=80"
            elif bg_type == "caution":
                badge, img = "badge-caution", "https://images.unsplash.com/photo-1519046904884-53103b34b206?auto=format&fit=crop&w=1200&q=80"
            else:
                badge, img = "badge-safe", "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80"

            st.markdown(f"""
                <div class="result-card" style="background-image: url('{img}');">
                    <div class="card-overlay"></div>
                    <div class="card-content">
                        <span class="status-badge {badge}">{status}</span>
                        <h2 style="margin-top:12px; color:white; font-weight:700; font-size:24px;">Current Risk Profile: {full_display}</h2>
                        <p style="font-size:15px; line-height:1.5; color:#f1f5f9; max-width:680px; margin-top:10px;">{ai_desc}</p>
                        <hr style="border-color:rgba(255,255,255,0.12); margin:18px 0;">
                        <p style="font-size:11px; color:#cbd5e1; margin:0;">🛰️ Data Arrays Sync — Lat: {lat:.4f}, Lon: {lon:.4f} | Measured Wave Swell: {wave_height:.2f}m</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>### 📅 Predictive 7-Day Planning Framework", unsafe_allow_html=True)
            cols = st.columns(7)
            for day_idx in range(min(7, len(daily_max_forecasts))):
                p_date = datetime.strptime(forecast_dates[day_idx], "%Y-%m-%d")
                max_w = daily_max_forecasts[day_idx]

                if status == "CLOSED BY AUTHORITY" or max_w > 2.0:
                    d_lbl, d_clr, d_win = "🚫 RISK", "#ef4444", "High Swells"
                elif max_w > 1.2:
                    d_lbl, d_clr, d_win = "🟡 CAUTION", "#f59e0b", "Shallow Water"
                else:
                    d_lbl, d_clr, d_win = "🟢 OPTIMAL", "#10b981", "9 AM - 4 PM"

                with cols[day_idx]:
                    st.markdown(f"""
                    <div class="planner-card">
                        <strong style="font-size:14px; color:#1e3a8a;">{p_date.strftime("%A")}</strong><br>
                        <span style="font-size:11px; color:#64748b;">{p_date.strftime("%b %d")}</span>
                        <p style="margin:8px 0; font-size:12px; font-weight:700; color:{d_clr};">{d_lbl} ({max_w:.2f}m)</p>
                        <span style="font-size:11px; color:#475569;">Window:<br><strong>{d_win}</strong></span>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.error("Failed to retrieve metrics parameters from Open-Meteo telemetry stream.")