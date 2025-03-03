"""
PromptCache class to manage caching of LangChain Hub prompts for the weather agent.
"""
import os
import datetime
from typing import Dict, Optional, List, Union, Any
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain import hub
from logger_config import setup_logger

logger = setup_logger(__name__)

# Define the weather prompt IDs
WEATHER_PROMPT_IDS = [
    "weather_agent"
]

class PromptCache:
    """Singleton class to manage cached prompts from LangChain Hub for the weather agent."""
    _instance = None
    _prompts: Dict[str, Union[ChatPromptTemplate, PromptTemplate]] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PromptCache, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the cache if it hasn't been initialized yet."""
        if not self._prompts:
            self.initialize_cache()
    
    def initialize_cache(self):
        """Initialize the cache by pulling all required prompts."""
        logger.info("Initializing weather prompt cache")
        
        # Define prompt configurations with their expected types
        prompt_configs = {
            # Weather agent prompts (ChatPromptTemplate)
            "weather_agent": "chat"
        }
        
        for prompt_id, prompt_type in prompt_configs.items():
            try:
                prompt = hub.pull(prompt_id)
                
                # Validate prompt based on expected type
                if prompt_type == "chat" and not isinstance(prompt, ChatPromptTemplate):
                    logger.warning("Expected ChatPromptTemplate for %s but got %s", prompt_id, type(prompt))
                    prompt = None
                elif prompt_type == "prompt" and not isinstance(prompt, PromptTemplate):
                    logger.warning("Expected PromptTemplate for %s but got %s", prompt_id, type(prompt))
                    prompt = None
                    
                self._prompts[prompt_id] = prompt
                logger.info("Successfully cached prompt: %s (%s)", prompt_id, type(prompt).__name__)
            except Exception as e:
                logger.error("Error caching prompt %s: %s", prompt_id, str(e))
                self._prompts[prompt_id] = None
    
    def get_prompt(self, prompt_id: str) -> Optional[Union[ChatPromptTemplate, PromptTemplate]]:
        """Get a prompt from the cache."""
        prompt = self._prompts.get(prompt_id)
        
        # If the prompt contains TODAY_DATE placeholder, update it
        if prompt and isinstance(prompt, ChatPromptTemplate):
            today_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
            
            # Create a new prompt with the updated date
            try:
                # For newer versions of LangChain, we need to handle the messages differently
                updated_messages = []
                for message in prompt.messages:
                    if hasattr(message, 'prompt') and hasattr(message.prompt, 'template'):
                        if "{TODAY_DATE}" in message.prompt.template:
                            # Create a new message with the updated date
                            updated_template = message.prompt.template.replace("{TODAY_DATE}", today_date)
                            # We need to recreate the message with the updated template
                            # This is a simplified approach and might need adjustment based on the exact structure
                            updated_messages.append(message.__class__(prompt=message.prompt.__class__(template=updated_template)))
                        else:
                            updated_messages.append(message)
                    else:
                        updated_messages.append(message)
                
                # Check if the prompt has the required placeholders for agent functionality
                has_agent_scratchpad = any(
                    hasattr(msg, 'prompt') and 
                    hasattr(msg.prompt, 'template') and 
                    "{agent_scratchpad}" in msg.prompt.template 
                    for msg in prompt.messages
                )
                
                has_chat_history = any(
                    hasattr(msg, 'prompt') and 
                    hasattr(msg.prompt, 'template') and 
                    "{chat_history}" in msg.prompt.template 
                    for msg in prompt.messages
                )
                
                # If the prompt is missing required placeholders, add them
                if not has_agent_scratchpad or not has_chat_history:
                    logger.info(f"Adding missing placeholders to prompt {prompt_id}")
                    
                    # Find the last human/user message to insert chat_history before it
                    for i, msg in enumerate(updated_messages):
                        if (hasattr(msg, '__class__') and 
                            ('Human' in msg.__class__.__name__ or 'User' in msg.__class__.__name__)):
                            if not has_chat_history:
                                # Insert chat_history before the human message
                                from langchain.prompts.chat import MessagesPlaceholder
                                updated_messages.insert(i, MessagesPlaceholder(variable_name="chat_history"))
                            break
                    
                    # Add agent_scratchpad at the end if it's missing
                    if not has_agent_scratchpad:
                        from langchain.prompts.chat import MessagesPlaceholder
                        updated_messages.append(MessagesPlaceholder(variable_name="agent_scratchpad"))
                
                # If we made any changes, create a new prompt
                if updated_messages:
                    # Make sure input_variables includes the required variables
                    input_variables = list(prompt.input_variables)
                    if "agent_scratchpad" not in input_variables:
                        input_variables.append("agent_scratchpad")
                    if "chat_history" not in input_variables:
                        input_variables.append("chat_history")
                    
                    # If the prompt uses 'question' instead of 'input', add a mapping
                    if "question" in input_variables and "input" not in input_variables:
                        input_variables.append("input")
                    
                    return ChatPromptTemplate(messages=updated_messages, input_variables=input_variables)
            except Exception as e:
                logger.error("Error updating prompt: %s", str(e))
        
        return prompt
    
    def get_all_prompts(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all prompts and their details from the cache.
        
        Returns:
            Dict[str, Dict]: Dictionary of prompt_id -> prompt details
        """
        result = {}
        for prompt_id, prompt in self._prompts.items():
            if prompt is None:
                result[prompt_id] = {
                    "template": "Failed to load prompt",
                    "input_variables": [],
                    "type": "None"
                }
                continue
                
            if isinstance(prompt, ChatPromptTemplate):
                # Handle ChatPromptTemplate
                messages_info = []
                
                # Extract message information
                try:
                    for message in prompt.messages:
                        if hasattr(message, 'prompt') and hasattr(message.prompt, 'template'):
                            messages_info.append({
                                "role": message.__class__.__name__.replace("MessagePromptTemplate", ""),
                                "content": message.prompt.template
                            })
                        else:
                            messages_info.append({
                                "role": "unknown",
                                "content": str(message)
                            })
                except Exception as e:
                    logger.error("Error extracting message information: %s", str(e))
                    messages_info.append({
                        "role": "error",
                        "content": f"Error: {str(e)}"
                    })
                
                result[prompt_id] = {
                    "template": messages_info,
                    "input_variables": prompt.input_variables,
                    "type": "ChatPromptTemplate"
                }
            else:
                # Handle regular PromptTemplate
                result[prompt_id] = {
                    "template": prompt.template if hasattr(prompt, 'template') else str(prompt),
                    "input_variables": prompt.input_variables,
                    "type": prompt.__class__.__name__
                }
                
        return result
    
    def get_prompt_ids(self) -> List[str]:
        """Get list of all prompt IDs in the cache."""
        return list(self._prompts.keys())
    
    def update_prompt(self, prompt_id: str) -> bool:
        """Update a specific prompt in the cache."""
        try:
            self._prompts[prompt_id] = hub.pull(prompt_id)
            logger.info("Successfully updated cached prompt: %s", prompt_id)
            return True
        except Exception as e:
            logger.error("Error updating prompt %s: %s", prompt_id, str(e))
            return False
    
    def update_all_prompts(self) -> Dict[str, bool]:
        """Update all prompts in the cache."""
        results = {}
        for prompt_id in self._prompts.keys():
            results[prompt_id] = self.update_prompt(prompt_id)
        return results
    
    def create_default_weather_prompt(self) -> ChatPromptTemplate:
        """Create the default weather prompt template."""
        today_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
        
        # Create a prompt template with the required agent_scratchpad and chat history
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""Hey there! ☀️ You're a friendly and helpful weather assistant with access to real-time weather data. 

            📅 Today is **{today_date}**.

            🌍 **Your job is simple:** Help users with their weather-related questions using accurate, up-to-date data! 

            ✅ **How you can help:**
            - If the user asks about **today's weather**, use `get_current_weather` 🌤️.
            - If they ask about the **forecast** (tomorrow, next week, specific dates), use `get_weather_forecast` 📅.
            - If the request isn't clear, just ask for more details in a friendly way.
            - Respond in **markdown format** and use **emojis** to make it engaging! 😊
            - Match the user's language and tone. If they're casual, be casual. If they're formal, be formal.
            - If the city isn't in the database, kindly let them know.

            ❌ **Things you shouldn't do:**
            - Never make up weather information.
            - Stay focused on weather-related questions only.

            --- 
            ✨ **Example Conversations:**

            **User:** "Hey! What's the weather like in Paris today?"  
            **You:** "🌤️ The current temperature in **Paris** is 18°C with clear skies. Enjoy your day! ☀️"  

            **User:** "Will it rain in New York tomorrow?"  
            **You:** "🌧️ **Tomorrow's forecast for New York:** Expect light showers in the afternoon with a high of 22°C."  

            **User:** "Can you tell me the weather for London next Monday?"  
            **You:** "📅 **London's forecast for Monday:** A mix of sun and clouds with a high of 19°C and a slight chance of rain. 🌥️"  

            **User:** "Weather in Mars?"  
            **You:** "Hmm... I can only check Earth's weather! 🌍 If you're asking about a specific city, let me know!"  
            """),
            
            ("placeholder", "{chat_history}"),
            ("user", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])
        
        return prompt

if __name__ == "__main__":
    prompt_cache = PromptCache()
    print(prompt_cache.get_all_prompts())

