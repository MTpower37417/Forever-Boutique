"""
Test suite for message processor of Forever Siam Fashion Boutique chatbot.
Tests message processing and response generation.
"""

import unittest
from datetime import datetime
from core.message_processor import MessageProcessor
from test_config import get_test_data

class TestMessageProcessor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.test_data = get_test_data()
        cls.processor = MessageProcessor()

    def test_process_message(self):
        """Test message processing"""
        # Test product inquiry
        response = self.processor.process_message(
            "มีชุดราตรีไหม?",
            "test_user"
        )
        self.assertIsNotNone(response)
        self.assertIn("Crystal Embellished Gown", response)
        
        # Test store location
        response = self.processor.process_message(
            "ร้านอยู่ที่ไหน?",
            "test_user"
        )
        self.assertIsNotNone(response)
        self.assertIn("Sukhumvit Road", response)
        
        # Test price range
        response = self.processor.process_message(
            "ราคาประมาณเท่าไหร่?",
            "test_user"
        )
        self.assertIsNotNone(response)
        self.assertIn("฿", response)

    def test_analyze_intent(self):
        """Test intent analysis"""
        # Test product intent
        intent = self.processor._analyze_intent("มีชุดราตรีไหม?")
        self.assertEqual(intent, "product_inquiry")
        
        # Test FAQ intent
        intent = self.processor._analyze_intent("ร้านเปิดกี่โมง?")
        self.assertEqual(intent, "faq")
        
        # Test size intent
        intent = self.processor._analyze_intent("ไซส์ M มีไหม?")
        self.assertEqual(intent, "size_inquiry")
        
        # Test booking intent
        intent = self.processor._analyze_intent("จองนัดลองชุดได้ไหม?")
        self.assertEqual(intent, "booking")

    def test_generate_response(self):
        """Test response generation"""
        # Test product response
        response = self.processor._generate_response(
            "product_inquiry",
            "ชุดราตรี",
            "test_user"
        )
        self.assertIsNotNone(response)
        self.assertIn("Crystal Embellished Gown", response)
        
        # Test FAQ response
        response = self.processor._generate_response(
            "faq",
            "hours",
            "test_user"
        )
        self.assertIsNotNone(response)
        self.assertIn("10:00-20:00", response)
        
        # Test size response
        response = self.processor._generate_response(
            "size_inquiry",
            "M",
            "test_user"
        )
        self.assertIsNotNone(response)
        self.assertIn("size M", response.lower())

    def test_extract_product_name(self):
        """Test product name extraction"""
        # Test direct product name
        product = self.processor._extract_product_name("มีชุดราตรีไหม?")
        self.assertEqual(product, "ชุดราตรี")
        
        # Test with additional context
        product = self.processor._extract_product_name(
            "อยากดูชุดราตรีสีดำ"
        )
        self.assertEqual(product, "ชุดราตรี")
        
        # Test with no product name
        product = self.processor._extract_product_name(
            "ร้านเปิดกี่โมง?"
        )
        self.assertIsNone(product)

    def test_format_product_response(self):
        """Test product response formatting"""
        product = {
            "name": "Crystal Embellished Gown",
            "price": 25000,
            "sizes": ["XS", "S", "M", "L"],
            "colors": ["black", "navy", "burgundy"]
        }
        
        response = self.processor._format_product_response(product)
        self.assertIsNotNone(response)
        self.assertIn("Crystal Embellished Gown", response)
        self.assertIn("฿25,000", response)
        self.assertIn("XS, S, M, L", response)
        self.assertIn("black, navy, burgundy", response)

    def test_handle_complaint(self):
        """Test complaint handling"""
        # Test valid complaint
        response = self.processor._handle_complaint(
            "ชุดที่สั่งมาสีไม่ตรงกับที่เห็นในรูป"
        )
        self.assertIsNotNone(response)
        self.assertIn("apologize", response.lower())
        self.assertIn("contact", response.lower())
        
        # Test invalid complaint
        response = self.processor._handle_complaint("")
        self.assertIsNotNone(response)
        self.assertIn("not understood", response.lower())

    def test_handle_lead_generation(self):
        """Test lead generation handling"""
        # Test valid lead request
        response = self.processor._handle_lead_generation(
            "สนใจชุดราตรี ราคา 20000-30000"
        )
        self.assertIsNotNone(response)
        self.assertIn("contact", response.lower())
        self.assertIn("name", response.lower())
        
        # Test invalid lead request
        response = self.processor._handle_lead_generation("")
        self.assertIsNotNone(response)
        self.assertIn("not understood", response.lower())

    def test_handle_general_inquiry(self):
        """Test general inquiry handling"""
        # Test valid inquiry
        response = self.processor._handle_general_inquiry(
            "มีโปรโมชั่นอะไรบ้าง?"
        )
        self.assertIsNotNone(response)
        self.assertIn("promotion", response.lower())
        
        # Test invalid inquiry
        response = self.processor._handle_general_inquiry("")
        self.assertIsNotNone(response)
        self.assertIn("not understood", response.lower())

    def test_conversation_history(self):
        """Test conversation history tracking"""
        # Add message to history
        self.processor._update_conversation_history(
            "test_user",
            "มีชุดราตรีไหม?",
            "Here are our evening wear options..."
        )
        
        # Get history
        history = self.processor.get_conversation_history("test_user")
        self.assertIsNotNone(history)
        self.assertEqual(len(history), 1)
        
        # Verify message content
        message = history[0]
        self.assertEqual(message["user_message"], "มีชุดราตรีไหม?")
        self.assertEqual(
            message["bot_response"],
            "Here are our evening wear options..."
        )

if __name__ == "__main__":
    unittest.main() 