import os
import json
import telebot
from datetime import datetime, timedelta
from typing import Dict, List, Optional

bot = telebot.TeleBot(os.getenv("TELEGRAM_BOT_TOKEN"))
chat_id = os.getenv("TELEGRAM_CHAT_ID")
CUSTOMER_FILE = "data/customers.json"

class CustomerProfile:
    def __init__(
        self,
        customer_id: str,
        name: str,
        phone: str,
        email: str,
        measurements: Dict[str, float],
        preferences: List[str],
        purchase_history: List[Dict],
        last_visit: Optional[datetime] = None,
        loyalty_points: int = 0
    ):
        self.customer_id = customer_id
        self.name = name
        self.phone = phone
        self.email = email
        self.measurements = measurements
        self.preferences = preferences
        self.purchase_history = purchase_history
        self.last_visit = last_visit or datetime.now()
        self.loyalty_points = loyalty_points

    def to_dict(self) -> Dict:
        return {
            "customer_id": self.customer_id,
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "measurements": self.measurements,
            "preferences": self.preferences,
            "purchase_history": self.purchase_history,
            "last_visit": self.last_visit.isoformat(),
            "loyalty_points": self.loyalty_points
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'CustomerProfile':
        return cls(
            customer_id=data["customer_id"],
            name=data["name"],
            phone=data["phone"],
            email=data["email"],
            measurements=data["measurements"],
            preferences=data["preferences"],
            purchase_history=data["purchase_history"],
            last_visit=datetime.fromisoformat(data["last_visit"]),
            loyalty_points=data["loyalty_points"]
        )

def load_customers() -> Dict[str, CustomerProfile]:
    """Load customer data from JSON file."""
    if not os.path.exists(CUSTOMER_FILE):
        return {}
    
    with open(CUSTOMER_FILE, "r") as f:
        data = json.load(f)
        return {
            customer_id: CustomerProfile.from_dict(customer_data)
            for customer_id, customer_data in data.items()
        }

def save_customers(customers: Dict[str, CustomerProfile]) -> None:
    """Save customer data to JSON file."""
    os.makedirs(os.path.dirname(CUSTOMER_FILE), exist_ok=True)
    with open(CUSTOMER_FILE, "w") as f:
        json.dump(
            {customer_id: customer.to_dict() 
             for customer_id, customer in customers.items()},
            f,
            indent=4
        )

def add_customer(
    customer_id: str,
    name: str,
    phone: str,
    email: str,
    measurements: Dict[str, float],
    preferences: List[str]
) -> CustomerProfile:
    """Add a new customer to the system."""
    customers = load_customers()
    
    if customer_id in customers:
        raise ValueError(f"Customer {customer_id} already exists")
    
    customer = CustomerProfile(
        customer_id=customer_id,
        name=name,
        phone=phone,
        email=email,
        measurements=measurements,
        preferences=preferences,
        purchase_history=[]
    )
    
    customers[customer_id] = customer
    save_customers(customers)
    
    bot.send_message(
        chat_id,
        f"✅ New customer added: {name}\n"
        f"Phone: {phone}\n"
        f"Email: {email}\n"
        f"Preferences: {', '.join(preferences)}"
    )
    
    return customer

def update_customer_profile(
    customer_id: str,
    **updates
) -> CustomerProfile:
    """Update customer profile information."""
    customers = load_customers()
    
    if customer_id not in customers:
        raise ValueError(f"Customer {customer_id} not found")
    
    customer = customers[customer_id]
    
    # Update provided fields
    for key, value in updates.items():
        if hasattr(customer, key):
            setattr(customer, key, value)
    
    customer.last_visit = datetime.now()
    save_customers(customers)
    
    bot.send_message(
        chat_id,
        f"✅ Updated profile for {customer.name}\n"
        f"Last visit: {customer.last_visit.strftime('%Y-%m-%d %H:%M')}"
    )
    
    return customer

def add_purchase(
    customer_id: str,
    purchase_data: Dict
) -> CustomerProfile:
    """Record a new purchase for a customer."""
    customers = load_customers()
    
    if customer_id not in customers:
        raise ValueError(f"Customer {customer_id} not found")
    
    customer = customers[customer_id]
    customer.purchase_history.append(purchase_data)
    
    # Add loyalty points (1 point per 100 baht)
    amount = purchase_data.get("amount", 0)
    points = int(amount / 100)
    customer.loyalty_points += points
    
    customer.last_visit = datetime.now()
    save_customers(customers)
    
    bot.send_message(
        chat_id,
        f"✅ New purchase recorded for {customer.name}\n"
        f"Amount: {amount} baht\n"
        f"Points earned: {points}\n"
        f"Total points: {customer.loyalty_points}"
    )
    
    return customer

def get_customer_profile(customer_id: str) -> Optional[CustomerProfile]:
    """Get customer profile by ID."""
    customers = load_customers()
    return customers.get(customer_id)

def get_inactive_customers(days: int = 30) -> List[CustomerProfile]:
    """Get list of customers who haven't visited in specified days."""
    customers = load_customers()
    cutoff_date = datetime.now() - timedelta(days=days)
    
    return [
        customer for customer in customers.values()
        if customer.last_visit < cutoff_date
    ]

def cleanup_inactive_customers(days: int = 365) -> None:
    """Remove customers who haven't visited in over a year."""
    customers = load_customers()
    cutoff_date = datetime.now() - timedelta(days=days)
    
    inactive_customers = [
        customer_id for customer_id, customer in customers.items()
        if customer.last_visit < cutoff_date
    ]
    
    for customer_id in inactive_customers:
        customer = customers[customer_id]
        del customers[customer_id]
        bot.send_message(
            chat_id,
            f"⚠️ Removed inactive customer: {customer.name}\n"
            f"Last visit: {customer.last_visit.strftime('%Y-%m-%d')}"
        )
    
    save_customers(customers) 