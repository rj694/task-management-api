import requests
import json
from pprint import pprint

BASE_URL = "http://localhost:5000/api/v1"

def test_tag_operations(auth_token):
    """Test tag operations."""
    print("=== Testing Tag Operations ===")
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    
    # Create a tag
    print("\n1. Creating a tag...")
    tag_data = {
        "name": "Important",
        "color": "#ff0000"
    }
    
    create_tag_response = requests.post(f"{BASE_URL}/tags", json=tag_data, headers=headers)
    print(f"Status code: {create_tag_response.status_code}")
    
    if create_tag_response.status_code != 201:
        print("Failed to create tag!")
        return None
    
    tag = create_tag_response.json()['tag']
    tag_id = tag['id']
    print(f"Created tag with ID: {tag_id}")
    
    # Get all tags
    print("\n2. Getting all tags...")
    get_tags_response = requests.get(f"{BASE_URL}/tags", headers=headers)
    print(f"Status code: {get_tags_response.status_code}")
    
    if get_tags_response.status_code == 200:
        tags = get_tags_response.json()
        print(f"Found {len(tags)} tags:")
        for tag in tags:
            print(f"  - {tag['name']} (ID: {tag['id']})")
    
    # Update the tag
    print("\n3. Updating a tag...")
    update_tag_data = {
        "name": "Very Important",
        "color": "#ff5500"
    }
    
    update_tag_response = requests.put(f"{BASE_URL}/tags/{tag_id}", json=update_tag_data, headers=headers)
    print(f"Status code: {update_tag_response.status_code}")
    
    if update_tag_response.status_code == 200:
        updated_tag = update_tag_response.json()['tag']
        print(f"Updated tag: {updated_tag['name']} (Color: {updated_tag['color']})")
    
    return tag_id

def test_task_with_tags(auth_token, tag_id):
    """Test task operations with tags."""
    print("\n=== Testing Tasks with Tags ===")
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    
    # Create a task with a tag
    print("\n1. Creating a task with a tag...")
    task_data = {
        "title": "Important Task",
        "description": "This is a very important task",
        "status": "pending",
        "priority": "high",
        "tag_ids": [tag_id]
    }
    
    create_task_response = requests.post(f"{BASE_URL}/tasks", json=task_data, headers=headers)
    print(f"Status code: {create_task_response.status_code}")
    
    if create_task_response.status_code != 201:
        print("Failed to create task!")
        return None
    
    task = create_task_response.json()['task']
    task_id = task['id']
    print(f"Created task with ID: {task_id}")
    
    # Get task with tags
    print("\n2. Getting task with tags...")
    get_task_response = requests.get(f"{BASE_URL}/tasks/{task_id}", headers=headers)
    print(f"Status code: {get_task_response.status_code}")
    
    if get_task_response.status_code == 200:
        task_with_tags = get_task_response.json()
        print(f"Task: {task_with_tags['title']}")
        print(f"Tags: {len(task_with_tags['tags'])}")
        for tag in task_with_tags['tags']:
            print(f"  - {tag['name']} (Color: {tag['color']})")
    
    # Filter tasks by tag
    print("\n3. Filtering tasks by tag...")
    get_filtered_tasks_response = requests.get(f"{BASE_URL}/tasks?tag={tag_id}", headers=headers)
    print(f"Status code: {get_filtered_tasks_response.status_code}")
    
    if get_filtered_tasks_response.status_code == 200:
        filtered_tasks = get_filtered_tasks_response.json()
        print(f"Found {filtered_tasks['total']} tasks with tag ID {tag_id}")
    
    return task_id

