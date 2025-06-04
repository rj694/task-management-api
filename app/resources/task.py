from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from datetime import datetime
from sqlalchemy import desc, asc, or_
from sqlalchemy.orm import selectinload, joinedload

from app import db
from app.models.task import Task
from app.models.tag import Tag
from app.models.activity_log import ActivityType
from app.schemas import (
    task_schema, tasks_schema, task_query_schema,
    task_bulk_delete_schema, task_bulk_update_schema
)

# **NEW IMPORTS FOR LOGGING**
from app.utils.activity_logger import (
    log_activity,
    get_task_id_from_response
)

task_bp = Blueprint('task', __name__)

# ---------------------------------------------------------------------- #
# Query helpers – unchanged
# ---------------------------------------------------------------------- #
@task_bp.route('', methods=['GET'])
@jwt_required()
def get_tasks():
    """Get all tasks for the current user."""
    current_user_id = get_jwt_identity()
    if isinstance(current_user_id, str):
        current_user_id = int(current_user_id)

    # Validate query parameters
    raw = {k: v for k, v in request.args.items() if v}
    try:
        q = task_query_schema.load(raw)
    except ValidationError as err:
        return jsonify({"error": "Invalid query parameters",
                        "messages": err.messages}), 400

    query = Task.query.options(selectinload(Task.tags)) \
                       .filter_by(user_id=current_user_id)

    if 'status' in q:    query = query.filter_by(status=q['status'])
    if 'priority' in q:  query = query.filter_by(priority=q['priority'])
    if 'search' in q:
        term = f"%{q['search']}%"
        query = query.filter(or_(Task.title.ilike(term),
                                 Task.description.ilike(term)))
    if 'tag' in q:
        query = query.join(Task.tags).filter(Tag.id == q['tag'])
    if 'due_before' in q: query = query.filter(Task.due_date <= q['due_before'])
    if 'due_after' in q:  query = query.filter(Task.due_date >= q['due_after'])

    sort_attr = getattr(Task, q.get('sort_by', 'created_at'))
    query = query.order_by(desc(sort_attr) if q.get('sort_order', 'desc') == 'desc'
                           else asc(sort_attr))

    page      = q.get('page', 1)
    per_page  = q.get('per_page', 10)
    total     = query.count()
    items     = query.limit(per_page).offset((page-1)*per_page).all()
    pages     = (total + per_page - 1) // per_page

    return jsonify({
        "tasks": tasks_schema.dump(items),
        "total": total,
        "pages": pages,
        "page": page,
        "per_page": per_page
    }), 200

@task_bp.route('/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """Get a specific task."""
    current_user_id = get_jwt_identity()
    if isinstance(current_user_id, str):
        current_user_id = int(current_user_id)

    task = (
        Task.query
            .options(joinedload(Task.tags), joinedload(Task.comments))
            .filter_by(id=task_id, user_id=current_user_id)
            .first()
    )
    if not task:
        return jsonify({"error": "Task not found"}), 404

    return jsonify(task_schema.dump(task)), 200

# ---------------------------------------------------------------------- #
# Create / update / delete – now with @log_activity
# ---------------------------------------------------------------------- #
@task_bp.route('', methods=['POST'])
@jwt_required()
@log_activity(               # <-- NEW
    activity_type=ActivityType.TASK_CREATE,
    entity_type="task",
    get_entity_id=get_task_id_from_response
)
def create_task():
    """Create a new task."""
    current_user_id = get_jwt_identity()
    if isinstance(current_user_id, str):
        current_user_id = int(current_user_id)

    try:
        data = task_schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Validation error",
                        "messages": err.messages}), 400

    task = Task(
        title=data['title'],
        user_id=current_user_id,
        description=data.get('description'),
        status=data.get('status', 'pending'),
        priority=data.get('priority', 'medium'),
        due_date=data.get('due_date')
    )
    db.session.add(task)
    db.session.commit()

    # Handle tags if supplied
    if data.get('tag_ids'):
        tags = Tag.query.filter(
            Tag.id.in_(data['tag_ids']),
            Tag.user_id == current_user_id
        ).all()
        if len(tags) != len(data['tag_ids']):
            return jsonify({"error": "One or more tags not found"}), 404
        task.tags.extend(tags)
        db.session.commit()

    task = Task.query.options(joinedload(Task.tags)).get(task.id)
    return jsonify({
        "message": "Task created successfully",
        "task": task_schema.dump(task)
    }), 201


