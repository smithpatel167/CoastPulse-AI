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
    .beach-count-note   { font-size: 12px; color: #64748b; margin-top: -8px; margin-bottom: 14px; }

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
    .ban-box-body  { margin: 6px 0 0 0; font-size: 13.5px; color: #ede9fe; font-weight: 500;
                     line-height: 1.65; }
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
        placeholder="e.g., goa, bali, diu, phuket, miami",
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
# 3. BEACH FINDER
#
# Strategy:
#   PRIMARY  → Overpass API: query OSM for natural=beach nodes/ways/relations
#              within a bounding box around the searched region. This returns
#              ONLY actual beaches — zero restaurants, cafes, or hotels.
#   FALLBACK → Nominatim with strict OSM type filtering (type=beach only).
#
# Why two steps:
#   Nominatim search("goa beach") returns anything with "beach" in its name or
#   address — cafe, resort, apartment. Overpass queries OSM tags directly so
#   only features tagged natural=beach are returned.
#
# region_coords: we first geocode the user's typed region (e.g. "goa", "diu")
# to get a bounding box, then query Overpass within that box.
# ==============================================================================

@st.cache_data(ttl=3600, show_spinner=False)
def geocode_region(query_text: str, country_iso: str) -> dict | None:
    """
    Geocodes the user's typed region name to lat/lon + bounding box.
    Returns the best non-beach result (the region itself, not a beach feature).
    """
    headers = {"User-Agent": "CoastPulseAI/4.0 (contact@coastpulse.ai)"}
    params  = {
        "q":              query_text,
        "format":         "jsonv2",
        "addressdetails": 1,
        "limit":          5,
        "featuretype":    "settlement,country,state,county,city,town,village,island,archipelago",
    }
    if country_iso:
        params["countrycodes"] = country_iso.lower()

    try:
        resp    = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params=params, headers=headers, timeout=12
        )
        results = resp.json()

        if not results:
            # Broader retry
            params.pop("featuretype", None)
            resp    = requests.get(
                "https://nominatim.openstreetmap.org/search",
                params=params, headers=headers, timeout=12
            )
            results = resp.json()

        if not results:
            return None

        # Prefer administrative/place results over beach features
        SKIP_TYPES = {"beach", "coastline"}
        SKIP_AMENITIES = {
            "cafe", "restaurant", "bar", "hotel", "hostel", "resort",
            "hospital", "school", "college", "university",
        }
        for r in results:
            if r.get("type") in SKIP_TYPES:
                continue
            addr = r.get("address", {})
            if addr.get("amenity", "").lower() in SKIP_AMENITIES:
                continue

            bb = r.get("boundingbox", [])   # [south, north, west, east]
            return {
                "lat":          float(r["lat"]),
                "lon":          float(r["lon"]),
                "display_name": r.get("display_name", ""),
                "state":        addr.get("state", addr.get("county", "")),
                "country":      addr.get("country", ""),
                "boundingbox":  bb,   # strings: [S, N, W, E]
            }
        return None
    except Exception:
        return None


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_beaches_overpass(south: float, north: float,
                           west: float,  east: float) -> list[dict]:
    """
    Queries OpenStreetMap Overpass API for all features tagged natural=beach
    within the given bounding box. Returns list of beach dicts.
    No limit — returns every beach OSM knows about in the area.
    """
    # Overpass QL: fetch nodes, ways, and relations with natural=beach
    query = f"""
[out:json][timeout:25];
(
  node["natural"="beach"]({south},{west},{north},{east});
  way["natural"="beach"]({south},{west},{north},{east});
  relation["natural"="beach"]({south},{west},{north},{east});
);
out center tags;
"""
    try:
        resp = requests.post(
            "https://overpass-api.de/api/interpreter",
            data={"data": query},
            timeout=30,
            headers={"User-Agent": "CoastPulseAI/4.0 (contact@coastpulse.ai)"},
        )
        data     = resp.json()
        elements = data.get("elements", [])

        beaches = []
        seen    = set()
        for el in elements:
            tags = el.get("tags", {})
            name = tags.get("name") or tags.get("name:en") or ""
            if not name or name.lower() in seen:
                continue
            seen.add(name.lower())

            # Get coordinates — nodes have lat/lon directly; ways/relations use center
            if el.get("type") == "node":
                lat = el["lat"]
                lon = el["lon"]
            else:
                center = el.get("center", {})
                lat    = center.get("lat", 0.0)
                lon    = center.get("lon", 0.0)

            if lat == 0.0 and lon == 0.0:
                continue

            beaches.append({
                "display_title": name,
                "lat":           lat,
                "lon":           lon,
                "full_address":  f"{name}, {tags.get('addr:city','') or tags.get('addr:state','')}".strip(", "),
                "state":         tags.get("addr:state", ""),
                "country":       tags.get("addr:country", ""),
                "district":      "",
                "score":         100,   # all Overpass results are genuine beaches
            })

        # Sort alphabetically for a clean list
        beaches.sort(key=lambda b: b["display_title"])
        return beaches

    except Exception:
        return []


