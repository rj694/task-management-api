import json
import pytest
import csv
from io import StringIO

def test_export_tasks_json(client, app, regular_user, test_tasks, auth_headers):
    """Test exporting tasks as JSON."""
    # Ensure objects are attached to session and store expected values
    with app.app_context():
        from app import db
        tasks = [db.session.merge(task) for task in test_tasks]
        
        expected_title = tasks[0].title
        expected_desc = tasks[0].description
        expected_status = tasks[0].status
        expected_priority = tasks[0].priority
    
    # Test successful export
    response = client.get('/api/v1/tasks/export?format=json', headers=auth_headers)
    
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    
    data = json.loads(response.data)
    assert len(data) == 3
    
    # Verify task data
    assert data[0]['title'] == expected_title
    assert data[0]['description'] == expected_desc
    assert data[0]['status'] == expected_status
    assert data[0]['priority'] == expected_priority
    
    # Test with filters
    response = client.get('/api/v1/tasks/export?format=json&status=pending', headers=auth_headers)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Check that all returned tasks have status 'pending'
    assert all(task['status'] == 'pending' for task in data)
    
    # Test without authentication
    response = client.get('/api/v1/tasks/export?format=json')
    
    assert response.status_code == 401
    assert json.loads(response.data)['error'] == 'Authorization required'

def test_export_tasks_csv(client, app, regular_user, test_tasks, auth_headers):
    """Test exporting tasks as CSV."""
    # Ensure objects are attached to session and store expected values
    with app.app_context():
        from app import db
        tasks = [db.session.merge(task) for task in test_tasks]
        
        expected_id = tasks[0].id
        expected_title = tasks[0].title
        expected_desc = tasks[0].description
        expected_status = tasks[0].status
        expected_priority = tasks[0].priority
    
    # Test successful export
    response = client.get('/api/v1/tasks/export?format=csv', headers=auth_headers)
    
    assert response.status_code == 200
    assert response.content_type.startswith('text/csv')
    assert 'attachment; filename=tasks.csv' in response.headers.get('Content-Disposition', '')
    
    # Parse CSV response
    csv_data = csv.reader(StringIO(response.data.decode('utf-8')))
    rows = list(csv_data)
    
    # Check header row
    header = rows[0]
    assert 'ID' in header
    assert 'Title' in header
    assert 'Description' in header
    assert 'Status' in header
    assert 'Priority' in header
    assert 'Due Date' in header
    
    # Check data rows
    assert len(rows) == 4  # Header + 3 tasks
    
    # Check the data in the first row
    data_row = rows[1]
    assert int(data_row[0]) == expected_id
    assert data_row[1] == expected_title
    assert data_row[2] == expected_desc
    assert data_row[3] == expected_status
    assert data_row[4] == expected_priority
    
    # Test with filters
    response = client.get('/api/v1/tasks/export?format=csv&status=pending', headers=auth_headers)
    
    assert response.status_code == 200
    csv_data = csv.reader(StringIO(response.data.decode('utf-8')))
    rows = list(csv_data)
    
    # Check that all returned tasks have status 'pending' (skipping header row)
    assert all(row[3] == 'pending' for row in rows[1:])
    
    # Test without authentication
    response = client.get('/api/v1/tasks/export?format=csv')
    
    assert response.status_code == 401
    assert json.loads(response.data)['error'] == 'Authorization required'

def test_export_invalid_format(client, auth_headers):
    """Test exporting tasks with invalid format."""
    response = client.get('/api/v1/tasks/export?format=invalid', headers=auth_headers)
    
    assert response.status_code == 400
    assert json.loads(response.data)['error'] == 'Unsupported export format'