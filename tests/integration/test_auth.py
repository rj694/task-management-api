import json
import pytest
from datetime import datetime, timedelta
from app.models.token_blacklist import TokenBlacklist

def test_register(client, json_content_headers):
    """Test user registration."""
    # Test successful registration
    response = client.post(
        '/api/v1/auth/register',
        data=json.dumps({
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'password123'
        }),
        headers=json_content_headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 201
    assert 'access_token' in data
    assert 'refresh_token' in data
    assert data['user']['username'] == 'newuser'
    assert data['user']['email'] == 'new@example.com'
    assert data['user']['role'] == 'user'  # Default role
    
    # Test duplicate username
    response = client.post(
        '/api/v1/auth/register',
        data=json.dumps({
            'username': 'newuser',
            'email': 'another@example.com',
            'password': 'password123'
        }),
        headers=json_content_headers
    )
    
    assert response.status_code == 409
    assert json.loads(response.data)['error'] == 'User with this username already exists'
    
    # Test duplicate email
    response = client.post(
        '/api/v1/auth/register',
        data=json.dumps({
            'username': 'anotheruser',
            'email': 'new@example.com',
            'password': 'password123'
        }),
        headers=json_content_headers
    )
    
    assert response.status_code == 409
    assert json.loads(response.data)['error'] == 'User with this email already exists'
    
    # Test validation errors
    response = client.post(
        '/api/v1/auth/register',
        data=json.dumps({
            'username': 'ab',  # Too short
            'email': 'invalid-email',  # Invalid email
            'password': '123'  # Too short
        }),
        headers=json_content_headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 400
    assert 'error' in data
    assert 'messages' in data
    assert 'username' in data['messages']
    assert 'email' in data['messages']
    assert 'password' in data['messages']

def test_login(client, app, regular_user, json_content_headers):
    """Test user login."""
    # Ensure we have the user's expected properties
    with app.app_context():
        from app import db
        user = db.session.merge(regular_user)
        expected_username = user.username
        expected_email = user.email
    
    # Test successful login
    response = client.post(
        '/api/v1/auth/login',
        data=json.dumps({
            'email': 'test@example.com',
            'password': 'password123'
        }),
        headers=json_content_headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert 'access_token' in data
    assert 'refresh_token' in data
    assert data['user']['username'] == expected_username
    assert data['user']['email'] == expected_email
    
    # Test invalid credentials
    response = client.post(
        '/api/v1/auth/login',
        data=json.dumps({
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }),
        headers=json_content_headers
    )
    
    assert response.status_code == 401
    assert json.loads(response.data)['error'] == 'Invalid credentials'
    
    # Test non-existent user
    response = client.post(
        '/api/v1/auth/login',
        data=json.dumps({
            'email': 'nonexistent@example.com',
            'password': 'password123'
        }),
        headers=json_content_headers
    )
    
    assert response.status_code == 401
    assert json.loads(response.data)['error'] == 'Invalid credentials'

def test_refresh_token(client, auth_tokens, json_content_headers):
    """Test token refresh."""
    # Test successful token refresh
    refresh_headers = {
        **json_content_headers,
        'Authorization': f"Bearer {auth_tokens['refresh_token']}"
    }
    
    response = client.post('/api/v1/auth/refresh', headers=refresh_headers)
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert 'access_token' in data
    
    # Test with access token (should fail)
    invalid_headers = {
        **json_content_headers,
        'Authorization': f"Bearer {auth_tokens['access_token']}"
    }
    
    response = client.post('/api/v1/auth/refresh', headers=invalid_headers)
    
    # Updated expectation - Flask-JWT-Extended returns 401 for wrong token type, not 422
    assert response.status_code == 401
    assert json.loads(response.data)['error'] in ['Token has expired', 'Invalid token']

def test_logout(client, app, auth_headers, json_content_headers):
    """Test user logout."""
    combined_headers = {**auth_headers, **json_content_headers}
    
    # Test successful logout
    response = client.post('/api/v1/auth/logout', headers=combined_headers)
    
    assert response.status_code == 200
    assert json.loads(response.data)['message'] == 'Successfully logged out'
    
    # Check if token was blacklisted
    with app.app_context():
        from app.models.token_blacklist import TokenBlacklist
        blacklisted = TokenBlacklist.query.count()
        assert blacklisted == 1
    
    # Test accessing protected endpoint after logout
    response = client.get('/api/v1/auth/me', headers=combined_headers)
    
    assert response.status_code == 401
    assert json.loads(response.data)['error'] == 'Token has been revoked'

def test_logout_all(client, app, auth_headers, json_content_headers):
    """Test logout from all devices."""
    combined_headers = {**auth_headers, **json_content_headers}
    
    # Test successful logout from all devices
    response = client.post('/api/v1/auth/logout/all', headers=combined_headers)
    
    assert response.status_code == 200
    assert json.loads(response.data)['message'] == 'Successfully logged out from all devices'
    
    # Check if token was blacklisted
    with app.app_context():
        from app.models.token_blacklist import TokenBlacklist
        blacklisted = TokenBlacklist.query.count()
        assert blacklisted == 1
    
    # Test accessing protected endpoint after logout
    response = client.get('/api/v1/auth/me', headers=combined_headers)
    
    assert response.status_code == 401
    assert json.loads(response.data)['error'] == 'Token has been revoked'

def test_me(client, app, regular_user, auth_headers):
    """Test getting current user details."""
    # Ensure we have the user's expected properties
    with app.app_context():
        from app import db
        user = db.session.merge(regular_user)
        expected_username = user.username
        expected_email = user.email
        expected_role = user.role
    
    # Test successful retrieval
    response = client.get('/api/v1/auth/me', headers=auth_headers)
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['username'] == expected_username
    assert data['email'] == expected_email
    assert data['role'] == expected_role
    
    # Test without authentication
    response = client.get('/api/v1/auth/me')
    
    assert response.status_code == 401
    assert json.loads(response.data)['error'] == 'Authorization required'

def test_update_me(client, app, regular_user, auth_headers, json_content_headers):
    """Test updating current user details."""
    # Get the user ID in a safe way
    with app.app_context():
        from app import db
        user = db.session.merge(regular_user)
        user_id = user.id
    
    combined_headers = {**auth_headers, **json_content_headers}
    
    # Test updating username
    response = client.put(
        '/api/v1/auth/me',
        data=json.dumps({
            'username': 'updateduser'
        }),
        headers=combined_headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['message'] == 'User updated successfully'
    assert data['user']['username'] == 'updateduser'
    
    # Verify in database
    with app.app_context():
        from app.models.user import User
        user = User.query.get(user_id)
        assert user.username == 'updateduser'
    
    # Test updating email
    response = client.put(
        '/api/v1/auth/me',
        data=json.dumps({
            'email': 'updated@example.com'
        }),
        headers=combined_headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['message'] == 'User updated successfully'
    assert data['user']['email'] == 'updated@example.com'
    
    # Test updating password
    response = client.put(
        '/api/v1/auth/me',
        data=json.dumps({
            'password': 'newpassword123'
        }),
        headers=combined_headers
    )
    
    assert response.status_code == 200
    assert json.loads(response.data)['message'] == 'User updated successfully'
    
    # Verify password was updated
    with app.app_context():
        from app.models.user import User
        user = User.query.get(user_id)
        assert user.check_password('newpassword123')
        assert not user.check_password('password123')
    
    # Test unique constraint violations
    # First create another user
    client.post(
        '/api/v1/auth/register',
        data=json.dumps({
            'username': 'anotheruser',
            'email': 'another@example.com',
            'password': 'password123'
        }),
        headers=json_content_headers
    )
    
    # Try to update to existing username
    response = client.put(
        '/api/v1/auth/me',
        data=json.dumps({
            'username': 'anotheruser'
        }),
        headers=combined_headers
    )
    
    assert response.status_code == 409
    assert json.loads(response.data)['error'] == 'Username already taken'
    
    # Try to update to existing email
    response = client.put(
        '/api/v1/auth/me',
        data=json.dumps({
            'email': 'another@example.com'
        }),
        headers=combined_headers
    )
    
    assert response.status_code == 409
    assert json.loads(response.data)['error'] == 'Email already taken'