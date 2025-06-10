"""
Test suite for main entry point of Forever Siam Fashion Boutique chatbot.
Tests initialization and basic functionality.
"""

import unittest
import asyncio
import os
from main import ForeverBoutiqueBot
from test_config import setup_test_environment

class TestMainEntryPoint(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        setup_test_environment()
        cls.bot = ForeverBoutiqueBot()

    def test_initialization(self):
        """Test bot initialization"""
        self.assertIsNotNone(self.bot)
        self.assertIsNotNone(self.bot.message_processor)
        self.assertIsNotNone(self.bot.business_logic)
        self.assertIsNotNone(self.bot.metrics_tracker)

    def test_environment_variables(self):
        """Test environment variables"""
        self.assertEqual(
            os.getenv("STORE_NAME"),
            "Forever Siam Fashion Boutique"
        )
        self.assertEqual(
            os.getenv("STORE_LOCATION"),
            "Sukhumvit Road, Bangkok"
        )
        self.assertEqual(
            os.getenv("CONTACT_PHONE"),
            "0812345678"
        )

    async def test_start_bot(self):
        """Test bot startup"""
        try:
            await self.bot.start()
            self.assertTrue(self.bot.is_running)
        finally:
            await self.bot.stop()

    async def test_stop_bot(self):
        """Test bot shutdown"""
        await self.bot.start()
        await self.bot.stop()
        self.assertFalse(self.bot.is_running)

    def test_imports(self):
        """Test all required imports"""
        try:
            from core.business_logic import BusinessLogic
            from core.message_processor import MessageProcessor
            from core.product_recommender import ProductRecommender
            from core.size_advisor import SizeAdvisor
            from core.booking_system import BookingSystem
            from core.customer_segmentation import CustomerSegmentation
            from integrations.facebook_messenger import FacebookMessenger
            from integrations.response_templates import ResponseTemplates
            from integrations.lead_capture import LeadCapture
        except ImportError as e:
            self.fail(f"Failed to import required module: {str(e)}")

    def test_file_structure(self):
        """Test project file structure"""
        required_dirs = [
            "core",
            "data",
            "integrations",
            "tests",
            "templates",
            "analytics"
        ]
        
        for dir_name in required_dirs:
            self.assertTrue(
                os.path.isdir(dir_name),
                f"Required directory not found: {dir_name}"
            )

    def test_data_files(self):
        """Test data file existence"""
        required_files = [
            "data/products.json",
            "data/faqs.json",
            "data/store_info.json",
            "data/size_guide.json"
        ]
        
        for file_path in required_files:
            self.assertTrue(
                os.path.isfile(file_path),
                f"Required file not found: {file_path}"
            )

    def test_config_files(self):
        """Test configuration file existence"""
        required_files = [
            "config.env",
            "requirements.txt",
            "README.md"
        ]
        
        for file_path in required_files:
            self.assertTrue(
                os.path.isfile(file_path),
                f"Required file not found: {file_path}"
            )

if __name__ == "__main__":
    unittest.main() 