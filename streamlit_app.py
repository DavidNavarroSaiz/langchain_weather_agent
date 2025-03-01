"""
Weather Agent Streamlit App

This module provides a Streamlit-based web interface for interacting with the 
Weather Agent API. It includes features for user authentication, chat interactions,
and chat history management.
"""

import streamlit as st
import requests
import json
from datetime import datetime

# API URL - Change this to your FastAPI server URL when deploying
API_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="Weather Agent",
    page_icon="🌤️",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling - ChatGPT-like interface with dark theme
st.markdown("""
<style>
    /* Global background and text colors */
    .stApp {
        background-color: #111827;
        color: #E5E7EB;
    }
    
    /* Sidebar styling */
    .css-1d391kg, .css-1cypcdb {
        background-color: #1F2937;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #E5E7EB;
    }
    
    /* Chat message styling */
    .chat-message {
        padding: 1.5rem; 
        border-radius: 0.5rem; 
        margin-bottom: 1rem; 
        display: flex;
        flex-direction: column;
    }
    .chat-message.user {
        background-color: #1F2937;
        border-left: 5px solid #3B82F6;
    }
    .chat-message.bot {
        background-color: #111827;
        border-left: 5px solid #10B981;
    }
    .chat-message .message-content {
        margin-top: 0;
        color: #E5E7EB;
    }
    .chat-message .timestamp {
        font-size: 0.8rem;
        color: #9CA3AF;
        margin-top: 0.5rem;
        align-self: flex-end;
    }
    
    /* Button styling */
    .stButton button {
        width: 100%;
        background-color: #3B82F6;
        color: white;
        border: none;
    }
    .stButton button:hover {
        background-color: #2563EB;
    }
    
    /* Form styling */
    .stForm {
        background-color: #1F2937;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    
    /* Input field styling */
    .stTextInput input {
        background-color: #1F2937;
        border: 1px solid #374151;
        border-radius: 4px;
        color: #E5E7EB;
    }
    
    /* Placeholder text */
    .stTextInput input::placeholder {
        color: #9CA3AF;
    }
    
    /* Info message */
    .stAlert {
        background-color: #1F2937;
        color: #E5E7EB;
    }
    
    /* Success message */
    .element-container div[data-testid="stText"] {
        color: #E5E7EB;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Session state initialization
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "access_token" not in st.session_state:
    st.session_state.access_token = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_page" not in st.session_state:
    st.session_state.current_page = "login"

def login(username, password):
    """
    Authenticate user with the API and store the access token.
    
    Args:
        username: User's username
        password: User's password
        
    Returns:
        bool: True if login was successful, False otherwise
    """
    try:
        response = requests.post(
            f"{API_URL}/token",
            data={"username": username, "password": password},
        )
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.access_token = data["access_token"]
            st.session_state.username = username
            st.session_state.authenticated = True
            st.session_state.current_page = "chat"
            fetch_chat_history()
            return True
        else:
            return False
    except Exception as e:
        st.error(f"Error during login: {str(e)}")
        return False

def signup(username, password):
    """
    Register a new user with the API.
    
    Args:
        username: New user's username
        password: New user's password
        
    Returns:
        bool: True if signup was successful, False otherwise
    """
    try:
        response = requests.post(
            f"{API_URL}/signup",
            json={"username": username, "password": password},
        )
        
        if response.status_code == 201:
            return True
        else:
            error_msg = response.json().get("detail", "Unknown error")
            st.error(f"Signup failed: {error_msg}")
            return False
    except Exception as e:
        st.error(f"Error during signup: {str(e)}")
        return False

def logout():
    """Log out the current user by clearing session state."""
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.access_token = ""
    st.session_state.chat_history = []
    st.session_state.current_page = "login"

def send_message(query):
    """
    Send a message to the weather agent API.
    
    Args:
        query: The user's query text
        
    Returns:
        str: The agent's response
    """
    if not query.strip():
        return None
        
    headers = {
        "Authorization": f"Bearer {st.session_state.access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{API_URL}/api/chat",
            headers=headers,
            json={"query": query}
        )
        
        if response.status_code == 200:
            return response.json()["response"]
        else:
            error_msg = response.json().get("detail", "Unknown error")
            st.error(f"Error: {error_msg}")
            if response.status_code == 401:
                # Token expired or invalid
                logout()
                st.rerun()
            return None
    except Exception as e:
        st.error(f"Error sending message: {str(e)}")
        return None

def fetch_chat_history():
    """Fetch chat history from the API and update the session state."""
    if not st.session_state.authenticated:
        return
        
    headers = {
        "Authorization": f"Bearer {st.session_state.access_token}"
    }
    
    try:
        response = requests.get(
            f"{API_URL}/chat-history",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.chat_history = data["messages"]
        else:
            error_msg = response.json().get("detail", "Unknown error")
            st.error(f"Error fetching chat history: {error_msg}")
            if response.status_code == 401:
                # Token expired or invalid
                logout()
                st.rerun()
    except Exception as e:
        st.error(f"Error fetching chat history: {str(e)}")

def clear_chat_history():
    """Clear the chat history in the API and update the session state."""
    if not st.session_state.authenticated:
        return
        
    headers = {
        "Authorization": f"Bearer {st.session_state.access_token}"
    }
    
    try:
        response = requests.delete(
            f"{API_URL}/chat-history",
            headers=headers
        )
        
        if response.status_code == 200:
            st.session_state.chat_history = []
            st.success("Chat history cleared successfully!")
        else:
            error_msg = response.json().get("detail", "Unknown error")
            st.error(f"Error clearing chat history: {error_msg}")
    except Exception as e:
        st.error(f"Error clearing chat history: {str(e)}")

def display_chat_message(role, content, timestamp=None):
    """
    Display a chat message with styling based on the role.
    
    Args:
        role: The role of the message sender ('human' or 'ai')
        content: The message content
        timestamp: Optional timestamp for the message
    """
    if role == "human":
        display_role = "You"
        message_class = "user"
    else:
        display_role = "Weather Agent"
        message_class = "bot"
        
    if timestamp is None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        
    st.markdown(f"""
    <div class="chat-message {message_class}">
        <div><strong>{display_role}:</strong></div>
        <div class="message-content">{content}</div>
        <div class="timestamp">{timestamp}</div>
    </div>
    """, unsafe_allow_html=True)

def login_page():
    """Render the login page."""
    st.title("🌤️ Weather Agent Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            login_button = st.form_submit_button("Login")
        with col2:
            signup_button = st.form_submit_button("Sign Up")
            
        if login_button and username and password:
            if login(username, password):
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")
                
        if signup_button and username and password:
            if signup(username, password):
                st.success("Account created successfully! You can now log in.")
            else:
                st.error("Failed to create account. Username may already exist.")

def chat_page():
    """Render the chat page."""
    st.title("🌤️ Weather Agent Chat")
    
    # Sidebar with user info and logout button
    with st.sidebar:
        st.write(f"Logged in as: **{st.session_state.username}**")
        
        if st.button("Logout"):
            logout()
            st.rerun()
            
        if st.button("Clear Chat History"):
            clear_chat_history()
            st.rerun()
    
    # Display chat history
    st.subheader("Chat History")
    
    if not st.session_state.chat_history:
        st.info("No chat history yet. Start by asking a question about the weather!")
    else:
        for message in st.session_state.chat_history:
            display_chat_message(message["role"], message["content"])
    
    # Chat input
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("Ask about the weather:", placeholder="What's the weather like in London today?")
        submit_button = st.form_submit_button("Send")
        
        if submit_button and user_input:
            # Add user message to UI
            display_chat_message("human", user_input)
            
            # Get response from API
            response = send_message(user_input)
            
            if response:
                # Add bot response to UI
                display_chat_message("ai", response)
                
                # Update chat history
                fetch_chat_history()
                
                # Force a rerun to update the UI with the new messages
                st.rerun()

# Main app logic
def main():
    """Main application entry point."""
    if not st.session_state.authenticated:
        login_page()
    else:
        chat_page()

if __name__ == "__main__":
    main() 