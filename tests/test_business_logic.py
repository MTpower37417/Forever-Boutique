"""
Test suite for business logic of Forever Siam Fashion Boutique chatbot.
Tests core business functionality and data handling.
"""

import unittest
import json
import os
from datetime import datetime
from core.business_logic import BusinessLogic
from test_config import get_test_data

class TestBusinessLogic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.test_data = get_test_data()
        cls.business_logic = BusinessLogic()

    def test_load_products(self):
        """Test product data loading"""
        products = self.business_logic.load_products()
        self.assertIsNotNone(products)
        self.assertGreater(len(products), 0)
        
        # Verify product structure
        test_product = products[0]
        self.assertIn("product_id", test_product)
        self.assertIn("name", test_product)
        self.assertIn("price", test_product)
        self.assertIn("sizes", test_product)

    def test_load_faqs(self):
        """Test FAQ data loading"""
        faqs = self.business_logic.load_faqs()
        self.assertIsNotNone(faqs)
        self.assertGreater(len(faqs), 0)
        
        # Verify FAQ structure
        test_faq = faqs["hours"]
        self.assertIn("question", test_faq)
        self.assertIn("answer", test_faq)
        self.assertIn("category", test_faq)

    def test_load_customer_data(self):
        """Test customer data loading"""
        customer_data = self.business_logic.load_customer_data()
        self.assertIsNotNone(customer_data)
        
        # Verify customer data structure
        if customer_data:
            test_customer = customer_data[0]
            self.assertIn("name", test_customer)
            self.assertIn("phone", test_customer)
            self.assertIn("email", test_customer)

    def test_handle_customer_query(self):
        """Test customer query handling"""
        # Test product query
        response = self.business_logic.handle_customer_query(
            "มีชุดราตรีไหม?",
            "test_user"
        )
        self.assertIsNotNone(response)
        self.assertIn("Crystal Embellished Gown", response)
        
        # Test FAQ query
        response = self.business_logic.handle_customer_query(
            "ร้านเปิดกี่โมง?",
            "test_user"
        )
        self.assertIsNotNone(response)
        self.assertIn("10:00-20:00", response)
        
        # Test size query
        response = self.business_logic.handle_customer_query(
            "ไซส์ M มีไหม?",
            "test_user"
        )
        self.assertIsNotNone(response)
        self.assertIn("size M", response.lower())

    def test_store_lead(self):
        """Test lead storage"""
        lead_data = {
            "name": "Test Lead",
            "phone": "0812345678",
            "email": "test@example.com",
            "interest": "wedding dress",
            "budget": "20000-30000"
        }
        
        success = self.business_logic.store_lead(lead_data)
        self.assertTrue(success)
        
        # Verify lead was stored
        customer_data = self.business_logic.load_customer_data()
        self.assertIsNotNone(customer_data)
        
        # Find stored lead
        stored_lead = next(
            (c for c in customer_data if c["phone"] == lead_data["phone"]),
            None
        )
        self.assertIsNotNone(stored_lead)
        self.assertEqual(stored_lead["name"], lead_data["name"])

    def test_track_customer_interaction(self):
        """Test customer interaction tracking"""
        interaction_data = {
            "customer_id": "test_user",
            "interaction_type": "product_inquiry",
            "product_id": "EW001",
            "timestamp": datetime.now().isoformat()
        }
        
        success = self.business_logic.track_customer_interaction(
            interaction_data
        )
        self.assertTrue(success)
        
        # Verify interaction was tracked
        customer_data = self.business_logic.load_customer_data()
        self.assertIsNotNone(customer_data)
        
        # Find customer
        customer = next(
            (c for c in customer_data if c["customer_id"] == "test_user"),
            None
        )
        self.assertIsNotNone(customer)
        self.assertIn("interactions", customer)

    def test_error_handling(self):
        """Test error handling"""
        # Test invalid query
        response = self.business_logic.handle_customer_query(
            "",
            "test_user"
        )
        self.assertIsNotNone(response)
        self.assertIn("not understood", response.lower())
        
        # Test invalid lead data
        invalid_lead = {
            "name": "Test Lead"
            # Missing required fields
        }
        
        success = self.business_logic.store_lead(invalid_lead)
        self.assertFalse(success)

    def test_data_persistence(self):
        """Test data persistence"""
        # Test product data persistence
        products = self.business_logic.load_products()
        self.assertIsNotNone(products)
        
        # Test FAQ data persistence
        faqs = self.business_logic.load_faqs()
        self.assertIsNotNone(faqs)
        
        # Test customer data persistence
        customer_data = self.business_logic.load_customer_data()
        self.assertIsNotNone(customer_data)

if __name__ == "__main__":
    unittest.main() 