@st.cache_data(ttl=3600, show_spinner=False)
def nominatim_beach_fallback(query_text: str, country_iso: str) -> list[dict]:
    """
    Fallback: Nominatim search restricted to type=beach only.
    Used when Overpass returns nothing (e.g. bounding box too small or API down).
    """
    headers = {"User-Agent": "CoastPulseAI/4.0 (contact@coastpulse.ai)"}
    params  = {
        "q":              f"{query_text} beach",
        "format":         "jsonv2",
        "addressdetails": 1,
        "limit":          50,
    }
    if country_iso:
        params["countrycodes"] = country_iso.lower()

    HARD_EXCLUDE_TYPES    = {"cafe", "restaurant", "bar", "hotel", "hostel", "fast_food",
                              "airport", "station", "hospital", "school", "college",
                              "university", "mall", "supermarket", "parking"}
    HARD_EXCLUDE_CLASSES  = {"amenity", "shop", "office", "building", "highway",
                              "railway", "aeroway"}
    ALLOW_TYPES           = {"beach", "coastline", "bay", "cove", "strait"}
    ALLOW_CLASSES         = {"natural", "water", "waterway"}

    try:
        resp    = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params=params, headers=headers, timeout=12
        )
        results = resp.json()

        beaches = []
        seen    = set()
        for item in results:
            ent_type  = item.get("type",  "").lower()
            ent_class = item.get("class", "").lower()

            # Strict include/exclude
            if ent_type in HARD_EXCLUDE_TYPES or ent_class in HARD_EXCLUDE_CLASSES:
                continue
            if ent_type not in ALLOW_TYPES and ent_class not in ALLOW_CLASSES:
                # Allow only if the word "beach" appears directly in the feature name
                first_token = item.get("display_name", "").split(",")[0].strip().lower()
                if "beach" not in first_token and "coast" not in first_token:
                    continue

            display_name = item.get("display_name", "")
            first_token  = display_name.split(",")[0].strip()
            addr         = item.get("address", {})

            key = first_token.lower()
            if key in seen:
                continue
            seen.add(key)

            beaches.append({
                "display_title": first_token,
                "lat":           float(item["lat"]),
                "lon":           float(item["lon"]),
                "full_address":  display_name,
                "state":         addr.get("state", addr.get("county", "")),
                "country":       addr.get("country", ""),
                "district":      "",
                "score":         80,
            })

        beaches.sort(key=lambda b: b["display_title"])
        return beaches

    except Exception:
        return []


