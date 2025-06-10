from telegram import Update
from telegram.ext import ContextTypes
import random
import json
import os
import time
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from core.customer_management import (
    get_customer_profile,
    update_customer_profile,
    get_inactive_customers
)
from utils.logger import log_follow_up
from utils.memory_logger import log_customer_memory
from utils.follow_up_learning_tracker import log_follow_up_learning
from utils.vip_checker import is_vip_customer
from utils.follow_up_selector import get_follow_up_meta
from utils.auto_responder import generate_follow_up_response

# Path for tracking last follow-up
LAST_FOLLOW_UP_PATH = Path("data/last_follow_up.json")

def save_follow_up_context(
    customer_id: str,
    message: str,
    follow_up_type: str
) -> None:
    """Save follow-up context for tracking."""
    timestamp = int(time.time())
    hash_value = hashlib.md5(message.encode()).hexdigest()

    try:
        with open(LAST_FOLLOW_UP_PATH, "w", encoding="utf-8") as f:
            json.dump({
                "customer_id": customer_id,
                "message": message,
                "type": follow_up_type,
                "timestamp": timestamp,
                "hash": hash_value
            }, f, ensure_ascii=False, indent=2)
        print("🧠 [Context] last_follow_up.json saved")
    except Exception as e:
        print(f"❌ Failed to save follow-up context: {e}")

async def follow_up_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle customer follow-up interactions."""
    query = update.callback_query
    await query.answer()

    customer_id = str(update.effective_user.id)

    # Load customer profile
    customer = get_customer_profile(customer_id)
    if not customer:
        await context.bot.send_message(
            chat_id=customer_id,
            text="⚠️ Customer profile not found"
        )
        return

    # Determine follow-up type based on customer history
    follow_up_type = determine_follow_up_type(customer)
    follow_up_meta = get_follow_up_meta(follow_up_type)
    
    if not follow_up_meta or "messages" not in follow_up_meta:
        await context.bot.send_message(
            chat_id=customer_id,
            text="⚠️ No follow-up messages available"
        )
        return

    # Select and send follow-up message
    message = random.choice(follow_up_meta["messages"])
    await context.bot.send_message(chat_id=customer_id, text=message)

    # Log follow-up
    log_follow_up(customer_id, follow_up_type, message)
    save_follow_up_context(customer_id, message, follow_up_type)

    print(f"⚡ Sent follow-up to {customer_id}: {message}")

async def handle_follow_up_reply(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle customer responses to follow-ups."""
    message = update.message
    user = update.effective_user

    if not message or not user:
        return

    # Load last follow-up context
    if "last_follow_up" not in context.user_data:
        if LAST_FOLLOW_UP_PATH.exists():
            try:
                with open(LAST_FOLLOW_UP_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    context.user_data["last_follow_up"] = {
                        "message": data["message"],
                        "type": data["type"]
                    }
                    print("🧠 [Fallback] Loaded last follow-up context from file")
            except Exception as e:
                print(f"❌ Failed to load fallback follow-up context: {e}")
                return

    last_follow_up = context.user_data.get("last_follow_up")
    if not last_follow_up:
        return

    sent_message = last_follow_up.get("message")
    follow_up_type = last_follow_up.get("type")

    if sent_message and sent_message.lower() in message.text.lower():
        # Log customer response
        log_follow_up_learning(
            customer_id=user.id,
            message=message.text,
            follow_up_type=follow_up_type or "Unknown"
        )
        log_customer_memory(
            customer_id=user.id,
            sent_message=sent_message,
            reply_text=message.text
        )
        print(f"[🧠 MemoryLogger] ✅ Reply saved for customer {user.id}")

        # Check VIP status
        is_vip = is_vip_customer(user.id)
        print(f"🔐 VIP Check: Customer {user.id} is VIP: {is_vip}")

        # Generate and send response
        follow_up_meta = get_follow_up_meta(follow_up_type)
        follow_up_name = follow_up_meta.get("name", "Customer Care")
        follow_up_style = follow_up_meta.get("style", "professional and friendly")

        response = generate_follow_up_response(
            follow_up_type=follow_up_type,
            follow_up_name=follow_up_name,
            follow_up_style=follow_up_style,
            is_vip=is_vip
        )

        await context.bot.send_message(chat_id=user.id, text=response)
        print(f"[🤖 AutoResponder] ✅ Sent: {response}")

def determine_follow_up_type(customer: 'CustomerProfile') -> str:
    """Determine appropriate follow-up type based on customer profile."""
    if not customer.purchase_history:
        return "new_customer"
    
    last_purchase = customer.purchase_history[-1]
    purchase_date = datetime.fromisoformat(last_purchase.get("date", ""))
    days_since_purchase = (datetime.now() - purchase_date).days
    
    if days_since_purchase < 7:
        return "recent_purchase"
    elif days_since_purchase < 30:
        return "monthly_follow_up"
    elif days_since_purchase < 90:
        return "quarterly_follow_up"
    else:
        return "inactive_customer"

def schedule_follow_ups() -> None:
    """Schedule follow-ups for inactive customers."""
    inactive_customers = get_inactive_customers(days=30)
    
    for customer in inactive_customers:
        follow_up_type = determine_follow_up_type(customer)
        follow_up_meta = get_follow_up_meta(follow_up_type)
        
        if follow_up_meta and "messages" in follow_up_meta:
            message = random.choice(follow_up_meta["messages"])
            # Schedule follow-up message
            # Implementation depends on your scheduling system
            print(f"Scheduled follow-up for {customer.name}: {message}") 