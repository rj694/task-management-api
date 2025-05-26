from app import db
from datetime import datetime

class Comment(db.Model):
    """Comment model for storing task comments."""
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    def __init__(self, content, task_id, user_id):
        self.content = content
        self.task_id = task_id
        self.user_id = user_id
    
    def to_dict(self):
        """Convert comment object to dictionary."""
        return {
            'id': self.id,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'task_id': self.task_id,
            'user_id': self.user_id
        }
    
    def __repr__(self):
        return f'<Comment {self.id}>'