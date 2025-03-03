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
from fastapi import FastAPI, HTTPException, Depends, status, Query, Body, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from weather_agent import create_weather_agent
from user_manager import UserManager
from prompt_cache import PromptCache
from logger_config import setup_logger

# Set up logger
logger = setup_logger(__name__)

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

# Initialize prompt cache on startup
@app.on_event("startup")
async def startup_event():
    """
    Initialize resources when the application starts.
    
    This function is called when the FastAPI application starts up.
    It initializes the prompt cache and logs the startup event.
    """
    logger.info("Starting Weather Agent API")
    
    try:
        # Initialize the prompt cache
        logger.debug("Initializing prompt cache")
        prompt_cache = PromptCache()
        prompt_cache.initialize_cache()
        
        # Log the available prompts
        prompts = prompt_cache.get_prompt_ids()
        logger.info(f"Prompt cache initialized with {len(prompts)} prompts: {', '.join(prompts)}")
        
        logger.info("Weather Agent API started successfully")
    except Exception as e:
        logger.critical(f"Failed to initialize application: {str(e)}", exc_info=True)

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
    
    This endpoint processes natural language queries about weather and returns
    responses from the LangChain-based weather agent. The agent has access to
    real-time weather data and can answer questions about current conditions
    and forecasts.
    
    Args:
        request: The query request containing the user's question
        current_user: The authenticated user (automatically provided by the dependency)
    
    Examples of queries:
    - "What's the weather like in London today?"
    - "Will it rain in New York tomorrow?"
    - "What's the forecast for Tokyo for the next 5 days?"
    
    Returns:
        QueryResponse containing the agent's response to the query
    
    Raises:
        HTTPException: If there's an error processing the query
    
    Requires authentication. The authenticated user's ID is used to maintain conversation context.
    """
    try:
        # Use the authenticated user's ID from the token
        user_id = current_user
        
        logger.info(f"Processing chat query for user '{user_id}': '{request.query}'")
        
        # Get or create the agent for this user
        agent, _ = get_agent(user_id)
        
        # Create config with session_id
        config = {"configurable": {"session_id": user_id}}
        
        # Process the query
        logger.debug(f"Invoking agent for user '{user_id}'")
        response = agent.invoke({"input": request.query}, config)
        
        logger.info(f"Successfully processed query for user '{user_id}'")
        logger.debug(f"Agent response: '{response['output'][:100]}...'")
        
        return QueryResponse(response=response["output"])
    except Exception as e:
        logger.error(f"Error processing query for user '{current_user}': {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

# Chat History Routes
@app.get(
    "/chat-history", 
    response_model=ChatHistoryResponse,
    tags=["Chat History"],
    summary="Get chat history for the current user"
)
async def get_chat_history(
    limit: int = Query(50, description="Maximum number of messages to return"),
    current_user: str = Depends(get_current_user)
):
    """
    Get chat history for the current authenticated user.
    
    This endpoint retrieves the conversation history between the user and the weather agent.
    The history is stored in the MongoDB database and is specific to each user.
    
    Args:
        limit: Maximum number of messages to return (defaults to 50)
        current_user: The authenticated user (automatically provided by the dependency)
    
    Returns:
        ChatHistoryResponse containing a list of chat messages with role and content
    
    Raises:
        HTTPException: If there's an error retrieving the chat history
    
    Requires authentication.
    """
    try:
        logger.info(f"Retrieving chat history for user '{current_user}' with limit {limit}")
        
        # Get or create the agent for this user
        _, memory = get_agent(current_user)
        
        # Get chat history directly from the memory handler
        chat_history = memory.get_chat_history()
        
        logger.debug(f"Retrieved {len(chat_history)} messages from history for user '{current_user}'")
        
        # Format messages for response
        messages = [
            {
                "role": "user" if msg.type == "human" else "assistant",
                "content": msg.content
            } 
            for msg in chat_history
        ]
        
        # Apply limit if specified
        if limit and limit > 0:
            messages = messages[-limit:]
            logger.debug(f"Applied limit, returning {len(messages)} messages")
        
        return ChatHistoryResponse(messages=messages)
    except Exception as e:
        logger.error(f"Error retrieving chat history for user '{current_user}': {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error retrieving chat history: {str(e)}")

@app.delete(
    "/chat-history",
    tags=["Chat History"],
    summary="Delete chat history for the current user"
)
async def delete_chat_history(current_user: str = Depends(get_current_user)):
    """
    Delete the chat history for the current authenticated user.
    
    This endpoint clears all conversation history between the user and the weather agent.
    It also removes the agent from the cache to force recreation on the next request.
    
    Args:
        current_user: The authenticated user (automatically provided by the dependency)
    
    Returns:
        A dictionary with status and message indicating successful deletion
    
    Raises:
        HTTPException: If there's an error deleting the chat history
    
    Requires authentication.
    """
    try:
        logger.info(f"Deleting chat history for user '{current_user}'")
        
        # Get or create the agent for this user
        _, memory = get_agent(current_user)
        
        # Clear chat history
        memory.clear_history()
        logger.debug(f"Chat history cleared for user '{current_user}'")
        
        # Remove from cache to force recreation on next request
        if current_user in agent_cache:
            del agent_cache[current_user]
            logger.debug(f"Removed agent from cache for user '{current_user}'")
        
        logger.info(f"Successfully deleted chat history for user '{current_user}'")
        return {"status": "success", "message": f"Chat history deleted for user {current_user}"}
    except Exception as e:
        logger.error(f"Error deleting chat history for user '{current_user}': {str(e)}", exc_info=True)
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
    
    This endpoint is for development and testing only. It runs the test_conversation_memory
    function from the test_memory module to verify that the conversation memory is working correctly.
    
    Returns:
        A dictionary with status and message indicating successful test completion
    
    Raises:
        HTTPException: If there's an error running the test
    """
    try:
        logger.info("Running test_memory script")
        
        from test_memory import test_conversation_memory
        
        # Run the test
        logger.debug("Executing test_conversation_memory function")
        test_conversation_memory()
        
        logger.info("Test completed successfully")
        return {"status": "success", "message": "Test completed successfully"}
    except Exception as e:
        logger.error(f"Error running test: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error running test: {str(e)}")

