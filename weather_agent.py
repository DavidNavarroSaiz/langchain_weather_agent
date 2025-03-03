import os
import datetime
import re
from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain import hub
from openweather_api import OpenWeather
from memory_handler import MongoDBConversationMemory
from prompt_cache import PromptCache
from logger_config import setup_logger

# Set up logger
logger = setup_logger(__name__)

# Load environment variables
load_dotenv()

# Initialize the OpenWeather client
weather_client = OpenWeather()

# Default user ID (can be replaced with actual user authentication)
DEFAULT_USER_ID = "test_user"

# Get today's date
TODAY_DATE = datetime.datetime.now().strftime("%A, %B %d, %Y")

@tool
def get_current_weather(city: str, country_code: str = None) -> str:
    """
    Get the current weather for a specific city.
    
    Args:
        city: The name of the city to get weather for
        country_code: The two-letter country code (optional)
        
    Returns:
        A string with the current weather information
    """
    location = weather_client.get_geolocation(city, country_code)
    if not location:
        return f"❌ Sorry, I couldn't find location information for **{city}**."

    lat, lon = location[0]["lat"], location[0]["lon"]
    weather_data = weather_client.get_current_weather(lat, lon)

    if not weather_data:
        return f"⚠️ Weather data for **{city}** is currently unavailable."

    return weather_client.format_current_weather(weather_data, city, country_code)

@tool
def get_weather_forecast(city: str, country_code: str = None) -> str:
    """
    Get a 5-day weather forecast for a specific city.
    
    Args:
        city: The name of the city to get forecast for
        country_code: The two-letter country code (optional)
        
    Returns:
        A string with the weather forecast information
    """
    location = weather_client.get_geolocation(city, country_code)
    if not location:
        return f"❌ Sorry, I couldn't find location information for **{city}**."

    lat, lon = location[0]["lat"], location[0]["lon"]
    forecast_data = weather_client.get_forecast(lat, lon)

    if not forecast_data:
        return f"⚠️ Forecast data for **{city}** is currently unavailable."

    return weather_client.format_forecast(forecast_data, city, country_code)


# Create the LangChain agent
def create_weather_agent(user_id=DEFAULT_USER_ID, k=5):
    """
    Create a LangChain agent for weather queries with MongoDB memory.
    
    Args:
        user_id (str, optional): User ID for the conversation memory
        k (int, optional): Number of past messages to remember
        
    Returns:
        tuple: (agent_with_memory, memory) - The agent with memory and the memory instance
    """
    logger.info(f"Creating weather agent for user {user_id}")
    
    # Initialize the language model
    try:
        model_name = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo-0125")
        logger.debug(f"Initializing language model: {model_name}")
        
        llm = ChatOpenAI(
            model=model_name,
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        logger.debug("Language model initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize language model: {str(e)}")
        raise
    
    # Define the tools
    logger.debug("Setting up agent tools")
    tools = [get_current_weather, get_weather_forecast]
    
    # Get the prompt from the PromptCache
    logger.debug("Getting prompt from cache")
    prompt_cache = PromptCache()
    prompt = prompt_cache.get_prompt("weather_agent")
    
    # If the prompt is not found in the cache, create a default one
    if prompt is None:
        logger.warning("Weather agent prompt not found in cache, creating default prompt")
        prompt = prompt_cache.create_default_weather_prompt()
    
    # Check if the prompt uses 'question' instead of 'input'
    input_mapping = {}
    if "question" in prompt.input_variables and "input" not in prompt.input_variables:
        logger.info("Prompt uses 'question' instead of 'input', adding mapping")
        input_mapping = {"input": "question"}
    
    # Create the agent
    try:
        logger.debug("Creating OpenAI tools agent")
        agent = create_openai_tools_agent(llm, tools, prompt)
        logger.debug("Agent created successfully")
    except Exception as e:
        logger.error(f"Failed to create agent: {str(e)}")
        raise

    # Create the agent executor
    try:
        logger.debug("Creating agent executor")
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True,
            input_mapping=input_mapping
        )
        logger.debug("Agent executor created successfully")
    except Exception as e:
        logger.error(f"Failed to create agent executor: {str(e)}")
        raise
    
    # Initialize MongoDB memory
    try:
        logger.debug(f"Initializing MongoDB memory with k={k}")
        memory = MongoDBConversationMemory(
            user_id=user_id,
            connection_string=os.getenv("MONGO_URI"),
            database_name=os.getenv("MONGO_DB"),
            collection_name=os.getenv("MONGO_COLLECTION"),
            k=k
        )
        logger.debug("MongoDB memory initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize MongoDB memory: {str(e)}")
        raise
    
    # Wrap the agent executor with message history
    try:
        logger.debug("Creating runnable with history")
        agent_with_memory = memory.create_runnable_with_history(agent_executor)
        logger.info(f"Weather agent created successfully for user {user_id}")
    except Exception as e:
        logger.error(f"Failed to create runnable with history: {str(e)}")
        raise
    
    return agent_with_memory, memory

if __name__ == "__main__":
    # Create the weather agent with memory
    logger.info("Starting Weather Assistant CLI")
    
    try:
        weather_agent, memory = create_weather_agent(DEFAULT_USER_ID)
        logger.info(f"Weather agent created successfully for user {DEFAULT_USER_ID}")
        
        print("🌦️ Welcome to the Weather Assistant! 🌦️")
        print("Today is:", TODAY_DATE)
        print("You can ask about current weather and forecasts.")
        print("Type 'exit' to quit.")

        while True:
            user_input = input("What would you like to know about the weather? ")
            if user_input.lower() in ["exit", "quit", "bye"]:
                logger.info("User requested to exit")
                print("👋 Goodbye! Stay safe and check the weather before heading out!")
                break
            
            logger.info(f"Processing user query: {user_input}")
            
            try:
                response = weather_agent.invoke({"input": user_input})
                response_output = response["output"]
                
                logger.info("Successfully generated response")
                logger.debug(f"Response: {response_output}")
                
                print("\n📢 Response:", response_output, "\n")
            except Exception as e:
                logger.error(f"Error processing query: {str(e)}", exc_info=True)
                print(f"❌ An error occurred: {e}")
    except Exception as e:
        logger.critical(f"Failed to start Weather Assistant: {str(e)}", exc_info=True)
        print(f"❌ Failed to start Weather Assistant: {e}")
