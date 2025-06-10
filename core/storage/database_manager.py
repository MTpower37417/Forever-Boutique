import os
import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, base_dir: str = "data"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize data directories
        self.dirs = {
            "customers": self.base_dir / "customers",
            "products": self.base_dir / "products",
            "bookings": self.base_dir / "bookings",
            "logs": self.base_dir / "logs",
            "cache": self.base_dir / "cache"
        }
        
        for dir_path in self.dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def save_json(self, data: Dict, filename: str, subdir: str = None) -> bool:
        """Save data to a JSON file."""
        try:
            if subdir:
                file_path = self.dirs[subdir] / filename
            else:
                file_path = self.base_dir / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error saving JSON {filename}: {e}")
            return False
    
    def load_json(self, filename: str, subdir: str = None) -> Optional[Dict]:
        """Load data from a JSON file."""
        try:
            if subdir:
                file_path = self.dirs[subdir] / filename
            else:
                file_path = self.base_dir / filename
            
            if not file_path.exists():
                return {}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading JSON {filename}: {e}")
            return None
    
    def append_csv(self, data: List[Dict], filename: str, subdir: str = None) -> bool:
        """Append data to a CSV file."""
        try:
            if subdir:
                file_path = self.dirs[subdir] / filename
            else:
                file_path = self.base_dir / filename
            
            # Create file with headers if it doesn't exist
            if not file_path.exists():
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
            
            # Append data
            with open(file_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writerows(data)
            return True
        except Exception as e:
            logger.error(f"Error appending to CSV {filename}: {e}")
            return False
    
    def read_csv(self, filename: str, subdir: str = None) -> List[Dict]:
        """Read data from a CSV file."""
        try:
            if subdir:
                file_path = self.dirs[subdir] / filename
            else:
                file_path = self.base_dir / filename
            
            if not file_path.exists():
                return []
            
            with open(file_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return list(reader)
        except Exception as e:
            logger.error(f"Error reading CSV {filename}: {e}")
            return []
    
    def backup_file(self, filename: str, subdir: str = None) -> bool:
        """Create a backup of a file."""
        try:
            if subdir:
                file_path = self.dirs[subdir] / filename
            else:
                file_path = self.base_dir / filename
            
            if not file_path.exists():
                return False
            
            backup_dir = self.base_dir / "backups"
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"{filename}.{timestamp}"
            
            with open(file_path, 'rb') as src, open(backup_path, 'wb') as dst:
                dst.write(src.read())
            return True
        except Exception as e:
            logger.error(f"Error backing up {filename}: {e}")
            return False
    
    def cleanup_old_backups(self, days: int = 30) -> None:
        """Remove backup files older than specified days."""
        try:
            backup_dir = self.base_dir / "backups"
            if not backup_dir.exists():
                return
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            for backup_file in backup_dir.glob("*.*"):
                try:
                    timestamp = datetime.strptime(
                        backup_file.suffix[1:],
                        "%Y%m%d_%H%M%S"
                    )
                    if timestamp < cutoff_date:
                        backup_file.unlink()
                except ValueError:
                    continue
        except Exception as e:
            logger.error(f"Error cleaning up old backups: {e}")
    
    def get_file_stats(self, filename: str, subdir: str = None) -> Dict[str, Any]:
        """Get statistics about a file."""
        try:
            if subdir:
                file_path = self.dirs[subdir] / filename
            else:
                file_path = self.base_dir / filename
            
            if not file_path.exists():
                return {}
            
            stats = file_path.stat()
            return {
                "size": stats.st_size,
                "created": datetime.fromtimestamp(stats.st_ctime),
                "modified": datetime.fromtimestamp(stats.st_mtime),
                "accessed": datetime.fromtimestamp(stats.st_atime)
            }
        except Exception as e:
            logger.error(f"Error getting stats for {filename}: {e}")
            return {} 