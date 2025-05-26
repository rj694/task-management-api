import requests
import json
from pprint import pprint

BASE_URL = "http://localhost:5000/api/v1"

def test_register():
    """Test user registration."""
    print("Testing user registration...")
    
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=data)
    
    print(f"Status code: {response.status_code}")
    pprint(response.json())
    
    return response.json()

def test_login():
    """Test user login."""
    print("\nTesting user login...")
    
    data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=data)
    
    print(f"Status code: {response.status_code}")
    pprint(response.json())
    
    return response.json()

def test_create_task(access_token):
    """Test task creation."""
    print("\nTesting task creation...")
    print(f"Using token: {access_token[:20]}...")
    
    # Make sure the header format is exactly 'Bearer <token>' with a space
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "title": "Test Task",
        "description": "This is a test task",
        "status": "pending",
        "priority": "high"
    }
    
    response = requests.post(f"{BASE_URL}/tasks", json=data, headers=headers)
    
    print(f"Status code: {response.status_code}")
    if response.status_code == 401:
        print("DEBUG: Authorization header sent:", headers["Authorization"])
    pprint(response.json())
    
    return response.json()

def test_get_tasks(access_token):
    """Test getting all tasks."""
    print("\nTesting get all tasks...")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(f"{BASE_URL}/tasks", headers=headers)
    
    print(f"Status code: {response.status_code}")
    pprint(response.json())
    
    return response.json()

def test_get_task(access_token, task_id):
    """Test getting a specific task."""
    print(f"\nTesting get task {task_id}...")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(f"{BASE_URL}/tasks/{task_id}", headers=headers)
    
    print(f"Status code: {response.status_code}")
    pprint(response.json())
    
    return response.json()

def test_update_task(access_token, task_id):
    """Test updating a task."""
    print(f"\nTesting update task {task_id}...")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "title": "Updated Test Task",
        "status": "in_progress"
    }
    
    response = requests.put(f"{BASE_URL}/tasks/{task_id}", json=data, headers=headers)
    
    print(f"Status code: {response.status_code}")
    pprint(response.json())
    
    return response.json()

def test_task_statistics(access_token):
    """Test getting task statistics."""
    print("\nTesting task statistics...")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(f"{BASE_URL}/tasks/statistics", headers=headers)
    
    print(f"Status code: {response.status_code}")
    pprint(response.json())
    
    return response.json()

def test_delete_task(access_token, task_id):
    """Test deleting a task."""
    print(f"\nTesting delete task {task_id}...")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.delete(f"{BASE_URL}/tasks/{task_id}", headers=headers)
    
    print(f"Status code: {response.status_code}")
    pprint(response.json())
    
    return response.json()

def run_tests():
    """Run all tests."""
    try:
        # Register a new user
        register_data = test_register()
        
        # Login
        login_data = test_login()
        access_token = login_data.get('access_token')
        
        if not access_token:
            print("Failed to get access token!")
            return
        
        # Create a task
        task_data = test_create_task(access_token)
        
        # Check if task creation was successful
        if 'task' not in task_data:
            print("Task creation failed!")
            return
            
        task_id = task_data['task']['id']
        
        # Get all tasks
        test_get_tasks(access_token)
        
        # Get a specific task
        test_get_task(access_token, task_id)
        
        # Update a task
        test_update_task(access_token, task_id)
        
        # Get task statistics
        test_task_statistics(access_token)
        
        # Delete a task
        test_delete_task(access_token, task_id)
        
        print("\nAll tests completed!")
    except Exception as e:
        print(f"Test error: {str(e)}")

if __name__ == "__main__":
    run_tests()