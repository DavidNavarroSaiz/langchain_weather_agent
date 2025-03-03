"""
Simple tests that don't depend on external services.
These tests can be run without mocking external dependencies.
"""

import os
import pytest



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