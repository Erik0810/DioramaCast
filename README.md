# DioramaCast

🏔️ **AI-Powered Weather Diorama Generator**

> **Live Application**: [https://dioramacast.app](https://dioramacast.app)

## Overview

**DioramaCast** is an enterprise-grade AI abstraction layer that transforms real-world weather data into stunning visual dioramas. Built as a production-ready web service, it demonstrates advanced cloud architecture, continuous integration/deployment practices, and robust API orchestration at scale.

### What It Does

DioramaCast intelligently combines multiple external APIs to deliver a seamless user experience:

1. **Interactive Geolocation** - Users select any location worldwide via an interactive map interface
2. **Real-Time Weather Integration** - Fetches live weather data from OpenWeatherMap API
3. **AI Image Generation** - Utilizes AI image generation APIs (Nano Banana Pro) to create custom isometric diorama artwork
4. **Dynamic Prompt Engineering** - Automatically constructs detailed prompts incorporating location, weather conditions, temperature, and user preferences
5. **Responsive Delivery** - Serves generated content through a modern, mobile-responsive interface

## Architecture & Technology

### Core Stack
- **Backend**: Flask (Python 3.12)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Map Visualization**: Leaflet.js with OpenStreetMap tiles
- **Styling**: Custom CSS with modern design patterns

### API Integrations
- **OpenWeatherMap API** - Real-time weather data retrieval
- **Nano Banana Pro API** - AI-powered image generation
- **Geolocation Services** - Interactive world map functionality

### Infrastructure & DevOps
- **Cloud Hosting**: Heroku production environment
- **Continuous Integration**: GitHub Actions automated testing
- **Continuous Deployment**: Automatic deployment from main branch to Heroku
- **Process Management**: Gunicorn WSGI server for production workloads
- **Environment Management**: Secure configuration via environment variables

### Scalability & Robustness
- **Enterprise-Ready Architecture** - Built to handle thousands of concurrent users
- **Stateless Design** - Horizontally scalable for growing demand
- **Error Handling** - Comprehensive exception management and graceful degradation
- **API Resilience** - Timeout handling and fallback mechanisms
- **Performance Optimization** - Efficient request processing and response caching strategies

## Key Features

- 🗺️ **Interactive World Map** - Click anywhere globally or search specific locations
- 🌤️ **Real-Time Weather Integration** - Live atmospheric data from OpenWeatherMap
- 🎨 **Customizable Parameters** - User-selectable art styles, time of day, and seasons
- 🖼️ **AI-Generated Artwork** - Unique isometric dioramas created on-demand
- 💎 **Modern UI/UX** - Responsive design with refined color palette
- ⚡ **Production Performance** - Optimized for speed and reliability
- 🔄 **Automated CI/CD** - Continuous testing and seamless deployments

## How It Works

### User Flow

1. **Select Location** - Click anywhere on the interactive world map or search for a specific city
2. **Weather Retrieval** - Application automatically fetches current weather conditions for the selected coordinates
3. **Customize Experience** - Choose preferred art style, time of day, and seasonal settings
4. **AI Generation** - Click "Generate Diorama" to initiate AI image creation
5. **View Results** - Unique isometric diorama appears with embedded weather information and city name

### Technical Flow

```
User Input (Location + Preferences)
    ↓
OpenWeatherMap API Call
    ↓
Dynamic Prompt Construction
    ↓
AI Image Generation API
    ↓
Rendered Diorama Display
```

### Prompt Engineering

The system employs sophisticated prompt engineering to create consistent, high-quality outputs. Each generated prompt includes:

- **Location context** - City name and iconic landmarks
- **Weather integration** - Current conditions (clear, rainy, cloudy, etc.)
- **Environmental parameters** - Temperature, atmospheric mood
- **Visual specifications** - Isometric perspective, 1000x1000 dimensions, PBR materials
- **Text overlays** - City name, date, temperature, weather icons
- **Artistic direction** - Minimalistic composition, soft lighting, refined textures

Example generated prompt structure:
```
Present a clear, 45° top-down isometric miniature 3D cartoon scene of [CITY], 
featuring iconic landmarks. Integrate [WEATHER] conditions with realistic 
atmospheric effects. Display title "[CITY]", weather icon, date, and 
temperature ([TEMP]°C) overlaid on the scene. Square 1000x1000 dimension.
```

## Continuous Integration & Deployment

### GitHub Actions CI Pipeline

Automated testing runs on every push and pull request:

- **Python Environment Setup** - Consistent Python 3.11 environment
- **Dependency Installation** - Automated package management
- **Application Testing** - Flask app integrity checks
- **API Endpoint Validation** - Smoke tests for all routes
- **Environment Verification** - Configuration validation

The CI workflow ensures code quality and catches issues before deployment.

### Continuous Deployment to Heroku

- **Automatic Deployment** - Main branch changes trigger production deployments
- **Zero-Downtime Updates** - Seamless rolling deployments
- **Environment Configuration** - Secure secrets management via Heroku config vars
- **Production WSGI Server** - Gunicorn for handling concurrent requests
- **Health Monitoring** - Automated application health checks

### Project Structure

```
DioramaCast/
├── app.py                    # Flask application & API endpoints
├── requirements.txt          # Python dependencies
├── runtime.txt              # Python version specification
├── Procfile                 # Heroku process configuration
├── .github/
│   └── workflows/
│       └── test.yml         # CI/CD pipeline configuration
├── templates/
│   └── index.html           # Main application template
└── static/
    ├── css/
    │   └── style.css        # Application styles
    └── js/
        └── app.js           # Client-side logic
```

## Performance & Scalability

### Built for Scale

- **Stateless Architecture** - Enables horizontal scaling across multiple dynos/containers
- **Concurrent Request Handling** - Gunicorn worker processes handle thousands of simultaneous users
- **Efficient API Management** - Optimized request patterns and timeout handling
- **Resource Optimization** - Minimal memory footprint per request
- **Load Distribution** - Ready for load balancer integration

### Production Readiness

- **Error Recovery** - Comprehensive exception handling prevents cascading failures
- **Graceful Degradation** - Fallback responses when external APIs are unavailable
- **Timeout Management** - Prevents resource exhaustion from slow API calls
- **Logging & Monitoring** - Production-grade logging for debugging and analytics
- **Security Best Practices** - Environment-based secrets, no hardcoded credentials

## Technical Highlights

### API Orchestration
Seamlessly coordinates multiple third-party services:
- Weather data retrieval with error handling and fallbacks
- AI image generation with dynamic prompt construction
- Geolocation services for global coverage

### Modern Development Practices
- **Environment-based Configuration** - 12-factor app methodology
- **Automated Testing** - CI pipeline with comprehensive checks
- **Version Control** - Git workflow with feature branches
- **Dependency Management** - Explicit version pinning for reproducibility
- **Documentation** - Comprehensive guides for API integration

### Code Quality
- Clean, maintainable Python codebase
- RESTful API design principles
- Separation of concerns (frontend/backend)
- Modular architecture for extensibility

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
