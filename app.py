"""
Weather Agent API

This module provides a FastAPI application for interacting with a LangChain-based
weather agent. It includes endpoints for user management, chat interactions, and
chat history management.

The API uses OAuth2 password bearer authentication and MongoDB for storing
user data and conversation history.
"""

import os
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Depends, status, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from weather_agent import create_weather_agent
from memory_handler import MongoDBConversationMemory
from user_manager import UserManager

# Load environment variables
load_dotenv()

# Initialize FastAPI app with metadata
app = FastAPI(
    title="Weather Agent API",
    description="""
    REST API for interacting with the LangChain Weather Agent.
    
    This API provides endpoints for:
    - User management (signup, login, deletion)
    - Weather agent chat interactions
    - Chat history management
    
    All endpoints except signup and login require authentication.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize user manager
user_manager = UserManager()

# OAuth2 password bearer for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Cache for agent instances to avoid recreating them for each request
agent_cache = {}

#
# Pydantic models for request/response
#

class QueryRequest(BaseModel):
    """Model for chat query requests"""
    query: str = Field(..., description="The user's query to the weather agent")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "What's the weather like in London today?"
            }
        }

class QueryResponse(BaseModel):
    """Model for chat query responses"""
    response: str = Field(..., description="The agent's response to the query")
    
    class Config:
        schema_extra = {
            "example": {
                "response": "The current weather in London is 12°C with light rain. Humidity is at 85% and wind speed is 10 km/h."
            }
        }
    
class ChatHistoryResponse(BaseModel):
    """Model for chat history responses"""
    messages: List[Dict[str, str]] = Field(..., description="List of chat messages with role and content")
    
    class Config:
        schema_extra = {
            "example": {
                "messages": [
                    {"role": "human", "content": "What's the weather like in London today?"},
                    {"role": "ai", "content": "The current weather in London is 12°C with light rain. Humidity is at 85% and wind speed is 10 km/h."}
                ]
            }
        }

class UserCreate(BaseModel):
    """Model for user creation requests"""
    username: str = Field(..., description="Username for the new account")
    password: str = Field(..., description="Password for the new account")
    
    class Config:
        schema_extra = {
            "example": {
                "username": "john_doe",
                "password": "secure_password123"
            }
        }

class UserResponse(BaseModel):
    """Model for user-related responses"""
    username: str = Field(..., description="Username of the affected account")
    message: str = Field(..., description="Status message")
    
    class Config:
        schema_extra = {
            "example": {
                "username": "john_doe",
                "message": "User created successfully"
            }
        }

class Token(BaseModel):
    """Model for authentication tokens"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(..., description="Token type (always 'bearer')")
    
    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }

