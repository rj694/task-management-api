import json
import pytest

def test_get_tags(client, app, regular_user, test_tags, auth_headers):
    """Test getting all tags."""
    # Ensure objects are attached to session and store expected values
    with app.app_context():
        from app import db
        user = db.session.merge(regular_user)
        tags = [db.session.merge(tag) for tag in test_tags]
        expected_user_id = user.id
        expected_tag_name = tags[0].name
        expected_tag_color = tags[0].color
    
    # Test successful retrieval
    response = client.get('/api/v1/tags', headers=auth_headers)
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert len(data) == 3
    assert data[0]['name'] == expected_tag_name
    assert data[0]['color'] == expected_tag_color
    assert data[0]['user_id'] == expected_user_id
    
    # Test without authentication
    response = client.get('/api/v1/tags')
    
    assert response.status_code == 401
    assert json.loads(response.data)['error'] == 'Authorization required'

def test_get_tag(client, app, regular_user, test_tags, auth_headers):
    """Test getting a specific tag."""
    # Ensure objects are attached to session and store expected values
    with app.app_context():
        from app import db
        user = db.session.merge(regular_user)
        tag = db.session.merge(test_tags[0])
        tag_id = tag.id
        expected_name = tag.name
        expected_color = tag.color
        expected_user_id = user.id
    
    # Test successful retrieval
    response = client.get(f'/api/v1/tags/{tag_id}', headers=auth_headers)
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['id'] == tag_id
    assert data['name'] == expected_name
    assert data['color'] == expected_color
    assert data['user_id'] == expected_user_id
    
    # Test non-existent tag
    response = client.get('/api/v1/tags/9999', headers=auth_headers)
    
    assert response.status_code == 404
    assert json.loads(response.data)['error'] == 'Tag not found'
    
    # Test without authentication
    response = client.get(f'/api/v1/tags/{tag_id}')
    
    assert response.status_code == 401
    assert json.loads(response.data)['error'] == 'Authorization required'

