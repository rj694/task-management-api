import json
import pytest

def test_get_task_comments(client, app, regular_user, test_tasks, test_comments, auth_headers):
    """Test getting all comments for a task."""
    # Ensure objects are attached to session and store expected values
    with app.app_context():
        from app import db
        user = db.session.merge(regular_user)
        task = db.session.merge(test_tasks[0])
        comment = db.session.merge(test_comments[0])
        
        task_id = task.id
        expected_user_id = user.id
        expected_content = comment.content
    
    # Test successful retrieval
    response = client.get(f'/api/v1/tasks/{task_id}/comments', headers=auth_headers)
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert len(data) == 2
    assert data[0]['content'] == expected_content
    assert data[0]['task_id'] == task_id
    assert data[0]['user_id'] == expected_user_id
    
    # Test non-existent task
    response = client.get('/api/v1/tasks/9999/comments', headers=auth_headers)
    
    assert response.status_code == 404
    assert json.loads(response.data)['error'] == 'Task not found'
    
    # Test without authentication
    response = client.get(f'/api/v1/tasks/{task_id}/comments')
    
    assert response.status_code == 401
    assert json.loads(response.data)['error'] == 'Authorization required'

def test_create_comment(client, app, regular_user, test_tasks, auth_headers, json_content_headers):
    """Test creating a comment for a task."""
    # Ensure objects are attached to session and store IDs
    with app.app_context():
        from app import db
        user = db.session.merge(regular_user)
        task = db.session.merge(test_tasks[0])
        
        user_id = user.id
        task_id = task.id
    
    combined_headers = {**auth_headers, **json_content_headers}
    
    # Test successful creation
    comment_data = {
        'content': 'This is a new comment'
    }
    
    response = client.post(
        f'/api/v1/tasks/{task_id}/comments',
        data=json.dumps(comment_data),
        headers=combined_headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 201
    assert data['message'] == 'Comment created successfully'
    assert data['comment']['content'] == comment_data['content']
    assert data['comment']['task_id'] == task_id
    assert data['comment']['user_id'] == user_id
    
    # Verify in database
    with app.app_context():
        from app.models.comment import Comment
        comment = Comment.query.filter_by(content='This is a new comment').first()
        assert comment is not None
        assert comment.content == comment_data['content']
        assert comment.task_id == task_id
        assert comment.user_id == user_id
    
    # Test non-existent task
    response = client.post(
        '/api/v1/tasks/9999/comments',
        data=json.dumps(comment_data),
        headers=combined_headers
    )
    
    assert response.status_code == 404
    assert json.loads(response.data)['error'] == 'Task not found'
    
    # Test validation errors
    invalid_comment_data = {
        'content': ''  # Empty content
    }
    
    response = client.post(
        f'/api/v1/tasks/{task_id}/comments',
        data=json.dumps(invalid_comment_data),
        headers=combined_headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 400
    assert 'error' in data
    assert 'messages' in data
    assert 'content' in data['messages']
    
    # Test without authentication
    response = client.post(
        f'/api/v1/tasks/{task_id}/comments',
        data=json.dumps(comment_data),
        headers=json_content_headers
    )
    
    assert response.status_code == 401
    assert json.loads(response.data)['error'] == 'Authorization required'

def test_get_comment(client, app, regular_user, test_tasks, test_comments, auth_headers):
    """Test getting a specific comment."""
    # Ensure objects are attached to session and store expected values
    with app.app_context():
        from app import db
        user = db.session.merge(regular_user)
        task = db.session.merge(test_tasks[0])
        comment = db.session.merge(test_comments[0])
        
        comment_id = comment.id
        expected_content = comment.content
        expected_task_id = task.id
        expected_user_id = user.id
    
    # Test successful retrieval
    response = client.get(f'/api/v1/comments/{comment_id}', headers=auth_headers)
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['id'] == comment_id
    assert data['content'] == expected_content
    assert data['task_id'] == expected_task_id
    assert data['user_id'] == expected_user_id
    
    # Test non-existent comment
    response = client.get('/api/v1/comments/9999', headers=auth_headers)
    
    assert response.status_code == 404
    assert json.loads(response.data)['error'] == 'Comment not found'
    
    # Test without authentication
    response = client.get(f'/api/v1/comments/{comment_id}')
    
    assert response.status_code == 401
    assert json.loads(response.data)['error'] == 'Authorization required'

def test_update_comment(client, app, regular_user, test_comments, auth_headers, json_content_headers):
    """Test updating a comment."""
    # Ensure objects are attached to session and store IDs
    with app.app_context():
        from app import db
        comment = db.session.merge(test_comments[0])
        comment_id = comment.id
    
    combined_headers = {**auth_headers, **json_content_headers}
    
    # Test successful update
    update_data = {
        'content': 'Updated comment content'
    }
    
    response = client.put(
        f'/api/v1/comments/{comment_id}',
        data=json.dumps(update_data),
        headers=combined_headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['message'] == 'Comment updated successfully'
    assert data['comment']['content'] == update_data['content']
    
    # Verify in database
    with app.app_context():
        from app.models.comment import Comment
        comment = Comment.query.get(comment_id)
        assert comment.content == update_data['content']
    
    # Test non-existent comment
    response = client.put(
        '/api/v1/comments/9999',
        data=json.dumps(update_data),
        headers=combined_headers
    )
    
    assert response.status_code == 404
    assert json.loads(response.data)['error'] == 'Comment not found'
    
    # Test validation errors
    invalid_update_data = {
        'content': ''  # Empty content
    }
    
    response = client.put(
        f'/api/v1/comments/{comment_id}',
        data=json.dumps(invalid_update_data),
        headers=combined_headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 400
    assert 'error' in data
    assert 'messages' in data
    assert 'content' in data['messages']
    
    # Test without authentication
    response = client.put(
        f'/api/v1/comments/{comment_id}',
        data=json.dumps(update_data),
        headers=json_content_headers
    )
    
    assert response.status_code == 401
    assert json.loads(response.data)['error'] == 'Authorization required'

def test_delete_comment(client, app, regular_user, test_comments, auth_headers):
    """Test deleting a comment."""
    # Ensure objects are attached to session and store IDs
    with app.app_context():
        from app import db
        comments = [db.session.merge(comment) for comment in test_comments]
        comment_id_1 = comments[0].id
        comment_id_2 = comments[1].id
    
    # Test successful deletion
    response = client.delete(f'/api/v1/comments/{comment_id_1}', headers=auth_headers)
    
    assert response.status_code == 200
    assert json.loads(response.data)['message'] == 'Comment deleted successfully'
    
    # Verify in database
    with app.app_context():
        from app.models.comment import Comment
        comment = Comment.query.get(comment_id_1)
        assert comment is None
    
    # Test non-existent comment
    response = client.delete('/api/v1/comments/9999', headers=auth_headers)
    
    assert response.status_code == 404
    assert json.loads(response.data)['error'] == 'Comment not found'
    
    # Test without authentication
    response = client.delete(f'/api/v1/comments/{comment_id_2}')
    
    assert response.status_code == 401
    assert json.loads(response.data)['error'] == 'Authorization required'