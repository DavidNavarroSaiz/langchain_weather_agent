import os
from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.runnables.history import RunnableWithMessageHistory


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
        self.user_id = user_id
        self.k = k  # Number of past messages to remember
        
        # Use provided connection details or fall back to environment variables
        connection_string = connection_string or os.getenv("MONGO_URI")
        database_name = database_name or os.getenv("MONGO_DB")
        collection_name = collection_name or os.getenv("MONGO_COLLECTION")
        
        self.chat_history = MongoDBChatMessageHistory(
            session_id=user_id,
            connection_string=connection_string,
            database_name=database_name,
            collection_name=collection_name,
        )
        self.memory = ConversationBufferWindowMemory(
            k=self.k,  # Stores the last `k` messages
            memory_key="chat_history",
            input_key="input",
            output_key="output",
            return_messages=True,
            chat_memory=self.chat_history,
        )

    def get_chat_history(self):
        """Retrieve chat history for the current session."""
        return self.memory.load_memory_variables({})["chat_history"]

    def add_user_message(self, message: str):
        """Add a user message to chat history."""
        self.chat_history.add_user_message(message)

    def add_ai_message(self, message: str):
        """Add an AI message to chat history."""
        self.chat_history.add_ai_message(message)

    def clear_history(self):
        """Clear chat history for the session."""
        self.chat_history.clear()
    
    def create_runnable_with_history(self, runnable):
        """
        Wrap a runnable with message history capabilities.
        
        Args:
            runnable: The LangChain runnable to wrap with history
            
        Returns:
            A RunnableWithMessageHistory instance
        """
        return RunnableWithMessageHistory(
            runnable=runnable,
            get_session_history=self._get_session_history,
            history_messages_key="chat_history",
        )
    
    def _get_session_history(self, session_id):
        """
        Get the chat history for a specific session.
        Used by RunnableWithMessageHistory.
        
        Args:
            session_id: The session ID to get history for
            
        Returns:
            A MongoDBChatMessageHistory instance
        """
        # If the session_id matches our user_id, return the existing chat history
        if session_id == self.user_id:
            return self.chat_history
        
        # Otherwise, create a new chat history for the specified session
        return MongoDBChatMessageHistory(
            session_id=session_id,
            connection_string=os.getenv("MONGO_URI"),
            database_name=os.getenv("MONGO_DB"),
            collection_name=os.getenv("MONGO_COLLECTION"),
        )
    
    