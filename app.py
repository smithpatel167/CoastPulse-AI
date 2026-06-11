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

    .agent-trace-box {
        background: #0f172a;
        border: 1px solid #1e3a5f;
        border-radius: 10px;
        padding: 14px 18px;
        margin-top: 18px;
        font-family: 'Courier New', monospace;
        font-size: 12px;
        color: #7dd3fc;
    }

    .agent-trace-box p {
        margin: 4px 0;
        color: #94a3b8;
    }

    .agent-trace-box span.step {
        color: #38bdf8;
        font-weight: 700;
    }

    .agent-trace-box span.tool {
        color: #34d399;
    }

    .agent-trace-box span.result {
        color: #fbbf24;
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


# ==============================================================================
# TOOL 1 — Real News Fetcher (replaces hardcoded scraper)
# Calls GNews API with the location name as search query.
# Falls back gracefully if API key is missing or request fails.
# ==============================================================================
@st.cache_data(ttl=900, show_spinner=False)
def fetch_live_coastal_news(location_name: str) -> dict:
    """
    Fetches real news headlines about a coastal location using GNews API.
    Returns a dict with 'articles' list and 'source' label for transparency.
    Add GNEWS_API_KEY to your Streamlit secrets to enable live news.
    Free tier: 100 requests/day — https://gnews.io
    """
    gnews_key = st.secrets.get("GNEWS_API_KEY", None)

    if gnews_key:
        try:
            query = f"{location_name} beach safety swimming"
            url = "https://gnews.io/api/v4/search"
            params = {
                "q": query,
                "token": gnews_key,
                "lang": "en",
                "max": 5,
                "sortby": "publishedAt"
            }
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            articles = data.get("articles", [])
            if articles:
                summaries = []
                for a in articles[:4]:
                    title = a.get("title", "")
                    desc = a.get("description", "")
                    published = a.get("publishedAt", "")[:10] if a.get("publishedAt") else ""
                    if title:
                        summaries.append(f"[{published}] {title}. {desc}")
                return {
                    "source": "GNews Live Feed",
                    "articles": summaries,
                    "raw_text": " | ".join(summaries)
                }
        except Exception:
            pass

    # Fallback — Wikipedia / Open data summary via Nominatim display name
    # Still real data, not hardcoded strings
    try:
        wiki_url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + location_name.replace(" ", "_")
        resp = requests.get(wiki_url, timeout=8)
        if resp.status_code == 200:
            extract = resp.json().get("extract", "")
            if extract:
                return {
                    "source": "Wikipedia Summary",
                    "articles": [extract[:400]],
                    "raw_text": extract[:400]
                }
    except Exception:
        pass

    # Last resort — generic real-time message (no hardcoded safety claims)
    return {
        "source": "Default",
        "articles": [],
        "raw_text": f"No specific news alerts currently found for {location_name}. Standard coastal conditions apply — verify with local authorities before entering water."
    }


# ==============================================================================
# TOOL 2 — Wave Risk Classifier (called as an agent tool by GPT-4o)
# ==============================================================================
def classify_wave_risk(wave_height: float, swimmer_grade: str) -> dict:
    """
    Classifies wave risk level based on height and swimmer experience.
    Returns structured dict consumed by the agent reasoning loop.
    """
    if swimmer_grade == "Beginner / Casual Wader":
        if wave_height > 0.6:
            risk = "HIGH"
            advice = "Waves exceeding 0.6m are dangerous for beginners. Wading only at ankle depth."
        elif wave_height > 0.3:
            risk = "MODERATE"
            advice = "Moderate swell for beginners. Stay near shore with a lifeguard present."
        else:
            risk = "LOW"
            advice = "Calm conditions suitable for beginners and casual wading."
    elif swimmer_grade == "Intermediate Swimmer":
        if wave_height > 1.2:
            risk = "HIGH"
            advice = "Strong swell for intermediate swimmers. Avoid open water."
        elif wave_height > 0.7:
            risk = "MODERATE"
            advice = "Choppy conditions. Swim parallel to shore and watch for rip currents."
        else:
            risk = "LOW"
            advice = "Good conditions for intermediate swimmers."
    else:  # Advanced / Surfer
        if wave_height > 2.5:
            risk = "HIGH"
            advice = "Extreme swell. Only experienced surfers with safety gear should proceed."
        elif wave_height > 1.5:
            risk = "MODERATE"
            advice = "Good surfing swell. Exercise standard water safety protocols."
        else:
            risk = "LOW"
            advice = "Light swell. Suitable for advanced swimmers and light surfing."

    return {
        "wave_height_m": wave_height,
        "swimmer_grade": swimmer_grade,
        "risk_level": risk,
        "advice": advice
    }


# ==============================================================================
# AGENTIC REASONING PIPELINE — GPT-4o with Tool Calling
# The agent autonomously decides which tools to call and in what order,
# then synthesizes all results into a final safety assessment.
# ==============================================================================
def run_coastal_safety_agent(location: str, wave_height: float, swimmer_grade: str) -> dict:
    """
    Agentic reasoning loop using GPT-4o function/tool calling via Azure AI Foundry.

    Agent flow:
      Step 1 — GPT-4o receives location + wave height, decides which tools to call
      Step 2 — Tools execute: fetch_live_coastal_news + classify_wave_risk
      Step 3 — GPT-4o receives all tool results, reasons over them
      Step 4 — Final structured JSON advisory is returned

    This replaces the old single-shot prompt approach with a genuine
    multi-step agentic loop where the model drives its own data gathering.
    """

    client = AzureOpenAI(
        api_key=st.secrets["AZURE_OPENAI_API_KEY"],
        api_version="2024-02-01",
        azure_endpoint=st.secrets["AZURE_OPENAI_ENDPOINT"]
    )

    deployment = st.secrets.get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")

    # --- Define tools available to the agent ---
    tools = [
        {
            "type": "function",
            "function": {
                "name": "fetch_live_coastal_news",
                "description": "Fetches real-time news articles and safety reports about a coastal beach location. Use this to check for bans, closures, pollution alerts, or hazard warnings.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location_name": {
                            "type": "string",
                            "description": "The beach or coastal location name to search news for, e.g. 'Diu Beach India'"
                        }
                    },
                    "required": ["location_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "classify_wave_risk",
                "description": "Classifies the swimming risk level based on current wave height and the traveler's experience level. Returns risk category and safety advice.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "wave_height": {
                            "type": "number",
                            "description": "Current wave height in meters"
                        },
                        "swimmer_grade": {
                            "type": "string",
                            "description": "Swimmer experience level: 'Beginner / Casual Wader', 'Intermediate Swimmer', or 'Advanced / Surfer'"
                        }
                    },
                    "required": ["wave_height", "swimmer_grade"]
                }
            }
        }
    ]

    # Agent trace for UI display
    agent_trace = []

    system_prompt = """You are CoastPulse AI — a coastal safety reasoning agent deployed on Azure AI Foundry.

Your job: analyze beach safety for travelers by autonomously gathering and reasoning over real-world data.

REASONING PROTOCOL:
1. Always call BOTH tools: fetch_live_coastal_news AND classify_wave_risk. You need both data points.
2. After receiving tool results, synthesize them logically:
   - If news reports an official ban or closure → status must be CLOSED BY AUTHORITY
   - If news is clear but waves are risky for the swimmer's level → CAUTION
   - If both news and waves are acceptable → SAFE
3. Never guess. Base your final answer entirely on tool outputs.
4. Return ONLY a raw valid JSON object — no markdown, no backticks, no HTML.

Output format:
{
  "status": "SAFE" or "CAUTION" or "CLOSED BY AUTHORITY",
  "bg_type": "safe" or "caution" or "danger",
  "description": "3-4 sentence human-readable advisory blending wave conditions and news findings.",
  "ban_detected": true or false,
  "ban_dates": "date range string or null",
  "news_source": "source label string"
}"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Analyze beach safety for: {location}\nCurrent wave height: {wave_height}m\nTraveler experience: {swimmer_grade}\n\nGather all necessary data using your tools and produce a final safety advisory."}
    ]

    agent_trace.append({"step": "INIT", "detail": f"Agent started for: {location} | Waves: {wave_height}m | Level: {swimmer_grade}"})

    # --- Agentic loop: keep running until model stops calling tools ---
    max_iterations = 5  # safety limit
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        response = client.chat.completions.create(
            model=deployment,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            max_tokens=600,
            temperature=0.1
        )

        choice = response.choices[0]

        # If model wants to call tools
        if choice.finish_reason == "tool_calls":
            tool_calls = choice.message.tool_calls
            messages.append(choice.message)  # append assistant message with tool_calls

            for tc in tool_calls:
                fn_name = tc.function.name
                fn_args = json.loads(tc.function.arguments)
                agent_trace.append({"step": f"TOOL CALL #{iteration}", "tool": fn_name, "args": fn_args})

                # Execute the tool locally
                if fn_name == "fetch_live_coastal_news":
                    result = fetch_live_coastal_news(fn_args["location_name"])
                elif fn_name == "classify_wave_risk":
                    result = classify_wave_risk(fn_args["wave_height"], fn_args["swimmer_grade"])
                else:
                    result = {"error": f"Unknown tool: {fn_name}"}

                agent_trace.append({"step": f"TOOL RESULT #{iteration}", "tool": fn_name, "result": str(result)[:200]})

                # Feed tool result back to agent
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(result)
                })

        # If model is done reasoning and gives final answer
        elif choice.finish_reason == "stop":
            raw_content = choice.message.content.strip()
            agent_trace.append({"step": "FINAL ANSWER", "detail": raw_content[:300]})

            # Clean any accidental markdown wrapping
            if raw_content.startswith("```json"):
                raw_content = raw_content.split("```json")[1].split("```")[0].strip()
            elif raw_content.startswith("```"):
                raw_content = raw_content.split("```")[1].split("```")[0].strip()

            try:
                parsed = json.loads(raw_content)
                parsed["_agent_trace"] = agent_trace
                return parsed
            except Exception:
                break

        else:
            break

    # Fallback if agent loop fails
    agent_trace.append({"step": "FALLBACK", "detail": "Agent loop ended without final answer"})
    return {
        "status": "CAUTION",
        "bg_type": "caution",
        "description": f"Wave height of {wave_height}m detected near {location}. Exercise caution and consult local authorities before entering the water.",
        "ban_detected": False,
        "ban_dates": None,
        "news_source": "Fallback",
        "_agent_trace": agent_trace
    }


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

        # --- Run agentic safety assessment ---
        with st.spinner("🤖 Agent reasoning over live data..."):
            polished_output = run_coastal_safety_agent(
                confirmed_node['display_title'], current_wave_height, skill_level
            )

        status    = polished_output.get("status", "SAFE")
        bg_type   = polished_output.get("bg_type", "safe")
        ai_desc   = polished_output.get("description", "")
        has_ban   = "YES" if polished_output.get("ban_detected", False) else "NO"
        ban_dates = polished_output.get("ban_dates") or "None"
        news_src  = polished_output.get("news_source", "")
        agent_trace = polished_output.get("_agent_trace", [])

        # Sanitize any stray tags from AI response
        for junk in ["```html", "```json", "```", "<div>", "</div>", "<p>", "</p>", "<span>", "</span>"]:
            ai_desc = ai_desc.replace(junk, "")
        ai_desc = ai_desc.strip()

        if has_ban == "YES" or status == "CLOSED BY AUTHORITY":
            display_status = "CLOSED BY AUTHORITY"
            pill_class = "badge-capsule-danger"
        elif bg_type == "caution" or status == "CAUTION":
            display_status = "CAUTION"
            pill_class = "badge-capsule-caution"
        else:
            display_status = "SAFE"
            pill_class = "badge-capsule-safe"

        # Background image based on risk
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
        news_src_html = f'<span style="font-size:10px;color:rgba(241,245,249,0.4);margin-left:8px;">📡 {news_src}</span>' if news_src else ""

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
            + news_src_html +
            '<h3 class="advisory-header-title">Safety Report: ' + location_title + '</h3>'
            + ban_alert_html +
            '<p class="advisory-prose-body">' + ai_desc + '</p>'
            '<div class="brand-stamp-footer">✨ Powered by CoastPulse AI · Azure AI Foundry</div>'
            '</div>'
        )

        st.markdown(card_html, unsafe_allow_html=True)

        # --- Agent Reasoning Trace (collapsible) ---
        if agent_trace:
            with st.expander("🤖 View Agent Reasoning Trace", expanded=False):
                trace_lines = ""
                for t in agent_trace:
                    step = t.get("step", "")
                    if "TOOL CALL" in step:
                        trace_lines += f'<p><span class="step">[{step}]</span> → <span class="tool">{t.get("tool","")}</span> args: {t.get("args","")}</p>'
                    elif "TOOL RESULT" in step:
                        trace_lines += f'<p><span class="step">[{step}]</span> → <span class="result">{t.get("result","")[:180]}...</span></p>'
                    elif "FINAL ANSWER" in step:
                        trace_lines += f'<p><span class="step">[{step}]</span> → {t.get("detail","")[:200]}...</p>'
                    else:
                        trace_lines += f'<p><span class="step">[{step}]</span> {t.get("detail","")}</p>'
                st.markdown(f'<div class="agent-trace-box">{trace_lines}</div>', unsafe_allow_html=True)

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