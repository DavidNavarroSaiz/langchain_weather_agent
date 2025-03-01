"""
Run Script for Weather Agent Application

This script starts both the FastAPI backend and Streamlit frontend simultaneously.
It uses subprocess to run both servers in parallel.

Note: This script requires Streamlit version 1.30.0 or higher.
"""

import subprocess
import sys
import time
import webbrowser
import os
from threading import Timer

def open_browser(url):
    """Open the browser after a delay to ensure the server is running."""
    webbrowser.open(url)

def main():
    """Start both the FastAPI backend and Streamlit frontend."""
    print("Starting Weather Agent Application...")
    
    # Check if Python is in the path
    python_cmd = sys.executable
    
    # Start FastAPI backend
    print("\n=== Starting FastAPI Backend ===")
    backend_process = subprocess.Popen(
        [python_cmd, "app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    # Wait for backend to start
    print("Waiting for backend to start...")
    time.sleep(3)
    
    # Start Streamlit frontend
    print("\n=== Starting Streamlit Frontend ===")
    try:
        frontend_process = subprocess.Popen(
            [python_cmd, "-m", "streamlit", "run", "streamlit_app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
    except Exception as e:
        print(f"Error starting Streamlit: {str(e)}")
        print("Make sure Streamlit is installed: pip install streamlit>=1.30.0")
        backend_process.terminate()
        sys.exit(1)
    
    # Open browser after a delay
    Timer(5, open_browser, ["http://localhost:8501"]).start()
    
    print("\n=== Weather Agent Application Started ===")
    print("FastAPI Backend: http://localhost:8000")
    print("Streamlit Frontend: http://localhost:8501")
    print("\nPress Ctrl+C to stop both servers\n")
    
    try:
        # Keep the script running and print output from both processes
        while True:
            # Check if processes are still running
            if backend_process.poll() is not None:
                backend_error = backend_process.stderr.read()
                print(f"Backend process has terminated unexpectedly")
                if backend_error:
                    print(f"Backend error: {backend_error}")
                break
                
            if frontend_process.poll() is not None:
                frontend_error = frontend_process.stderr.read()
                print(f"Frontend process has terminated unexpectedly")
                if frontend_error:
                    print(f"Frontend error: {frontend_error}")
                break
                
            # Print any output from the processes
            backend_out = backend_process.stdout.readline()
            if backend_out:
                print(f"[Backend] {backend_out.strip()}")
                
            frontend_out = frontend_process.stdout.readline()
            if frontend_out:
                print(f"[Frontend] {frontend_out.strip()}")
                
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        
    finally:
        # Terminate both processes
        if backend_process.poll() is None:
            backend_process.terminate()
            
        if frontend_process.poll() is None:
            frontend_process.terminate()
            
        print("Servers shut down successfully")

if __name__ == "__main__":
    main() 