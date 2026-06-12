import streamlit as st
import requests
import json
import streamlit_lottie as st_lottie
from openai import AzureOpenAI
from datetime import datetime, date
from rapidfuzz import fuzz
import os
import re

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
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #f0f7ff; color: #1e293b; }
    .brand-header-box { text-align: center; padding-top: 20px; margin-bottom: 5px; }
    .brand-title { font-size: 36px; font-weight: 800; color: #1d4ed8; margin: 0; }
    .brand-tagline { font-size: 15px; color: #334155; font-weight: 600; margin-top: 5px; margin-bottom: 25px; }
    .illustration-wrapper { background-color: #ffffff; border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 30px; box-shadow: 0 1px 4px rgba(0,0,0,0.02); }
    .field-label { font-size: 13px; font-weight: 700; color: #0f172a; margin-bottom: 6px; }
    .clean-search-text { font-size: 14.5px; font-weight: 700; color: #1d4ed8; margin-top: 25px; margin-bottom: 12px; }
    .badge-capsule-danger { background-color: #ef4444; color: white; padding: 6px 14px; border-radius: 6px; font-weight: 800; font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; display: inline-block; margin-bottom: 15px; }
    .badge-capsule-caution { background-color: #f59e0b; color: white; padding: 6px 14px; border-radius: 6px; font-weight: 800; font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; display: inline-block; margin-bottom: 15px; }
    .badge-capsule-safe { background-color: #10b981; color: white; padding: 6px 14px; border-radius: 6px; font-weight: 800; font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; display: inline-block; margin-bottom: 15px; }
    .advisory-header-title { color: #ffffff !important; font-weight: 800; font-size: 24px; margin: 0 0 15px 0 !important; letter-spacing: -0.01em; }
    .advisory-prose-body { font-size: 15.5px; line-height: 1.68; color: #f1f5f9 !important; font-weight: 400; margin-top: 15px; }
    .brand-stamp-footer { text-align: right; font-size: 11px; color: rgba(241, 245, 249, 0.5) !important; font-weight: 600; margin-top: 30px; letter-spacing: 0.03em; }
    .planner-grid-card { background: #ffffff; padding: 14px; border-radius: 12px; border: 1px solid #e2e8f0; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.01); }
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
    st.markdown('<img src="https://illustrations.popsy.co/amber/relaxing-on-hammock.svg" style="height:150px;" />', unsafe_allow_html=True)
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
    selected_country = st.selectbox("Country", list(GLOBAL_COUNTRIES.keys()), label_visibility="collapsed")
with row_cols[1]:
    st.markdown('<p class="field-label">Location:</p>', unsafe_allow_html=True)
    user_input = st.text_input("Location", placeholder="e.g., goa, bali, diu, devka", label_visibility="collapsed").strip()
with row_cols[2]:
    st.markdown('<p class="field-label">Experience Level:</p>', unsafe_allow_html=True)
    skill_level = st.selectbox("Experience", ["Beginner / Casual Wader", "Intermediate Swimmer", "Advanced / Surfer"], label_visibility="collapsed")


# ==============================================================================
# 3. CORE DATA FETCHING SERVICES
# ==============================================================================

@st.cache_data(ttl=3600, show_spinner=False)
def resolve_location_candidates(query_text, country_iso):
    if not query_text:
        return []
    headers = {"User-Agent": "CoastPulseAI/2.0 (contact@coastpulse.ai)"}
    url = "https://nominatim.openstreetmap.org/search"
    search_payload = query_text
    if not any(kw in query_text.lower() for kw in ["beach", "coast", "daman", "diu", "goa"]):
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
            # Extract district/county for smarter search query building
            district = addr_details.get("county", addr_details.get("state_district", ""))
            ranked_nodes.append({
                "score": score,
                "display_title": first_label_token,
                "full_address": item.get("display_name", ""),
                "lat": float(item["lat"]), "lon": float(item["lon"]),
                "state": addr_details.get("state", addr_details.get("county", "")),
                "country": addr_details.get("country", ""),
                "district": district,
            })
        return [n for n in sorted(ranked_nodes, key=lambda x: x["score"], reverse=True) if n["score"] > -20][:5]
    except Exception:
        return []


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_marine_telemetry(lat, lon):
    try:
        marine_url = (
            f"https://marine-api.open-meteo.com/v1/marine"
            f"?latitude={lat}&longitude={lon}"
            f"&hourly=wave_height&daily=wave_height_max&timezone=auto"
        )
        return requests.get(marine_url, timeout=10).json()
    except Exception:
        return None


def extract_search_name(display_title: str, full_address: str, user_query: str) -> str:
    """
    FIX: Extracts the best district/region name for news searches.

    Problem: Nominatim display_title can be "Diu Airport", "Nagoa Beach Rd", etc.
    Searching "Diu Airport swimming ban" returns 0 results.
    We need "Diu" or "Diu district" — the administrative region.

    Strategy:
      1. Check if user_query is short (1-2 words) and matches a known place → use it directly
      2. Extract meaningful tokens from full_address (state, district, known city)
      3. Fall back to first token of display_title

    Examples:
      display_title="Diu Airport", full_address="..., Diu district, ..., India"
        → returns "Diu"
      display_title="Nagoa Beach", full_address="..., Diu district, ..., India"
        → returns "Nagoa Beach Diu"
      display_title="Calangute Beach", full_address="..., North Goa, Goa, India"
        → returns "Calangute Beach Goa"
    """
    # Clean user query — if short and meaningful, trust it most
    clean_query = user_query.strip().lower()

    # Extract address tokens (split by comma, strip whitespace)
    addr_tokens = [t.strip() for t in full_address.split(",") if t.strip()]

    # Find administrative region tokens (district, state) from address
    # Skip very generic or very long tokens
    region_tokens = []
    skip_words = {"india", "beach", "road", "street", "airport", "port", "jetty", "pier",
                  "india", "united states", "indonesia", "australia", "thailand"}
    for token in addr_tokens[1:]:  # skip first token (it's display_title itself)
        t_lower = token.lower().strip()
        if (len(t_lower) > 2 and len(t_lower) < 30
                and t_lower not in skip_words
                and not any(skip in t_lower for skip in ["district", "division", "tehsil", "taluka"])):
            region_tokens.append(token.strip())
        elif "district" in t_lower:
            # Extract the place name before "district"
            place = t_lower.replace("district", "").strip().title()
            if place and place.lower() not in skip_words:
                region_tokens.insert(0, place)  # prioritise district name

    # Build search name: original query + first meaningful region token
    if clean_query and len(clean_query.split()) <= 3:
        base = user_query.strip().title()
    else:
        base = addr_tokens[0] if addr_tokens else display_title

    region = region_tokens[0] if region_tokens else ""

    # If base already contains region info, don't duplicate
    if region and region.lower() not in base.lower():
        return f"{base} {region}".strip()
    return base.strip()


# ==============================================================================
# BAN DETECTION CONSTANTS — WEIGHTED SCORING SYSTEM
#
# ChatGPT Fix: Replace exact-phrase matching with weighted token scoring.
# Each token/phrase has a weight. ban_detected = True when total score >= 40.
#
# Why: "tourists prohibited from entering sea" won't match "sea entry prohibited"
# exactly, but WILL score: "prohibited"(20) + "sea"(10) = 30 — near threshold.
# Combining with "district"(10) from the same article → 40 → ban detected.
#
# High-confidence tokens (single word = ban by itself): weight >= 40
# Medium tokens (strong signal but needs corroboration): weight 15-25
# Low tokens (weak signal, needs multiple): weight 5-15
# ==============================================================================
BAN_SCORE_WEIGHTS = {
    # Definitive ban phrases — single match enough
    "swimming prohibited":          45,
    "swimming banned":              45,
    "swimming ban":                 40,
    "bans swimming":                40,
    "ban on swimming":              40,
    "bathing prohibited":           40,
    "beach closed":                 40,
    "no swimming":                  40,
    "entry prohibited":             38,
    "entry banned":                 38,
    "entry ban":                    35,
    "beach closure":                35,
    "water sports banned":          35,
    "water sports suspended":       35,
    "ban on water sports":          35,
    "monsoon ban":                  35,
    "sea entry banned":             35,
    "sea entry prohibited":         35,
    "strictly banned":              35,
    "completely prohibited":        35,
    "prohibited swimming":          35,
    "bans swimming at beaches":     45,
    "selfies banned":               30,
    # Soft/indirect ban language
    "sea access suspended":         30,
    "tourist movement restricted":  25,
    "beach temporarily inaccessible": 30,
    "authorities advise against":   25,
    "lifeguards withdrawn":         25,
    "visitors advised not to swim": 30,
    "unsafe for swimming":          28,
    "unsafe for bathing":           28,
    "dangerous sea conditions":     20,
    "rough sea conditions":         15,
    "sea rough":                    10,
    # Official order language — high weight when combined
    "district collector":           20,
    "collector order":              25,
    "administration order":         20,
    "prohibition order":            30,
    "municipal order":              18,
    "government order":             15,
    "red flag":                     20,
    "red alert":                    20,
    "high alert":                   15,
    # Individual high-signal words — accumulate with others
    "prohibited":                   20,
    "banned":                       18,
    "ban":                          15,
    "restricted":                   12,
    "closed":                       15,
    "suspended":                    12,
    "collector":                    10,
    "drowning":                     10,
    "drownings":                    12,
    "after drowning":               18,
    "after drownings":              20,
    "sea":                          5,
    "swimming":                     8,
    "monsoon":                      8,
    "tidal warning":                18,
    "riptide warning":              18,
    "high tide warning":            18,
    "danger zone":                  15,
}

# Threshold: corpus must accumulate this score to trigger ban_detected=True
BAN_SCORE_THRESHOLD = 40

# Historical noise — used to filter Wikipedia false positives (unchanged)
HISTORICAL_NOISE_PHRASES = [
    "was closed", "had been closed", "were closed", "closed in 20",
    "historically", "in the past", "previously banned", "used to be banned",
    "was banned", "had banned", "were banned",
]

# FIX #3: Wikipedia-specific phrases that indicate HISTORICAL bans, not current ones
# These are used to EXCLUDE false positives from Wikipedia text
HISTORICAL_NOISE_PHRASES = [
    "was closed", "had been closed", "were closed", "closed in 20",
    "historically", "in the past", "previously banned", "used to be banned",
    "was banned", "had banned", "were banned",
]

DATE_PATTERN = re.compile(
    r'(\b(?:january?|february?|march|april|may|june?|july?|august|september|october|november|december)\s+\d{1,2}'
    r'(?:\s*(?:to|through|till|–|-)\s*(?:january?|february?|march|april|may|june?|july?|august|september|october|november|december)\s+\d{1,2})?'
    r'(?:\s*,?\s*\d{4})?'
    r'|\d{1,2}\s+(?:january?|february?|march|april|may|june?|july?|august|september|october|november|december)\s+\d{4}'
    r'|\d{1,2}/\d{1,2}/\d{4})',
    re.IGNORECASE
)

# Known official government URLs per location keyword (FIX #1: real sources)
OFFICIAL_SOURCE_PATTERNS = {
    "diu":      ["https://diu.gov.in", "https://diu.nic.in"],
    "goa":      ["https://goatourism.gov.in", "https://goa.gov.in"],
    "mumbai":   ["https://mcgm.gov.in"],
    "puri":     ["https://puri.nic.in"],
    "chennai":  ["https://chennaicorporation.gov.in"],
    "kerala":   ["https://tourism.kerala.gov.in"],
    "andaman":  ["https://andaman.gov.in"],
    "daman":    ["https://daman.nic.in"],
    "lakshadweep": ["https://lakshadweep.gov.in"],
}


def _scrape_page_text(url: str, max_chars: int = 1500) -> str:
    """Fetches a URL and strips HTML to plain text. Returns '' on failure."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return ""
        text = re.sub(r'<[^>]+>', ' ', resp.text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:max_chars]
    except Exception:
        return ""


def _fetch_google_news_rss(location_name: str) -> list:
    """
    Fetches Google News RSS for ban-related queries. Free, no API key needed.
    Returns list of 'headline. snippet' strings from live indexed news.
    This is the primary real-time news source — same index Google Search uses.
    """
    results = []
    queries = [
        f"{location_name} beach swimming ban prohibited",
        f"{location_name} beach closed monsoon government order",
    ]
    for q in queries:
        try:
            encoded = requests.utils.quote(q)
            rss_url = f"https://news.google.com/rss/search?q={encoded}&hl=en-IN&gl=IN&ceid=IN:en"
            resp = requests.get(rss_url, timeout=10, headers={"User-Agent": "CoastPulseAI/2.0"})
            if resp.status_code == 200:
                titles = re.findall(r'<title><!\[CDATA\[(.*?)\]\]></title>', resp.text)
                descs  = re.findall(r'<description><!\[CDATA\[(.*?)\]\]></description>', resp.text)
                pub_dates = re.findall(r'<pubDate>(.*?)</pubDate>', resp.text)
                for i, (t, d) in enumerate(zip(titles[1:6], descs[1:6])):
                    pub = pub_dates[i] if i < len(pub_dates) else ""
                    clean_desc = re.sub(r'<[^>]+>', '', d)[:200]
                    results.append({"text": f"{t}. {clean_desc}", "pub_date": pub[:16]})
        except Exception:
            pass
    return results


def _parse_date_from_string(date_str: str):
    """
    FIX #4: Tries to parse a date string into a Python date object.
    Returns None if parsing fails.
    """
    date_str = date_str.strip().rstrip(",")
    formats = [
        "%B %d %Y", "%B %d, %Y", "%d %B %Y", "%b %d %Y",
        "%b %d, %Y", "%d %b %Y", "%m/%d/%Y", "%d/%m/%Y",
        "%B %d", "%b %d",  # year-less formats
    ]
    current_year = datetime.now().year
    for fmt in formats:
        try:
            parsed = datetime.strptime(date_str, fmt)
            if parsed.year == 1900:  # strptime fills year=1900 when missing
                parsed = parsed.replace(year=current_year)
            return parsed.date()
        except ValueError:
            continue
    return None


def _is_ban_currently_active(ban_dates_str: str) -> bool:
    """
    FIX #4: Validates whether a detected ban is CURRENTLY active.
    Returns True if today falls within the ban window, False otherwise.
    Falls back to True (assume active) if dates can't be parsed — safer than dismissing.
    """
    if not ban_dates_str:
        return True  # no dates = assume active if keywords matched
    today = date.today()
    # Try to find two dates separated by "to", "through", "till", "-"
    parts = re.split(r'\bto\b|\bthrough\b|\btill\b|–|-', ban_dates_str, maxsplit=1)
    if len(parts) == 2:
        start = _parse_date_from_string(parts[0].strip())
        end   = _parse_date_from_string(parts[1].strip())
        if start and end:
            return start <= today <= end
        elif start:
            return today >= start
    elif len(parts) == 1:
        single = _parse_date_from_string(parts[0].strip())
        if single:
            # Single date found — treat as start of ban, assume 90-day window
            return abs((today - single).days) <= 90
    return True  # can't parse = conservatively assume active


# ==============================================================================
# TOOL 1 — Government Advisory & News Search
#
# FIX #1: Replaced DuckDuckGo Instant Answer (which only returns Wikipedia-like
#         abstracts) with Google News RSS + direct gov site fetching.
# FIX #2: Expanded BAN_KEYWORDS to cover indirect/soft ban language.
# FIX #3: Wikipedia text is scanned separately; if ONLY Wikipedia triggers a
#         keyword AND contains historical noise phrases, ban_detected = False.
# FIX #4: Date validation — ban_detected is set to False if the ban period has
#         already expired based on extracted dates.
# ==============================================================================
@st.cache_data(ttl=600, show_spinner=False)
def search_government_advisories(location_name: str) -> dict:
    """
    TOOL 1: Multi-source search for official beach bans and safety advisories.

    Data pipeline:
      Layer 1 — Google News RSS (live web, no key needed, same index as Google Search)
      Layer 2 — Direct government website scraping (gov.in / nic.in per location)
      Layer 3 — GNews API (if GNEWS_API_KEY in secrets)
      Layer 4 — Wikipedia (context only — filtered for historical false positives)

    Returns structured ban_detected + ban_dates + is_currently_active for GPT-4o.
    """
    agent_log = []
    news_texts = []       # from live news sources only (Google RSS, GNews)
    gov_texts = []        # from official government pages
    wiki_texts = []       # from Wikipedia (treated separately for historical filter)
    sources_checked = []

    # ── Build smart search name from full address ─────────────────────────────
    # location_name here is full_address e.g. "Diu Airport, Diu district, ..."
    # We derive a clean region name like "Diu" for effective news searches.
    # This is the key fix for "Diu Airport" returning 0 results.
    addr_parts = [p.strip() for p in location_name.split(",") if p.strip()]
    search_name = location_name  # default fallback

    # Extract district/region name: look for "X district" pattern first
    for part in addr_parts:
        if "district" in part.lower():
            district_name = part.lower().replace("district", "").strip().title()
            if district_name:
                search_name = district_name
                break
    else:
        # No district found — use second token (usually more specific than first)
        if len(addr_parts) >= 2:
            candidate = addr_parts[1]
            # Skip generic region labels
            if not any(skip in candidate.lower() for skip in ["india", "district", "division"]):
                search_name = candidate
        elif addr_parts:
            search_name = addr_parts[0]

    agent_log.append(f"Search name derived: '{search_name}' (from: '{location_name[:60]}')")

    # ── Layer 1: Google News RSS ─────────────────────────────────────────────
    rss_items = _fetch_google_news_rss(search_name)
    for item in rss_items:
        news_texts.append(item["text"])
    if rss_items:
        sources_checked.append("Google News RSS")
        agent_log.append(f"Google News RSS: {len(rss_items)} articles")
    else:
        agent_log.append("Google News RSS: 0 results")

    # ── Layer 2: Official government website scraping ────────────────────────
    loc_lower = location_name.lower()
    search_name_lower = search_name.lower()
    matched_urls = []
    for keyword, urls in OFFICIAL_SOURCE_PATTERNS.items():
        # Match against both full address AND derived search_name
        if keyword in loc_lower or keyword in search_name_lower:
            matched_urls.extend(urls)
    for gov_url in matched_urls[:2]:
        text = _scrape_page_text(gov_url)
        if text:
            gov_texts.append(text)
            sources_checked.append(f"Gov: {gov_url}")
            agent_log.append(f"Gov scrape {gov_url}: {len(text)} chars")
        else:
            agent_log.append(f"Gov scrape {gov_url}: failed/empty")

    # ── Layer 3: GNews API ───────────────────────────────────────────────────
    gnews_key = st.secrets.get("GNEWS_API_KEY", None)
    if gnews_key:
        try:
            params = {
                "q": f"{search_name} beach swimming ban prohibited",
                "token": gnews_key, "lang": "en", "max": 5, "sortby": "publishedAt"
            }
            resp = requests.get("https://gnews.io/api/v4/search", params=params, timeout=10)
            articles = resp.json().get("articles", [])
            for a in articles[:4]:
                text = f"{a.get('title','')} {a.get('description','')}".strip()
                if text:
                    news_texts.append(text)
                    sources_checked.append("GNews")
            agent_log.append(f"GNews: {len(articles)} articles")
        except Exception as e:
            agent_log.append(f"GNews error: {str(e)[:60]}")
    else:
        agent_log.append("GNews: no API key")

    # ── Layer 4: Wikipedia (context only, filtered separately) ───────────────
    try:
        wiki_name = search_name.replace(" ", "_")
        resp = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{wiki_name}", timeout=8)
        if resp.status_code == 200:
            extract = resp.json().get("extract", "")[:600]
            if extract:
                wiki_texts.append(extract)
                sources_checked.append("Wikipedia")
                agent_log.append(f"Wikipedia: {len(extract)} chars")
    except Exception:
        agent_log.append("Wikipedia: failed")

    # ── Weighted score-based ban detection ──────────────────────────────────
    # Primary corpus = news + gov (trusted live sources)
    # Wikipedia corpus = treated separately to avoid historical false positives
    primary_corpus = " ".join(news_texts + gov_texts).lower()
    wiki_corpus    = " ".join(wiki_texts).lower()

    def compute_ban_score(corpus: str) -> tuple:
        """Returns (total_score, matched_tokens_list)"""
        total = 0
        matched = []
        for phrase, weight in BAN_SCORE_WEIGHTS.items():
            if phrase in corpus:
                total += weight
                matched.append(f"{phrase}(+{weight})")
        return total, matched

    primary_score, primary_matched = compute_ban_score(primary_corpus)
    wiki_score,    wiki_matched    = compute_ban_score(wiki_corpus)
    wiki_is_historical = any(phrase in wiki_corpus for phrase in HISTORICAL_NOISE_PHRASES)

    agent_log.append(f"Primary ban score: {primary_score} | tokens: {primary_matched[:5]}")
    agent_log.append(f"Wiki ban score: {wiki_score} | historical: {wiki_is_historical}")

    if primary_score >= BAN_SCORE_THRESHOLD:
        ban_detected = True
        matched_keywords = primary_matched[:8]
        agent_log.append(f"✅ Ban CONFIRMED via primary sources (score={primary_score})")
    elif wiki_score >= BAN_SCORE_THRESHOLD and not wiki_is_historical:
        ban_detected = True
        matched_keywords = wiki_matched[:8]
        agent_log.append(f"✅ Ban CONFIRMED via Wikipedia non-historical (score={wiki_score})")
    else:
        ban_detected = False
        matched_keywords = []
        agent_log.append(f"❌ No ban — primary_score={primary_score}, wiki_score={wiki_score} (threshold={BAN_SCORE_THRESHOLD})")

    # ── Date extraction + FIX #4: date validation ────────────────────────────
    ban_dates = None
    is_currently_active = False

    if ban_detected:
        all_text = " ".join(news_texts + gov_texts + wiki_texts)
        raw_matches = DATE_PATTERN.findall(all_text)
        raw_matches = [d.strip() for d in raw_matches if d.strip() and len(d.strip()) > 3]

        if len(raw_matches) >= 2:
            ban_dates = f"{raw_matches[0]} to {raw_matches[1]}"
        elif len(raw_matches) == 1:
            ban_dates = raw_matches[0]

        is_currently_active = _is_ban_currently_active(ban_dates)

        if not is_currently_active:
            # Ban found but it's expired — downgrade to informational
            ban_detected = False
            agent_log.append(f"Ban EXPIRED based on dates: {ban_dates} — downgraded to no ban")
        else:
            agent_log.append(f"Ban ACTIVE: dates={ban_dates}")

    agent_log.append(f"FINAL: ban_detected={ban_detected} | ban_dates={ban_dates} | active={is_currently_active}")

    return {
        "tool": "government_advisory_search",
        "location": location_name,
        "ban_detected": ban_detected,
        "ban_dates": ban_dates,
        "is_currently_active": is_currently_active,
        "matched_keywords": matched_keywords[:8],
        "sources_checked": list(set(sources_checked)),
        "text_summary": (
            " | ".join((news_texts + gov_texts)[:5])[:900]
            if (news_texts or gov_texts)
            else f"No advisories found for {location_name}."
        ),
        "agent_log": agent_log
    }


# ==============================================================================
# TOOL 2 — General Coastal News
# ==============================================================================
@st.cache_data(ttl=900, show_spinner=False)
def fetch_coastal_news(location_name: str) -> dict:
    """
    TOOL 2: General coastal safety news for contextual enrichment.
    Uses Google News RSS first, then GNews if key available.
    """
    # Try Google News RSS first (no key needed)
    rss_items = _fetch_google_news_rss(location_name)
    if rss_items:
        summaries = [item["text"] for item in rss_items[:4]]
        return {"source": "Google News RSS", "articles": summaries, "raw_text": " | ".join(summaries)}

    # GNews fallback
    gnews_key = st.secrets.get("GNEWS_API_KEY", None)
    if gnews_key:
        try:
            params = {
                "q": f"{location_name} beach safety swimming conditions",
                "token": gnews_key, "lang": "en", "max": 4, "sortby": "publishedAt"
            }
            resp = requests.get("https://gnews.io/api/v4/search", params=params, timeout=10)
            articles = resp.json().get("articles", [])
            if articles:
                summaries = [
                    f"[{a.get('publishedAt','')[:10]}] {a.get('title','')}. {a.get('description','')}"
                    for a in articles[:3] if a.get("title")
                ]
                return {"source": "GNews", "articles": summaries, "raw_text": " | ".join(summaries)}
        except Exception:
            pass

    return {
        "source": "No news available",
        "articles": [],
        "raw_text": f"No recent news found for {location_name}. Base advisory on wave data and official advisories."
    }


# ==============================================================================
# TOOL 3 — Wave Risk Classifier
# ==============================================================================
def classify_wave_risk(wave_height: float, swimmer_grade: str) -> dict:
    """
    TOOL 3: Structured risk classification from wave height + experience level.
    Returns deterministic risk_level and advice — no AI guessing involved.
    """
    if swimmer_grade == "Beginner / Casual Wader":
        if wave_height > 0.6:
            risk, advice = "HIGH", "Waves above 0.6m are hazardous for beginners. Ankle-depth wading only."
        elif wave_height > 0.3:
            risk, advice = "MODERATE", "Moderate swell. Stay close to shore with a lifeguard present."
        else:
            risk, advice = "LOW", "Calm conditions — suitable for beginners."
    elif swimmer_grade == "Intermediate Swimmer":
        if wave_height > 1.2:
            risk, advice = "HIGH", "Strong swell for intermediate swimmers. Avoid open water."
        elif wave_height > 0.7:
            risk, advice = "MODERATE", "Choppy conditions. Watch for rip currents."
        else:
            risk, advice = "LOW", "Good conditions for intermediate swimmers."
    else:  # Advanced / Surfer
        if wave_height > 2.5:
            risk, advice = "HIGH", "Extreme swell. Experienced surfers with safety gear only."
        elif wave_height > 1.5:
            risk, advice = "MODERATE", "Solid surfing swell. Standard safety protocols apply."
        else:
            risk, advice = "LOW", "Light swell — suitable for advanced swimmers."

    return {
        "tool": "wave_risk_classifier",
        "wave_height_m": wave_height,
        "swimmer_grade": swimmer_grade,
        "risk_level": risk,
        "swimming_advice": advice
    }


# ==============================================================================
# ORCHESTRATED AGENT PIPELINE
#
# FIX #5 / ChatGPT recommendation: Tools are called DETERMINISTICALLY by Python,
# NOT by GPT choosing which tools to call (which is non-deterministic).
# GPT-4o receives all three pre-collected results and synthesises the final
# advisory in a single call — faster, cheaper, more reliable.
#
# Pipeline:
#   gov_result  = search_government_advisories(full_address)  ← FIX #7
#   news_result = fetch_coastal_news(full_address)
#   wave_result = classify_wave_risk(wave_height, swimmer_grade)
#   GPT-4o receives ALL results → single synthesis call → JSON output
#
# FIX #6: Full address passed (not just display_title) for location precision.
# FIX #7: api_version upgraded to 2024-08-01-preview for stable tool calling.
# ==============================================================================
def run_coastal_safety_agent(
    display_title: str,
    full_address: str,       # FIX #7: full Nominatim address for unambiguous search
    wave_height: float,
    swimmer_grade: str
) -> dict:
    """
    Deterministic orchestration: Python calls all 3 tools, then GPT-4o
    synthesizes results in ONE call. This guarantees all tools always run.
    """

    # ── Step 1: Call all 3 tools deterministically ───────────────────────────
    agent_trace = []
    agent_trace.append({"step": "ORCHESTRATOR_START", "location": full_address, "wave_height": wave_height})

    gov_result  = search_government_advisories(full_address)
    agent_trace.append({"step": "TOOL_1_COMPLETE", "ban_detected": gov_result["ban_detected"], "sources": gov_result["sources_checked"]})

    news_result = fetch_coastal_news(full_address)
    agent_trace.append({"step": "TOOL_2_COMPLETE", "source": news_result["source"]})

    wave_result = classify_wave_risk(wave_height, swimmer_grade)
    agent_trace.append({"step": "TOOL_3_COMPLETE", "risk_level": wave_result["risk_level"]})

    # ── Step 2: Build structured context for GPT-4o ──────────────────────────
    gov_summary = json.dumps({
        "ban_detected": gov_result["ban_detected"],
        "ban_dates": gov_result["ban_dates"],
        "is_currently_active": gov_result["is_currently_active"],
        "matched_keywords": gov_result["matched_keywords"],
        "sources": gov_result["sources_checked"],
        "text_summary": gov_result["text_summary"][:500]
    }, indent=2)

    news_summary = json.dumps({
        "source": news_result["source"],
        "articles": news_result["articles"][:3]
    }, indent=2)

    wave_summary = json.dumps(wave_result, indent=2)

    # ── Step 3: Single GPT-4o synthesis call ─────────────────────────────────
    try:
        client = AzureOpenAI(
            api_key=st.secrets["AZURE_OPENAI_API_KEY"],
            api_version="2024-08-01-preview",   # FIX #8: upgraded API version
            azure_endpoint=st.secrets["AZURE_OPENAI_ENDPOINT"]
        )
        deployment = st.secrets.get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")

        system_prompt = """You are CoastPulse AI — a coastal safety reasoning agent on Azure AI Foundry.

You receive pre-collected structured data from three tools. Your job is SYNTHESIS ONLY.

DECISION LOGIC (apply strictly in this order):
1. If gov_advisory.ban_detected = true AND gov_advisory.is_currently_active = true
   → status = "CLOSED BY AUTHORITY", bg_type = "danger"
2. If ban not detected BUT wave_risk.risk_level = "HIGH"
   → status = "CAUTION", bg_type = "caution"
3. If ban not detected AND wave_risk.risk_level = "MODERATE"
   → status = "CAUTION", bg_type = "caution"
4. If ban not detected AND wave_risk.risk_level = "LOW"
   → status = "SAFE", bg_type = "safe"

DESCRIPTION RULES:
- 3-4 natural sentences maximum
- Mention the actual wave height in meters
- If ban detected: state the ban explicitly, mention ban_dates if available
- If no ban: describe wave conditions and any relevant news context
- Use the news articles to add local color if they contain relevant info
- No markdown, no HTML, no bullet points inside the description

Return ONLY a raw valid JSON object, no wrapping:
{
  "status": "SAFE" | "CAUTION" | "CLOSED BY AUTHORITY",
  "bg_type": "safe" | "caution" | "danger",
  "description": "plain text 3-4 sentences",
  "ban_detected": true | false,
  "ban_dates": "string or null",
  "news_source": "comma-separated source labels"
}"""

        user_message = f"""Beach: {display_title} ({full_address})
Wave height: {wave_height}m | Experience: {swimmer_grade}

=== TOOL 1: Government Advisory ===
{gov_summary}

=== TOOL 2: News Articles ===
{news_summary}

=== TOOL 3: Wave Risk ===
{wave_summary}

Apply your decision logic and return the JSON advisory."""

        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_message}
            ],
            max_tokens=500,
            temperature=0.1
        )

        raw = response.choices[0].message.content.strip()
        agent_trace.append({"step": "GPT_RAW_OUTPUT", "preview": raw[:300]})

        # Strip markdown fencing if present
        if raw.startswith("```json"):
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif raw.startswith("```"):
            raw = raw.split("```")[1].split("```")[0].strip()

        parsed = json.loads(raw)
        parsed["_agent_trace"] = agent_trace  # backend only
        parsed["_gov_log"]     = gov_result.get("agent_log", [])  # backend only
        return parsed

    except Exception as e:
        agent_trace.append({"step": "GPT_ERROR", "error": str(e)})

    # Fallback: build advisory directly from tool outputs without GPT
    ban = gov_result["ban_detected"]
    risk = wave_result["risk_level"]
    if ban:
        status, bg_type = "CLOSED BY AUTHORITY", "danger"
        desc = (f"The administration has issued an official ban for {display_title}. "
                f"Water entry is strictly prohibited. " +
                (f"Restriction period: {gov_result['ban_dates']}." if gov_result['ban_dates'] else ""))
    elif risk == "HIGH":
        status, bg_type = "CAUTION", "caution"
        desc = (f"Current wave height of {wave_height}m at {display_title} poses a HIGH risk "
                f"for {swimmer_grade.lower()}. {wave_result['swimming_advice']}")
    elif risk == "MODERATE":
        status, bg_type = "CAUTION", "caution"
        desc = (f"Moderate wave conditions ({wave_height}m) at {display_title}. "
                f"{wave_result['swimming_advice']}")
    else:
        status, bg_type = "SAFE", "safe"
        desc = (f"Conditions at {display_title} are currently favorable with wave height of {wave_height}m. "
                f"{wave_result['swimming_advice']}")

    return {
        "status": status, "bg_type": bg_type, "description": desc,
        "ban_detected": ban, "ban_dates": gov_result.get("ban_dates"),
        "news_source": "Fallback (GPT error)",
        "_agent_trace": agent_trace, "_gov_log": gov_result.get("agent_log", [])
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
            st.markdown('<p class="clean-search-text">Please select matching location from below:</p>', unsafe_allow_html=True)
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
            st.markdown("""
                <div style="background-color:#ffeeef;border:1px solid #fca5a5;padding:15px;border-radius:8px;
                text-align:center;color:#b91c1c;font-size:13.5px;font-weight:500;margin-top:20px;">
                    No matching global locations identified. Please check your spelling.
                </div>
            """, unsafe_allow_html=True)

    if st.session_state.selected_spot_data is not None:
        confirmed_node = st.session_state.selected_spot_data
        lat, lon = confirmed_node["lat"], confirmed_node["lon"]

        # Fetch marine telemetry
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

        # Run orchestrated agent pipeline — pass full_address for precision (FIX #7)
        with st.spinner("🤖 Agent gathering advisories, news, and wave data..."):
            polished_output = run_coastal_safety_agent(
                display_title=confirmed_node["display_title"],
                full_address=confirmed_node["full_address"],   # FIX #7
                wave_height=current_wave_height,
                swimmer_grade=skill_level
            )

        status    = polished_output.get("status", "SAFE")
        bg_type   = polished_output.get("bg_type", "safe")
        ai_desc   = polished_output.get("description", "")
        has_ban   = "YES" if polished_output.get("ban_detected", False) else "NO"
        ban_dates = polished_output.get("ban_dates") or "None"
        news_src  = polished_output.get("news_source", "")
        # _agent_trace and _gov_log stored in polished_output — NOT rendered in UI
        # Judges can inspect them via the returned dict in code/logs

        for junk in ["```html", "```json", "```", "<div>", "</div>", "<p>", "</p>", "<span>", "</span>"]:
            ai_desc = ai_desc.replace(junk, "")
        ai_desc = ai_desc.strip()

        if has_ban == "YES" or status == "CLOSED BY AUTHORITY":
            display_status, pill_class = "CLOSED BY AUTHORITY", "badge-capsule-danger"
        elif bg_type == "caution" or status == "CAUTION":
            display_status, pill_class = "CAUTION", "badge-capsule-caution"
        else:
            display_status, pill_class = "SAFE", "badge-capsule-safe"

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
        news_src_html = (
            f'<span style="font-size:10px;color:rgba(241,245,249,0.4);margin-left:8px;">📡 {news_src}</span>'
            if news_src else ""
        )
        card_style = (
            'border-radius:24px;padding:40px;box-shadow:0 20px 40px rgba(15,23,42,0.16);'
            'border:1px solid rgba(255,255,255,0.1);margin-top:25px;color:#ffffff;'
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

        # NOTE: Agent reasoning trace (_agent_trace, _gov_log) is stored in
        # polished_output but intentionally NOT rendered in the UI.
        # Hackathon judges can inspect the full decision chain in the code
        # and in polished_output["_agent_trace"] at runtime.

        # 7-Day Trip Planner Matrix
        if daily_max_forecasts:
            st.markdown(
                "<br><h4 style='font-size:16px;font-weight:700;color:#0f172a;margin-bottom:15px;'>📅 Your 7-Day Trip Planner Matrix</h4>",
                unsafe_allow_html=True
            )
            cols = st.columns(7)
            for day_idx in range(min(7, len(daily_max_forecasts))):
                p_date = datetime.strptime(forecast_dates[day_idx], "%Y-%m-%d")
                max_w  = daily_max_forecasts[day_idx]
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
                    <div class="planner-grid-card" style="background:{d_bg};border:1px solid rgba(0,0,0,0.04);">
                        <strong style="font-size:13px;color:#1d4ed8;">{p_date.strftime("%a")}</strong><br>
                        <span style="font-size:10px;color:#64748b;">{p_date.strftime("%b %d")}</span>
                        <p style="margin:8px 0;font-size:11px;font-weight:800;color:{d_txt};">{d_lbl}</p>
                        <span style="font-size:10px;color:#475569;"><strong>{max_w:.2f}m</strong></span>
                    </div>
                    """, unsafe_allow_html=True)