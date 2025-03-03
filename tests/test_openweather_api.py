import pytest
from unittest.mock import patch, MagicMock
import requests
from openweather_api import OpenWeather

class TestOpenWeatherAPI:
    """Tests for the OpenWeather API client."""
    
    @pytest.fixture
    def openweather(self):
        """Create an instance of the OpenWeather client."""
        return OpenWeather()
    
    @patch("openweather_api.requests.get")
    def test_get_geolocation_success(self, mock_get, openweather):
        """Test getting geolocation with successful API response."""
        # Setup
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"name": "London", "lat": 51.5074, "lon": -0.1278, "country": "GB"}
        ]
        mock_get.return_value = mock_response
        
        # Execute
        result = openweather.get_geolocation("London")
        
        # Assert
        assert result == [{"name": "London", "lat": 51.5074, "lon": -0.1278, "country": "GB"}]
        mock_get.assert_called_once()
        
    @patch("openweather_api.requests.get")
    def test_get_geolocation_not_found(self, mock_get, openweather):
        """Test getting geolocation with no results."""
        # Setup
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response
        
        # Execute
        result = openweather.get_geolocation("NonExistentCity")
        
        # Assert
        assert result == []
        mock_get.assert_called_once()
        
    @patch("openweather_api.requests.get")
    def test_get_geolocation_api_error(self, mock_get, openweather):
        """Test getting geolocation with API error."""
        # Setup
        mock_get.side_effect = requests.RequestException("API error")
        
        # Execute
        result = openweather.get_geolocation("London")
        
        # Assert
        assert result == []
        mock_get.assert_called_once()
        
    @patch("openweather_api.requests.get")
    def test_get_current_weather_success(self, mock_get, openweather):
        """Test getting current weather with successful API response."""
        # Setup
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "main": {"temp": 15.5, "feels_like": 14.8, "humidity": 76},
            "weather": [{"main": "Clouds", "description": "scattered clouds"}],
            "wind": {"speed": 3.6},
            "dt": 1646318698,
            "name": "London"
        }
        mock_get.return_value = mock_response
        
        # Execute
        result = openweather.get_current_weather(51.5074, -0.1278)
        
        # Assert
        assert result["main"]["temp"] == 15.5
        assert result["weather"][0]["description"] == "scattered clouds"
        mock_get.assert_called_once()
        
    @patch("openweather_api.requests.get")
    def test_get_current_weather_api_error(self, mock_get, openweather):
        """Test getting current weather with API error."""
        # Setup
        mock_get.side_effect = requests.RequestException("API error")
        
        # Execute
        result = openweather.get_current_weather(51.5074, -0.1278)
        
        # Assert
        assert result is None
        mock_get.assert_called_once()
        
    @patch("openweather_api.requests.get")
    def test_get_weather_forecast_success(self, mock_get, openweather):
        """Test getting weather forecast with successful API response."""
        # Setup
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "list": [
                {
                    "dt": 1646319600,
                    "main": {"temp": 15.5, "feels_like": 14.8, "humidity": 76},
                    "weather": [{"main": "Clouds", "description": "scattered clouds"}],
                    "wind": {"speed": 3.6},
                    "dt_txt": "2023-03-03 12:00:00"
                },
                {
                    "dt": 1646330400,
                    "main": {"temp": 14.2, "feels_like": 13.5, "humidity": 82},
                    "weather": [{"main": "Rain", "description": "light rain"}],
                    "wind": {"speed": 4.1},
                    "dt_txt": "2023-03-03 15:00:00"
                }
            ],
            "city": {"name": "London", "country": "GB"}
        }
        mock_get.return_value = mock_response
        
        # Execute
        result = openweather.get_weather_forecast(51.5074, -0.1278)
        
        # Assert
        assert len(result["list"]) == 2
        assert result["list"][0]["main"]["temp"] == 15.5
        assert result["list"][1]["weather"][0]["main"] == "Rain"
        mock_get.assert_called_once()
        
    @patch("openweather_api.requests.get")
    def test_get_weather_forecast_api_error(self, mock_get, openweather):
        """Test getting weather forecast with API error."""
        # Setup
        mock_get.side_effect = requests.RequestException("API error")
        
        # Execute
        result = openweather.get_weather_forecast(51.5074, -0.1278)
        
        # Assert
        assert result is None
        mock_get.assert_called_once() 