from app import db
from app.models.user import User
from app.models.task import Task
from sqlalchemy import text

def init_db():
    """Initialize database with tables."""
    # Create tables
    db.create_all()
    print("Database tables created.")

def drop_db():
    """Drop all database tables."""
    db.drop_all()
    print("Database tables dropped.")

def create_sample_data():
    """Create sample data for development."""
    # Create a regular user
    user = User(
        username="demo",
        email="demo@example.com",
        password="password123",
        role="user"
    )
    db.session.add(user)
    
    # Create an admin user
    admin = User(
        username="admin",
        email="admin@example.com",
        password="adminpassword",
        role="admin"
    )
    db.session.add(admin)
    
    db.session.commit()
    
    # Create sample tasks for regular user
    tasks = [
        Task(
            title="Complete project setup",
            description="Initialize the project structure and dependencies",
            status="completed",
            priority="high",
            user_id=user.id
        ),
        Task(
            title="Implement user authentication",
            description="Create login and registration endpoints",
            status="in_progress",
            priority="high",
            user_id=user.id
        ),
        Task(
            title="Design database schema",
            description="Create models for users and tasks",
            status="completed",
            priority="medium",
            user_id=user.id
        ),
        Task(
            title="Write API documentation",
            description="Document all API endpoints using Swagger",
            status="pending",
            priority="low",
            user_id=user.id
        )
    ]
    
    db.session.add_all(tasks)
    
    # Create sample tasks for admin user
    admin_tasks = [
        Task(
            title="Review security policies",
            description="Ensure all endpoints have proper authorization",
            status="pending",
            priority="high",
            user_id=admin.id
        ),
        Task(
            title="Deploy to production",
            description="Prepare and deploy the app to production server",
            status="pending",
            priority="medium",
            user_id=admin.id
        )
    ]
    
    db.session.add_all(admin_tasks)
    db.session.commit()
    
    print(f"Created regular user: {user.username}")
    print(f"Created admin user: {admin.username}")
    print(f"Created {len(tasks)} tasks for regular user")
    print(f"Created {len(admin_tasks)} tasks for admin user")