def test_create_tag(client, app, regular_user, auth_headers, json_content_headers):
    """Test creating a tag."""
    # Ensure user is attached to session and store ID
    with app.app_context():
        from app import db
        user = db.session.merge(regular_user)
        user_id = user.id
    
    combined_headers = {**auth_headers, **json_content_headers}
    
    # Test successful creation
    tag_data = {
        'name': 'New Tag',
        'color': '#ff00ff'
    }
    
    response = client.post(
        '/api/v1/tags',
        data=json.dumps(tag_data),
        headers=combined_headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 201
    assert data['message'] == 'Tag created successfully'
    assert data['tag']['name'] == tag_data['name']
    assert data['tag']['color'] == tag_data['color']
    assert data['tag']['user_id'] == user_id
    
    # Verify in database
    with app.app_context():
        from app.models.tag import Tag
        tag = Tag.query.filter_by(name='New Tag').first()
        assert tag is not None
        assert tag.name == tag_data['name']
        assert tag.color == tag_data['color']
        assert tag.user_id == user_id
    
    # Test with default color
    minimal_tag_data = {
        'name': 'Minimal Tag'
    }
    
    response = client.post(
        '/api/v1/tags',
        data=json.dumps(minimal_tag_data),
        headers=combined_headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 201
    assert data['tag']['name'] == minimal_tag_data['name']
    assert data['tag']['color'] == '#3498db'  # Default color
    
    # Test duplicate tag name
    duplicate_tag_data = {
        'name': 'New Tag'  # Same as first tag
    }
    
    response = client.post(
        '/api/v1/tags',
        data=json.dumps(duplicate_tag_data),
        headers=combined_headers
    )
    
    assert response.status_code == 409
    assert json.loads(response.data)['error'] == 'Tag with this name already exists'
    
    # Test validation errors
    invalid_tag_data = {
        'name': '',  # Empty name
        'color': 'invalid-color'  # Invalid color format
    }
    
    response = client.post(
        '/api/v1/tags',
        data=json.dumps(invalid_tag_data),
        headers=combined_headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 400
    assert 'error' in data
    assert 'messages' in data
    assert 'name' in data['messages']
    assert 'color' in data['messages']
    
    # Test without authentication
    response = client.post(
        '/api/v1/tags',
        data=json.dumps(tag_data),
        headers=json_content_headers
    )
    
    assert response.status_code == 401
    assert json.loads(response.data)['error'] == 'Authorization required'

def test_update_tag(client, app, regular_user, test_tags, auth_headers, json_content_headers):
    """Test updating a tag."""
    # Ensure objects are attached to session and store expected values
    with app.app_context():
        from app import db
        tags = [db.session.merge(tag) for tag in test_tags]
        tag_id = tags[0].id
        other_tag_name = tags[1].name
    
    combined_headers = {**auth_headers, **json_content_headers}
    
    # Test successful update
    update_data = {
        'name': 'Updated Tag',
        'color': '#00ffff'
    }
    
    response = client.put(
        f'/api/v1/tags/{tag_id}',
        data=json.dumps(update_data),
        headers=combined_headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['message'] == 'Tag updated successfully'
    assert data['tag']['name'] == update_data['name']
    assert data['tag']['color'] == update_data['color']
    
    # Verify in database
    with app.app_context():
        from app.models.tag import Tag
        tag = Tag.query.get(tag_id)
        assert tag.name == update_data['name']
        assert tag.color == update_data['color']
    
    # Test partial update
    partial_update = {
        'color': '#ffff00'
    }
    
    response = client.put(
        f'/api/v1/tags/{tag_id}',
        data=json.dumps(partial_update),
        headers=combined_headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['tag']['name'] == update_data['name']  # Unchanged
    assert data['tag']['color'] == partial_update['color']
    
    # Test conflict with existing tag name
    conflict_update = {
        'name': other_tag_name  # Name of another tag
    }
    
    response = client.put(
        f'/api/v1/tags/{tag_id}',
        data=json.dumps(conflict_update),
        headers=combined_headers
    )
    
    assert response.status_code == 409
    assert json.loads(response.data)['error'] == 'Tag with this name already exists'
    
    # Test non-existent tag
    response = client.put(
        '/api/v1/tags/9999',
        data=json.dumps(update_data),
        headers=combined_headers
    )
    
    assert response.status_code == 404
    assert json.loads(response.data)['error'] == 'Tag not found'
    
    # Test without authentication
    response = client.put(
        f'/api/v1/tags/{tag_id}',
        data=json.dumps(update_data),
        headers=json_content_headers
    )
    
    assert response.status_code == 401
    assert json.loads(response.data)['error'] == 'Authorization required'

def test_delete_tag(client, app, regular_user, test_tags, auth_headers):
    """Test deleting a tag."""
    # Ensure tags are attached to session and store IDs
    with app.app_context():
        from app import db
        tags = [db.session.merge(tag) for tag in test_tags]
        tag_id_1 = tags[0].id
        tag_id_2 = tags[1].id
    
    # Test successful deletion
    response = client.delete(f'/api/v1/tags/{tag_id_1}', headers=auth_headers)
    
    assert response.status_code == 200
    assert json.loads(response.data)['message'] == 'Tag deleted successfully'
    
    # Verify in database
    with app.app_context():
        from app.models.tag import Tag
        tag = Tag.query.get(tag_id_1)
        assert tag is None
    
    # Test non-existent tag
    response = client.delete('/api/v1/tags/9999', headers=auth_headers)
    
    assert response.status_code == 404
    assert json.loads(response.data)['error'] == 'Tag not found'
    
    # Test without authentication
    response = client.delete(f'/api/v1/tags/{tag_id_2}')
    
    assert response.status_code == 401
    assert json.loads(response.data)['error'] == 'Authorization required'

def test_task_tag_relationships(client, app, regular_user, test_tasks, test_tags, auth_headers, json_content_headers):
    """Test tag-task relationships."""
    # Ensure objects are attached to session and store IDs
    with app.app_context():
        from app import db
        tasks = [db.session.merge(task) for task in test_tasks]
        tags = [db.session.merge(tag) for tag in test_tags]
        task_id = tasks[0].id
        tag_id = tags[0].id
    
    combined_headers = {**auth_headers, **json_content_headers}
    
    # Test adding tag to task
    tag_data = {
        'tag_id': tag_id
    }
    
    response = client.post(
        f'/api/v1/tasks/{task_id}/tags',
        data=json.dumps(tag_data),
        headers=combined_headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['message'] == 'Tag added to task successfully'
    assert len(data['task']['tags']) == 1
    assert data['task']['tags'][0]['id'] == tag_id
    
    # Verify in database
    with app.app_context():
        from app.models.task import Task
        from app.models.tag import Tag
        task = Task.query.get(task_id)
        tag = Tag.query.get(tag_id)
        assert tag in task.tags
    
    # Test filtering tasks by tag
    response = client.get(f'/api/v1/tasks?tag={tag_id}', headers=auth_headers)
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert len(data['tasks']) == 1
    assert data['tasks'][0]['id'] == task_id
    
    # Test removing tag from task
    response = client.delete(
        f'/api/v1/tasks/{task_id}/tags/{tag_id}',
        headers=auth_headers
    )
    
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['message'] == 'Tag removed from task successfully'
    assert len(data['task']['tags']) == 0
    
    # Verify in database
    with app.app_context():
        from app.models.task import Task
        from app.models.tag import Tag
        task = Task.query.get(task_id)
        tag = Tag.query.get(tag_id)
        assert tag not in task.tags