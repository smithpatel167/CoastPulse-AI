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
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #f0f7ff; color: #1e293b; }
    .brand-header-box { text-align: center; padding-top: 20px; margin-bottom: 5px; }
    .brand-title { font-size: 36px; font-weight: 800; color: #1d4ed8; margin: 0; }
    .brand-tagline { font-size: 15px; color: #334155; font-weight: 600; margin-top: 5px; margin-bottom: 25px; }
    .illustration-wrapper { background-color: #ffffff; border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 30px; box-shadow: 0 1px 4px rgba(0,0,0,0.02); }
    .field-label { font-size: 13px; font-weight: 700; color: #0f172a; margin-bottom: 6px; }
    .clean-search-text { font-size: 14.5px; font-weight: 700; color: #1d4ed8; margin-top: 25px; margin-bottom: 12px; }
    .badge-capsule-danger  { background-color: #ef4444; color: white; padding: 6px 14px; border-radius: 6px; font-weight: 800; font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; display: inline-block; margin-bottom: 15px; }
    .badge-capsule-caution { background-color: #f59e0b; color: white; padding: 6px 14px; border-radius: 6px; font-weight: 800; font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; display: inline-block; margin-bottom: 15px; }
    .badge-capsule-safe    { background-color: #10b981; color: white; padding: 6px 14px; border-radius: 6px; font-weight: 800; font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; display: inline-block; margin-bottom: 15px; }
    .advisory-header-title  { color: #ffffff !important; font-weight: 800; font-size: 24px; margin: 0 0 15px 0 !important; letter-spacing: -0.01em; }
    .advisory-prose-body    { font-size: 15.5px; line-height: 1.68; color: #f1f5f9 !important; font-weight: 400; margin-top: 15px; }
    .brand-stamp-footer     { text-align: right; font-size: 11px; color: rgba(241,245,249,0.5) !important; font-weight: 600; margin-top: 30px; letter-spacing: 0.03em; }
    .planner-grid-card      { background: #ffffff; padding: 14px; border-radius: 12px; border: 1px solid #e2e8f0; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.01); }
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
# 3. LOCATION RESOLVER
# ==============================================================================
NON_BEACH_PENALTY_WORDS = ["airport", "railway", "station", "hotel", "resort",
                            "hospital", "school", "college", "university", "road",
                            "highway", "mall", "market", "temple", "mosque", "church"]

@st.cache_data(ttl=3600, show_spinner=False)
def resolve_location_candidates(query_text, country_iso):
    if not query_text:
        return []
    headers = {"User-Agent": "CoastPulseAI/2.0 (contact@coastpulse.ai)"}
    url = "https://nominatim.openstreetmap.org/search"
    search_payload = query_text
    if not any(kw in query_text.lower() for kw in ["beach", "coast", "goa", "diu"]):
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
            ent_type     = item.get("type", "").lower()
            ent_class    = item.get("class", "").lower()
            addr_details = item.get("address", {})
            display_name = item.get("display_name", "")
            first_token  = display_name.split(",")[0].strip()
            dn_lower     = display_name.lower()

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

            ranked_nodes.append({
                "score":         score,
                "display_title": first_token,
                "full_address":  display_name,
                "lat":           float(item["lat"]),
                "lon":           float(item["lon"]),
                "state":         addr_details.get("state", addr_details.get("county", "")),
                "country":       addr_details.get("country", ""),
                "district":      district,
            })

        ranked_nodes.sort(key=lambda x: x["score"], reverse=True)
        return [n for n in ranked_nodes if n["score"] > -20][:5]
    except Exception:
        return []


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_marine_telemetry(lat, lon):
    try:
        url = (f"https://marine-api.open-meteo.com/v1/marine"
               f"?latitude={lat}&longitude={lon}"
               f"&hourly=wave_height&daily=wave_height_max&timezone=auto")
        return requests.get(url, timeout=10).json()
    except Exception:
        return None


# ==============================================================================
# 4. SEARCH NAME BUILDER
# ==============================================================================
def build_search_name(user_input: str, district: str, state: str) -> str:
    base = user_input.strip().title()
    if len(base.split()) <= 2:
        return base
    if district and district.lower() not in base.lower():
        return f"{base} {district}"
    return base


# ==============================================================================
# 5. BAN DETECTION — WEIGHTED SCORING SYSTEM
# ==============================================================================
BAN_SCORE_WEIGHTS = {
    "swimming prohibited":            45,
    "swimming banned":                45,
    "swimming ban":                   40,
    "bans swimming":                  40,
    "ban on swimming":                40,
    "bans swimming at beaches":       50,
    "bathing prohibited":             40,
    "beach closed":                   40,
    "no swimming":                    40,
    "entry prohibited":               38,
    "entry banned":                   38,
    "entry ban":                      35,
    "water sports banned":            35,
    "water sports suspended":         35,
    "ban on water sports":            35,
    "monsoon ban":                    35,
    "sea entry banned":               35,
    "sea entry prohibited":           35,
    "strictly banned":                35,
    "completely prohibited":          35,
    "prohibited swimming":            35,
    "selfies banned":                 30,
    "sea access suspended":           30,
    "beach temporarily inaccessible": 30,
    "visitors advised not to swim":   30,
    "unsafe for swimming":            28,
    "unsafe for bathing":             28,
    "authorities advise against":     25,
    "tourist movement restricted":    25,
    "lifeguards withdrawn":           25,
    "dangerous sea conditions":       20,
    "collector order":                25,
    "prohibition order":              30,
    "district collector":             20,
    "administration order":           20,
    "municipal order":                18,
    "government order":               15,
    "red flag":                       20,
    "red alert":                      20,
    "high alert":                     15,
    "prohibited":                     20,
    "banned":                         18,
    "ban":                            15,
    "restricted":                     12,
    "suspended":                      12,
    "closed":                         12,
    "collector":                      10,
    "after drowning":                 18,
    "after drownings":                20,
    "drowning":                       10,
    "drownings":                      12,
    "monsoon":                        8,
    "swimming":                       8,
    "sea":                            5,
    "tidal warning":                  18,
    "riptide warning":                18,
    "high tide warning":              18,
    "rough sea conditions":           15,
}

BAN_SCORE_THRESHOLD = 40

HISTORICAL_NOISE_PHRASES = [
    "was closed", "had been closed", "were closed", "closed in 20",
    "previously banned", "used to be banned", "was banned", "had banned",
    "historically", "in the past",
]

DATE_PATTERN = re.compile(
    r'(\b(?:january?|february?|march|april|may|june?|july?|august|september|'
    r'october|november|december)\s+\d{1,2}'
    r'(?:\s*(?:to|through|till|–|-)\s*(?:january?|february?|march|april|may|'
    r'june?|july?|august|september|october|november|december)\s+\d{1,2})?'
    r'(?:\s*,?\s*\d{4})?'
    r'|\d{1,2}\s+(?:january?|february?|march|april|may|june?|july?|august|'
    r'september|october|november|december)\s+\d{4})',
    re.IGNORECASE
)

# Internal only — used for scraping, never shown to user
OFFICIAL_GOV_URLS = {
    "diu":         ["https://diu.gov.in", "https://diu.nic.in"],
    "daman":       ["https://daman.nic.in"],
    "goa":         ["https://goatourism.gov.in"],
    "puri":        ["https://puri.nic.in"],
    "andaman":     ["https://andaman.gov.in"],
    "lakshadweep": ["https://lakshadweep.gov.in"],
    "mumbai":      ["https://mcgm.gov.in"],
    "kerala":      ["https://tourism.kerala.gov.in"],
}

SEASONAL_BAN_HINTS = {
    "diu":    {"months": [6, 7, 8, 9], "note": "Diu historically enforces sea-entry bans Jun–Sep during monsoon."},
    "daman":  {"months": [6, 7, 8, 9], "note": "Daman enforces monsoon sea restrictions Jun–Sep."},
    "mumbai": {"months": [6, 7, 8],    "note": "Mumbai beaches often issue monsoon red-flag warnings Jun–Aug."},
    "puri":   {"months": [6, 7, 8],    "note": "Puri beach sees monsoon restrictions and drowning warnings Jun–Aug."},
}


def _scrape_page_text(url: str, max_chars: int = 1500) -> str:
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return ""
        text = re.sub(r'<[^>]+>', ' ', resp.text)
        return re.sub(r'\s+', ' ', text).strip()[:max_chars]
    except Exception:
        return ""


def _fetch_google_news_rss(search_name: str) -> list:
    results = []
    queries = [
        f"{search_name} swimming ban",
        f"{search_name} beach closed prohibited",
        f"{search_name} sea entry ban monsoon",
        f"{search_name} collector order beach",
    ]
    for q in queries:
        try:
            encoded = requests.utils.quote(q)
            rss_url = f"https://news.google.com/rss/search?q={encoded}&hl=en-IN&gl=IN&ceid=IN:en"
            resp = requests.get(rss_url, timeout=10,
                                headers={"User-Agent": "Mozilla/5.0 CoastPulseAI"})
            if resp.status_code == 200:
                titles    = re.findall(r'<title><!\[CDATA\[(.*?)\]\]></title>', resp.text)
                descs     = re.findall(r'<description><!\[CDATA\[(.*?)\]\]></description>', resp.text)
                pub_dates = re.findall(r'<pubDate>(.*?)</pubDate>', resp.text)
                for i, (t, d) in enumerate(zip(titles[1:6], descs[1:6])):
                    pub        = pub_dates[i][:16] if i < len(pub_dates) else ""
                    clean_desc = re.sub(r'<[^>]+>', '', d)[:200]
                    results.append({"text": f"{t}. {clean_desc}", "pub_date": pub})
        except Exception:
            pass
    return results


def _parse_date(s: str):
    s = s.strip().rstrip(",")
    for fmt in ["%B %d %Y", "%B %d, %Y", "%d %B %Y", "%b %d %Y",
                "%b %d, %Y", "%d %b %Y", "%B %d", "%b %d"]:
        try:
            p = datetime.strptime(s, fmt)
            if p.year == 1900:
                p = p.replace(year=datetime.now().year)
            return p.date()
        except ValueError:
            continue
    return None


def _is_ban_active(ban_dates_str: str) -> bool:
    if not ban_dates_str:
        return True
    today = date.today()
    parts = re.split(r'\bto\b|\bthrough\b|\btill\b|–|-', ban_dates_str, maxsplit=1)
    if len(parts) == 2:
        start = _parse_date(parts[0])
        end   = _parse_date(parts[1])
        if start and end:
            return start <= today <= end
        if start:
            return today >= start
    elif len(parts) == 1:
        single = _parse_date(parts[0])
        if single:
            return abs((today - single).days) <= 90
    return True


def _compute_ban_score(corpus: str) -> tuple:
    total, matched = 0, []
    for phrase, weight in BAN_SCORE_WEIGHTS.items():
        if phrase in corpus:
            total += weight
            matched.append(f"{phrase}(+{weight})")
    return total, matched


# ==============================================================================
# TOOL 1 — Government Advisory & News Search
# NOTE: sources_used is kept for internal agent logging ONLY.
#       It is NEVER passed to GPT and NEVER rendered in the UI.
# ==============================================================================
@st.cache_data(ttl=600, show_spinner=False)
def search_government_advisories(search_name: str, full_address: str) -> dict:
    agent_log    = []
    news_texts   = []
    gov_texts    = []
    # sources_used is internal/diagnostic only — not shown to user
    sources_used = []

    # ── Layer 1: Google News RSS ─────────────────────────────────────────────
    rss_items = _fetch_google_news_rss(search_name)
    for item in rss_items:
        news_texts.append(item["text"])
    if rss_items:
        sources_used.append("Google News RSS")
        agent_log.append(f"Google News RSS: {len(rss_items)} articles for '{search_name}'")
    else:
        agent_log.append(f"Google News RSS: 0 results for '{search_name}'")

    # ── Layer 2: Official government website scraping ────────────────────────
    addr_lower  = full_address.lower()
    name_lower  = search_name.lower()
    for keyword, urls in OFFICIAL_GOV_URLS.items():
        if keyword in addr_lower or keyword in name_lower:
            for gov_url in urls[:1]:
                text = _scrape_page_text(gov_url)
                if text:
                    gov_texts.append(text)
                    sources_used.append(f"Gov:{gov_url}")
                    agent_log.append(f"Gov scrape {gov_url}: {len(text)} chars")
                else:
                    agent_log.append(f"Gov scrape {gov_url}: empty/failed")

    # ── Layer 3: GNews API (optional) ────────────────────────────────────────
    gnews_key = st.secrets.get("GNEWS_API_KEY", None)
    if gnews_key:
        try:
            params = {
                "q": f"{search_name} beach swimming ban prohibited",
                "token": gnews_key, "lang": "en", "max": 5, "sortby": "publishedAt"
            }
            resp     = requests.get("https://gnews.io/api/v4/search", params=params, timeout=10)
            articles = resp.json().get("articles", [])
            for a in articles[:4]:
                text = f"{a.get('title','')} {a.get('description','')}".strip()
                if text:
                    news_texts.append(text)
                    sources_used.append("GNews")
            agent_log.append(f"GNews: {len(articles)} articles")
        except Exception as e:
            agent_log.append(f"GNews error: {str(e)[:60]}")
    else:
        agent_log.append("GNews: no key")

    # ── Weighted ban scoring ─────────────────────────────────────────────────
    primary_corpus = " ".join(news_texts + gov_texts).lower()
    ban_score, matched_tokens = _compute_ban_score(primary_corpus)
    ban_detected = ban_score >= BAN_SCORE_THRESHOLD

    agent_log.append(f"Ban score: {ban_score} / threshold {BAN_SCORE_THRESHOLD}")
    agent_log.append(f"Matched tokens: {matched_tokens[:6]}")
    agent_log.append(f"ban_detected: {ban_detected}")

    # ── Date extraction & activity check ─────────────────────────────────────
    ban_dates           = None
    is_currently_active = False

    if ban_detected:
        all_text  = " ".join(news_texts + gov_texts)
        raw_dates = DATE_PATTERN.findall(all_text)
        raw_dates = [d.strip() for d in raw_dates if d.strip() and len(d.strip()) > 3]
        if len(raw_dates) >= 2:
            ban_dates = f"{raw_dates[0]} to {raw_dates[1]}"
        elif raw_dates:
            ban_dates = raw_dates[0]

        is_currently_active = _is_ban_active(ban_dates)

        if not is_currently_active:
            ban_detected = False
            agent_log.append(f"Ban EXPIRED — dates: {ban_dates}")
        else:
            agent_log.append(f"Ban ACTIVE — dates: {ban_dates}")

    # ── Seasonal hint ─────────────────────────────────────────────────────────
    seasonal_hint = ""
    current_month = datetime.now().month
    for keyword, info in SEASONAL_BAN_HINTS.items():
        if keyword in name_lower and current_month in info["months"]:
            seasonal_hint = info["note"]
            agent_log.append(f"Seasonal hint applied: {seasonal_hint}")
            break

    return {
        "tool":                "government_advisory_search",
        "search_name":         search_name,
        "ban_detected":        ban_detected,
        "ban_dates":           ban_dates,
        "ban_score":           ban_score,
        "is_currently_active": is_currently_active,
        "matched_tokens":      matched_tokens[:8],
        # sources_used is intentionally NOT returned — stays internal
        "seasonal_hint":       seasonal_hint,
        "text_summary":        " | ".join((news_texts + gov_texts)[:5])[:800] if (news_texts or gov_texts) else "No advisories found.",
        "agent_log":           agent_log,
    }


# ==============================================================================
# TOOL 2 — General Coastal News
# ==============================================================================
@st.cache_data(ttl=900, show_spinner=False)
def fetch_coastal_news(search_name: str) -> dict:
    rss_items = _fetch_google_news_rss(search_name)
    if rss_items:
        summaries = [item["text"] for item in rss_items[:4]]
        return {"articles": summaries, "raw_text": " | ".join(summaries)}

    gnews_key = st.secrets.get("GNEWS_API_KEY", None)
    if gnews_key:
        try:
            params = {"q": f"{search_name} beach safety swimming conditions",
                      "token": gnews_key, "lang": "en", "max": 4, "sortby": "publishedAt"}
            resp     = requests.get("https://gnews.io/api/v4/search", params=params, timeout=10)
            articles = resp.json().get("articles", [])
            if articles:
                summaries = [
                    f"[{a.get('publishedAt','')[:10]}] {a.get('title','')}. {a.get('description','')}"
                    for a in articles[:3] if a.get("title")
                ]
                return {"articles": summaries, "raw_text": " | ".join(summaries)}
        except Exception:
            pass

    return {"articles": [], "raw_text": f"No recent news for {search_name}."}


# ==============================================================================
# TOOL 3 — Wave Risk Classifier
# ==============================================================================
def classify_wave_risk(wave_height: float, swimmer_grade: str) -> dict:
    if swimmer_grade == "Beginner / Casual Wader":
        if wave_height > 0.6:
            risk, advice = "HIGH", "Waves above 0.6m are hazardous for beginners. Ankle-depth wading only."
        elif wave_height > 0.3:
            risk, advice = "MODERATE", "Moderate swell. Stay close to shore with a lifeguard present."
        else:
            risk, advice = "LOW", "Calm — suitable for beginners."
    elif swimmer_grade == "Intermediate Swimmer":
        if wave_height > 1.2:
            risk, advice = "HIGH", "Strong swell for intermediate swimmers. Avoid open water."
        elif wave_height > 0.7:
            risk, advice = "MODERATE", "Choppy conditions. Watch for rip currents."
        else:
            risk, advice = "LOW", "Good conditions for intermediate swimmers."
    else:
        if wave_height > 2.5:
            risk, advice = "HIGH", "Extreme swell. Experienced surfers with safety gear only."
        elif wave_height > 1.5:
            risk, advice = "MODERATE", "Solid surfing swell. Standard safety protocols apply."
        else:
            risk, advice = "LOW", "Light swell — suitable for advanced swimmers."

    return {"tool": "wave_risk_classifier", "wave_height_m": wave_height,
            "swimmer_grade": swimmer_grade, "risk_level": risk, "swimming_advice": advice}


# ==============================================================================
# ORCHESTRATED AGENT PIPELINE
# ==============================================================================
def run_coastal_safety_agent(
    display_title: str,
    full_address:  str,
    user_input:    str,
    district:      str,
    state:         str,
    wave_height:   float,
    swimmer_grade: str,
) -> dict:

    search_name = build_search_name(user_input, district, state)

    agent_trace = [{"step": "INIT", "search_name": search_name,
                    "display_title": display_title, "wave_height": wave_height}]

    gov_result  = search_government_advisories(search_name, full_address)
    agent_trace.append({"step": "TOOL_1_DONE", "ban_detected": gov_result["ban_detected"],
                        "ban_score": gov_result["ban_score"]})

    news_result = fetch_coastal_news(search_name)
    agent_trace.append({"step": "TOOL_2_DONE"})

    wave_result = classify_wave_risk(wave_height, swimmer_grade)
    agent_trace.append({"step": "TOOL_3_DONE", "risk_level": wave_result["risk_level"]})

    # ── Build GPT context ─────────────────────────────────────────────────────
    gov_ctx = json.dumps({
        "ban_detected":        gov_result["ban_detected"],
        "ban_score":           gov_result["ban_score"],
        "ban_score_threshold": BAN_SCORE_THRESHOLD,
        "ban_dates":           gov_result["ban_dates"],
        "is_currently_active": gov_result["is_currently_active"],
        "matched_tokens":      gov_result["matched_tokens"],
        "seasonal_hint":       gov_result["seasonal_hint"],
        "text_summary":        gov_result["text_summary"][:600],
    }, indent=2)

    news_ctx = json.dumps({
        "articles": news_result["articles"][:3],
    }, indent=2)

    wave_ctx = json.dumps(wave_result, indent=2)

    # ── GPT-4o synthesis ──────────────────────────────────────────────────────
    try:
        client = AzureOpenAI(
            api_key=st.secrets["AZURE_OPENAI_API_KEY"],
            api_version="2024-08-01-preview",
            azure_endpoint=st.secrets["AZURE_OPENAI_ENDPOINT"]
        )
        deployment = st.secrets.get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")

        system_prompt = """You are CoastPulse AI — a coastal safety intelligence agent.

You receive structured data from three tools: government advisory search, news, and wave analysis.
Your job is to synthesise this into a clear, human-friendly safety verdict for a beach visitor.

═══ DECISION LOGIC (apply strictly in this order) ═══

1. If gov_advisory.ban_detected = true AND is_currently_active = true
   → status = "CLOSED BY AUTHORITY", bg_type = "danger"

2. If ban_detected = false BUT seasonal_hint is non-empty AND wave risk is HIGH or MODERATE
   → status = "CAUTION", bg_type = "caution"

3. If wave_risk.risk_level = "HIGH"
   → status = "CAUTION", bg_type = "caution"

4. If wave_risk.risk_level = "MODERATE"
   → status = "CAUTION", bg_type = "caution"

5. If wave_risk.risk_level = "LOW"
   → status = "SAFE", bg_type = "safe"

═══ DESCRIPTION RULES ═══

Write exactly 3–4 plain sentences in warm, natural human language. No markdown. No HTML. No bullet points. No URLs. No website names. No source citations.

Sentence 1: State the overall safety verdict clearly (e.g. "Swimming at [location] is currently banned by local authorities.")
Sentence 2: Give the wave height and what it means for the user's experience level.
Sentence 3: If a ban is active — state it plainly and include the ban period if known (e.g. "The administration has restricted all sea entry from 1st June to 30th September."). If no ban — give practical advice based on conditions.
Sentence 4 (optional): Add any seasonal pattern note or extra safety tip.

IMPORTANT — things to NEVER include in description:
- Any URL, website address, or domain name
- Any source name like "Google News", "GNews", "gov.in", "nic.in"
- Any technical field names like "ban_score", "matched_tokens"
- Phrases like "according to our data" or "based on sources"

═══ OUTPUT FORMAT ═══

Return ONLY raw valid JSON — no markdown fences, no extra text:
{
  "status": "SAFE" | "CAUTION" | "CLOSED BY AUTHORITY",
  "bg_type": "safe" | "caution" | "danger",
  "description": "plain 3–4 sentence human advisory",
  "ban_detected": true | false,
  "ban_dates": "e.g. 1st June to 30th September" or null
}"""

        user_msg = f"""Location: {display_title} ({full_address})
Search term used: "{search_name}"
Wave height: {wave_height}m | Swimmer experience: {swimmer_grade}
Today's date: {datetime.now().strftime("%d %B %Y")}

=== TOOL 1 — Government Advisory & Ban Detection ===
{gov_ctx}

=== TOOL 2 — Coastal News Headlines ===
{news_ctx}

=== TOOL 3 — Wave Risk Analysis ===
{wave_ctx}

Apply the decision logic and return the JSON advisory. Write the description as you would explain this to a friend planning a beach trip — warm, clear, and helpful."""

        response = client.chat.completions.create(
            model=deployment,
            messages=[{"role": "system", "content": system_prompt},
                      {"role": "user",   "content": user_msg}],
            max_tokens=500,
            temperature=0.1
        )

        raw = response.choices[0].message.content.strip()
        agent_trace.append({"step": "GPT_OUTPUT", "preview": raw[:300]})

        if raw.startswith("```json"):
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif raw.startswith("```"):
            raw = raw.split("```")[1].split("```")[0].strip()

        parsed = json.loads(raw)
        parsed["_agent_trace"] = agent_trace
        parsed["_gov_log"]     = gov_result["agent_log"]
        return parsed

    except Exception as e:
        agent_trace.append({"step": "GPT_ERROR", "error": str(e)})

    # ── Fallback (no GPT) ─────────────────────────────────────────────────────
    ban  = gov_result["ban_detected"]
    risk = wave_result["risk_level"]
    hint = gov_result.get("seasonal_hint", "")

    if ban:
        status, bg_type = "CLOSED BY AUTHORITY", "danger"
        period = f" The restriction is in effect from {gov_result['ban_dates']}." if gov_result["ban_dates"] else ""
        desc = (f"Swimming at {display_title} is currently banned by the local administration."
                f"{period} All sea entry is strictly prohibited until further notice."
                f" Please do not enter the water regardless of conditions.")
    elif risk == "HIGH":
        status, bg_type = "CAUTION", "caution"
        desc = (f"Conditions at {display_title} are currently risky, with wave heights of {wave_height}m."
                f" {wave_result['swimming_advice']}"
                + (f" {hint}" if hint else ""))
    elif risk == "MODERATE":
        status, bg_type = "CAUTION", "caution"
        desc = (f"Moderate wave conditions of {wave_height}m have been recorded at {display_title}."
                f" {wave_result['swimming_advice']}"
                + (f" {hint}" if hint else ""))
    else:
        status, bg_type = "SAFE", "safe"
        desc = (f"Conditions at {display_title} look good right now, with calm waves of {wave_height}m."
                f" {wave_result['swimming_advice']}"
                + (f" {hint}" if hint else ""))

    return {
        "status": status, "bg_type": bg_type, "description": desc,
        "ban_detected": ban, "ban_dates": gov_result.get("ban_dates"),
        "_agent_trace": agent_trace, "_gov_log": gov_result.get("agent_log", []),
    }


# ==============================================================================
# 6. RUNTIME PIPELINE CONTROLLER
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
                title   = candidate["display_title"]
                state_c = candidate["state"]
                country = candidate["country"]
                btn_lbl = f"📍 {title}"
                if state_c:  btn_lbl += f", {state_c}"
                if country:  btn_lbl += f" ({country})"
                if st.button(btn_lbl, key=f"node_btn_{index}", use_container_width=True):
                    st.session_state.selected_spot_data = candidate
                    st.rerun()
        else:
            st.markdown("""
                <div style="background-color:#ffeeef;border:1px solid #fca5a5;padding:15px;
                border-radius:8px;text-align:center;color:#b91c1c;font-size:13.5px;
                font-weight:500;margin-top:20px;">
                    No matching locations found. Please check your spelling.
                </div>""", unsafe_allow_html=True)

    if st.session_state.selected_spot_data is not None:
        node = st.session_state.selected_spot_data
        lat, lon = node["lat"], node["lon"]

        marine_payload      = fetch_marine_telemetry(lat, lon)
        current_wave_height = 0.0
        daily_max_forecasts = []
        forecast_dates      = []

        if marine_payload:
            if "hourly" in marine_payload and "wave_height" in marine_payload["hourly"]:
                ts   = marine_payload["hourly"]["time"]
                hs   = [h if h is not None else 0.0 for h in marine_payload["hourly"]["wave_height"]]
                now  = datetime.now()
                idx  = min(range(len(ts)), key=lambda i: abs(
                    datetime.fromisoformat(ts[i].replace("Z", "")) - now))
                current_wave_height = hs[idx]
            if "daily" in marine_payload and "wave_height_max" in marine_payload["daily"]:
                daily_max_forecasts = [w if w is not None else 0.0
                                       for w in marine_payload["daily"]["wave_height_max"]]
                forecast_dates = marine_payload["daily"].get("time", [])

        with st.spinner("🤖 Agent gathering live advisories and wave data..."):
            output = run_coastal_safety_agent(
                display_title = node["display_title"],
                full_address  = node["full_address"],
                user_input    = user_input,
                district      = node.get("district", ""),
                state         = node.get("state", ""),
                wave_height   = current_wave_height,
                swimmer_grade = skill_level,
            )

        status    = output.get("status", "SAFE")
        bg_type   = output.get("bg_type", "safe")
        ai_desc   = output.get("description", "")
        has_ban   = output.get("ban_detected", False)
        ban_dates = output.get("ban_dates") or None

        # Strip any accidental markup from description
        for junk in ["```html", "```json", "```", "<div>", "</div>", "<p>", "</p>", "<span>", "</span>"]:
            ai_desc = ai_desc.replace(junk, "")
        ai_desc = ai_desc.strip()

        # ── Determine display status & pill ──────────────────────────────────
        if has_ban or status == "CLOSED BY AUTHORITY":
            display_status, pill_class = "CLOSED BY AUTHORITY", "badge-capsule-danger"
        elif bg_type == "caution" or status == "CAUTION":
            display_status, pill_class = "CAUTION", "badge-capsule-caution"
        else:
            display_status, pill_class = "SAFE", "badge-capsule-safe"

        # ── Background image per risk level ──────────────────────────────────
        bg_img = {
            "danger":  "https://images.unsplash.com/photo-1505118380757-91f5f5632de0?auto=format&fit=crop&w=1200&q=80",
            "caution": "https://images.unsplash.com/photo-1519046904884-53103b34b206?auto=format&fit=crop&w=1200&q=80",
        }.get(bg_type, "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80")

        # ── Ban alert block (shown only when a ban is active) ─────────────────
        ban_alert_html = ""
        if has_ban:
            ban_period_text = (
                f"Restriction period: <strong>{ban_dates}</strong>"
                if ban_dates else
                "Duration not specified — treat as ongoing until official notice is lifted."
            )
            ban_alert_html = (
                '<div style="background:rgba(239,68,68,0.15);border:1px solid rgba(239,68,68,0.3);'
                'border-radius:10px;padding:14px 16px;margin:16px 0;">'
                '<strong style="color:#fca5a5;font-size:13px;text-transform:uppercase;">'
                '🛑 OFFICIAL ENTRY BAN ENFORCED</strong>'
                f'<p style="margin:6px 0 0 0;font-size:13px;color:#fee2e2;font-weight:500;">'
                f'District administration has closed all water entry. {ban_period_text}</p>'
                '</div>'
            )

        # ── Main advisory card ────────────────────────────────────────────────
        # NOTE: no URL, no source label, no news_src_html anywhere in this card
        card_style = (
            'border-radius:24px;padding:40px;box-shadow:0 20px 40px rgba(15,23,42,0.16);'
            'border:1px solid rgba(255,255,255,0.1);margin-top:25px;color:#ffffff;'
            f'background-image:linear-gradient(rgba(10,20,40,0.62),rgba(10,20,40,0.72)),url({bg_img});'
            'background-size:cover;background-position:center;'
        )
        st.markdown(
            f'<div style="{card_style}">'
            f'<span class="{pill_class}">{display_status}</span>'
            f'<h3 class="advisory-header-title">Safety Report: {node["display_title"]}</h3>'
            f'{ban_alert_html}'
            f'<p class="advisory-prose-body">{ai_desc}</p>'
            f'<div class="brand-stamp-footer">✨ Powered by CoastPulse AI · Azure AI Foundry</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        # _agent_trace and _gov_log remain in output dict for backend inspection only
        # They are never rendered in the UI

        # ── 7-Day Trip Planner ────────────────────────────────────────────────
        if daily_max_forecasts:
            st.markdown(
                "<br><h4 style='font-size:16px;font-weight:700;color:#0f172a;margin-bottom:15px;'>"
                "📅 Your 7-Day Trip Planner Matrix</h4>",
                unsafe_allow_html=True
            )
            cols = st.columns(7)
            for i in range(min(7, len(daily_max_forecasts))):
                p_date = datetime.strptime(forecast_dates[i], "%Y-%m-%d")
                max_w  = daily_max_forecasts[i]
                if has_ban:
                    lbl, bg, txt = "🚫 CLOSED", "#fff1f2", "#b91c1c"
                elif max_w > 1.6:
                    lbl, bg, txt = "🚫 RISK",   "#fff1f2", "#b91c1c"
                elif max_w > 1.1 or status == "CAUTION":
                    lbl, bg, txt = "🟡 CAUTION", "#fef9c3", "#a16207"
                else:
                    lbl, bg, txt = "🟢 PERFECT", "#f0fdf4", "#15803d"
                with cols[i]:
                    st.markdown(f"""
                    <div class="planner-grid-card" style="background:{bg};border:1px solid rgba(0,0,0,0.04);">
                        <strong style="font-size:13px;color:#1d4ed8;">{p_date.strftime("%a")}</strong><br>
                        <span style="font-size:10px;color:#64748b;">{p_date.strftime("%b %d")}</span>
                        <p style="margin:8px 0;font-size:11px;font-weight:800;color:{txt};">{lbl}</p>
                        <span style="font-size:10px;color:#475569;"><strong>{max_w:.2f}m</strong></span>
                    </div>""", unsafe_allow_html=True)