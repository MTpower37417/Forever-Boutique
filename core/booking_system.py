"""
Booking system for Forever Siam Fashion Boutique.
Manages fitting appointments and customer scheduling.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr, constr

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Appointment(BaseModel):
    """Model for fitting appointments"""
    appointment_id: str
    customer_name: constr(min_length=2, max_length=100)
    phone: constr(min_length=10, max_length=15)
    email: Optional[EmailStr]
    date: datetime
    duration: int = 45  # minutes
    party_size: int = 1
    purpose: str
    notes: Optional[str]
    status: str = "scheduled"
    created_at: datetime
    updated_at: datetime

class BookingSystem:
    def __init__(
        self,
        appointments_file: str = "data/appointments.json",
        store_info_file: str = "data/store_info.json"
    ):
        """Initialize booking system"""
        self.appointments_file = appointments_file
        self.store_info_file = store_info_file
        self.appointments: Dict[str, Appointment] = {}
        self.store_info = self.load_store_info()
        self.load_appointments()

    def load_store_info(self) -> Dict[str, Any]:
        """Load store information"""
        try:
            with open(self.store_info_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading store info: {str(e)}")
            return {}

    def load_appointments(self) -> None:
        """Load existing appointments"""
        try:
            with open(self.appointments_file, "r") as f:
                data = json.load(f)
                self.appointments = {
                    appt_id: Appointment(**appt_data)
                    for appt_id, appt_data in data.items()
                }
        except FileNotFoundError:
            logger.info("No existing appointments file found. Starting fresh.")
            self.appointments = {}
        except Exception as e:
            logger.error(f"Error loading appointments: {str(e)}")
            self.appointments = {}

    def save_appointments(self) -> None:
        """Save appointments to file"""
        try:
            with open(self.appointments_file, "w") as f:
                json.dump(
                    {appt_id: appt.dict() for appt_id, appt in self.appointments.items()},
                    f,
                    indent=2,
                    default=str
                )
        except Exception as e:
            logger.error(f"Error saving appointments: {str(e)}")

    def get_available_slots(
        self,
        date: datetime,
        duration: int = 45
    ) -> List[Dict[str, Any]]:
        """
        Get available appointment slots for a date
        
        Args:
            date: Date to check availability
            duration: Appointment duration in minutes
            
        Returns:
            List of available time slots
        """
        try:
            # Get store hours for the date
            weekday = date.strftime("%A").lower()
            hours = self.store_info["hours"]["weekday"][weekday]
            open_time, close_time = self._parse_store_hours(hours)
            
            # Generate all possible slots
            slots = []
            current_time = open_time
            while current_time + timedelta(minutes=duration) <= close_time:
                # Check if slot is available
                if self._is_slot_available(current_time, duration):
                    slots.append({
                        "start_time": current_time.strftime("%I:%M %p"),
                        "end_time": (current_time + timedelta(minutes=duration)).strftime("%I:%M %p")
                    })
                current_time += timedelta(minutes=30)  # 30-minute intervals
            
            return slots
        except Exception as e:
            logger.error(f"Error getting available slots: {str(e)}")
            return []

    def _parse_store_hours(self, hours_str: str) -> tuple:
        """Parse store hours string to datetime objects"""
        try:
            open_time, close_time = hours_str.split(" - ")
            today = datetime.now().date()
            
            # Parse times
            open_dt = datetime.strptime(open_time, "%I:%M %p").time()
            close_dt = datetime.strptime(close_time, "%I:%M %p").time()
            
            return (
                datetime.combine(today, open_dt),
                datetime.combine(today, close_dt)
            )
        except Exception as e:
            logger.error(f"Error parsing store hours: {str(e)}")
            return (datetime.now(), datetime.now())

    def _is_slot_available(self, start_time: datetime, duration: int) -> bool:
        """Check if a time slot is available"""
        try:
            end_time = start_time + timedelta(minutes=duration)
            
            # Check for overlapping appointments
            for appointment in self.appointments.values():
                if appointment.status != "cancelled":
                    appt_start = appointment.date
                    appt_end = appt_start + timedelta(minutes=appointment.duration)
                    
                    if (start_time < appt_end and end_time > appt_start):
                        return False
            
            return True
        except Exception as e:
            logger.error(f"Error checking slot availability: {str(e)}")
            return False

    def book_appointment(
        self,
        customer_name: str,
        phone: str,
        date: datetime,
        email: Optional[str] = None,
        party_size: int = 1,
        purpose: str = "fitting",
        notes: Optional[str] = None
    ) -> Optional[Appointment]:
        """
        Book a new appointment
        
        Args:
            customer_name: Customer's name
            phone: Customer's phone number
            date: Appointment date and time
            email: Optional customer email
            party_size: Number of people in the party
            purpose: Purpose of the appointment
            notes: Optional appointment notes
            
        Returns:
            Created Appointment object if successful, None otherwise
        """
        try:
            # Validate party size
            max_party_size = self.store_info["services"]["fitting"]["max_party_size"]
            if party_size > max_party_size:
                raise ValueError(f"Party size cannot exceed {max_party_size}")
            
            # Check if slot is available
            if not self._is_slot_available(date, 45):  # Default 45-minute duration
                raise ValueError("Selected time slot is not available")
            
            # Create appointment
            appointment = Appointment(
                appointment_id=f"APT{datetime.now().strftime('%Y%m%d%H%M%S')}",
                customer_name=customer_name,
                phone=phone,
                email=email,
                date=date,
                party_size=party_size,
                purpose=purpose,
                notes=notes,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Save appointment
            self.appointments[appointment.appointment_id] = appointment
            self.save_appointments()
            
            return appointment
        except Exception as e:
            logger.error(f"Error booking appointment: {str(e)}")
            return None

    def cancel_appointment(self, appointment_id: str) -> bool:
        """
        Cancel an existing appointment
        
        Args:
            appointment_id: ID of the appointment to cancel
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if appointment_id not in self.appointments:
                raise ValueError("Appointment not found")
            
            appointment = self.appointments[appointment_id]
            appointment.status = "cancelled"
            appointment.updated_at = datetime.now()
            
            self.save_appointments()
            return True
        except Exception as e:
            logger.error(f"Error cancelling appointment: {str(e)}")
            return False

    def reschedule_appointment(
        self,
        appointment_id: str,
        new_date: datetime
    ) -> Optional[Appointment]:
        """
        Reschedule an existing appointment
        
        Args:
            appointment_id: ID of the appointment to reschedule
            new_date: New appointment date and time
            
        Returns:
            Updated Appointment object if successful, None otherwise
        """
        try:
            if appointment_id not in self.appointments:
                raise ValueError("Appointment not found")
            
            # Check if new slot is available
            if not self._is_slot_available(new_date, 45):  # Default 45-minute duration
                raise ValueError("Selected time slot is not available")
            
            appointment = self.appointments[appointment_id]
            appointment.date = new_date
            appointment.updated_at = datetime.now()
            
            self.save_appointments()
            return appointment
        except Exception as e:
            logger.error(f"Error rescheduling appointment: {str(e)}")
            return None

    def get_appointment(self, appointment_id: str) -> Optional[Appointment]:
        """
        Get appointment details
        
        Args:
            appointment_id: ID of the appointment to retrieve
            
        Returns:
            Appointment object if found, None otherwise
        """
        return self.appointments.get(appointment_id)

    def get_customer_appointments(
        self,
        phone: str,
        include_cancelled: bool = False
    ) -> List[Appointment]:
        """
        Get all appointments for a customer
        
        Args:
            phone: Customer's phone number
            include_cancelled: Whether to include cancelled appointments
            
        Returns:
            List of Appointment objects
        """
        try:
            appointments = [
                appt for appt in self.appointments.values()
                if appt.phone == phone and (include_cancelled or appt.status != "cancelled")
            ]
            return sorted(appointments, key=lambda x: x.date)
        except Exception as e:
            logger.error(f"Error getting customer appointments: {str(e)}")
            return []

    def get_appointments_by_date(
        self,
        date: datetime,
        include_cancelled: bool = False
    ) -> List[Appointment]:
        """
        Get all appointments for a specific date
        
        Args:
            date: Date to get appointments for
            include_cancelled: Whether to include cancelled appointments
            
        Returns:
            List of Appointment objects
        """
        try:
            appointments = [
                appt for appt in self.appointments.values()
                if appt.date.date() == date.date() and
                (include_cancelled or appt.status != "cancelled")
            ]
            return sorted(appointments, key=lambda x: x.date)
        except Exception as e:
            logger.error(f"Error getting appointments by date: {str(e)}")
 