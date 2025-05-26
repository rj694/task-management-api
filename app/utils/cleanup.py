from app import db
from app.models.token_blacklist import TokenBlacklist
from datetime import datetime, timezone
import logging

def cleanup_expired_tokens():
    """Remove expired tokens from the blacklist."""
    try:
        # Get current time
        now = datetime.now(timezone.utc)
        
        # Find expired tokens
        expired_tokens = TokenBlacklist.query.filter(TokenBlacklist.expires_at < now).all()
        
        if expired_tokens:
            # Delete expired tokens
            for token in expired_tokens:
                db.session.delete(token)
            
            # Commit changes
            db.session.commit()
            
            return len(expired_tokens)
        
        return 0
    except Exception as e:
        logging.error(f"Error cleaning up expired tokens: {str(e)}")
        db.session.rollback()
        return -1