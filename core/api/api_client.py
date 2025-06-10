import os
import json
import aiohttp
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging
from urllib.parse import urljoin

from utils.logger import logger
from core.auth.security_manager import security_manager

class APIClient:
    def __init__(self):
        self.base_url = os.getenv("API_BASE_URL", "")
        self.api_key = os.getenv("API_KEY", "")
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = logging.getLogger("api_client")
        
        # Rate limiting
        self.rate_limit = int(os.getenv("API_RATE_LIMIT", "100"))
        self.rate_limit_window = int(os.getenv("API_RATE_LIMIT_WINDOW", "3600"))
        self.request_timestamps: List[datetime] = []
    
    async def __aenter__(self):
        """Create aiohttp session when entering context."""
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close aiohttp session when exiting context."""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits."""
        now = datetime.now()
        window_start = now - timedelta(seconds=self.rate_limit_window)
        
        # Remove old timestamps
        self.request_timestamps = [
            ts for ts in self.request_timestamps
            if ts > window_start
        ]
        
        if len(self.request_timestamps) >= self.rate_limit:
            return False
        
        self.request_timestamps.append(now)
        return True
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make an API request with rate limiting and error handling."""
        if not await self._check_rate_limit():
            raise Exception("Rate limit exceeded")
        
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
        
        url = urljoin(self.base_url, endpoint)
        
        try:
            async with self.session.request(
                method,
                url,
                json=data,
                params=params
            ) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            self.logger.error(f"API request failed: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise
    
    # Customer Management API
    async def create_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new customer."""
        return await self._make_request(
            "POST",
            "/customers",
            data=customer_data
        )
    
    async def get_customer(self, customer_id: str) -> Dict[str, Any]:
        """Get customer details."""
        return await self._make_request(
            "GET",
            f"/customers/{customer_id}"
        )
    
    async def update_customer(
        self,
        customer_id: str,
        customer_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update customer details."""
        return await self._make_request(
            "PUT",
            f"/customers/{customer_id}",
            data=customer_data
        )
    
    # Booking Management API
    async def create_booking(self, booking_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new booking."""
        return await self._make_request(
            "POST",
            "/bookings",
            data=booking_data
        )
    
    async def get_booking(self, booking_id: str) -> Dict[str, Any]:
        """Get booking details."""
        return await self._make_request(
            "GET",
            f"/bookings/{booking_id}"
        )
    
    async def update_booking(
        self,
        booking_id: str,
        booking_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update booking details."""
        return await self._make_request(
            "PUT",
            f"/bookings/{booking_id}",
            data=booking_data
        )
    
    async def cancel_booking(self, booking_id: str) -> Dict[str, Any]:
        """Cancel a booking."""
        return await self._make_request(
            "POST",
            f"/bookings/{booking_id}/cancel"
        )
    
    # Product Management API
    async def get_products(
        self,
        category: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> Dict[str, Any]:
        """Get list of products with optional filtering."""
        params = {
            "page": page,
            "limit": limit
        }
        if category:
            params["category"] = category
        
        return await self._make_request(
            "GET",
            "/products",
            params=params
        )
    
    async def get_product(self, product_id: str) -> Dict[str, Any]:
        """Get product details."""
        return await self._make_request(
            "GET",
            f"/products/{product_id}"
        )
    
    async def update_product_stock(
        self,
        product_id: str,
        stock_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update product stock levels."""
        return await self._make_request(
            "PUT",
            f"/products/{product_id}/stock",
            data=stock_data
        )
    
    # Analytics API
    async def get_sales_analytics(
        self,
        start_date: str,
        end_date: str,
        group_by: str = "day"
    ) -> Dict[str, Any]:
        """Get sales analytics data."""
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "group_by": group_by
        }
        
        return await self._make_request(
            "GET",
            "/analytics/sales",
            params=params
        )
    
    async def get_customer_analytics(
        self,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """Get customer analytics data."""
        params = {
            "start_date": start_date,
            "end_date": end_date
        }
        
        return await self._make_request(
            "GET",
            "/analytics/customers",
            params=params
        )
    
    # Notification API
    async def send_notification(
        self,
        notification_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send a notification."""
        return await self._make_request(
            "POST",
            "/notifications",
            data=notification_data
        )
    
    async def get_notification_status(
        self,
        notification_id: str
    ) -> Dict[str, Any]:
        """Get notification status."""
        return await self._make_request(
            "GET",
            f"/notifications/{notification_id}"
        )

# Create global API client instance
api_client = APIClient() 