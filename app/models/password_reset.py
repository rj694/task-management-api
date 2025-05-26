from app import db
from datetime import datetime, timedelta
import secrets

class PasswordResetToken(db.Model):
    """Model for storing password reset tokens."""
    __tablename__ = 'password_reset_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(100), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, user_id, expires_in_hours=24):
        self.token = secrets.token_urlsafe(32)
        self.user_id = user_id
        self.expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
    
    @property
    def is_expired(self):
        """Check if token has expired."""
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_valid(self):
        """Check if token is valid (not expired and not used)."""
        return not self.is_expired and not self.used
    
    def mark_as_used(self):
        """Mark token as used."""
        self.used = True
    
    @classmethod
    def get_valid_token(cls, token):
        """Get a valid token by token string."""
        reset_token = cls.query.filter_by(token=token, used=False).first()
        if reset_token and reset_token.is_valid:
            return reset_token
        return None
    
    def __repr__(self):
        return f'<PasswordResetToken {self.token[:8]}...>'