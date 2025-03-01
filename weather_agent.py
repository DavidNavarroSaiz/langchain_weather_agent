import os
import datetime
import re
from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from openweather_api import OpenWeather
from memory_handler import MongoDBConversationMemory

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
    # Initialize the language model
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo-0125"),
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Define the tools
    tools = [get_current_weather, get_weather_forecast]
    
    # Create a prompt template with the required agent_scratchpad and chat history
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"""You are a weather assistant with access to real-time weather data.
        
        📅 Today is **{TODAY_DATE}**.
        
        ✅ Your main tasks:
        - If the user asks about **current weather (today)**, use `get_current_weather`.
        - If the user asks about **future weather (tomorrow, next week, specific days, dates, or mentions "forecast")**, use `get_weather_forecast`.
        - If the user's request is unclear, ask for clarification.
        - Provide detailed responses in markdown format with emojis.
        - Match the user's language when responding.
        - If the city is not in the database, politely inform the user.

        ❌ **You CANNOT:**
        - Make up weather information.
        - Answer non-weather-related questions.

        Example interactions:
        **User:** "What's the weather like in Paris today?"
        **Response:** "🌤️ The current temperature in **Paris** is 18°C with clear skies."

        **User:** "Will it rain in New York tomorrow?"
        **Response:** "📅 **Tomorrow’s forecast for New York:** ..." (uses `get_weather_forecast`).
        
        **User:** "Weather for London next Monday?"
        **Response:** "📅 **Weather forecast for Monday in London:** ..." (uses `get_weather_forecast`).
        """),
        
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    
    # Create the agent
    agent = create_openai_tools_agent(llm, tools, prompt)

    # Create the agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True
    )
    
    # Initialize MongoDB memory
    memory = MongoDBConversationMemory(
        user_id=user_id,
        connection_string=os.getenv("MONGO_URI"),
        database_name=os.getenv("MONGO_DB"),
        collection_name=os.getenv("MONGO_COLLECTION"),
        k=k
    )
    
    # Wrap the agent executor with message history
    agent_with_memory = memory.create_runnable_with_history(agent_executor)
    
    return agent_with_memory, memory

if __name__ == "__main__":
    # Create the weather agent with memory
    weather_agent, memory = create_weather_agent(DEFAULT_USER_ID)
    
    print("🌦️ Welcome to the Weather Assistant! 🌦️")
    print("Today is:", TODAY_DATE)
    print("You can ask about current weather and forecasts.")
    print("Type 'exit' to quit.")

    while True:
        user_input = input("What would you like to know about the weather? ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("👋 Goodbye! Stay safe and check the weather before heading out!")
            break
        
        
        
        try:
            response = weather_agent.invoke({"input": user_input})
            response_output = response["output"]
            
            print("\n📢 Response:", response_output, "\n")
        except Exception as e:
            print(f"❌ An error occurred: {e}")
