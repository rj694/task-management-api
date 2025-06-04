from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from datetime import datetime, timedelta
from sqlalchemy import desc, asc
from sqlalchemy.orm import selectinload, joinedload
from app import db
from app.models.task import Task
from app.models.tag import Tag
from app.schemas import task_schema, tasks_schema, task_query_schema, task_bulk_delete_schema, task_bulk_update_schema

task_bp = Blueprint('task', __name__)

@task_bp.route('', methods=['GET'])
@jwt_required()
def get_tasks():
    """Get all tasks for the current user."""
    current_user_id = get_jwt_identity()
    
    # Convert string ID back to integer if needed
    if isinstance(current_user_id, str):
        current_user_id = int(current_user_id)
    
    # Get and validate query parameters
    query_params = {}
    for key, value in request.args.items():
        if value:  # Only include non-empty parameters
            query_params[key] = value
    
    try:
        # Validate query parameters
        query_data = task_query_schema.load(query_params)
    except ValidationError as err:
        return jsonify({"error": "Invalid query parameters", "messages": err.messages}), 400
    
    # Base query with eager loading of tags
    query = (Task.query
                  .options(selectinload(Task.tags))
                  .filter_by(user_id=current_user_id))
    
    # Apply filters if provided
    if 'status' in query_data:
        query = query.filter_by(status=query_data['status'])
    if 'priority' in query_data:
        query = query.filter_by(priority=query_data['priority'])
    if 'search' in query_data:
        term = f"%{query_data['search']}%"
        query = query.filter(or_(Task.title.ilike(term),
                                 Task.description.ilike(term)))
    if 'tag' in query_data:
        query = query.join(Task.tags).filter(Tag.id == query_data['tag'])
    if 'due_before' in query_data:
        query = query.filter(Task.due_date <= query_data['due_before'])
    if 'due_after' in query_data:
        query = query.filter(Task.due_date >= query_data['due_after'])
    
    # Apply sorting
    sort_by = query_data.get('sort_by', 'created_at')
    sort_order = query_data.get('sort_order', 'desc')
    
    if sort_order == 'desc':
        query = query.order_by(desc(getattr(Task, sort_by)))
    else:
        query = query.order_by(asc(getattr(Task, sort_by)))
    
    # Apply pagination
    page = query_data.get('page', 1)
    per_page = query_data.get('per_page', 10)
    
    # Handle pagination for SQLAlchemy 2.0
    total = query.count()
    items = query.limit(per_page).offset((page - 1) * per_page).all()
    total_pages = (total + per_page - 1) // per_page  # Ceiling division
    
    return jsonify({
        "tasks": tasks_schema.dump(items),
        "total": total,
        "pages": total_pages,
        "page": page,
        "per_page": per_page
    }), 200

