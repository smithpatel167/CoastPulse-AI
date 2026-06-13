# 🌊 CoastPulse AI — Coastal Safety Intelligence Console

CoastPulse AI is an advanced multi-agent coastal safety intelligence platform designed to help tourists, swimmers, and beach visitors make informed travel decisions before visiting a coastal destination.

The platform combines real-time marine telemetry, web intelligence gathering, and AI-powered legal notice verification to determine whether a beach is genuinely safe to visit and whether any active government restrictions, swimming bans, or hazard advisories are currently in effect.

🚀 **Live Application:** https://coastpulse-ai.streamlit.app/

---

# 🧠 System Architecture

CoastPulse AI follows a multi-agent architecture consisting of independent retrieval and reasoning layers.

## Agent 1 — Search & Retrieval Agent

Responsible for collecting coastal safety signals from multiple external sources.

### Functions

* Searches Google News RSS feeds
* Searches Google Custom Search Engine (CSE)
* Searches SerpAPI results
* Collects municipal notices
* Collects tourism advisories
* Collects regional news reports
* Collects government restrictions
* Retrieves marine forecast data

### Output

Agent 1 produces a structured evidence package containing:

* News headlines
* Snippets
* Publication dates
* Government notices
* Wave forecast information

These results are forwarded to Agent 2.

---

## Agent 2 — Verification & Advisory Agent

Powered by Azure AI Foundry.

### Functions

* Chronological reasoning
* Date validation
* Ban verification
* Restriction expiry validation
* Risk assessment
* Safety advisory generation

### Model Configuration

```python
temperature = 0
```

Using deterministic reasoning ensures consistent classification and minimizes hallucinations.

### Output

Agent 2 generates:

* Beach Safety Status
* Ban Verification Status
* AI Safety Advisory
* Visitor Recommendations
* Risk Explanation
* 7-Day Planning Matrix

---

# ⚡ Features

## 🌊 Real-Time Marine Telemetry

Live marine forecasts are retrieved from Open-Meteo Marine APIs including:

* Wave Height
* Maximum Wave Height
* Swell Conditions
* Hourly Forecasts

---

## 🏖️ Beach Discovery

Automatically identifies coastal beaches using:

* OpenStreetMap Nominatim
* Overpass API

---

## 🚨 Government Ban Detection

Searches and validates:

* Swimming bans
* Tourist restrictions
* Coastal closure orders
* Hazard notices
* Monsoon advisories

---

## 🤖 AI-Powered Verification

Azure AI Foundry evaluates:

* Whether a restriction is active
* Whether a restriction has expired
* Whether news reports are still relevant
* Whether marine conditions increase risk

---

## 🏊 Skill-Based Risk Classification

Risk recommendations adapt based on user skill level.

### Beginner / Casual Wader

Most conservative thresholds.

### Intermediate Swimmer

Moderate thresholds.

### Advanced Swimmer / Surfer

More tolerant thresholds.

---

## 📅 7-Day Trip Planning Matrix

The application generates a weekly planning dashboard.

Possible classifications:

| Status  | Meaning                       |
| ------- | ----------------------------- |
| PERFECT | Excellent conditions          |
| CAUTION | Visit possible with awareness |
| RISK    | Hazardous conditions          |
| BANNED  | Active government restriction |

---

## 🎨 User Experience

Built with:

* Streamlit
* Custom CSS
* Responsive Layouts
* Lottie Animations

---

# 🛠️ Technology Stack

## Frontend

* Streamlit
* HTML
* CSS

## Backend

* Python

## AI Layer

* Azure AI Foundry
* Azure OpenAI SDK

## Search Layer

* Google News RSS
* SerpAPI
* Google Custom Search Engine

## Data Layer

* Open-Meteo Marine API
* OpenStreetMap Nominatim API
* Overpass API

---

# 📂 Project Structure

```text
CoastPulse-AI/
│
├── app.py
├── requirements.txt
│
├── .streamlit/
│   └── secrets.toml
│
└── assets/
```

---

# 🛠️ Local Installation

## 1. Clone Repository

```bash
git clone https://github.com/smithpatel167/CoastPulse-AI.git

cd CoastPulse-AI
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Example requirements:

```text
streamlit
requests
openai
streamlit-lottie
pandas
feedparser
```

---

## 4. Configure Secrets

Create:

```text
.streamlit/secrets.toml
```

Add:

```toml
AZURE_OPENAI_API_KEY = "YOUR_AZURE_KEY"

AZURE_OPENAI_ENDPOINT = "https://YOUR_RESOURCE.openai.azure.com/"

AZURE_OPENAI_DEPLOYMENT_NAME = "gpt-4o"

SERPAPI_KEY = "YOUR_SERPAPI_KEY"

GOOGLE_CSE_KEY = "YOUR_CSE_KEY"

GOOGLE_CSE_CX = "YOUR_CSE_ENGINE_ID"
```

---

## 5. Run Application

```bash
streamlit run app.py
```

Application will launch at:

```text
http://localhost:8501
```

---

# 🌐 API References

## OpenStreetMap Nominatim

Used for:

* Geocoding
* Reverse Geocoding
* Location Discovery

Documentation:

https://nominatim.org/

---

## Overpass API

Used for:

* Beach Discovery
* Geographic Feature Extraction

Documentation:

https://overpass-api.de/

---

## Open-Meteo Marine API

Used for:

* Wave Height
* Maximum Wave Height
* Marine Forecasting

Documentation:

https://open-meteo.com/

---

## Azure AI Foundry

Used for:

* Reasoning
* Ban Verification
* Advisory Generation

Documentation:

https://azure.microsoft.com/products/ai-foundry/

---

## SerpAPI

Used for:

* Google Search Results
* Web Intelligence Collection

Documentation:

https://serpapi.com/

---

## Google Custom Search Engine

Used for:

* Focused Search Retrieval
* Government Notice Discovery

Documentation:

https://programmablesearchengine.google.com/

---

# 🔒 Safety Philosophy

CoastPulse AI does not rely solely on wave conditions.

A beach may appear physically safe while simultaneously being subject to:

* Government restrictions
* Temporary closures
* Monsoon bans
* Hazard advisories

The platform therefore combines:

1. Physical ocean conditions
2. Legal restrictions
3. News intelligence
4. AI reasoning

to generate a unified safety assessment.

---

# 🚀 Future Roadmap

Planned enhancements include:

* Weather integration
* Rip current prediction
* Satellite imagery support
* Multilingual advisories
* Mobile application
* Push notifications
* Historical safety analytics

---

# 👨‍💻 Developed For

**Agents League Hackathon**

Built using:

* Azure AI Foundry
* Streamlit
* Open-Meteo APIs
* OpenStreetMap Ecosystem

---

## License

MIT License
