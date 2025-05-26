from app import db

# Many-to-many relationship table between tasks and tags
task_tags = db.Table('task_tags',
    db.Column('task_id', db.Integer, db.ForeignKey('tasks.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)

class Tag(db.Model):
    """Tag model for categorizing tasks."""
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    color = db.Column(db.String(7), default="#3498db")  # Default to a blue color
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # Relationships
    tasks = db.relationship(
    'Task',
    secondary=task_tags,
    lazy='selectin',
    backref=db.backref('tags', lazy='selectin')
    )
    
    def __init__(self, name, user_id, color="#3498db"):
        self.name = name
        self.user_id = user_id
        self.color = color
    
    def to_dict(self):
        """Convert tag object to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'user_id': self.user_id
        }
    
    def __repr__(self):
        return f'<Tag {self.name}>'