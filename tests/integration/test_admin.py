import json
import pytest

def test_get_users(client, app, regular_user, admin_user, admin_auth_headers, auth_headers):
    """Test getting all users (admin only)."""
    # Ensure objects are attached to session and store IDs
    with app.app_context():
        from app import db
        regular = db.session.merge(regular_user)
        admin = db.session.merge(admin_user)
        regular_id = regular.id
        admin_id = admin.id
    
    # Test successful retrieval as admin
    response = client.get('/api/v1/admin/users', headers=admin_auth_headers)
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert 'users' in data
    assert len(data['users']) >= 2  # At least regular_user and admin_user
    
    user_ids = [user['id'] for user in data['users']]
    assert regular_id in user_ids
    assert admin_id in user_ids
    
    # Test with pagination
    response = client.get('/api/v1/admin/users?page=1&per_page=1', headers=admin_auth_headers)
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert len(data['users']) == 1
    assert data['page'] == 1
    assert data['per_page'] == 1
    
    # Test access denied for regular user
    response = client.get('/api/v1/admin/users', headers=auth_headers)
    
    assert response.status_code == 403
    assert json.loads(response.data)['error'] == 'Admin privileges required'
    
    # Test without authentication
    response = client.get('/api/v1/admin/users')
    
    assert response.status_code == 401
    assert json.loads(response.data)['error'] == 'Authorization required'

def test_get_user(client, app, regular_user, admin_user, admin_auth_headers, auth_headers):
    """Test getting a specific user (admin only)."""
    # Ensure objects are attached to session and store expected values
    with app.app_context():
        from app import db
        regular = db.session.merge(regular_user)
        
        regular_id = regular.id
        expected_username = regular.username
        expected_email = regular.email
        expected_role = regular.role
    
    # Test successful retrieval as admin
    response = client.get(f'/api/v1/admin/users/{regular_id}', headers=admin_auth_headers)
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['id'] == regular_id
    assert data['username'] == expected_username
    assert data['email'] == expected_email
    assert data['role'] == expected_role
    
    # Test non-existent user
    response = client.get('/api/v1/admin/users/9999', headers=admin_auth_headers)
    
    assert response.status_code == 404
    assert json.loads(response.data)['error'] == 'User not found'
    
    # Test access denied for regular user
    response = client.get(f'/api/v1/admin/users/{regular_id}', headers=auth_headers)
    
    assert response.status_code == 403
    assert json.loads(response.data)['error'] == 'Admin privileges required'
    
    # Test without authentication
    response = client.get(f'/api/v1/admin/users/{regular_id}')
    
    assert response.status_code == 401
    assert json.loads(response.data)['error'] == 'Authorization required'

