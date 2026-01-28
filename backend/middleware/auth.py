"""
Authentication Middleware.
Verifies Firebase ID Tokens.
"""
from typing import Optional, Dict, Any
from firebase_admin import auth
import logging

logger = logging.getLogger(__name__)

class AuthMiddleware:
    def verify_token(self, auth_header: str) -> Optional[Dict[str, Any]]:
        """
        Verify Bearer token from Authorization header.
        Returns decoded token dict if valid, None otherwise.
        """
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
            
        token = auth_header.split("Bearer ")[1]
        try:
            # Verify the ID token while checking if the token is revoked by
            # passing check_revoked=True.
            decoded_token = auth.verify_id_token(token, check_revoked=True)
            return decoded_token
        except ValueError:
            logger.warning("Invalid token format")
            return None
        except auth.AuthError as e:
            logger.warning(f"Token verification failed: {e}")
            return None
