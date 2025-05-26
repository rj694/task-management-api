from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.utils.auth import admin_required
from app.models.user import User
from app.schemas import user_schema, users_schema
from app import db
from marshmallow import ValidationError

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    """Get all users (admin only)."""
    # Get query parameters for pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Paginate users
    pagination = User.query.paginate(page=page, per_page=per_page)

    return jsonify({
        "users": users_schema.dump(pagination.items),
        "total": pagination.total,
        "pages": pagination.pages,
        "page": page,
        "per_page": per_page
    }), 200

@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    """Get a specific user (admin only)."""
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user_schema.dump(user)), 200

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """Update a specific user (admin only)."""
    # Fetch the target user
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Disallow an admin from updating themselves via this endpoint
    current_user_id = get_jwt_identity()
    if isinstance(current_user_id, str):
        try:
            current_user_id = int(current_user_id)
        except ValueError:
            pass

    if current_user_id == user_id:
        return jsonify({"error": "Admin privileges required"}), 403

    # Get the updates from the request
    data = request.get_json() or {}

    # Update username if provided and not taken
    if 'username' in data and data['username'] != user.username:
        if User.query.filter_by(username=data['username']).first():
            return jsonify({"error": "Username already taken"}), 409
        user.username = data['username']

    # Update email if provided and not taken
    if 'email' in data and data['email'] != user.email:
        if User.query.filter_by(email=data['email']).first():
            return jsonify({"error": "Email already taken"}), 409
        user.email = data['email']

    # Update role if provided
    if 'role' in data and data['role'] in ['user', 'admin']:
        user.role = data['role']

    # Update password if provided
    if 'password' in data:
        user.set_password(data['password'])

    # Commit all changes
    db.session.commit()

    return jsonify({
        "message": "User updated successfully",
        "user": user_schema.dump(user)
    }), 200

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Delete a specific user (admin only)."""
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({
        "message": "User deleted successfully"
    }), 200

@admin_bp.route('/stats', methods=['GET'])
@admin_required
def get_admin_statistics():
    """Get admin statistics (admin only)."""
    # Get total users
    total_users = User.query.count()

    # Get users by role
    admin_users = User.query.filter_by(role='admin').count()
    regular_users = User.query.filter_by(role='user').count()

    # Get total tasks
    from app.models.task import Task
    total_tasks = Task.query.count()

    # Get tasks by status
    from sqlalchemy import func
    task_by_status = db.session.query(
        Task.status, func.count(Task.id)
    ).group_by(Task.status).all()
    status_stats = {status: count for status, count in task_by_status}

    return jsonify({
        "user_stats": {
            "total": total_users,
            "admins": admin_users,
            "regular_users": regular_users
        },
        "task_stats": {
            "total": total_tasks,
            "by_status": status_stats
        }
    }), 200