def test_update_user(client, app, regular_user, admin_user, admin_auth_headers, auth_headers, json_content_headers):
    """Test updating a user (admin only)."""
    # Ensure objects are attached to session and store IDs
    with app.app_context():
        from app import db
        regular = db.session.merge(regular_user)
        regular_id = regular.id
    
    combined_admin_headers = {**admin_auth_headers, **json_content_headers}
    combined_regular_headers = {**auth_headers, **json_content_headers}
    
    # Test successful update as admin
    update_data = {
        'username': 'updated_user',
        'email': 'updated@example.com',
        'role': 'admin'  # Change role to admin
    }
    
    response = client.put(
        f'/api/v1/admin/users/{regular_id}',
        data=json.dumps(update_data),
        headers=combined_admin_headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['message'] == 'User updated successfully'
    assert data['user']['username'] == update_data['username']
    assert data['user']['email'] == update_data['email']
    assert data['user']['role'] == update_data['role']
    
    # Verify in database
    with app.app_context():
        from app.models.user import User
        user = User.query.get(regular_id)
        assert user.username == update_data['username']
        assert user.email == update_data['email']
        assert user.role == update_data['role']
    
    # Test partial update
    partial_update = {
        'username': 'partially_updated_user'
    }
    
    response = client.put(
        f'/api/v1/admin/users/{regular_id}',
        data=json.dumps(partial_update),
        headers=combined_admin_headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['user']['username'] == partial_update['username']
    assert data['user']['email'] == update_data['email']  # Unchanged
    assert data['user']['role'] == update_data['role']  # Unchanged
    
    # Test non-existent user
    response = client.put(
        '/api/v1/admin/users/9999',
        data=json.dumps(update_data),
        headers=combined_admin_headers
    )
    
    assert response.status_code == 404
    assert json.loads(response.data)['error'] == 'User not found'
    
    # Test access denied for regular user
    response = client.put(
        f'/api/v1/admin/users/{regular_id}',
        data=json.dumps(update_data),
        headers=combined_regular_headers
    )
    
    assert response.status_code == 403
    assert json.loads(response.data)['error'] == 'Admin privileges required'
    
    # Test without authentication
    response = client.put(
        f'/api/v1/admin/users/{regular_id}',
        data=json.dumps(update_data),
        headers=json_content_headers
    )
    
    assert response.status_code == 401
    assert json.loads(response.data)['error'] == 'Authorization required'

def test_delete_user(client, app, regular_user, admin_user, admin_auth_headers, auth_headers):
    """Test deleting a user (admin only)."""
    # Ensure objects are attached to session and store IDs
    with app.app_context():
        from app import db
        admin = db.session.merge(admin_user)
        admin_id = admin.id
    
    # Create a user to delete
    response = client.post(
        '/api/v1/auth/register',
        data=json.dumps({
            'username': 'user_to_delete',
            'email': 'delete@example.com',
            'password': 'password123'
        }),
        headers={'Content-Type': 'application/json'}
    )
    
    register_data = json.loads(response.data)
    user_id = register_data['user']['id']
    
    # Test successful deletion as admin
    response = client.delete(f'/api/v1/admin/users/{user_id}', headers=admin_auth_headers)
    
    assert response.status_code == 200
    assert json.loads(response.data)['message'] == 'User deleted successfully'
    
    # Verify in database
    with app.app_context():
        from app.models.user import User
        user = User.query.get(user_id)
        assert user is None
    
    # Test non-existent user
    response = client.delete('/api/v1/admin/users/9999', headers=admin_auth_headers)
    
    assert response.status_code == 404
    assert json.loads(response.data)['error'] == 'User not found'
    
    # Test access denied for regular user
    response = client.delete(f'/api/v1/admin/users/{admin_id}', headers=auth_headers)
    
    assert response.status_code == 403
    assert json.loads(response.data)['error'] == 'Admin privileges required'
    
    # Test without authentication
    response = client.delete(f'/api/v1/admin/users/{admin_id}')
    
    assert response.status_code == 401
    assert json.loads(response.data)['error'] == 'Authorization required'

def test_admin_stats(client, app, regular_user, admin_user, test_tasks, admin_auth_headers, auth_headers):
    """Test getting admin statistics (admin only)."""
    # Ensure objects are attached to session
    with app.app_context():
        from app import db
        # Just merge one object to ensure it's attached
        db.session.merge(regular_user)
        db.session.merge(test_tasks[0])
    
    # Test successful retrieval as admin
    response = client.get('/api/v1/admin/stats', headers=admin_auth_headers)
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert 'user_stats' in data
    assert 'task_stats' in data
    assert data['user_stats']['total'] >= 2  # At least regular_user and admin_user
    assert 'admins' in data['user_stats']
    assert 'regular_users' in data['user_stats']
    assert data['task_stats']['total'] >= 3  # At least the 3 test tasks
    assert 'by_status' in data['task_stats']
    
    # Test access denied for regular user
    response = client.get('/api/v1/admin/stats', headers=auth_headers)
    
    assert response.status_code == 403
    assert json.loads(response.data)['error'] == 'Admin privileges required'
    
    # Test without authentication
    response = client.get('/api/v1/admin/stats')
    
    assert response.status_code == 401
    assert json.loads(response.data)['error'] == 'Authorization required'