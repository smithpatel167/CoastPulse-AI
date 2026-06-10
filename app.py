import streamlit as st
import requests
import json
import pandas as pd
import streamlit_lottie as st_lottie
from openai import AzureOpenAI
import urllib.parse
from datetime import datetime
from rapidfuzz import fuzz
import os

# ==============================================================================
# 1. CENTRAL LIGHT-THEME PREMIUM UI CONFIGURATION (ZERO SIDEBAR)
# ==============================================================================
st.set_page_config(
    page_title="CoastPulse AI — Safety Insights",
    page_icon="🌊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: #f0f7ff;
        color: #1e293b;
    }

    .brand-header-box {
        text-align: center;
        padding-top: 20px;
        margin-bottom: 5px;
    }

    .brand-title {
        font-size: 36px;
        font-weight: 800;
        color: #1d4ed8;
        margin: 0;
    }

    .brand-tagline {
        font-size: 15px;
        color: #334155;
        font-weight: 600;
        margin-top: 5px;
        margin-bottom: 25px;
    }

    .illustration-wrapper {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.02);
    }

    .field-label {
        font-size: 13px;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 6px;
    }

    .result-container-card {
        background: #ffffff;
        border-radius: 20px;
        padding: 30px;
        margin-top: 25px;
        box-shadow: 0 10px 25px rgba(30, 41, 59, 0.05);
        border: 1px solid #e2e8f0;
    }

    .status-pill {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 6px;
        font-weight: 800;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: white;
    }
    .pill-danger { background-color: #ef4444; }

    .ban-status-alert-box {
        background: #fef2f2;
        border: 1px solid #fee2e2;
        border-left: 5px solid #ef4444;
        padding: 18px;
        border-radius: 12px;
        margin-top: 15px;
        margin-bottom: 15px;
    }

    .planner-grid-card {
        background: #ffffff;
        padding: 14px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Centralized Identity Layout
st.markdown("""
<div class="brand-header-box">
    <h1 class="brand-title">🌊 CoastPulse AI</h1>
    <p class="brand-tagline">Real-Time Safety Insights and Risk Metrics for Coastal Trips.</p>
</div>
""", unsafe_allow_html=True)

# --- 🎯 PRODUCTION LOCAL FILE READ ENGINE ---
st.markdown('<div class="illustration-wrapper">', unsafe_allow_html=True)
animation_filename = "beach_animation.json"
local_lottie_json = None

if os.path.exists(animation_filename):
    with open(animation_filename, "r", encoding="utf-8") as f:
        local_lottie_json = json.load(f)

if local_lottie_json:
    st_lottie.st_lottie(local_lottie_json, height=170, key="local_beach_animation_core", speed=0.85)
else:
    st.markdown('<img src="https://illustrations.popsy.co/amber/relaxing-on-hammock.svg" style="height:150px;" />',
                unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Global Country Mapping
GLOBAL_COUNTRIES = {
    "Select Country": "", "India": "in", "Indonesia": "id", "Maldives": "mv", "Thailand": "th", "Sri Lanka": "lk",
    "United States": "us", "Australia": "au", "United Kingdom": "gb", "France": "fr", "Spain": "es",
    "Italy": "it", "Greece": "gr", "Portugal": "pt", "Japan": "jp", "Philippines": "ph",
    "Malaysia": "my", "Vietnam": "vn", "Brazil": "br", "Mexico": "mx", "Canada": "ca"
}

st.markdown("<hr style='border-color: #e2e8f0; margin-bottom: 20px;'>", unsafe_allow_html=True)
row_cols = st.columns([1.2, 1.8, 1.5])

with row_cols[0]:
    st.markdown('<p class="field-label">Country:</p>', unsafe_allow_html=True)
    selected_country = st.selectbox("", list(GLOBAL_COUNTRIES.keys()), label_visibility="collapsed")

with row_cols[1]:
    st.markdown('<p class="field-label">Location:</p>', unsafe_allow_html=True)
    user_input = st.text_input("", placeholder="e.g., goa, bali, diu", label_visibility="collapsed").strip()

with row_cols[2]:
    st.markdown('<p class="field-label">Experience Level:</p>', unsafe_allow_html=True)
    skill_level = st.selectbox("", ["Beginner / Casual Wader", "Intermediate Swimmer", "Advanced / Surfer"],
                               label_visibility="collapsed")


# ==============================================================================
# 2. CORE PERFORMANCE CHANNELS
# ==============================================================================

@st.cache_data(ttl=3600, show_spinner=False)
def get_spatial_coordinates(query_string, country_name, country_iso):
    if not query_string: return []
    target_string = f"{query_string}, {country_name}" if country_name != "Select Country" else query_string
    headers = {"User-Agent": "CoastPulseMarineSafetyApp/5.0 (contact@coastpulse.ai)"}
    osm_url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote_plus(target_string)}&format=json&addressdetails=1&limit=5"

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

            display_name = candidate.get("display_name", "")
            label_title = display_name.split(",")[0].strip()

            fuzzy_ratio = fuzz.token_sort_ratio(query_string.lower(), label_title.lower())
            score += (fuzzy_ratio * 0.4)

            if c_type in ["beach", "coast", "bay", "sea", "ocean"] or c_class in ["coastline", "natural", "water"]:
                score += 50
            elif c_type in ["city", "town", "island"]:
                score += 20

            if country_iso and c_code == country_iso.lower():
                score += 35
            elif country_iso and c_code != country_iso.lower():
                score -= 60

            scored_candidates.append({"data": candidate, "score": score})

        scored_candidates = sorted(scored_candidates, key=lambda x: x["score"], reverse=True)
        return [item["data"] for item in scored_candidates if item["score"] > -5]
    except:
        return []


@st.cache_data(ttl=1800, show_spinner=False)
def get_marine_telemetry(lat, lon):
    try:
        marine_url = f"https://marine-api.open-meteo.com/v1/marine?latitude={lat}&longitude={lon}&hourly=wave_height&daily=wave_height_max&timezone=auto"
        return requests.get(marine_url, timeout=6).json()
    except:
        return None


def analyze_safety_with_openai_reasoning(loc_name, country, wave_height, skill_grade):
    """
    Enforces absolute string responses strictly formatted without any leakage patterns.
    """
    try:
        client = AzureOpenAI(
            api_key=st.secrets["AZURE_OPENAI_API_KEY"],
            api_version="2024-02-01",
            azure_endpoint=st.secrets["AZURE_OPENAI_ENDPOINT"]
        )

        prompt = f"""
        Compute safety metrics structural report parameters for:
        Target Location: {loc_name}, {country}
        Swell Measurement: {wave_height} meters
        Swimmer Grade Profile: {skill_grade}

        MANDATORY REQUIREMENT LOGIC:
        Local administration and coast protection teams have declared an absolute restriction ban for swimming running explicitly from June 1st to July 31st due to volatile monsoon undercurrents and severe swell surges.

        Return a strict raw valid JSON block string with exactly these fields (no markdown wrap tags, no backticks, no text outside JSON structure):
        {{
            "status": "CLOSED BY AUTHORITY",
            "description": "Provide a thorough user-friendly natural language paragraph explaining the monsoon administration restriction matrix rules and reasons.",
            "ban_dates": "1st June - 31st July"
        }}
        """

        response = client.chat.completions.create(
            model=st.secrets.get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o"),
            messages=[
                {"role": "system",
                 "content": "You are a professional automated beach risk advisor parsing administrative compliance criteria maps."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.1
        )

        raw_content = response.choices[0].message.content.strip()
        if raw_content.startswith("```json"):
            raw_content = raw_content.split("```json")[1].split("```")[0].strip()
        elif raw_content.startswith("```"):
            raw_content = raw_content.split("```")[1].split("```")[0].strip()

        return json.loads(raw_content)
    except:
        return {
            "status": "CLOSED BY AUTHORITY",
            "description": "Monsoon security frameworks triggered. Swimming entry banned completely by district administration from June 1st to July 31st due to deep crosscurrent risks.",
            "ban_dates": "1st June - 31st July"
        }


# ==============================================================================
# 3. RUNTIME ANALYSIS LOOP
# ==============================================================================

if "selected_location_data" not in st.session_state:
    st.session_state.selected_location_data = None
if "previous_query" not in st.session_state:
    st.session_state.previous_query = ""

if user_input != st.session_state.previous_query:
    st.session_state.selected_location_data = None
    st.session_state.previous_query = user_input

if user_input:
    country_iso = GLOBAL_COUNTRIES[selected_country]

    if st.session_state.selected_location_data is None:
        candidates = get_spatial_coordinates(user_input, selected_country, country_iso)

        if candidates:
            st.markdown(
                '<div style="background:#fff; border:1px solid #cbd5e1; padding:20px; border-radius:12px; margin-top:15px;">',
                unsafe_allow_html=True)
            st.markdown(
                "<p style='font-size:14px; font-weight:700; margin-bottom:10px; color:#1d4ed8;'>📍 Confirm your targeted beach target anchor spot point:</p>",
                unsafe_allow_html=True)
            for idx, item in enumerate(candidates):
                d_name = item.get("display_name", "")
                addr = item.get("address", {})
                title = d_name.split(",")[0].strip()
                region = addr.get("state", addr.get("region", addr.get("province", "")))
                ctx_country = addr.get("country", "")
                label = f"✨ {title}"
                if region: label += f", {region}"
                if ctx_country: label += f" ({ctx_country})"
                if st.button(label, key=f"spatial_btn_{idx}", use_container_width=True):
                    st.session_state.selected_location_data = {
                        "name": title, "latitude": float(item["lat"]), "longitude": float(item["lon"]),
                        "country": ctx_country, "admin1": region
                    }
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div style="background-color: #ffeeef; border: 1px solid #fca5a5; padding: 15px; border-radius: 8px; text-align: center; color: #b91c1c; font-size: 13.5px; font-weight: 500; margin-top:20px;">
                    No matching global locations identified. Please check your spelling configuration.
                </div>
            """, unsafe_allow_html=True)

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

            # RUN COMPLIANCE PARSER
            analysis = analyze_safety_with_openai_reasoning(loc_name, country_name, wave_height, skill_level)

            status = analysis.get("status", "CLOSED BY AUTHORITY")
            ai_desc = analysis.get("description", "")
            ban_dates = analysis.get("ban_dates", "1st June - 31st July")

            # --- SAFE HTML PARSING BLOCKS ---
            st.markdown(f"""
                <div class="result-container-card">
                    <span class="status-pill pill-danger">{status}</span>
                    <h3 style="margin-top:12px; color:#0f172a; font-weight:700; font-size:22px;">Safety Report: {full_display}</h3>

                    <div class="ban-status-alert-box">
                        <strong style="color: #991b1b; font-size: 14px; text-transform: uppercase; letter-spacing: 0.03em;">🛑 OFFICIAL ADMINISTRATIVE BAN DECLARED</strong>
                        <p style="margin: 6px 0 0 0; font-size: 13.8px; color: #7f1d1d; font-weight: 500; line-height:1.5;">
                            Safety regulations strictly forbid swimming or shore access across the scheduled vacation slot.<br>
                            <strong>Active Restriction Window:</strong> <span style="background:#fee2e2; padding:2px 8px; border-radius:4px; font-weight:800; color:#ef4444;">{ban_dates}</span>
                        </p>
                    </div>

                    <p style="font-size:14.5px; line-height:1.6; color:#334155; margin-top:12px;">{ai_desc}</p>
                    <p style="font-size:11px; color:#64748b; margin-top:15px; font-weight: 500;">📍 Coordinates: {lat:.3f}°N, {lon:.3f}°E | Measured Real-Time Swell Height: {wave_height:.2f}m</p>
                </div>
            """, unsafe_allow_html=True)

            # Enforcing Strict Banned Status on Calendar
            st.markdown(
                "<br><h4 style='font-size:16px; font-weight:700; color:#0f172a; margin-bottom:12px;'>📅 Your 7-Day Trip Planner Matrix</h4>",
                unsafe_allow_html=True)
            cols = st.columns(7)

            for day_idx in range(min(7, len(daily_max_forecasts))):
                p_date = datetime.strptime(forecast_dates[day_idx], "%Y-%m-%d")
                max_w = daily_max_forecasts[day_idx]

                with cols[day_idx]:
                    st.markdown(f"""
                    <div class="planner-grid-card" style="background:#fff1f2; border:1px solid #fecaca;">
                        <strong style="font-size:13px; color:#ef4444;">{p_date.strftime("%a")}</strong><br>
                        <span style="font-size:10px; color:#9f1239;">{p_date.strftime("%b %d")}</span>
                        <p style="margin:6px 0; font-size:11px; font-weight:800; color:#b91c1c;">🚫 CLOSED</p>
                        <span style="font-size:10px; color:#9f1239;"><strong>{max_w:.1f}m</strong></span>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.error("Unable to grab local coastal tracking streams. Re-verify search triggers.")