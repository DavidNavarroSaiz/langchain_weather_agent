import logging
import sys
from typing import Optional

def setup_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    Set up a logger with the specified name and level.
    
    Args:
        name: The name of the logger
        level: The logging level (defaults to INFO if not specified)
        
    Returns:
        A configured logger instance
    """
    if level is None:
        level = logging.INFO
        
    logger = logging.getLogger(name)
    
    # Only configure the logger if it hasn't been configured yet
    if not logger.handlers:
        logger.setLevel(level)
        
        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Add formatter to handler
        handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(handler)
        
        # Prevent propagation to the root logger
        logger.propagate = False
        
    return logger 