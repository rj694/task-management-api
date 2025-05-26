import json
import pytest
from datetime import datetime, timedelta

def test_get_tasks(client, app, regular_user, test_tasks, auth_headers):
    """Test getting all tasks."""
    # Test successful retrieval
    response = client.get('/api/v1/tasks', headers=auth_headers)
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert 'tasks' in data
    assert len(data['tasks']) == 3
    assert data['total'] == 3
    assert data['page'] == 1
    assert data['per_page'] == 10
    
    # Test with pagination
    response = client.get('/api/v1/tasks?page=1&per_page=2', headers=auth_headers)
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert len(data['tasks']) == 2
    assert data['total'] == 3
    assert data['pages'] == 2
    assert data['page'] == 1
    assert data['per_page'] == 2
    
    # Test with status filter
    response = client.get('/api/v1/tasks?status=pending', headers=auth_headers)
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert len(data['tasks']) == 1
    assert data['tasks'][0]['status'] == 'pending'
    
    # Test with priority filter
    response = client.get('/api/v1/tasks?priority=high', headers=auth_headers)
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert len(data['tasks']) == 1
    assert data['tasks'][0]['priority'] == 'high'
    
    # Test with search
    response = client.get('/api/v1/tasks?search=Test Task 1', headers=auth_headers)
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert len(data['tasks']) == 1
    assert 'Test Task 1' in data['tasks'][0]['title']
    
    # Test with sorting
    response = client.get('/api/v1/tasks?sort_by=title&sort_order=asc', headers=auth_headers)
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert len(data['tasks']) == 3
    assert data['tasks'][0]['title'] < data['tasks'][1]['title']
    assert data['tasks'][1]['title'] < data['tasks'][2]['title']
    
    # Test without authentication
    response = client.get('/api/v1/tasks')
    
    assert response.status_code == 401
    assert json.loads(response.data)['error'] == 'Authorization required'

def test_get_task(client, app, regular_user, test_tasks, auth_headers):
    """Test getting a specific task."""
    # Get task ID safely
    with app.app_context():
        from app import db
        task = db.session.merge(test_tasks[0])
        task_id = task.id
        expected_title = task.title
        expected_description = task.description
        expected_status = task.status
        expected_priority = task.priority
    
    # Test successful retrieval
    response = client.get(f'/api/v1/tasks/{task_id}', headers=auth_headers)
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['id'] == task_id
    assert data['title'] == expected_title
    assert data['description'] == expected_description
    assert data['status'] == expected_status
    assert data['priority'] == expected_priority
    
    # Test non-existent task
    response = client.get(f'/api/v1/tasks/9999', headers=auth_headers)
    
    assert response.status_code == 404
    assert json.loads(response.data)['error'] == 'Task not found'
    
    # Test without authentication
    response = client.get(f'/api/v1/tasks/{task_id}')
    
    assert response.status_code == 401
    assert json.loads(response.data)['error'] == 'Authorization required'

