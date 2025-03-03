import requests
import os
from dotenv import load_dotenv
import datetime
from logger_config import setup_logger

# Load environment variables from .env file
load_dotenv()

# Set up logger
logger = setup_logger(__name__)


class OpenWeather:
    """
    Client for interacting with the OpenWeather API.
    
    This class provides methods to fetch weather data, forecasts, and geolocation
    information from the OpenWeather API, as well as formatting the responses
    into human-readable formats.
    """
    BASE_URL = os.getenv("OPENWEATHER_BASE_URL")
    GEO_URL = os.getenv("OPENWEATHER_GEO_URL")
    FORECAST_URL = os.getenv("OPENWEATHER_FORECAST_URL")
    MAP_URL = os.getenv("OPENWEATHER_MAP_URL")

    def __init__(self):
        """Initialize the OpenWeather client with API key from environment variables."""
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        if not self.api_key:
            logger.error(
                "OpenWeather API key not found in environment variables")
        logger.debug("OpenWeather client initialized")

    def get_geolocation(self, city_name, country_code=None, state_code=None, limit=1):
        """
        Get geolocation data for a city.
        
        Args:
            city_name (str): Name of the city
            country_code (str, optional): Two-letter country code
            state_code (str, optional): State code (mainly for US locations)
            limit (int, optional): Maximum number of results to return
            
        Returns:
            list: List of geolocation data (empty list if the request failed)
        """
        params = {
            "q": f"{city_name},{state_code},{country_code}" if state_code and country_code else city_name,
            "limit": limit,
            "appid": self.api_key
        }
        logger.debug(f"Getting geolocation for {city_name}")
        try:
            response = requests.get(self.GEO_URL, params=params)
            if response.status_code == 200:
                logger.info(
                    f"Successfully retrieved geolocation for {city_name}")
                return response.json()
            else:
                logger.warning(
                    f"Failed to get geolocation for {city_name}: {response.status_code}")
                return []
        except Exception as e:
            logger.error(
                f"Error getting geolocation for {city_name}: {str(e)}")
            return []

    def get_current_weather(self, lat, lon, units="metric", lang="en"):
        """
        Get current weather data for a location.
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            units (str, optional): Units of measurement ('metric', 'imperial', or 'standard')
            lang (str, optional): Language code for the response
            
        Returns:
            dict or None: Weather data or None if the request failed
        """
        params = {
            "lat": lat,
            "lon": lon,
            "units": units,
            "lang": lang,
            "appid": self.api_key
        }
        logger.debug(f"Getting current weather for coordinates: {lat}, {lon}")
        try:
            response = requests.get(self.BASE_URL, params=params)
            if response.status_code == 200:
                logger.info(
                    f"Successfully retrieved current weather for coordinates: {lat}, {lon}")
                return response.json()
            else:
                logger.warning(
                    f"Failed to get current weather: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error getting current weather: {str(e)}")
            return None

    def get_forecast(self, lat, lon, units="metric", lang="en", cnt=40):
        """
        Get weather forecast for a location.
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            units (str, optional): Units of measurement ('metric', 'imperial', or 'standard')
            lang (str, optional): Language code for the response
            cnt (int, optional): Number of timestamps to return (max 40)
            
        Returns:
            dict or None: Forecast data or None if the request failed
        """
        params = {
            "lat": lat,
            "lon": lon,
            "units": units,
            "lang": lang,
            "cnt": cnt,
            "appid": self.api_key
        }
        logger.debug(f"Getting forecast for coordinates: {lat}, {lon}")
        try:
            response = requests.get(self.FORECAST_URL, params=params)
            if response.status_code == 200:
                logger.info(
                    f"Successfully retrieved forecast for coordinates: {lat}, {lon}")
                return response.json()
            else:
                logger.warning(
                    f"Failed to get forecast: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error getting forecast: {str(e)}")
            return None

    def get_weather_forecast(self, lat, lon, units="metric", lang="en", cnt=40):
        """
        Alias for get_forecast method.
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            units (str, optional): Units of measurement ('metric', 'imperial', or 'standard')
            lang (str, optional): Language code for the response
            cnt (int, optional): Number of timestamps to return (max 40)
            
        Returns:
            dict or None: Forecast data or None if the request failed
        """
        return self.get_forecast(lat, lon, units, lang, cnt)

    def get_weather_map_url(self, layer, z, x, y):
        """
        Get URL for a weather map tile.
        
        Args:
            layer (str): Map layer type
            z (int): Zoom level
            x (int): X coordinate
            y (int): Y coordinate
            
        Returns:
            str: URL for the requested map tile
        """
        return f"{self.MAP_URL}/{layer}/{z}/{x}/{y}.png?appid={self.api_key}"

    def _get_wind_direction(self, degrees):
        """
        Convert wind direction in degrees to cardinal direction.
        
        Args:
            degrees (float): Wind direction in degrees
            
        Returns:
            str: Cardinal direction (N, NE, E, etc.)
        """
        directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                      "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        index = round(degrees / (360 / len(directions))) % len(directions)
        return directions[index]

    def _get_weather_emoji(self, weather_main):
        """
        Get emoji for weather condition.
        
        Args:
            weather_main (str): Main weather condition from API
            
        Returns:
            str: Emoji representing the weather condition
        """
        weather_emojis = {
            "Clear": "☀️",
            "Clouds": "☁️",
            "Rain": "🌧️",
            "Drizzle": "🌦️",
            "Thunderstorm": "⛈️",
            "Snow": "❄️",
            "Mist": "🌫️",
            "Smoke": "🌫️",
            "Haze": "🌫️",
            "Dust": "🌫️",
            "Fog": "🌫️",
            "Sand": "🌫️",
            "Ash": "🌫️",
            "Squall": "💨",
            "Tornado": "🌪️"
        }
        return weather_emojis.get(weather_main, "🌡️")

    def format_current_weather(self, weather_data, city_name, country_code=None):
        """
        Format current weather data into a human-readable string.
        
        Args:
            weather_data (dict): Weather data from the OpenWeather API
            city_name (str): Name of the city
            country_code (str, optional): Two-letter country code
            
        Returns:
            str: Formatted weather information
        """
        logger.debug(f"Formatting current weather data for {city_name}")
        try:
            # Extract data
            location_name = f"{city_name}, {country_code.upper()}" if country_code else city_name
            temp = weather_data["main"]["temp"]
            feels_like = weather_data["main"]["feels_like"]
            temp_min = weather_data["main"]["temp_min"]
            temp_max = weather_data["main"]["temp_max"]
            humidity = weather_data["main"]["humidity"]
            pressure = weather_data["main"]["pressure"]
            wind_speed = weather_data["wind"]["speed"]
            wind_deg = weather_data["wind"]["deg"]
            clouds = weather_data["clouds"]["all"]
            weather_desc = weather_data["weather"][0]["description"]
            weather_main = weather_data["weather"][0]["main"]

            # Get weather emoji
            weather_emoji = self._get_weather_emoji(weather_main)

            # Format the response
            response = f"""
                ## Current Weather for {location_name} {weather_emoji}

                **Conditions:** {weather_desc.capitalize()}
                **Temperature:** {temp}°C (Feels like: {feels_like}°C)
                **Range:** {temp_min}°C to {temp_max}°C
                **Humidity:** {humidity}%
                **Pressure:** {pressure} hPa
                **Wind:** {wind_speed} m/s at {self._get_wind_direction(wind_deg)}
                **Cloud Cover:** {clouds}%
                            """

            # Add sunrise and sunset if available
            if "sys" in weather_data and "sunrise" in weather_data["sys"] and "sunset" in weather_data["sys"]:
                sunrise = datetime.datetime.fromtimestamp(
                    weather_data["sys"]["sunrise"]).strftime("%H:%M")
                sunset = datetime.datetime.fromtimestamp(
                    weather_data["sys"]["sunset"]).strftime("%H:%M")
                response += f"""
**Sunrise:** {sunrise}
**Sunset:** {sunset}
                """

            # Add visibility if available
            if "visibility" in weather_data:
                visibility_km = weather_data["visibility"] / 1000
                response += f"**Visibility:** {visibility_km:.1f} km\n"

            # Add rain data if available
            if "rain" in weather_data:
                if "1h" in weather_data["rain"]:
                    response += f"**Rain (1h):** {weather_data['rain']['1h']} mm\n"
                if "3h" in weather_data["rain"]:
                    response += f"**Rain (3h):** {weather_data['rain']['3h']} mm\n"

            # Add snow data if available
            if "snow" in weather_data:
                if "1h" in weather_data["snow"]:
                    response += f"**Snow (1h):** {weather_data['snow']['1h']} mm\n"
                if "3h" in weather_data["snow"]:
                    response += f"**Snow (3h):** {weather_data['snow']['3h']} mm\n"

            logger.info(
                f"Successfully formatted current weather data for {city_name}")
            return response
        except Exception as e:
            logger.error(f"Error formatting current weather data: {str(e)}")
            return f"Error formatting weather data: {str(e)}"

    def format_forecast(self, forecast_data, city_name, country_code=None):
        """
        Format forecast data into a human-readable string.
        
        Args:
            forecast_data (dict): Forecast data from the OpenWeather API
            city_name (str): Name of the city
            country_code (str, optional): Two-letter country code
            
        Returns:
            str: Formatted forecast information
        """
        logger.debug(f"Formatting forecast data for {city_name}")
        try:
            # Extract data
            forecast_list = forecast_data.get("list", [])
            location_name = f"{city_name}, {country_code.upper()}" if country_code else city_name

            # Format the header
            result = f"## 5-Day Weather Forecast for {location_name}\n\n"

            # Group forecasts by day
            forecasts_by_day = {}
            for forecast in forecast_list:
                # Get date from timestamp
                dt = datetime.datetime.fromtimestamp(forecast["dt"])
                date_str = dt.strftime("%Y-%m-%d")
                time_str = dt.strftime("%H:%M")

                # Initialize day if not exists
                if date_str not in forecasts_by_day:
                    forecasts_by_day[date_str] = []

                # Add forecast to day
                forecasts_by_day[date_str].append({
                    "time": time_str,
                    "temp": forecast["main"]["temp"],
                    "feels_like": forecast["main"]["feels_like"],
                    "description": forecast["weather"][0]["description"],
                    "main": forecast["weather"][0]["main"],
                    "humidity": forecast["main"]["humidity"],
                    "wind_speed": forecast["wind"]["speed"],
                    "wind_deg": forecast["wind"]["deg"],
                    "rain": forecast.get("rain", {}).get("3h", 0) if "rain" in forecast else 0,
                    "snow": forecast.get("snow", {}).get("3h", 0) if "snow" in forecast else 0
                })

            # Format each day
            for date_str, forecasts in sorted(forecasts_by_day.items()):
                # Convert date string to datetime for better formatting
                date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                day_name = date_obj.strftime("%A")

                # Add day header
                result += f"### {day_name}, {date_obj.strftime('%B %d')}\n\n"

                # Add each forecast for the day
                for forecast in forecasts:
                    # Get weather emoji
                    weather_emoji = self._get_weather_emoji(forecast["main"])

                    result += f"**{forecast['time']}** {weather_emoji} {forecast['description'].capitalize()}\n"
                    result += f"🌡️ Temp: {forecast['temp']}°C (Feels like: {forecast['feels_like']}°C)\n"
                    result += f"💧 Humidity: {forecast['humidity']}%\n"
                    result += f"💨 Wind: {forecast['wind_speed']} m/s at {self._get_wind_direction(forecast['wind_deg'])}\n"

                    # Add rain and snow if present
                    if forecast["rain"]:
                        result += f"🌧️ Rain: {forecast['rain']} mm\n"
                    if forecast["snow"]:
                        result += f"❄️ Snow: {forecast['snow']} mm\n"

                    result += "\n"

            logger.info(
                f"Successfully formatted forecast data for {city_name}")
            return result
        except Exception as e:
            logger.error(f"Error formatting forecast data: {str(e)}")
            return f"Error formatting forecast data: {str(e)}"


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
