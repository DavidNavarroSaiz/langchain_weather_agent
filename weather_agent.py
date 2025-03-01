import os
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
    # Get geolocation first
    location = weather_client.get_geolocation(city, country_code)
    if not location:
        return f"Could not find location information for {city}"
    
    # Get coordinates
    lat, lon = location[0]["lat"], location[0]["lon"]
    
    # Get current weather
    weather_data = weather_client.get_current_weather(lat, lon)
    if not weather_data:
        return f"Could not retrieve weather data for {city}"
    
    # Use the formatting function from OpenWeather class
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
    # Get geolocation first
    location = weather_client.get_geolocation(city, country_code)
    if not location:
        return f"Could not find location information for {city}"
    
    # Get coordinates
    lat, lon = location[0]["lat"], location[0]["lon"]
    
    # Get forecast
    forecast_data = weather_client.get_forecast(lat, lon)
    if not forecast_data:
        return f"Could not retrieve forecast data for {city}"
    
    # Use the formatting function from OpenWeather class
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
    tools = [
        get_current_weather,
        get_weather_forecast,
    ]
    
    # Create a prompt template with the required agent_scratchpad and chat history
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a weather assistant that must use the provided tools to fetch weather data. 
        You are not allowed to generate answers based on general knowledge.

        If a user asks about the weather in a city, you must call `get_current_weather` or `get_weather_forecast`.

        - If the user asks for **current weather**, use `get_current_weather`.
        - If the user asks for **forecast**, use `get_weather_forecast`.

        When responding to the user, consider the chat history to provide context-aware responses.
        If the user refers to a previous conversation, check the chat history.

        If the city name is missing, ask for clarification.
        DO NOT answer general questions about weather without using the tools.
        provide the answer in the same language as the user's question.
        if the user's question is not about weather, say "I'm sorry, I can only answer questions about weather."
        if the user's question is not clear, ask for clarification.
        if the user's question is about a city that is not in the database, say "I'm sorry, I don't know the weather in that city."
        provide the output in markdown format with a proper use of emojis, be detailed and explain the user in detail
        """),
        
        # Include chat history in the prompt
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        # Add the required MessagesPlaceholder for agent_scratchpad
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
    print("You can ask about current weather and forecasts.")
    print("Type 'exit' to quit.")
    print()
    
    while True:
        user_input = input("What would you like to know about the weather? ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Goodbye! Have a great day! ☀️")
            break
        
        try:
            # Process the user input with memory
            response = weather_agent.invoke({"input": user_input})
            response_output = response["output"]
            
            print("\nResponse:", response_output)
            print()
        except Exception as e:
            print(f"❌ An error occurred: {e}") 