@task_bp.route('/<int:task_id>', methods=['PUT'])
@jwt_required()
@log_activity(
    activity_type=ActivityType.TASK_UPDATE,
    entity_type="task",
    get_entity_id="task_id"
)
def update_task(task_id):
    """Update a specific task."""
    current_user_id = get_jwt_identity()
    if isinstance(current_user_id, str):
        current_user_id = int(current_user_id)

    task = Task.query.filter_by(id=task_id, user_id=current_user_id).first()
    if not task:
        return jsonify({"error": "Task not found"}), 404

    try:
        data = task_schema.load(request.json, partial=True)
    except ValidationError as err:
        return jsonify({"error": "Validation error",
                        "messages": err.messages}), 400

    for field in ('title', 'description', 'status',
                  'priority', 'due_date'):
        if field in data:
            setattr(task, field, data[field])

    # Tags
    if 'tag_ids' in data:
        task.tags = []
        if data['tag_ids']:
            tags = Tag.query.filter(
                Tag.id.in_(data['tag_ids']),
                Tag.user_id == current_user_id
            ).all()
            if len(tags) != len(data['tag_ids']):
                return jsonify({"error": "One or more tags not found"}), 404
            task.tags.extend(tags)

    db.session.commit()
    task = Task.query.options(joinedload(Task.tags)).get(task.id)
    return jsonify({
        "message": "Task updated successfully",
        "task": task_schema.dump(task)
    }), 200


@task_bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
@log_activity(
    activity_type=ActivityType.TASK_DELETE,
    entity_type="task",
    get_entity_id="task_id"
)
def delete_task(task_id):
    """Delete a specific task."""
    current_user_id = get_jwt_identity()
    if isinstance(current_user_id, str):
        current_user_id = int(current_user_id)

    task = Task.query.filter_by(id=task_id, user_id=current_user_id).first()
    if not task:
        return jsonify({"error": "Task not found"}), 404

    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted successfully"}), 200

# ---------------------------------------------------------------------- #
# Bulk operations – activity logged once per call
# ---------------------------------------------------------------------- #
@task_bp.route('/bulk/delete', methods=['POST'])
@jwt_required()
@log_activity(ActivityType.TASK_BULK_DELETE, entity_type="task")
def bulk_delete_tasks():
    """Delete multiple tasks."""
    current_user_id = get_jwt_identity()
    if isinstance(current_user_id, str):
        current_user_id = int(current_user_id)

    try:
        data = task_bulk_delete_schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Validation error",
                        "messages": err.messages}), 400

    count = db.session.query(Task).filter(
        Task.id.in_(data['task_ids']),
        Task.user_id == current_user_id
    ).delete(synchronize_session=False)
    db.session.commit()

    return jsonify({"message": f"{count} tasks deleted successfully"}), 200


@task_bp.route('/bulk/update', methods=['PUT'])
@jwt_required()
@log_activity(ActivityType.TASK_BULK_UPDATE, entity_type="task")
def bulk_update_tasks():
    """Update multiple tasks."""
    current_user_id = get_jwt_identity()
    if isinstance(current_user_id, str):
        current_user_id = int(current_user_id)

    try:
        data = task_bulk_update_schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "Validation error",
                        "messages": err.messages}), 400

    valid_fields = {'status', 'priority', 'due_date'}
    if not set(data['updates']).issubset(valid_fields):
        return jsonify({"error": "Only status, priority or due_date "
                                 "can be mass-updated"}), 400

    tasks = Task.query.filter(
        Task.id.in_(data['task_ids']),
        Task.user_id == current_user_id
    ).all()

    for task in tasks:
        for field, value in data['updates'].items():
            setattr(task, field, value)

    db.session.commit()
    return jsonify({
        "message": f"{len(tasks)} tasks updated successfully"
    }), 200