#
# Helper functions
#

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Dependency to get the current authenticated user from the token.
    
    Args:
        token: The authentication token from the request
        
    Returns:
        str: The username extracted from the token
        
    Raises:
        HTTPException: If the token is invalid or the user doesn't exist
    """
    if not user_manager.user_exists(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token

def get_agent(user_id: str):
    """
    Get or create an agent for the specified user_id.
    
    Args:
        user_id: The user ID to get or create an agent for
        
    Returns:
        tuple: A tuple containing (agent, memory)
    """
    if user_id not in agent_cache:
        agent, memory = create_weather_agent(user_id=user_id)
        agent_cache[user_id] = (agent, memory)
    return agent_cache[user_id]

#
# API Routes
#

# User Management Routes
@app.post(
    "/signup", 
    response_model=UserResponse,
    tags=["User Management"],
    summary="Create a new user account",
    status_code=status.HTTP_201_CREATED
)
async def create_user(user: UserCreate):
    """
    Create a new user account with the provided username and password.
    
    - **username**: Unique username for the account
    - **password**: Password for the account
    
    Returns a success message if the account was created.
    
    Raises a 400 error if the username already exists.
    """
    if user_manager.register_user(user.username, user.password):
        return UserResponse(
            username=user.username,
            message="User created successfully"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

@app.post(
    "/token", 
    response_model=Token,
    tags=["User Management"],
    summary="Login and get access token"
)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate a user and return an access token.
    
    - **username**: The user's username
    - **password**: The user's password
    
    Returns an access token if authentication is successful.
    
    Raises a 401 error if authentication fails.
    """
    if user_manager.authenticate_user(form_data.username, form_data.password):
        # In a real app, you would generate a JWT token
        # For simplicity, we're using the username as the token
        return Token(
            access_token=form_data.username,
            token_type="bearer"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.delete(
    "/users/{username}", 
    response_model=UserResponse,
    tags=["User Management"],
    summary="Delete a user account"
)
async def delete_user(
    username: str, 
    current_user: str = Depends(get_current_user)
):
    """
    Delete a user account (only if it's the current user).
    
    - **username**: The username of the account to delete
    
    Returns a success message if the account was deleted.
    
    Raises:
    - 403 error if trying to delete another user's account
    - 404 error if the user doesn't exist
    """
    # Only allow users to delete their own account
    if current_user != username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user"
        )
    
    if user_manager.delete_user(username):
        # Also delete chat history
        try:
            # Get or create the agent for this user
            _, memory = get_agent(username)
            memory.clear_history()
            
            # Remove from cache
            if username in agent_cache:
                del agent_cache[username]
        except Exception:
            # Continue even if clearing history fails
            pass
            
        return UserResponse(
            username=username,
            message="User deleted successfully"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

# Weather Agent Routes
@app.post(
    "/api/chat", 
    response_model=QueryResponse,
    tags=["Weather Agent"],
    summary="Send a query to the weather agent"
)
async def chat_agent(
    request: QueryRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Send a query to the weather agent and get a response.
    
    - **query**: The user's question about weather
    
    Examples of queries:
    - "What's the weather like in London today?"
    - "Will it rain in New York tomorrow?"
    - "What's the forecast for Tokyo for the next 5 days?"
    
    Returns the agent's response to the query.
    
    Requires authentication. The authenticated user's ID is used to maintain conversation context.
    """
    try:
        # Use the authenticated user's ID from the token
        user_id = current_user
        
        # Get or create the agent for this user
        agent, _ = get_agent(user_id)
        
        # Create config with session_id
        config = {"configurable": {"session_id": user_id}}
        
        # Process the query
        response = agent.invoke({"input": request.query}, config)
        
        return QueryResponse(response=response["output"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

# Chat History Routes
@app.get(
    "/chat-history", 
    response_model=ChatHistoryResponse,
    tags=["Chat History"],
    summary="Get chat history for the current user"
)
async def get_chat_history(
    limit: int = Query(10, description="Maximum number of messages to return"),
    current_user: str = Depends(get_current_user)
):
    """
    Get the chat history for the current authenticated user.
    
    - **limit**: Optional parameter to limit the number of messages returned
    
    Returns a list of chat messages with their roles and content.
    
    Requires authentication.
    """
    try:
        # Get or create the agent for this user
        _, memory = get_agent(current_user)
        
        # Get chat history
        chat_history = memory.get_chat_history()
        
        # Convert to a list of dictionaries
        messages = [
            {"role": msg.type, "content": msg.content}
            for msg in chat_history
        ]
        
        # Apply limit if specified
        if limit and limit > 0:
            messages = messages[-limit:]
        
        return ChatHistoryResponse(messages=messages)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving chat history: {str(e)}")

@app.delete(
    "/chat-history",
    tags=["Chat History"],
    summary="Delete chat history for the current user"
)
async def delete_chat_history(current_user: str = Depends(get_current_user)):
    """
    Delete the chat history for the current authenticated user.
    
    Returns a success message if the history was deleted.
    
    Requires authentication.
    """
    try:
        # Get or create the agent for this user
        _, memory = get_agent(current_user)
        
        # Clear chat history
        memory.clear_history()
        
        # Remove from cache to force recreation on next request
        if current_user in agent_cache:
            del agent_cache[current_user]
        
        return {"status": "success", "message": f"Chat history deleted for user {current_user}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting chat history: {str(e)}")

# Testing Routes
@app.post(
    "/run-test",
    tags=["Testing"],
    summary="Run the test_memory script",
    include_in_schema=False  # Hide from documentation
)
async def run_test_memory():
    """
    Run the test_memory script for testing purposes.
    
    This endpoint is for development and testing only.
    """
    try:
        from test_memory import test_conversation_memory
        
        # Run the test
        test_conversation_memory()
        
        return {"status": "success", "message": "Test completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running test: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 