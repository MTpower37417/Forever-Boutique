"""
Metrics Tracker
Tracks and logs chatbot interactions and metrics
"""

import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

class MetricsTracker:
    def __init__(self):
        self.metrics = {
            'messages_received': 0,
            'messages_sent': 0,
            'errors': 0
        }
        logger.info("MetricsTracker initialized successfully")

    def track_message_received(self, platform: str, user_id: str):
        """Track received message"""
        try:
            self.metrics['messages_received'] += 1
            logger.info(f"Message received from {user_id} on {platform}")
        except Exception as e:
            logger.error(f"Error tracking received message: {str(e)}", exc_info=True)

    def track_message_sent(self, platform: str, user_id: str):
        """Track sent message"""
        try:
            self.metrics['messages_sent'] += 1
            logger.info(f"Message sent to {user_id} on {platform}")
        except Exception as e:
            logger.error(f"Error tracking sent message: {str(e)}", exc_info=True)

    def track_error(self, error_type: str, details: str):
        """Track error occurrence"""
        try:
            self.metrics['errors'] += 1
            logger.error(f"Error tracked: {error_type} - {details}")
        except Exception as e:
            logger.error(f"Error tracking error: {str(e)}", exc_info=True)

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return self.metrics.copy() 