"""
Basic utility tests that don't require complex mocking.
"""

import os
import pytest
from datetime import datetime

def test_date_formatting():
    """Test simple date formatting."""
    # Get today's date
    today = datetime.now()
    
    # Format it as a string
    formatted_date = today.strftime("%A, %B %d, %Y")
    
    # Check that the format is correct
    assert isinstance(formatted_date, str)
    assert len(formatted_date) > 10  # Basic length check
    assert today.strftime("%Y") in formatted_date  # Year should be in the string

def test_environment_setup():
    """Test that the environment is set up correctly."""
    # Check that we're in the right directory
    assert os.path.exists("requirements.txt"), "Not in the project root directory"
    
    # Check that the tests directory exists
    assert os.path.exists("tests"), "Tests directory not found"
    
    # Check that the .env file exists
    assert os.path.exists(".env"), ".env file not found"

def test_requirements_file():
    """Test that the requirements.txt file contains essential packages."""
    with open("requirements.txt", "r") as f:
        requirements = f.read()
    
    # Check for essential packages
    essential_packages = [
        "python-dotenv",
        "requests",
        "langchain",
        "fastapi",
        "pytest"
    ]
    
    for package in essential_packages:
        assert package in requirements, f"{package} not found in requirements.txt"

def test_simple_math():
    """Test simple math operations to verify pytest is working."""
    assert 1 + 1 == 2
    assert 10 - 5 == 5
    assert 3 * 4 == 12
    assert 10 / 2 == 5 