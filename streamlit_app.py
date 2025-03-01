"""
Weather Agent Streamlit App - UI Enhanced Version

A Streamlit-based chat application for interacting with the Weather Agent API.
Features:
- User authentication
- Real-time chat with AI
- Chat history management
- Streamed responses for a smoother experience
"""

import streamlit as st
import requests
import json
from datetime import datetime

# API Configuration - Adjust to your FastAPI server
API_URL = "http://localhost:8000"

# Set up Streamlit page
st.set_page_config(
    page_title="Weather Agent Chat",
    page_icon="🌤️",
    layout="centered",
)

# Custom styling for chat bubbles
st.markdown("""
    <style>
        .stChatInput { background-color: #1F2937 !important; color: white; }
        .stChatMessageUser { background-color: #3B82F6 !important; color: white; }
        .stChatMessageBot { background-color: #10B981 !important; color: white; }
    </style>
""", unsafe_allow_html=True)

# Initialize session state variables
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "access_token" not in st.session_state:
    st.session_state.access_token = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

def login(username, password):
    """Authenticate user via API."""
    try:
        response = requests.post(f"{API_URL}/token", data={"username": username, "password": password})
        if response.status_code == 200:
            data = response.json()
            st.session_state.access_token = data["access_token"]
            st.session_state.username = username
            st.session_state.authenticated = True
            fetch_chat_history()
            return True
        else:
            return False
    except Exception as e:
        st.error(f"Login error: {e}")
        return False

def signup(username, password):
    """Register new user via API."""
    try:
        response = requests.post(f"{API_URL}/signup", json={"username": username, "password": password})
        return response.status_code == 201
    except Exception as e:
        st.error(f"Signup error: {e}")
        return False

def logout():
    """Logout user and clear session state."""
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.access_token = ""
    st.session_state.messages = []
    st.rerun()

def send_message(query):
    """Send user query to API and return response."""
    if not query.strip():
        return None

    headers = {"Authorization": f"Bearer {st.session_state.access_token}", "Content-Type": "application/json"}
    
    try:
        response = requests.post(f"{API_URL}/api/chat", headers=headers, json={"query": query})
        if response.status_code == 200:
            return response.json()["response"]
        else:
            st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
            if response.status_code == 401:
                logout()
            return None
    except Exception as e:
        st.error(f"Error sending message: {e}")
        return None

def fetch_chat_history():
    """Retrieve chat history from API."""
    if not st.session_state.authenticated:
        return

    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
    
    try:
        response = requests.get(f"{API_URL}/chat-history", headers=headers)
        if response.status_code == 200:
            st.session_state.messages = response.json()["messages"]
        else:
            st.error(f"Error fetching chat history: {response.json().get('detail', 'Unknown error')}")
            if response.status_code == 401:
                logout()
    except Exception as e:
        st.error(f"Error fetching chat history: {e}")

# Login Page
def login_page():
    """Render login interface."""
    st.title("🌤️ Weather Agent Login")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")
        signup_button = st.form_submit_button("Sign Up")

    if login_button and username and password:
        if login(username, password):
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid username or password.")

    if signup_button and username and password:
        if signup(username, password):
            st.success("Account created successfully! You can now log in.")
        else:
            st.error("Signup failed. Username may already exist.")

# Chat Page
def chat_page():
    """Render the chat interface."""
    st.title("🌤️ Weather Agent Chat")

    # Sidebar
    with st.sidebar:
        st.write(f"Logged in as: **{st.session_state.username}**")
        if st.button("Logout"):
            logout()
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.success("Chat history cleared!")

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input
    user_input = st.chat_input("Ask about the weather:")
    
    if user_input:
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Get response from API
        response = send_message(user_input)

        if response:
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

# Main Application
def main():
    """Main app logic."""
    if not st.session_state.authenticated:
        login_page()
    else:
        chat_page()

if __name__ == "__main__":
    main()
