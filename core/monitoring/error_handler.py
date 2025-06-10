import os
import sys
import traceback
import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
import json
from pathlib import Path

from utils.logger import logger

class ErrorHandler:
    def __init__(self):
        self.error_handlers: Dict[str, List[Callable]] = {}
        self.error_counts: Dict[str, int] = {}
        self.error_threshold = int(os.getenv("ERROR_THRESHOLD", "100"))
        self.error_window = int(os.getenv("ERROR_WINDOW", "3600"))
        self.error_timestamps: Dict[str, List[datetime]] = {}
        self.logger = logging.getLogger("error_handler")
    
    def register_handler(
        self,
        error_type: str,
        handler: Callable[[Exception, Dict[str, Any]], None]
    ) -> None:
        """Register an error handler for a specific error type."""
        if error_type not in self.error_handlers:
            self.error_handlers[error_type] = []
        self.error_handlers[error_type].append(handler)
        self.logger.info(f"Registered handler for {error_type}")
    
    def handle_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Handle an error with appropriate logging and monitoring."""
        error_type = type(error).__name__
        context = context or {}
        
        # Log error
        self.logger.error(
            f"Error occurred: {error_type}",
            extra={
                "error": str(error),
                "traceback": traceback.format_exc(),
                "context": context
            }
        )
        
        # Update error counts
        if error_type not in self.error_counts:
            self.error_counts[error_type] = 0
        self.error_counts[error_type] += 1
        
        # Update error timestamps
        if error_type not in self.error_timestamps:
            self.error_timestamps[error_type] = []
        self.error_timestamps[error_type].append(datetime.now())
        
        # Clean up old timestamps
        self._cleanup_old_timestamps(error_type)
        
        # Check error threshold
        if self._check_error_threshold(error_type):
            self._handle_threshold_exceeded(error_type)
        
        # Call registered handlers
        if error_type in self.error_handlers:
            for handler in self.error_handlers[error_type]:
                try:
                    handler(error, context)
                except Exception as e:
                    self.logger.error(
                        f"Error in error handler: {str(e)}",
                        extra={"original_error": str(error)}
                    )
    
    def _cleanup_old_timestamps(self, error_type: str) -> None:
        """Remove timestamps older than the error window."""
        if error_type not in self.error_timestamps:
            return
        
        window_start = datetime.now() - timedelta(seconds=self.error_window)
        self.error_timestamps[error_type] = [
            ts for ts in self.error_timestamps[error_type]
            if ts > window_start
        ]
    
    def _check_error_threshold(self, error_type: str) -> bool:
        """Check if error count exceeds threshold within window."""
        if error_type not in self.error_timestamps:
            return False
        
        return len(self.error_timestamps[error_type]) >= self.error_threshold
    
    def _handle_threshold_exceeded(self, error_type: str) -> None:
        """Handle cases where error threshold is exceeded."""
        self.logger.critical(
            f"Error threshold exceeded for {error_type}",
            extra={
                "error_type": error_type,
                "count": len(self.error_timestamps[error_type]),
                "threshold": self.error_threshold,
                "window": self.error_window
            }
        )
        
        # Notify administrators
        self._notify_administrators(error_type)
        
        # Take corrective action
        self._take_corrective_action(error_type)
    
    def _notify_administrators(self, error_type: str) -> None:
        """Notify administrators about critical error conditions."""
        try:
            # Get error statistics
            stats = self.get_error_statistics(error_type)
            
            # Log notification
            self.logger.info(
                "Notifying administrators",
                extra={
                    "error_type": error_type,
                    "statistics": stats
                }
            )
            
            # TODO: Implement actual notification (email, SMS, etc.)
        except Exception as e:
            self.logger.error(f"Failed to notify administrators: {e}")
    
    def _take_corrective_action(self, error_type: str) -> None:
        """Take corrective action for critical error conditions."""
        try:
            # Log corrective action
            self.logger.info(
                "Taking corrective action",
                extra={"error_type": error_type}
            )
            
            # TODO: Implement actual corrective actions
            # - Restart services
            # - Clear caches
            # - Reset connections
            # - etc.
        except Exception as e:
            self.logger.error(f"Failed to take corrective action: {e}")
    
    def get_error_statistics(self, error_type: Optional[str] = None) -> Dict[str, Any]:
        """Get error statistics for monitoring."""
        stats = {
            "total_errors": sum(self.error_counts.values()),
            "error_types": {}
        }
        
        if error_type:
            if error_type in self.error_counts:
                stats["error_types"][error_type] = {
                    "count": self.error_counts[error_type],
                    "recent_count": len(self.error_timestamps.get(error_type, [])),
                    "first_occurrence": min(self.error_timestamps.get(error_type, [datetime.now()])),
                    "last_occurrence": max(self.error_timestamps.get(error_type, [datetime.now()]))
                }
        else:
            for et in self.error_counts:
                stats["error_types"][et] = {
                    "count": self.error_counts[et],
                    "recent_count": len(self.error_timestamps.get(et, [])),
                    "first_occurrence": min(self.error_timestamps.get(et, [datetime.now()])),
                    "last_occurrence": max(self.error_timestamps.get(et, [datetime.now()]))
                }
        
        return stats
    
    def reset_error_counts(self, error_type: Optional[str] = None) -> None:
        """Reset error counts for monitoring."""
        if error_type:
            if error_type in self.error_counts:
                self.error_counts[error_type] = 0
                self.error_timestamps[error_type] = []
        else:
            self.error_counts.clear()
            self.error_timestamps.clear()

# Create global error handler instance
error_handler = ErrorHandler()

# Register default error handlers
@error_handler.register_handler("ValueError")
def handle_value_error(error: Exception, context: Dict[str, Any]) -> None:
    """Handle ValueError with specific logging."""
    logger.log_error(
        "value_error",
        str(error),
        context
    )

@error_handler.register_handler("TypeError")
def handle_type_error(error: Exception, context: Dict[str, Any]) -> None:
    """Handle TypeError with specific logging."""
    logger.log_error(
        "type_error",
        str(error),
        context
    )

@error_handler.register_handler("KeyError")
def handle_key_error(error: Exception, context: Dict[str, Any]) -> None:
    """Handle KeyError with specific logging."""
    logger.log_error(
        "key_error",
        str(error),
        context
    )

@error_handler.register_handler("AttributeError")
def handle_attribute_error(error: Exception, context: Dict[str, Any]) -> None:
    """Handle AttributeError with specific logging."""
    logger.log_error(
        "attribute_error",
        str(error),
        context
    )

@error_handler.register_handler("Exception")
def handle_general_error(error: Exception, context: Dict[str, Any]) -> None:
    """Handle general exceptions with specific logging."""
    logger.log_error(
        "general_error",
        str(error),
        context
    ) 