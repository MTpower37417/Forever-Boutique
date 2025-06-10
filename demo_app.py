"""
Forever Boutique Chatbot Demo Application
"""

from dotenv import load_dotenv
import os
import logging
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from core.chatbot_handler import ChatbotHandler
from core.message_processor import MessageProcessor
from core.business_logic import BusinessLogic
from analytics.metrics_tracker import MetricsTracker

# Load environment variables from config.env
load_dotenv('config.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Verify critical environment variables
required_vars = ['OPENAI_API_KEY', 'FB_PAGE_ACCESS_TOKEN', 'FB_VERIFY_TOKEN']
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    logger.error(f"Missing environment variables: {missing_vars}")
    raise ValueError(f"Required environment variables missing: {missing_vars}")

app = FastAPI(title="Forever Boutique Chat Demo")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize dependencies
try:
    message_processor = MessageProcessor()
    business_logic = BusinessLogic()
    metrics_tracker = MetricsTracker()

    # Initialize chatbot
    chatbot = ChatbotHandler(
        message_processor=message_processor,
        business_logic=business_logic,
        metrics_tracker=metrics_tracker
    )
    logger.info("All components initialized successfully")
except Exception as e:
    logger.error(f"Error initializing components: {str(e)}", exc_info=True)
    raise

# Mount templates
templates = Jinja2Templates(directory="templates")

class ChatMessage(BaseModel):
    message: str

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the chat interface"""
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        logger.error(f"Error serving root: {str(e)}", exc_info=True)
        raise

@app.post("/chat")
async def chat(message: ChatMessage):
    """Handle chat messages"""
    try:
        # Validate input
        if not message.message or not isinstance(message.message, str):
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid message format"},
                headers={"Content-Type": "application/json; charset=utf-8"}
            )

        # Process message through chatbot
        response = await chatbot.handle_message(
            platform="web",
            user_id="demo_user",
            message=message.message
        )
        
        # Track the interaction
        metrics_tracker.track_message_received("web", "demo_user")
        metrics_tracker.track_message_sent("web", "demo_user")
        
        return JSONResponse(
            content={"response": response},
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}\n{traceback.format_exc()}")
        metrics_tracker.track_error("chat_error", str(e))
        return JSONResponse(
            status_code=500,
            content={"error": "ขออภัยค่ะ เกิดข้อผิดพลาด กรุณาลองใหม่อีกครั้งค่ะ"},
            headers={"Content-Type": "application/json; charset=utf-8"}
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        return JSONResponse(
            content={
                "status": "healthy",
                "version": "1.0.0",
                "services": {
                    "chatbot": "operational",
                    "message_processor": "operational",
                    "business_logic": "operational",
                    "metrics_tracker": "operational"
                }
            }
        )
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"status": "unhealthy", "error": str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 