#!/usr/bin/env python
"""
Test Runner Script for the Weather Agent

This script provides a convenient way to run tests for the Weather Agent project.
It supports running all tests, specific test files, or tests with specific markers.

Usage:
    python run_tests.py [options]

Options:
    --unit           Run only unit tests
    --integration    Run only integration tests
    --api            Run only API tests
    --file FILE      Run tests in the specified file
    --verbose        Show verbose output
    --coverage       Generate coverage report
    --html           Generate HTML coverage report
    --help           Show this help message
"""

import sys
import os
import subprocess
import argparse
import importlib.util

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def is_package_installed(package_name):
    """Check if a package is installed."""
    return importlib.util.find_spec(package_name) is not None

def install_package(package_name):
    """Install a package using pip."""
    print(f"Installing {package_name}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

def ensure_dependencies():
    """Ensure all required dependencies are installed."""
    required_packages = {
        "pytest": "pytest",
        "pytest_cov": "pytest-cov",
    }
    
    missing_packages = []
    for module_name, package_name in required_packages.items():
        if not is_package_installed(module_name):
            missing_packages.append(package_name)
    
    if missing_packages:
        print("Some required packages are missing. Installing them now...")
        for package in missing_packages:
            install_package(package)
        print("All required packages installed successfully.")

def main():
    """Run the tests based on command line arguments."""
    # Ensure dependencies are installed
    ensure_dependencies()
    
    parser = argparse.ArgumentParser(description="Run tests for the Weather Agent")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--api", action="store_true", help="Run only API tests")
    parser.add_argument("--file", type=str, help="Run tests in the specified file")
    parser.add_argument("--verbose", action="store_true", help="Show verbose output")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--html", action="store_true", help="Generate HTML coverage report")
    
    args = parser.parse_args()
    
    # Build the pytest command
    cmd = ["pytest"]
    
    # Add verbosity
    if args.verbose:
        cmd.append("-v")
    
    # Add coverage
    if args.coverage or args.html:
        cmd.append("--cov=.")
        
    # Add HTML coverage report
    if args.html:
        cmd.append("--cov-report=html")
    elif args.coverage:
        cmd.append("--cov-report=term-missing")
    
    # Add test markers
    if args.unit:
        cmd.append("-m")
        cmd.append("unit")
    elif args.integration:
        cmd.append("-m")
        cmd.append("integration")
    elif args.api:
        cmd.append("-m")
        cmd.append("api")
    
    # Add specific file
    if args.file:
        cmd.append(f"tests/test_{args.file}.py")
    
    # Print the command being run
    print(f"Running: {' '.join(cmd)}")
    
    # Run the tests
    result = subprocess.run(cmd)
    
    # Return the exit code
    return result.returncode

if __name__ == "__main__":
    sys.exit(main()) 