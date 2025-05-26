from app import db
from datetime import datetime

class Task(db.Model):
    """Task model for storing task related details."""
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending', index=True)  # pending, in_progress, completed
    priority = db.Column(db.String(20), default='medium', index=True)  # low, medium, high
    due_date = db.Column(db.DateTime, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Relationships
    comments = db.relationship('Comment', backref='task', lazy=True, cascade='all, delete-orphan')
    
    # The tags relationship is defined in the Tag model via the task_tags table
    
    def __init__(self, title, user_id, description=None, status='pending', 
                 priority='medium', due_date=None):
        self.title = title
        self.user_id = user_id
        self.description = description
        self.status = status
        self.priority = priority
        self.due_date = due_date
    
    def to_dict(self):
        """Convert task object to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user_id': self.user_id
        }
    
    def __repr__(self):
        return f'<Task {self.title}>'