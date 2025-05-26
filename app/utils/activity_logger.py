from functools import wraps
from flask import request, g
from flask_jwt_extended import get_jwt_identity
from app.models.activity_log import ActivityLog, ActivityType
from app import db

def log_activity(activity_type, entity_type=None, get_entity_id=None, description_template=None):
    """Decorator to log activities automatically."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Execute the wrapped function
            result = f(*args, **kwargs)
            
            # Only log if the operation was successful (2xx status code)
            if hasattr(result, 'status_code') and 200 <= result[1] < 300:
                try:
                    # Get current user ID
                    current_user_id = get_jwt_identity()
                    if isinstance(current_user_id, str):
                        current_user_id = int(current_user_id)
                    
                    # Get entity ID if provided
                    entity_id = None
                    if get_entity_id:
                        if callable(get_entity_id):
                            entity_id = get_entity_id(result, *args, **kwargs)
                        else:
                            entity_id = kwargs.get(get_entity_id)
                    
                    # Generate description
                    description = None
                    if description_template:
                        if callable(description_template):
                            description = description_template(result, *args, **kwargs)
                        else:
                            description = description_template.format(**kwargs)
                    
                    # Log the activity
                    ActivityLog.log(
                        user_id=current_user_id,
                        activity_type=activity_type,
                        entity_type=entity_type,
                        entity_id=entity_id,
                        description=description,
                        request=request
                    )
                    
                    # Commit as part of the same transaction
                    db.session.commit()
                    
                except Exception as e:
                    # Don't let logging errors break the application
                    print(f"Error logging activity: {str(e)}")
                    db.session.rollback()
            
            return result
        
        return decorated_function
    return decorator

def get_task_id_from_response(result, *args, **kwargs):
    """Extract task ID from response."""
    if 'task_id' in kwargs:
        return kwargs['task_id']
    try:
        data = result[0].get_json()
        if data and 'task' in data and 'id' in data['task']:
            return data['task']['id']
    except:
        pass
    return None

def get_tag_id_from_response(result, *args, **kwargs):
    """Extract tag ID from response."""
    if 'tag_id' in kwargs:
        return kwargs['tag_id']
    try:
        data = result[0].get_json()
        if data and 'tag' in data and 'id' in data['tag']:
            return data['tag']['id']
    except:
        pass
    return None

def get_comment_id_from_response(result, *args, **kwargs):
    """Extract comment ID from response."""
    if 'comment_id' in kwargs:
        return kwargs['comment_id']
    try:
        data = result[0].get_json()
        if data and 'comment' in data and 'id' in data['comment']:
            return data['comment']['id']
    except:
        pass
    return None