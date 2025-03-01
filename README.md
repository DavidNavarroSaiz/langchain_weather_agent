# OpenWeather API Wrapper

A simple Python wrapper for the OpenWeather API that uses environment variables for configuration.

## Setup

1. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

2. Configure your `.env` file:
   - The repository includes a `.env` file with your API key and the OpenWeather API URLs
   - Make sure to keep this file secure and do not commit it to public repositories

## Usage

```python
from openwather_api import OpenWeather

# Initialize the client (API key is loaded from .env file)
weather = OpenWeather()

# Get geolocation for a city
location = weather.get_geolocation("London", "GB")
if location:
    lat, lon = location[0]["lat"], location[0]["lon"]
    
    # Get current weather
    current_weather = weather.get_current_weather(lat, lon)
    
    # Get forecast
    forecast = weather.get_forecast(lat, lon)
    
    # Get weather map URL
    map_url = weather.get_weather_map_url("clouds_new", 10, 500, 250)
```

## Available Methods

- `get_geolocation(city_name, country_code=None, state_code=None, limit=1)`: Get geographic coordinates for a location
- `get_current_weather(lat, lon, units="metric", lang="en")`: Get current weather for coordinates
- `get_forecast(lat, lon, units="metric", lang="en", cnt=40)`: Get weather forecast
- `get_weather_map_url(layer, z, x, y)`: Get URL for weather map tiles