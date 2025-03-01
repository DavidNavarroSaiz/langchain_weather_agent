import os
from dotenv import load_dotenv
from weather_agent import create_weather_agent

# Load environment variables
load_dotenv()

def test_conversation_memory():
    # Set a test user ID
    test_user_id = "test_user_1"
    
    # Create the weather agent with memory
    weather_agent, memory = create_weather_agent(user_id=test_user_id, k=5)
    
    print("🌦️ Testing Weather Assistant with MongoDB Memory 🌦️")
    print(f"User ID: {test_user_id}")
    print("MongoDB URI:", os.getenv("MONGO_URI"))
    print("Database:", os.getenv("MONGO_DB"))
    print("Collection:", os.getenv("MONGO_COLLECTION"))
    print("\nStarting conversation test...\n")
    
    # Create config with session_id
    config = {"configurable": {"session_id": test_user_id}}
    
    # First query
    query1 = "What's the weather like in London?"
    print(f"User: {query1}")
    response1 = weather_agent.invoke({"input": query1}, config)
    print(f"Assistant: {response1['output']}\n")
    
    # Second query with reference to previous query
    query2 = "How about the forecast for the next few days?"
    print(f"User: {query2}")
    response2 = weather_agent.invoke({"input": query2}, config)
    print(f"Assistant: {response2['output']}\n")
    
    # Third query with reference to previous location
    query3 = "What's the temperature there right now?"
    print(f"User: {query3}")
    response3 = weather_agent.invoke({"input": query3}, config)
    print(f"Assistant: {response3['output']}\n")
    
    # Check the stored messages
    print("Retrieving chat history from MongoDB...")
    chat_history = memory.get_chat_history()
    print(f"Number of messages in history: {len(chat_history)}")
    
    print("\nChat History:")
    for i, message in enumerate(chat_history):
        print(f"{i+1}. {message.type}: {message.content[:50]}...")

if __name__ == "__main__":
    test_conversation_memory() 