"""
Response templates for Forever Siam Fashion Boutique chatbot.
These templates are used to generate consistent, professional responses
for various customer interactions.
"""

class ResponseTemplates:
    # Greeting templates
    GREETINGS = {
        "welcome": (
            "Welcome to Forever Siam Fashion Boutique! 👗✨\n\n"
            "I'm your personal fashion assistant. How can I help you today?\n\n"
            "• Browse our collections\n"
            "• Book a fitting appointment\n"
            "• Get size recommendations\n"
            "• Learn about our services"
        ),
        "returning": (
            "Welcome back to Forever Siam! 👋\n\n"
            "It's great to see you again. How can I assist you today?"
        ),
        "goodbye": (
            "Thank you for chatting with Forever Siam! 👋\n\n"
            "We hope to see you soon. Remember, you can always message us for assistance."
        )
    }

    # Product-related templates
    PRODUCTS = {
        "collection_intro": (
            "Here are our {category} collections:\n\n"
            "{products}\n\n"
            "Would you like to know more about any specific piece?"
        ),
        "product_details": (
            "✨ {name} ✨\n\n"
            "Description: {description}\n"
            "Price: ฿{price:,.2f}\n"
            "Available sizes: {sizes}\n"
            "Colors: {colors}\n\n"
            "Would you like to:\n"
            "• Book a fitting appointment\n"
            "• Check availability\n"
            "• See similar styles"
        ),
        "out_of_stock": (
            "I apologize, but {product_name} is currently out of stock in size {size}.\n\n"
            "Would you like to:\n"
            "• Be notified when it's back in stock\n"
            "• See similar styles\n"
            "• Check other sizes"
        )
    }

    # Size and fitting templates
    SIZING = {
        "size_guide": (
            "Here's our size guide for {category}:\n\n"
            "{size_chart}\n\n"
            "Would you like to:\n"
            "• Book a fitting appointment\n"
            "• Get personalized recommendations\n"
            "• Learn about our alteration services"
        ),
        "fitting_appointment": (
            "Great choice! Let's book your fitting appointment.\n\n"
            "Available dates:\n{available_dates}\n\n"
            "Please select your preferred date and time."
        ),
        "alteration_info": (
            "Our alteration services include:\n\n"
            "• Hem adjustments (up to 4 inches)\n"
            "• Waist adjustments (up to 2 inches)\n"
            "• Strap adjustments (up to 2 inches)\n\n"
            "Basic alterations are complimentary with purchase.\n"
            "Complex alterations may incur additional charges."
        )
    }

    # Appointment templates
    APPOINTMENTS = {
        "booking_confirmation": (
            "✅ Your fitting appointment is confirmed!\n\n"
            "Date: {date}\n"
            "Time: {time}\n"
            "Duration: 45 minutes\n\n"
            "Please arrive 5 minutes early. We look forward to seeing you!"
        ),
        "booking_reminder": (
            "Reminder: Your fitting appointment is tomorrow!\n\n"
            "Date: {date}\n"
            "Time: {time}\n\n"
            "Please bring your ID and any specific items you'd like to try."
        ),
        "reschedule": (
            "I understand you need to reschedule your appointment.\n\n"
            "Here are our available slots:\n{available_slots}\n\n"
            "Please select your preferred time."
        )
    }

    # Lead capture templates
    LEADS = {
        "contact_request": (
            "I'd be happy to help you further! Please provide:\n\n"
            "• Your name\n"
            "• Phone number\n"
            "• Preferred contact time\n\n"
            "Our team will get back to you within 24 hours."
        ),
        "lead_confirmation": (
            "Thank you for your interest in Forever Siam! ✨\n\n"
            "We've received your information and will contact you at {contact_time}.\n\n"
            "In the meantime, would you like to:\n"
            "• Browse our collections\n"
            "• Learn about our services\n"
            "• Get size recommendations"
        )
    }

    # Error and fallback templates
    ERRORS = {
        "not_understood": (
            "I apologize, but I didn't quite understand that. Could you please rephrase your question?\n\n"
            "You can ask me about:\n"
            "• Our collections\n"
            "• Sizing and fittings\n"
            "• Store location and hours\n"
            "• Pricing and payment options"
        ),
        "technical_error": (
            "I apologize, but I'm experiencing some technical difficulties.\n\n"
            "Please try again in a few moments, or contact our team directly at:\n"
            "📞 +66 2 123 4567\n"
            "✉️ info@foreversiam.com"
        )
    }

    # Store information templates
    STORE_INFO = {
        "location": (
            "📍 Forever Siam Fashion Boutique\n"
            "123 Sukhumvit Road\n"
            "Klongtoey, Bangkok 10110\n\n"
            "🚉 BTS: Asok Station (Exit 3)\n"
            "🚇 MRT: Sukhumvit Station (Exit 2)\n\n"
            "View on Google Maps: {map_link}"
        ),
        "hours": (
            "🕒 Store Hours:\n\n"
            "Monday - Saturday: 10:00 AM - 8:00 PM\n"
            "Sunday: 11:00 AM - 7:00 PM\n\n"
            "We are closed on major holidays."
        ),
        "contact": (
            "📞 Phone: +66 2 123 4567\n"
            "📱 WhatsApp: +66 8 1234 5678\n"
            "✉️ Email: info@foreversiam.com\n\n"
            "Follow us on social media:\n"
            "Facebook: @foreversiam\n"
            "Instagram: @foreversiam\n"
            "Line: @foreversiam"
        )
    }

    # Sales and promotion templates
    SALES = {
        "promotion_announcement": (
            "🎉 Special Promotion Alert! 🎉\n\n"
            "{promotion_details}\n\n"
            "Valid until {end_date}.\n"
            "Book your appointment now to take advantage of this offer!"
        ),
        "loyalty_program": (
            "✨ Forever Siam Loyalty Program ✨\n\n"
            "Join our loyalty program to enjoy:\n"
            "• Exclusive previews of new collections\n"
            "• Special member-only discounts\n"
            "• Birthday rewards\n"
            "• Early access to sales\n\n"
            "Would you like to join now?"
        )
    }

    @classmethod
    def get_template(cls, category: str, template_name: str, **kwargs) -> str:
        """
        Get a formatted template string.
        
        Args:
            category: Template category (e.g., 'GREETINGS', 'PRODUCTS')
            template_name: Name of the specific template
            **kwargs: Format parameters for the template
            
        Returns:
            Formatted template string
        """
        try:
            template = getattr(cls, category)[template_name]
            return template.format(**kwargs)
        except KeyError:
            return cls.ERRORS["not_understood"]
        except Exception as e:
            logging.error(f"Error formatting template: {str(e)}")
            return cls.ERRORS["technical_error"] 