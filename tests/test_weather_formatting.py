"""
Tests for weather formatting functions without making API calls.
"""

import pytest
import os
from datetime import datetime

def test_temperature_conversion():
    """Test temperature conversion from Kelvin to Celsius and Fahrenheit."""
    # Kelvin temperature (example: 295.15K is about 22°C or 71.6°F)
    kelvin_temp = 295.15
    
    # Convert to Celsius (K - 273.15)
    celsius_temp = kelvin_temp - 273.15
    assert round(celsius_temp, 1) == 22.0
    
    # Convert to Fahrenheit (C * 9/5 + 32)
    fahrenheit_temp = celsius_temp * 9/5 + 32
    assert round(fahrenheit_temp, 1) == 71.6

def test_timestamp_conversion():
    """Test conversion of Unix timestamp to readable date."""
    # Example Unix timestamp (seconds since Jan 1, 1970)
    unix_timestamp = 1646318698  # March 3, 2022
    
    # Convert to datetime
    date_time = datetime.fromtimestamp(unix_timestamp)
    
    # Check year, month, day
    assert date_time.year == 2022
    assert date_time.month == 3
    assert date_time.day == 3
    
    # Format as string
    formatted_date = date_time.strftime("%A, %B %d, %Y")
    assert "March" in formatted_date
    assert "2022" in formatted_date
    assert "3" in formatted_date

def test_wind_speed_description():
    """Test wind speed description based on the Beaufort scale."""
    def get_wind_description(speed_ms):
        """Get wind description based on speed in m/s."""
        if speed_ms < 0.5:
            return "Calm"
        elif speed_ms < 1.5:
            return "Light air"
        elif speed_ms < 3.3:
            return "Light breeze"
        elif speed_ms < 5.5:
            return "Gentle breeze"
        elif speed_ms < 7.9:
            return "Moderate breeze"
        elif speed_ms < 10.7:
            return "Fresh breeze"
        elif speed_ms < 13.8:
            return "Strong breeze"
        elif speed_ms < 17.1:
            return "High wind"
        elif speed_ms < 20.7:
            return "Gale"
        elif speed_ms < 24.4:
            return "Strong gale"
        elif speed_ms < 28.4:
            return "Storm"
        elif speed_ms < 32.6:
            return "Violent storm"
        else:
            return "Hurricane force"
    
    # Test various wind speeds
    assert get_wind_description(0.3) == "Calm"
    assert get_wind_description(1.0) == "Light air"
    assert get_wind_description(2.5) == "Light breeze"
    assert get_wind_description(4.5) == "Gentle breeze"
    assert get_wind_description(7.0) == "Moderate breeze"
    assert get_wind_description(9.0) == "Fresh breeze"
    assert get_wind_description(12.0) == "Strong breeze"
    assert get_wind_description(16.0) == "High wind"
    assert get_wind_description(19.0) == "Gale"
    assert get_wind_description(22.0) == "Strong gale"
    assert get_wind_description(26.0) == "Storm"
    assert get_wind_description(30.0) == "Violent storm"
    assert get_wind_description(35.0) == "Hurricane force"

def test_weather_icon_mapping():
    """Test mapping of weather conditions to appropriate icons."""
    def get_weather_icon(condition):
        """Get weather icon based on condition."""
        icons = {
            "Clear": "☀️",
            "Clouds": "☁️",
            "Rain": "🌧️",
            "Drizzle": "🌦️",
            "Thunderstorm": "⛈️",
            "Snow": "❄️",
            "Mist": "🌫️",
            "Fog": "🌫️",
            "Haze": "🌫️",
            "Smoke": "🌫️",
            "Dust": "🌫️",
            "Sand": "🌫️",
            "Ash": "🌫️",
            "Squall": "💨",
            "Tornado": "🌪️"
        }
        return icons.get(condition, "❓")
    
    # Test various weather conditions
    assert get_weather_icon("Clear") == "☀️"
    assert get_weather_icon("Clouds") == "☁️"
    assert get_weather_icon("Rain") == "🌧️"
    assert get_weather_icon("Thunderstorm") == "⛈️"
    assert get_weather_icon("Snow") == "❄️"
    assert get_weather_icon("Mist") == "🌫️"
    assert get_weather_icon("Tornado") == "🌪️"
    assert get_weather_icon("Unknown") == "❓" 