def resolve_beaches_for_region(query_text: str, country_iso: str) -> tuple[list[dict], str]:
    """
    Master resolver. Returns (beaches_list, region_name_for_news_search).

    1. Geocode the region to get bounding box
    2. Query Overpass for all beaches inside that box
    3. If Overpass finds nothing, fall back to Nominatim beach-only search
    4. Return the region name (e.g. "Diu" or "Goa") for RSS news queries
    """
    region = geocode_region(query_text, country_iso)

    region_name = query_text.strip().title()  # default: use what user typed

    if region:
        # Extract a clean region name from geocoding result
        addr_parts = region["display_name"].split(",")
        region_name = addr_parts[0].strip() if addr_parts else region_name

        bb = region.get("boundingbox", [])
        if len(bb) == 4:
            try:
                south, north = float(bb[0]), float(bb[1])
                west,  east  = float(bb[2]), float(bb[3])

                # Expand box slightly for small territories (e.g. Diu is tiny)
                lat_span = north - south
                lon_span = east  - west
                if lat_span < 0.3:
                    pad    = (0.3 - lat_span) / 2
                    south -= pad
                    north += pad
                if lon_span < 0.3:
                    pad   = (0.3 - lon_span) / 2
                    west -= pad
                    east += pad

                overpass_beaches = fetch_beaches_overpass(south, north, west, east)
                if overpass_beaches:
                    # Enrich with region state/country info if missing
                    for b in overpass_beaches:
                        if not b["state"]:   b["state"]   = region.get("state",   "")
                        if not b["country"]: b["country"] = region.get("country", "")
                    return overpass_beaches, region_name

            except (ValueError, TypeError):
                pass

    # Fallback to Nominatim beach search
    fallback = nominatim_beach_fallback(query_text, country_iso)
    return fallback, region_name


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
# 5. RSS NEWS FETCHER
#
# CRITICAL FIX: always searches using the REGION name (e.g. "Diu", "Goa"),
# NOT the individual beach name (e.g. "Jallandhar Beach").
# A ban on "Diu" covers all beaches in Diu — the news will say "Diu beaches
# banned", not "Jallandhar Beach banned".
# ==============================================================================
@st.cache_data(ttl=480, show_spinner=False)
def fetch_rss_headlines(region_name: str) -> list[dict]:
    """
    Fetches Google News RSS headlines for the region (not specific beach).
    Returns up to 25 deduplicated articles covering ban, safety, and conditions.
    """
    queries = [
        f"{region_name} beach swimming ban",
        f"{region_name} beach closed prohibited entry ban",
        f"{region_name} sea entry banned monsoon restriction",
        f"{region_name} beach safety drowning warning",
        f"{region_name} coastal water sports suspended",
    ]

    seen    = set()
    results = []

    for q in queries:
        try:
            encoded = requests.utils.quote(q)
            url     = f"https://news.google.com/rss/search?q={encoded}&hl=en&gl=IN&ceid=IN:en"
            resp    = requests.get(
                url, timeout=10,
                headers={"User-Agent": "Mozilla/5.0 CoastPulseAI/4.0"}
            )
            if resp.status_code != 200:
                continue

            titles    = re.findall(r'<title><!\[CDATA\[(.*?)\]\]></title>',            resp.text)
            descs     = re.findall(r'<description><!\[CDATA\[(.*?)\]\]></description>', resp.text)
            pub_dates = re.findall(r'<pubDate>(.*?)</pubDate>',                         resp.text)

            for i, title in enumerate(titles[1:8]):   # skip feed title at [0]
                title_clean = title.strip()
                if title_clean in seen:
                    continue
                seen.add(title_clean)

                desc_raw   = descs[i] if i < len(descs) else ""
                desc_clean = re.sub(r'<[^>]+>', ' ', desc_raw)
                desc_clean = re.sub(r'\s+', ' ', desc_clean).strip()[:350]
                pub        = pub_dates[i][:25].strip() if i < len(pub_dates) else ""

                results.append({
                    "title":    title_clean,
                    "desc":     desc_clean,
                    "pub_date": pub,
                })
        except Exception:
            continue

    return results[:25]


# ==============================================================================
# 6. WAVE RISK CLASSIFIER
# ==============================================================================
def classify_wave_risk(wave_height: float, swimmer_grade: str) -> dict:
    if swimmer_grade == "Beginner / Casual Wader":
        if wave_height > 0.6:
            risk, advice = "HIGH", f"Waves of {wave_height:.2f}m are hazardous for beginners — ankle-depth wading only."
        elif wave_height > 0.3:
            risk, advice = "MODERATE", f"Waves of {wave_height:.2f}m — stay close to shore, only enter with a lifeguard present."
        else:
            risk, advice = "LOW", f"Calm waves of {wave_height:.2f}m — suitable conditions for beginners."
    elif swimmer_grade == "Intermediate Swimmer":
        if wave_height > 1.2:
            risk, advice = "HIGH", f"Waves of {wave_height:.2f}m are too strong for intermediate swimmers — avoid open water."
        elif wave_height > 0.7:
            risk, advice = "MODERATE", f"Choppy conditions at {wave_height:.2f}m — watch for rip currents."
        else:
            risk, advice = "LOW", f"Good conditions at {wave_height:.2f}m for intermediate swimmers."
    else:
        if wave_height > 2.5:
            risk, advice = "HIGH", f"Extreme swell at {wave_height:.2f}m — experienced surfers with full safety gear only."
        elif wave_height > 1.5:
            risk, advice = "MODERATE", f"Solid surf swell at {wave_height:.2f}m — standard safety protocols apply."
        else:
            risk, advice = "LOW", f"Light swell at {wave_height:.2f}m — good conditions for advanced swimmers."

    return {"risk_level": risk, "wave_height_m": wave_height,
            "swimmer_grade": swimmer_grade, "advice": advice}


