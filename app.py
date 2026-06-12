import streamlit as st
import requests
import json
import streamlit_lottie as st_lottie
from openai import AzureOpenAI
from datetime import datetime
from rapidfuzz import fuzz
import os
import re

# ==============================================================================
# 1. PAGE CONFIG & STYLING
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
    .brand-header-box   { text-align: center; padding-top: 20px; margin-bottom: 5px; }
    .brand-title        { font-size: 36px; font-weight: 800; color: #1d4ed8; margin: 0; }
    .brand-tagline      { font-size: 15px; color: #334155; font-weight: 600; margin-top: 5px; margin-bottom: 25px; }
    .illustration-wrapper {
        background-color: #ffffff; border-radius: 12px; padding: 20px;
        text-align: center; margin-bottom: 30px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.02);
    }
    .field-label        { font-size: 13px; font-weight: 700; color: #0f172a; margin-bottom: 6px; }
    .clean-search-text  { font-size: 14.5px; font-weight: 700; color: #1d4ed8; margin-top: 25px; margin-bottom: 12px; }

    /* ── Status pills ── */
    .badge-ban     { background-color: #7c3aed; color: white; padding: 6px 14px; border-radius: 6px;
                     font-weight: 800; font-size: 11px; text-transform: uppercase;
                     letter-spacing: 0.06em; display: inline-block; margin-bottom: 15px; }
    .badge-caution { background-color: #f59e0b; color: white; padding: 6px 14px; border-radius: 6px;
                     font-weight: 800; font-size: 11px; text-transform: uppercase;
                     letter-spacing: 0.06em; display: inline-block; margin-bottom: 15px; }
    .badge-safe    { background-color: #10b981; color: white; padding: 6px 14px; border-radius: 6px;
                     font-weight: 800; font-size: 11px; text-transform: uppercase;
                     letter-spacing: 0.06em; display: inline-block; margin-bottom: 15px; }

    .advisory-header-title { color: #ffffff !important; font-weight: 800; font-size: 24px;
                              margin: 0 0 15px 0 !important; letter-spacing: -0.01em; }
    .advisory-prose-body   { font-size: 15.5px; line-height: 1.72; color: #f1f5f9 !important;
                              font-weight: 400; margin-top: 15px; }
    .ban-box { background: rgba(124,58,237,0.18); border: 1px solid rgba(167,139,250,0.4);
                border-radius: 10px; padding: 14px 16px; margin: 16px 0; }
    .ban-box-title { color: #ddd6fe; font-size: 13px; font-weight: 800; text-transform: uppercase; }
    .ban-box-body  { margin: 6px 0 0 0; font-size: 13.5px; color: #ede9fe; font-weight: 500; }
    .brand-stamp-footer { text-align: right; font-size: 11px; color: rgba(241,245,249,0.45) !important;
                          font-weight: 600; margin-top: 30px; letter-spacing: 0.03em; }
    .planner-grid-card  { background: #ffffff; padding: 14px; border-radius: 12px;
                          border: 1px solid #e2e8f0; text-align: center;
                          box-shadow: 0 1px 3px rgba(0,0,0,0.01); }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="brand-header-box">
    <h1 class="brand-title">🌊 CoastPulse AI</h1>
    <p class="brand-tagline">Real-Time Safety Insights and Risk Metrics for Coastal Trips.</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="illustration-wrapper">', unsafe_allow_html=True)
animation_filename = "beach_animation.json"
local_lottie_json = None
if os.path.exists(animation_filename):
    with open(animation_filename, "r", encoding="utf-8") as f:
        local_lottie_json = json.load(f)
if local_lottie_json:
    st_lottie.st_lottie(local_lottie_json, height=160, key="coastpulse_lottie", speed=0.85)
else:
    st.markdown(
        '<img src="https://illustrations.popsy.co/amber/relaxing-on-hammock.svg" '
        'style="height:150px;" />',
        unsafe_allow_html=True
    )
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
    "Curaçao": "cw", "Cyprus": "cy", "Democratic Republic of the Congo": "cd",
    "Denmark": "dk", "Djibouti": "dj", "Dominica": "dm", "Dominican Republic": "do",
    "Ecuador": "ec", "Egypt": "eg", "El Salvador": "sv", "Equatorial Guinea": "gq",
    "Eritrea": "er", "Estonia": "ee", "Fiji": "fj", "Finland": "fi", "France": "fr",
    "Gabon": "ga", "Gambia": "gm", "Georgia": "ge", "Germany": "de", "Ghana": "gh",
    "Gibraltar": "gi", "Greece": "gr", "Greenland": "gl", "Grenada": "gd",
    "Guadeloupe": "gp", "Guatemala": "gt", "Guinea": "gn", "Guinea-Bissau": "gw",
    "Guyana": "gy", "Haiti": "ht", "Honduras": "hn", "Hong Kong": "hk",
    "Iceland": "is", "India": "in", "Indonesia": "id", "Iran": "ir", "Iraq": "iq",
    "Ireland": "ie", "Israel": "il", "Italy": "it", "Ivory Coast": "ci",
    "Jamaica": "jm", "Japan": "jp", "Jordan": "jo", "Kenya": "ke", "Kiribati": "ki",
    "Kuwait": "kw", "Latvia": "lv", "Lebanon": "lb", "Liberia": "lr", "Libya": "ly",
    "Lithuania": "lt", "Madagascar": "mg", "Malaysia": "my", "Maldives": "mv",
    "Malta": "mt", "Mauritania": "mr", "Mauritius": "mu", "Mexico": "mx",
    "Micronesia": "fm", "Monaco": "mc", "Montenegro": "me", "Morocco": "ma",
    "Mozambique": "mz", "Myanmar": "mm", "Namibia": "na", "Nauru": "nr",
    "Netherlands": "nl", "New Zealand": "nz", "Nicaragua": "ni", "Nigeria": "ng",
    "Norway": "no", "Oman": "om", "Pakistan": "pk", "Palau": "pw", "Panama": "pa",
    "Papua New Guinea": "pg", "Peru": "pe", "Philippines": "ph", "Poland": "pl",
    "Portugal": "pt", "Puerto Rico": "pr", "Qatar": "qa", "Romania": "ro",
    "Russia": "ru", "Samoa": "ws", "Saudi Arabia": "sa", "Senegal": "sn",
    "Seychelles": "sc", "Sierra Leone": "sl", "Singapore": "sg", "Sint Maarten": "sx",
    "Slovakia": "sk", "Slovenia": "si", "Solomon Islands": "sb", "Somalia": "so",
    "South Africa": "za", "South Korea": "kr", "Spain": "es", "Sri Lanka": "lk",
    "St. Kitts and Nevis": "kn", "St. Lucia": "lc", "St. Vincent": "vc",
    "Sudan": "sd", "Suriname": "sr", "Sweden": "se", "Syria": "sy", "Taiwan": "tw",
    "Tanzania": "tz", "Thailand": "th", "Togo": "tg", "Tonga": "to",
    "Trinidad and Tobago": "tt", "Tunisia": "tn", "Turkey": "tr",
    "Turks and Caicos Islands": "tc", "Tuvalu": "tv", "Ukraine": "ua",
    "United Arab Emirates": "ae", "United Kingdom": "gb", "United States": "us",
    "Uruguay": "uy", "Vanuatu": "vu", "Venezuela": "ve", "Vietnam": "vn", "Yemen": "ye",
}

st.markdown("<hr style='border-color: #e2e8f0; margin-bottom: 20px;'>", unsafe_allow_html=True)
row_cols = st.columns([1.2, 1.8, 1.5])
with row_cols[0]:
    st.markdown('<p class="field-label">Country:</p>', unsafe_allow_html=True)
    selected_country = st.selectbox(
        "Country", list(GLOBAL_COUNTRIES.keys()), label_visibility="collapsed"
    )
with row_cols[1]:
    st.markdown('<p class="field-label">Location:</p>', unsafe_allow_html=True)
    user_input = st.text_input(
        "Location",
        placeholder="e.g., goa, bali, diu, miami beach",
        label_visibility="collapsed"
    ).strip()
with row_cols[2]:
    st.markdown('<p class="field-label">Experience Level:</p>', unsafe_allow_html=True)
    skill_level = st.selectbox(
        "Experience",
        ["Beginner / Casual Wader", "Intermediate Swimmer", "Advanced / Surfer"],
        label_visibility="collapsed"
    )

# ==============================================================================
# 3. LOCATION RESOLVER  (Nominatim — no hardcoded URLs)
# ==============================================================================
NON_BEACH_PENALTY_WORDS = [
    "airport", "railway", "station", "hotel", "resort", "hospital",
    "school", "college", "university", "road", "highway", "mall",
    "market", "temple", "mosque", "church",
]


@st.cache_data(ttl=3600, show_spinner=False)
def resolve_location_candidates(query_text: str, country_iso: str) -> list:
    if not query_text:
        return []
    headers = {"User-Agent": "CoastPulseAI/3.0 (contact@coastpulse.ai)"}
    base_url = "https://nominatim.openstreetmap.org/search"

    search_payload = query_text
    if not any(kw in query_text.lower() for kw in ["beach", "coast"]):
        search_payload = f"{query_text} beach"

    params = {"q": search_payload, "format": "jsonv2", "addressdetails": 1, "limit": 15}
    if country_iso:
        params["countrycodes"] = country_iso.lower()

    try:
        resp = requests.get(base_url, params=params, headers=headers, timeout=12)
        results = resp.json()

        # Retry without "beach" appended if nothing returned
        if not results and search_payload != query_text:
            params["q"] = query_text
            resp = requests.get(base_url, params=params, headers=headers, timeout=12)
            results = resp.json()

        if not results:
            return []

        ranked = []
        for item in results:
            score = 0
            ent_type = item.get("type", "").lower()
            ent_class = item.get("class", "").lower()
            addr = item.get("address", {})
            display_name = item.get("display_name", "")
            first_token = display_name.split(",")[0].strip()
            dn_lower = display_name.lower()

            score += fuzz.token_sort_ratio(query_text.lower(), first_token.lower()) * 0.4

            if ent_type in ["beach", "coast", "bay", "sea", "ocean"] or \
                    ent_class in ["coastline", "natural", "water"]:
                score += 60
            elif "beach" in dn_lower or "coast" in dn_lower:
                score += 40

            if any(w in dn_lower for w in NON_BEACH_PENALTY_WORDS):
                score -= 40

            district = ""
            for part in display_name.split(","):
                p = part.strip()
                if "district" in p.lower():
                    district = p.lower().replace("district", "").strip().title()
                    break

            ranked.append({
                "score": score,
                "display_title": first_token,
                "full_address": display_name,
                "lat": float(item["lat"]),
                "lon": float(item["lon"]),
                "state": addr.get("state", addr.get("county", "")),
                "country": addr.get("country", ""),
                "district": district,
            })

        ranked.sort(key=lambda x: x["score"], reverse=True)
        return [n for n in ranked if n["score"] > -20][:5]
    except Exception:
        return []


# ==============================================================================
# 4. MARINE TELEMETRY
# ==============================================================================
@st.cache_data(ttl=1800, show_spinner=False)
def fetch_marine_telemetry(lat: float, lon: float) -> dict | None:
    try:
        url = (
            f"https://marine-api.open-meteo.com/v1/marine"
            f"?latitude={lat}&longitude={lon}"
            f"&hourly=wave_height&daily=wave_height_max&timezone=auto"
        )
        return requests.get(url, timeout=10).json()
    except Exception:
        return None


# ==============================================================================
# 5. RSS NEWS FETCHER  — no hardcoded sites, pure Google News RSS
#
# Strategy: run 5 queries covering both ban language and general safety,
# return all headlines + descriptions as plain text for GPT to reason over.
# ==============================================================================
@st.cache_data(ttl=480, show_spinner=False)
def fetch_rss_headlines(search_name: str) -> list[dict]:
    """
    Fetches Google News RSS for multiple targeted queries.
    Returns list of {title, description, pub_date} dicts — raw text, no scoring.
    GPT-4o does all the reasoning from these headlines.
    """
    queries = [
        f"{search_name} beach swimming ban",
        f"{search_name} beach closed prohibited",
        f"{search_name} sea entry banned monsoon",
        f"{search_name} beach safety warning",
        f"{search_name} beach drowning restriction",
    ]

    seen = set()
    results = []

    for q in queries:
        try:
            encoded = requests.utils.quote(q)
            url = f"https://news.google.com/rss/search?q={encoded}&hl=en&gl=IN&ceid=IN:en"
            resp = requests.get(
                url, timeout=10,
                headers={"User-Agent": "Mozilla/5.0 CoastPulseAI/3.0"}
            )
            if resp.status_code != 200:
                continue

            titles = re.findall(r'<title><!\[CDATA\[(.*?)\]\]></title>', resp.text)
            descs = re.findall(r'<description><!\[CDATA\[(.*?)\]\]></description>', resp.text)
            pub_dates = re.findall(r'<pubDate>(.*?)</pubDate>', resp.text)

            # titles[0] is the feed title — skip it
            for i, title in enumerate(titles[1:8]):
                title_clean = title.strip()
                if title_clean in seen:
                    continue
                seen.add(title_clean)

                desc_raw = descs[i] if i < len(descs) else ""
                desc_clean = re.sub(r'<[^>]+>', ' ', desc_raw)
                desc_clean = re.sub(r'\s+', ' ', desc_clean).strip()[:300]
                pub = pub_dates[i][:25].strip() if i < len(pub_dates) else ""

                results.append({
                    "title": title_clean,
                    "desc": desc_clean,
                    "pub_date": pub,
                })
        except Exception:
            continue

    return results[:20]  # cap at 20 to stay within GPT token budget


# ==============================================================================
# 6. WAVE RISK CLASSIFIER  (deterministic — no hardcoding of locations)
# ==============================================================================
def classify_wave_risk(wave_height: float, swimmer_grade: str) -> dict:
    if swimmer_grade == "Beginner / Casual Wader":
        if wave_height > 0.6:
            risk = "HIGH"
            advice = f"Waves of {wave_height:.2f}m are hazardous for beginners — ankle-depth wading only."
        elif wave_height > 0.3:
            risk = "MODERATE"
            advice = f"Waves of {wave_height:.2f}m — stay close to shore and only enter with a lifeguard present."
        else:
            risk = "LOW"
            advice = f"Calm waves of {wave_height:.2f}m — suitable conditions for beginners."

    elif swimmer_grade == "Intermediate Swimmer":
        if wave_height > 1.2:
            risk = "HIGH"
            advice = f"Waves of {wave_height:.2f}m are too strong for intermediate swimmers — avoid open water."
        elif wave_height > 0.7:
            risk = "MODERATE"
            advice = f"Choppy conditions at {wave_height:.2f}m — watch for rip currents."
        else:
            risk = "LOW"
            advice = f"Good conditions at {wave_height:.2f}m for intermediate swimmers."

    else:  # Advanced / Surfer
        if wave_height > 2.5:
            risk = "HIGH"
            advice = f"Extreme swell at {wave_height:.2f}m — experienced surfers with full safety gear only."
        elif wave_height > 1.5:
            risk = "MODERATE"
            advice = f"Solid surf swell at {wave_height:.2f}m — standard safety protocols apply."
        else:
            risk = "LOW"
            advice = f"Light swell at {wave_height:.2f}m — good conditions for advanced swimmers."

    return {
        "risk_level": risk,
        "wave_height_m": wave_height,
        "swimmer_grade": swimmer_grade,
        "advice": advice,
    }


# ==============================================================================
# 7. GPT-4o REASONING AGENT
#
# GPT receives:
#   • Full raw RSS headlines + descriptions (no pre-filtering)
#   • Wave risk data
#   • Location + date context
#
# GPT decides EVERYTHING:
#   • Whether a ban exists (from reading headlines like a human would)
#   • The ban reason and dates (extracted from headline text)
#   • The overall status: BAN BY AUTHORITY / CAUTION / SAFE
#   • The natural language description shown to the user
#
# Nothing is hardcoded — GPT reasons from live news just as a human analyst would.
# ==============================================================================
def run_coastal_safety_agent(
        display_title: str,
        full_address: str,
        user_input: str,
        district: str,
        state: str,
        wave_height: float,
        swimmer_grade: str,
) -> dict:
    # Build a clean 1-2 word search term
    base = user_input.strip().title()
    if len(base.split()) <= 2:
        search_name = base
    elif district and district.lower() not in base.lower():
        search_name = f"{base} {district}"
    else:
        search_name = base

    agent_trace = [{"step": "INIT", "search_name": search_name, "wave_height": wave_height}]

    # ── Fetch live headlines ──────────────────────────────────────────────────
    headlines = fetch_rss_headlines(search_name)
    wave_result = classify_wave_risk(wave_height, swimmer_grade)

    agent_trace.append({"step": "RSS_DONE", "headline_count": len(headlines)})
    agent_trace.append({"step": "WAVE_DONE", "risk": wave_result["risk_level"]})

    # ── Format headlines for GPT ──────────────────────────────────────────────
    if headlines:
        headlines_text = "\n".join(
            f"[{h['pub_date']}] {h['title']}. {h['desc']}"
            for h in headlines
        )
    else:
        headlines_text = "No news headlines retrieved for this location."

    # ── GPT-4o synthesis ──────────────────────────────────────────────────────
    try:
        client = AzureOpenAI(
            api_key=st.secrets["AZURE_OPENAI_API_KEY"],
            api_version="2024-08-01-preview",
            azure_endpoint=st.secrets["AZURE_OPENAI_ENDPOINT"],
        )
        deployment = st.secrets.get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")

        system_prompt = f"""You are CoastPulse AI — a coastal safety intelligence agent.

Today's date: {datetime.now().strftime("%d %B %Y")}

You will receive:
  1. A list of recent news headlines about a beach/coastal location
  2. Live wave height data and risk classification

Your task: read the headlines like an intelligent analyst and produce a safety verdict for a traveller.

══════════════════════════════════════════
STEP 1 — DECIDE THE STATUS
══════════════════════════════════════════

Read every headline carefully. Ask yourself:

A) Do any headlines clearly indicate an ACTIVE official ban, prohibition, restriction,
   or closure of the beach / sea entry?
   Examples of ban language: "swimming banned", "sea entry prohibited", "beach closed by administration",
   "collector imposes ban", "no entry order", "water sports suspended by authorities", etc.

   → If YES and the ban appears to still be in effect as of today's date:
     status = "BAN BY AUTHORITY"

B) If no active ban, but headlines OR wave data suggest dangerous/risky conditions:
   → status = "CAUTION"

C) If no ban and no significant risk:
   → status = "SAFE"

══════════════════════════════════════════
STEP 2 — EXTRACT BAN DETAILS (only if status = "BAN BY AUTHORITY")
══════════════════════════════════════════

From the headline text, extract:
- ban_reason: why the ban was imposed (e.g. "following two drowning incidents", "due to monsoon rough seas", "after tourist safety review")
- ban_dates:  the restriction period if mentioned in headlines (e.g. "1st June to 30th September 2025")
              If no dates found in headlines, set to null.
- ban_by:     who imposed it (e.g. "District Collector", "Municipal Corporation", "State Government") — only if mentioned

══════════════════════════════════════════
STEP 3 — WRITE THE DESCRIPTION
══════════════════════════════════════════

Write 3–4 sentences in warm, clear, conversational English — as if you are a knowledgeable
friend explaining the situation to someone planning a beach trip.

Rules:
- Lead with the most important fact (the ban if active, else the wave risk)
- Include the ban reason and dates naturally in the sentences if available
- Always mention the wave height and what it means for their experience level
- If status is SAFE and no ban — be encouraging but mention any relevant caution
- NEVER include: URLs, website names, domain names, source names (Google News, RSS, etc.),
  technical field names, or phrases like "according to our data"

══════════════════════════════════════════
OUTPUT — return ONLY this raw JSON, no markdown fences:
══════════════════════════════════════════
{{
  "status":      "BAN BY AUTHORITY" | "CAUTION" | "SAFE",
  "bg_type":     "ban" | "caution" | "safe",
  "ban_detected": true | false,
  "ban_reason":  "why the ban was issued, from news" | null,
  "ban_dates":   "date range from news e.g. 1 June to 30 September" | null,
  "ban_by":      "issuing authority from news" | null,
  "description": "3–4 warm conversational sentences for the traveller"
}}"""

        user_msg = f"""Location: {display_title}
Full address: {full_address}
Wave height: {wave_height:.2f}m
Experience level: {swimmer_grade}
Wave risk classification: {wave_result['risk_level']} — {wave_result['advice']}

══ LIVE NEWS HEADLINES ══
{headlines_text}

Read the headlines above and apply the 3-step reasoning to produce the JSON advisory."""

        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg},
            ],
            max_tokens=600,
            temperature=0.1,
        )

        raw = response.choices[0].message.content.strip()
        agent_trace.append({"step": "GPT_DONE", "preview": raw[:300]})

        # Strip accidental markdown fences
        if raw.startswith("```json"):
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif raw.startswith("```"):
            raw = raw.split("```")[1].split("```")[0].strip()

        parsed = json.loads(raw)
        parsed["_agent_trace"] = agent_trace
        parsed["_headlines"] = headlines  # backend only, never rendered
        return parsed

    except Exception as e:
        agent_trace.append({"step": "GPT_ERROR", "error": str(e)})

    # ── Pure-Python fallback (no GPT available) ───────────────────────────────
    # Simple keyword check on headlines for emergency fallback only
    headline_blob = " ".join(
        f"{h['title']} {h['desc']}" for h in headlines
    ).lower()

    ban_keywords = [
        "swimming banned", "beach closed", "entry prohibited", "sea entry banned",
        "no swimming", "swimming prohibited", "ban on swimming", "bans swimming",
        "water sports banned", "beach shut", "entry ban",
    ]
    fallback_ban = any(kw in headline_blob for kw in ban_keywords)
    risk = wave_result["risk_level"]

    if fallback_ban:
        status, bg_type = "BAN BY AUTHORITY", "ban"
        desc = (
            f"Authorities have issued an official ban on sea entry at {display_title}. "
            f"All water activities are currently prohibited. "
            f"Current wave height is {wave_height:.2f}m. "
            f"Please do not enter the water until the ban is officially lifted."
        )
    elif risk == "HIGH":
        status, bg_type = "CAUTION", "caution"
        desc = (
            f"Conditions at {display_title} are risky right now. "
            f"{wave_result['advice']} "
            f"Exercise extreme caution and stay close to shore."
        )
    elif risk == "MODERATE":
        status, bg_type = "CAUTION", "caution"
        desc = (
            f"The sea at {display_title} is moderately choppy. "
            f"{wave_result['advice']} "
            f"Swim only in designated safe zones with lifeguards present."
        )
    else:
        status, bg_type = "SAFE", "safe"
        desc = (
            f"Conditions at {display_title} look good for a beach visit. "
            f"{wave_result['advice']} "
            f"Always swim in supervised areas and be aware of any local flag warnings."
        )

    return {
        "status": status,
        "bg_type": bg_type,
        "ban_detected": fallback_ban,
        "ban_reason": None,
        "ban_dates": None,
        "ban_by": None,
        "description": desc,
        "_agent_trace": agent_trace,
        "_headlines": headlines,
    }


# ==============================================================================
# 8. RUNTIME PIPELINE CONTROLLER
# ==============================================================================
if "selected_spot_data" not in st.session_state:
    st.session_state.selected_spot_data = None
if "last_query_string" not in st.session_state:
    st.session_state.last_query_string = ""

if user_input != st.session_state.last_query_string:
    st.session_state.selected_spot_data = None
    st.session_state.last_query_string = user_input

if user_input:
    country_iso = GLOBAL_COUNTRIES[selected_country]

    # ── Step A: Show location picker ──────────────────────────────────────────
    if st.session_state.selected_spot_data is None:
        matches = resolve_location_candidates(user_input, country_iso)
        if matches:
            st.markdown(
                '<p class="clean-search-text">Please select the matching location below:</p>',
                unsafe_allow_html=True
            )
            for idx, candidate in enumerate(matches):
                lbl = f"📍 {candidate['display_title']}"
                if candidate["state"]:   lbl += f", {candidate['state']}"
                if candidate["country"]: lbl += f" ({candidate['country']})"
                if st.button(lbl, key=f"node_btn_{idx}", use_container_width=True):
                    st.session_state.selected_spot_data = candidate
                    st.rerun()
        else:
            st.markdown("""
                <div style="background:#ffeeef;border:1px solid #fca5a5;padding:15px;
                border-radius:8px;text-align:center;color:#b91c1c;font-size:13.5px;
                font-weight:500;margin-top:20px;">
                    No matching locations found. Please check your spelling.
                </div>""", unsafe_allow_html=True)

    # ── Step B: Run agent and render card ─────────────────────────────────────
    if st.session_state.selected_spot_data is not None:
        node = st.session_state.selected_spot_data
        lat, lon = node["lat"], node["lon"]

        # Fetch wave data
        marine_payload = fetch_marine_telemetry(lat, lon)
        current_wave_height = 0.0
        daily_max_forecasts = []
        forecast_dates = []

        if marine_payload:
            if "hourly" in marine_payload and "wave_height" in marine_payload["hourly"]:
                ts = marine_payload["hourly"]["time"]
                hs = [h if h is not None else 0.0
                      for h in marine_payload["hourly"]["wave_height"]]
                now = datetime.now()
                idx = min(
                    range(len(ts)),
                    key=lambda i: abs(datetime.fromisoformat(ts[i].replace("Z", "")) - now)
                )
                current_wave_height = hs[idx]
            if "daily" in marine_payload and "wave_height_max" in marine_payload["daily"]:
                daily_max_forecasts = [
                    w if w is not None else 0.0
                    for w in marine_payload["daily"]["wave_height_max"]
                ]
                forecast_dates = marine_payload["daily"].get("time", [])

        # Run agent
        with st.spinner("🤖 Analysing live news and wave conditions…"):
            output = run_coastal_safety_agent(
                display_title=node["display_title"],
                full_address=node["full_address"],
                user_input=user_input,
                district=node.get("district", ""),
                state=node.get("state", ""),
                wave_height=current_wave_height,
                swimmer_grade=skill_level,
            )

        # ── Parse output ──────────────────────────────────────────────────────
        status = output.get("status", "SAFE")
        bg_type = output.get("bg_type", "safe")
        has_ban = output.get("ban_detected", False)
        ban_reason = output.get("ban_reason") or ""
        ban_dates = output.get("ban_dates") or ""
        ban_by = output.get("ban_by") or ""
        ai_desc = output.get("description", "")

        # Sanitise description — strip any accidental markup
        for junk in ["```html", "```json", "```", "<div>", "</div>",
                     "<p>", "</p>", "<span>", "</span>"]:
            ai_desc = ai_desc.replace(junk, "")
        ai_desc = ai_desc.strip()

        # ── Status pill ───────────────────────────────────────────────────────
        if has_ban or status == "BAN BY AUTHORITY":
            display_status = "🚫 BAN BY AUTHORITY"
            pill_class = "badge-ban"
            bg_type = "ban"
        elif bg_type == "caution" or status == "CAUTION":
            display_status = "⚠️ CAUTION"
            pill_class = "badge-caution"
        else:
            display_status = "✅ SAFE"
            pill_class = "badge-safe"

        # ── Background image (free Unsplash, one per status) ─────────────────
        # ban    → stormy/dramatic sea
        # caution → rough wave beach
        # safe   → calm tropical beach
        bg_images = {
            "ban": "https://images.unsplash.com/photo-1505118380757-91f5f5632de0"
                   "?auto=format&fit=crop&w=1200&q=80",
            "caution": "https://images.unsplash.com/photo-1519046904884-53103b34b206"
                       "?auto=format&fit=crop&w=1200&q=80",
            "safe": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e"
                    "?auto=format&fit=crop&w=1200&q=80",
        }
        bg_img = bg_images.get(bg_type, bg_images["safe"])

        # ── Ban detail box (only when a ban is confirmed) ─────────────────────
        ban_box_html = ""
        if has_ban or status == "BAN BY AUTHORITY":
            rows = []
            if ban_by:
                rows.append(f"<strong>Issued by:</strong> {ban_by}")
            if ban_reason:
                rows.append(f"<strong>Reason:</strong> {ban_reason.capitalize()}")
            if ban_dates:
                rows.append(f"<strong>Restriction period:</strong> {ban_dates}")
            else:
                rows.append("<strong>Duration:</strong> Ongoing — check local authorities for updates")

            detail_html = "<br>".join(rows) if rows else \
                "Authorities have restricted water access. Treat as ongoing."

            ban_box_html = (
                '<div class="ban-box">'
                '<div class="ban-box-title">🚫 Official Ban Enforced</div>'
                f'<p class="ban-box-body">{detail_html}</p>'
                '</div>'
            )

        # ── Main advisory card ────────────────────────────────────────────────
        card_style = (
            "border-radius:24px;padding:40px;"
            "box-shadow:0 20px 40px rgba(15,23,42,0.16);"
            "border:1px solid rgba(255,255,255,0.1);"
            "margin-top:25px;color:#ffffff;"
            f"background-image:linear-gradient("
            f"rgba(10,20,40,0.60),rgba(10,20,40,0.75)),url({bg_img});"
            "background-size:cover;background-position:center;"
        )
        st.markdown(
            f'<div style="{card_style}">'
            f'<span class="{pill_class}">{display_status}</span>'
            f'<h3 class="advisory-header-title">Safety Report: {node["display_title"]}</h3>'
            f'{ban_box_html}'
            f'<p class="advisory-prose-body">{ai_desc}</p>'
            f'<div class="brand-stamp-footer">✨ CoastPulse AI · Powered by Azure AI Foundry</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        # _agent_trace and _headlines are in output dict — backend only, never rendered

        # ── 7-Day Trip Planner ────────────────────────────────────────────────
        if daily_max_forecasts:
            st.markdown(
                "<br><h4 style='font-size:16px;font-weight:700;color:#0f172a;"
                "margin-bottom:15px;'>📅 Your 7-Day Trip Planner Matrix</h4>",
                unsafe_allow_html=True
            )
            cols = st.columns(7)
            for i in range(min(7, len(daily_max_forecasts))):
                p_date = datetime.strptime(forecast_dates[i], "%Y-%m-%d")
                max_w = daily_max_forecasts[i]

                if has_ban or status == "BAN BY AUTHORITY":
                    lbl, bg, txt = "🚫 BANNED", "#f3e8ff", "#6d28d9"
                elif max_w > 1.6:
                    lbl, bg, txt = "🚫 RISK", "#fff1f2", "#b91c1c"
                elif max_w > 1.1 or status == "CAUTION":
                    lbl, bg, txt = "🟡 CAUTION", "#fef9c3", "#a16207"
                else:
                    lbl, bg, txt = "🟢 PERFECT", "#f0fdf4", "#15803d"

                with cols[i]:
                    st.markdown(
                        f'<div class="planner-grid-card" '
                        f'style="background:{bg};border:1px solid rgba(0,0,0,0.04);">'
                        f'<strong style="font-size:13px;color:#1d4ed8;">'
                        f'{p_date.strftime("%a")}</strong><br>'
                        f'<span style="font-size:10px;color:#64748b;">'
                        f'{p_date.strftime("%b %d")}</span>'
                        f'<p style="margin:8px 0;font-size:11px;font-weight:800;color:{txt};">'
                        f'{lbl}</p>'
                        f'<span style="font-size:10px;color:#475569;">'
                        f'<strong>{max_w:.2f}m</strong></span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
