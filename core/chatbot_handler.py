"""
Chatbot Handler
Manages message processing and response generation
"""

import logging
from typing import Dict, Any, Optional
from core.message_processor import MessageProcessor
from core.business_logic import BusinessLogic
from analytics.metrics_tracker import MetricsTracker
from core.simple_chatbot import get_simple_response

logger = logging.getLogger(__name__)

class ChatbotHandler:
    def __init__(
        self,
        message_processor: MessageProcessor,
        business_logic: BusinessLogic,
        metrics_tracker: MetricsTracker
    ):
        self.message_processor = message_processor
        self.business_logic = business_logic
        self.metrics_tracker = metrics_tracker
        logger.info("ChatbotHandler initialized successfully")

    async def handle_message(self, platform: str, user_id: str, message: str) -> str:
        """Process incoming message and generate response (simple mode override)"""
        try:
            # Simple chatbot always takes priority for demo
            return get_simple_response(message)
        except Exception as e:
            logger.error(f"Error in simple chatbot: {str(e)}", exc_info=True)
            return "ขออภัยค่ะ เกิดข้อผิดพลาด กรุณาลองใหม่อีกครั้งค่ะ"

    async def handle_product_inquiry(self, user_id: str, product_id: str) -> str:
        """Handle product-specific inquiries"""
        try:
            # Get product recommendations
            recommendations = await self.business_logic.get_product_recommendations(user_id)
            
            # Track product inquiry
            await self.business_logic.track_customer_interaction(
                user_id,
                'product_inquiry',
                {
                    'product_id': product_id,
                    'recommendations': recommendations
                }
            )
            
            return f"I can help you with information about product {product_id}. Would you like to know more about similar products?"
            
        except Exception as e:
            logger.error(f"Error handling product inquiry: {str(e)}")
            return "I apologize, but I'm having trouble retrieving product information. Please try again later."

    async def handle_lead_capture(self, user_id: str, lead_data: Dict) -> str:
        """Handle lead capture and qualification"""
        try:
            # Process lead data
            response = await self.business_logic.handle_customer_query(
                user_id,
                f"New lead: {lead_data}"
            )
            
            # Track lead capture
            await self.business_logic.track_customer_interaction(
                user_id,
                'lead_capture',
                lead_data
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling lead capture: {str(e)}")
            return "I apologize, but I'm having trouble processing your information. Please try again or contact our team directly."

    async def handle_feedback(self, user_id: str, feedback: str) -> str:
        """Handle customer feedback"""
        try:
            # Process feedback
            response = await self.business_logic.handle_customer_query(
                user_id,
                f"Feedback: {feedback}"
            )
            
            # Track feedback
            await self.business_logic.track_customer_interaction(
                user_id,
                'feedback',
                {'feedback': feedback}
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling feedback: {str(e)}")
            return "I apologize, but I'm having trouble processing your feedback. Please try again or contact our team directly."

    def get_conversation_history(self, user_id: str) -> list:
        """Get conversation history for a user"""
        return self.message_processor.get_conversation_history(user_id)