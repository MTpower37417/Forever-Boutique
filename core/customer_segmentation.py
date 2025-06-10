"""
Customer segmentation system for Forever Siam Fashion Boutique.
Analyzes customer behavior and categorizes customers for targeted marketing.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CustomerProfile(BaseModel):
    """Model for customer profile"""
    customer_id: str
    name: str
    phone: str
    email: Optional[str]
    first_purchase_date: Optional[datetime]
    last_purchase_date: Optional[datetime]
    total_purchases: int = 0
    total_spent: float = 0.0
    preferred_categories: List[str] = []
    preferred_price_range: Dict[str, float] = {}
    visit_frequency: float = 0.0
    segment: str = "new"
    lifetime_value: float = 0.0
    created_at: datetime
    updated_at: datetime

class CustomerSegmentation:
    def __init__(
        self,
        customers_file: str = "data/customers.json",
        transactions_file: str = "data/transactions.json"
    ):
        """Initialize customer segmentation system"""
        self.customers_file = customers_file
        self.transactions_file = transactions_file
        self.customers: Dict[str, CustomerProfile] = {}
        self.transactions: List[Dict[str, Any]] = []
        self.load_data()

    def load_data(self) -> None:
        """Load customer and transaction data"""
        try:
            # Load customers
            with open(self.customers_file, "r") as f:
                data = json.load(f)
                self.customers = {
                    cust_id: CustomerProfile(**cust_data)
                    for cust_id, cust_data in data.items()
                }
        except FileNotFoundError:
            logger.info("No existing customers file found. Starting fresh.")
            self.customers = {}
        except Exception as e:
            logger.error(f"Error loading customers: {str(e)}")
            self.customers = {}

        try:
            # Load transactions
            with open(self.transactions_file, "r") as f:
                self.transactions = json.load(f)
        except FileNotFoundError:
            logger.info("No existing transactions file found. Starting fresh.")
            self.transactions = []
        except Exception as e:
            logger.error(f"Error loading transactions: {str(e)}")
            self.transactions = []

    def save_data(self) -> None:
        """Save customer and transaction data"""
        try:
            # Save customers
            with open(self.customers_file, "w") as f:
                json.dump(
                    {cust_id: cust.dict() for cust_id, cust in self.customers.items()},
                    f,
                    indent=2,
                    default=str
                )
        except Exception as e:
            logger.error(f"Error saving customers: {str(e)}")

    def add_customer(
        self,
        name: str,
        phone: str,
        email: Optional[str] = None
    ) -> Optional[CustomerProfile]:
        """
        Add a new customer
        
        Args:
            name: Customer's name
            phone: Customer's phone number
            email: Optional customer email
            
        Returns:
            Created CustomerProfile object if successful, None otherwise
        """
        try:
            # Create customer profile
            customer = CustomerProfile(
                customer_id=f"CUST{datetime.now().strftime('%Y%m%d%H%M%S')}",
                name=name,
                phone=phone,
                email=email,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Save customer
            self.customers[customer.customer_id] = customer
            self.save_data()
            
            return customer
        except Exception as e:
            logger.error(f"Error adding customer: {str(e)}")
            return None

    def update_customer_profile(
        self,
        customer_id: str,
        transaction: Dict[str, Any]
    ) -> Optional[CustomerProfile]:
        """
        Update customer profile with new transaction
        
        Args:
            customer_id: ID of the customer
            transaction: Transaction data
            
        Returns:
            Updated CustomerProfile object if successful, None otherwise
        """
        try:
            if customer_id not in self.customers:
                raise ValueError("Customer not found")
            
            customer = self.customers[customer_id]
            
            # Update purchase history
            customer.total_purchases += 1
            customer.total_spent += transaction["amount"]
            
            # Update dates
            purchase_date = datetime.fromisoformat(transaction["date"])
            if not customer.first_purchase_date:
                customer.first_purchase_date = purchase_date
            customer.last_purchase_date = purchase_date
            
            # Update preferred categories
            category = transaction["category"]
            if category not in customer.preferred_categories:
                customer.preferred_categories.append(category)
            
            # Update preferred price range
            if not customer.preferred_price_range:
                customer.preferred_price_range = {
                    "min": transaction["amount"],
                    "max": transaction["amount"]
                }
            else:
                customer.preferred_price_range["min"] = min(
                    customer.preferred_price_range["min"],
                    transaction["amount"]
                )
                customer.preferred_price_range["max"] = max(
                    customer.preferred_price_range["max"],
                    transaction["amount"]
                )
            
            # Update visit frequency
            if customer.first_purchase_date:
                days_since_first = (purchase_date - customer.first_purchase_date).days
                if days_since_first > 0:
                    customer.visit_frequency = customer.total_purchases / days_since_first
            
            # Update lifetime value
            customer.lifetime_value = customer.total_spent
            
            # Update segment
            customer.segment = self._determine_segment(customer)
            
            # Update timestamp
            customer.updated_at = datetime.now()
            
            # Save changes
            self.save_data()
            
            return customer
        except Exception as e:
            logger.error(f"Error updating customer profile: {str(e)}")
            return None

    def _determine_segment(self, customer: CustomerProfile) -> str:
        """
        Determine customer segment based on behavior
        
        Args:
            customer: Customer profile to analyze
            
        Returns:
            Customer segment name
        """
        try:
            if not customer.first_purchase_date:
                return "new"
            
            # Calculate metrics
            days_since_first = (datetime.now() - customer.first_purchase_date).days
            if days_since_first == 0:
                return "new"
            
            purchase_frequency = customer.total_purchases / days_since_first
            avg_purchase_value = customer.total_spent / customer.total_purchases
            
            # Determine segment
            if purchase_frequency >= 0.1 and avg_purchase_value >= 20000:
                return "vip"
            elif purchase_frequency >= 0.05 and avg_purchase_value >= 10000:
                return "loyal"
            elif purchase_frequency >= 0.02:
                return "regular"
            elif days_since_first <= 30:
                return "new"
            else:
                return "inactive"
        except Exception as e:
            logger.error(f"Error determining segment: {str(e)}")
            return "new"

    def get_customer_segments(self) -> Dict[str, List[CustomerProfile]]:
        """
        Get all customers grouped by segment
        
        Returns:
            Dictionary mapping segments to lists of CustomerProfile objects
        """
        try:
            segments: Dict[str, List[CustomerProfile]] = {
                "vip": [],
                "loyal": [],
                "regular": [],
                "new": [],
                "inactive": []
            }
            
            for customer in self.customers.values():
                segments[customer.segment].append(customer)
            
            return segments
        except Exception as e:
            logger.error(f"Error getting customer segments: {str(e)}")
            return {}

    def get_segment_metrics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get metrics for each customer segment
        
        Returns:
            Dictionary containing segment metrics
        """
        try:
            segments = self.get_customer_segments()
            metrics = {}
            
            for segment, customers in segments.items():
                if not customers:
                    continue
                
                total_customers = len(customers)
                total_spent = sum(c.total_spent for c in customers)
                avg_purchase_value = total_spent / sum(c.total_purchases for c in customers)
                avg_lifetime_value = total_spent / total_customers
                
                metrics[segment] = {
                    "total_customers": total_customers,
                    "total_spent": total_spent,
                    "avg_purchase_value": avg_purchase_value,
                    "avg_lifetime_value": avg_lifetime_value,
                    "preferred_categories": self._get_segment_preferences(customers)
                }
            
            return metrics
        except Exception as e:
            logger.error(f"Error getting segment metrics: {str(e)}")
            return {}

    def _get_segment_preferences(
        self,
        customers: List[CustomerProfile]
    ) -> Dict[str, int]:
        """
        Get category preferences for a segment
        
        Args:
            customers: List of customers in the segment
            
        Returns:
            Dictionary mapping categories to preference counts
        """
        try:
            preferences = {}
            for customer in customers:
                for category in customer.preferred_categories:
                    preferences[category] = preferences.get(category, 0) + 1
            
            return dict(sorted(
                preferences.items(),
                key=lambda x: x[1],
                reverse=True
            ))
        except Exception as e:
            logger.error(f"Error getting segment preferences: {str(e)}")
            return {}

    def get_customer_recommendations(
        self,
        customer_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get product recommendations for a customer
        
        Args:
            customer_id: ID of the customer
            limit: Maximum number of recommendations
            
        Returns:
            List of recommended products
        """
        try:
            if customer_id not in self.customers:
                raise ValueError("Customer not found")
            
            customer = self.customers[customer_id]
            
            # Get similar customers
            similar_customers = self._find_similar_customers(customer)
            
            # Get products purchased by similar customers
            recommendations = []
            for similar_customer in similar_customers:
                for transaction in self.transactions:
                    if (transaction["customer_id"] == similar_customer.customer_id and
                        transaction["category"] in customer.preferred_categories):
                        recommendations.append(transaction["product"])
            
            # Remove duplicates and limit results
            unique_recommendations = []
            seen_products = set()
            
            for rec in recommendations:
                if rec["id"] not in seen_products:
                    seen_products.add(rec["id"])
                    unique_recommendations.append(rec)
            
            return unique_recommendations[:limit]
        except Exception as e:
            logger.error(f"Error getting customer recommendations: {str(e)}")
            return []

    def _find_similar_customers(
        self,
        customer: CustomerProfile,
        limit: int = 5
    ) -> List[CustomerProfile]:
        """
        Find customers with similar preferences
        
        Args:
            customer: Customer to find similar customers for
            limit: Maximum number of similar customers
            
        Returns:
            List of similar CustomerProfile objects
        """
        try:
            # Calculate similarity scores
            similarities = []
            for other_customer in self.customers.values():
                if other_customer.customer_id == customer.customer_id:
                    continue
                
                # Calculate category similarity
                category_similarity = len(
                    set(customer.preferred_categories) &
                    set(other_customer.preferred_categories)
                ) / len(set(customer.preferred_categories) | set(other_customer.preferred_categories))
                
                # Calculate price range similarity
                price_similarity = 1.0
                if customer.preferred_price_range and other_customer.preferred_price_range:
                    customer_range = (
                        customer.preferred_price_range["max"] -
                        customer.preferred_price_range["min"]
                    )
                    other_range = (
                        other_customer.preferred_price_range["max"] -
                        other_customer.preferred_price_range["min"]
                    )
                    if customer_range > 0 and other_range > 0:
                        price_similarity = 1 - abs(
                            (customer_range - other_range) /
                            max(customer_range, other_range)
                        )
                
                # Calculate overall similarity
                similarity = (category_similarity + price_similarity) / 2
                similarities.append((other_customer, similarity))
            
            # Sort by similarity and return top matches
            similarities.sort(key=lambda x: x[1], reverse=True)
            return [customer for customer, _ in similarities[:limit]]
        except Exception as e:
            logger.error(f"Error finding similar customers: {str(e)}")
            return [] 