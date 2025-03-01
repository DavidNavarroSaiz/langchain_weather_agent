# Weather Agent Streamlit App

This is a Streamlit frontend for the Weather Agent API. It provides a user-friendly interface for interacting with the weather agent, including user authentication, chat functionality, and chat history management.

## Features

- **User Authentication**: Sign up, log in, and log out functionality
- **Chat Interface**: Send queries to the weather agent and view responses
- **Chat History**: View and clear your chat history
- **Responsive Design**: Works on desktop and mobile devices

## Prerequisites

- Python 3.8 or higher
- FastAPI backend running (see instructions below)
- Required Python packages (install using `pip install -r requirements.txt`)
- Streamlit version 1.30.0 or higher

## Setup and Running

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Option 1: Run Both Servers with a Single Command (Recommended)

The easiest way to run the application is to use the provided run script:

```bash
python run_app.py
```

This will:
- Start the FastAPI backend
- Start the Streamlit frontend
- Open your browser automatically
- Show logs from both servers in a single terminal

### 3. Option 2: Run Servers Separately

If you prefer to run the servers separately:

#### Start the FastAPI Backend

```bash
python app.py
```

This will start the backend server at http://localhost:8000.

#### Start the Streamlit Frontend

In a separate terminal, run:

```bash
streamlit run streamlit_app.py
```

This will start the Streamlit app and automatically open it in your default web browser (typically at http://localhost:8501).

## Usage

1. **Sign Up**: Create a new account with a username and password
2. **Log In**: Log in with your credentials
3. **Chat**: Ask questions about the weather (e.g., "What's the weather like in London today?")
4. **View History**: See your chat history in the main chat window
5. **Clear History**: Use the "Clear Chat History" button in the sidebar to delete your chat history
6. **Log Out**: Use the "Logout" button in the sidebar when you're done

## Configuration

By default, the app connects to a FastAPI backend running at `http://localhost:8000`. If your backend is running at a different URL, update the `API_URL` variable in `streamlit_app.py`.

## Example Queries

- "What's the weather like in New York today?"
- "Will it rain in London tomorrow?"
- "What's the temperature in Tokyo right now?"
- "What's the forecast for Paris for the next 5 days?"
- "Is it sunny in Miami today?"

## Troubleshooting

- **Authentication Issues**: Make sure the FastAPI backend is running and accessible
- **Connection Errors**: Check that the `API_URL` in `streamlit_app.py` matches your FastAPI server URL
- **Missing Dependencies**: Ensure all required packages are installed using `pip install -r requirements.txt`
- **Streamlit Errors**: If you see errors related to `st.experimental_rerun()`, make sure you have Streamlit version 1.30.0 or higher installed 