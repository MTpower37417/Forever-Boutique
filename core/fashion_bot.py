import os
import asyncio
import logging
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    CallbackQueryHandler, ContextTypes, MessageHandler, filters
)
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv

from core.path_config import CONFIG_ENV
from core.start_handler import start
from core.menu_handler import fashion_menu
from core.customer_management import get_customer_profile, save_customer_profile
from core.menu_ui import open_fashion_menu, back_to_settings, close_menu
from core.main_menu_ui import main_menu_handler

from core.handlers.product_handler import product_handler
from core.handlers.booking_handler import booking_handler
from core.handlers.size_handler import size_handler
from core.handlers.faq_handler import faq_handler
from core.handlers.store_info_handler import store_info_handler
from core.handlers.customer_follow_up import follow_up_handler
from core.handlers.insight_handler import insight_handler
from core.handlers.set_time_action import set_time_action_handler
from core.handlers.help_handler import help_handler
from core.handlers.customer_response_handler import customer_response_handler
from core.handlers.ai_combined_reply_handler import hybrid_ai_handler
from core.handlers.admin_toggle_handler import toggle_system_status

from utils.customer_loader import get_customer_prompt

load_dotenv(CONFIG_ENV)

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

async def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    admin_id = os.getenv("TELEGRAM_ADMIN_ID")

    logging.info("🚀 Starting Forever Boutique bot with hybrid_ai_handler...")
    application = ApplicationBuilder().token(token).build()
    application.bot_data["ADMIN_ID"] = admin_id

    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", fashion_menu))
    application.add_handler(CommandHandler("products", product_handler))
    application.add_handler(CommandHandler("booking", booking_handler))
    application.add_handler(CommandHandler("size", size_handler))
    application.add_handler(CommandHandler("faq", faq_handler))
    application.add_handler(CommandHandler("store", store_info_handler))
    application.add_handler(CommandHandler("settings", set_time_action_handler))
    application.add_handler(CommandHandler("admin_menu", admin_menu_handler))
    application.add_handler(CommandHandler("help", help_handler))

    # Callback query handlers
    application.add_handler(CallbackQueryHandler(open_fashion_menu, pattern="^open_fashion_menu$"))
    application.add_handler(CallbackQueryHandler(customer_response_handler, pattern="^customer_"))
    application.add_handler(CallbackQueryHandler(close_menu, pattern="^close_menu$"))
    application.add_handler(CallbackQueryHandler(back_to_settings, pattern="^settings_back$"))
    application.add_handler(CallbackQueryHandler(main_menu_handler, pattern="^main_menu$"))
    application.add_handler(CallbackQueryHandler(admin_menu_handler, pattern="^admin_menu$"))
    application.add_handler(CallbackQueryHandler(follow_up_handler, pattern="^follow_up$"))
    application.add_handler(CallbackQueryHandler(product_handler, pattern="^product_"))
    application.add_handler(CallbackQueryHandler(booking_handler, pattern="^booking_"))
    application.add_handler(CallbackQueryHandler(size_handler, pattern="^size_"))
    application.add_handler(CallbackQueryHandler(faq_handler, pattern="^faq_"))
    application.add_handler(CallbackQueryHandler(store_info_handler, pattern="^store_"))
    application.add_handler(CallbackQueryHandler(insight_handler, pattern="^admin_insight_"))
    application.add_handler(CallbackQueryHandler(toggle_system_status, pattern="^toggle_system$"))

    # Message handler for general queries
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, hybrid_ai_handler)
    )

    await application.run_polling()

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.get_event_loop().run_until_complete(main()) 