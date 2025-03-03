import os
import sys
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables
load_dotenv()

# Import app after environment variables are loaded
from app import app
from weather_agent import create_weather_agent
from openweather_api import OpenWeather
from user_manager import UserManager
from memory_handler import MongoDBConversationMemory

@pytest.fixture
def test_client():
    """
    Create a test client for the FastAPI app.
    """
    with TestClient(app) as client:
        yield client

@pytest.fixture
def mock_openweather():
    """
    Create a mock for the OpenWeather API client.
    """
    with patch("weather_agent.OpenWeather") as mock:
        mock_instance = MagicMock()
        mock.return_value = mock_instance
        
        # Mock geolocation response
        mock_instance.get_geolocation.return_value = [
            {"name": "London", "lat": 51.5074, "lon": -0.1278, "country": "GB"}
        ]
        
        # Mock current weather response
        mock_instance.get_current_weather.return_value = {
            "main": {"temp": 15.5, "feels_like": 14.8, "humidity": 76},
            "weather": [{"main": "Clouds", "description": "scattered clouds"}],
            "wind": {"speed": 3.6},
            "dt": 1646318698,
            "name": "London"
        }
        
        # Mock forecast response
        mock_instance.get_weather_forecast.return_value = {
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
        
        yield mock_instance

@pytest.fixture
def mock_user_manager():
    """
    Create a mock for the UserManager.
    """
    with patch("app.UserManager") as mock:
        mock_instance = MagicMock()
        mock.return_value = mock_instance
        
        # Mock user verification
        mock_instance.verify_user.return_value = True
        
        # Mock user creation
        mock_instance.create_user.return_value = {"username": "testuser", "created_at": "2023-03-03T12:00:00"}
        
        yield mock_instance

@pytest.fixture
def mock_memory():
    """
    Create a mock for the MongoDB conversation memory.
    """
    with patch("weather_agent.MongoDBConversationMemory") as mock:
        mock_instance = MagicMock()
        mock.return_value = mock_instance
        
        # Mock chat history
        mock_instance.get_chat_history.return_value = [
            {"type": "human", "content": "What's the weather like in London?"},
            {"type": "ai", "content": "The current weather in London is cloudy with a temperature of 15.5°C."}
        ]
        
        yield mock_instance

@pytest.fixture
def test_user_token():
    """
    Create a test JWT token for authentication.
    """
    # This is a dummy token for testing purposes
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlciIsImV4cCI6OTk5OTk5OTk5OX0.mock_signature" 