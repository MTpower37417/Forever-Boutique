"""
Test Facebook Messenger integration
"""

import unittest
import json
import os
from datetime import datetime
import hmac
import hashlib
from fastapi.testclient import TestClient
from integrations.facebook_messenger import app, verify_signature

class TestFacebookIntegration(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.client = TestClient(app)
        self.test_message = {
            "object": "page",
            "entry": [{
                "id": "test_page_id",
                "messaging": [{
                    "sender": {"id": "test_user_id"},
                    "recipient": {"id": "test_page_id"},
                    "timestamp": int(datetime.now().timestamp()),
                    "message": {
                        "text": "มีชุดราตรีไหม?"
                    }
                }]
            }]
        }
        
        # Set test environment variables
        os.environ["FB_VERIFY_TOKEN"] = "test_verify_token"
        os.environ["FB_PAGE_ACCESS_TOKEN"] = "test_page_token"
        os.environ["FB_APP_SECRET"] = "test_app_secret"

    def test_webhook_verification(self):
        """Test webhook verification endpoint"""
        # Test successful verification
        response = self.client.get(
            "/webhook",
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": "test_verify_token",
                "hub.challenge": "test_challenge"
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, "test_challenge")
        
        # Test failed verification
        response = self.client.get(
            "/webhook",
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": "wrong_token",
                "hub.challenge": "test_challenge"
            }
        )
        self.assertEqual(response.status_code, 403)

    def test_signature_verification(self):
        """Test webhook signature verification"""
        # Create test signature
        test_body = json.dumps(self.test_message).encode()
        test_signature = hmac.new(
            "test_app_secret".encode(),
            test_body,
            hashlib.sha1
        ).hexdigest()
        
        # Test valid signature
        self.assertTrue(
            verify_signature(test_body, f"sha1={test_signature}")
        )
        
        # Test invalid signature
        self.assertFalse(
            verify_signature(test_body, "sha1=invalid_signature")
        )

    def test_webhook_message_handling(self):
        """Test webhook message handling"""
        # Create test signature
        test_body = json.dumps(self.test_message).encode()
        test_signature = hmac.new(
            "test_app_secret".encode(),
            test_body,
            hashlib.sha1
        ).hexdigest()
        
        # Test message handling
        response = self.client.post(
            "/webhook",
            json=self.test_message,
            headers={"X-Hub-Signature": f"sha1={test_signature}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_send_message(self):
        """Test sending message to Facebook"""
        # This test would require mocking the Facebook API
        # For now, we'll just verify the endpoint exists
        response = self.client.post(
            "/send-template",
            json={
                "recipient_id": "test_user_id",
                "template_name": "greeting",
                "template_data": {"name": "Test User"}
            }
        )
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main() 