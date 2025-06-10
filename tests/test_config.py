"""
Test configuration for Forever Siam Fashion Boutique chatbot.
Contains test data and settings for unit tests.
"""

import os
from typing import Dict, Any

# Test environment settings
TEST_ENV = {
    "STORE_NAME": "Forever Siam Fashion Boutique",
    "STORE_LOCATION": "Sukhumvit Road, Bangkok",
    "CONTACT_PHONE": "0812345678",
    "CONTACT_EMAIL": "test@foreversiam.com",
    "OPENING_HOURS": "10:00-20:00",
    "TEST_MODE": True
}

# Test customer data
TEST_CUSTOMER = {
    "name": "Test Customer",
    "phone": "0812345678",
    "email": "test@example.com",
    "measurements": {
        "bust": 86,
        "waist": 66,
        "hips": 91,
        "height": 165,
        "unit": "cm"
    }
}

# Test appointment data
TEST_APPOINTMENT = {
    "customer_name": "Test Customer",
    "phone": "0812345678",
    "email": "test@example.com",
    "date": "2024-02-20",
    "time": "14:00",
    "duration": 60,
    "party_size": 2,
    "purpose": "wedding dress fitting",
    "notes": "Test appointment"
}

# Test product data
TEST_PRODUCT = {
    "product_id": "EW001",
    "name": "Crystal Embellished Gown",
    "category": "evening_wear",
    "price": 25000,
    "sizes": ["XS", "S", "M", "L"],
    "colors": ["black", "navy", "burgundy"],
    "description": "Test product description"
}

# Test FAQ data
TEST_FAQ = {
    "question": "ร้านเปิดกี่โมง?",
    "answer": "ร้านเปิดทุกวัน 10:00-20:00 น.",
    "category": "hours"
}

# Test size guide data
TEST_SIZE_GUIDE = {
    "size": "M",
    "measurements": {
        "bust": {"min": 86, "max": 91},
        "waist": {"min": 66, "max": 71},
        "hips": {"min": 91, "max": 96}
    },
    "height_range": {"min": 160, "max": 170}
}

# Test response templates
TEST_RESPONSES = {
    "greeting": "สวัสดีค่ะ ยินดีต้อนรับสู่ Forever Siam Fashion Boutique",
    "farewell": "ขอบคุณที่แวะมาใช้บริการค่ะ",
    "error": "ขออภัยค่ะ ไม่สามารถเข้าใจคำถามได้",
    "help": "สามารถสอบถามเกี่ยวกับสินค้า ราคา และการนัดหมายได้ค่ะ"
}

def get_test_data() -> Dict[str, Any]:
    """Get all test data"""
    return {
        "env": TEST_ENV,
        "customer": TEST_CUSTOMER,
        "appointment": TEST_APPOINTMENT,
        "product": TEST_PRODUCT,
        "faq": TEST_FAQ,
        "size_guide": TEST_SIZE_GUIDE,
        "responses": TEST_RESPONSES
    }

def setup_test_environment():
    """Set up test environment variables"""
    for key, value in TEST_ENV.items():
        os.environ[key] = str(value) 