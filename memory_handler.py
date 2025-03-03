import os
from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.runnables.history import RunnableWithMessageHistory
from logger_config import setup_logger

# Set up logger
logger = setup_logger(__name__)

class MongoDBConversationMemory:
    """
    Chat Memory with MongoDB for LangChain Agents, integrating:
    - MongoDB chat history storage
    - Conversation Buffer Window Memory with configurable `k`
    - RunnableWithMessageHistory for chaining with LangChain LLMs
    """

    def __init__(
        self,
        user_id: str,
        connection_string: str = None,
        database_name: str = None,
        collection_name: str = None,
        k: int = 4,  # Default window memory size
    ):
        """
        Initialize MongoDB conversation memory.
        
        Args:
            user_id (str): User ID for the conversation
            connection_string (str, optional): MongoDB connection string
            database_name (str, optional): MongoDB database name
            collection_name (str, optional): MongoDB collection name
            k (int, optional): Number of past messages to remember
        """
        self.user_id = user_id
        self.k = k  # Number of past messages to remember
        
        # Use provided connection details or fall back to environment variables
        connection_string = connection_string or os.getenv("MONGO_URI")
        database_name = database_name or os.getenv("MONGO_DB")
        collection_name = collection_name or os.getenv("MONGO_COLLECTION")
        
        if not connection_string or not database_name or not collection_name:
            logger.error("Missing MongoDB connection details")
            raise ValueError("MongoDB connection details are required")
        
        logger.debug(f"Initializing MongoDB conversation memory for user {user_id}")
        
        # Initialize MongoDB chat history
        self.message_history = MongoDBChatMessageHistory(
            connection_string=connection_string,
            database_name=database_name,
            collection_name=collection_name,
            session_id=user_id
        )
        
        # Initialize conversation memory
        self.memory = ConversationBufferWindowMemory(
            chat_memory=self.message_history,
            return_messages=True,
            k=k
        )
        
        logger.info(f"MongoDB conversation memory initialized for user {user_id}")

    def get_chat_history(self):
        """
        Get the chat history for the current user.
        
        Returns:
            list: List of chat messages
        """
        logger.debug(f"Getting chat history for user {self.user_id}")
        return self.message_history.messages

    def add_user_message(self, message: str):
        """
        Add a user message to chat history.
        
        Args:
            message (str): The message to add
        """
        logger.debug(f"Adding user message for user {self.user_id}")
        self.message_history.add_user_message(message)

    def add_ai_message(self, message: str):
        """
        Add an AI message to chat history.
        
        Args:
            message (str): The message to add
        """
        logger.debug(f"Adding AI message for user {self.user_id}")
        self.message_history.add_ai_message(message)

    def clear_history(self):
        """Clear chat history for the session."""
        logger.info(f"Clearing chat history for user {self.user_id}")
        self.message_history.clear()
    
    def create_runnable_with_history(self, runnable):
        """
        Create a runnable with message history.
        
        Args:
            runnable: The runnable to wrap with message history
            
        Returns:
            RunnableWithMessageHistory: The wrapped runnable
        """
        logger.debug(f"Creating runnable with history for user {self.user_id}")
        
        # Create a configurable runnable with history
        runnable_with_history = RunnableWithMessageHistory(
            runnable=runnable,
            get_session_history=self._get_session_history,
            session_id=self.user_id,
            history_messages_key="chat_history",
            input_messages_key="input",
            output_messages_key="output",
        )
        
        logger.info(f"Created runnable with history for user {self.user_id}")
        return runnable_with_history
    
    def _get_session_history(self, session_id):
        """
        Get the chat history for a specific session.
        
        Args:
            session_id (str): The session ID
            
        Returns:
            MongoDBChatMessageHistory: The chat history for the session
        """
        logger.debug(f"Getting session history for session {session_id}")
        
        # If the session_id matches our user_id, return the existing chat history
        if session_id == self.user_id:
            return self.message_history
        
        # Otherwise, create a new chat history for the specified session
        return MongoDBChatMessageHistory(
            session_id=session_id,
            connection_string=os.getenv("MONGO_URI"),
            database_name=os.getenv("MONGO_DB"),
            collection_name=os.getenv("MONGO_COLLECTION"),
        )
    
    