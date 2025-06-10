"""
Lead capture module for Forever Siam Fashion Boutique.
Handles collection, validation, and storage of customer information.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, constr

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CustomerLead(BaseModel):
    """Model for customer lead information"""
    name: constr(min_length=2, max_length=100)
    phone: constr(min_length=10, max_length=15)
    email: Optional[EmailStr]
    preferred_contact_time: Optional[str]
    interests: List[str]
    budget_range: Optional[str]
    occasion: Optional[str]
    timeline: Optional[str]
    source: str
    created_at: datetime
    status: str = "new"
    notes: Optional[str]

class LeadCapture:
    def __init__(self, data_file: str = "data/leads.json"):
        """Initialize lead capture system"""
        self.data_file = data_file
        self.leads: Dict[str, CustomerLead] = {}
        self.load_leads()

    def load_leads(self) -> None:
        """Load existing leads from file"""
        try:
            with open(self.data_file, "r") as f:
                data = json.load(f)
                self.leads = {
                    phone: CustomerLead(**lead_data)
                    for phone, lead_data in data.items()
                }
        except FileNotFoundError:
            logger.info("No existing leads file found. Starting fresh.")
            self.leads = {}
        except Exception as e:
            logger.error(f"Error loading leads: {str(e)}")
            self.leads = {}

    def save_leads(self) -> None:
        """Save leads to file"""
        try:
            with open(self.data_file, "w") as f:
                json.dump(
                    {phone: lead.dict() for phone, lead in self.leads.items()},
                    f,
                    indent=2,
                    default=str
                )
        except Exception as e:
            logger.error(f"Error saving leads: {str(e)}")

    def add_lead(self, lead_data: Dict[str, Any]) -> Optional[CustomerLead]:
        """
        Add a new lead to the system
        
        Args:
            lead_data: Dictionary containing lead information
            
        Returns:
            Created CustomerLead object if successful, None otherwise
        """
        try:
            # Add creation timestamp
            lead_data["created_at"] = datetime.now()
            
            # Create lead object
            lead = CustomerLead(**lead_data)
            
            # Store lead
            self.leads[lead.phone] = lead
            
            # Save to file
            self.save_leads()
            
            return lead
        except Exception as e:
            logger.error(f"Error adding lead: {str(e)}")
            return None

    def update_lead(self, phone: str, update_data: Dict[str, Any]) -> Optional[CustomerLead]:
        """
        Update existing lead information
        
        Args:
            phone: Phone number of the lead to update
            update_data: Dictionary containing updated information
            
        Returns:
            Updated CustomerLead object if successful, None otherwise
        """
        try:
            if phone not in self.leads:
                logger.warning(f"Lead not found: {phone}")
                return None
                
            # Get existing lead
            lead = self.leads[phone]
            
            # Update lead data
            updated_data = lead.dict()
            updated_data.update(update_data)
            
            # Create updated lead
            updated_lead = CustomerLead(**updated_data)
            
            # Store updated lead
            self.leads[phone] = updated_lead
            
            # Save to file
            self.save_leads()
            
            return updated_lead
        except Exception as e:
            logger.error(f"Error updating lead: {str(e)}")
            return None

    def get_lead(self, phone: str) -> Optional[CustomerLead]:
        """
        Get lead information by phone number
        
        Args:
            phone: Phone number to look up
            
        Returns:
            CustomerLead object if found, None otherwise
        """
        return self.leads.get(phone)

    def get_leads_by_status(self, status: str) -> List[CustomerLead]:
        """
        Get all leads with a specific status
        
        Args:
            status: Status to filter by
            
        Returns:
            List of CustomerLead objects
        """
        return [
            lead for lead in self.leads.values()
            if lead.status == status
        ]

    def get_leads_by_interest(self, interest: str) -> List[CustomerLead]:
        """
        Get all leads interested in a specific category
        
        Args:
            interest: Interest to filter by
            
        Returns:
            List of CustomerLead objects
        """
        return [
            lead for lead in self.leads.values()
            if interest in lead.interests
        ]

    def qualify_lead(self, phone: str, qualification_data: Dict[str, Any]) -> Optional[CustomerLead]:
        """
        Qualify a lead with additional information
        
        Args:
            phone: Phone number of the lead to qualify
            qualification_data: Dictionary containing qualification information
            
        Returns:
            Updated CustomerLead object if successful, None otherwise
        """
        try:
            if phone not in self.leads:
                logger.warning(f"Lead not found: {phone}")
                return None
                
            # Get existing lead
            lead = self.leads[phone]
            
            # Update qualification data
            update_data = {
                "budget_range": qualification_data.get("budget_range"),
                "occasion": qualification_data.get("occasion"),
                "timeline": qualification_data.get("timeline"),
                "status": "qualified"
            }
            
            return self.update_lead(phone, update_data)
        except Exception as e:
            logger.error(f"Error qualifying lead: {str(e)}")
            return None

    def add_note(self, phone: str, note: str) -> Optional[CustomerLead]:
        """
        Add a note to a lead
        
        Args:
            phone: Phone number of the lead
            note: Note to add
            
        Returns:
            Updated CustomerLead object if successful, None otherwise
        """
        try:
            if phone not in self.leads:
                logger.warning(f"Lead not found: {phone}")
                return None
                
            # Get existing lead
            lead = self.leads[phone]
            
            # Add timestamp to note
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_note = f"[{timestamp}] {note}"
            
            # Update notes
            current_notes = lead.notes or ""
            updated_notes = f"{current_notes}\n{new_note}".strip()
            
            return self.update_lead(phone, {"notes": updated_notes})
        except Exception as e:
            logger.error(f"Error adding note: {str(e)}")
            return None

    def get_lead_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics of leads
        
        Returns:
            Dictionary containing lead statistics
        """
        try:
            total_leads = len(self.leads)
            status_counts = {}
            interest_counts = {}
            
            for lead in self.leads.values():
                # Count by status
                status_counts[lead.status] = status_counts.get(lead.status, 0) + 1
                
                # Count by interest
                for interest in lead.interests:
                    interest_counts[interest] = interest_counts.get(interest, 0) + 1
            
            return {
                "total_leads": total_leads,
                "status_breakdown": status_counts,
                "interest_breakdown": interest_counts,
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error generating lead summary: {str(e)}")
            return {} 