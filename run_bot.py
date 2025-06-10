"""
Run Forever Siam Fashion Boutique chatbot
"""

import os
import logging
from dotenv import load_dotenv
import uvicorn
from integrations.facebook_messenger import app
from core.message_processor import MessageProcessor
from core.business_logic import BusinessLogic
from analytics.metrics_tracker import MetricsTracker
from core.chatbot_handler import ChatbotHandler
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chatbot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_environment():
    """Load and verify environment variables"""
    # Load from config.env
    load_dotenv('config.env')
    
    # Set default values if not present
    os.environ.setdefault('FB_VERIFY_TOKEN', 'forever_siam_verify_token')
    os.environ.setdefault('FB_PAGE_ACCESS_TOKEN', 'your_page_access_token_here')
    os.environ.setdefault('FB_APP_SECRET', 'your_app_secret_here')
    os.environ.setdefault('FB_PAGE_ID', 'your_page_id_here')
    os.environ.setdefault('HOST', '0.0.0.0')
    os.environ.setdefault('PORT', '8000')
    os.environ.setdefault('DEBUG', 'False')
    
    # Log environment status
    logger.info("Environment variables loaded:")
    logger.info(f"FB_VERIFY_TOKEN: {'Set' if os.getenv('FB_VERIFY_TOKEN') else 'Not set'}")
    logger.info(f"FB_PAGE_ACCESS_TOKEN: {'Set' if os.getenv('FB_PAGE_ACCESS_TOKEN') else 'Not set'}")
    logger.info(f"FB_APP_SECRET: {'Set' if os.getenv('FB_APP_SECRET') else 'Not set'}")
    logger.info(f"FB_PAGE_ID: {'Set' if os.getenv('FB_PAGE_ID') else 'Not set'}")

def initialize_components():
    """Initialize all required components"""
    try:
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
        
        logger.info("All components initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error initializing components: {str(e)}")
        return False

def main():
    """Main entry point"""
    try:
        # Parse command-line arguments
        parser = argparse.ArgumentParser()
        parser.add_argument('--port', type=int, default=None, help='Port to run the server on')
        args = parser.parse_args()

        # Load environment variables
        load_environment()
        
        # Initialize components
        if not initialize_components():
            logger.error("Failed to initialize components")
            return
            
        # Get server configuration
        host = os.getenv("HOST", "0.0.0.0")
        env_port = os.getenv("PORT")
        # Priority: CLI arg > env var > default
        port = args.port or (int(env_port) if env_port else 8001)
        reload = os.getenv("DEBUG", "False").lower() == "true"
        
        # Start server
        logger.info(f"Starting server on {host}:{port}")
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=reload
        )
        
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}")
        raise

if __name__ == "__main__":
    main() 