# ==============================================================================
# 7. GPT-4o REASONING AGENT
#
# KEY DESIGN DECISIONS:
#
# A) RSS is searched by REGION (e.g. "Diu"), not by individual beach name.
#    A ban covering "all beaches in Diu" applies to any specific Diu beach.
#
# B) GPT receives today's date prominently and MUST reason about ban expiry:
#    - If news says ban runs "June 1 to July 30" and today is August 8 → ban EXPIRED
#    - GPT must say SAFE or CAUTION based on wave data, not the expired ban
#    - If ban end date is in the future relative to today → ban ACTIVE
#
# C) GPT writes description for the SPECIFIC SELECTED BEACH, not just the region.
#    It knows which exact beach was selected (display_title).
# ==============================================================================
def run_coastal_safety_agent(
    display_title: str,   # specific beach selected (e.g. "Jallandhar Beach")
    full_address:  str,
    region_name:   str,   # region used for news search (e.g. "Diu")
    wave_height:   float,
    swimmer_grade: str,
) -> dict:

    today_str   = datetime.now().strftime("%d %B %Y")
    today_dt    = datetime.now()
    agent_trace = [{"step": "INIT", "beach": display_title,
                    "region": region_name, "wave_height": wave_height}]

    # Fetch headlines using REGION name
    headlines   = fetch_rss_headlines(region_name)
    wave_result = classify_wave_risk(wave_height, swimmer_grade)

    agent_trace.append({"step": "RSS_DONE",  "count": len(headlines), "region": region_name})
    agent_trace.append({"step": "WAVE_DONE", "risk":  wave_result["risk_level"]})

    if headlines:
        headlines_text = "\n".join(
            f"[{h['pub_date']}] {h['title']}. {h['desc']}"
            for h in headlines
        )
    else:
        headlines_text = "No relevant news headlines found for this region."

    try:
        client = AzureOpenAI(
            api_key        = st.secrets["AZURE_OPENAI_API_KEY"],
            api_version    = "2024-08-01-preview",
            azure_endpoint = st.secrets["AZURE_OPENAI_ENDPOINT"],
        )
        deployment = st.secrets.get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")

        system_prompt = f"""You are CoastPulse AI — a real-time coastal safety intelligence agent.

TODAY'S DATE: {today_str}
This date is authoritative. You MUST use it when reasoning about whether any ban or restriction is still active.

════════════════════════════════════════════════════
CONTEXT YOU RECEIVE
════════════════════════════════════════════════════
1. The specific beach the user selected (e.g. "Jallandhar Beach, Diu")
2. The region those headlines were searched for (e.g. "Diu")
3. Live wave height data and risk classification for that exact beach
4. Recent news headlines about the REGION (because official bans typically cover
   all beaches in a region, not individual ones)

════════════════════════════════════════════════════
STEP 1 — SCAN HEADLINES FOR ACTIVE BANS
════════════════════════════════════════════════════

Read every headline and description carefully. Look for:
• Official orders: swimming banned/prohibited, beach closed, sea entry banned,
  no entry, water sports suspended, district collector order, administration order
• Any authority restricting access to beaches in the region
• Drowning incidents that triggered closures

For each ban signal you find, extract:
• What the ban covers (swimming, water sports, all sea entry, etc.)
• The dates: START and END date if mentioned
• Who issued it (district collector, municipal council, state government, etc.)
• The reason (monsoon, drowning deaths, rough seas, safety review, etc.)

════════════════════════════════════════════════════
STEP 2 — CRITICAL: REASON ABOUT BAN DATES vs TODAY
════════════════════════════════════════════════════

Today is {today_str}. This is non-negotiable.

If a ban was found:
  a) If no end date mentioned → assume ban is CURRENTLY ACTIVE → status = "BAN BY AUTHORITY"
  b) If end date is IN THE FUTURE relative to today → ban is ACTIVE → status = "BAN BY AUTHORITY"
  c) If end date has ALREADY PASSED relative to today → ban has EXPIRED
     → Do NOT set status to BAN BY AUTHORITY
     → Instead evaluate wave risk and set status to CAUTION or SAFE accordingly
     → In description, briefly mention the ban has ended and conditions are now X

EXAMPLE: Today is 12 June 2025. Headlines say ban runs "June 1 to July 30".
→ July 30 is in the future → ban is ACTIVE → status = "BAN BY AUTHORITY" ✓

EXAMPLE: Today is 8 August 2025. Headlines say ban ran "June 1 to July 30".
→ July 30 has passed → ban EXPIRED → evaluate wave risk → SAFE or CAUTION ✓

EXAMPLE: Today is 15 July 2025. Headlines say ban with no end date.
→ No end date → treat as ACTIVE → status = "BAN BY AUTHORITY" ✓

If there is a regional ban covering all beaches (e.g. "all beaches in Diu are banned"),
it APPLIES to the specific selected beach too, even if that beach isn't named individually.

════════════════════════════════════════════════════
STEP 3 — WRITE THE DESCRIPTION
════════════════════════════════════════════════════

Write 3–5 warm, clear sentences as if explaining to a friend planning a beach trip.

For BAN BY AUTHORITY:
  • Sentence 1: State clearly that the beach/region has an active official ban
  • Sentence 2: Explain the reason (from news) and who issued the ban
  • Sentence 3: State the restriction period with actual dates from the news
  • Sentence 4: Mention the current wave height and what it means
  • Sentence 5: Safety closing advice

For CAUTION or SAFE:
  • Sentence 1: Overall condition verdict for this specific beach
  • Sentence 2: Wave height and what it means for their experience level  
  • Sentence 3: Practical advice
  • Sentence 4 (optional): Mention if a ban recently ended or any other context

NEVER include: URLs, website names, domain names, source names, technical terms like
"ban_score", "RSS", "matched_tokens", or phrases like "according to our data".

════════════════════════════════════════════════════
OUTPUT — return ONLY this raw JSON, no markdown fences:
════════════════════════════════════════════════════
{{
  "status":       "BAN BY AUTHORITY" | "CAUTION" | "SAFE",
  "bg_type":      "ban" | "caution" | "safe",
  "ban_detected": true | false,
  "ban_expired":  true | false,
  "ban_reason":   "reason extracted from news" | null,
  "ban_dates":    "e.g. 1 June to 30 July 2025" | null,
  "ban_by":       "authority name from news" | null,
  "description":  "3-5 warm sentences for the traveller"
}}"""

        user_msg = f"""Beach selected by user: {display_title}
Full address: {full_address}
Region searched for news: {region_name}
Today's date: {today_str}
Wave height at this beach: {wave_height:.2f}m
Swimmer experience level: {swimmer_grade}
Wave risk classification: {wave_result['risk_level']} — {wave_result['advice']}

══ LIVE NEWS HEADLINES FOR REGION: {region_name} ══
{headlines_text}

Apply the 3-step reasoning. Remember today is {today_str}.
If the headlines mention a ban — check if the ban end date is before or after today.
Return the JSON advisory."""

        response = client.chat.completions.create(
            model       = deployment,
            messages    = [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_msg},
            ],
            max_tokens  = 650,
            temperature = 0.05,   # near-zero temp for reliable date reasoning
        )

        raw = response.choices[0].message.content.strip()
        agent_trace.append({"step": "GPT_DONE", "preview": raw[:300]})

        for fence in ["```json", "```"]:
            if raw.startswith(fence):
                raw = raw.split(fence, 1)[1].split("```")[0].strip()
                break

        parsed = json.loads(raw)
        parsed["_agent_trace"] = agent_trace
        parsed["_headlines"]   = headlines
        return parsed

    except Exception as e:
        agent_trace.append({"step": "GPT_ERROR", "error": str(e)})

    # ── Pure-Python fallback (GPT unavailable) ────────────────────────────────
    headline_blob = " ".join(
        f"{h['title']} {h['desc']}" for h in headlines
    ).lower()
    ban_kws = [
        "swimming banned", "beach closed", "entry prohibited", "sea entry banned",
        "no swimming", "swimming prohibited", "ban on swimming", "bans swimming",
        "water sports banned", "beach shut", "entry ban", "sea closed",
    ]
    fallback_ban = any(kw in headline_blob for kw in ban_kws)
    risk         = wave_result["risk_level"]

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
            f"{wave_result['advice']} Stay close to shore and heed all flag warnings."
        )
    elif risk == "MODERATE":
        status, bg_type = "CAUTION", "caution"
        desc = (
            f"The sea at {display_title} is moderately choppy. "
            f"{wave_result['advice']} Swim only in designated safe zones with lifeguards present."
        )
    else:
        status, bg_type = "SAFE", "safe"
        desc = (
            f"Conditions at {display_title} look good for a beach visit. "
            f"{wave_result['advice']} Always swim in supervised areas and watch for flag warnings."
        )

    return {
        "status": status, "bg_type": bg_type, "ban_detected": fallback_ban,
        "ban_expired": False, "ban_reason": None, "ban_dates": None, "ban_by": None,
        "description": desc, "_agent_trace": agent_trace, "_headlines": headlines,
    }


