import os
import json
import hashlib
import hmac
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import logging
from pathlib import Path

from utils.logger import logger

class SecurityManager:
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.token_file = self.config_dir / "tokens.json"
        self.admin_file = self.config_dir / "admins.json"
        self.session_file = self.config_dir / "sessions.json"
        
        # Load or initialize security data
        self.tokens = self._load_json(self.token_file, {})
        self.admins = self._load_json(self.admin_file, {})
        self.sessions = self._load_json(self.session_file, {})
        
        # Set up logging
        self.logger = logging.getLogger("security")
    
    def _load_json(self, file_path: Path, default: Dict) -> Dict:
        """Load JSON data from file."""
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return default
        except Exception as e:
            self.logger.error(f"Error loading {file_path}: {e}")
            return default
    
    def _save_json(self, file_path: Path, data: Dict) -> bool:
        """Save JSON data to file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            self.logger.error(f"Error saving {file_path}: {e}")
            return False
    
    def verify_bot_token(self, token: str) -> bool:
        """Verify the bot token."""
        stored_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not stored_token:
            self.logger.error("Bot token not found in environment")
            return False
        
        return hmac.compare_digest(token, stored_token)
    
    def verify_admin(self, user_id: str) -> bool:
        """Verify if a user is an admin."""
        return user_id in self.admins
    
    def add_admin(self, user_id: str, name: str) -> bool:
        """Add a new admin user."""
        try:
            self.admins[user_id] = {
                "name": name,
                "added_at": datetime.now().isoformat(),
                "last_active": datetime.now().isoformat()
            }
            return self._save_json(self.admin_file, self.admins)
        except Exception as e:
            self.logger.error(f"Error adding admin {user_id}: {e}")
            return False
    
    def remove_admin(self, user_id: str) -> bool:
        """Remove an admin user."""
        try:
            if user_id in self.admins:
                del self.admins[user_id]
                return self._save_json(self.admin_file, self.admins)
            return False
        except Exception as e:
            self.logger.error(f"Error removing admin {user_id}: {e}")
            return False
    
    def create_session(self, user_id: str, duration_hours: int = 24) -> Optional[str]:
        """Create a new session for a user."""
        try:
            # Generate session token
            token = hashlib.sha256(
                f"{user_id}{time.time()}".encode()
            ).hexdigest()
            
            # Store session data
            self.sessions[token] = {
                "user_id": user_id,
                "created_at": datetime.now().isoformat(),
                "expires_at": (
                    datetime.now() + timedelta(hours=duration_hours)
                ).isoformat()
            }
            
            if self._save_json(self.session_file, self.sessions):
                return token
            return None
        except Exception as e:
            self.logger.error(f"Error creating session for {user_id}: {e}")
            return None
    
    def verify_session(self, token: str) -> Tuple[bool, Optional[str]]:
        """Verify a session token and return user ID if valid."""
        try:
            if token not in self.sessions:
                return False, None
            
            session = self.sessions[token]
            expires_at = datetime.fromisoformat(session["expires_at"])
            
            if datetime.now() > expires_at:
                del self.sessions[token]
                self._save_json(self.session_file, self.sessions)
                return False, None
            
            return True, session["user_id"]
        except Exception as e:
            self.logger.error(f"Error verifying session {token}: {e}")
            return False, None
    
    def invalidate_session(self, token: str) -> bool:
        """Invalidate a session token."""
        try:
            if token in self.sessions:
                del self.sessions[token]
                return self._save_json(self.session_file, self.sessions)
            return False
        except Exception as e:
            self.logger.error(f"Error invalidating session {token}: {e}")
            return False
    
    def cleanup_expired_sessions(self) -> None:
        """Remove expired sessions."""
        try:
            now = datetime.now()
            expired = [
                token for token, session in self.sessions.items()
                if datetime.fromisoformat(session["expires_at"]) < now
            ]
            
            for token in expired:
                del self.sessions[token]
            
            if expired:
                self._save_json(self.session_file, self.sessions)
                self.logger.info(f"Cleaned up {len(expired)} expired sessions")
        except Exception as e:
            self.logger.error(f"Error cleaning up sessions: {e}")
    
    def update_admin_activity(self, user_id: str) -> None:
        """Update last active timestamp for an admin."""
        try:
            if user_id in self.admins:
                self.admins[user_id]["last_active"] = datetime.now().isoformat()
                self._save_json(self.admin_file, self.admins)
        except Exception as e:
            self.logger.error(f"Error updating admin activity for {user_id}: {e}")
    
    def get_admin_list(self) -> Dict[str, Dict]:
        """Get list of all admins with their details."""
        return self.admins
    
    def get_active_sessions(self) -> Dict[str, Dict]:
        """Get list of all active sessions."""
        self.cleanup_expired_sessions()
        return self.sessions

# Create global security manager instance
security_manager = SecurityManager() 