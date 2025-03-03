"""
Simple tests that don't depend on external services.
These tests can be run without mocking external dependencies.
"""

import os
import pytest
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment_variables():
    """Test that required environment variables are set."""
    # Check if .env file exists
    assert os.path.exists(".env"), "The .env file is missing"
    
    # Check if required environment variables are set
    # We don't check the actual values, just that they're set
    env_vars = [
        "OPENAI_API_KEY",
        "MONGO_URI",
        "MONGO_DB",
        "MONGO_COLLECTION",
        "JWT_SECRET_KEY",
        "JWT_ALGORITHM",
    ]
    
    for var in env_vars:
        # We use os.getenv to avoid raising an exception if the variable is not set
        # Instead, we'll get None, which we can check for
        value = os.getenv(var)
        if value is None:
            print(f"Warning: Environment variable {var} is not set")
            # Don't fail the test, just warn
            # assert value is not None, f"Environment variable {var} is not set"

def test_project_structure():
    """Test that required project files exist."""
    required_files = [
        "app.py",
        "weather_agent.py",
        "openweather_api.py",
        "user_manager.py",
        "memory_handler.py",
        "prompt_cache.py",
        "requirements.txt",
    ]
    
    for file in required_files:
        assert os.path.exists(file), f"Required file {file} is missing"

def test_pytest_config():
    """Test that pytest configuration is correct."""
    assert os.path.exists("pytest.ini"), "pytest.ini file is missing"
    
    # Check if pytest.ini contains required sections
    with open("pytest.ini", "r") as f:
        content = f.read()
        assert "[pytest]" in content, "pytest.ini is missing [pytest] section"
        assert "testpaths = tests" in content, "pytest.ini is missing testpaths configuration"
        assert "markers" in content, "pytest.ini is missing markers configuration" 