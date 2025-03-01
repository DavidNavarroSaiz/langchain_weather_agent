import os
import hashlib
import secrets
from typing import Dict, Optional
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class UserManager:
    """
    Handles user management operations including:
    - User registration
    - Authentication
    - User deletion
    """
    
    def __init__(
        self,
        connection_string: str = None,
        database_name: str = None,
        collection_name: str = "users"  # Separate collection for users
    ):
        # Use provided connection details or fall back to environment variables
        self.connection_string = connection_string or os.getenv("MONGO_URI")
        self.database_name = database_name or os.getenv("MONGO_DB")
        self.collection_name = collection_name
        
        # Connect to MongoDB
        self.client = MongoClient(self.connection_string)
        self.db = self.client[self.database_name]
        self.users = self.db[self.collection_name]
        
        # Create index for username to ensure uniqueness
        self.users.create_index("username", unique=True)
    
    def _hash_password(self, password: str, salt: Optional[str] = None) -> Dict[str, str]:
        """
        Hash a password with a salt for secure storage
        
        Args:
            password: The password to hash
            salt: Optional salt, generated if not provided
            
        Returns:
            Dictionary with hashed password and salt
        """
        if not salt:
            salt = secrets.token_hex(16)
            
        # Create a hash with the password and salt
        pw_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # Number of iterations
        ).hex()
        
        return {"hash": pw_hash, "salt": salt}
    
    def register_user(self, username: str, password: str) -> bool:
        """
        Register a new user
        
        Args:
            username: The username (will be used as user_id)
            password: The password to hash and store
            
        Returns:
            True if registration successful, False otherwise
        """
        # Check if username already exists
        if self.users.find_one({"username": username}):
            return False
        
        # Hash the password
        password_data = self._hash_password(password)
        
        # Create user document
        user = {
            "username": username,
            "password_hash": password_data["hash"],
            "salt": password_data["salt"],
            "created_at": os.getenv("CURRENT_TIMESTAMP", "")
        }
        
        # Insert the user
        try:
            self.users.insert_one(user)
            return True
        except Exception:
            return False
    
    def authenticate_user(self, username: str, password: str) -> bool:
        """
        Authenticate a user
        
        Args:
            username: The username to check
            password: The password to verify
            
        Returns:
            True if authentication successful, False otherwise
        """
        # Find the user
        user = self.users.find_one({"username": username})
        if not user:
            return False
        
        # Hash the provided password with the stored salt
        password_data = self._hash_password(password, user["salt"])
        
        # Compare the hashes
        return password_data["hash"] == user["password_hash"]
    
    def delete_user(self, username: str) -> bool:
        """
        Delete a user
        
        Args:
            username: The username to delete
            
        Returns:
            True if deletion successful, False otherwise
        """
        result = self.users.delete_one({"username": username})
        return result.deleted_count > 0
    
    def user_exists(self, username: str) -> bool:
        """
        Check if a user exists
        
        Args:
            username: The username to check
            
        Returns:
            True if user exists, False otherwise
        """
        return self.users.find_one({"username": username}) is not None 