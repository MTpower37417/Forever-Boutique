"""
Size advisor system for Forever Siam Fashion Boutique.
Helps customers find their perfect fit and provides size recommendations.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel, confloat

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Measurements(BaseModel):
    """Model for customer measurements"""
    bust: confloat(gt=0)
    waist: confloat(gt=0)
    hips: confloat(gt=0)
    height: confloat(gt=0)
    unit: str = "cm"  # or "inches"

class SizeRecommendation(BaseModel):
    """Model for size recommendations"""
    recommended_size: str
    confidence_score: float
    fit_notes: List[str]
    alteration_needed: bool
    alteration_notes: Optional[List[str]]
    body_type: str
    style_recommendations: List[str]

class SizeAdvisor:
    def __init__(
        self,
        size_guide_file: str = "data/size_guide.json",
        products_file: str = "data/products.json"
    ):
        """Initialize size advisor"""
        self.size_guide_file = size_guide_file
        self.products_file = products_file
        self.size_guide = self.load_size_guide()
        self.products = self.load_products()

    def load_size_guide(self) -> Dict[str, Any]:
        """Load size guide from file"""
        try:
            with open(self.size_guide_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading size guide: {str(e)}")
            return {}

    def load_products(self) -> Dict[str, Any]:
        """Load product catalog from file"""
        try:
            with open(self.products_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading products: {str(e)}")
            return {}

    def get_size_recommendation(
        self,
        measurements: Measurements,
        product_id: Optional[str] = None
    ) -> SizeRecommendation:
        """
        Get size recommendation based on measurements
        
        Args:
            measurements: Customer measurements
            product_id: Optional product ID for specific product recommendations
            
        Returns:
            SizeRecommendation object
        """
        try:
            # Convert measurements to cm if needed
            if measurements.unit == "inches":
                measurements = self._convert_to_cm(measurements)
            
            # Determine body type
            body_type = self._determine_body_type(measurements)
            
            # Get size chart
            size_chart = self.size_guide["size_chart"]["sizes"]
            
            # Find best matching size
            best_size = None
            best_score = 0.0
            fit_notes = []
            
            for size, ranges in size_chart.items():
                score = 0.0
                size_notes = []
                
                # Check bust
                bust_range = self._parse_measurement_range(ranges["bust"])
                if bust_range[0] <= measurements.bust <= bust_range[1]:
                    score += 0.4
                    size_notes.append("Bust fits well")
                elif measurements.bust < bust_range[0]:
                    score += 0.2
                    size_notes.append("Bust slightly small")
                else:
                    score += 0.2
                    size_notes.append("Bust slightly large")
                
                # Check waist
                waist_range = self._parse_measurement_range(ranges["waist"])
                if waist_range[0] <= measurements.waist <= waist_range[1]:
                    score += 0.4
                    size_notes.append("Waist fits well")
                elif measurements.waist < waist_range[0]:
                    score += 0.2
                    size_notes.append("Waist slightly small")
                else:
                    score += 0.2
                    size_notes.append("Waist slightly large")
                
                # Check hips
                hips_range = self._parse_measurement_range(ranges["hips"])
                if hips_range[0] <= measurements.hips <= hips_range[1]:
                    score += 0.2
                    size_notes.append("Hips fit well")
                elif measurements.hips < hips_range[0]:
                    score += 0.1
                    size_notes.append("Hips slightly small")
                else:
                    score += 0.1
                    size_notes.append("Hips slightly large")
                
                if score > best_score:
                    best_score = score
                    best_size = size
                    fit_notes = size_notes
            
            # Check if alterations are needed
            alteration_needed = best_score < 0.8
            alteration_notes = []
            
            if alteration_needed:
                alteration_notes = self._get_alteration_notes(measurements, best_size)
            
            # Get style recommendations based on body type
            style_recommendations = self._get_style_recommendations(body_type)
            
            # Create recommendation
            recommendation = SizeRecommendation(
                recommended_size=best_size,
                confidence_score=best_score,
                fit_notes=fit_notes,
                alteration_needed=alteration_needed,
                alteration_notes=alteration_notes,
                body_type=body_type,
                style_recommendations=style_recommendations
            )
            
            # Add product-specific notes if product_id provided
            if product_id:
                product_notes = self._get_product_specific_notes(product_id, best_size)
                recommendation.fit_notes.extend(product_notes)
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Error getting size recommendation: {str(e)}")
            raise

    def _convert_to_cm(self, measurements: Measurements) -> Measurements:
        """Convert measurements from inches to centimeters"""
        return Measurements(
            bust=measurements.bust * 2.54,
            waist=measurements.waist * 2.54,
            hips=measurements.hips * 2.54,
            height=measurements.height * 2.54,
            unit="cm"
        )

    def _parse_measurement_range(self, range_str: str) -> Tuple[float, float]:
        """Parse measurement range string to tuple of floats"""
        try:
            # Remove units and split
            range_str = range_str.split("(")[0].strip()
            min_str, max_str = range_str.split("-")
            return float(min_str.strip()), float(max_str.strip())
        except Exception as e:
            logger.error(f"Error parsing measurement range: {str(e)}")
            return (0.0, 0.0)

    def _determine_body_type(self, measurements: Measurements) -> str:
        """Determine body type based on measurements"""
        try:
            # Calculate ratios
            bust_waist_ratio = measurements.bust / measurements.waist
            hip_waist_ratio = measurements.hips / measurements.waist
            
            # Determine body type
            if 0.9 <= bust_waist_ratio <= 1.1 and 0.9 <= hip_waist_ratio <= 1.1:
                return "hourglass"
            elif hip_waist_ratio > 1.1:
                return "pear"
            elif bust_waist_ratio > 1.1:
                return "apple"
            else:
                return "rectangle"
        except Exception as e:
            logger.error(f"Error determining body type: {str(e)}")
            return "rectangle"

    def _get_alteration_notes(
        self,
        measurements: Measurements,
        size: str
    ) -> List[str]:
        """Get notes about needed alterations"""
        try:
            notes = []
            size_ranges = self.size_guide["size_chart"]["sizes"][size]
            
            # Check bust alterations
            bust_range = self._parse_measurement_range(size_ranges["bust"])
            if measurements.bust < bust_range[0]:
                notes.append(f"Bust may need to be taken in by {bust_range[0] - measurements.bust:.1f} cm")
            elif measurements.bust > bust_range[1]:
                notes.append(f"Bust may need to be let out by {measurements.bust - bust_range[1]:.1f} cm")
            
            # Check waist alterations
            waist_range = self._parse_measurement_range(size_ranges["waist"])
            if measurements.waist < waist_range[0]:
                notes.append(f"Waist may need to be taken in by {waist_range[0] - measurements.waist:.1f} cm")
            elif measurements.waist > waist_range[1]:
                notes.append(f"Waist may need to be let out by {measurements.waist - waist_range[1]:.1f} cm")
            
            # Check hip alterations
            hip_range = self._parse_measurement_range(size_ranges["hips"])
            if measurements.hips < hip_range[0]:
                notes.append(f"Hips may need to be taken in by {hip_range[0] - measurements.hips:.1f} cm")
            elif measurements.hips > hip_range[1]:
                notes.append(f"Hips may need to be let out by {measurements.hips - hip_range[1]:.1f} cm")
            
            return notes
        except Exception as e:
            logger.error(f"Error getting alteration notes: {str(e)}")
            return []

    def _get_style_recommendations(self, body_type: str) -> List[str]:
        """Get style recommendations based on body type"""
        try:
            return self.size_guide["style_guidance"]["body_types"][body_type]["recommended_styles"]
        except Exception as e:
            logger.error(f"Error getting style recommendations: {str(e)}")
            return []

    def _get_product_specific_notes(self, product_id: str, size: str) -> List[str]:
        """Get product-specific fitting notes"""
        try:
            notes = []
            
            # Find product
            product = None
            for category in self.products["categories"].values():
                for p in category["products"]:
                    if p["id"] == product_id:
                        product = p
                        break
                if product:
                    break
            
            if not product:
                return notes
            
            # Check size availability
            if size not in product["sizes"]:
                notes.append(f"Size {size} is not available in this style")
            
            # Add style-specific notes
            if "fitted" in product["description"].lower():
                notes.append("This is a fitted style - consider sizing up if you prefer a looser fit")
            elif "flowing" in product["description"].lower():
                notes.append("This is a flowing style - consider sizing down if you prefer a more fitted look")
            
            return notes
        except Exception as e:
            logger.error(f"Error getting product-specific notes: {str(e)}")
            return []

    def get_measurement_guide(self) -> Dict[str, Any]:
        """Get measurement guide for customers"""
        try:
            return {
                "instructions": self.size_guide["fitting_tips"]["general"],
                "specific_instructions": {
                    "bust": self.size_guide["fitting_tips"]["bust"],
                    "waist": self.size_guide["fitting_tips"]["waist"],
                    "hips": self.size_guide["fitting_tips"]["hips"]
                }
            }
        except Exception as e:
            logger.error(f"Error getting measurement guide: {str(e)}")
            return {} 