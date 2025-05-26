from app import create_app, db
from app.models.user import User
from app.models.task import Task
from datetime import datetime, timedelta

def verify_models():
    """Verify that models are correctly implemented."""
    # Create a test-specific app with SQLite in-memory database
    app = create_app('app.config.TestingConfig')  # This uses SQLite in-memory
    
    with app.app_context():
        # Drop and recreate tables to start fresh
        db.drop_all()
        db.create_all()
        
        print("Testing User model...")
        
        # Create a test user
        user = User(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        db.session.add(user)
        db.session.commit()
        
        # Check if user was created successfully
        fetched_user = User.query.filter_by(username="testuser").first()
        assert fetched_user is not None, "User was not created or cannot be retrieved"
        assert fetched_user.email == "test@example.com", "User email does not match"
        assert fetched_user.check_password("password123"), "Password checking failed"
        
        print("User model verification passed!")
        
        print("Testing Task model...")
        
        # Create test tasks for the user
        tasks = [
            Task(
                title="Task 1",
                description="Description for Task 1",
                status="pending",
                priority="high",
                user_id=user.id,
                due_date=datetime.utcnow() + timedelta(days=1)
            ),
            Task(
                title="Task 2",
                description="Description for Task 2",
                status="in_progress",
                priority="medium",
                user_id=user.id
            )
        ]
        
        db.session.add_all(tasks)
        db.session.commit()
        
        # Check if tasks were created successfully
        user_tasks = Task.query.filter_by(user_id=user.id).all()
        assert len(user_tasks) == 2, f"Expected 2 tasks, but got {len(user_tasks)}"
        
        # Check task relationship
        assert len(user.tasks) == 2, f"User tasks relationship returned {len(user.tasks)} tasks instead of 2"
        
        # Check task conversion to dict
        task_dict = tasks[0].to_dict()
        assert task_dict['title'] == "Task 1", "Task to_dict() method failed"
        assert task_dict['status'] == "pending", "Task to_dict() method failed"
        
        print("Task model verification passed!")
        
        # Clean up
        db.session.delete(user)  # This should cascade delete the tasks
        db.session.commit()
        
        # Verify cascade delete
        remaining_tasks = Task.query.filter_by(user_id=user.id).all()
        assert len(remaining_tasks) == 0, "Cascade delete failed for tasks"
        
        print("All models verified successfully!")

if __name__ == "__main__":
    verify_models()