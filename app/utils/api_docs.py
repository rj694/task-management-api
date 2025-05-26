from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User

api_docs_bp = Blueprint('api_docs', __name__)

@api_docs_bp.route('', methods=['GET'])
def get_api_docs():
    """Get API documentation."""
    return jsonify({
        "api_version": "v1",
        "title": "Task Management API",
        "description": "A RESTful API for managing tasks",
        "endpoints": {
            "authentication": {
                "/api/v1/auth/register": {
                    "methods": ["POST"],
                    "description": "Register a new user"
                },
                "/api/v1/auth/login": {
                    "methods": ["POST"],
                    "description": "Login a user"
                },
                "/api/v1/auth/refresh": {
                    "methods": ["POST"],
                    "description": "Refresh access token"
                },
                "/api/v1/auth/logout": {
                    "methods": ["POST"],
                    "description": "Logout a user (revoke current token)"
                },
                "/api/v1/auth/logout/all": {
                    "methods": ["POST"],
                    "description": "Logout from all devices (revoke all tokens)"
                },
                "/api/v1/auth/me": {
                    "methods": ["GET", "PUT"],
                    "description": "Get or update current user details"
                }
            },
            "tasks": {
                "/api/v1/tasks": {
                    "methods": ["GET", "POST"],
                    "description": "Get all tasks or create a new task"
                },
                "/api/v1/tasks/<id>": {
                    "methods": ["GET", "PUT", "DELETE"],
                    "description": "Get, update or delete a specific task"
                },
                "/api/v1/tasks/bulk/delete": {
                    "methods": ["POST"],
                    "description": "Delete multiple tasks"
                },
                "/api/v1/tasks/bulk/update": {
                    "methods": ["PUT"],
                    "description": "Update multiple tasks"
                },
                "/api/v1/tasks/statistics": {
                    "methods": ["GET"],
                    "description": "Get task statistics"
                },
                "/api/v1/tasks/<id>/tags": {
                    "methods": ["POST"],
                    "description": "Add a tag to a task"
                },
                "/api/v1/tasks/<id>/tags/<tag_id>": {
                    "methods": ["DELETE"],
                    "description": "Remove a tag from a task"
                }
            },
            "tags": {
                "/api/v1/tags": {
                    "methods": ["GET", "POST"],
                    "description": "Get all tags or create a new tag"
                },
                "/api/v1/tags/<id>": {
                    "methods": ["GET", "PUT", "DELETE"],
                    "description": "Get, update or delete a specific tag"
                }
            },
            "comments": {
                "/api/v1/tasks/<id>/comments": {
                    "methods": ["GET", "POST"],
                    "description": "Get all comments for a task or create a new comment"
                },
                "/api/v1/comments/<id>": {
                    "methods": ["GET", "PUT", "DELETE"],
                    "description": "Get, update or delete a specific comment"
                }
            },
            "export": {
                "/api/v1/tasks/export": {
                    "methods": ["GET"],
                    "description": "Export tasks in different formats (json, csv)"
                }
            },
            "admin": {
                "/api/v1/admin/users": {
                    "methods": ["GET"],
                    "description": "Get all users (admin only)"
                },
                "/api/v1/admin/users/<id>": {
                    "methods": ["GET", "PUT", "DELETE"],
                    "description": "Get, update or delete a specific user (admin only)"
                },
                "/api/v1/admin/stats": {
                    "methods": ["GET"],
                    "description": "Get admin statistics (admin only)"
                }
            }
        }
    }), 200

@api_docs_bp.route('/user', methods=['GET'])
@jwt_required()
def get_user_api_docs():
    """Get API documentation with user role information."""
    current_user_id = get_jwt_identity()
    
    # Convert string ID back to integer if needed
    if isinstance(current_user_id, str):
        current_user_id = int(current_user_id)
    
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Base documentation
    docs = get_api_docs().json
    
    # Add user role information
    docs["user"] = {
        "id": user.id,
        "username": user.username,
        "role": user.role
    }
    
    # Add role-specific information
    if user.role == 'admin':
        docs["admin_access"] = True
    else:
        docs["admin_access"] = False
    
    return jsonify(docs), 200