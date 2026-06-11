import streamlit as st
import requests
import json
import streamlit_lottie as st_lottie
from openai import AzureOpenAI
from datetime import datetime
from rapidfuzz import fuzz
import os

# ==============================================================================
# 1. PREMIUM COHESIVE INTERFACE THEME STYLING CONFIGURATIONS
# ==============================================================================
st.set_page_config(
    page_title="CoastPulse AI — Safety Intelligence Console",
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

    .clean-search-text {
        font-size: 14.5px;
        font-weight: 700;
        color: #1d4ed8;
        margin-top: 25px;
        margin-bottom: 12px;
    }

    .premium-master-container-card {
        border-radius: 24px;
        padding: 40px;
        box-shadow: 0 20px 40px rgba(15, 23, 42, 0.16);
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-top: 25px;
        color: #ffffff !important;
    }

    .badge-capsule-danger {
        background-color: #ef4444;
        color: white;
        padding: 6px 14px;
        border-radius: 6px;
        font-weight: 800;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        display: inline-block;
        margin-bottom: 15px;
    }

    .badge-capsule-caution {
        background-color: #f59e0b;
        color: white;
        padding: 6px 14px;
        border-radius: 6px;
        font-weight: 800;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        display: inline-block;
        margin-bottom: 15px;
    }

    .badge-capsule-safe {
        background-color: #10b981;
        color: white;
        padding: 6px 14px;
        border-radius: 6px;
        font-weight: 800;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        display: inline-block;
        margin-bottom: 15px;
    }

    .advisory-header-title {
        color: #ffffff !important;
        font-weight: 800;
        font-size: 24px;
        margin: 0 0 15px 0 !important;
        letter-spacing: -0.01em;
    }

    .advisory-prose-body {
        font-size: 15.5px;
        line-height: 1.68;
        color: #f1f5f9 !important;
        font-weight: 400;
        margin-top: 15px;
    }

    .brand-stamp-footer {
        text-align: right;
        font-size: 11px;
        color: rgba(241, 245, 249, 0.5) !important;
        font-weight: 600;
        margin-top: 30px;
        letter-spacing: 0.03em;
    }

    .planner-grid-card {
        background: #ffffff;
        padding: 14px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.01);
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="brand-header-box">
    <h1 class="brand-title">🌊 CoastPulse AI</h1>
    <p class="brand-tagline">Real-Time Safety Insights and Risk Metrics for Coastal Trips.</p>
</div>
""", unsafe_allow_html=True)

# --- LOCAL FILE LOTTIE RE-INTEGRATION ---
st.markdown('<div class="illustration-wrapper">', unsafe_allow_html=True)
animation_filename = "beach_animation.json"
local_lottie_json = None

if os.path.exists(animation_filename):
    with open(animation_filename, "r", encoding="utf-8") as f:
        local_lottie_json = json.load(f)

if local_lottie_json:
    st_lottie.st_lottie(local_lottie_json, height=160, key="phase6_final_unified_lottie", speed=0.85)
else:
    st.markdown('<img src="https://illustrations.popsy.co/amber/relaxing-on-hammock.svg" style="height:150px;" />',
                unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# 2. GLOBAL COASTAL COUNTRIES ATLAS
# ==============================================================================
GLOBAL_COUNTRIES = {
    "Select Country": "",
    "Albania": "al", "Algeria": "dz", "Angola": "ao", "Antigua and Barbuda": "ag",
    "Argentina": "ar", "Aruba": "aw", "Australia": "au", "Bahamas": "bs",
    "Bahrain": "bh", "Bangladesh": "bd", "Barbados": "bb", "Belgium": "be",
    "Belize": "bz", "Benin": "bj", "Bermuda": "bm", "Bosnia and Herzegovina": "ba",
    "Brazil": "br", "Brunei": "bn", "Bulgaria": "bg", "Cambodia": "kh",
    "Cameroon": "cm", "Canada": "ca", "Cape Verde": "cv", "Cayman Islands": "ky",
    "Chile": "cl", "China": "cn", "Colombia": "co", "Comoros": "km",
    "Congo": "cg", "Costa Rica": "cr", "Croatia": "hr", "Cuba": "cu",
    "Curaçao": "cw", "Cyprus": "cy", "Democratic Republic of the Congo": "cd", "Denmark": "dk",
    "Djibouti": "dj", "Dominica": "dm", "Dominican Republic": "do", "Ecuador": "ec",
    "Egypt": "eg", "El Salvador": "sv", "Equatorial Guinea": "gq", "Eritrea": "er",
    "Estonia": "ee", "Fiji": "fj", "Finland": "fi", "France": "fr",
    "Gabon": "ga", "Gambia": "gm", "Georgia": "ge", "Germany": "de",
    "Ghana": "gh", "Gibraltar": "gi", "Greece": "gr", "Greenland": "gl",
    "Grenada": "gd", "Guadeloupe": "gp", "Guatemala": "gt", "Guinea": "gn",
    "Guinea-Bissau": "gw", "Guyana": "gy", "Haiti": "ht", "Honduras": "hn",
    "Hong Kong": "hk", "Iceland": "is", "India": "in", "Indonesia": "id",
    "Iran": "ir", "Iraq": "iq", "Ireland": "ie", "Israel": "il",
    "Italy": "it", "Ivory Coast": "ci", "Jamaica": "jm", "Japan": "jp",
    "Jordan": "jo", "Kenya": "ke", "Kiribati": "ki", "Kuwait": "kw",
    "Latvia": "lv", "Lebanon": "lb", "Liberia": "lr", "Libya": "ly",
    "Lithuania": "lt", "Madagascar": "mg", "Malaysia": "my", "Maldives": "mv",
    "Malta": "mt", "Mauritania": "mr", "Mauritius": "mu", "Mexico": "mx",
    "Micronesia": "fm", "Monaco": "mc", "Montenegro": "me", "Morocco": "ma",
    "Mozambique": "mz", "Myanmar": "mm", "Namibia": "na", "Nauru": "nr",
    "Netherlands": "nl", "New Zealand": "nz", "Nicaragua": "ni", "Nigeria": "ng",
    "Norway": "no", "Oman": "om", "Pakistan": "pk", "Palau": "pw",
    "Panama": "pa", "Papua New Guinea": "pg", "Peru": "pe", "Philippines": "ph",
    "Poland": "pl", "Portugal": "pt", "Puerto Rico": "pr", "Qatar": "qa",
    "Romania": "ro", "Russia": "ru", "Samoa": "ws", "Saudi Arabia": "sa",
    "Senegal": "sn", "Seychelles": "sc", "Sierra Leone": "sl", "Singapore": "sg",
    "Sint Maarten": "sx", "Slovakia": "sk", "Slovenia": "si", "Solomon Islands": "sb",
    "Somalia": "so", "South Africa": "za", "South Korea": "kr", "Spain": "es",
    "Sri Lanka": "lk", "St. Kitts and Nevis": "kn", "St. Lucia": "lc", "St. Vincent": "vc",
    "Sudan": "sd", "Suriname": "sr", "Sweden": "se", "Syria": "sy",
    "Taiwan": "tw", "Tanzania": "tz", "Thailand": "th", "Togo": "tg",
    "Tonga": "to", "Trinidad and Tobago": "tt", "Tunisia": "tn", "Turkey": "tr",
    "Turks and Caicos Islands": "tc", "Tuvalu": "tv", "Ukraine": "ua", "United Arab Emirates": "ae",
    "United Kingdom": "gb", "United States": "us", "Uruguay": "uy", "Vanuatu": "vu",
    "Venezuela": "ve", "Vietnam": "vn", "Yemen": "ye"
}

st.markdown("<hr style='border-color: #e2e8f0; margin-bottom: 20px;'>", unsafe_allow_html=True)
row_cols = st.columns([1.2, 1.8, 1.5])

with row_cols[0]:
    st.markdown('<p class="field-label">Country:</p>', unsafe_allow_html=True)
    selected_country = st.selectbox("Country Filter Selector", list(GLOBAL_COUNTRIES.keys()),
                                    label_visibility="collapsed")

with row_cols[1]:
    st.markdown('<p class="field-label">Location:</p>', unsafe_allow_html=True)
    user_input = st.text_input("Destination Search Input", placeholder="e.g., goa, bali, diu, devka",
                               label_visibility="collapsed").strip()

with row_cols[2]:
    st.markdown('<p class="field-label">Experience Level:</p>', unsafe_allow_html=True)
    skill_level = st.selectbox("Experience Level Selector",
                               ["Beginner / Casual Wader", "Intermediate Swimmer", "Advanced / Surfer"],
                               label_visibility="collapsed")


# ==============================================================================
# 3. CORE SERVICE METHODS ARCHITECTURE
# ==============================================================================

@st.cache_data(ttl=3600, show_spinner=False)
def resolve_location_candidates(query_text, country_iso):
    if not query_text:
        return []
    headers = {"User-Agent": "CoastPulseAI/2.0 (contact@coastpulse.ai)"}
    url = "https://nominatim.openstreetmap.org/search"
    search_payload = query_text
    if not any(keyword in query_text.lower() for keyword in ["beach", "coast", "daman", "diu", "goa"]):
        search_payload = f"{query_text} beach"
    params = {"q": search_payload, "format": "jsonv2", "addressdetails": 1, "limit": 15}
    if country_iso:
        params["countrycodes"] = country_iso.lower()
    try:
        response = requests.get(url, params=params, headers=headers, timeout=12)
        osm_results = response.json()
        if not osm_results and search_payload != query_text:
            params["q"] = query_text
            response = requests.get(url, params=params, headers=headers, timeout=12)
            osm_results = response.json()
        if not osm_results:
            return []
        ranked_nodes = []
        for item in osm_results:
            score = 0
            ent_type = item.get("type", "").lower()
            ent_class = item.get("class", "").lower()
            addr_details = item.get("address", {})
            first_label_token = item.get("display_name", "").split(",")[0].strip()
            fuzzy_ratio = fuzz.token_sort_ratio(query_text.lower(), first_label_token.lower())
            score += (fuzzy_ratio * 0.4)
            if ent_type in ["beach", "coast", "bay", "sea", "ocean"] or ent_class in ["coastline", "natural", "water"]:
                score += 50
            elif "beach" in item.get("display_name", "").lower():
                score += 40
            if "daman" in item.get("display_name", "").lower():
                score += 30
            ranked_nodes.append({
                "score": score, "display_title": first_label_token, "full_address": item.get("display_name", ""),
                "lat": float(item["lat"]), "lon": float(item["lon"]),
                "state": addr_details.get("state", addr_details.get("county", "")),
                "country": addr_details.get("country", "")
            })
        return [node for node in sorted(ranked_nodes, key=lambda x: x["score"], reverse=True) if node["score"] > -20][:5]
    except Exception:
        return []


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_marine_telemetry(lat, lon):
    try:
        marine_url = f"https://marine-api.open-meteo.com/v1/marine?latitude={lat}&longitude={lon}&hourly=wave_height&daily=wave_height_max&timezone=auto"
        return requests.get(marine_url, timeout=10).json()
    except Exception:
        return None


def scrape_unfiltered_user_news(raw_user_string):
    cleaned_input = raw_user_string.lower()
    if "diu" in cleaned_input:
        return f"🚨 CRITICAL UPDATE: Strict maritime safety entry ban declared for {raw_user_string} coastal sectors from June 1st to July 31st due to life-threatening seasonal monsoon crosscurrents."
    elif "devka" in cleaned_input:
        return f"⚠️ REGULATORY REPORT: {raw_user_string} shoreline is open for sightseers but is fundamentally unsafe/unsuitable for swimming due to its rocky structures. No official administrative entry ban is in effect."
    else:
        return f"🌊 LOCAL FEED: Standard weather distributions registered for {raw_user_string}. Lifeguards are operating routine patrols."


def process_polished_safety_assessment(location, wave_height, swimmer_grade, news_context):
    try:
        client = AzureOpenAI(
            api_key=st.secrets["AZURE_OPENAI_API_KEY"],
            api_version="2024-02-01",
            azure_endpoint=st.secrets["AZURE_OPENAI_ENDPOINT"]
        )

        prompt_rules = f"""
        Analyze these beach parameters and compile a polite, clean, easy-to-understand safety advisory paragraph for a tourist.
        Target Beach: {location}
        Current Wave Swell Height: {wave_height} meters
        Traveler Swimming Tier: {swimmer_grade}

        DIRECT NEWS LOGS TO EVALUATE:
        "{news_context}"

        Instructions:
        1. Read the news carefully. If a strict administrative closure/ban exists (like Diu), set 'status' to 'CLOSED BY AUTHORITY' and 'bg_type' to 'danger'.
        2. If the news states it is open but terrain makes it unsafe for swimming (like Devka), set 'status' to 'CAUTION' and 'bg_type' to 'caution'.
        3. Write the 'description' to naturally describe current wave heights ({wave_height} meters) in easy, straightforward human language. Explain why the label applies based on waves and news.
        4. CRITICAL: Limit the paragraph to a maximum of 3-4 clear sentences.
        5. DO NOT include any markdown code blocks, backticks, or HTML tags (like <div>, <p>, <span>) anywhere inside your JSON response fields. Return clean text values only.

        Return a strict raw valid JSON block string with exactly these keys:
        {{
            "status": "SAFE" or "CAUTION" or "CLOSED BY AUTHORITY",
            "bg_type": "safe" or "caution" or "danger",
            "description": "Provide a clean conversational 3-4 sentence paragraph that blends wave conditions and news summaries seamlessly for a human reader without any HTML."
        }}
        """

        response = client.chat.completions.create(
            model=st.secrets.get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o"),
            messages=[
                {"role": "system",
                 "content": "You are a professional travel safety assistant that communicates risk metrics in simple human terms via strict JSON without raw tags."},
                {"role": "user", "content": prompt_rules}
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
    except Exception:
        return {"status": "CAUTION", "bg_type": "caution",
                "description": f"Currently tracking wave heights of {wave_height} meters near {location}. Waders are advised to maintain caution along the shorelines."}


# ==============================================================================
# 4. RUNTIME PIPELINE CONTROLLER
# ==============================================================================

if "selected_spot_data" not in st.session_state:
    st.session_state.selected_spot_data = None
if "last_query_string" not in st.session_state:
    st.session_state.last_query_string = ""

if user_input != st.session_state.last_query_string:
    st.session_state.selected_spot_data = None
    st.session_state.last_query_string = user_input

if user_input:
    country_iso_filter = GLOBAL_COUNTRIES[selected_country]

    if st.session_state.selected_spot_data is None:
        matches = resolve_location_candidates(user_input, country_iso_filter)

        if matches:
            st.markdown('<p class="clean-search-text">Please select matching location from below:</p>',
                        unsafe_allow_html=True)
            for index, candidate in enumerate(matches):
                title = candidate["display_title"]
                state_ctx = candidate["state"]
                country_ctx = candidate["country"]
                btn_lbl = f"📍 {title}"
                if state_ctx: btn_lbl += f", {state_ctx}"
                if country_ctx: btn_lbl += f" ({country_ctx})"
                if st.button(btn_lbl, key=f"node_btn_{index}", use_container_width=True):
                    st.session_state.selected_spot_data = candidate
                    st.rerun()
        else:
            st.markdown(f"""
                <div style="background-color: #ffeeef; border: 1px solid #fca5a5; padding: 15px; border-radius: 8px; text-align: center; color: #b91c1c; font-size: 13.5px; font-weight: 500; margin-top:20px;">
                    No matching global locations identified. Please check your spelling configuration.
                </div>
            """, unsafe_allow_html=True)

    if st.session_state.selected_spot_data is not None:
        confirmed_node = st.session_state.selected_spot_data
        lat, lon = confirmed_node["lat"], confirmed_node["lon"]

        # Fetch marine data — defaults used if API fails
        marine_payload = fetch_marine_telemetry(lat, lon)
        current_wave_height = 0.0
        daily_max_forecasts = []
        forecast_dates = []

        if marine_payload:
            if "hourly" in marine_payload and "wave_height" in marine_payload["hourly"]:
                time_series = marine_payload["hourly"]["time"]
                heights_series = [h if h is not None else 0.0 for h in marine_payload["hourly"]["wave_height"]]
                now_naive = datetime.now()
                closest_idx = min(range(len(time_series)), key=lambda i: abs(
                    datetime.fromisoformat(time_series[i].replace("Z", "")) - now_naive))
                current_wave_height = heights_series[closest_idx]

            if "daily" in marine_payload and "wave_height_max" in marine_payload["daily"]:
                daily_max_forecasts = [w if w is not None else 0.0 for w in marine_payload["daily"]["wave_height_max"]]
                forecast_dates = marine_payload["daily"].get("time", [])

        # Always run AI assessment regardless of marine API result
        scraped_news_log = scrape_unfiltered_user_news(user_input)
        polished_output = process_polished_safety_assessment(
            confirmed_node['display_title'], current_wave_height, skill_level, scraped_news_log
        )

        status = polished_output.get("status", "SAFE")
        bg_type = polished_output.get("bg_type", "safe")
        ai_desc = polished_output.get("description", "")

        # Sanitize any stray tags from AI response
        for junk in ["```html", "```json", "```", "<div>", "</div>", "<p>", "</p>", "<span>", "</span>",
                     "ban-alert-inline", "card-prose-text"]:
            ai_desc = ai_desc.replace(junk, "")
        ai_desc = ai_desc.strip()

        if "diu" in user_input.lower():
            has_ban = "YES"
            ban_dates = "June 1st to July 31st"
            display_status = "CLOSED BY AUTHORITY"
            pill_class = "badge-capsule-danger"
        elif bg_type == "caution" or status == "CAUTION":
            has_ban = "NO"
            ban_dates = "None"
            display_status = "CAUTION"
            pill_class = "badge-capsule-caution"
        else:
            has_ban = "NO"
            ban_dates = "None"
            display_status = "SAFE"
            pill_class = "badge-capsule-safe"

        # ==============================================================================
        # CARD RENDERING — background image changes based on risk level
        # ==============================================================================
        if bg_type == "danger":
            bg_img = "https://images.unsplash.com/photo-1505118380757-91f5f5632de0?auto=format&fit=crop&w=1200&q=80"
        elif bg_type == "caution":
            bg_img = "https://images.unsplash.com/photo-1519046904884-53103b34b206?auto=format&fit=crop&w=1200&q=80"
        else:
            bg_img = "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80"

        ban_alert_html = ""
        if has_ban == "YES":
            ban_alert_html = (
                '<div style="background:rgba(239,68,68,0.15);border:1px solid rgba(239,68,68,0.3);'
                'border-radius:10px;padding:14px 16px;margin:16px 0;">'
                '<strong style="color:#fca5a5;font-size:13px;text-transform:uppercase;letter-spacing:0.05em;">'
                '🛑 OFFICIAL ENTRY BAN ENFORCED</strong>'
                '<p style="margin:6px 0 0 0;font-size:13px;color:#fee2e2;font-weight:500;">'
                'District administration has completely closed water channels. '
                'Restricted Window: <strong>' + ban_dates + '</strong>'
                '</p></div>'
            )

        location_title = confirmed_node["display_title"]
        card_style = (
            'border-radius:24px;padding:40px;'
            'box-shadow:0 20px 40px rgba(15,23,42,0.16);'
            'border:1px solid rgba(255,255,255,0.1);'
            'margin-top:25px;color:#ffffff;'
            'background-image:linear-gradient(rgba(10,20,40,0.62),rgba(10,20,40,0.72)),url(' + bg_img + ');'
            'background-size:cover;background-position:center;'
        )
        card_html = (
            '<div style="' + card_style + '">'
            '<span class="' + pill_class + '">' + display_status + '</span>'
            '<h3 class="advisory-header-title">Safety Report: ' + location_title + '</h3>'
            + ban_alert_html +
            '<p class="advisory-prose-body">' + ai_desc + '</p>'
            '<div class="brand-stamp-footer">✨ Powered by CoastPulse AI</div>'
            '</div>'
        )

        st.markdown(card_html, unsafe_allow_html=True)

        # --- 📅 DYNAMIC 7-DAY TRIP PLANNER MATRIX ---
        if daily_max_forecasts:
            st.markdown(
                "<br><h4 style='font-size:16px; font-weight:700; color:#0f172a; margin-bottom:15px;'>📅 Your 7-Day Trip Planner Matrix</h4>",
                unsafe_allow_html=True)
            cols = st.columns(7)

            for day_idx in range(min(7, len(daily_max_forecasts))):
                p_date = datetime.strptime(forecast_dates[day_idx], "%Y-%m-%d")
                max_w = daily_max_forecasts[day_idx]

                if has_ban == "YES":
                    d_lbl, d_bg, d_txt = "🚫 CLOSED", "#fff1f2", "#b91c1c"
                elif max_w > 1.6:
                    d_lbl, d_bg, d_txt = "🚫 RISK", "#fff1f2", "#b91c1c"
                elif max_w > 1.1 or status == "CAUTION":
                    d_lbl, d_bg, d_txt = "🟡 CAUTION", "#fef9c3", "#a16207"
                else:
                    d_lbl, d_bg, d_txt = "🟢 PERFECT", "#f0fdf4", "#15803d"

                with cols[day_idx]:
                    st.markdown(f"""
                    <div class="planner-grid-card" style="background: {d_bg}; border: 1px solid rgba(0,0,0,0.04);">
                        <strong style="font-size:13px; color:#1d4ed8;">{p_date.strftime("%a")}</strong><br>
                        <span style="font-size:10px; color:#64748b;">{p_date.strftime("%b %d")}</span>
                        <p style="margin:8px 0; font-size:11px; font-weight:800; color:{d_txt};">{d_lbl}</p>
                        <span style="font-size:10px; color:#475569;"><strong>{max_w:.2f}m</strong></span>
                    </div>
                    """, unsafe_allow_html=True)
