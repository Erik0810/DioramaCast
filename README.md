# DioramaCast

🏔️ **AI-Powered Weather Diorama Generator**

> **Live Application**: [https://dioramacast.app](https://dioramacast.app)

## Overview

**DioramaCast** is an enterprise-grade AI abstraction layer that transforms real-world weather data into stunning visual dioramas. This production-ready service orchestrates multiple APIs—OpenWeatherMap for live weather data and Nano Banana Pro for AI image generation—to create custom isometric diorama artwork based on any location's current conditions.

## Technology Stack

**Core:** Flask (Python 3.12), HTML5/CSS3/JavaScript, Leaflet.js, Gunicorn

**APIs:** OpenWeatherMap (weather data), Nano Banana Pro (AI image generation)

**Infrastructure:** Heroku cloud hosting, GitHub Actions CI/CD, automatic deployment from main branch

**Architecture:** Stateless design built to handle thousands of concurrent users with horizontal scaling, graceful degradation, and comprehensive error handling

## Features

- 🗺️ Interactive world map with location search
- 🌤️ Real-time weather data integration
- 🎨 Customizable art styles, time of day, and seasons
- 🖼️ AI-generated isometric dioramas on-demand
- 💎 Responsive, modern UI design
- ⚡ Production-optimized performance
- 🔄 Automated CI/CD pipeline

## How It Works

**Flow:** User selects location → Weather API fetches conditions → Dynamic prompt constructed → AI generates isometric diorama → Image displayed with embedded weather data

**Prompt Engineering:** The system constructs detailed prompts incorporating city landmarks, current weather conditions, temperature, and user-selected preferences (art style, time of day, season) to generate consistent, high-quality 1000x1000px isometric dioramas with text overlays.

## CI/CD & Deployment

**GitHub Actions:** Automated testing on every push—environment setup, dependency installation, Flask integrity checks, API endpoint validation

**Heroku Deployment:** Main branch changes automatically deploy to production with zero-downtime rolling updates, Gunicorn WSGI server, and secure environment configuration

## Production Quality

**Scalability:** Stateless architecture with horizontal scaling, Gunicorn worker processes handling thousands of concurrent users

**Reliability:** Comprehensive error handling, graceful API degradation, timeout management, production-grade logging

**Best Practices:** Environment-based configuration (12-factor), automated testing, RESTful API design, clean modular codebase

---

## Local Development

<details>
<summary>Click to expand local setup instructions</summary>

### Prerequisites
- Python 3.8 or higher
- pip package manager
- API keys (OpenWeatherMap, Nano Banana Pro)

### Quick Start

1. Clone the repository:
```bash
git clone https://github.com/Erik0810/DioramaCast.git
cd DioramaCast
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
```
Edit `.env` with your API keys.

4. Run locally:
```bash
python app.py
```

5. Access at `http://localhost:5000`

For detailed API integration instructions, see [API_INTEGRATION.md](API_INTEGRATION.md).

</details>

---

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Weather data powered by [OpenWeatherMap](https://openweathermap.org)
- Map visualization via [Leaflet.js](https://leafletjs.com) and [OpenStreetMap](https://www.openstreetmap.org)
- AI image generation through Nano Banana Pro API
- Icons by [Font Awesome](https://fontawesome.com)

---

**Portfolio Project by Erik** | [Live Demo](https://dioramacast.app) | Built with ❤️ using Flask & AI
