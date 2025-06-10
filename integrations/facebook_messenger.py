import json
import logging
import hmac
import hashlib
import os
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request, Response, Header, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import aiohttp
from core.chatbot_handler import ChatbotHandler
from core.message_processor import MessageProcessor
from core.business_logic import BusinessLogic
from analytics.metrics_tracker import MetricsTracker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Forever Siam Facebook Messenger Bot")

# Initialize dependencies
message_processor = MessageProcessor()
business_logic = BusinessLogic()
metrics_tracker = MetricsTracker()

# Initialize chatbot with dependencies
chatbot = ChatbotHandler(
    message_processor=message_processor,
    business_logic=business_logic,
    metrics_tracker=metrics_tracker
)

# Facebook configuration
FB_VERIFY_TOKEN = os.getenv("FB_VERIFY_TOKEN", "forever_siam_verify_token")
FB_PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")
FB_APP_SECRET = os.getenv("FB_APP_SECRET")
FB_API_VERSION = "v18.0"
FB_API_URL = f"https://graph.facebook.com/{FB_API_VERSION}"

class MessengerMessage(BaseModel):
    """Model for Facebook Messenger message data"""
    sender_id: str
    message_text: str
    timestamp: int
    page_id: str

class WebhookData(BaseModel):
    """Model for Facebook webhook data"""
    object: str
    entry: list

def verify_signature(request_body: bytes, signature: str) -> bool:
    """Verify Facebook webhook signature"""
    if not FB_APP_SECRET:
        logger.warning("FB_APP_SECRET not set, skipping signature verification")
        return True
        
    expected_signature = hmac.new(
        FB_APP_SECRET.encode('utf-8'),
        request_body,
        hashlib.sha1
    ).hexdigest()
    
    return hmac.compare_digest(f"sha1={expected_signature}", signature)

@app.get("/webhook")
async def verify_webhook(request: Request):
    """Verify webhook for Facebook Messenger"""
    try:
        # Get verification parameters
        mode = request.query_params.get("hub.mode")
        token = request.query_params.get("hub.verify_token")
        challenge = request.query_params.get("hub.challenge")

        # Verify token
        if mode and token:
            if mode == "subscribe" and token == FB_VERIFY_TOKEN:
                return Response(content=challenge, media_type="text/plain")
            return JSONResponse(
                status_code=403,
                content={"error": "Verification failed"}
            )
    except Exception as e:
        logger.error(f"Webhook verification error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )

@app.post("/webhook")
async def webhook(
    request: Request,
    x_hub_signature: str = Header(None)
):
    """Handle incoming messages from Facebook Messenger"""
    try:
        # Get request body for signature verification
        body = await request.body()
        
        # Verify signature if app secret is configured
        if FB_APP_SECRET and not verify_signature(body, x_hub_signature):
            raise HTTPException(status_code=403, detail="Invalid signature")
            
        # Parse webhook data
        data = await request.json()
        webhook_data = WebhookData(**data)

        # Process each entry
        for entry in webhook_data.entry:
            for event in entry.get("messaging", []):
                # Extract message data
                sender_id = event["sender"]["id"]
                message = event.get("message", {})
                
                if "text" in message:
                    # Create message object
                    messenger_message = MessengerMessage(
                        sender_id=sender_id,
                        message_text=message["text"],
                        timestamp=event["timestamp"],
                        page_id=entry["id"]
                    )
                    
                    # Process message
                    await process_message(messenger_message)

        return JSONResponse(content={"status": "ok"})
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )

async def process_message(message: MessengerMessage):
    """Process incoming message and generate response"""
    try:
        # Track message received
        metrics_tracker.track_message_received("facebook", message.sender_id)

        # Process message through chatbot
        response = await chatbot.handle_message(
            platform="facebook",
            user_id=message.sender_id,
            message=message.message_text
        )

        # Send response back to user
        await send_message(message.sender_id, response)

        # Track message sent
        metrics_tracker.track_message_sent("facebook", message.sender_id)
    except Exception as e:
        logger.error(f"Message processing error: {str(e)}")
        # Send error message to user
        await send_message(
            message.sender_id,
            "I apologize, but I'm having trouble processing your request. Please try again later."
        )

async def send_message(recipient_id: str, message_text: str):
    """Send message to Facebook user using Graph API"""
    if not FB_PAGE_ACCESS_TOKEN:
        logger.error("FB_PAGE_ACCESS_TOKEN not configured")
        return
        
    try:
        url = f"{FB_API_URL}/me/messages"
        headers = {
            "Authorization": f"Bearer {FB_PAGE_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        data = {
            "recipient": {"id": recipient_id},
            "message": {"text": message_text}
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Facebook API error: {error_text}")
                    raise Exception(f"Facebook API error: {error_text}")
                    
                result = await response.json()
                logger.info(f"Message sent successfully: {result}")
                
        # Track message sent
        metrics_tracker.track_message_sent("facebook", recipient_id)
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        raise

@app.post("/send-template")
async def send_template_message(recipient_id: str, template_name: str, template_data: Dict[str, Any]):
    """Send template message to Facebook user"""
    try:
        # Load template
        template = load_template(template_name)
        
        # Fill template with data
        filled_template = fill_template(template, template_data)
        
        # Send template message
        await send_message(recipient_id, filled_template)
        
        return JSONResponse(content={"status": "ok"})
    except Exception as e:
        logger.error(f"Template message error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to send template message"}
        )

def load_template(template_name: str) -> Dict[str, Any]:
    """Load message template from file"""
    try:
        with open(f"templates/facebook/{template_name}.json", "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading template: {str(e)}")
        raise

def fill_template(template: Dict[str, Any], data: Dict[str, Any]) -> str:
    """Fill template with provided data"""
    try:
        # Replace placeholders in template with actual data
        message = template["message"]
        for key, value in data.items():
            message = message.replace(f"{{{key}}}", str(value))
        return message
    except Exception as e:
        logger.error(f"Error filling template: {str(e)}")
        raise

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 