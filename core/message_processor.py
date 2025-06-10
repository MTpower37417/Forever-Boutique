"""
Message Processor
Handles message preprocessing and normalization
"""

import logging
import re
from typing import Dict, Any

logger = logging.getLogger(__name__)

class MessageProcessor:
    def __init__(self):
        logger.info("MessageProcessor initialized successfully")

    def process_message(self, message: str) -> str:
        """Process and normalize incoming message"""
        try:
            if not message or not isinstance(message, str):
                return ""

            # Remove extra whitespace
            message = message.strip()
            
            # Convert to lowercase for matching
            message = message.lower()
            
            # Remove special characters but keep Thai characters
            message = re.sub(r'[^\w\s\u0E00-\u0E7F]', '', message)
            
            return message
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            return message  # Return original message if processing fails 