@task_bp.route('/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """Get a specific task."""
    current_user_id = get_jwt_identity()
    
    # Convert string ID back to integer if needed
    if isinstance(current_user_id, str):
        current_user_id = int(current_user_id)
    
    # Eager load tags and comments
    task = Task.query.options(
        joinedload(Task.tags),
        joinedload(Task.comments)
    ).filter_by(id=task_id, user_id=current_user_id).first()
    
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    return jsonify(task_schema.dump(task)), 200

@task_bp.route('', methods=['POST'])
@jwt_required()
def create_task():
    """Create a new task."""
    current_user_id = get_jwt_identity()
    
    # Convert string ID back to integer if needed
    if isinstance(current_user_id, str):
        current_user_id = int(current_user_id)
    
    try:
        # Validate and deserialize input
        data = task_schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Validation error", "messages": err.messages}), 400
    
    # Create new task
    task = Task(
        title=data['title'],
        user_id=current_user_id,
        description=data.get('description'),
        status=data.get('status', 'pending'),
        priority=data.get('priority', 'medium'),
        due_date=data.get('due_date')
    )
    
    # Add task to database
    db.session.add(task)
    db.session.commit()
    
    # Add tags if provided
    if 'tag_ids' in data and data['tag_ids']:
        tags = Tag.query.filter(
            Tag.id.in_(data['tag_ids']),
            Tag.user_id == current_user_id
        ).all()
        
        if len(tags) != len(data['tag_ids']):
            return jsonify({"error": "One or more tags not found"}), 404
        
        for tag in tags:
            task.tags.append(tag)
        
        db.session.commit()
    
    # Reload task with relationships
    task = Task.query.options(joinedload(Task.tags)).get(task.id)
    
    return jsonify({
        "message": "Task created successfully",
        "task": task_schema.dump(task)
    }), 201

@task_bp.route('/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    """Update a specific task."""
    current_user_id = get_jwt_identity()
    
    # Convert string ID back to integer if needed
    if isinstance(current_user_id, str):
        current_user_id = int(current_user_id)
    
    task = Task.query.filter_by(id=task_id, user_id=current_user_id).first()
    
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    try:
        # Validate and deserialize input
        data = task_schema.load(request.json, partial=True)
    except ValidationError as err:
        return jsonify({"error": "Validation error", "messages": err.messages}), 400
    
    # Update task fields
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'status' in data:
        task.status = data['status']
    if 'priority' in data:
        task.priority = data['priority']
    if 'due_date' in data:
        task.due_date = data['due_date']
    
    # Update tags if provided
    if 'tag_ids' in data:
        # First remove all existing tags
        task.tags = []
        
        if data['tag_ids']:
            tags = Tag.query.filter(
                Tag.id.in_(data['tag_ids']),
                Tag.user_id == current_user_id
            ).all()
            
            if len(tags) != len(data['tag_ids']):
                return jsonify({"error": "One or more tags not found"}), 404
            
            for tag in tags:
                task.tags.append(tag)
    
    # Update task in database
    db.session.commit()
    
    # Reload task with relationships
    task = Task.query.options(joinedload(Task.tags)).get(task.id)
    
    return jsonify({
        "message": "Task updated successfully",
        "task": task_schema.dump(task)
    }), 200

@task_bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """Delete a specific task."""
    current_user_id = get_jwt_identity()
    
    # Convert string ID back to integer if needed
    if isinstance(current_user_id, str):
        current_user_id = int(current_user_id)
    
    task = Task.query.filter_by(id=task_id, user_id=current_user_id).first()
    
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    # Delete task from database
    db.session.delete(task)
    db.session.commit()
    
    return jsonify({
        "message": "Task deleted successfully"
    }), 200

@task_bp.route('/bulk/delete', methods=['POST'])
@jwt_required()
def bulk_delete_tasks():
    """Delete multiple tasks."""
    current_user_id = get_jwt_identity()
    
    # Convert string ID back to integer if needed
    if isinstance(current_user_id, str):
        current_user_id = int(current_user_id)
    
    try:
        # Validate and deserialize input
        data = task_bulk_delete_schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Validation error", "messages": err.messages}), 400
    
    task_ids = data['task_ids']
    
    # Delete tasks
    result = db.session.query(Task).filter(
        Task.id.in_(task_ids),
        Task.user_id == current_user_id
    ).delete(synchronize_session=False)
    
    db.session.commit()
    
    return jsonify({
        "message": f"{result} tasks deleted successfully"
    }), 200

@task_bp.route('/bulk/update', methods=['PUT'])
@jwt_required()
def bulk_update_tasks():
    """Update multiple tasks."""
    current_user_id = get_jwt_identity()
    
    # Convert string ID back to integer if needed
    if isinstance(current_user_id, str):
        current_user_id = int(current_user_id)
    
    try:
        # Validate and deserialize input
        data = task_bulk_update_schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Validation error", "messages": err.messages}), 400
    
    task_ids = data['task_ids']
    updates = data['updates']
    
    # Validate update fields
    valid_fields = {'status', 'priority', 'due_date'}
    for field in updates.keys():
        if field not in valid_fields:
            return jsonify({"error": f"Invalid field: {field}"}), 400
    
    # Update tasks
    tasks = Task.query.filter(
        Task.id.in_(task_ids),
        Task.user_id == current_user_id
    ).all()
    
    for task in tasks:
        for field, value in updates.items():
            setattr(task, field, value)
    
    db.session.commit()
    
    return jsonify({
        "message": f"{len(tasks)} tasks updated successfully"
    }), 200

@task_bp.route('/<int:task_id>/tags', methods=['POST'])
@jwt_required()
def add_tag_to_task(task_id):
    """Add a tag to a task."""
    current_user_id = get_jwt_identity()
    
    # Convert string ID back to integer if needed
    if isinstance(current_user_id, str):
        current_user_id = int(current_user_id)
    
    task = Task.query.filter_by(id=task_id, user_id=current_user_id).first()
    
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    try:
        # Get tag ID from request
        tag_id = request.json.get('tag_id')
        if not tag_id:
            return jsonify({"error": "Tag ID is required"}), 400
    except Exception:
        return jsonify({"error": "Invalid request format"}), 400
    
    # Get tag
    tag = Tag.query.filter_by(id=tag_id, user_id=current_user_id).first()
    
    if not tag:
        return jsonify({"error": "Tag not found"}), 404
    
    # Check if task already has this tag
    if tag in task.tags:
        return jsonify({"error": "Task already has this tag"}), 409
    
    # Add tag to task
    task.tags.append(tag)
    db.session.commit()
    
    # Reload task with relationships
    task = Task.query.options(joinedload(Task.tags)).get(task.id)
    
    return jsonify({
        "message": "Tag added to task successfully",
        "task": task_schema.dump(task)
    }), 200

@task_bp.route('/<int:task_id>/tags/<int:tag_id>', methods=['DELETE'])
@jwt_required()
def remove_tag_from_task(task_id, tag_id):
    """Remove a tag from a task."""
    current_user_id = get_jwt_identity()
    
    # Convert string ID back to integer if needed
    if isinstance(current_user_id, str):
        current_user_id = int(current_user_id)
    
    task = Task.query.filter_by(id=task_id, user_id=current_user_id).first()
    
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    tag = Tag.query.filter_by(id=tag_id, user_id=current_user_id).first()
    
    if not tag:
        return jsonify({"error": "Tag not found"}), 404
    
    # Check if task has this tag
    if tag not in task.tags:
        return jsonify({"error": "Task does not have this tag"}), 404
    
    # Remove tag from task
    task.tags.remove(tag)
    db.session.commit()
    
    # Reload task with relationships
    task = Task.query.options(joinedload(Task.tags)).get(task.id)
    
    return jsonify({
        "message": "Tag removed from task successfully",
        "task": task_schema.dump(task)
    }), 200

@task_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_task_statistics():
    """Get statistics about user's tasks."""
    current_user_id = get_jwt_identity()
    
    # Convert string ID back to integer if needed
    if isinstance(current_user_id, str):
        current_user_id = int(current_user_id)
    
    # Get total tasks
    total_tasks = Task.query.filter_by(user_id=current_user_id).count()
    
    # Get tasks by status
    status_counts = db.session.query(
        Task.status, db.func.count(Task.id)
    ).filter_by(user_id=current_user_id).group_by(Task.status).all()
    
    status_stats = {status: count for status, count in status_counts}
    
    # Get tasks by priority
    priority_counts = db.session.query(
        Task.priority, db.func.count(Task.id)
    ).filter_by(user_id=current_user_id).group_by(Task.priority).all()
    
    priority_stats = {priority: count for priority, count in priority_counts}
    
    # Get tasks by tag
    tag_counts = db.session.query(
        Tag.name, db.func.count(Task.id)
    ).join(Task.tags).filter(Task.user_id == current_user_id).group_by(Tag.name).all()
    
    tag_stats = {tag_name: count for tag_name, count in tag_counts}
    
    # Get overdue tasks
    overdue_tasks = Task.query.filter(
        Task.user_id == current_user_id,
        Task.due_date < datetime.utcnow(),
        Task.status != 'completed'
    ).count()
    
    # Get upcoming tasks (due in the next 7 days)
    upcoming_tasks = Task.query.filter(
        Task.user_id == current_user_id,
        Task.due_date >= datetime.utcnow(),
        Task.due_date <= datetime.utcnow() + timedelta(days=7),
        Task.status != 'completed'
    ).count()
    
    return jsonify({
        "total_tasks": total_tasks,
        "by_status": status_stats,
        "by_priority": priority_stats,
        "by_tag": tag_stats,
        "overdue_tasks": overdue_tasks,
        "upcoming_tasks": upcoming_tasks
    }), 200