def test_create_task(client, app, regular_user, auth_headers, json_content_headers):
    """Test creating a task."""
    # Get user ID safely
    with app.app_context():
        from app import db
        user = db.session.merge(regular_user)
        user_id = user.id
    
    combined_headers = {**auth_headers, **json_content_headers}
    
    # Test successful creation
    task_data = {
        'title': 'New Test Task',
        'description': 'Description for New Test Task',
        'status': 'pending',
        'priority': 'high',
        'due_date': (datetime.utcnow() + timedelta(days=1)).isoformat()
    }
    
    response = client.post(
        '/api/v1/tasks',
        data=json.dumps(task_data),
        headers=combined_headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 201
    assert data['message'] == 'Task created successfully'
    assert data['task']['title'] == task_data['title']
    assert data['task']['description'] == task_data['description']
    assert data['task']['status'] == task_data['status']
    assert data['task']['priority'] == task_data['priority']
    
    # Verify in database
    with app.app_context():
        from app.models.task import Task
        task = Task.query.filter_by(title='New Test Task').first()
        assert task is not None
        assert task.title == task_data['title']
        assert task.description == task_data['description']
        assert task.status == task_data['status']
        assert task.priority == task_data['priority']
        assert task.user_id == user_id
    
    # Test with minimum required fields
    minimal_task_data = {
        'title': 'Minimal Task'
    }
    
    response = client.post(
        '/api/v1/tasks',
        data=json.dumps(minimal_task_data),
        headers=combined_headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 201
    assert data['task']['title'] == minimal_task_data['title']
    assert data['task']['status'] == 'pending'  # Default value
    assert data['task']['priority'] == 'medium'  # Default value
    
    # Test validation errors
    invalid_task_data = {
        'title': '',  # Empty title
        'status': 'invalid_status',  # Invalid status
        'priority': 'invalid_priority',  # Invalid priority
        'due_date': 'invalid_date'  # Invalid date format
    }
    
    response = client.post(
        '/api/v1/tasks',
        data=json.dumps(invalid_task_data),
        headers=combined_headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 400
    assert 'error' in data
    assert 'messages' in data
    assert 'title' in data['messages']
    assert 'status' in data['messages']
    assert 'priority' in data['messages']
    assert 'due_date' in data['messages']
    
    # Test without authentication
    response = client.post(
        '/api/v1/tasks',
        data=json.dumps(task_data),
        headers=json_content_headers
    )
    
    assert response.status_code == 401
    assert json.loads(response.data)['error'] == 'Authorization required'

def test_update_task(client, app, regular_user, test_tasks, auth_headers, json_content_headers):
    """Test updating a task."""
    # Get task ID safely
    with app.app_context():
        from app import db
        task = db.session.merge(test_tasks[0])
        task_id = task.id
    
    combined_headers = {**auth_headers, **json_content_headers}
    
    # Test successful update
    update_data = {
        'title': 'Updated Test Task',
        'description': 'Updated Description',
        'status': 'in_progress',
        'priority': 'low'
    }
    
    response = client.put(
        f'/api/v1/tasks/{task_id}',
        data=json.dumps(update_data),
        headers=combined_headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['message'] == 'Task updated successfully'
    assert data['task']['title'] == update_data['title']
    assert data['task']['description'] == update_data['description']
    assert data['task']['status'] == update_data['status']
    assert data['task']['priority'] == update_data['priority']
    
    # Verify in database
    with app.app_context():
        from app.models.task import Task
        task = Task.query.get(task_id)
        assert task.title == update_data['title']
        assert task.description == update_data['description']
        assert task.status == update_data['status']
        assert task.priority == update_data['priority']
    
    # Test partial update
    partial_update = {
        'title': 'Partially Updated Task'
    }
    
    response = client.put(
        f'/api/v1/tasks/{task_id}',
        data=json.dumps(partial_update),
        headers=combined_headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['task']['title'] == partial_update['title']
    assert data['task']['description'] == update_data['description']  # Unchanged
    assert data['task']['status'] == update_data['status']  # Unchanged
    assert data['task']['priority'] == update_data['priority']  # Unchanged
    
    # Test non-existent task
    response = client.put(
        '/api/v1/tasks/9999',
        data=json.dumps(update_data),
        headers=combined_headers
    )
    
    assert response.status_code == 404
    assert json.loads(response.data)['error'] == 'Task not found'
    
    # Test validation errors
    invalid_update = {
        'status': 'invalid_status',
        'priority': 'invalid_priority'
    }
    
    response = client.put(
        f'/api/v1/tasks/{task_id}',
        data=json.dumps(invalid_update),
        headers=combined_headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 400
    assert 'error' in data
    assert 'messages' in data
    assert 'status' in data['messages']
    assert 'priority' in data['messages']
    
    # Test without authentication
    response = client.put(
        f'/api/v1/tasks/{task_id}',
        data=json.dumps(update_data),
        headers=json_content_headers
    )
    
    assert response.status_code == 401
    assert json.loads(response.data)['error'] == 'Authorization required'

def test_delete_task(client, app, regular_user, test_tasks, auth_headers):
    """Test deleting a task."""
    # Get task IDs safely
    with app.app_context():
        from app import db
        tasks = [db.session.merge(task) for task in test_tasks]
        task_id_1 = tasks[0].id
        task_id_2 = tasks[1].id
    
    # Test successful deletion
    response = client.delete(f'/api/v1/tasks/{task_id_1}', headers=auth_headers)
    
    assert response.status_code == 200
    assert json.loads(response.data)['message'] == 'Task deleted successfully'
    
    # Verify in database
    with app.app_context():
        from app.models.task import Task
        task = Task.query.get(task_id_1)
        assert task is None
    
    # Test non-existent task
    response = client.delete(f'/api/v1/tasks/9999', headers=auth_headers)
    
    assert response.status_code == 404
    assert json.loads(response.data)['error'] == 'Task not found'
    
    # Test without authentication
    response = client.delete(f'/api/v1/tasks/{task_id_2}')
    
    assert response.status_code == 401
    assert json.loads(response.data)['error'] == 'Authorization required'

def test_task_statistics(client, app, regular_user, test_tasks, auth_headers):
    """Test getting task statistics."""
    # Ensure test_tasks are attached to the session
    with app.app_context():
        from app import db
        # Just merge one task to ensure it's attached - we're not using its properties directly
        db.session.merge(test_tasks[0])
    
    # Test successful retrieval
    response = client.get('/api/v1/tasks/statistics', headers=auth_headers)
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert 'total_tasks' in data
    assert data['total_tasks'] == 3
    assert 'by_status' in data
    assert 'pending' in data['by_status']
    assert 'in_progress' in data['by_status']
    assert 'completed' in data['by_status']
    assert 'by_priority' in data
    assert 'high' in data['by_priority']
    assert 'medium' in data['by_priority']
    assert 'low' in data['by_priority']
    
    # Test without authentication
    response = client.get('/api/v1/tasks/statistics')
    
    assert response.status_code == 401
    assert json.loads(response.data)['error'] == 'Authorization required'

def test_bulk_actions(client, app, regular_user, test_tasks, auth_headers, json_content_headers):
    """Test bulk actions on tasks."""
    # Get task IDs safely
    with app.app_context():
        from app import db
        tasks = [db.session.merge(task) for task in test_tasks]
        task_ids = [task.id for task in tasks]
    
    combined_headers = {**auth_headers, **json_content_headers}
    
    # Test bulk update
    bulk_update_data = {
        'task_ids': task_ids,
        'updates': {
            'status': 'in_progress',
            'priority': 'high'
        }
    }
    
    response = client.put(
        '/api/v1/tasks/bulk/update',
        data=json.dumps(bulk_update_data),
        headers=combined_headers
    )
    
    assert response.status_code == 200
    assert json.loads(response.data)['message'] == f"{len(task_ids)} tasks updated successfully"
    
    # Verify in database
    with app.app_context():
        from app.models.task import Task
        for task_id in task_ids:
            task = Task.query.get(task_id)
            assert task.status == 'in_progress'
            assert task.priority == 'high'
    
    # Test bulk delete
    bulk_delete_data = {
        'task_ids': task_ids[:2]  # Delete first two tasks
    }
    
    response = client.post(
        '/api/v1/tasks/bulk/delete',
        data=json.dumps(bulk_delete_data),
        headers=combined_headers
    )
    
    assert response.status_code == 200
    assert json.loads(response.data)['message'] == f"{len(bulk_delete_data['task_ids'])} tasks deleted successfully"
    
    # Verify in database
    with app.app_context():
        from app.models.task import Task
        for task_id in bulk_delete_data['task_ids']:
            task = Task.query.get(task_id)
            assert task is None
        
        # The third task should still exist
        task = Task.query.get(task_ids[2])
        assert task is not None
    
    # Test validation errors
    invalid_bulk_update = {
        'task_ids': [],  # Empty list
        'updates': {
            'status': 'invalid_status'  # Invalid status
        }
    }
    
    response = client.put(
        '/api/v1/tasks/bulk/update',
        data=json.dumps(invalid_bulk_update),
        headers=combined_headers
    )
    
    assert response.status_code == 400
    assert 'error' in json.loads(response.data)