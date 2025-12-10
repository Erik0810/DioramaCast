# DioramaCast

🏔️ Generate beautiful dioramas based on real-world weather of any location

## Overview

DioramaCast is a modern Flask web application that combines real-time weather data with AI image generation to create stunning miniature diorama scenes. Select any location on an interactive world map, view its current weather conditions, customize your diorama settings, and generate a unique artistic representation.

## Features

- 🗺️ **Interactive World Map** - Click anywhere or search for locations
- 🌤️ **Real-time Weather Data** - Get current weather conditions via OpenWeatherMap API
- 🎨 **Customizable Settings** - Choose art style, time of day, and season
- 🖼️ **AI-Generated Dioramas** - Create unique miniature scenes based on location and weather
- 💎 **Modern UI** - Sleek design with cream white and dark blue theme
- 📱 **Responsive Layout** - Works on desktop and mobile devices

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- API keys (see below)

### Installation

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

Edit `.env` and add your API keys:
- **OPENWEATHER_API_KEY**: Get a free API key from [OpenWeatherMap](https://openweathermap.org/api)
- **NANABANA_API_KEY**: Configure your image generation API key

4. Run the application:
```bash
python app.py
```

5. Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

1. **Select a Location**: 
   - Click anywhere on the world map, or
   - Use the search bar to find a specific location

2. **View Weather**: 
   - Weather information automatically loads for the selected location

3. **Customize Settings**:
   - Choose your preferred art style
   - Select time of day
   - Pick a season

4. **Generate Diorama**:
   - Click the "Generate Diorama" button
   - Wait for the AI to create your unique image
   - View the generated diorama in the bottom-right panel

## API Requirements

### OpenWeatherMap API
- **Purpose**: Retrieve real-time weather data
- **Free Tier**: 1,000 calls/day
- **Sign Up**: https://openweathermap.org/api

### Nano Banana Pro API
- **Purpose**: Generate diorama images
- **Note**: You'll need to configure the actual API integration in `app.py`
- The current implementation includes a placeholder for the image generation endpoint

## Project Structure

```
DioramaCast/
├── app.py                 # Flask application and API endpoints
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
├── templates/
│   └── index.html        # Main HTML template
└── static/
    ├── css/
    │   └── style.css     # Application styles
    └── js/
        └── app.js        # Client-side JavaScript
```

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Map Library**: Leaflet.js
- **Weather API**: OpenWeatherMap
- **Styling**: Custom CSS with modern design
- **Icons**: Font Awesome

## Customization

### Modifying the Theme
Edit the CSS variables in `static/css/style.css`:
```css
:root {
    --dark-blue: #1a2332;
    --cream-white: #f8f6f0;
    /* ... other colors */
}
```

### Adding More Settings
1. Add HTML form elements in `templates/index.html`
2. Update the settings gathering in `static/js/app.js`
3. Modify the prompt generation in `app.py`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Weather data provided by OpenWeatherMap
- Map tiles from OpenStreetMap
- Icons by Font Awesome
