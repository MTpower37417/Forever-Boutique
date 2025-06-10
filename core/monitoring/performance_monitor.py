import os
import time
import psutil
import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
import json
from pathlib import Path
import threading
from functools import wraps

from utils.logger import logger

class PerformanceMonitor:
    def __init__(self):
        self.metrics: Dict[str, List[Dict[str, Any]]] = {}
        self.thresholds: Dict[str, float] = {
            "cpu_percent": float(os.getenv("CPU_THRESHOLD", "80")),
            "memory_percent": float(os.getenv("MEMORY_THRESHOLD", "80")),
            "response_time": float(os.getenv("RESPONSE_TIME_THRESHOLD", "1000")),
            "error_rate": float(os.getenv("ERROR_RATE_THRESHOLD", "5"))
        }
        self.monitoring_interval = int(os.getenv("MONITORING_INTERVAL", "60"))
        self.retention_period = int(os.getenv("METRICS_RETENTION_DAYS", "7"))
        self.logger = logging.getLogger("performance_monitor")
        self._monitoring_thread: Optional[threading.Thread] = None
        self._stop_monitoring = threading.Event()
    
    def start_monitoring(self) -> None:
        """Start the performance monitoring thread."""
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            return
        
        self._stop_monitoring.clear()
        self._monitoring_thread = threading.Thread(
            target=self._monitor_performance,
            daemon=True
        )
        self._monitoring_thread.start()
        self.logger.info("Performance monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop the performance monitoring thread."""
        if not self._monitoring_thread or not self._monitoring_thread.is_alive():
            return
        
        self._stop_monitoring.set()
        self._monitoring_thread.join()
        self.logger.info("Performance monitoring stopped")
    
    def _monitor_performance(self) -> None:
        """Monitor system performance metrics."""
        while not self._stop_monitoring.is_set():
            try:
                # Collect system metrics
                metrics = self._collect_system_metrics()
                
                # Store metrics
                self._store_metrics(metrics)
                
                # Check thresholds
                self._check_thresholds(metrics)
                
                # Clean up old metrics
                self._cleanup_old_metrics()
                
                # Wait for next interval
                time.sleep(self.monitoring_interval)
            except Exception as e:
                self.logger.error(f"Error in performance monitoring: {e}")
    
    def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system performance metrics."""
        process = psutil.Process()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": process.cpu_percent(),
            "memory_percent": process.memory_percent(),
            "memory_info": {
                "rss": process.memory_info().rss,
                "vms": process.memory_info().vms
            },
            "thread_count": process.num_threads(),
            "open_files": len(process.open_files()),
            "connections": len(process.connections())
        }
    
    def _store_metrics(self, metrics: Dict[str, Any]) -> None:
        """Store performance metrics."""
        for metric_name, value in metrics.items():
            if metric_name not in self.metrics:
                self.metrics[metric_name] = []
            
            self.metrics[metric_name].append({
                "timestamp": metrics["timestamp"],
                "value": value
            })
    
    def _check_thresholds(self, metrics: Dict[str, Any]) -> None:
        """Check if metrics exceed thresholds."""
        for metric_name, threshold in self.thresholds.items():
            if metric_name in metrics:
                value = metrics[metric_name]
                if value > threshold:
                    self.logger.warning(
                        f"Metric {metric_name} exceeded threshold",
                        extra={
                            "metric": metric_name,
                            "value": value,
                            "threshold": threshold
                        }
                    )
    
    def _cleanup_old_metrics(self) -> None:
        """Remove metrics older than retention period."""
        cutoff = datetime.now() - timedelta(days=self.retention_period)
        
        for metric_name in self.metrics:
            self.metrics[metric_name] = [
                m for m in self.metrics[metric_name]
                if datetime.fromisoformat(m["timestamp"]) > cutoff
            ]
    
    def get_metrics(
        self,
        metric_name: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get performance metrics with optional filtering."""
        if not start_time:
            start_time = datetime.now() - timedelta(days=1)
        if not end_time:
            end_time = datetime.now()
        
        result = {}
        
        if metric_name:
            if metric_name in self.metrics:
                result[metric_name] = [
                    m for m in self.metrics[metric_name]
                    if start_time <= datetime.fromisoformat(m["timestamp"]) <= end_time
                ]
        else:
            for name, values in self.metrics.items():
                result[name] = [
                    m for m in values
                    if start_time <= datetime.fromisoformat(m["timestamp"]) <= end_time
                ]
        
        return result
    
    def set_threshold(self, metric_name: str, threshold: float) -> None:
        """Set threshold for a metric."""
        self.thresholds[metric_name] = threshold
        self.logger.info(
            f"Set threshold for {metric_name}",
            extra={"threshold": threshold}
        )
    
    def get_thresholds(self) -> Dict[str, float]:
        """Get all metric thresholds."""
        return self.thresholds.copy()
    
    def reset_metrics(self, metric_name: Optional[str] = None) -> None:
        """Reset performance metrics."""
        if metric_name:
            if metric_name in self.metrics:
                self.metrics[metric_name] = []
        else:
            self.metrics.clear()

# Create global performance monitor instance
performance_monitor = PerformanceMonitor()

# Decorator for monitoring function performance
def monitor_performance(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Log performance metric
            logger.log_performance(
                func.__name__,
                execution_time,
                {"args": str(args), "kwargs": str(kwargs)}
            )
            
            return result
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            
            # Log error with performance metric
            logger.log_error(
                func.__name__,
                str(e),
                {
                    "execution_time": execution_time,
                    "args": str(args),
                    "kwargs": str(kwargs)
                }
            )
            raise
    
    return wrapper 