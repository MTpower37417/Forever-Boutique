"""
Forever Boutique AI Chatbot
Main entry point for the business chatbot system
"""

import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from integrations.facebook_messenger import app as messenger_app
from core.chatbot_handler import ChatbotHandler
from core.message_processor import MessageProcessor
from core.business_logic import BusinessLogic
from integrations.line_official import LineOfficial
from integrations.website_chat import WebsiteChat
from analytics.metrics_tracker import MetricsTracker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Forever Boutique Chatbot")

# Initialize dependencies
message_processor = MessageProcessor()
business_logic = BusinessLogic()
metrics_tracker = MetricsTracker()

# Initialize chatbot
chatbot = ChatbotHandler(
    message_processor=message_processor,
    business_logic=business_logic,
    metrics_tracker=metrics_tracker
)

# Mount Facebook Messenger routes
app.mount("/webhook", messenger_app)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(
        content={
            "status": "healthy",
            "version": "1.0.0",
            "services": {
                "chatbot": "operational",
                "facebook_messenger": "operational"
            }
        }
    )

@app.get("/")
async def root():
    """Root endpoint"""
    return JSONResponse(
        content={
            "message": "Forever Boutique Chatbot API",
            "status": "operational",
            "endpoints": {
                "health": "/health",
                "webhook": "/webhook"
            }
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 