# Prompt Management Endpoints
@app.get(
    "/prompts", 
    tags=["Prompt Management"],
    summary="List all prompts in the cache"
)
async def list_prompts(current_user: str = Depends(get_current_user)):
    """
    List all prompts in the cache and their details.
    
    Returns a dictionary containing all prompts in the cache and their details.
    
    Requires authentication.
    """
    try:
        prompt_cache = PromptCache()
        prompts = prompt_cache.get_all_prompts()
        return {
            "status": "success",
            "message": f"Found {len(prompts)} prompts",
            "data": {
                "prompt_count": len(prompts),
                "prompts": prompts
            }
        }
    except Exception as e:
        logger.error("Error listing prompts: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Failed to list prompts",
                "error_details": str(e)
            }
        )

@app.get(
    "/prompts/{prompt_id}", 
    tags=["Prompt Management"],
    summary="Get details of a specific prompt"
)
async def get_prompt_details(
    prompt_id: str = Path(..., description="ID of the prompt to examine"),
    current_user: str = Depends(get_current_user)
):
    """
    Get detailed information about a specific prompt.
    
    Returns the details of the specified prompt, including its template and input variables.
    
    Requires authentication.
    
    Args:
        prompt_id: The ID of the prompt to examine
    """
    try:
        prompt_cache = PromptCache()
        prompt = prompt_cache.get_prompt(prompt_id)
        
        if prompt is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "status": "error",
                    "message": f"Prompt '{prompt_id}' not found in cache",
                }
            )
        
        # Get prompt details from the cache
        all_prompts = prompt_cache.get_all_prompts()
        prompt_details = all_prompts.get(prompt_id, {})
        
        return {
            "status": "success",
            "message": f"Retrieved details for prompt: {prompt_id}",
            "data": prompt_details
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting prompt details: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Failed to get prompt details",
                "error_details": str(e)
            }
        )

@app.get(
    "/test-prompts", 
    tags=["Prompt Management"],
    summary="Test all prompts in the cache"
)
async def test_prompts(current_user: str = Depends(get_current_user)):
    """
    Test all prompts in the cache to ensure they are valid and can be used.
    
    Returns a dictionary containing the test results for each prompt.
    
    Requires authentication.
    """
    try:
        prompt_cache = PromptCache()
        prompts = prompt_cache.get_all_prompts()
        
        # Test each prompt by checking if it exists and has the expected structure
        test_results = {}
        for prompt_id, details in prompts.items():
            prompt = prompt_cache.get_prompt(prompt_id)
            test_results[prompt_id] = {
                "exists": prompt is not None,
                "type": details.get("type", "Unknown"),
                "input_variables": details.get("input_variables", []),
                "valid": prompt is not None and hasattr(prompt, "format")
            }
        
        return {
            "status": "success",
            "message": f"Tested {len(test_results)} prompts",
            "data": {
                "test_results": test_results
            }
        }
    except Exception as e:
        logger.error("Error testing prompts: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Failed to test prompts",
                "error_details": str(e)
            }
        )

@app.post(
    "/prompts/update-all", 
    tags=["Prompt Management"],
    summary="Update all prompts in the cache"
)
async def update_all_prompts(current_user: str = Depends(get_current_user)):
    """
    Update all prompts in the cache by pulling the latest versions from LangChain Hub.
    
    Use this endpoint after making changes to prompts in LangChain Hub to refresh all cached versions.
    
    Returns a dictionary containing the update results for each prompt.
    
    Requires authentication.
    """
    try:
        prompt_cache = PromptCache()
        
        # Update all prompts
        results = prompt_cache.update_all_prompts()
        
        # Count successes and failures
        success_count = sum(1 for success in results.values() if success)
        failure_count = len(results) - success_count
        
        # Get updated prompt details
        all_prompts = prompt_cache.get_all_prompts()
        
        return {
            "status": "success",
            "message": f"Updated {success_count} prompts successfully, {failure_count} failed",
            "data": {
                "update_results": results,
                "prompts": all_prompts
            }
        }
    except Exception as e:
        logger.error("Error updating all prompts: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Failed to update all prompts",
                "error_details": str(e)
            }
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 