import requests
import os
from dotenv import load_dotenv
import datetime

# Load environment variables from .env file
load_dotenv()

class OpenWeather:
    BASE_URL = os.getenv("OPENWEATHER_BASE_URL")
    GEO_URL = os.getenv("OPENWEATHER_GEO_URL")
    FORECAST_URL = os.getenv("OPENWEATHER_FORECAST_URL")
    MAP_URL = os.getenv("OPENWEATHER_MAP_URL")

    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY")

    def get_geolocation(self, city_name, country_code=None, state_code=None, limit=1):
        params = {
            "q": f"{city_name},{state_code},{country_code}" if state_code and country_code else city_name,
            "limit": limit,
            "appid": self.api_key
        }
        response = requests.get(self.GEO_URL, params=params)
        return response.json() if response.status_code == 200 else None

    def get_current_weather(self, lat, lon, units="metric", lang="en"):
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": units,
            "lang": lang
        }
        response = requests.get(self.BASE_URL, params=params)
        return response.json() if response.status_code == 200 else None

    def get_forecast(self, lat, lon, units="metric", lang="en", cnt=40):
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": units,
            "lang": lang,
            "cnt": cnt
        }
        response = requests.get(self.FORECAST_URL, params=params)
        return response.json() if response.status_code == 200 else None

    def get_weather_map_url(self, layer, z, x, y):
        return self.MAP_URL.format(layer=layer, z=z, x=x, y=y) + f"?appid={self.api_key}"
        
    def format_current_weather(self, weather_data, city_name, country_code=None):
        """
        Format current weather data into a readable string with all available information
        
        Args:
            weather_data: The weather data from the API
            city_name: The name of the city
            country_code: The country code (optional)
            
        Returns:
            A formatted string with complete weather information
        """
        if not weather_data:
            return f"No weather data available for {city_name}"
            
        # Extract data
        main = weather_data.get("main", {})
        weather = weather_data.get("weather", [{}])[0]
        wind = weather_data.get("wind", {})
        sys = weather_data.get("sys", {})
        clouds = weather_data.get("clouds", {})
        coord = weather_data.get("coord", {})
        
        # Format timestamp
        timestamp = weather_data.get("dt", 0)
        date_time = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        
        # Get country from data if not provided
        if not country_code and "country" in sys:
            country_code = sys["country"]
            
        # Format sunrise and sunset if available
        sunrise = sys.get("sunrise")
        sunset = sys.get("sunset")
        sunrise_str = datetime.datetime.fromtimestamp(sunrise).strftime('%H:%M:%S') if sunrise else "N/A"
        sunset_str = datetime.datetime.fromtimestamp(sunset).strftime('%H:%M:%S') if sunset else "N/A"
        
        # Format the output
        result = f"""
        📍 Current Weather in {city_name}{f', {country_code}' if country_code else ''}
        ⏰ Updated: {date_time}
        📌 Coordinates: Lat {coord.get('lat')}, Lon {coord.get('lon')}

        🌡️ Temperature Information:
        Current: {main.get('temp')}°C
        Feels like: {main.get('feels_like')}°C
        Min: {main.get('temp_min')}°C
        Max: {main.get('temp_max')}°C

        🌤️ Weather Condition: 
        Main: {weather.get('main')}
        Description: {weather.get('description')}
        Weather ID: {weather.get('id')}
        Icon: {weather.get('icon')}

        💧 Humidity: {main.get('humidity')}%
        🧭 Pressure: {main.get('pressure')} hPa
        Sea Level: {main.get('sea_level', 'N/A')} hPa
        Ground Level: {main.get('grnd_level', 'N/A')} hPa

        💨 Wind Information:
        Speed: {wind.get('speed')} m/s
        Direction: {wind.get('deg')}°
        Gust: {wind.get('gust', 'N/A')} m/s

        ☁️ Cloudiness: {clouds.get('all')}%
        👁️ Visibility: {weather_data.get('visibility', 0) / 1000} km

        🌅 Sunrise: {sunrise_str}
        🌇 Sunset: {sunset_str}
        ⏱️ Timezone: UTC {weather_data.get('timezone', 0) // 3600:+d} hours
        """
        return result
        
    def format_forecast(self, forecast_data, city_name, country_code=None):
        """
        Format forecast data into a readable string with all available information
        
        Args:
            forecast_data: The forecast data from the API
            city_name: The name of the city
            country_code: The country code (optional)
            
        Returns:
            A formatted string with complete forecast information
        """
        if not forecast_data:
            return f"No forecast data available for {city_name}"
            
        # Extract data
        forecast_list = forecast_data.get("list", [])
        if not forecast_list:
            return "No forecast data available"
            
        # Get city information
        city_info = forecast_data.get("city", {})
        if not country_code and "country" in city_info:
            country_code = city_info["country"]
            
        # Get forecasts for different days (every 8th entry is a new day, approximately)
        daily_forecasts = [forecast_list[i] for i in range(0, min(40, len(forecast_list)), 8)]
        
        # Format city information
        city_coord = city_info.get("coord", {})
        population = city_info.get("population", "N/A")
        timezone = city_info.get("timezone", 0) // 3600  # Convert seconds to hours
        sunrise = city_info.get("sunrise")
        sunset = city_info.get("sunset")
        sunrise_str = datetime.datetime.fromtimestamp(sunrise).strftime('%H:%M:%S') if sunrise else "N/A"
        sunset_str = datetime.datetime.fromtimestamp(sunset).strftime('%H:%M:%S') if sunset else "N/A"
        
        result = f"""📅 5-Day Weather Forecast for {city_name}{f', {country_code}' if country_code else ''}

        🌐 City Information:
        Coordinates: Lat {city_coord.get('lat')}, Lon {city_coord.get('lon')}
        Population: {population}
        Timezone: UTC {timezone:+d} hours
        Sunrise: {sunrise_str}
        Sunset: {sunset_str}

        """
                
        for forecast in daily_forecasts:
            # Format timestamp
            timestamp = forecast.get("dt", 0)
            date_time = datetime.datetime.fromtimestamp(timestamp).strftime('%A, %b %d, %Y')
            time = datetime.datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')
            
            main = forecast.get("main", {})
            weather = forecast.get("weather", [{}])[0]
            clouds = forecast.get("clouds", {})
            wind = forecast.get("wind", {})
            visibility = forecast.get("visibility", "N/A")
            
            result += f"""
                📆 {date_time} at {time}
                🌡️ Temperature Information:
                Current: {main.get('temp')}°C
                Feels like: {main.get('feels_like')}°C
                Min: {main.get('temp_min')}°C
                Max: {main.get('temp_max')}°C

                🌤️ Weather Condition:
                Main: {weather.get('main')}
                Description: {weather.get('description')}
                Weather ID: {weather.get('id')}
                Icon: {weather.get('icon')}

                💧 Humidity: {main.get('humidity')}%
                🧭 Pressure Information:
                Pressure: {main.get('pressure')} hPa
                Sea Level: {main.get('sea_level', 'N/A')} hPa
                Ground Level: {main.get('grnd_level', 'N/A')} hPa

                💨 Wind Information:
                Speed: {wind.get('speed')} m/s
                Direction: {wind.get('deg')}°
                Gust: {wind.get('gust', 'N/A')} m/s

                ☁️ Cloudiness: {clouds.get('all')}%
                👁️ Visibility: {visibility if visibility == 'N/A' else f'{visibility / 1000} km'}
                """
            
            # Add precipitation info if available
            if "pop" in forecast:
                pop = forecast.get("pop", 0) * 100  # Convert to percentage
                result += f"🌧️ Chance of precipitation: {pop:.0f}%\n"
                
            # Add rain info if available
            if "rain" in forecast:
                rain = forecast.get("rain", {})
                if isinstance(rain, dict):
                    for period, amount in rain.items():
                        result += f"☔ Rain ({period}): {amount} mm\n"
                else:
                    result += f"☔ Rain: {rain} mm\n"
                    
            # Add snow info if available
            if "snow" in forecast:
                snow = forecast.get("snow", {})
                if isinstance(snow, dict):
                    for period, amount in snow.items():
                        result += f"❄️ Snow ({period}): {amount} mm\n"
                else:
                    result += f"❄️ Snow: {snow} mm\n"
                    
        return result

# Example usage:
if __name__ == "__main__":
    # API key is loaded from .env file
    weather = OpenWeather()
    
    # Get geolocation
    location = weather.get_geolocation("Medellin", "CO")
    if location:
        lat, lon = location[0]["lat"], location[0]["lon"]
        print("Latitude:", lat, "Longitude:", lon)
        
        # Get current weather
        # current_weather = weather.get_current_weather(lat, lon)
        # print("\nCurrent Weather:", current_weather)

        # # Get forecast
        # forecast = weather.get_forecast(lat, lon)
        # print("\nForecast:", forecast)
        
        # # Print formatted weather
        # print("\nFormatted Current Weather:")
        # print(weather.format_current_weather(current_weather, "Medellin", "CO"))
        
        # # Print formatted forecast
        # print("\nFormatted Forecast:")
        # print(weather.format_forecast(forecast, "Medellin", "CO"))

        
