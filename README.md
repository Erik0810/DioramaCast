# DioramaCast

🏔️ **AI-Powered Weather Diorama Generator**

> **Live Application**: [https://dioramacast.app](https://dioramacast.app)

## Overview

DioramaCast combines real-time weather data with AI image generation to create isometric diorama artwork. Select any location on the map, and the app fetches current weather conditions from OpenWeatherMap, then uses Nano Banana Pro to generate a custom diorama based on that location's weather.

## Technology Stack

**Backend:** Flask (Python 3.12), Gunicorn

**Frontend:** HTML5, CSS3, JavaScript, Leaflet.js

**APIs:** OpenWeatherMap (weather data), Nano Banana Pro (AI generation)

**Hosting:** Heroku with automatic deployment from main branch

**CI/CD:** GitHub Actions for automated testing

## Features

- 🗺️ Interactive world map with location search
- 🌤️ Real-time weather data
- 🎨 Customizable art styles, time of day, and seasons
- 🖼️ AI-generated dioramas on demand
- 💎 Responsive UI design
- 🔄 Automated testing and deployment

## How It Works

1. User selects a location on the map
2. App fetches current weather from OpenWeatherMap API
3. System builds a prompt with the location, weather, and user preferences
4. AI generates a 1000x1000px isometric diorama
5. Image displays with weather info and city name

## Deployment

**CI/CD:** GitHub Actions runs tests on every push (environment setup, dependencies, Flask checks, API validation)

**Hosting:** Heroku automatically deploys changes from the main branch with zero downtime

**Built for Scale:** Stateless design with horizontal scaling to handle thousands of concurrent users. Includes error handling, API timeouts, and environment-based configuration.

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
