from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models.user import User

def admin_required(fn):
    """
    Decorator for endpoints that require admin privileges.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        
        # Convert string ID back to integer if needed
        if isinstance(user_id, str):
            try:
                user_id = int(user_id)
            except ValueError:
                return jsonify({"error": "Invalid user ID"}), 400
            
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        if user.role != 'admin':
            return jsonify({"error": "Admin privileges required"}), 403
        
        return fn(*args, **kwargs)
    
    return wrapper

def get_current_user():
    """
    Helper function to get the current authenticated user.
    """
    user_id = get_jwt_identity()
    
    # Convert string ID back to integer if needed
    if isinstance(user_id, str):
        try:
            user_id = int(user_id)
        except ValueError:
            return None
            
    return User.query.get(user_id)

def is_owner_or_admin(model_instance):
    """
    Check if the current user is the owner of the model instance or an admin.
    """
    user = get_current_user()
    
    if not user:
        return False
    
    # Check if user is admin
    if user.role == 'admin':
        return True
    
    # Check if user is owner (if the model has a user_id attribute)
    if hasattr(model_instance, 'user_id'):
        return model_instance.user_id == user.id
    
    return False

def owner_or_admin_required(model_class):
    """
    Decorator for endpoints that require the user to be owner or admin.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            
            # Get ID from URL parameters
            id_param = None
            for name, value in kwargs.items():
                if name.endswith('_id'):
                    id_param = value
                    break
            
            if id_param is None:
                return jsonify({"error": "Resource ID not found in request"}), 400
            
            # Get model instance
            instance = model_class.query.get(id_param)
            
            if not instance:
                return jsonify({"error": "Resource not found"}), 404
            
            # Check if user is owner or admin
            if not is_owner_or_admin(instance):
                return jsonify({"error": "You don't have permission to access this resource"}), 403
            
            return fn(*args, **kwargs)
        
        return wrapper
    
    return decorator