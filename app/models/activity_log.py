from app import db
from datetime import datetime
from enum import Enum

class ActivityType(Enum):
    """Types of activities that can be logged."""
    # Authentication
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_REGISTER = "user_register"
    PASSWORD_RESET_REQUEST = "password_reset_request"
    PASSWORD_RESET_COMPLETE = "password_reset_complete"
    
    # Task operations
    TASK_CREATE = "task_create"
    TASK_UPDATE = "task_update"
    TASK_DELETE = "task_delete"
    TASK_BULK_UPDATE = "task_bulk_update"
    TASK_BULK_DELETE = "task_bulk_delete"
    
    # Tag operations
    TAG_CREATE = "tag_create"
    TAG_UPDATE = "tag_update"
    TAG_DELETE = "tag_delete"
    TAG_ADDED_TO_TASK = "tag_added_to_task"
    TAG_REMOVED_FROM_TASK = "tag_removed_from_task"
    
    # Comment operations
    COMMENT_CREATE = "comment_create"
    COMMENT_UPDATE = "comment_update"
    COMMENT_DELETE = "comment_delete"
    
    # User operations
    USER_UPDATE = "user_update"
    USER_DELETE = "user_delete"

class ActivityLog(db.Model):
    """Model for logging user activities."""
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False, index=True)
    entity_type = db.Column(db.String(50))  # e.g., 'task', 'tag', 'comment'
    entity_id = db.Column(db.Integer)  # ID of the affected entity
    description = db.Column(db.Text)
    activity_data = db.Column(db.JSON)  # Additional data about the activity (renamed from metadata)
    ip_address = db.Column(db.String(45))  # Support IPv6
    user_agent = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __init__(self, user_id, activity_type, entity_type=None, entity_id=None, 
                 description=None, activity_data=None, ip_address=None, user_agent=None):
        self.user_id = user_id
        self.activity_type = activity_type.value if isinstance(activity_type, ActivityType) else activity_type
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.description = description
        self.activity_data = activity_data
        self.ip_address = ip_address
        self.user_agent = user_agent
    
    def to_dict(self):
        """Convert activity log to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'activity_type': self.activity_type,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'description': self.description,
            'activity_data': self.activity_data,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def log(cls, user_id, activity_type, request=None, **kwargs):
        """Convenience method to log an activity."""
        log_entry = cls(
            user_id=user_id,
            activity_type=activity_type,
            entity_type=kwargs.get('entity_type'),
            entity_id=kwargs.get('entity_id'),
            description=kwargs.get('description'),
            activity_data=kwargs.get('activity_data'),  # Updated from metadata
            ip_address=request.remote_addr if request else None,
            user_agent=request.headers.get('User-Agent', '')[:256] if request else None
        )
        
        db.session.add(log_entry)
        # Note: Caller is responsible for committing the transaction
        return log_entry
    
    @classmethod
    def get_user_activities(cls, user_id, limit=50, offset=0, activity_types=None):
        """Get activities for a specific user."""
        query = cls.query.filter_by(user_id=user_id)
        
        if activity_types:
            query = query.filter(cls.activity_type.in_(activity_types))
        
        return query.order_by(cls.created_at.desc()).limit(limit).offset(offset).all()
    
    @classmethod
    def get_entity_history(cls, entity_type, entity_id, limit=50):
        """Get activity history for a specific entity."""
        return cls.query.filter_by(
            entity_type=entity_type,
            entity_id=entity_id
        ).order_by(cls.created_at.desc()).limit(limit).all()
    
    def __repr__(self):
        return f'<ActivityLog {self.activity_type} by user {self.user_id}>'