def test_task_comments(auth_token, task_id):
    """Test task comments."""
    print("\n=== Testing Task Comments ===")
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    
    # Add a comment to a task
    print("\n1. Adding a comment to a task...")
    comment_data = {
        "content": "This is a very important comment on this task!"
    }
    
    create_comment_response = requests.post(f"{BASE_URL}/tasks/{task_id}/comments", json=comment_data, headers=headers)
    print(f"Status code: {create_comment_response.status_code}")
    
    if create_comment_response.status_code != 201:
        print("Failed to create comment!")
        return None
    
    comment = create_comment_response.json()['comment']
    comment_id = comment['id']
    print(f"Created comment with ID: {comment_id}")
    
    # Get all comments for a task
    print("\n2. Getting all comments for a task...")
    get_comments_response = requests.get(f"{BASE_URL}/tasks/{task_id}/comments", headers=headers)
    print(f"Status code: {get_comments_response.status_code}")
    
    if get_comments_response.status_code == 200:
        comments = get_comments_response.json()
        print(f"Found {len(comments)} comments:")
        for comment in comments:
            print(f"  - {comment['content']}")
    
    # Update a comment
    print("\n3. Updating a comment...")
    update_comment_data = {
        "content": "This is an updated comment!"
    }
    
    update_comment_response = requests.put(f"{BASE_URL}/comments/{comment_id}", json=update_comment_data, headers=headers)
    print(f"Status code: {update_comment_response.status_code}")
    
    if update_comment_response.status_code == 200:
        updated_comment = update_comment_response.json()['comment']
        print(f"Updated comment: {updated_comment['content']}")
    
    return comment_id

def test_task_export(auth_token):
    """Test task export functionality."""
    print("\n=== Testing Task Export ===")
    
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    
    # Export tasks as JSON
    print("\n1. Exporting tasks as JSON...")
    export_json_response = requests.get(f"{BASE_URL}/tasks/export?format=json", headers=headers)
    print(f"Status code: {export_json_response.status_code}")
    
    if export_json_response.status_code == 200:
        tasks = export_json_response.json()
        print(f"Exported {len(tasks)} tasks in JSON format")
    
    # Export tasks as CSV
    print("\n2. Exporting tasks as CSV...")
    export_csv_response = requests.get(f"{BASE_URL}/tasks/export?format=csv", headers=headers)
    print(f"Status code: {export_csv_response.status_code}")
    
    if export_csv_response.status_code == 200:
        content_disposition = export_csv_response.headers.get('Content-Disposition')
        content_type = export_csv_response.headers.get('Content-Type')
        print(f"Exported tasks in CSV format (Content-Type: {content_type})")
        print(f"Content-Disposition: {content_disposition}")
        
        # Save CSV file locally
        with open("tasks_export.csv", "w") as f:
            f.write(export_csv_response.text)
        print("Saved exported CSV to tasks_export.csv")

def test_rate_limiting(auth_token):
    """Test rate limiting."""
    print("\n=== Testing Rate Limiting ===")
    
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    
    # Perform multiple requests to trigger rate limiting
    print("\n1. Making multiple requests to test rate limiting...")
    endpoint = f"{BASE_URL}/tasks"
    
    for i in range(1, 6):
        print(f"Request {i}...")
        response = requests.get(endpoint, headers=headers)
        print(f"Status code: {response.status_code}")
        
        # Check for rate limit headers
        remaining = response.headers.get('X-RateLimit-Remaining')
        limit = response.headers.get('X-RateLimit-Limit')
        reset = response.headers.get('X-RateLimit-Reset')
        
        if remaining and limit and reset:
            print(f"Rate limit: {remaining}/{limit} requests remaining, resets in {reset}s")

def run_tests():
    """Run all tests."""
    print("=== Testing Advanced Features ===")
    
    # Login to get an access token
    print("\nLogging in to get an access token...")
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Status code: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print("Login failed!")
        return
    
    auth_token = login_response.json()['access_token']
    
    # Test tag operations
    tag_id = test_tag_operations(auth_token)
    
    if tag_id:
        # Test task with tags
        task_id = test_task_with_tags(auth_token, tag_id)
        
        if task_id:
            # Test task comments
            comment_id = test_task_comments(auth_token, task_id)
            
            # Test task export
            test_task_export(auth_token)
    
    # Test rate limiting
    test_rate_limiting(auth_token)
    
    print("\n=== All Tests Completed ===")

if __name__ == "__main__":
    run_tests()