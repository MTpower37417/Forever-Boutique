"""
Product recommendation system for Forever Siam Fashion Boutique.
Provides intelligent dress recommendations based on occasions, preferences, and customer data.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductRecommendation(BaseModel):
    """Model for product recommendations"""
    product_id: str
    name: str
    description: str
    price_range: Dict[str, float]
    match_score: float
    match_reasons: List[str]
    image_url: str

class ProductRecommender:
    def __init__(self, products_file: str = "data/products.json"):
        """Initialize product recommender"""
        self.products_file = products_file
        self.products = self.load_products()
        self.occasion_keywords = self.load_occasion_keywords()

    def load_products(self) -> Dict[str, Any]:
        """Load product catalog from file"""
        try:
            with open(self.products_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading products: {str(e)}")
            return {}

    def load_occasion_keywords(self) -> Dict[str, List[str]]:
        """Load occasion keywords for matching"""
        return {
            "wedding": [
                "wedding", "ceremony", "formal", "bride", "bridesmaid",
                "reception", "white tie", "black tie"
            ],
            "cocktail": [
                "cocktail", "semi-formal", "party", "evening", "dinner",
                "gala", "celebration"
            ],
            "business": [
                "business", "professional", "office", "meeting", "conference",
                "presentation", "formal"
            ],
            "casual": [
                "casual", "day", "lunch", "brunch", "shopping", "outdoor",
                "relaxed"
            ]
        }

    def get_recommendations(
        self,
        occasion: str,
        budget_range: Optional[Dict[str, float]] = None,
        preferred_colors: Optional[List[str]] = None,
        preferred_styles: Optional[List[str]] = None,
        size: Optional[str] = None,
        limit: int = 5
    ) -> List[ProductRecommendation]:
        """
        Get product recommendations based on criteria
        
        Args:
            occasion: The occasion for the dress
            budget_range: Optional budget range (min, max)
            preferred_colors: Optional list of preferred colors
            preferred_styles: Optional list of preferred styles
            size: Optional preferred size
            limit: Maximum number of recommendations to return
            
        Returns:
            List of ProductRecommendation objects
        """
        try:
            recommendations = []
            
            # Normalize occasion
            occasion = occasion.lower()
            
            # Determine occasion category
            occasion_category = self._categorize_occasion(occasion)
            
            # Get relevant products
            category_products = self.products["categories"].get(occasion_category, {}).get("products", [])
            
            for product in category_products:
                # Calculate match score
                match_score = 0.0
                match_reasons = []
                
                # Check budget
                if budget_range:
                    product_min = product["price_range"]["min"]
                    product_max = product["price_range"]["max"]
                    if (product_min >= budget_range["min"] and 
                        product_max <= budget_range["max"]):
                        match_score += 0.3
                        match_reasons.append("Within budget")
                
                # Check colors
                if preferred_colors:
                    matching_colors = [
                        color for color in preferred_colors
                        if color.lower() in [c.lower() for c in product["colors"]]
                    ]
                    if matching_colors:
                        match_score += 0.2
                        match_reasons.append(f"Available in {', '.join(matching_colors)}")
                
                # Check size availability
                if size and size in product["sizes"]:
                    match_score += 0.2
                    match_reasons.append(f"Available in size {size}")
                
                # Check occasion match
                if occasion in [o.lower() for o in product["occasions"]]:
                    match_score += 0.3
                    match_reasons.append("Perfect for the occasion")
                
                # Create recommendation if score > 0
                if match_score > 0:
                    recommendation = ProductRecommendation(
                        product_id=product["id"],
                        name=product["name"],
                        description=product["description"],
                        price_range=product["price_range"],
                        match_score=match_score,
                        match_reasons=match_reasons,
                        image_url=product["image_url"]
                    )
                    recommendations.append(recommendation)
            
            # Sort by match score and limit results
            recommendations.sort(key=lambda x: x.match_score, reverse=True)
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            return []

    def _categorize_occasion(self, occasion: str) -> str:
        """
        Categorize occasion into product category
        
        Args:
            occasion: The occasion to categorize
            
        Returns:
            Product category name
        """
        occasion = occasion.lower()
        
        # Check each category's keywords
        for category, keywords in self.occasion_keywords.items():
            if any(keyword in occasion for keyword in keywords):
                if category == "wedding":
                    return "bridesmaid_dresses"
                elif category == "cocktail":
                    return "cocktail_dresses"
                elif category == "business":
                    return "cocktail_dresses"  # Business-appropriate cocktail dresses
                elif category == "casual":
                    return "cocktail_dresses"  # Casual cocktail dresses
        
        # Default to cocktail dresses if no specific match
        return "cocktail_dresses"

    def get_complementary_items(
        self,
        product_id: str,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Get complementary items for a product
        
        Args:
            product_id: ID of the main product
            limit: Maximum number of complementary items to return
            
        Returns:
            List of complementary product dictionaries
        """
        try:
            # Find main product
            main_product = None
            for category in self.products["categories"].values():
                for product in category["products"]:
                    if product["id"] == product_id:
                        main_product = product
                        break
                if main_product:
                    break
            
            if not main_product:
                return []
            
            # Get complementary accessories
            complementary_items = []
            for accessory in self.products["accessories"]["products"]:
                # Check color compatibility
                if any(color in main_product["colors"] for color in accessory["colors"]):
                    complementary_items.append(accessory)
            
            return complementary_items[:limit]
            
        except Exception as e:
            logger.error(f"Error getting complementary items: {str(e)}")
            return []

    def get_occasion_guide(self, occasion: str) -> Dict[str, Any]:
        """
        Get style guide for an occasion
        
        Args:
            occasion: The occasion to get style guide for
            
        Returns:
            Dictionary containing style guide information
        """
        try:
            occasion = occasion.lower()
            category = self._categorize_occasion(occasion)
            
            # Get relevant products
            products = self.products["categories"].get(category, {}).get("products", [])
            
            # Extract style information
            styles = set()
            colors = set()
            price_ranges = []
            
            for product in products:
                styles.update(product.get("occasions", []))
                colors.update(product.get("colors", []))
                price_ranges.append(product["price_range"])
            
            # Calculate average price range
            avg_min = sum(p["min"] for p in price_ranges) / len(price_ranges) if price_ranges else 0
            avg_max = sum(p["max"] for p in price_ranges) / len(price_ranges) if price_ranges else 0
            
            return {
                "occasion": occasion,
                "category": category,
                "recommended_styles": list(styles),
                "popular_colors": list(colors),
                "average_price_range": {
                    "min": avg_min,
                    "max": avg_max
                },
                "tips": self._get_occasion_tips(occasion)
            }
            
        except Exception as e:
            logger.error(f"Error getting occasion guide: {str(e)}")
            return {}

    def _get_occasion_tips(self, occasion: str) -> List[str]:
        """
        Get style tips for an occasion
        
        Args:
            occasion: The occasion to get tips for
            
        Returns:
            List of style tips
        """
        occasion = occasion.lower()
        
        if "wedding" in occasion:
            return [
                "Choose a dress that complements the wedding's formality level",
                "Consider the venue and time of day",
                "Avoid white or ivory unless you're the bride",
                "Accessorize with elegant jewelry and a clutch"
            ]
        elif "cocktail" in occasion:
            return [
                "Knee-length or midi dresses are perfect for cocktail events",
                "Choose sophisticated fabrics like silk or lace",
                "Add statement jewelry for elegance",
                "Consider the event's dress code"
            ]
        elif "business" in occasion:
            return [
                "Opt for conservative cuts and lengths",
                "Choose professional colors like navy, black, or gray",
                "Keep accessories minimal and elegant",
                "Ensure the dress is appropriate for your workplace"
            ]
        else:
            return [
                "Consider the event's formality level",
                "Choose colors that complement your skin tone",
                "Select a style that flatters your body type",
                "Accessorize appropriately for the occasion"
            ] 