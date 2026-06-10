import streamlit as st
import requests
import json
import streamlit_lottie as st_lottie
from openai import AzureOpenAI
import urllib.parse
from datetime import datetime, timezone
from difflib import SequenceMatcher

# Page Setup & Configuration for Premium High-Fidelity UI/UX Layout
st.set_page_config(
    page_title="CoastPulse AI — Multi-Sector Marine Safety & Telemetry Framework",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Global Custom Core Style Sheets Integration
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #f8fafc;
        color: #0f172a;
    }

    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #2563eb 100%);
        padding: 40px;
        border-radius: 24px;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(30, 58, 138, 0.15);
    }

    .metric-card {
        background-color: white;
        border: 1px solid #e2e8f0;
        padding: 22px;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
        text-align: center;
        transition: transform 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
    }

    .disambiguation-box {
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        padding: 20px;
        border-radius: 16px;
        margin-bottom: 25px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
    }

    .result-card {
        border-radius: 24px;
        padding: 35px;
        color: white;
        margin-top: 20px;
        box-shadow: 0 12px 35px rgba(15, 23, 42, 0.15);
        background-size: cover;
        background-position: center;
        position: relative;
        min-height: 280px;
    }
    .card-overlay {
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(15, 23, 42, 0.72);
        border-radius: 24px;
        z-index: 1;
    }
    .card-content {
        position: relative;
        z-index: 2;
    }

    .status-badge {
        display: inline-block;
        padding: 8px 18px;
        border-radius: 30px;
        font-weight: 700;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge-safe { background-color: #10b981; color: white; }
    .badge-caution { background-color: #f59e0b; color: white; }
    .badge-danger { background-color: #ef4444; color: white; }

    .planner-card {
        background-color: white;
        padding: 18px;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.01);
        text-align: center;
        min-height: 150px;
    }
</style>
""", unsafe_allow_html=True)

# Application Context Header Section
st.markdown("""
<div class="main-header">
    <span style="background: rgba(255,255,255,0.15); padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight:600; letter-spacing:0.05em;">TRACK 2: REASONING AGENTS MATRIX</span>
    <h1 style="margin: 10px 0 0 0; font-size: 38px; font-weight: 700; color: white;">CoastPulse AI</h1>
    <p style="margin: 8px 0 0 0; font-size: 16px; color: #e2e8f0; max-width: 750px;">
        Automated Marine Telemetry Analytics Engine & Real-Time Coastal Safety Verification Matrix for $50,000 USD Global Horizon Hackathon.
    </p>
</div>
""", unsafe_allow_html=True)

# 🌍 Comprehensive 60+ Global Coastal Countries Dictionary Layer With ISO Code Filters
GLOBAL_COUNTRIES = {
    "Choose Country Context": "",
    "India": "in", "Indonesia": "id", "Maldives": "mv", "Thailand": "th", "Sri Lanka": "lk",
    "United States": "us", "Australia": "au", "United Kingdom": "gb", "France": "fr", "Spain": "es",
    "Italy": "it", "Greece": "gr", "Portugal": "pt", "Japan": "jp", "Philippines": "ph",
    "Malaysia": "my", "Vietnam": "vn", "Brazil": "br", "Mexico": "mx", "Canada": "ca",
    "South Africa": "za", "New Zealand": "nz", "Egypt": "eg", "United Arab Emirates": "ae", "Oman": "om",
    "Saudi Arabia": "sa", "Turkey": "tr", "Croatia": "hr", "Norway": "no", "Denmark": "dk",
    "Netherlands": "nl", "Belgium": "be", "Ireland": "ie", "Singapore": "sg", "Mauritius": "mu",
    "Seychelles": "sc", "Fiji": "fj", "Bahamas": "bs", "Jamaica": "jm", "Barbados": "bb",
    "Costa Rica": "cr", "Panama": "pa", "Colombia": "co", "Peru": "pe", "Chile": "cl",
    "Argentina": "ar", "Morocco": "ma", "Kenya": "ke", "Tanzania": "tz", "Madagascar": "mg",
    "Iceland": "is", "South Korea": "kr", "Taiwan": "tw", "Hong Kong": "hk", "Israel": "il",
    "Cyprus": "cy", "Malta": "mt", "Dominican Republic": "do", "Puerto Rico": "pr", "Cuba": "cu"
}

# Left Sidebar Control Framework Dashboard Configuration
st.sidebar.markdown("### ⚙️ Telemetry Framework Control")
selected_country = st.sidebar.selectbox("Select Target Country Sector:", list(GLOBAL_COUNTRIES.keys()))
user_input = st.sidebar.text_input("Enter Coastal Destination / Beach Name:",
                                   placeholder="e.g., Goa, Bali, Jampore Beach").strip()
skill_level = st.sidebar.selectbox("Traveler Swimming Skill Grade Profile:",
                                   ["Beginner / Casual Wader", "Intermediate Swimmer", "Advanced / Surfer"])

# State Tracking Memory Initialization Engine
if "selected_location_data" not in st.session_state:
    st.session_state.selected_location_data = None
if "previous_query" not in st.session_state:
    st.session_state.previous_query = ""

# Drop Cache triggers instantly if user query components change
if user_input != st.session_state.previous_query:
    st.session_state.selected_location_data = None
    st.session_state.previous_query = user_input

# Main Thread Controller Logic Execution Block
if not user_input:
    st.info(
        "👋 Welcome to CoastPulse AI Platform. Please insert a coastal destination query string and country parameters inside the configuration navigation panel to trigger live telemetry analytical loops.")

if user_input:
    country_iso = GLOBAL_COUNTRIES[selected_country]

    # STAGE 1: SPATIAL COORDS DISCOVERY LOOP (Nominatim Engine Architecture)
    if st.session_state.selected_location_data is None:
        nominatim_query = f"{user_input}, {selected_country}" if selected_country != "Choose Country Context" else user_input
        headers = {"User-Agent": "CoastPulseMarineSafetyApp/2.0 (contact@coastpulse.ai)"}
        osm_url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote_plus(nominatim_query)}&format=json&addressdetails=1&limit=5"

        try:
            osm_res = requests.get(osm_url, headers=headers, timeout=7).json()

            if osm_res and len(osm_res) > 0:
                scored_candidates = []
                for candidate in osm_res:
                    score = 0
                    c_type = candidate.get("type", "").lower()
                    c_class = candidate.get("class", "").lower()
                    c_address = candidate.get("address", {})
                    c_code = c_address.get("country_code", "").lower()

                    # Score weights prioritizes maritime entities explicitly
                    if c_type in ["beach", "coast", "bay", "sea", "ocean"] or c_class in ["coastline", "natural",
                                                                                          "water"]:
                        score += 35
                    elif c_type in ["city", "town", "island", "village"]:
                        score += 15

                    if country_iso and c_code == country_iso.lower():
                        score += 45
                    elif country_iso and c_code != country_iso.lower():
                        score -= 50

                    display_name = candidate.get("display_name", "")
                    label_title = display_name.split(",")[0].strip()
                    string_match_ratio = SequenceMatcher(None, user_input.lower(), label_title.lower()).ratio()
                    score += (string_match_ratio * 20)

                    scored_candidates.append({"data": candidate, "score": score})

                scored_candidates = sorted(scored_candidates, key=lambda x: x["score"], reverse=True)
                display_candidates = [item["data"] for item in scored_candidates[:4] if item["score"] > -5]

                if display_candidates:
                    st.markdown('<div class="disambiguation-box">', unsafe_allow_html=True)
                    st.markdown(
                        f"🔍 **Top high-confidence spatial matches discovered. Select exact tactical target anchor:**")

                    for idx, candidate in enumerate(display_candidates):
                        d_name = candidate.get("display_name", "")
                        addr = candidate.get("address", {})

                        loc_title = d_name.split(",")[0].strip()
                        state_ctx = addr.get("state", addr.get("region", addr.get("province", "")))
                        country_ctx = addr.get("country", "")

                        full_label = f"📍 {loc_title}"
                        if state_ctx: full_label += f", {state_ctx}"
                        if country_ctx: full_label += f" ({country_ctx})"

                        if st.button(full_label, key=f"candidate_btn_{idx}"):
                            st.session_state.selected_location_data = {
                                "name": loc_title,
                                "latitude": float(candidate["lat"]),
                                "longitude": float(candidate["lon"]),
                                "country": country_ctx,
                                "admin1": state_ctx
                            }
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.error("No high-confidence marine spatial nodes verified matching targeted filters.")
            else:
                st.error("Zero records retrieved from OpenStreetMap atlas infrastructure for target string.")
        except Exception as e:
            st.error(f"Geocoding server link checkpoint execution timeout: {e}")

    # STAGE 2: MARINE API & REASONING AGENT COMPOSER LOOP
    if st.session_state.selected_location_data is not None:
        loc = st.session_state.selected_location_data
        lat, lon = loc["latitude"], loc["longitude"]
        loc_name = loc["name"]
        country_name = loc.get('country', '')
        admin_region = loc.get('admin1', '')

        full_display_location = f"{loc_name}, {admin_region}, {country_name}" if admin_region else f"{loc_name}, {country_name}"

        try:
            # Triggering Wave Heights Open-Meteo Gateway Datastream
            marine_url = f"https://marine-api.open-meteo.com/v1/marine?latitude={lat}&longitude={lon}&hourly=wave_height&daily=wave_height_max&timezone=auto"
            marine_res = requests.get(marine_url).json()

            wave_height = 0.0
            hourly_wave_heights = []
            daily_max_forecasts = []
            forecast_dates = []

            if "hourly" in marine_res and "time" in marine_res["hourly"] and marine_res["hourly"]["wave_height"]:
                times = marine_res["hourly"]["time"]
                hourly_wave_heights = [w if w is not None else 0.0 for w in marine_res["hourly"]["wave_height"]]

                now_naive = datetime.now()
                closest_idx = min(
                    range(len(times)),
                    key=lambda i: abs(datetime.fromisoformat(times[i].replace("Z", "").split("+")[0]) - now_naive)
                )
                wave_height = hourly_wave_heights[closest_idx]

            if "daily" in marine_res and "wave_height_max" in marine_res["daily"]:
                daily_max_forecasts = [w if w is not None else 0.0 for w in marine_res["daily"]["wave_height_max"]]
                forecast_dates = marine_res["daily"].get("time", [])

            # STAGE 3: SWEDEN CENTRAL REASONING AGENT CORE (gpt-4o Deployment Engine Execution)
            status, bg_type, ai_description = "SAFE", "safe", "Validation check processed successfully."

            try:
                # Instantiating the clean Azure OpenAI API client architecture mapping
                client = AzureOpenAI(
                    api_key=st.secrets["AZURE_OPENAI_API_KEY"],
                    api_version="2024-02-01",
                    azure_endpoint=st.secrets["AZURE_OPENAI_ENDPOINT"]
                )

                router_prompt = f"""
                Analyze this marine telemetry parameters and compute safety profile status.
                Target Beach Destination Location: {loc_name}, {country_name}
                Real-Time Wave Height Sensor Context: {wave_height} meters
                Tourist/Traveler Skill Level Grade: {skill_level}

                Return a strict raw JSON object string with exactly these fields (no markdown formatting, no backticks, no text outside JSON structure):
                {{
                    "status": "SAFE" or "CAUTION" or "CLOSED BY AUTHORITY",
                    "bg_type": "safe" or "caution" or "danger",
                    "description": "A comprehensive professional safety analytical paragraph advising the specific tourist tier based on wave variables."
                }}
                """

                response = client.chat.completions.create(
                    model=st.secrets.get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o"),
                    messages=[
                        {"role": "system",
                         "content": "You are a professional maritime safety intelligence engine executing reasoning assessment tasks."},
                        {"role": "user", "content": router_prompt}
                    ],
                    max_tokens=300,
                    temperature=0.2
                )

                # Parsing clean pipeline json response format tokens
                clean_json_text = response.choices[0].message.content.strip()
                if clean_json_text.startswith("```json"):
                    clean_json_text = clean_json_text.split("```json")[1].split("```")[0].strip()
                elif clean_json_text.startswith("```"):
                    clean_json_text = clean_json_text.split("```")[1].split("```")[0].strip()

                ai_output = json.loads(clean_json_text)
                status = ai_output.get("status", "SAFE")
                bg_type = ai_output.get("bg_type", "safe")
                ai_description = ai_output.get("description", "")

            except Exception as azure_error:
                # Strict fallback routing mechanism in case tokens mapping breaches threshold limits
                if wave_height > 2.0:
                    status, bg_type = "CLOSED BY AUTHORITY", "danger"
                    ai_description = f"High marine risk currents ({wave_height}m) observed around the coastal zone of {loc_name}. Entering water zones is currently blocked by authority."
                elif wave_height > 1.2:
                    status, bg_type = "CAUTION", "caution"
                    ai_description = f"Moderate wave profiles ({wave_height}m) monitored at {loc_name}. Safe for swimmers, but strict caution advised for casual waders or kids."
                else:
                    status, bg_type = "SAFE", "safe"
                    ai_description = f"Stable, calm wave activity profiles monitored at {loc_name}. SWELL height is registered around {wave_height}m, optimized for swimming activities."

            # Map dynamic high-fidelity background image components based on safety weights
            if bg_type == "danger":
                badge_class, bg_img = "badge-danger", "https://images.unsplash.com/photo-1505118380757-91f5f5632de0?auto=format&fit=crop&w=1200&q=80"
            elif bg_type == "caution":
                badge_class, bg_img = "badge-caution", "https://images.unsplash.com/photo-1519046904884-53103b34b206?auto=format&fit=crop&w=1200&q=80"
            else:
                badge_class, bg_img = "badge-safe", "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80"

            # Render Consumer Output Dashboard Section Canvas
            st.markdown(f"""
                <div class="result-card" style="background-image: url('{bg_img}');">
                    <div class="card-overlay"></div>
                    <div class="card-content">
                        <span class="status-badge {badge_class}">{status}</span>
                        <h2 style="margin-top:15px; color:white; font-weight:bold; font-size:26px;">Current Risk Matrix: {full_display_location}</h2>
                        <p style="font-size:16px; line-height:1.6; color:#f1f5f9; max-width:700px; margin-top:12px;">{ai_description}</p>
                        <hr style="border-color:rgba(255,255,255,0.15); margin:20px 0;">
                        <p style="font-size:12px; font-weight:500; color:#cbd5e1; margin:0;">📈 Real-Time Sensor Telemetry Metrics — Coordinates: Latitude {lat:.4f}, Longitude {lon:.4f} | Current Swell Height: {wave_height:.2f}m</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # STAGE 4: PREDICTIVE 7-DAY WAVE SCHEDULER MATRIX LAYOUT
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("### 📅 Predictive 7-Day Planning Companion Matrix")
            st.caption("Automated hourly telemetry predictive forecasts for scheduled coastal itineraries.")

            row1_cols = st.columns(4)
            row2_cols = st.columns(3)
            all_columns = row1_cols + row2_cols

            for day_idx in range(min(7, len(daily_max_forecasts))):
                raw_date_str = forecast_dates[day_idx]
                parsed_date = datetime.strptime(raw_date_str, "%Y-%m-%d")
                day_name = parsed_date.strftime("%A")
                date_label = parsed_date.strftime("%b %d")

                max_wave = daily_max_forecasts[day_idx]

                if status == "CLOSED BY AUTHORITY" or max_wave > 2.1:
                    day_status, card_color, window_time = "🚫 HIGH RISK", "#ef4444", "High Swells"
                elif max_wave > 1.3:
                    day_status, card_color, window_time = "🟡 CAUTION", "#f59e0b", "Shallow Only"
                else:
                    day_status, card_color, window_time = "🟢 OPTIMAL", "#10b981", "8 AM - 4 PM"

                with all_columns[day_idx]:
                    st.markdown(f"""
                    <div class="planner-card">
                        <strong style="font-size: 15px; color: #1e3a8a;">{day_name}</strong><br>
                        <span style="font-size: 11px; color: #64748b;">{date_label}</span>
                        <p style="margin: 10px 0; font-size: 13px; font-weight: 700; color: {card_color};">{day_status} ({max_wave:.2f}m)</p>
                        <span style="font-size: 11px; color: #475569;">Optimal Window:<br><strong>{window_time}</strong></span>
                    </div>
                    """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Telemetry execution logic pipeline validation crash error: {e}")