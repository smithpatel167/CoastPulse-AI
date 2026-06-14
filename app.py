import streamlit as st
import requests
import json
import streamlit_lottie as st_lottie
from openai import AzureOpenAI
from datetime import datetime
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
    .brand-tagline      { font-size: 15px; color: #334155; font-weight: 600;
                          margin-top: 5px; margin-bottom: 25px; }

    .field-label  { font-size: 13px; font-weight: 700; color: #0f172a; margin-bottom: 6px; }
    .clean-search-text { font-size: 14.5px; font-weight: 700; color: #1d4ed8;
                         margin-top: 25px; margin-bottom: 12px; }

    /* status pills */
    .badge-ban     { background-color: #7c3aed; color: white; padding: 6px 14px;
                     border-radius: 6px; font-weight: 800; font-size: 11px;
                     text-transform: uppercase; letter-spacing: 0.06em;
                     display: inline-block; margin-bottom: 15px; }
    .badge-caution { background-color: #f59e0b; color: white; padding: 6px 14px;
                     border-radius: 6px; font-weight: 800; font-size: 11px;
                     text-transform: uppercase; letter-spacing: 0.06em;
                     display: inline-block; margin-bottom: 15px; }
    .badge-safe    { background-color: #10b981; color: white; padding: 6px 14px;
                     border-radius: 6px; font-weight: 800; font-size: 11px;
                     text-transform: uppercase; letter-spacing: 0.06em;
                     display: inline-block; margin-bottom: 15px; }

    .advisory-header-title { color: #ffffff !important; font-weight: 800; font-size: 24px;
                              margin: 0 0 15px 0 !important; letter-spacing: -0.01em; }
    .advisory-prose-body   { font-size: 15.5px; line-height: 1.72; color: #f1f5f9 !important;
                              font-weight: 400; margin-top: 15px; }
    .ban-box       { background: rgba(124,58,237,0.18);
                     border: 1px solid rgba(167,139,250,0.4);
                     border-radius: 10px; padding: 14px 16px; margin: 16px 0; }
    .ban-box-title { color: #ddd6fe; font-size: 13px; font-weight: 800;
                     text-transform: uppercase; }
    .ban-box-body  { margin: 6px 0 0 0; font-size: 13.5px; color: #ede9fe;
                     font-weight: 500; line-height: 1.65; }
    .brand-stamp-footer { text-align: right; font-size: 11px;
                          color: rgba(241,245,249,0.45) !important;
                          font-weight: 600; margin-top: 30px; letter-spacing: 0.03em; }
    .planner-grid-card  { background: #ffffff; padding: 14px; border-radius: 12px;
                          border: 1px solid #e2e8f0; text-align: center;
                          box-shadow: 0 1px 3px rgba(0,0,0,0.01); }
    .agent-step    { font-size: 12px; color: #64748b; padding: 3px 0; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="brand-header-box">
    <h1 class="brand-title">🌊 CoastPulse AI</h1>
    <p class="brand-tagline">Real-Time Safety Insights and Risk Metrics for Coastal Trips.</p>
</div>
""", unsafe_allow_html=True)

animation_filename = "beach_animation.json"

if os.path.exists(animation_filename):
    with open(animation_filename, "r", encoding="utf-8") as f:
        local_lottie_json = json.load(f)
    st_lottie.st_lottie(local_lottie_json, height=160, key="coastpulse_lottie", speed=0.85)

# ==============================================================================
# 2. COUNTRIES
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

st.markdown("<hr style='border-color:#e2e8f0;margin-bottom:20px;'>", unsafe_allow_html=True)
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
        placeholder="e.g., goa, diu, phuket, miami, bali",
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
# ==============================================================================
@st.cache_data(ttl=3600, show_spinner=False)
def geocode_region(query_text: str, country_iso: str) -> dict | None:
    headers = {"User-Agent": "CoastPulseAI/5.0 (contact@coastpulse.ai)"}
    params = {"q": query_text, "format": "jsonv2", "addressdetails": 1, "limit": 5}
    if country_iso:
        params["countrycodes"] = country_iso.lower()
    SKIP_TYPES = {"beach", "coastline", "bay"}
    SKIP_AMENITY = {"cafe", "restaurant", "bar", "hotel", "hostel",
                    "resort", "hospital", "school", "college"}
    try:
        resp = requests.get("https://nominatim.openstreetmap.org/search",
                            params=params, headers=headers, timeout=12)
        results = resp.json()
        if not results:
            return None
        for r in results:
            if r.get("type") in SKIP_TYPES:
                continue
            if r.get("address", {}).get("amenity", "").lower() in SKIP_AMENITY:
                continue
            bb = r.get("boundingbox", [])
            addr = r.get("address", {})
            return {
                "lat": float(r["lat"]), "lon": float(r["lon"]),
                "display_name": r.get("display_name", ""),
                "state": addr.get("state", addr.get("county", "")),
                "country": addr.get("country", ""),
                "boundingbox": bb,
            }
        return None
    except Exception:
        return None


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_beaches_overpass(south: float, north: float,
                           west: float, east: float) -> list[dict]:
    query = f"""
[out:json][timeout:30];
(
  node["natural"="beach"]({south},{west},{north},{east});
  way["natural"="beach"]({south},{west},{north},{east});
  relation["natural"="beach"]({south},{west},{north},{east});
);
out center tags;
"""
    try:
        resp = requests.post("https://overpass-api.de/api/interpreter",
                             data={"data": query}, timeout=35,
                             headers={"User-Agent": "CoastPulseAI/5.0"})
        elements = resp.json().get("elements", [])
        beaches, seen = [], set()
        for el in elements:
            tags = el.get("tags", {})
            name = tags.get("name") or tags.get("name:en") or ""
            if not name or name.lower() in seen:
                continue
            seen.add(name.lower())
            if el.get("type") == "node":
                lat, lon = el["lat"], el["lon"]
            else:
                c = el.get("center", {})
                lat, lon = c.get("lat", 0.0), c.get("lon", 0.0)
            if lat == 0.0 and lon == 0.0:
                continue
            beaches.append({
                "display_title": name,
                "lat": lat, "lon": lon,
                "full_address": name,
                "state": tags.get("addr:state", ""),
                "country": tags.get("addr:country", ""),
            })
        beaches.sort(key=lambda b: b["display_title"])
        return beaches
    except Exception:
        return []


@st.cache_data(ttl=3600, show_spinner=False)
def nominatim_beach_fallback(query_text: str, country_iso: str) -> list[dict]:
    headers = {"User-Agent": "CoastPulseAI/5.0 (contact@coastpulse.ai)"}
    params = {"q": f"{query_text} beach", "format": "jsonv2",
              "addressdetails": 1, "limit": 50}
    if country_iso:
        params["countrycodes"] = country_iso.lower()
    ALLOW_TYPES = {"beach", "coastline", "bay", "cove"}
    ALLOW_CLASSES = {"natural", "water"}
    HARD_EXCL_CLS = {"amenity", "shop", "office", "building",
                     "highway", "railway", "aeroway"}
    try:
        resp = requests.get("https://nominatim.openstreetmap.org/search",
                            params=params, headers=headers, timeout=12)
        results = resp.json()
        beaches, seen = [], set()
        for item in results:
            et = item.get("type", "").lower()
            ec = item.get("class", "").lower()
            if ec in HARD_EXCL_CLS:
                continue
            if et not in ALLOW_TYPES and ec not in ALLOW_CLASSES:
                first = item.get("display_name", "").split(",")[0].lower()
                if "beach" not in first and "coast" not in first:
                    continue
            dn = item.get("display_name", "")
            key = dn.split(",")[0].strip().lower()
            if key in seen:
                continue
            seen.add(key)
            addr = item.get("address", {})
            beaches.append({
                "display_title": dn.split(",")[0].strip(),
                "lat": float(item["lat"]), "lon": float(item["lon"]),
                "full_address": dn,
                "state": addr.get("state", addr.get("county", "")),
                "country": addr.get("country", ""),
            })
        beaches.sort(key=lambda b: b["display_title"])
        return beaches
    except Exception:
        return []


def resolve_beaches_for_region(query_text: str,
                               country_iso: str) -> tuple[list[dict], str]:
    region = geocode_region(query_text, country_iso)
    region_name = query_text.strip().title()

    if region:
        region_name = region["display_name"].split(",")[0].strip()
        bb = region.get("boundingbox", [])
        if len(bb) == 4:
            try:
                s, n, w, e = (float(bb[0]), float(bb[1]),
                              float(bb[2]), float(bb[3]))
                if (n - s) < 0.3:
                    pad = (0.3 - (n - s)) / 2
                    s -= pad;
                    n += pad
                if (e - w) < 0.3:
                    pad = (0.3 - (e - w)) / 2
                    w -= pad;
                    e += pad
                beaches = fetch_beaches_overpass(s, n, w, e)
                if beaches:
                    for b in beaches:
                        if not b["state"]:
                            b["state"] = region.get("state", "")
                        if not b["country"]:
                            b["country"] = region.get("country", "")
                    return beaches, region_name
            except (ValueError, TypeError):
                pass

    return nominatim_beach_fallback(query_text, country_iso), region_name


# ==============================================================================
# 4. MARINE TELEMETRY
# ==============================================================================
@st.cache_data(ttl=1800, show_spinner=False)
def fetch_marine_telemetry(lat: float, lon: float) -> dict | None:
    try:
        url = (f"https://marine-api.open-meteo.com/v1/marine"
               f"?latitude={lat}&longitude={lon}"
               f"&hourly=wave_height&daily=wave_height_max&timezone=auto")
        return requests.get(url, timeout=10).json()
    except Exception:
        return None


# ==============================================================================
# 5. WAVE RISK CLASSIFIER
# ==============================================================================
def classify_wave_risk(wave_height: float, swimmer_grade: str) -> dict:
    if swimmer_grade == "Beginner / Casual Wader":
        if wave_height > 0.6:
            risk, adv = "HIGH", f"{wave_height:.2f}m waves — hazardous, ankle-depth wading only."
        elif wave_height > 0.3:
            risk, adv = "MODERATE", f"{wave_height:.2f}m waves — stay close to shore with lifeguard."
        else:
            risk, adv = "LOW", f"{wave_height:.2f}m waves — calm, suitable for beginners."
    elif swimmer_grade == "Intermediate Swimmer":
        if wave_height > 1.2:
            risk, adv = "HIGH", f"{wave_height:.2f}m — too strong, avoid open water."
        elif wave_height > 0.7:
            risk, adv = "MODERATE", f"{wave_height:.2f}m — choppy, watch for rip currents."
        else:
            risk, adv = "LOW", f"{wave_height:.2f}m — good conditions."
    else:
        if wave_height > 2.5:
            risk, adv = "HIGH", f"{wave_height:.2f}m — extreme swell, full safety gear required."
        elif wave_height > 1.5:
            risk, adv = "MODERATE", f"{wave_height:.2f}m — solid surf, standard protocols apply."
        else:
            risk, adv = "LOW", f"{wave_height:.2f}m — good for advanced swimmers."
    return {"risk_level": risk, "wave_height_m": wave_height,
            "swimmer_grade": swimmer_grade, "advice": adv}


# ==============================================================================
# 6. SEARCH AGENT  (Agent 1)
#
# PROVIDER PRIORITY ORDER:
#   1. Serper API   (SERPER_API_KEY)    — PRIMARY, 2500 free credits/month
#                                         https://serper.dev
#   2. SerpAPI      (SERPAPI_KEY)       — FALLBACK only if Serper not configured
#                                         Use sparingly — 130 searches left!
#   3. RSS                              — Always runs as free baseline
#
# QUERY COUNT REDUCED: 3 queries per provider (was 5) to save credits.
# Serper uses just 1 credit per search — much more economical than SerpAPI.
# ==============================================================================

BAN_TERMS = [
    "banned", "ban", "prohibited", "prohibition", "closed", "closure",
    "restriction", "restricted", "suspended", "suspension", "not allowed",
    "entry barred", "no entry", "no swimming", "barred", "forbidden",
    "collector order", "administration order", "district order",
    "municipal order", "government order", "authority order",
]

# ── 3 focused queries instead of 5 — covers all ban signals with fewer credits ──
SEARCH_QUERIES_TEMPLATE = [
    "{region} beach swimming ban prohibited closed",
    "{region} sea entry banned monsoon restriction order",
    "{region} beach safety warning drowning water sports suspended",
]


@st.cache_data(ttl=480, show_spinner=False)
def agent1_search(region_name: str) -> dict:
    """
    Agent 1 — Search Agent.
    Priority: Serper (primary) → SerpAPI (fallback) → RSS (always).
    Reduced to 3 queries per provider to conserve credits.
    """
    serper_key = st.secrets.get("SERPER_API_KEY", "")
    serpapi_key = st.secrets.get("SERPAPI_KEY", "")

    all_raw = []
    providers_used = []

    # ── 1. Serper API (PRIMARY — use this first, cheapest) ───────────────────
    if serper_key:
        serper_raw = _raw_serper(region_name, serper_key)
        all_raw.extend(serper_raw)
        providers_used.append(f"Serper ({len(serper_raw)} results)")

    # ── 2. SerpAPI (FALLBACK — only if Serper not configured) ────────────────
    elif serpapi_key:
        serp_raw = _raw_serpapi(region_name, serpapi_key)
        all_raw.extend(serp_raw)
        providers_used.append(f"SerpAPI ({len(serp_raw)} results)")

    # ── 3. RSS baseline (always runs — free) ─────────────────────────────────
    rss_raw = _raw_rss(region_name)
    all_raw.extend(rss_raw)
    providers_used.append(f"RSS ({len(rss_raw)} results)")

    result = _build_search_results(all_raw)
    result["providers_used"] = providers_used
    return result


def _raw_serper(region_name: str, api_key: str) -> list[dict]:
    """
    Serper.dev Google Search API — PRIMARY provider.
    Cost: 1 credit per search. Free plan: 2,500 credits/month.
    Sign up: https://serper.dev  →  API keys  →  copy key
    secrets.toml:  SERPER_API_KEY = "your-key-here"

    Runs 3 queries × up to 10 results = up to 30 raw results per beach check.
    """
    queries = [q.format(region=region_name) for q in SEARCH_QUERIES_TEMPLATE]
    raw = []
    for q in queries:
        try:
            resp = requests.post(
                "https://google.serper.dev/search",
                headers={
                    "X-API-KEY": api_key,
                    "Content-Type": "application/json",
                },
                json={
                    "q": q,
                    "num": 10,
                    "hl": "en",
                    "gl": "in",
                    "tbs": "qdr:m",  # last month results
                },
                timeout=12,
            )
            if resp.status_code != 200:
                continue
            data = resp.json()
            for r in data.get("organic", []):
                raw.append({
                    "title": r.get("title", ""),
                    "snippet": r.get("snippet", ""),
                    "url": r.get("link", ""),
                })
            # Also grab news results if present (often have ban announcements)
            for r in data.get("news", []):
                raw.append({
                    "title": r.get("title", ""),
                    "snippet": r.get("snippet", ""),
                    "url": r.get("link", ""),
                })
        except Exception:
            continue
    return raw


def _raw_serpapi(region_name: str, api_key: str) -> list[dict]:
    """
    SerpAPI — FALLBACK only (130 searches left, use sparingly!).
    Runs only 3 queries when Serper is not configured.
    secrets.toml:  SERPAPI_KEY = "your-key-here"
    """
    queries = [q.format(region=region_name) for q in SEARCH_QUERIES_TEMPLATE]
    raw = []
    for q in queries:
        try:
            resp = requests.get(
                "https://serpapi.com/search",
                params={
                    "q": q,
                    "api_key": api_key,
                    "engine": "google",
                    "num": 10,
                    "hl": "en",
                    "gl": "in",
                    "tbs": "qdr:m",
                },
                timeout=12,
            )
            if resp.status_code != 200:
                continue
            for r in resp.json().get("organic_results", []):
                raw.append({
                    "title": r.get("title", ""),
                    "snippet": r.get("snippet", ""),
                    "url": r.get("link", ""),
                })
        except Exception:
            continue
    return raw


def _raw_rss(region_name: str) -> list[dict]:
    """
    Google News RSS — free, no key, always available.
    Runs 3 queries as free baseline.
    """
    queries = [q.format(region=region_name) for q in SEARCH_QUERIES_TEMPLATE]
    seen, raw = set(), []
    for q in queries:
        try:
            encoded = requests.utils.quote(q)
            url = f"https://news.google.com/rss/search?q={encoded}&hl=en&gl=IN&ceid=IN:en"
            resp = requests.get(url, timeout=10,
                                headers={"User-Agent": "Mozilla/5.0 CoastPulseAI/6.0"})
            if resp.status_code != 200:
                continue
            titles = re.findall(r'<title><!\[CDATA\[(.*?)\]\]></title>', resp.text)
            descs = re.findall(r'<description><!\[CDATA\[(.*?)\]\]></description>', resp.text)
            for i, title in enumerate(titles[1:8]):
                t = title.strip()
                if t in seen:
                    continue
                seen.add(t)
                desc_raw = descs[i] if i < len(descs) else ""
                desc = re.sub(r'<[^>]+>', ' ', desc_raw)
                desc = re.sub(r'\s+', ' ', desc).strip()[:300]
                raw.append({"title": t, "snippet": desc, "url": ""})
        except Exception:
            continue
    return raw


def _build_search_results(raw_items: list[dict]) -> dict:
    """Shared scorer/packager used by all search providers."""
    seen, all_results = set(), []
    for item in raw_items:
        title = item.get("title", "").strip()
        snippet = item.get("snippet", "").strip()
        url = item.get("url", "")
        key = title.lower()[:80]
        if not title or key in seen:
            continue
        seen.add(key)
        combined = (title + " " + snippet).lower()
        ban_score = sum(1 for t in BAN_TERMS if t in combined)
        all_results.append({"title": title, "snippet": snippet,
                            "url": url, "ban_score": ban_score})

    all_results.sort(key=lambda r: r["ban_score"], reverse=True)
    ban_hits = [r for r in all_results if r["ban_score"] >= 1]
    return {"results": all_results[:30], "ban_hits": ban_hits[:10],
            "total_found": len(all_results), "queries_used": []}


def _rss_fallback(region_name: str) -> dict:
    """Packaged RSS-only fallback."""
    raw = _raw_rss(region_name)
    result = _build_search_results(raw)
    result["providers_used"] = [f"RSS only ({len(raw)} results)"]
    return result


# ==============================================================================
# 7. VERIFICATION + ADVISORY AGENT  (Agent 2)
# ==============================================================================
def agent2_verify_and_advise(
        display_title: str,
        region_name: str,
        search_data: dict,
        wave_result: dict,
        swimmer_grade: str,
) -> dict:
    today_str = datetime.now().strftime("%d %B %Y")

    ban_hits = search_data.get("ban_hits", [])
    general = [r for r in search_data.get("results", []) if r not in ban_hits]

    evidence_lines = []
    if ban_hits:
        evidence_lines.append("=== HIGH-RELEVANCE RESULTS (ban/restriction language detected) ===")
        for r in ban_hits[:8]:
            evidence_lines.append(f"TITLE:   {r['title']}")
            evidence_lines.append(f"SNIPPET: {r['snippet']}")
            evidence_lines.append("")
    if general[:6]:
        evidence_lines.append("=== GENERAL SAFETY RESULTS ===")
        for r in general[:6]:
            evidence_lines.append(f"TITLE:   {r['title']}")
            evidence_lines.append(f"SNIPPET: {r['snippet']}")
            evidence_lines.append("")

    evidence_text = "\n".join(evidence_lines) if evidence_lines else \
        "No search results available for this region."

    client = AzureOpenAI(
        api_key=st.secrets["AZURE_OPENAI_API_KEY"],
        api_version="2024-08-01-preview",
        azure_endpoint=st.secrets["AZURE_OPENAI_ENDPOINT"],
    )
    deployment = st.secrets.get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")

    system_prompt = f"""You are CoastPulse AI — a coastal safety verification and advisory agent.

TODAY'S DATE: {today_str}
This date is authoritative. All date reasoning must use this exact date.

You receive:
1. Web search results (title + snippet) about beach safety for a region
2. Live wave data for the specific selected beach
3. The visitor's swimming experience level

════════════════════════════════════════════
PHASE 1 — VERIFY BAN FROM SEARCH EVIDENCE
════════════════════════════════════════════

Read every title and snippet carefully. Snippets contain actual article text —
they often include exact restriction language, dates, authority names.

Look for evidence of:
• Official orders banning swimming, sea entry, water sports, beach access
• District Collector, Municipal Corporation, Administration, Government orders
• Monsoon restrictions, seasonal bans, post-drowning closures
• Any official entity restricting public beach access

For each ban signal, extract:
• ban_scope:  what exactly is banned (e.g. "swimming and water sports", "all sea entry")
• ban_dates:  start and end dates as written in the snippet
• ban_by:     issuing authority name
• ban_reason: stated reason (monsoon, drowning, rough seas, safety review)

════════════════════════════════════════════
PHASE 2 — DATE REASONING (CRITICAL)
════════════════════════════════════════════

Today is {today_str}. This is fixed and authoritative.

After finding a ban, check its dates:

CASE A — No end date mentioned:
→ Treat ban as CURRENTLY ACTIVE
→ ban_detected = true, ban_expired = false

CASE B — End date is IN THE FUTURE (after {today_str}):
→ Ban is CURRENTLY ACTIVE
→ ban_detected = true, ban_expired = false

CASE C — End date has ALREADY PASSED (before {today_str}):
→ Ban has EXPIRED — do NOT set ban status
→ ban_detected = false, ban_expired = true
→ Fall through to wave risk assessment
→ Optionally mention the expired ban in description

CASE D — No ban evidence found:
→ ban_detected = false, ban_expired = false
→ Assess safety purely from wave risk

════════════════════════════════════════════
PHASE 3 — DETERMINE STATUS
════════════════════════════════════════════

Priority order:
1. ban_detected = true AND ban_expired = false → status = "BAN BY AUTHORITY"
2. wave risk = HIGH  → status = "CAUTION"
3. wave risk = MODERATE → status = "CAUTION"
4. wave risk = LOW → status = "SAFE"

════════════════════════════════════════════
PHASE 4 — WRITE DESCRIPTION
════════════════════════════════════════════

Write 3–5 warm, clear sentences as a knowledgeable friend would explain to
someone planning a beach trip. Use simple English, no jargon.

STRICT RULES — NEVER include in description:
• URLs or domain names of any kind
• Source names: "Bing", "Google", "search results", "RSS", "website", "Serper"
• Technical terms: "ban_score", "snippet", "API", "agent"
• Phrases like "according to our data" or "based on search results"

════════════════════════════════════════════
OUTPUT — raw JSON only, no markdown fences:
════════════════════════════════════════════
{{
  "status":       "BAN BY AUTHORITY" | "CAUTION" | "SAFE",
  "bg_type":      "ban" | "caution" | "safe",
  "ban_detected": true | false,
  "ban_expired":  true | false,
  "ban_scope":    "what is banned" | null,
  "ban_dates":    "e.g. 1 June to 30 July 2025" | null,
  "ban_by":       "authority name" | null,
  "ban_reason":   "reason from evidence" | null,
  "description":  "3–5 warm human sentences"
}}"""

    user_msg = f"""Beach selected: {display_title}
Region: {region_name}
Today's date: {today_str}
Wave height: {wave_result['wave_height_m']:.2f}m
Experience: {swimmer_grade}
Wave risk: {wave_result['risk_level']} — {wave_result['advice']}

{evidence_text}

Apply all 4 phases. Reason carefully about whether ban dates are before or
after {today_str}. Return the JSON advisory."""

    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg},
        ],
        max_tokens=700,
        temperature=0,
    )

    raw = response.choices[0].message.content.strip()
    for fence in ["```json", "```"]:
        if raw.startswith(fence):
            raw = raw.split(fence, 1)[1].split("```")[0].strip()
            break
    return json.loads(raw)


# ==============================================================================
# 8. MASTER PIPELINE
# ==============================================================================
def run_two_agent_pipeline(
        display_title: str,
        region_name: str,
        wave_height: float,
        swimmer_grade: str,
        status_placeholder,
) -> dict:
    wave_result = classify_wave_risk(wave_height, swimmer_grade)

    serper_key = bool(st.secrets.get("SERPER_API_KEY", ""))
    serpapi_key = bool(st.secrets.get("SERPAPI_KEY", ""))

    if serper_key:
        provider_label = "Serper + RSS"
    elif serpapi_key:
        provider_label = "SerpAPI (fallback) + RSS"
    else:
        provider_label = "RSS only"

    status_placeholder.markdown(
        '<p class="agent-step">✨ AI agent is gathering real-time safety info and preparing your advisory...</p>',
        unsafe_allow_html=True
    )

    search_data = agent1_search(region_name)
    n_results = search_data["total_found"]
    n_ban_hits = len(search_data["ban_hits"])
    providers_used = search_data.get("providers_used", [])
    provider_detail = " | ".join(providers_used)

    status_placeholder.markdown(
        f'<p class="agent-step">✅ Agent 1 — {n_results} unique results '
        f'({n_ban_hits} with restriction signals) · {provider_detail}</p>',
        unsafe_allow_html=True
    )

    status_placeholder.markdown(
        '<p class="agent-step">✨ AI agent is gathering real-time safety info and preparing your advisory...</p>',
        unsafe_allow_html=True
    )

    try:
        result = agent2_verify_and_advise(
            display_title=display_title,
            region_name=region_name,
            search_data=search_data,
            wave_result=wave_result,
            swimmer_grade=swimmer_grade,
        )
        status_placeholder.empty()
        return result
    except Exception as e:
        status_placeholder.empty()
        return _fallback_advisory(display_title, wave_result, search_data, str(e))


def _fallback_advisory(display_title: str, wave_result: dict,
                       search_data: dict, error: str) -> dict:
    blob = " ".join(
        f"{r['title']} {r['snippet']}" for r in search_data.get("results", [])
    ).lower()
    ban_kws = ["swimming banned", "beach closed", "entry prohibited",
               "sea entry banned", "no swimming", "water sports banned"]
    has_ban = any(k in blob for k in ban_kws)
    risk = wave_result["risk_level"]
    wh = wave_result["wave_height_m"]

    if has_ban:
        return {"status": "BAN BY AUTHORITY", "bg_type": "ban",
                "ban_detected": True, "ban_expired": False,
                "ban_scope": None, "ban_dates": None, "ban_by": None,
                "ban_reason": "official order",
                "description": (
                    f"Authorities have issued an official ban on sea entry at "
                    f"{display_title}. All water activities are currently prohibited. "
                    f"Current wave height is {wh:.2f}m. Please do not enter the water "
                    f"until the ban is officially lifted."
                )}
    elif risk == "HIGH":
        return {"status": "CAUTION", "bg_type": "caution",
                "ban_detected": False, "ban_expired": False,
                "ban_scope": None, "ban_dates": None, "ban_by": None, "ban_reason": None,
                "description": (
                    f"{display_title} is open but conditions are risky. "
                    f"{wave_result['advice']} Exercise extreme caution and "
                    f"stay close to shore at all times."
                )}
    elif risk == "MODERATE":
        return {"status": "CAUTION", "bg_type": "caution",
                "ban_detected": False, "ban_expired": False,
                "ban_scope": None, "ban_dates": None, "ban_by": None, "ban_reason": None,
                "description": (
                    f"The sea at {display_title} is moderately choppy. "
                    f"{wave_result['advice']} Swim only in supervised zones "
                    f"with lifeguards present."
                )}
    else:
        return {"status": "SAFE", "bg_type": "safe",
                "ban_detected": False, "ban_expired": False,
                "ban_scope": None, "ban_dates": None, "ban_by": None, "ban_reason": None,
                "description": (
                    f"{display_title} looks good for a beach visit today. "
                    f"{wave_result['advice']} Always swim in supervised areas "
                    f"and watch for local flag warnings."
                )}


# ==============================================================================
# 9. RUNTIME CONTROLLER
# ==============================================================================
for key in ["selected_spot_data", "last_query_string", "beach_list", "region_name"]:
    if key not in st.session_state:
        st.session_state[key] = None if key in ("selected_spot_data",) else \
            [] if key == "beach_list" else ""

if user_input != st.session_state.last_query_string:
    st.session_state.selected_spot_data = None
    st.session_state.last_query_string = user_input
    st.session_state.beach_list = []
    st.session_state.region_name = ""

if user_input:
    country_iso = GLOBAL_COUNTRIES[selected_country]

    if not st.session_state.beach_list:
        with st.spinner("🔍 Finding beaches in this region…"):
            beaches, rn = resolve_beaches_for_region(user_input, country_iso)
            st.session_state.beach_list = beaches
            st.session_state.region_name = rn

    beaches = st.session_state.beach_list
    region_name = st.session_state.region_name

    if st.session_state.selected_spot_data is None:
        if beaches:
            c = len(beaches)
            st.markdown(
                f'<p class="clean-search-text">🏖️ Found <strong>{c}</strong> '
                f'beach{"es" if c != 1 else ""} in <strong>{region_name}</strong>'
                f' — select one to check conditions:</p>',
                unsafe_allow_html=True
            )
            for idx, b in enumerate(beaches):
                lbl = f"🏖️ {b['display_title']}"
                if b.get("state"):   lbl += f", {b['state']}"
                if b.get("country"): lbl += f" ({b['country']})"
                if st.button(lbl, key=f"beach_btn_{idx}", use_container_width=True):
                    st.session_state.selected_spot_data = b
                    st.rerun()
        else:
            st.markdown("""
                <div style="background:#ffeeef;border:1px solid #fca5a5;
                padding:15px;border-radius:8px;text-align:center;
                color:#b91c1c;font-size:13.5px;font-weight:500;margin-top:20px;">
                No beaches found. Try a different spelling or select a country.
                </div>""", unsafe_allow_html=True)

    if st.session_state.selected_spot_data is not None:
        node = st.session_state.selected_spot_data
        lat, lon = node["lat"], node["lon"]

        marine = fetch_marine_telemetry(lat, lon)
        wave_height = 0.0
        daily_max = []
        forecast_dates = []

        if marine:
            if "hourly" in marine and "wave_height" in marine["hourly"]:
                ts = marine["hourly"]["time"]
                hs = [h or 0.0 for h in marine["hourly"]["wave_height"]]
                now = datetime.now()
                idx = min(range(len(ts)),
                          key=lambda i: abs(
                              datetime.fromisoformat(ts[i].replace("Z", "")) - now))
                wave_height = hs[idx]
            if "daily" in marine and "wave_height_max" in marine["daily"]:
                daily_max = [w or 0.0 for w in marine["daily"]["wave_height_max"]]
                forecast_dates = marine["daily"].get("time", [])

        status_ph = st.empty()

        output = run_two_agent_pipeline(
            display_title=node["display_title"],
            region_name=region_name,
            wave_height=wave_height,
            swimmer_grade=skill_level,
            status_placeholder=status_ph,
        )

        status = output.get("status", "SAFE")
        bg_type = output.get("bg_type", "safe")
        has_ban = output.get("ban_detected", False)
        ban_expired = output.get("ban_expired", False)
        ban_scope = output.get("ban_scope") or ""
        ban_dates = output.get("ban_dates") or ""
        ban_by = output.get("ban_by") or ""
        ban_reason = output.get("ban_reason") or ""
        ai_desc = output.get("description", "")

        for junk in ["```html", "```json", "```", "<div>", "</div>", "<p>", "</p>"]:
            ai_desc = ai_desc.replace(junk, "")
        ai_desc = ai_desc.strip()

        if has_ban and not ban_expired:
            display_status = "🚫 BAN BY AUTHORITY"
            pill_class = "badge-ban"
            bg_type = "ban"
        elif bg_type == "caution" or status == "CAUTION":
            display_status = "⚠️ CAUTION"
            pill_class = "badge-caution"
        else:
            display_status = "✅ SAFE"
            pill_class = "badge-safe"

        bg_img = {
            "ban": "https://images.unsplash.com/photo-1625224588466-56616e65dc59"
                   "?auto=format&fit=crop&w=1200&q=80",
            "caution": "https://images.unsplash.com/photo-1519046904884-53103b34b206"
                       "?auto=format&fit=crop&w=1200&q=80",
            "safe": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e"
                    "?auto=format&fit=crop&w=1200&q=80",
        }.get(bg_type, "https://images.unsplash.com/photo-1507525428034-b723cf961d3e"
                       "?auto=format&fit=crop&w=1200&q=80")

        ban_box_html = ""
        if has_ban and not ban_expired:
            rows = []
            if ban_by:     rows.append(f"<strong>Issued by:</strong> {ban_by}")
            if ban_scope:  rows.append(f"<strong>Covers:</strong> {ban_scope.capitalize()}")
            if ban_reason: rows.append(f"<strong>Reason:</strong> {ban_reason.capitalize()}")
            rows.append(
                f"<strong>Restriction period:</strong> {ban_dates}"
                if ban_dates else
                "<strong>Duration:</strong> Ongoing — verify with local authorities"
            )
            ban_box_html = (
                '<div class="ban-box">'
                '<div class="ban-box-title">🚫 Official Ban In Effect</div>'
                f'<p class="ban-box-body">{"<br>".join(rows)}</p>'
                '</div>'
            )

        card_style = (
            "border-radius:24px;padding:40px;"
            "box-shadow:0 20px 40px rgba(15,23,42,0.16);"
            "border:1px solid rgba(255,255,255,0.1);"
            "margin-top:25px;color:#ffffff;"
            f"background-image:linear-gradient(rgba(10,20,40,0.60),"
            f"rgba(10,20,40,0.75)),url({bg_img});"
            "background-size:cover;background-position:center;"
        )
        st.markdown(
            f'<div style="{card_style}">'
            f'<span class="{pill_class}">{display_status}</span>'
            f'<h3 class="advisory-header-title">Safety Report: '
            f'{node["display_title"]}</h3>'
            f'{ban_box_html}'
            f'<p class="advisory-prose-body">{ai_desc}</p>'
            f'<div class="brand-stamp-footer">'
            f'✨ Powered by CoastPulse AI </div>'
            f'</div>',
            unsafe_allow_html=True
        )

        if daily_max:
            st.markdown(
                "<br><h4 style='font-size:16px;font-weight:700;color:#0f172a;"
                "margin-bottom:15px;'>📅 Your 7-Day Trip Planner Matrix</h4>",
                unsafe_allow_html=True
            )
            cols = st.columns(7)
            for i in range(min(7, len(daily_max))):
                p_date = datetime.strptime(forecast_dates[i], "%Y-%m-%d")
                mw = daily_max[i]
                if has_ban and not ban_expired:
                    lbl, bg, txt = "🚫 BANNED", "#f3e8ff", "#6d28d9"
                elif mw > 1.6:
                    lbl, bg, txt = "🚫 RISK", "#fff1f2", "#b91c1c"
                elif mw > 1.1 or status == "CAUTION":
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
                        f'<p style="margin:8px 0;font-size:11px;font-weight:800;'
                        f'color:{txt};">{lbl}</p>'
                        f'<span style="font-size:10px;color:#475569;">'
                        f'<strong>{mw:.2f}m</strong></span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )