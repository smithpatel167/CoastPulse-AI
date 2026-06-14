# 🌊 CoastPulse AI — Coastal Safety Intelligence Console

CoastPulse AI is an advanced multi-agent coastal safety intelligence platform designed to help tourists, swimmers, and beach visitors make informed travel decisions before visiting a coastal destination.

The platform combines real-time marine telemetry, web intelligence gathering, and AI-powered legal notice verification to determine whether a beach is genuinely safe to visit and whether any active government restrictions, swimming bans, or hazard advisories are currently in effect.

🚀 **Live Application:** [coastpulse-ai.streamlit.app](https://coastpulse-ai.streamlit.app/)

---

# 🧠 System Architecture

CoastPulse AI follows a multi-agent architecture consisting of independent retrieval and reasoning layers.

## Agent 1 — Search & Retrieval Agent

Responsible for collecting coastal safety signals from multiple external sources. Built with an automated, **high-availability failover pipeline architecture**, it prioritizes high-throughput SERP APIs and instantly falls back to alternative data pipelines if rate limits are hit, ensuring zero-downtime intelligence harvesting.

### Functions

* Searches Google News RSS feeds
* Queries high-throughput Google Search scraping layers (**Serper API** / **SerpAPI**)
* Executes multi-threaded operations across diverse web endpoints
* Collects municipal notices and regional news reports
* Gathers tourism advisories and government restriction orders
* Retrieves live open-ocean marine forecast data

### Output

Agent 1 produces a structured evidence package containing:

* News headlines and web snippets
* Publication dates
* Verified government notices
* Wave forecast metadata

These results are dynamically forwarded to Agent 2.

---

## Agent 2 — Verification & Advisory Agent

Powered by Azure AI Foundry.

### Functions

* Chronological reasoning and live calendar cross-referencing
* Date validation (checking if bans are currently active, pending, or expired)
* Legal restriction and beach closure verification
* Skill-adaptive risk assessment
* Context-aware safety advisory generation

### Model Configuration

```python
temperature = 0
```

Leveraging precision prompt structuring and zero-temperature configurations (`temperature=0`) inside Azure AI Foundry eliminates hallucinations regarding legal dates, ensuring ban periods are parsed accurately against live calendars.

### Output

Agent 2 generates:

* Beach Safety Status
* Ban Verification Status
* Clean AI Safety Advisory (devoid of algorithmic debris or tracking URLs)
* Visitor Recommendations
* Risk Explanation
* 7-Day Planning Matrix

---

# ⚡ Features

## 🌊 Real-Time Marine Telemetry

Live marine forecasts are retrieved from Open-Meteo Marine APIs including wave height (meters), maximum wave height, swell conditions, and hourly outlooks.

## 🏖️ Beach Discovery

Automatically identifies coastal beach coordinate nodes and geographical structures using OpenStreetMap Nominatim and the Overpass API.

## 🚨 Government Ban Detection

Searches and validates swimming bans, tourist restrictions, coastal closure orders, hazard notices, and seasonal monsoon advisories.

## 🤖 AI-Powered Verification

Azure AI Foundry acts as the core cognitive gateway, running temporal calculations against the absolute current date to check if extracted local bans are active or expired.

## 🏊 Skill-Based Risk Classification

Risk recommendations adapt based on user skill level:

* **Beginner / Casual Wader:** Most conservative thresholds.
* **Intermediate Swimmer:** Moderate safety thresholds.
* **Advanced Swimmer / Surfer:** More tolerant, wave-swell optimized thresholds.

## 📅 7-Day Trip Planning Matrix

The application generates a unified weekly planning dashboard using custom CSS status injections.

| Status  | Meaning                       |
| ------- | ----------------------------- |
| PERFECT | Excellent marine conditions   |
| CAUTION | Visit possible with awareness |
| RISK    | Hazardous physical conditions |
| BANNED  | Active government restriction |

---

# 🛠️ Technology Stack

* **Frontend & UI:** Streamlit, Custom HTML/CSS, Lottie Animations
* **Backend:** Python
* **AI Layer:** Azure AI Foundry, Azure OpenAI SDK
* **Search & Web Intelligence:** Google News RSS, Serper API, SerpAPI
* **Geospatial & Telemetry Data:** Open-Meteo Marine API, OpenStreetMap Nominatim API, Overpass API

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

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Secrets

Create a `.streamlit/secrets.toml` file:

```toml
AZURE_OPENAI_API_KEY = "YOUR_AZURE_KEY"
AZURE_OPENAI_ENDPOINT = "https://YOUR_RESOURCE.openai.azure.com/"
AZURE_OPENAI_DEPLOYMENT_NAME = "gpt-4o"

SERPER_API_KEY = "YOUR_SERPER_KEY"
SERPAPI_KEY = "YOUR_SERPAPI_KEY"
```

## 5. Run Application

```bash
streamlit run app.py
```

---

# 🌐 API References

* **OpenStreetMap Nominatim:** Geocoding and location discovery. (https://nominatim.org/)
* **Overpass API:** Geographic feature extraction for mapping coastal boundaries. (https://overpass-api.de/)
* **Open-Meteo Marine API:** High-resolution wave and swell marine forecasting. (https://open-meteo.com/)
* **Azure AI Foundry:** Core reasoning gateway and deterministic safety assessment generator. (https://azure.microsoft.com/products/ai-foundry/)
* **Serper API & SerpAPI:** High-throughput, resilient web intelligence retrieval infrastructure.

---

# 🔒 Safety Philosophy

CoastPulse AI rejects single-datapoint assessments. A beach may appear physically calm and safe while simultaneously being subject to sudden monsoon bans or hazardous environmental closures.

The platform guarantees safety by executing a zero-trust multi-point validation check:

1. **Physical Ocean Conditions** (Waves, Swell, Speed)
2. **Legal Restrictions** (Municipal bans, Administrative orders)
3. **News Intelligence** (Local drowning alerts, high-signal warnings)

Only after all validation layers agree is a final safety recommendation generated.

---

# 🚀 Future Roadmap

* Real-time rip current machine learning prediction maps
* Satellite SAR imagery integration for surface water anomaly detection
* Multilingual automated advisories for international travelers
* Mobile application with geo-fenced push notifications
* Historical coastal safety analytics engine

---

# 👨‍💻 Developed For

**Agents League Hackathon**

Built using Azure AI Foundry, Streamlit, Open-Meteo APIs, and the OpenStreetMap ecosystem.

---

## License

MIT License
