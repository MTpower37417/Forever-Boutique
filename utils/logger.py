import os
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from pythonjsonlogger import jsonlogger

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['level'] = record.levelname
        log_record['logger'] = record.name

class Logger:
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure root logger
        self.setup_root_logger()
        
        # Create loggers for different components
        self.loggers = {
            "bot": self.setup_logger("bot"),
            "customer": self.setup_logger("customer"),
            "booking": self.setup_logger("booking"),
            "product": self.setup_logger("product"),
            "error": self.setup_logger("error"),
            "performance": self.setup_logger("performance")
        }
    
    def setup_root_logger(self) -> None:
        """Configure the root logger."""
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        
        # File handler
        file_handler = logging.FileHandler(
            self.log_dir / "bot.log",
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        file_formatter = CustomJsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    def setup_logger(self, name: str) -> logging.Logger:
        """Set up a component-specific logger."""
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        
        # Component-specific file handler
        file_handler = logging.FileHandler(
            self.log_dir / f"{name}.log",
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        formatter = CustomJsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def log_bot_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Log bot-related events."""
        logger = self.loggers["bot"]
        logger.info(
            f"Bot Event: {event_type}",
            extra={"event_type": event_type, "data": data}
        )
    
    def log_customer_event(self, customer_id: str, event_type: str, data: Dict[str, Any]) -> None:
        """Log customer-related events."""
        logger = self.loggers["customer"]
        logger.info(
            f"Customer Event: {event_type}",
            extra={
                "customer_id": customer_id,
                "event_type": event_type,
                "data": data
            }
        )
    
    def log_booking_event(self, booking_id: str, event_type: str, data: Dict[str, Any]) -> None:
        """Log booking-related events."""
        logger = self.loggers["booking"]
        logger.info(
            f"Booking Event: {event_type}",
            extra={
                "booking_id": booking_id,
                "event_type": event_type,
                "data": data
            }
        )
    
    def log_product_event(self, product_id: str, event_type: str, data: Dict[str, Any]) -> None:
        """Log product-related events."""
        logger = self.loggers["product"]
        logger.info(
            f"Product Event: {event_type}",
            extra={
                "product_id": product_id,
                "event_type": event_type,
                "data": data
            }
        )
    
    def log_error(self, error_type: str, error_message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Log error events."""
        logger = self.loggers["error"]
        logger.error(
            f"Error: {error_type}",
            extra={
                "error_type": error_type,
                "error_message": error_message,
                "context": context or {}
            }
        )
    
    def log_performance(self, operation: str, duration_ms: float, context: Optional[Dict[str, Any]] = None) -> None:
        """Log performance metrics."""
        logger = self.loggers["performance"]
        logger.info(
            f"Performance: {operation}",
            extra={
                "operation": operation,
                "duration_ms": duration_ms,
                "context": context or {}
            }
        )
    
    def get_recent_logs(self, logger_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent logs for a specific logger."""
        log_file = self.log_dir / f"{logger_name}.log"
        if not log_file.exists():
            return []
        
        logs = []
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f.readlines()[-limit:]:
                try:
                    log_entry = json.loads(line)
                    logs.append(log_entry)
                except json.JSONDecodeError:
                    continue
        
        return logs
    
    def cleanup_old_logs(self, days: int = 30) -> None:
        """Remove log files older than specified days."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for log_file in self.log_dir.glob("*.log"):
            try:
                if datetime.fromtimestamp(log_file.stat().st_mtime) < cutoff_date:
                    log_file.unlink()
            except Exception as e:
                print(f"Error cleaning up log file {log_file}: {e}")

# Create global logger instance
logger = Logger() 