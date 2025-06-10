"""
Test suite for Forever Siam Fashion Boutique chatbot.
Tests core functionality and conversation flows.
"""

import unittest
import json
import os
from datetime import datetime
from typing import Dict, Any

from core.chatbot_handler import ChatbotHandler
from core.business_logic import BusinessLogic
from core.product_recommender import ProductRecommender
from core.size_advisor import SizeAdvisor
from core.booking_system import BookingSystem
from core.customer_segmentation import CustomerSegmentation
from integrations.response_templates import ResponseTemplates

class TestForeverBoutiqueChatbot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        # Initialize components
        cls.chatbot = ChatbotHandler()
        cls.business_logic = BusinessLogic()
        cls.product_recommender = ProductRecommender()
        cls.size_advisor = SizeAdvisor()
        cls.booking_system = BookingSystem()
        cls.customer_segmentation = CustomerSegmentation()
        
        # Load test data
        cls.load_test_data()

    @classmethod
    def load_test_data(cls):
        """Load test data from files"""
        try:
            # Load store info
            with open("data/store_info.json", "r", encoding="utf-8") as f:
                cls.store_info = json.load(f)
            
            # Load products
            with open("data/products.json", "r", encoding="utf-8") as f:
                cls.products = json.load(f)
            
            # Load FAQs
            with open("data/faqs.json", "r", encoding="utf-8") as f:
                cls.faqs = json.load(f)
            
            # Load size guide
            with open("data/size_guide.json", "r", encoding="utf-8") as f:
                cls.size_guide = json.load(f)
        except Exception as e:
            print(f"Error loading test data: {str(e)}")
            raise

    def test_project_structure(self):
        """Test project structure and file existence"""
        required_files = [
            "main.py",
            "core/business_logic.py",
            "core/chatbot_handler.py",
            "core/product_recommender.py",
            "core/size_advisor.py",
            "core/booking_system.py",
            "core/customer_segmentation.py",
            "data/products.json",
            "data/faqs.json",
            "data/store_info.json",
            "data/size_guide.json"
        ]
        
        for file_path in required_files:
            self.assertTrue(
                os.path.exists(file_path),
                f"Required file not found: {file_path}"
            )

    def test_store_location_query(self):
        """Test store location query response"""
        # Test Thai query
        response = self.chatbot.handle_message(
            platform="test",
            user_id="test_user",
            message="ร้านอยู่ที่ไหน?"
        )
        
        # Verify response contains location information
        self.assertIn("Sukhumvit Road", response)
        self.assertIn("Bangkok", response)
        self.assertIn("BTS", response)
        self.assertIn("MRT", response)

    def test_price_range_query(self):
        """Test price range query response"""
        # Test Thai query
        response = self.chatbot.handle_message(
            platform="test",
            user_id="test_user",
            message="ราคาประมาณเท่าไหร่?"
        )
        
        # Verify response contains price information
        self.assertIn("฿", response)
        self.assertIn("evening wear", response.lower())
        self.assertIn("cocktail dresses", response.lower())

    def test_product_recommendation(self):
        """Test product recommendation system"""
        # Test Thai query for evening wear
        response = self.chatbot.handle_message(
            platform="test",
            user_id="test_user",
            message="มีชุดราตรีไหม?"
        )
        
        # Verify response contains product recommendations
        self.assertIn("Crystal Embellished Gown", response)
        self.assertIn("Silk Chiffon Maxi", response)
        self.assertIn("price", response.lower())

    def test_size_availability(self):
        """Test size availability check"""
        # Test Thai query for size M
        response = self.chatbot.handle_message(
            platform="test",
            user_id="test_user",
            message="ไซส์ M มีไหม?"
        )
        
        # Verify response contains size information
        self.assertIn("size M", response.lower())
        self.assertIn("available", response.lower())
        self.assertIn("measurements", response.lower())

    def test_booking_appointment(self):
        """Test appointment booking flow"""
        # Test booking request
        response = self.chatbot.handle_message(
            platform="test",
            user_id="test_user",
            message="จองนัดลองชุดได้ไหม?"
        )
        
        # Verify response contains booking information
        self.assertIn("appointment", response.lower())
        self.assertIn("available", response.lower())
        self.assertIn("duration", response.lower())

    def test_faq_responses(self):
        """Test FAQ response system"""
        # Test common questions
        test_questions = {
            "ร้านเปิดกี่โมง?": "hours",
            "รับบัตรเครดิตไหม?": "payment",
            "มีการแก้ไขชุดไหม?": "alterations",
            "ส่งของได้ไหม?": "delivery"
        }
        
        for question, category in test_questions.items():
            response = self.chatbot.handle_message(
                platform="test",
                user_id="test_user",
                message=question
            )
            
            # Verify response contains relevant information
            self.assertIn(
                self.faqs[category]["answer"].lower(),
                response.lower()
            )

    def test_size_advisor(self):
        """Test size advisor functionality"""
        # Test size recommendation
        measurements = {
            "bust": 86,
            "waist": 66,
            "hips": 91,
            "height": 165,
            "unit": "cm"
        }
        
        recommendation = self.size_advisor.get_size_recommendation(measurements)
        
        # Verify recommendation
        self.assertIsNotNone(recommendation)
        self.assertIn(recommendation.recommended_size, ["XS", "S", "M", "L", "XL"])
        self.assertTrue(0 <= recommendation.confidence_score <= 1)

    def test_product_recommender(self):
        """Test product recommendation system"""
        # Test occasion-based recommendation
        recommendations = self.product_recommender.get_recommendations(
            occasion="wedding",
            budget_range={"min": 10000, "max": 30000}
        )
        
        # Verify recommendations
        self.assertGreater(len(recommendations), 0)
        for rec in recommendations:
            self.assertIn(rec.product_id, ["EW001", "EW002", "CD001"])
            self.assertTrue(
                rec.price_range["min"] >= 10000 and
                rec.price_range["max"] <= 30000
            )

    def test_customer_segmentation(self):
        """Test customer segmentation system"""
        # Test customer profile creation
        customer = self.customer_segmentation.add_customer(
            name="Test Customer",
            phone="0812345678",
            email="test@example.com"
        )
        
        # Verify customer profile
        self.assertIsNotNone(customer)
        self.assertEqual(customer.segment, "new")
        self.assertEqual(customer.total_purchases, 0)

    def test_error_handling(self):
        """Test error handling"""
        # Test invalid message
        response = self.chatbot.handle_message(
            platform="test",
            user_id="test_user",
            message=""
        )
        
        # Verify error response
        self.assertIn("not understood", response.lower())
        self.assertIn("help", response.lower())

        # Test invalid size query
        response = self.chatbot.handle_message(
            platform="test",
            user_id="test_user",
            message="ไซส์ XXX มีไหม?"
        )
        
        # Verify error response
        self.assertIn("not available", response.lower())
        self.assertIn("size guide", response.lower())

if __name__ == "__main__":
    unittest.main() 