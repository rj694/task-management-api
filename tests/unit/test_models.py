from datetime import datetime, timedelta
from app.models.user import User
from app.models.task import Task
from app.models.tag import Tag
from app.models.comment import Comment
from app.models.token_blacklist import TokenBlacklist

def test_user_model(app):
    """Test User model."""
    with app.app_context():
        # Test user creation
        user = User(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.role == "user"  # Default role
        assert user.check_password("password123")
        assert not user.check_password("wrongpassword")
        
        # Test admin role
        admin = User(
            username="admin",
            email="admin@example.com",
            password="adminpass",
            role="admin"
        )
        
        assert admin.role == "admin"
        assert admin.is_admin()
        assert not user.is_admin()
        
        # Test to_dict method
        user_dict = user.to_dict()
        assert user_dict['username'] == "testuser"
        assert user_dict['email'] == "test@example.com"
        assert user_dict['role'] == "user"
        assert 'password_hash' not in user_dict  # Should not expose password hash

def test_task_model(app, regular_user):
    """Test Task model."""
    with app.app_context():
        # Ensure the user is attached to the current session
        from app import db
        user = db.session.merge(regular_user)
        
        # Test task creation
        task = Task(
            title="Test Task",
            description="This is a test task",
            status="pending",
            priority="high",
            due_date=datetime.utcnow() + timedelta(days=1),
            user_id=user.id
        )
        
        assert task.title == "Test Task"
        assert task.description == "This is a test task"
        assert task.status == "pending"
        assert task.priority == "high"
        assert task.user_id == user.id
        assert task.due_date is not None
        
        # Test default values
        simple_task = Task(
            title="Simple Task",
            user_id=user.id
        )
        
        assert simple_task.status == "pending"  # Default status
        assert simple_task.priority == "medium"  # Default priority
        assert simple_task.description is None
        assert simple_task.due_date is None
        
        # Test to_dict method
        task_dict = task.to_dict()
        assert task_dict['title'] == "Test Task"
        assert task_dict['description'] == "This is a test task"
        assert task_dict['status'] == "pending"
        assert task_dict['priority'] == "high"
        assert task_dict['user_id'] == user.id
        assert 'due_date' in task_dict
        assert 'created_at' in task_dict
        assert 'updated_at' in task_dict

def test_tag_model(app, regular_user):
    """Test Tag model."""
    with app.app_context():
        # Ensure the user is attached to the current session
        from app import db
        user = db.session.merge(regular_user)
        
        # Test tag creation
        tag = Tag(
            name="Work",
            color="#ff5500",
            user_id=user.id
        )
        
        assert tag.name == "Work"
        assert tag.color == "#ff5500"
        assert tag.user_id == user.id
        
        # Test default color
        simple_tag = Tag(
            name="Simple",
            user_id=user.id
        )
        
        assert simple_tag.color == "#3498db"  # Default color
        
        # Test to_dict method
        tag_dict = tag.to_dict()
        assert tag_dict['name'] == "Work"
        assert tag_dict['color'] == "#ff5500"
        assert tag_dict['user_id'] == user.id

def test_comment_model(app, regular_user, test_tasks):
    """Test Comment model."""
    with app.app_context():
        # Ensure objects are attached to the current session
        from app import db
        user = db.session.merge(regular_user)
        tasks = [db.session.merge(task) for task in test_tasks]
        
        # Test comment creation
        comment = Comment(
            content="This is a test comment",
            task_id=tasks[0].id,
            user_id=user.id
        )
        
        assert comment.content == "This is a test comment"
        assert comment.task_id == tasks[0].id
        assert comment.user_id == user.id
        
        # Test to_dict method
        comment_dict = comment.to_dict()
        assert comment_dict['content'] == "This is a test comment"
        assert comment_dict['task_id'] == tasks[0].id
        assert comment_dict['user_id'] == user.id
        assert 'created_at' in comment_dict
        assert 'updated_at' in comment_dict

def test_token_blacklist_model(app, regular_user):
    """Test TokenBlacklist model."""
    with app.app_context():
        # Ensure the user is attached to the current session
        from app import db
        user = db.session.merge(regular_user)
        
        # Test token blacklist creation
        expires_at = datetime.utcnow() + timedelta(hours=1)
        token_blacklist = TokenBlacklist(
            jti="test-jti-123",
            token_type="access",
            user_id=user.id,
            expires_at=expires_at
        )
        
        assert token_blacklist.jti == "test-jti-123"
        assert token_blacklist.token_type == "access"
        assert token_blacklist.user_id == user.id
        assert token_blacklist.expires_at == expires_at
        
        # Test is_token_revoked class method
        jwt_payload = {"jti": "test-jti-123"}
        
        # Token not in database yet
        assert not TokenBlacklist.is_token_revoked(jwt_payload)
        
        # Add token to database
        db.session.add(token_blacklist)
        db.session.commit()
        
        # Now token should be revoked
        assert TokenBlacklist.is_token_revoked(jwt_payload)

def test_relationships(app, regular_user, test_tasks, test_tags, test_comments):
    """Test model relationships."""
    with app.app_context():
        # Ensure all objects are attached to the current session
        from app import db
        user = db.session.merge(regular_user)
        tasks = [db.session.merge(task) for task in test_tasks]
        tags = [db.session.merge(tag) for tag in test_tags]
        comments = [db.session.merge(comment) for comment in test_comments]
        
        # Test User-Task relationship
        user = User.query.get(user.id)
        assert len(user.tasks) == 3
        assert user.tasks[0].title == tasks[0].title
        
        # Test User-Tag relationship
        assert len(user.tags) == 3
        assert user.tags[0].name == tags[0].name
        
        # Test User-Comment relationship
        assert len(user.comments) == 2
        assert user.comments[0].content == comments[0].content
        
        # Test Task-Comment relationship
        task = Task.query.get(tasks[0].id)
        assert len(task.comments) == 2
        assert task.comments[0].content == comments[0].content
        
        # Test Tag-Task relationship
        # First add a tag to a task
        task.tags.append(tags[0])
        db.session.commit()
        
        # Refresh tag from database
        tag = Tag.query.get(tags[0].id)
        
        # Check relationship
        assert task in tag.tasks
        assert tag in task.tags