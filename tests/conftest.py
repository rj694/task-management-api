import pytest
from datetime import datetime, timedelta
from app import create_app, db
from app.models.user import User
from app.models.task import Task
from app.models.tag import Tag
from app.models.comment import Comment
from flask_jwt_extended import create_access_token, create_refresh_token

@pytest.fixture
def app():
    """Create application for the tests."""
    app = create_app('app.config.TestingConfig')
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    yield app
    
    # Clean up
    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def regular_user(app):
    """Create regular test user."""
    with app.app_context():
        user = User(
            username="testuser",
            email="test@example.com",
            password="password123",
            role="user"
        )
        db.session.add(user)
        db.session.commit()
        
        # Store the user ID for later use
        user_id = user.id
        
        # Clear the session to simulate real usage
        db.session.close()
        
        # Return a fresh instance of the user for each test
        fresh_user = db.session.get(User, user_id)
        yield fresh_user
        
        # Clean up session after the test is done
        db.session.close()

@pytest.fixture
def admin_user(app):
    """Create admin test user."""
    with app.app_context():
        admin = User(
            username="admin",
            email="admin@example.com",
            password="adminpassword",
            role="admin"
        )
        db.session.add(admin)
        db.session.commit()
        
        # Store the user ID for later use
        admin_id = admin.id
        
        # Clear the session to simulate real usage
        db.session.close()
        
        # Return a fresh instance of the user for each test
        fresh_admin = db.session.get(User, admin_id)
        yield fresh_admin
        
        # Clean up session after the test is done
        db.session.close()

@pytest.fixture
def auth_tokens(app, regular_user):
    """Create authentication tokens for a regular user."""
    with app.app_context():
        # Get a fresh instance to ensure it's attached to the session
        user = db.session.merge(regular_user)
        
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }

@pytest.fixture
def admin_auth_tokens(app, admin_user):
    """Create authentication tokens for an admin user."""
    with app.app_context():
        # Get a fresh instance to ensure it's attached to the session
        admin = db.session.merge(admin_user)
        
        access_token = create_access_token(identity=str(admin.id))
        refresh_token = create_refresh_token(identity=str(admin.id))
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }

@pytest.fixture
def auth_headers(auth_tokens):
    """Create authentication headers for a regular user."""
    return {
        "Authorisation": f"Bearer {auth_tokens['access_token']}"
    }

@pytest.fixture
def admin_auth_headers(admin_auth_tokens):
    """Create authentication headers for an admin user."""
    return {
        "Authorisation": f"Bearer {admin_auth_tokens['access_token']}"
    }

@pytest.fixture
def test_tasks(app, regular_user):
    """Create test tasks for a regular user."""
    with app.app_context():
        # Get a fresh instance to ensure it's attached to the session
        user = db.session.merge(regular_user)
        
        tasks = [
            Task(
                title="Test Task 1",
                description="Description for Test Task 1",
                status="pending",
                priority="high",
                due_date=datetime.utcnow() + timedelta(days=1),
                user_id=user.id
            ),
            Task(
                title="Test Task 2",
                description="Description for Test Task 2",
                status="in_progress",
                priority="medium",
                user_id=user.id
            ),
            Task(
                title="Test Task 3",
                description="Description for Test Task 3",
                status="completed",
                priority="low",
                user_id=user.id
            )
        ]
        
        db.session.add_all(tasks)
        db.session.commit()
        
        # Store task IDs
        task_ids = [task.id for task in tasks]
        
        # Clear the session
        db.session.close()
        
        # Return fresh instances
        fresh_tasks = [db.session.get(Task, task_id) for task_id in task_ids]
        return fresh_tasks

@pytest.fixture
def test_tags(app, regular_user):
    """Create test tags for a regular user."""
    with app.app_context():
        # Get a fresh instance to ensure it's attached to the session
        user = db.session.merge(regular_user)
        
        tags = [
            Tag(
                name="Work",
                color="#ff5500",
                user_id=user.id
            ),
            Tag(
                name="Personal",
                color="#00ff55",
                user_id=user.id
            ),
            Tag(
                name="Urgent",
                color="#ff0000",
                user_id=user.id
            )
        ]
        
        db.session.add_all(tags)
        db.session.commit()
        
        # Store tag IDs
        tag_ids = [tag.id for tag in tags]
        
        # Clear the session
        db.session.close()
        
        # Return fresh instances
        fresh_tags = [db.session.get(Tag, tag_id) for tag_id in tag_ids]
        return fresh_tags

@pytest.fixture
def test_comments(app, regular_user, test_tasks):
    """Create test comments for a task."""
    with app.app_context():
        # Get fresh instances
        user = db.session.merge(regular_user)
        task = db.session.merge(test_tasks[0])
        
        comments = [
            Comment(
                content="This is a test comment 1",
                task_id=task.id,
                user_id=user.id
            ),
            Comment(
                content="This is a test comment 2",
                task_id=task.id,
                user_id=user.id
            )
        ]
        
        db.session.add_all(comments)
        db.session.commit()
        
        # Store comment IDs
        comment_ids = [comment.id for comment in comments]
        
        # Clear the session
        db.session.close()
        
        # Return fresh instances
        fresh_comments = [db.session.get(Comment, comment_id) for comment_id in comment_ids]
        return fresh_comments

@pytest.fixture
def json_content_headers():
    """Create JSON content headers."""
    return {
        "Content-Type": "application/json"
    }