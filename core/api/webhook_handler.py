import os
import json
import hmac
import hashlib
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import logging
from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from utils.logger import logger
from core.auth.security_manager import security_manager

app = FastAPI(title="Forever Boutique API")

class WebhookHandler:
    def __init__(self):
        self.webhook_secret = os.getenv("WEBHOOK_SECRET", "")
        self.handlers: Dict[str, Callable] = {}
        self.logger = logging.getLogger("webhook")
    
    def register_handler(self, event_type: str, handler: Callable) -> None:
        """Register a handler for a specific event type."""
        self.handlers[event_type] = handler
        self.logger.info(f"Registered handler for {event_type}")
    
    async def handle_webhook(self, request: Request) -> JSONResponse:
        """Handle incoming webhook requests."""
        try:
            # Verify webhook signature
            signature = request.headers.get("X-Webhook-Signature")
            if not self._verify_signature(request, signature):
                raise HTTPException(status_code=401, detail="Invalid signature")
            
            # Parse request body
            body = await request.json()
            event_type = body.get("type")
            
            if not event_type or event_type not in self.handlers:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported event type: {event_type}"
                )
            
            # Process event
            handler = self.handlers[event_type]
            result = await handler(body)
            
            return JSONResponse(content=result)
        except Exception as e:
            self.logger.error(f"Error handling webhook: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def _verify_signature(self, request: Request, signature: Optional[str]) -> bool:
        """Verify webhook signature."""
        if not self.webhook_secret or not signature:
            return False
        
        try:
            # Get request body
            body = await request.body()
            
            # Calculate expected signature
            expected = hmac.new(
                self.webhook_secret.encode(),
                body,
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected)
        except Exception as e:
            self.logger.error(f"Error verifying signature: {e}")
            return False

# Create webhook handler instance
webhook_handler = WebhookHandler()

# API Models
class WebhookEvent(BaseModel):
    type: str
    data: Dict[str, Any]
    timestamp: datetime

class WebhookResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

# API Routes
@app.post("/webhook")
async def handle_webhook(
    request: Request,
    x_webhook_signature: str = Header(None)
) -> WebhookResponse:
    """Handle incoming webhook requests."""
    return await webhook_handler.handle_webhook(request)

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Register event handlers
@webhook_handler.register_handler("customer.created")
async def handle_customer_created(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle customer creation event."""
    try:
        customer_data = event["data"]
        # Process customer creation
        logger.log_customer_event(
            customer_data["id"],
            "created",
            customer_data
        )
        return {"success": True, "message": "Customer created successfully"}
    except Exception as e:
        logger.log_error("customer_creation", str(e), event)
        return {"success": False, "message": str(e)}

@webhook_handler.register_handler("booking.created")
async def handle_booking_created(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle booking creation event."""
    try:
        booking_data = event["data"]
        # Process booking creation
        logger.log_booking_event(
            booking_data["id"],
            "created",
            booking_data
        )
        return {"success": True, "message": "Booking created successfully"}
    except Exception as e:
        logger.log_error("booking_creation", str(e), event)
        return {"success": False, "message": str(e)}

@webhook_handler.register_handler("product.updated")
async def handle_product_updated(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle product update event."""
    try:
        product_data = event["data"]
        # Process product update
        logger.log_product_event(
            product_data["id"],
            "updated",
            product_data
        )
        return {"success": True, "message": "Product updated successfully"}
    except Exception as e:
        logger.log_error("product_update", str(e), event)
        return {"success": False, "message": str(e)}

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.log_error("api_error", str(exc), {"path": request.url.path})
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "Internal server error"}
    ) 