# ==============================================================================
# 8. RUNTIME PIPELINE CONTROLLER
# ==============================================================================
if "selected_spot_data" not in st.session_state:
    st.session_state.selected_spot_data = None
if "last_query_string" not in st.session_state:
    st.session_state.last_query_string = ""
if "beach_list" not in st.session_state:
    st.session_state.beach_list = []
if "region_name" not in st.session_state:
    st.session_state.region_name = ""

# Reset when user changes query
if user_input != st.session_state.last_query_string:
    st.session_state.selected_spot_data = None
    st.session_state.last_query_string  = user_input
    st.session_state.beach_list         = []
    st.session_state.region_name        = ""

if user_input:
    country_iso = GLOBAL_COUNTRIES[selected_country]

    # ── Step A: Resolve beach list ────────────────────────────────────────────
    if not st.session_state.beach_list:
        with st.spinner("🔍 Finding beaches in this region…"):
            beaches, region_nm = resolve_beaches_for_region(user_input, country_iso)
            st.session_state.beach_list  = beaches
            st.session_state.region_name = region_nm

    beaches    = st.session_state.beach_list
    region_name = st.session_state.region_name

    # ── Step B: Show beach picker ─────────────────────────────────────────────
    if st.session_state.selected_spot_data is None:
        if beaches:
            count = len(beaches)
            st.markdown(
                f'<p class="clean-search-text">🏖️ Found {count} beach{"es" if count != 1 else ""} '
                f'in <strong>{region_name}</strong> — select one to check conditions:</p>',
                unsafe_allow_html=True
            )
            for idx, candidate in enumerate(beaches):
                lbl = f"🏖️ {candidate['display_title']}"
                state_part   = candidate.get("state", "")
                country_part = candidate.get("country", "")
                if state_part:   lbl += f", {state_part}"
                if country_part: lbl += f" ({country_part})"
                if st.button(lbl, key=f"beach_btn_{idx}", use_container_width=True):
                    st.session_state.selected_spot_data = candidate
                    st.rerun()
        else:
            st.markdown("""
                <div style="background:#ffeeef;border:1px solid #fca5a5;padding:15px;
                border-radius:8px;text-align:center;color:#b91c1c;font-size:13.5px;
                font-weight:500;margin-top:20px;">
                    No beaches found for this location. Try a different spelling
                    or select a country from the dropdown.
                </div>""", unsafe_allow_html=True)

    # ── Step C: Run agent and render card ─────────────────────────────────────
    if st.session_state.selected_spot_data is not None:
        node = st.session_state.selected_spot_data
        lat, lon = node["lat"], node["lon"]

        # Wave data
        marine_payload      = fetch_marine_telemetry(lat, lon)
        current_wave_height = 0.0
        daily_max_forecasts = []
        forecast_dates      = []

        if marine_payload:
            if "hourly" in marine_payload and "wave_height" in marine_payload["hourly"]:
                ts  = marine_payload["hourly"]["time"]
                hs  = [h if h is not None else 0.0
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

        with st.spinner("🤖 Analysing live regional news and wave conditions…"):
            output = run_coastal_safety_agent(
                display_title = node["display_title"],
                full_address  = node.get("full_address", node["display_title"]),
                region_name   = region_name,          # ← used for RSS, not beach name
                wave_height   = current_wave_height,
                swimmer_grade = skill_level,
            )

        # ── Parse output ──────────────────────────────────────────────────────
        status      = output.get("status",       "SAFE")
        bg_type     = output.get("bg_type",      "safe")
        has_ban     = output.get("ban_detected",  False)
        ban_expired = output.get("ban_expired",   False)
        ban_reason  = output.get("ban_reason")   or ""
        ban_dates   = output.get("ban_dates")    or ""
        ban_by      = output.get("ban_by")       or ""
        ai_desc     = output.get("description",  "")

        for junk in ["```html", "```json", "```", "<div>", "</div>",
                     "<p>", "</p>", "<span>", "</span>"]:
            ai_desc = ai_desc.replace(junk, "")
        ai_desc = ai_desc.strip()

        # ── Status pill ───────────────────────────────────────────────────────
        if has_ban and not ban_expired:
            display_status = "🚫 BAN BY AUTHORITY"
            pill_class     = "badge-ban"
            bg_type        = "ban"
        elif bg_type == "caution" or status == "CAUTION":
            display_status = "⚠️ CAUTION"
            pill_class     = "badge-caution"
        else:
            display_status = "✅ SAFE"
            pill_class     = "badge-safe"

        # ── Background images ─────────────────────────────────────────────────
        bg_images = {
            "ban":     "https://images.unsplash.com/photo-1505118380757-91f5f5632de0"
                       "?auto=format&fit=crop&w=1200&q=80",   # stormy sea
            "caution": "https://images.unsplash.com/photo-1519046904884-53103b34b206"
                       "?auto=format&fit=crop&w=1200&q=80",   # rough waves
            "safe":    "https://images.unsplash.com/photo-1507525428034-b723cf961d3e"
                       "?auto=format&fit=crop&w=1200&q=80",   # calm tropical beach
        }
        bg_img = bg_images.get(bg_type, bg_images["safe"])

        # ── Ban detail box ────────────────────────────────────────────────────
        ban_box_html = ""
        if has_ban and not ban_expired:
            rows = []
            if ban_by:
                rows.append(f"<strong>Issued by:</strong> {ban_by}")
            if ban_reason:
                rows.append(f"<strong>Reason:</strong> {ban_reason.capitalize()}")
            if ban_dates:
                rows.append(f"<strong>Restriction period:</strong> {ban_dates}")
            else:
                rows.append("<strong>Duration:</strong> Ongoing — verify with local authorities")

            ban_box_html = (
                '<div class="ban-box">'
                '<div class="ban-box-title">🚫 Official Ban In Effect</div>'
                f'<p class="ban-box-body">{"<br>".join(rows)}</p>'
                '</div>'
            )

        # ── Main advisory card ────────────────────────────────────────────────
        card_style = (
            "border-radius:24px;padding:40px;"
            "box-shadow:0 20px 40px rgba(15,23,42,0.16);"
            "border:1px solid rgba(255,255,255,0.1);"
            "margin-top:25px;color:#ffffff;"
            f"background-image:linear-gradient(rgba(10,20,40,0.60),rgba(10,20,40,0.75)),"
            f"url({bg_img});"
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
                max_w  = daily_max_forecasts[i]

                if has_ban and not ban_expired:
                    lbl, bg, txt = "🚫 BANNED",  "#f3e8ff", "#6d28d9"
                elif max_w > 1.6:
                    lbl, bg, txt = "🚫 RISK",    "#fff1f2", "#b91c1c"
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