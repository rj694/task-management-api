from app import db
from datetime import datetime

class TokenBlacklist(db.Model):
    """Model for storing blacklisted tokens."""
    __tablename__ = 'token_blacklist'
    
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, unique=True)
    token_type = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    revoked_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    
    def __repr__(self):
        return f'<TokenBlacklist {self.jti}>'
    
    @classmethod
    def is_token_revoked(cls, jwt_payload):
        """Check if the given token is blacklisted."""
        jti = jwt_payload['jti']
        return cls.query.filter_by(jti=jti).first() is not None