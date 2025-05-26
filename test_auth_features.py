import requests
import json
from pprint import pprint

BASE_URL = "http://localhost:5000/api/v1"

def test_register_login_logout():
    """Test the complete authentication flow."""
    # Register a new user
    print("1. Registering a new user...")
    register_data = {
        "username": "testuser2",
        "email": "test2@example.com",
        "password": "password123"
    }
    
    register_response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    print(f"Status code: {register_response.status_code}")
    
    if register_response.status_code != 201:
        login_data = {
            "email": "test2@example.com",
            "password": "password123"
        }
        print("\nUser might already exist. Trying to login...")
        login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if login_response.status_code != 200:
            print(f"Login failed with status code: {login_response.status_code}")
            return
        tokens = login_response.json()
    else:
        tokens = register_response.json()
    
    access_token = tokens.get('access_token')
    refresh_token = tokens.get('refresh_token')
    
    # Get user profile
    print("\n2. Getting user profile...")
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    profile_response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"Status code: {profile_response.status_code}")
    pprint(profile_response.json())
    
    # Logout
    print("\n3. Logging out...")
    logout_response = requests.post(f"{BASE_URL}/auth/logout", headers=headers)
    print(f"Status code: {logout_response.status_code}")
    pprint(logout_response.json())
    
    # Try to use the token after logout
    print("\n4. Trying to use the token after logout...")
    profile_response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"Status code: {profile_response.status_code}")
    pprint(profile_response.json())
    
    # Try to refresh the token
    print("\n5. Trying to refresh the token...")
    refresh_headers = {
        "Authorization": f"Bearer {refresh_token}"
    }
    refresh_response = requests.post(f"{BASE_URL}/auth/refresh", headers=refresh_headers)
    print(f"Status code: {refresh_response.status_code}")
    
    return True

def test_admin_endpoints(admin_email, admin_password):
    """Test the admin endpoints."""
    # Login as admin
    print("\n6. Logging in as admin...")
    login_data = {
        "email": admin_email,
        "password": admin_password
    }
    
    login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Status code: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print("Admin login failed.")
        return
    
    admin_token = login_response.json().get('access_token')
    admin_headers = {
        "Authorization": f"Bearer {admin_token}"
    }
    
    # Get all users (admin only)
    print("\n7. Getting all users (admin only)...")
    users_response = requests.get(f"{BASE_URL}/admin/users", headers=admin_headers)
    print(f"Status code: {users_response.status_code}")
    
    if users_response.status_code == 200:
        users_data = users_response.json()
        print(f"Total users: {users_data.get('total')}")
    
    # Get admin statistics
    print("\n8. Getting admin statistics...")
    stats_response = requests.get(f"{BASE_URL}/admin/stats", headers=admin_headers)
    print(f"Status code: {stats_response.status_code}")
    
    if stats_response.status_code == 200:
        pprint(stats_response.json())
    
    return True

def run_tests():
    """Run all tests."""
    print("=== Testing Authentication Features ===")
    auth_tests_passed = test_register_login_logout()
    
    if auth_tests_passed:
        print("\n=== Authentication Tests Passed ===")
    else:
        print("\n=== Authentication Tests Failed ===")
    
    # You'll need to replace these with your actual admin credentials
    admin_email = input("\nEnter admin email: ")
    admin_password = input("Enter admin password: ")
    
    print("\n=== Testing Admin Features ===")
    admin_tests_passed = test_admin_endpoints(admin_email, admin_password)
    
    if admin_tests_passed:
        print("\n=== Admin Tests Passed ===")
    else:
        print("\n=== Admin Tests Failed ===")

if __name__ == "__main__":
    run_tests()